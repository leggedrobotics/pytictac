from setuptools import find_packages
from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pytictac",
    version="1.0.4",
    author="Jonas Frey",
    author_email="jonfrey@ethz.ch",
    packages=find_packages(),
    python_requires=">=3.6",
    description="A small example package",
    install_requires=[],
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
