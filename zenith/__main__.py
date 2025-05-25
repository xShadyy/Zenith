import argparse
import platform
import sys
from random import choice
from socket import gethostbyname

import pyfiglet
from rich.align import Align

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
    module_name,
    prompt,
    set_readline,
)

config = get_config()

def create_skull_art():
    from rich.text import Text
    
    skull_lines = [
        "          .                                                      .",
        "        .n                   .                 .                  n.",
        "  .   .dP                  dP                   9b                 9b.    .",
        " 4    qXb         .       dX                     Xb       .        dXp     t",
        "dX.    9Xb      .dXb    __                         __    dXb.     dXP     .Xb",
        "9XXb._       _.dXXXXb dXXXXbo.                 .odXXXXb dXXXXb._       _.dXXP",
        " 9XXXXXXXXXXXXXXXXXXXVXXXXXXXXOo.           .oOXXXXXXXXVXXXXXXXXXXXXXXXXXXXP",
        "  9XXXXXXXXXXXXXXXXXXXXX'~   ~OOO8b   d8OOO'~   ~XXXXXXXXXXXXXXXXXXXXXP'",
        "    9XXXXXXXXXXXP' 9XX'   PROJECT   98v8P'  ZENITH   XXP' 9XXXXXXXXXXXP'",
        "        ~~~~~~~       9X.          .db|db.          .XP       ~~~~~~~",
        "                        )b.  .dbo.dP'v'9b.odb.  .dX(",
        "                      ,dXXXXXXXXXXXb     dXXXXXXXXXXXb.",
        "                     dXXXXXXXXXXXP'   .   9XXXXXXXXXXXb",
        "                    dXXXXXXXXXXXXb   d|b   dXXXXXXXXXXXXb",
        "                    9XXb'   XXXXXb.dX|Xb.dXXXXX'   dXXP",
        "                     '      9XXXXXX(   )XXXXXXP      '",
        "                              XXXX X.v'.X XXXX",
        "                              XP^X'b   d'X^XX",
        "                              X. 9     '  P )X",
        "                              b         '  d'",
        "                                            '"
    ]
    
    text = Text()
    for line in skull_lines:
        if "PROJECT" in line and "ZENITH" in line:
            parts = line.split("PROJECT")
            text.append(parts[0])
            text.append("PROJECT", style="red")
            
            remaining = parts[1].split("ZENITH")
            text.append(remaining[0])
            text.append("ZENITH", style="red")
            text.append(remaining[1])
        else:
            text.append(line)
        text.append("\n")
    
    return text

SKULL_ART = create_skull_art()

TERMS = """
I shall not use Zenith to engage in any activity that infringes 
intellectual property rights, violates privacy or 
security, distributes malicious code,
or otherwise harms individuals, systems, or networks.
I shall not use Zenith to manipulate or reverse engineer the platform,
exploit it for unauthorized access,
facilitate fraudulent, deceptive, or abusive behavior,
or use it in any other unlawful or unethical manner.
Author is not responsible for any misuse of this tool.
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
    
    # Create columns for categories
    from rich.columns import Columns
    from rich.text import Text
    
    category_texts = []
    for value in MENU_ITEMS:
        name = module_name(value)
        text = Text(name.upper(), style="command")
        category_texts.append(text)
    
    console.print(Columns(category_texts, equal=True, expand=True))
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
    console.print(Align.center(SKULL_ART), style="skull_art")
    console.print("Developed by: xShadyy", style="subtitle", justify="center")
    console.print("─" * 60, style="table_border", justify="center")
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
