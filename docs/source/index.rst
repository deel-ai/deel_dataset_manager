.. DEEL Dataset Manager documentation master file, created by
   sphinx-quickstart on Tue Nov 17 14:51:29 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to DEEL Dataset Manager's documentation!
================================================

This project aims to ease the installation and usage of self-hosted and proprietary
datasets in artificial intelligence projects.

Installation
------------

You can install the manager directly from pypi:

.. code-block:: bash

   # Note: This currently does not work, see the README.
   pip install deel-datasets


Configuration
-------------

The configuration file specifies how the datasets should be downloaded, or
if the datasets do no have to be downloaded (e.g. on Google Cloud).

The configuration file should be at ``$HOME/.deel/config.yml``:

* On Windows system it is ``C:\Users\$USERNAME\.deel\config.yml`` unless you
  have set the `HOME` environment variable.
* The ``DEEL_CONFIGURATION_FILE`` environment variable can be used to specify the
  location of the configuration file if you do not want to use the default one.

The configuration file is a **YAML** file, see :ref:`configuration` for more details.

DEEL dataset plugin
-------------------

Without plugins, the manager is only able to download a dataset and returns the path to
the local folder containing it (after download).
By installing plugins, you gain access to automatic way of loading datasets or pre-processing
data.

Plugins are Python packages with proper
`entry points <https://packaging.python.org/specifications/entry-points/>`_.
See :ref:`plugins` for more information on how to create plugins.

Basic usage
-----------

To load a dataset, you can simply do:

.. code-block:: python

   import deel.datasets

   # Load the default mode of dataset-a dataset:
   dataset = deel.datasets.load("dataset-a")

   # Load the tensorflow version of the dataset-b dataset (default mode for dataset-b):
   dataset = deel.datasets.load("dataset-b")

   # Load the pytorch version of the dataset-b dataset:
   dataset = deel.datasets.load("dataset-b", mode="pytorch")

The :py:func:`deel.datasets.load` function is the basic entry to access the datasets.
By passing ``with_info=True``, extra information can be retrieved as a python
dictionary. Information are not standardized, so each dataset may provide
different ones:
The ``mode`` argument can be used to load different "version" of the dataset. By default,
only the ``path`` mode is available and will return the path to the local folder
containing the dataset.
By installing plugins, new modes can be made available for each datasets (see plugin
implementation below).

.. code-block:: python

   import deel.datasets

   # Load the tensorflow version of the dataset-b dataset:
   dataset, info = deel.datasets.load("dataset-b", mode="tensorflow", with_info=True)

   print(info["classes"])

The function can take extra parameters depending on the chosen dataset and mode,
for instance, you can specify the percentage of training data for the ``dataset-b``
dataset:

.. code-block:: python

   import deel.datasets

   # Load the tensorflow version of the dataset-b dataset:
   dataset = deel.datasets.load("dataset-b", mode="tensorflow", percent_train=60)

Uninstalling
------------

To uninstall the DEEL dataset manager package , simply run ``pip uninstall``:

.. code-block:: bash

   pip uninstall deel-datasets

.. toctree::
   :maxdepth: 4
   :caption: Contents:
   :glob:

   configuration
   plugins
   cli

   deel.datasets

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
