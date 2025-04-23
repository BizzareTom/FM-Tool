# pylint: disable=exec-used
import os
from typing import Dict, Union, List

from setuptools import setup, find_packages  # type: ignore[import-untyped]

source_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fm_tool")

version_scope: Dict[str, Dict[str, str]] = {}
with open(os.path.join(source_root, "version.py"), encoding="utf-8") as f:
    exec(f.read(), version_scope)
version = version_scope["__version__"]

project_scope: Dict[str, Dict[str, Union[str, List[str]]]] = {}
with open(os.path.join(source_root, "project.py"), encoding="utf-8") as f:
    exec(f.read(), project_scope)
project = project_scope["project"]

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

classifiers = [
    "Intended Audience :: End Users/Desktop",

    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",

    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",

    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",

    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy"
]

classifiers.extend(project["categories"])

if version["tag"] == "alpha":
    classifiers.append("Development Status :: 3 - Alpha")

if version["tag"] == "beta":
    classifiers.append("Development Status :: 4 - Beta")

if version["tag"] == "stable":
    classifiers.append("Development Status :: 5 - Production/Stable")

del project["categories"]
del project["year"]

setup(
    version=version["short"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GPLv3",
    packages=find_packages(exclude=["tests"]),
    entry_points={ "gui_scripts": [ "FM-Tool = fm_tool.__main__:main" ] },
    install_requires=[
        "requests>=2.32.3",
        "pyperclip>=1.9.0",
        "pillow>=11.2.1"
    ],
    python_requires=">=3.9",
    include_package_data=True,
    zip_safe=False,
    classifiers=classifiers,
    **project
)
