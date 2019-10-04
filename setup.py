#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
from setuptools import setup, find_packages
 
# Ceci n'est qu'un appel de fonction. Mais il est trèèèèèèèèèèès long
# et il comporte beaucoup de paramètres
setup(
 
    # le nom de votre bibliothèque, tel qu'il apparaitre sur pypi
    name='deel',
 
    # la version du code
    version="0.0.3",
    packages=find_packages(),
    author="DEEL",
    author_email="collaborateurs.du.projet.deel@irt-saintexupery.com",
    description="Dataset Loader for DEEL datasets",
    long_description=open('README.md').read(),
    include_package_data=True,
    url='https://forge.deel.ai/bertrand.cayssiols/deel_dataset_manager',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    license="WTFPL",
)