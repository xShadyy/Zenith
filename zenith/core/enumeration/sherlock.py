import os

from zenith.core.menu import set_readline
from zenith.core.repo import GitHubRepo
from zenith.core.usernames import add_username, get_usernames


class SherlockRepo(GitHubRepo):
    def __init__(self):
        super().__init__(
            path="sherlock-project/sherlock",
            install={
                "pip": "requirements.txt",
                "apt-get": "python3-dev libssl-dev libffi-dev",
                "yum": "python3-devel openssl-devel libffi-devel",
                "dnf": "python3-devel openssl-devel libffi-devel",
                "pacman": "python python-pip",
                "brew": "python3",
            },
            description="Hunt down social media accounts by username across social networks",
        )

    def run(self):
        os.chdir(self.full_path)
        usernames = get_usernames()
        set_readline(usernames)
        user_usernames = input("\nEnter one or more usernames: ").strip()
        for username in user_usernames.split():
            if username not in usernames:
                add_username(username)
        return os.system(f"python3 sherlock {user_usernames}")


sherlock = SherlockRepo()
