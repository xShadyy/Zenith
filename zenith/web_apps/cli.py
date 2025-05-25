from zenith.core.menu import tools_cli
from .photon import photon

__tools__ = [photon]


def cli():
    tools_cli(__name__, __tools__)
