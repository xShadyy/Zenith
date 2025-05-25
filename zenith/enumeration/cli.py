# Core
from zenith.core.menu import tools_cli
from .sherlock import sherlock
from .sublist3r import sublist3r
from .reconng import recon_ng
from .theHarvester import theharvester



__tools__ = [sherlock, sublist3r,recon_ng, theharvester]


def cli():
    tools_cli(__name__, __tools__)