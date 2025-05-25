#!/usr/bin/env python3
import argparse
import platform
import sys

import pyfiglet
from rich.columns import Columns
from rich.text import Text

import zenith.core.information_gathering
import zenith.core.networking
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

# Config
config = get_config()

# Terms and Conditions
TERMS = """
I shall not use Zenith to:
(i) upload or otherwise transmit, display or distribute any
content that infringes any trademark, trade secret, copyright
or other proprietary or intellectual property rights of any
person; (ii) upload or otherwise transmit any material that contains
software viruses or any other computer code, files or programs
designed to interrupt, destroy or limit the functionality of any
computer software or hardware or telecommunications equipment;
"""

MENU_ITEMS = [
    zenith.core.information_gathering,
    zenith.core.networking,
    zenith.core.web_apps,
    zenith.core.passwords,
    zenith.core.obfuscation,
    zenith.core.utilities,
]
BUILTIN_FUNCTIONS = {
    "exit": lambda: exec("raise KeyboardInterrupt"),
}
items = {}
for item in MENU_ITEMS:
    items[module_name(item)] = item
commands = list(items.keys()) + list(BUILTIN_FUNCTIONS.keys())


def print_menu_items():
    cols = []
    for value in MENU_ITEMS:
        name = module_name(value)
        tools = format_tools(value.__tools__)
        tools_str = Text()
        tools_str.append("\n")
        tools_str.append(name, style="command")
        tools_str.append(tools)
        cols.append(tools_str)
    console.print(Columns(cols, equal=True, expand=True))
    for key in BUILTIN_FUNCTIONS:
        console.print(key, style="command")


def agreement():
    while not config.getboolean("zenith", "agreement"):
        clear_screen()
        console.print(TERMS, style="bold yellow")
        agree = input("You must agree to our terms and conditions first (Y/n) ")
        if agree.lower().startswith("y"):
            config.set("zenith", "agreement", "true")


def mainloop():
    agreement()
    clear_screen()
    # Render banner with custom 'slant' font
    banner = pyfiglet.figlet_format("Zenith", font="slant")
    console.print(banner, style="bold white")
    print_menu_items()
    selected = input(prompt()).strip()
    if not selected or selected not in commands:
        console.print("Invalid Command", style="bold yellow")
        clear_screen()
        return
    if selected in BUILTIN_FUNCTIONS:
        return BUILTIN_FUNCTIONS[selected]()
    try:
        return items[selected].cli()
    except Exception as error:
        console.print(str(error))
        console.print_exception()


def info():
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
        console.print(f"# {key}")
        console.print(value, end="\n\n")


def interactive():
    try:
        while True:
            set_readline(commands)
            mainloop()
    except KeyboardInterrupt:
        console.print("\nExiting...")
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
