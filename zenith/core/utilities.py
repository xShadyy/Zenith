import os
from abc import ABCMeta
from base64 import b64decode
from socket import gethostbyname

import pyfiglet
from requests import get

from zenith.console import console

from .config import GITHUB_PATH, INSTALL_DIR
from .hosts import add_host, get_hosts
from .menu import confirm, set_readline, tools_cli


class Utility(metaclass=ABCMeta):
    def __init__(self, description: str = None):
        self.description = description

    def __str__(self) -> str:
        return self.__class__.__name__

    def run(self) -> None:
        pass


class host2ip(Utility):
    def __init__(self):
        super().__init__(description="Gets IP from host")

    def run(self):
        hosts = get_hosts()
        set_readline(hosts)
        user_host = input("\nEnter a host: ").strip()
        if user_host not in hosts:
            add_host(user_host)
        ip = gethostbyname(user_host)
        console.print(f"\n{user_host} has the IP of {ip}")


class base64_decode(Utility):
    def __init__(self):
        super().__init__(description="Decodes base64")

    def run(self):
        user_base64 = input("\nEnter base64: ").strip()
        text = b64decode(user_base64)
        console.print(f"\nDecoded: {text}")


class print_contributors(Utility):
    def __init__(self):
        super().__init__(description="Prints the author")

    def run(self):
        banner = pyfiglet.figlet_format("Author")
        console.print(banner, style="bold white")

        response = get(
            f"https://api.github.com/repos/{GITHUB_PATH}/contributors", timeout=30
        )
        contributors = response.json()
        for contributor in sorted(
            contributors, key=lambda c: c["contributions"], reverse=True
        ):
            username = contributor.get("login")
            console.print(f" {username} ".center(30, "-"))


class reset_tool_dependencies(Utility):
    def __init__(self):
        super().__init__(description="Reset tool dependency markers")

    def run(self):
        import glob

        deps_files = glob.glob(os.path.join(INSTALL_DIR, "*", ".zenith_deps_installed"))
        if not deps_files:
            console.print("No dependency markers found", style="info")
            return

        console.print(f"Found {len(deps_files)} dependency markers:", style="info")
        for deps_file in deps_files:
            tool_name = os.path.basename(os.path.dirname(deps_file))
            console.print(f"  {tool_name}", style="tool_description")

        if confirm("Do you want to reset all dependency markers?"):
            for deps_file in deps_files:
                try:
                    os.remove(deps_file)
                    tool_name = os.path.basename(os.path.dirname(deps_file))
                    console.print(
                        f"Reset dependencies for {tool_name}", style="success"
                    )
                except OSError as e:
                    console.print(f"Failed to remove {deps_file}: {e}", style="error")


__tools__ = [
    tool()
    for tool in [host2ip, base64_decode, print_contributors, reset_tool_dependencies]
]


def cli():
    tools_cli(__name__, __tools__, links=False)
