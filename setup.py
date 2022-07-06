# -*- coding: utf-8 -*-
# Copyright IRT Antoine de Saint Exupéry et Université Paul Sabatier Toulouse III - All
# rights reserved. DEEL is a research program operated by IVADO, IRT Saint Exupéry,
# CRIAQ and ANITI - https://www.deel.ai/
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from setuptools import find_namespace_packages
from setuptools import setup

dev_requires = [
    "black",
    "flake8",
    "flake8-black",
    "mypy",
    "pytest",
    "numpy",
]

docs_requires = [
    "sphinx==3.3.1",
    "recommonmark",
    "sphinx_rtd_theme",
    "sphinx_markdown_builder",
    "sphinx_autodoc_typehints",
    "sphinxcontrib_katex",
    "ipython",  # required for Pygments
]

setup(
    # Name of the package:
    name="deel-datasets",
    # Version of the package:
    version="0.0.7",
    # Find the package automatically (include everything):
    packages=find_namespace_packages(include=["deel.*"]),
    # Author information:
    author="DEEL",
    author_email="justin.plakoo@irt-saintexupery.com",
    # Description of the package:
    description="Dataset loader for DEEL datasets",
    long_description=open("README.md").read(),
    # URL for sources:
    url="https://forge.deel.ai/devops/deel_dataset_manager",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    # License:
    license="MIT",
    # Requirements:
    install_requires=[
        "webdavclient3==0.13",
        "tqdm",
        "h5py",
        "pyyaml",
        "psutil",
        "numpy",
        "Pillow",
        "PyYAML",
    ],
    extras_require={"dev": dev_requires, "docs": docs_requires},
)
