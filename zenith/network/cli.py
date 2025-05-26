from zenith.core.menu import tools_cli
from .nmap import nmap

__tools__ = [nmap]


def cli():
    tools_cli(__name__, __tools__)
