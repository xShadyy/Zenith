import os

from zenith.core.repo import GitHubRepo


class CuppRepo(GitHubRepo):
    def __init__(self):
        super().__init__(
            path="Mebus/cupp",
            install=None,
            description="Common User Passwords Profiler",
        )

    def run(self):
        os.chdir(self.full_path)
        return os.system("python3 cupp.py -i")


cupp = CuppRepo()
