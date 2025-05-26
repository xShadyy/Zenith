import os
import subprocess
from abc import ABCMeta, abstractmethod
from collections.abc import Iterable
from shutil import rmtree, which
from typing import Dict, List, Optional, Union

from git import RemoteProgress, Repo
from rich.progress import BarColumn, Progress, TaskID
from rich.table import Table

from zenith.console import console
from zenith.core.config import INSTALL_DIR, get_config
from zenith.core.menu import confirm
from zenith.core.package_manager import (
    detect_os,
    detect_package_manager,
    get_install_command,
    install_package,
)

config = get_config()


def print_pip_deps(packages: str | Iterable[str]) -> None:
    requirements = []
    if isinstance(packages, str) and os.path.exists(packages):
        with open(packages, encoding="utf-8") as requirements_file:
            for line in requirements_file:
                if line.strip():
                    requirements.append(line)
    elif isinstance(packages, Iterable):
        requirements = list(packages)
    else:
        raise ValueError
    table = Table("Packages", title="Pip Dependencies", title_style="highlight")
    for req in requirements:
        table.add_row(req)
    console.print()
    console.print(table)


class InstallError(Exception):
    pass


class CloneError(Exception):
    pass


class GitProgress(RemoteProgress):
    def __init__(self) -> None:
        super().__init__()
        self.progress = Progress(
            "[progress.description]{task.description}",
            BarColumn(None),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "[progress.filesize]{task.fields[msg]}",
        )
        self.current_opcode = None
        self.task: TaskID | None = None

    def update(
        self, opcode, count: int, max_value: int, msg: str | None = None
    ) -> None:
        opcode_strs = {
            self.COUNTING: "Counting",
            self.COMPRESSING: "Compressing",
            self.WRITING: "Writing",
            self.RECEIVING: "Receiving",
            self.RESOLVING: "Resolving",
            self.FINDING_SOURCES: "Finding sources",
            self.CHECKING_OUT: "Checking out",
        }
        stage, real_opcode = opcode & self.STAGE_MASK, opcode & self.OP_MASK

        try:
            count = int(count)
            max_value = int(max_value)
        except ValueError:
            return

        if self.current_opcode != real_opcode:
            if self.task:
                self.progress.update(self.task, total=1, completed=1, msg="")
            self.current_opcode = real_opcode
            self.task = self.progress.add_task(
                opcode_strs[real_opcode].ljust(15), msg=""
            )

        if stage & self.BEGIN:
            self.progress.start()
        if stage & self.END:
            self.progress.stop()
        if self.task:
            self.progress.update(
                self.task, msg=msg or "", total=max_value, completed=count
            )


