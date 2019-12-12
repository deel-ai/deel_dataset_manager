# DEEL dataset manager

This project aims to ease the installation and usage of the datasets for the DEEL
project.

## Installation:

You can install this package by using `pip`. If you have set-up SSH keys properly
for [https://forge.deel.ai](https://forge.deel.ai), you can use the SSH version:

```
pip install git+ssh://git@forge.deel.ai:22012/devops/deel_dataset_manager.git
```

Otherwize the HTTPS version should work but you will have to enter your credentials
manually:

```
pip install git+https://forge.deel.ai/devops/deel_dataset_manager.git
```


## Basic usage

Each DEEL dataset has its own structure (e.g., `tensorflow`, `pytorch`, etc.). To load
a dataset, you can simply do:

```python
import deel.datasets

# Load the default mode of landcover dataset:
landcover = deel.datasets.load("landcover")

# Load the tensorflow version of the blink dataset:
blink_tf = deel.datasets.load("blink", mode="tensorflow")

# Load the pytorch version of the blink dataset:
blink_torch = deel.datasets.load("blink", mode="pytorch")
```

The `deel.datasets.load` function is the basic entry to access the datasets.
The function can take extra parameters depending on the chosen dataset and mode,
for instance, you can specify the percentage of training data for the `blink`
dataset:

```python
import deel.datasets

# Load the tensorflow version of the blink dataset:
blink_tf = deel.datasets.load("blink", mode="tensorflow", percent_train=60)
```

The following files contain examples for the `blink` and `landcover` dataset:

- [examples/landcover/tensorflow_example.py](examples/landcover/tensorflow_example.py)
- [examples/landcover/load_example.py](examples/landcover/load_example.py)

## Configuration:

While a configuration file is not strictly required for the moment, it is still recommended
to create one.
The configuration file specifies where the datasets should be downloaded from, or
if the datasets do no have to be downloaded (e.g. on Google Cloud).

The configuration file should be at `$HOME/.deel/config.yml` (the `DEEL_CONFIGURATION_FILE`
can be used to specify the location of the configuration file).

The configuration file is a simple YAML file:

```yaml
# Version of the configuration (currently 1):
version: 1

# Provider for the datasets:
provider:
    type: webdav
    url: https://datasets.deel.ai
    auth:
        method: "simple"
        username: "deel-datasets"
        password: "e]{qE/Pc65z'Nt?zLe-cK!_y?6f6"

# Local storage for the datasets:
path: /home/username/.deel/datasets
```

### GCloud configuration

If you are using a Google Cloud virtual machine, you can avoid downloading the datasets
by mounting and using the `deel-datasets` gcloud drive.

You first need to attach the disk to your machine using the Google Cloud console, then run
the following command that add a line to `/etc/fstab` to ease the mount of the drive (this
assumes you are using `bash` or a compliant shell):

```
echo UUID=`sudo blkid -s UUID -o value /dev/disk/by-id/google-deel-datasets` /mnt/deel-datasets ext4 discard,defaults,nofail 0 2 | sudo tee -a /etc/fstab
```

You can then mount the drive:

```
sudo mount /mnt/deel-datasets
```

You only need to do this manually the first time. The disk will be automatically mounted on the
next restarts of the virtual machine.

You then need to configure the package for Google Cloud. You can do so by creating a
file under `$HOME/.deel/config.yml` with the following content:

```yaml
version: 1

provider: gcloud
```

### Providers

Currently available providers are `webdav`, `local` and `gcloud`.
The `webdav` provider is the default-one and will fetch datasets from a WebDAV server
and needs at least the `url` configuration parameter (`auth` is not mandatory but required
for the `https://datasets.deel.ai` server).
The `local` provider does not require any extra configuration and will simply
fetch data from the specified `path`.

When using the `webdav` provider, the `path` parameter indicates where the datasets
should be stored locally.

The `gcloud` provider is similar to the `local` provider, except that it will try to
locate the dataset storage location automatically based on the currently mounted drives.


## Contributing

The first step for contributing is to open
[a new issue](https://forge.deel.ai/DevOps/deel_dataset_manager/issues/new).

You then need to fork this repository, or create a dedicated branch if you have
sufficient privileges.
Once you are done, you can open a merge request for your changes to be integrated
in this repository.

### Adding a new dataset

#### 1. Provide the dataset

The first step to add a dataset is to upload one to the DEEL server or store it
on the `deel-datasets` gcloud-drive.

#### 2. Create the interface

The second step is to create the `python` interface. The `deel.datasets` package
is written such that adding extra datasets should be quite easy.
Assuming you want to add a `mock` dataset, you simply need to provide `MockDataset`
class extending `Dataset` under `deel.datasets.mock`.
Here is possible implementation of a `MockDataset` that consists of a single `.csv`
file loaded in a `pandas.DataFrame`:

```python
# Content of deel/datasets/mock/__init__.py

# -*- encoding: utf-8 -*-

import pathlib
import typing

from ..dataset import Dataset
from ..settings import Settings


# The name of the class is important, it should be XDataset where X
# is the capitalize version of the dataset name (`mock` -> `Mock`):
class MockDataset(Dataset):

    # Default mode for the dataset (basic):
    _default_mode = "basic"

    # Dataset consists of a single .csv file:
    _single_file = True

    def __init__(
        self, version: str = "latest", settings: typing.Optional[Settings] = None
    ):
        """
        Args:
            version: Version of the dataset.
            settings: The settings to use for this dataset, or `None` to use the
            default settings.
        """
        super().__init__("mock", version, settings)

    # The name of the method matters! It should be load_MODE, where MODE
    # is one of the available modes. Here we choose to provide a single
    # "basic" mode.
    def load_basic(self, path: pathlib.Path):
        # You should only import pandas when required to avoid
        # adding extra dependencies to the package:
        import pandas as pd

        return pd.read_csv(path)
```

### Environment

In order to locally run the test suite, you need a proper `tox` installation:

```bash
# You should install tox globally on your system, not on a dedicated
# environment:
pip install tox
```

You can install the development dependencies by running the following
command within the repository:

```bash
# You should do this in a dedicated virtual environment:
pip install -e .[dev]
```

This will install the required linters (`black`, `flake8`, `mypy`) and the
unit test library `pytest`.

Once you are done, you can run `tox` to check that your code is correct:

```
tox
```
