# Core
from zenith.core.menu import tools_cli

from .cuteit import cuteit

__tools__ = [cuteit]


def cli():
    tools_cli(__name__, __tools__)