class GitHubRepo(metaclass=ABCMeta):
    def __init__(
        self,
        path: str = "xShadyy/zenith",
        install: str | dict[str, str | list[str]] = "pip install -e .",
        description=None,
    ) -> None:
        self.path = path
        self.name = self.path.split("/")[-1]
        self.install_options = install
        self.full_path = os.path.join(INSTALL_DIR, self.name)
        self.deps_marker = os.path.join(self.full_path, ".zenith_deps_installed")
        self.description = description
        self.scriptable_os = ["debian", "windows", "macos", "arch"]

    def __str__(self) -> str:
        return self.name.lower().replace("-", "_")

    def _check_pip_dependencies_installed(self) -> bool:
        if (
            not isinstance(self.install_options, dict)
            or "pip" not in self.install_options
        ):
            return True

        packages = self.install_options.get("pip")
        if (
            not packages
            or isinstance(packages, str)
            and packages.startswith("pip install")
        ):
            return True

        if os.path.exists(self.deps_marker):
            return True

        requirements_file = (
            os.path.join(self.full_path, packages)
            if isinstance(packages, str)
            else None
        )
        if requirements_file and os.path.exists(requirements_file):
            try:

                with open(requirements_file, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):

                            pkg_name = (
                                line.split(">=")[0]
                                .split("==")[0]
                                .split("<=")[0]
                                .split(">")[0]
                                .split("<")[0]
                                .split("!")[0]
                                .strip()
                            )
                            if pkg_name:
                                try:
                                    result = subprocess.run(
                                        [
                                            subprocess.sys.executable,
                                            "-c",
                                            f'import {pkg_name.replace("-", "_")}',
                                        ],
                                        capture_output=True,
                                        timeout=5,
                                    )
                                    if result.returncode != 0:
                                        return False
                                except (subprocess.TimeoutExpired, Exception):

                                    return False
                return True
            except (FileNotFoundError, Exception):
                return False
        return False

    def _mark_dependencies_installed(self) -> None:

        try:
            with open(self.deps_marker, "w", encoding="utf-8") as f:
                f.write(f"Dependencies installed for {self.name}\n")
        except OSError:
            pass

    def reset_dependencies(self) -> None:
        try:
            if os.path.exists(self.deps_marker):
                os.remove(self.deps_marker)
        except OSError:
            pass

    def clone(self, overwrite: bool = False) -> str:
        if os.path.exists(self.full_path):
            if not overwrite:
                repo = Repo(self.full_path)
                repo.remotes.origin.pull()
                return self.full_path
            rmtree(self.full_path)
        url = f"https://github.com/{self.path}"
        if config.getboolean("zenith", "ssh_clone"):
            url = f"git@github.com:{self.path}.git"
        Repo.clone_from(url, self.full_path, progress=GitProgress())
        if not os.path.exists(self.full_path):
            raise CloneError(f"{self.full_path} not found")
        return self.full_path

    def install(self, no_confirm: bool = False, clone: bool = True) -> None:
        if not no_confirm and not confirm(
            f"\nDo you want to install https://github.com/{self.path}?"
        ):
            raise InstallError("User cancelled installation")

        if clone:
            self.clone()

        if self._check_pip_dependencies_installed():
            return

        if not self.install_options:
            return

        command = "exit 1"

        if clone:
            os.chdir(self.full_path)
        else:
            os.chdir(INSTALL_DIR)

        install = self.install_options
        current_os = detect_os()
        package_manager = detect_package_manager()

        if isinstance(install, dict):
            if "pip" in install:
                packages = install.get("pip")
                message = ""

                if isinstance(packages, list):
                    message = "Do you want to install these packages?"
                    packages_str = " ".join(packages)
                    command = f"pip install {packages_str}"
                    try:
                        print_pip_deps(packages)
                    except (ValueError, FileNotFoundError):
                        pass

                elif isinstance(packages, str):
                    if packages.startswith("pip install"):

                        command = packages
                        message = f"Do you want to run: {command}?"
                    else:

                        requirements_file = os.path.join(self.full_path, packages)
                        if os.path.exists(requirements_file):
                            command = f"pip install -r {requirements_file}"
                            message = f"Do you want to install packages from {requirements_file}?"
                            try:
                                print_pip_deps(requirements_file)
                            except (ValueError, FileNotFoundError):
                                pass
                        else:

                            pyproject_file = os.path.join(
                                self.full_path, "pyproject.toml"
                            )
                            if os.path.exists(pyproject_file):
                                command = "pip install ."
                                message = f"Installing current directory (pyproject.toml found)"
                            else:
                                console.print(
                                    f"Warning: Requirements file {requirements_file} not found",
                                    style="warning",
                                )
                                console.print("Skipping pip installation", style="info")
                                return

                if not confirm(message):
                    raise InstallError("User cancelled pip installation")

            elif "go" in install and which("go"):
                command = install.get("go")

            elif "binary" in install:
                bin_url = install.get("binary")
                if which("curl"):
                    command = f"curl -L -o {self.full_path}/{self.name} -s {bin_url}"
                elif which("wget"):
                    command = f"wget -q -O {self.full_path}/{self.name} {bin_url}"
                else:
                    raise InstallError("Supported download tools missing")
                command = f"mkdir -p {self.full_path} && {command} && chmod +x {self.full_path}/{self.name}"

            elif package_manager and package_manager in install:
                package_name = install.get(package_manager)
                if isinstance(package_name, str):
                    command = get_install_command(package_name, package_manager)
                else:
                    command = str(package_name)

            elif "brew" in install and (which("brew") or package_manager == "brew"):
                package_name = install.get("brew")
                if package_name.startswith("install "):
                    command = f"brew {package_name}"
                else:
                    command = f"brew install {package_name}"

            elif current_os == "linux" and package_manager:
                linux_mappings = {
                    "apt-get": install.get("linux")
                    or install.get("debian")
                    or install.get("ubuntu"),
                    "yum": install.get("linux")
                    or install.get("rhel")
                    or install.get("centos"),
                    "pacman": install.get("linux") or install.get("arch"),
                    "dnf": install.get("linux") or install.get("fedora"),
                }

                if (
                    package_manager in linux_mappings
                    and linux_mappings[package_manager]
                ):
                    command = str(linux_mappings[package_manager])
                elif "linux" in install:
                    command = str(install["linux"])

            elif current_os == "macos" and "macos" in install:
                command = str(install["macos"])

            elif current_os == "windows" and "windows" in install:
                command = str(install["windows"])

            elif current_os in install and current_os in self.scriptable_os:
                command = str(install[current_os])
            else:
                if package_manager and self._try_auto_install():
                    console.print(
                        f"Successfully auto-installed dependencies using {package_manager}",
                        style="bold green",
                    )
                    self._mark_dependencies_installed()
                    return
                else:
                    available_options = (
                        list(install.keys())
                        if isinstance(install, dict)
                        else ["manual command"]
                    )
                    raise InstallError(
                        f"Platform not supported. Available options: {', '.join(available_options)}. "
                        f"Detected OS: {current_os}, Package manager: {package_manager or 'none'}"
                    )
        else:
            command = install

        if command != "exit 1":
            result = os.system(command)
            if result != 0:
                raise InstallError(
                    f"Installation command failed with exit code {result}"
                )

            if "pip" in str(command):
                self._mark_dependencies_installed()
        else:
            raise InstallError("No valid installation command determined")

    def _try_auto_install(self) -> bool:
        package_manager = detect_package_manager()
        if not package_manager:
            return False

        tool_packages = {
            "nmap": "nmap",
            "bettercap": "bettercap" if package_manager == "pacman" else None,
            "sqlmap": None,
            "sublist3r": None,
            "sherlock": None,
            "photon": None,
            "xsstrike": None,
        }

        tool_name = self.name.lower()
        package_name = tool_packages.get(tool_name)

        if package_name and confirm(
            f"Auto-install {package_name} using {package_manager}?"
        ):
            return install_package(package_name, package_manager)

        return False

    def installed(self) -> bool:

        if not os.path.exists(self.full_path):
            return False

        if isinstance(self.install_options, dict) and "pip" in self.install_options:
            return self._check_pip_dependencies_installed()

        return True

    @abstractmethod
    def run(self) -> int:
        pass
