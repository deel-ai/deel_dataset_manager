# -*- encoding: utf-8 -*-

from setuptools import setup, find_namespace_packages

dev_requires = [
    "black",
    "flake8",
    "flake8-black",
    "mypy",
    "pytest",
]

setup(
    # Name of the package:
    name="deel-datasets",
    # Version of the package:
    version="0.0.5",
    # Find the package automatically (include everything):
    packages=find_namespace_packages(include=["deel.*"]),
    package_data={"deel.datasets": ["default-config.yml"]},
    # Author information:
    author="DEEL",
    author_email="collaborateurs.du.projet.deel@irt-saintexupery.com",
    # Description of the package:
    description="Dataset loader for DEEL datasets",
    long_description=open("README.md").read(),
    include_package_data=True,
    # URL for sources:
    url="https://forge.deel.ai/devops/deel_dataset_manager",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    # License:
    license="WTFPL",
    # Requirements:
    install_requires=["webdavclient3==0.13", "tqdm", "h5py", "pyyaml", "psutil",],
    extras_require={"dev": dev_requires},
)
