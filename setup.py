#!/usr/bin/env python
import os
import sys
from typing import Any, Dict, List

from setuptools import Command, find_packages, setup

# Package meta-data.
NAME = "zenith"
DESCRIPTION = "Flexible Framework for Conducting Penetration Tests"
URL = "https://github.com/zenith-collective/Zenith"
GIT_URL = URL
PROJECT_URLS = {
    "Documentation": GIT_URL + "/blob/main/README.md",
    "Issue Tracker": GIT_URL + "/issues",
    "Source": GIT_URL,
}
EMAIL = "tymoteusz.netter@gmail.com"
AUTHOR = "Zenith-Collective"
REQUIRES_PYTHON = ">=3.12.0"

here = os.path.abspath(os.path.dirname(__file__))

pkg_vars: dict[str, Any] = {}
with open(os.path.join(here, NAME, "__version__.py"), encoding="utf-8") as f:
    exec(f.read(), pkg_vars)

try:
    with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


def get_requirements(path: str) -> list[str]:
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


class TagCommand(Command):
    description = "Push latest version as git tag."
    user_options: list[Any] = []

    @staticmethod
    def status(s: str) -> None:
        print(f"\033[1m{s}\033[0m")

    def initialize_options(self) -> None:
        pass

    def finalize_options(self) -> None:
        pass

    def run(self) -> None:
        self.status("Pushing git tags…")
        version = pkg_vars.get("__version__")
        os.system(f"git tag v{version}")
        os.system("git push --tags")
        sys.exit()


setup(
    name=NAME,
    version=pkg_vars.get("__version__"),
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    project_urls=PROJECT_URLS,
    python_requires=REQUIRES_PYTHON,
    packages=find_packages(exclude=["tests*", "*.tests*", "tests"]),
    install_requires=get_requirements("requirements.txt"),
    extras_require={
        "dev": get_requirements("requirements-dev.txt"),
    },
    entry_points={
        "console_scripts": [
            "zenith=zenith.__main__:main",
        ],
    },
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Tools",
    ],
    cmdclass={"push_tag": TagCommand},
)
