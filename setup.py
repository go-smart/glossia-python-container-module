import os
import sys

from setuptools import setup, find_packages

NAME = "Go-Smart Simulation Architecture -- Container Support Module"
DESCRIPTION = """
Python module for interaction with the Go-Smart Simulation Architecture,
providing simple, in-container tools for authors of GSSA families, that
is Docker-sandboxed simulation codes.
"""
LICENSE = "MIT License"
URL = "https://github.com/gosmart/gssa-container-module"
AUTHOR = "Phil Weir"
EMAIL = "phil.weir@numa.ie"
META_PATH = os.path.join("gosmart", "__init__.py")
KEYWORDS = ["gssa", "gosmart", "simulation", "docker"]
INSTALL_REQUIRES = ['pyyaml']
INSTALL_REQUIRES_3 = ['Click', 'pyyaml', 'hachiko']

if sys.version_info < (3,):
    excluded_packages = ["gosmart.scripts.*"]
    entry_points = ""
else:
    excluded_packages = []
    entry_points = '''
        [console_scripts]
        gosling=gosmart.scripts.gosling:cli
    '''
    INSTALL_REQUIRES += INSTALL_REQUIRES_3

PACKAGES = find_packages(exclude=["tests*"] + excluded_packages)

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
        install_requires=INSTALL_REQUIRES,
        include_package_data=True,
        entry_points=entry_points
    )
