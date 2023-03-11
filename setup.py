from setuptools import find_packages
from distutils.core import setup

setup(
    name="pytictac",
    version="1.0.0",
    author="Jonas Frey",
    author_email="jonfrey@ethz.ch",
    packages=find_packages(),
    python_requires=">=3.6",
    description="A small example package",
    install_requires=[],
)
