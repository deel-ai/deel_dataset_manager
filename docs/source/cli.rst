.. _cli:

Command Line
------------

The ``deel-datasets`` package comes with some command line utilities that
can be accessed using:

.. code-block:: bash

    python -m deel.datasets ARGS...

The ``--help`` option can be used to view the full capabilities of the command
line program.
By default, the program uses the configuration at ``$HOME/.deel/config.yml`` (or
specified by the environment variable), but the ``-c`` argument can be used to
specified a custom configuration file.

.. code-block:: bash

    $ python -m deel.datasets --help
    usage: __main__.py [-h] [-c CONFIG] {check,list,download,remove} ...

    DEEL dataset manager

    positional arguments:
    {check,list,download,remove}
                            sub-command help
        check               check config
        list                list datasets
        download            download datasets
        remove              remove local datasets

    optional arguments:
    -h, --help            show this help message and exit
    -c CONFIG, --config CONFIG
                            configuration file to use

Listing datasets
................

The ``list`` command can be used to list available and installed datasets.

.. code-block:: bash

    $ python -m deel.datasets list --help
    usage: __main__.py list [-h] [-l] [prov_conf]

    positional arguments:
    prov_conf    provider in configuration to use

    optional arguments:
    -h, --help   show this help message and exit
    -l, --local  for a non-local provider (e.g., WebDAV), list only local datasets

If the configuration specify remote providers (e.g., WebDAV), this will list
the datasets available remotely (from all providers).
To list the dataset already downloaded, you can use the ``--local`` option.

.. code-block:: bash

    $ python -m deel.datasets list
    Listing datasets at https://datasets.company.com:
    dataset-a: 3.0.1 [latest], 3.0.0
    dataset-b: 1.0 [latest]
    dataset-c: 1.0 [latest]
    $ python -m deel.datasets list --local
    Listing datasets at /opt/datasets:
    dataset-a: 3.0.1 [latest], 3.0.0
    dataset-c: 1.0 [latest]

Downloading datasets
....................

Datasets are automatically downloaded when required, but you can download them
manually using the ``download`` command.

.. code-block:: bash

    $ python -m deel.datasets download --help
    usage: __main__.py download [-h] [-p [PROV_CONF]] [-f] datasets [datasets ...]

    positional arguments:
    datasets              datasets to download, format name:version with :version being optional

    optional arguments:
    -h, --help            show this help message and exit
    -p [PROV_CONF], --provider [PROV_CONF]
                            provider in configuration to use
    -f, --force           force download

If the configuration does not specify a remote provider, the command does nothing
except displaying some information.
The ``-p`` argument can be used to specify the provider to download the dataset
from in case the dataset is available from multiple providers.
The ``:VERSION`` can be omitted, in which case ``:latest`` is implied. To force
the re-download of a dataset, the ``--force`` option can be used.

.. code-block:: bash

    $ python -m deel.datasets download dataset-a:3.0.0
    Fetching dataset-a:3.0.0...
    dataset-a-3.0.0-20191004.zip: 100%|██████████████████████| 122M/122M [00:03<00:00, 39.3Mbytes/s]
    Dataset dataset-a:3.0.0 stored at '/opt/datasets/dataset-a/3.0.0'.

Removing datasets
.................

The ``remove`` command can be used to delete local datasets.

.. code-block:: bash

    $ python -m deel.datasets remove --help
    usage: __main__.py remove [-h] [-a ALL] [datasets [datasets ...]]

    positional arguments:
    datasets           datasets to remove, format name:version, [...]

    optional arguments:
    -h, --help         show this help message and exit
    -a ALL, --all ALL  remove all local datasets

If ``:VERSION`` is omitted, the whole dataset corresponding to ``NAME`` is
deleted (all the versions).
If the ``--all`` option is used, all datasets are removed from the local storage.
