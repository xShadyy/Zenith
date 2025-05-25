import platform
import subprocess
from shutil import which
from typing import Optional

from zenith.console import console


def detect_os() -> str:
    """Detect the operating system using platform.system()."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    elif system == "windows":
        return "windows"
    else:
        return system


def detect_package_manager() -> Optional[str]:
    """Detect available package manager using shutil.which()."""
    package_managers = ["brew", "apt-get", "yum", "pacman", "dnf", "zypper"]

    for pm in package_managers:
        if which(pm):
            return pm

    return None


def install_package(package_name: str, package_manager: str = None) -> bool:
    """ """
    if package_manager is None:
        package_manager = detect_package_manager()

    if package_manager is None:
        console.print("No supported package manager found", style="bold red")
        return False

    install_commands = {
        "brew": ["brew", "install", package_name],
        "apt-get": ["sudo", "apt-get", "install", "-y", package_name],
        "yum": ["sudo", "yum", "install", "-y", package_name],
        "pacman": ["sudo", "pacman", "-S", "--noconfirm", package_name],
        "dnf": ["sudo", "dnf", "install", "-y", package_name],
        "zypper": ["sudo", "zypper", "install", "-y", package_name],
    }

    if package_manager not in install_commands:
        console.print(
            f"Unsupported package manager: {package_manager}", style="bold red"
        )
        return False

    command = install_commands[package_manager]

    try:
        console.print(
            f"Installing {package_name} using {package_manager}...", style="bold yellow"
        )
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        console.print(f"Successfully installed {package_name}", style="bold green")
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"Failed to install {package_name}: {e}", style="bold red")
        if e.stderr:
            console.print(f"Error output: {e.stderr}", style="bold red")
        return False
    except FileNotFoundError:
        console.print(f"Package manager {package_manager} not found", style="bold red")
        return False


def get_install_command(
    package_name: str, package_manager: str = None
) -> Optional[str]:
    """ """
    if package_manager is None:
        package_manager = detect_package_manager()

    if package_manager is None:
        return None

    install_commands = {
        "brew": f"brew install {package_name}",
        "apt-get": f"sudo apt-get install -y {package_name}",
        "yum": f"sudo yum install -y {package_name}",
        "pacman": f"sudo pacman -S --noconfirm {package_name}",
        "dnf": f"sudo dnf install -y {package_name}",
        "zypper": f"sudo zypper install -y {package_name}",
    }

    return install_commands.get(package_manager)


def update_package_manager() -> bool:
    """Update package manager repositories."""
    package_manager = detect_package_manager()

    if package_manager is None:
        return False

    update_commands = {
        "brew": ["brew", "update"],
        "apt-get": ["sudo", "apt-get", "update"],
        "yum": ["sudo", "yum", "check-update"],
        "pacman": ["sudo", "pacman", "-Sy"],
        "dnf": ["sudo", "dnf", "check-update"],
        "zypper": ["sudo", "zypper", "refresh"],
    }

    if package_manager not in update_commands:
        return False

    try:
        console.print(
            f"Updating {package_manager} repositories...", style="bold yellow"
        )
        subprocess.run(
            update_commands[package_manager], check=True, capture_output=True
        )
        console.print("Package manager updated successfully", style="bold green")
        return True
    except subprocess.CalledProcessError:
        console.print("Failed to update package manager", style="bold red")
        return False
