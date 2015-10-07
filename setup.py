import os

from setuptools import setup, find_packages

NAME = "Go-Smart Simulation Architecture -- Container Support Module"
DESCRIPTION = """
Python module for interaction with the Go-Smart Simulation Architecture,
providing simple, in-container tools for authors of GSSA families, that
is Docker-sandboxed simulation codes.
"""
LICENSE = "MIT License"
URL = "https://github.com/numa-engineering/gosmart-gssa_container-module"
AUTHOR = "Phil Weir"
EMAIL = "phil.weir@numa.ie"
PACKAGES = find_packages(exclude=["tests*"])
META_PATH = os.path.join("gosmart", "__init__.py")
KEYWORDS = ["gssa", "gosmart", "simulation", "docker"]

# Note that this Python module is MIT licensed, unlike most of GSSA,
# as it allows code developers to write their own self-contained
# containers numerics without sharing requirements (beyond security auditing)
CLASSIFIERS = [
    "Development Status :: Alpha",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

INSTALL_REQUIRES = []
HERE = os.path.abspath(os.path.dirname(__file__))


if __name__ == "__main__":
    setup(
        name=NAME,
        description=DESCRIPTION,
        license=LICENSE,
        url=URL,
        author=AUTHOR,
        author_email=EMAIL,
        maintainer=AUTHOR,
        maintainer_email=EMAIL,
        keywords=KEYWORDS,
        packages=PACKAGES,
        zip_safe=False,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES
    )
