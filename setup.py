#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements():
    with open('requirements.txt') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="baato-rideshare-test",
    version="1.0.0",
    author="Auto-Generated",
    author_email="test@example.com",
    description="Comprehensive test suite for evaluating Baato.io API feasibility in ride-sharing applications",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/example/baato-rideshare-test",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Scientific/Engineering :: GIS",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "baato-test=baato_rideshare_feasibility_test:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config.json", "README.md", "requirements.txt"],
    },
    keywords="baato maps api testing ride-sharing gis nepal location",
    project_urls={
        "Bug Reports": "https://github.com/example/baato-rideshare-test/issues",
        "Source": "https://github.com/example/baato-rideshare-test",
        "Documentation": "https://docs.baato.io",
    },
)