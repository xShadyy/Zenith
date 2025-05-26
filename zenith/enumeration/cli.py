from zenith.core.menu import tools_cli

from .sherlock import sherlock

__tools__ = [sherlock]


def cli():
    tools_cli(__name__, __tools__)
