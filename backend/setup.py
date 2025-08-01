#!/usr/bin/env python3
from setuptools import setup, find_packages
import os

# Get version from app/__init__.py
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'app', '__init__.py')
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"').strip("'")
    return "1.0.0"

setup(
    name="photoid-backend",
    version=get_version(),
    description="PhotoID AI Backend Application",
    packages=find_packages(),
    python_requires=">=3.11,<3.13",
    install_requires=[],
    author="PhotoID Team",
    author_email="team@photoid.com",
    url="https://github.com/emreliman/PhotoId",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)