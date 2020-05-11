# DEEL dataset manager

This project aims to ease the installation and usage of the datasets for the DEEL
project.

## Installation

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

### Configuration

The configuration file specifies how the datasets should be downloaded, or
if the datasets do no have to be downloaded (e.g. on Google Cloud).

The configuration file should be at `$HOME/.deel/config.yml`:

- On Windows system it is `C:\Users\$USERNAME\.deel\config.yml` unless you
  have set the `HOME` environment variable.
- The `DEEL_CONFIGURATION_FILE` environment variable can be used to specify the
  location of the configuration file if you do not want to use the default one.

Below is a basic authentication for DEEL core team members (replace `${username}` by
your OS username (you can also store datasets somewhere else),
and `${deel-user}` and `${deel-password}` by your credentials for the DEEL tools):

```yaml
# Version of the configuration (currently 1):
version: 1

provider:
    type: webdav

    url: https://share.deel.ai/remote.php/webdav
    folder: Datasets

    auth:
        method: "simple"
        username: "${deel-user}"
        password: "${deel-password}"

path: /home/${username}/.deel/datasets
```

See below for other configuration options.

### Uninstalling

To uninstall the package, simply run `pip uninstall`:

```
pip uninstall deel-datasets
```


## Basic usage

To load a dataset, you can simply do:

```python
import deel.datasets

# Load the default mode of landcover dataset:
landcover = deel.datasets.load("landcover")

# Load the tensorflow version of the blink dataset (default mode for blink):
blink = deel.datasets.load("blink")

# Load the pytorch version of the blink dataset:
blink = deel.datasets.load("blink", mode="pytorch")
```

The `deel.datasets.load` function is the basic entry to access the datasets.
By passing `with_info=True`, extra information can be retrieved as a python
dictionary. Information are not standardized, so each dataset may provide
different ones:

```python
import deel.datasets

# Load the tensorflow version of the blink dataset:
blink, info = deel.datasets.load("blink", mode="tensorflow", with_info=True)

print(info["classes"])
```


The function can take extra parameters depending on the chosen dataset and mode,
for instance, you can specify the percentage of training data for the `blink`
dataset:

```python
import deel.datasets

# Load the tensorflow version of the blink dataset:
blink = deel.datasets.load("blink", mode="tensorflow", percent_train=60)
```

The following files contain examples for the `blink` and `landcover` dataset:

- [examples/landcover/tensorflow_example.py](examples/landcover/tensorflow_example.py)
- [examples/landcover/load_example.py](examples/landcover/load_example.py)

## Configuration:

### GCloud configuration

If you are using a Google Cloud virtual machine, you can avoid downloading the datasets
by mounting and using the `deel-datasets` gcloud drive (see below).
This can be done by using the following (very simple) configuration (still at
`$HOME/.deel/config.yml`):

```yaml
version: 1

provider: gcloud
```

#### Accessing the `deel-datasets` on a Google Cloud virtual machine

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

**Note:** You only need to do this manually the first time. The disk will be automatically
mounted on the next restarts of the virtual machine.

### Command line utilities

The `deel-datasets` package comes with some command line utilities that can be accessed using:

```
python -m deel.datasets ARGS...
```

The `--help` option can be used to view the full capabilities of the command line program.
By default, the program uses the configuration at `$HOME/.deel/config.yml`, but the `-c`
argument can be used to specified a custom configuration file.

The following commands are available (not exhaustive):

- `list` &mdash; List the available datasets. If the configuration specify a remote provider
  (e.g., WebDAV), this will list the datasets available remotely. To list the dataset already
  downloaded, you can use the `--local` option.

```bash
$ python -m deel.datasets list
Listing datasets at https://datasets.deel.ai:
  blink: 3.0.1 [latest], 3.0.0
  landcover: 1.0 [latest]
  landcover-resolution: 1.0 [latest]
$ python -m deel.datasets list --local
Listing datasets at /opt/datasets:
  blink: 3.0.1 [latest], 3.0.0
  landcover: 1.0 [latest]
  landcover-resolution: 1.0 [latest]
```

- `download NAME[:VERSION]` &mdash; Download the specified dataset. If the configuration
  does not specify a remote provider, this does nothing except outputing some information.
  The `:VERSION` can be omitted, in which case `:latest` is implied. To force the re-download
  of a dataset, the `--force` option can be used.

```bash
$ python -m deel.datasets download blink:3.0.0
Fetching blink:3.0.0...
blink-3.0.0-20191004.zip: 100%|█████████████████████████████████████████| 122M/122M [00:03<00:00, 39.3Mbytes/s]
Dataset blink:3.0.0 stored at '/opt/datasets/blink/3.0.0'.
```

- `remove NAME[:VERSION]` &mdash; Remove the specified dataset from the local storage (if
  possible). If `:VERSION` is omitted, the whole dataset corresponding to `NAME` is
  deleted. If the `--all` option is used, all datasets are removed from the local storage.

### Providers

Currently available providers are `webdav`, `ftp`, `local` and `gcloud`.
The `webdav` provider is the default-one and will fetch datasets from a WebDAV server
and needs at least the `url` configuration parameter (`auth` is not mandatory but required
for the `https://datasets.deel.ai` server).
The `ftp` provider is similar to the `webdav` provider except that it will fetch datasets
from a FTP server instead of a WebDAV one and needs at least the `url` configuration parameter.
The `local` provider does not require any extra configuration and will simply
fetch data from the specified `path`.

When using the `webdav` or `ftp` provider, the `path` parameter indicates where the datasets
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

The second step is to create the `python` interface for the dataset.
The `deel.datasets` package is written such that adding extra datasets should
be quite easy.
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

By default, the `with_info` option will return a dictionary containing the name and
the version of the dataset.
If you want to provide extra information, you can return a dictionary from the `load_XXX`
methods, e.g.:

```python
def load_pytorch(self, path: pathlib.Path):
    # Load a pytorch dataset:
    dataset = ...

    return dataset, {"classes": ["foo", "bar"}
```

The `deel.datasets.utils` package contains utility functions to load `numpy`, `pytorch`
and `tensorflow` image dataset in a consistent way, and the `Dataset` class contains some
utiity methods to generate the information dictionary from the return of these methods.
Here is a very simple example for loading a dataset:

```python
def load_pytorch(self, path: pathlib.Path, image_size: Tuple[int, int]):
    # Use relative import only if you are inside the deel package:
    from ..utils import load_pytorch_image_dataset

    # Load the dataset using the utility function:
    dataset, idx_to_class = load_pytorch_image_dataset(
        self.load_path(path),  # This is require only if `load_path` modifies the path.
        image_size=image_size,
        train_split=.7,
    )

    # The `_make_class_info` is provided by `Dataset`:
    return dataset, self._make_class_info(idx_to_class)
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
