# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import unicode_literals

import io
import os.path
import sys

import setuptools


MODULE_NAME = "sqliteschema"
REPOSITORY_URL = "https://github.com/thombashi/{:s}".format(MODULE_NAME)
REQUIREMENT_DIR = "requirements"
ENCODING = "utf8"

pkg_info = {}


def need_pytest():
    return set(["pytest", "test", "ptr"]).intersection(sys.argv)


def get_release_command_class():
    try:
        from releasecmd import ReleaseCommand
    except ImportError:
        return {}

    return {"release": ReleaseCommand}


with open(os.path.join(MODULE_NAME, "__version__.py")) as f:
    exec(f.read(), pkg_info)

with io.open("README.rst", encoding=ENCODING) as fp:
    long_description = fp.read()

with open(os.path.join(REQUIREMENT_DIR, "requirements.txt")) as f:
    install_requires = [line.strip() for line in f if line.strip()]

with open(os.path.join(REQUIREMENT_DIR, "test_requirements.txt")) as f:
    tests_requires = [line.strip() for line in f if line.strip()]

SETUPTOOLS_REQUIRES = ["setuptools>=38.3.0"]
PYTEST_RUNNER_REQUIRES = ["pytest-runner"] if need_pytest() else []

dumps_requires = ["pytablewriter>=0.40.0,<1.0.0"]
tests_requires = frozenset(tests_requires + dumps_requires)

setuptools.setup(
    name=MODULE_NAME,
    version=pkg_info["__version__"],
    url=REPOSITORY_URL,

    author=pkg_info["__author__"],
    author_email=pkg_info["__email__"],
    description="""
    A Python library to dump table schema of a SQLite database file.
    """,
    include_package_data=True,
    keywords=["SQLite", "library", "schema"],
    license=pkg_info["__license__"],
    long_description=long_description,
    packages=setuptools.find_packages(exclude=["test*"]),
    project_urls={
        "Tracker": "{:s}/issues".format(REPOSITORY_URL),
    },
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*',

    install_requires=SETUPTOOLS_REQUIRES + install_requires,
    setup_requires=SETUPTOOLS_REQUIRES + PYTEST_RUNNER_REQUIRES,
    tests_require=tests_requires,
    extras_require={
        "build": ["wheel"],
        "dumps": dumps_requires,
        "release": ["releasecmd>=0.0.12,<0.1.0"],
        "test": tests_requires,
    },

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
    ],
    cmdclass=get_release_command_class())
