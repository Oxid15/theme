import os
import sys
import setuptools

sys.path.append(os.path.abspath(__file__))
from theme import __version__, __author__, __author_email__


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="theme",
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    license='MIT',
    description="Simple CLI labeling tool for text classification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Linux"
    ],
    package_dir={"theme": "./theme"},
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    install_requires=[
        'numpy',
        'pandas',
    ]
)
