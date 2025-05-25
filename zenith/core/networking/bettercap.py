import os
from shutil import which

from zenith.core.repo import GitHubRepo


class BettercapRepo(GitHubRepo):
    def __init__(self):
        super().__init__(
            path="bettercap/bettercap",
            install={
                "pacman": "bettercap",  # Available in Arch repos
                "brew": "bettercap",
                "apt-get": "sudo apt install -y golang git build-essential libpcap-dev libusb-1.0-0-dev libnetfilter-queue-dev && go install github.com/bettercap/bettercap@latest",
                "yum": "sudo yum install -y golang git gcc libpcap-devel libusb-devel && go install github.com/bettercap/bettercap@latest",
                "dnf": "sudo dnf install -y golang git gcc libpcap-devel libusb-devel && go install github.com/bettercap/bettercap@latest",
                "linux": "sudo apt install -y golang git build-essential libpcap-dev libusb-1.0-0-dev libnetfilter-queue-dev && go install github.com/bettercap/bettercap@latest",
                "arch": "sudo pacman -S --noconfirm bettercap",
            },
            description="Swiss army knife for network attacks and monitoring",
        )

    def installed(self):
        return which("bettercap")

    def install(self):
        super().install(clone=False)

    def run(self):
        print("Please note that bettercap must be run with sudo")
        return os.system("sudo bettercap")


bettercap = BettercapRepo()
