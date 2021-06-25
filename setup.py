"""Setup module installation."""

import os
import re

from setuptools import find_packages, setup


def load_requirements(path: str) -> list:
    with open(path, encoding="utf-8") as file:
        return [
            line.replace("==", ">=")
            for line in file.read().split("\n")
            if line and not line.startswith(("#", "-"))
        ]


if __name__ == "__main__":
    MODULE_NAME = "deltachat_kivy"
    URL = f"https://github.com/adbenitez/{MODULE_NAME}"

    with open("README.md") as f:
        long_desc = f.read()

    setup(
        name=MODULE_NAME,
        setup_requires=["setuptools_scm"],
        use_scm_version={
            "root": ".",
            "relative_to": __file__,
            "tag_regex": r"^(?P<prefix>v)?(?P<version>[^\+]+)(?P<suffix>.*)?$",
            "git_describe_command": "git describe --dirty --tags --long --match v*.*.*",
        },
        description="Delta Chat client made with Kivy",
        long_description=long_desc,
        long_description_content_type="text/markdown",
        author="adbenitez",
        author_email="adbenitez@nauta.cu",
        url=URL,
        packages=find_packages(),
        keywords="deltachat client kivy",
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: End Users/Desktop",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Programming Language :: Python :: 3",
        ],
        entry_points=f"""
            [console_scripts]
            deltachat-kivy={MODULE_NAME}.main:main
        """,
        python_requires=">=3.5",
        install_requires=load_requirements("requirements.txt"),
        extras_require={"test": load_requirements("requirements-test.txt")},
        include_package_data=True,
        zip_safe=False,
    )
