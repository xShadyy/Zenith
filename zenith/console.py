from rich.console import Console
from rich.theme import Theme
from rich.traceback import install

install()

zenith_theme = Theme(
    {
        "command": "black on white",
        "subtitle": "bold black",
        "warning": "bold yellow",
        "error": "bold red",
        "success": "bold green",
        "tool_name": "bright_cyan",
        "tool_description": "bright_white",
        "prompt": "bright_blue",
        "table_border": "white",
        "link": "blue underline",
        "skull_art": "bold white",
        "menu_category": "bright_yellow",
        "info": "cyan",
        "highlight": "bold bright_white on blue",
    }
)
console = Console(theme=zenith_theme)
