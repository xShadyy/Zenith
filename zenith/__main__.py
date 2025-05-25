import argparse
import platform
import sys
from random import choice
from socket import gethostbyname

import pyfiglet
from rich.align import Align
from rich.columns import Columns
from rich.text import Text

import zenith.core.enumeration
import zenith.core.network
import zenith.core.obfuscation
import zenith.core.passwords
import zenith.core.utilities
import zenith.core.web_apps
from zenith.console import console
from zenith.core.config import CONFIG_FILE, get_config, write_config
from zenith.core.menu import (
    clear_screen,
    format_tools,
    module_name,
    prompt,
    set_readline,
)

config = get_config()

SKULL_ART = r"""
"""

TERMS = """
"""

MENU_ITEMS = [
    zenith.core.enumeration,
    zenith.core.network,
    zenith.core.web_apps,
    zenith.core.passwords,
    zenith.core.obfuscation,
    zenith.core.utilities,
]
BUILTIN_FUNCTIONS = {
    "exit": lambda: exec("raise KeyboardInterrupt"),
}
items = {module_name(item): item for item in MENU_ITEMS}
commands = list(items.keys()) + list(BUILTIN_FUNCTIONS.keys())


def print_menu_items():
    console.print("Available Categories:", style="menu_category")
    console.print()
    cols = []
    for value in MENU_ITEMS:
        name = module_name(value)
        tools = format_tools(value.__tools__)
        tools_str = Text()
        tools_str.append(name.upper(), style="command")
        tools_str.append(tools, style="tool_description")
        cols.append(tools_str)
    console.print(Columns(cols, equal=True, expand=True))
    console.print()
    console.print("System Commands:", style="menu_category")
    for key in BUILTIN_FUNCTIONS:
        console.print(f"  {key}", style="command")
    console.print()


def agreement():
    while not config.getboolean("zenith", "agreement"):
        clear_screen()
        console.print("Terms and Conditions", style="highlight")
        console.print()
        console.print(TERMS, style="warning")
        console.print()
        agree = input("You must agree to our terms and conditions first (Y/n) ")
        if agree.lower().startswith("y"):
            config.set("zenith", "agreement", "true")


def mainloop():
    agreement()
    clear_screen()
    console.print(Align.center(SKULL_ART), style="bold white on black")
    console.print()
    console.print()
    console.print("Penetration Testing Framework", style="info", justify="center")
    console.print("Developed by: xShadyy", style="info", justify="center")
    console.print("─" * 60, style="table_border", justify="center")
    console.print()
    print_menu_items()
    selected = input(prompt()).strip()
    if not selected or selected not in commands:
        console.print("Invalid Command", style="error")
        console.print(
            "Please select a valid option from the menu above", style="warning"
        )
        console.print()
        input("Press [ENTER] to continue...")
        clear_screen()
        return
    if selected in BUILTIN_FUNCTIONS:
        return BUILTIN_FUNCTIONS[selected]()
    try:
        return items[selected].cli()
    except Exception as error:
        console.print(f"Error: {str(error)}", style="error")
        console.print_exception()


def info():
    console.print("System Information", style="highlight")
    console.print()
    data = {}
    with open(CONFIG_FILE, encoding="utf-8") as file:
        data["Config File"] = file.read().strip()
    data["Python Version"] = platform.python_version()
    data["Platform"] = platform.platform()
    os_name = config.get("zenith", "os")
    if os_name == "macos":
        data["macOS"] = platform.mac_ver()[0]
    elif os_name == "windows":
        data["Windows"] = platform.win32_ver()[0]
    for key, value in data.items():
        console.print(f"{key}", style="info")
        console.print(value, style="tool_description")
        console.print()


def interactive():
    try:
        while True:
            set_readline(commands)
            mainloop()
    except KeyboardInterrupt:
        console.print("\nExiting Zenith...", style="info")
        write_config(config)
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="A Modular Framework")
    parser.add_argument("-i", "--info", action="store_true", help="gets zenith info")
    parser.add_argument("-s", "--suggest", action="store_true", help="suggest a tool")
    args = parser.parse_args()
    if args.info:
        info()
    elif args.suggest:
        zenith.core.utilities.suggest_tool()
    else:
        interactive()


if __name__ == "__main__":
    main()
