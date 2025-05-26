import os
import shutil
from collections.abc import Iterable

from rich import box
from rich.style import Style
from rich.table import Table
from rich.text import Text

from zenith.console import console
from zenith.core.config import INSTALL_DIR

BACK_COMMANDS = ["back", "return"]


class CommandCompleter:
    def __init__(self, options: Iterable[str]):
        self.options = sorted(options)

    def complete(self, text: str, state: int):
        response = None
        matches = []
        if state == 0:
            if text:
                matches = [s for s in self.options if s and s.startswith(text.lower())]
            else:
                matches = self.options[:]
        try:
            response = matches[state]
        except IndexError:
            pass
        return response


def set_readline(items: Iterable[str]):
    try:
        import readline
    except ImportError:
        pass
    else:

        if isinstance(items, list):
            readline.set_completer(CommandCompleter(items).complete)
        elif isinstance(items, dict):
            readline.set_completer(CommandCompleter(items.keys()).complete)
        else:
            readline.set_completer(CommandCompleter(list(items)).complete)
        readline.parse_and_bind("tab: complete")


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def format_tools(tools):
    cutoff = 5
    etc = False
    if len(tools) > cutoff:
        tools = tools[:cutoff]
        etc = True
    res = "".join([f"\n{str(tool)}" for tool in tools])
    if etc:
        res += "\n..."
    return res


def module_name(module):
    return module.__name__.split(".")[-1]


def prompt(path="", base_path="~"):
    encoded_path = os.path.join(base_path, path, "")
    GRAY = "\033[90m"
    RESET = "\033[0m"
    return f"\n{GRAY}Zenith{RESET} {encoded_path}# >>> "


def input_wait():
    console.print()
    input("Press [ENTER] to continue... ")
    clear_screen()


def tools_cli(name, tools, links=True):
    table = Table(box=box.ROUNDED, border_style="table_border", title_style="highlight")
    table.add_column("Name", style="tool_name", no_wrap=True, width=20)
    table.add_column("Description", style="tool_description", min_width=40)
    if links:
        table.add_column("Repository", style="link", no_wrap=True, width=30)

    tools_dict = {}
    for tool in tools:
        tools_dict[str(tool)] = tool
        args = [str(tool), tool.description]
        if links:
            text_link = Text(f"{tool.path}")
            text_link.stylize(Style(link=f"https://github.com/{tool.path}"))
            args.append(text_link)
        table.add_row(*args)

    console.print()
    console.print(table, justify="center")
    console.print()
    console.print("Available Commands:", style="info")
    console.print("  Type tool name to run", style="tool_description")
    console.print("  Type 'back' or 'return' to go back", style="tool_description")
    console.print("  Type 'exit' to quit", style="tool_description")
    console.print()
    set_readline(list(tools_dict.keys()) + BACK_COMMANDS)
    selected_tool = input(prompt(name.split(".")[-2])).strip()
    if selected_tool not in tools_dict:
        if selected_tool in BACK_COMMANDS:
            return
        if selected_tool == "exit":
            raise KeyboardInterrupt
        console.print("Invalid Command", style="error")
        console.print("Please select a valid tool from the list above", style="warning")
        console.print()
        input("Press [ENTER] to continue...")
        clear_screen()
        return tools_cli(name, tools, links)
    tool = tools_dict.get(selected_tool)

    if hasattr(tool, "install") and not tool.installed():

        console.print(f"\n{selected_tool} is not installed.", style="warning")
        from zenith.core.repo import InstallError

        if confirm(f"Do you want to install {selected_tool}?"):
            console.print(f"Installing {selected_tool}...", style="info")
            try:

                tool.install(no_confirm=True)

                if not tool.installed():
                    console.print(
                        f"Installation failed: Tool verification check failed",
                        style="error",
                    )
                    return input_wait()

                console.print(
                    f"{selected_tool} successfully installed!", style="success"
                )
            except InstallError as e:
                console.print(f"Installation failed: {str(e)}", style="error")
                return input_wait()
            except Exception as e:
                console.print(f"Unexpected error: {str(e)}", style="error")
                return input_wait()
        else:
            console.print("Installation cancelled", style="info")
            return input_wait()

    try:
        console.print(f"\nRunning {selected_tool}...", style="info")
        console.print("─" * 50, style="info")
        response = tool.run()

        if response and response > 0 and response != 256:
            console.print("─" * 50, style="info")
            console.print(
                f"Note: {selected_tool} returned a non-zero exit code ({response})",
                style="warning",
            )
            return tools_cli(name, tools, links)

    except KeyboardInterrupt:
        console.print("\nOperation cancelled by user", style="warning")
        return

    return input_wait()


def confirm(message="Do you want to?"):
    response = input(f"{message} (y/n): ").lower()
    if response:
        return response[0] == "y"
    return False
