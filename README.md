# DEEL dataset manager

This project aims to ease the installation and usage of the datasets for the DEEL
project.

## Installation

You can install the manager directly from pypi:
```bash
pip install deel-datasets
```

You can also install this package by using `pip`. If you have set-up SSH keys properly
for [https://forge.deel.ai](https://forge.deel.ai), you can use the SSH version:

```
pip install git+ssh://git@forge.deel.ai:22012/devops/deel_dataset_manager.git
```

Otherwize the HTTPS version should work but you will have to enter your credentials
manually:

```
pip install git+https://forge.deel.ai/devops/deel_dataset_manager.git
```

## Configuration

The configuration file specifies how the datasets should be downloaded, or
if the datasets do no have to be downloaded (e.g. on Google Cloud).

The configuration file should be at `$HOME/.deel/config.yml`:

- On Windows system it is `C:\Users\$USERNAME\.deel\config.yml` unless you
  have set the `HOME` environment variable.
- The `DEEL_CONFIGURATION_FILE` environment variable can be used to specify the
  location of the configuration file if you do not want to use the default one.

The configuration file is a **YAML** file.

The second version of the providers configuration file allows to define a list
of providers.

Two key words are mandatory to specify the use of this version:
- `version: 2` (indicates the version of the configuration file)
- `providers:` (value = list of providers)

`providers` is the root node of the provider configurations list.
Each child node of `providers` node define a provider configuration.
The name of child node is the name of the configuration.
It may be used in command line to specify the provider (e.g., option `-p` for `download`).

Currently available providers are `webdav`, `ftp`, `http`, `local` and `gcloud`.

- The `webdav` provider will fetch datasets from a WebDAV server and needs at least the `url`
configuration parameter.
The WebDAV provider supports basic authentication (see example below).
If the datasets are not at the root of the WebDAV server, the `folder` configuration can be used to
specify the remote path (see example below).

- The `ftp` provider is similar to the `webdav` provider except that it will fetch datasets
from a FTP server instead of a WebDAV one and needs at least the `url` configuration parameter.

- The `local` provider does not require any extra configuration and will simply
fetch data from the specified `path`.

When using remote providers such as `webdav`, `http` or `ftp` provider, the `path` parameter indicates
where the datasets should be stored locally.

- The `gcloud` provider is similar to the `local` provider, except that it will try to
locate the dataset storage location automatically based on a mounted drive.
The `disk` configuration parameter is mandatory and specify the name of the GCloud drive.

#### Configuration example

Below is an example of a configuration for the DEEL dataset manager:

```yaml
# Version of the configuration (currently 2):
version: 2

# Provider for the datasets - The names of the providers do not have to match
# their types:
providers:

  # A GCloud provider with a shared GCloud drive named "my-disk-name".
  gcloud:
    type: gcloud
    disk: my-disk-name

  # A local storage at "/data/dataset".
  local:
    type: local
    source: /data/dataset/

  # An FTP provider.
  ftp:
    type: ftp

    # The "url" parameter contains the full path (server + folder):
    url: ftp://ftp.softronics.ch/mvtec_anomaly_detection

    # The "auth" is optional if the FTP server is public:
    auth:
      method: "simple"
      username: "${username}"
      password: "${password}"

  # A public WebDAV server.
  webdav_public:
    type: webdav
    url: https://my-public-webdav.com

  # A private WebDAV server where the datasets are not at the root.
  # Note: This example can be used with Cloud storage such as Nextcloud with
  # a shared "datasets" drive.
  webdav_private:
    type: webdav
    url: https://my-cloud-provider.com/remote.php/webdav
    folder: datasets
    auth:
        method: "simple"
        username: "${username}"
        password: "${password}"

# The local path where datasets are stored when they are from a remote provider:
path: /home/${username}/.deel/datasets
```

You can name a provider `default` to use it by-default.
When looking for a dataset, the dataset is first looked-up in the `default` provider,
then in other providers.
The manager tries providers one-by-one in the order they are declared until it finds
one providing the dataset.

## Uninstalling

To uninstall the deel dataset manager package , simply run `pip uninstall`:

```
pip uninstall deel-datasets
```

## DEEL dataset plugin

Without plugins, the manager is only able to download a dataset and returns the path to
the local folder containing it (after download).
By installing plugins, you gain access to automatic way of loading datasets or pre-processing
data.

### Plugins installation

Plugins can be installed using `pip`.

Some plugins are available on *forge.deel.ai* project and can be installed.
You can browse https://forge.deel.ai/DevOps/datasets for the list of available datasets.

    # SSH version (with proper SSH key setup):
    pip install git+ssh://forge.deel.ai:22012/devops/datasets/${name}_dataset.git

    # HTTPS version:
    pip install git+https://forge.deel.ai/devops/datasets/${name}_dataset.git

## Examples of usage

### Basic usage

To load a dataset, you can simply do:

```python
import deel.datasets

# Load the default mode of dataset-a dataset:
landcover = deel.datasets.load("dataset-a")

# Load the tensorflow version of the dataset-b dataset (default mode for dataset-b):
blink = deel.datasets.load("dataset-b")

# Load the pytorch version of the dataset-b dataset:
blink = deel.datasets.load("dataset-b", mode="pytorch")
```

The `deel.datasets.load` function is the basic entry to access the datasets.
By passing `with_info=True`, extra information can be retrieved as a python
dictionary. Information are not standardized, so each dataset may provide
different ones:
The `mode` argument can be used to load different "version" of the dataset. By default,
only the `path` mode is available and will return the path to the local folder
containing the dataset.
By installing plugins, new modes can be made available for each datasets (see plugin
implementation below).

```python
import deel.datasets

# Load the tensorflow version of the dataset-b dataset:
blink, info = deel.datasets.load("dataset-b", mode="tensorflow", with_info=True)

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
  dataset-a: 3.0.1 [latest], 3.0.0
  dataset-b: 1.0 [latest]
  dataset-c: 1.0 [latest]
$ python -m deel.datasets list --local
Listing datasets at /opt/datasets:
  dataset-a: 3.0.1 [latest], 3.0.0
  dataset-c: 1.0 [latest]
```

- `download NAME[:VERSION]` &mdash; Download the specified dataset. If the configuration
  does not specify a remote provider, this does nothing except outputing some information.
  The `:VERSION` can be omitted, in which case `:latest` is implied. To force the re-download
  of a dataset, the `--force` option can be used.

```bash
$ python -m deel.datasets download dataset-a:3.0.0
Fetching dataset-a:3.0.0...
dataset-a-3.0.0-20191004.zip: 100%|█████████████████████████████████████████| 122M/122M [00:03<00:00, 39.3Mbytes/s]
Dataset dataset-a:3.0.0 stored at '/opt/datasets/dataset-a/3.0.0'.
```

- `remove NAME[:VERSION]` &mdash; Remove the specified dataset from the local storage (if
  possible). If `:VERSION` is omitted, the whole dataset corresponding to `NAME` is
  deleted. If the `--all` option is used, all datasets are removed from the local storage.

## Contributing

The first step for contributing is to open
[a new issue](https://forge.deel.ai/DevOps/deel_dataset_manager/issues/new).

You then need to fork this repository, or create a dedicated branch if you have
sufficient privileges.
Once you are done, you can open a merge request for your changes to be integrated
in this repository.

### Adding a new dataset

## Dell dataset plugin implementation

A deel dataset plugin is an extension of the `Dataset` class defined in the DEEL dataset manager project.
It allows to access to specific datasets files using the load method of defined modes.

### The dataset class

Below is an example implementation of a dataset class `ExampleDataset`.
The `load_XXX` methods defines the various mode, e.g. `load_pytorch` adds
a `pytorch` mode to the dataset.
The default mode used (when none is specified) can be set using the
`_default_mode` class attribute.

```python
import h5py
import pathlib
import typing

from deel.datasets.dataset import Dataset
from deel.datasets.settings import Settings


class ExampleDataset(Dataset):

    # Default mode:
    _default_mode: str = "numpy"

    def __init__(
        self, version: str = "latest", settings: typing.Optional[Settings] = None
    ):
        """
        Args:
            version: Version of the dataset.
            settings: The settings to use for this dataset, or `None` to use the
            default settings.
        """
        # `data_name` is the name of the folder containing the dataset on the
        # provider (remote or local).
        super().__init__("data_name", version, settings)

    def load_numpy(self, path: pathlib.Path):
        """
        Numpy mode for this dataset.
        """
        # Dataset-specific code:
        return data

    def load_csv(self, path: pathlib.Path):
        """
        CSV mode for this dataset.
        """

        import pandas as pd

        return pd.read_csv(path, sep=";", index_col=0)

    def load_pytorch(
        self,
        path: pathlib.Path,
        nstack: int = 4,
        transform: typing.Callable = None,
    ):
        """
        Pytorch mode for this dataset. With extra arguments that can
        be passed to the `deel.datasets.load` method using named parameters.
        """
        from .torch import SourceDataSet

        return SourceDataSet(self.load_path(path), nstack, transform)
```

By default, the `with_info` option will return a dictionary containing the name and
the version of the dataset.
If you want to provide extra information, you can return a dictionary from the `load_XXX` methods, e.g.:

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

### Packaging the dataset(s)

To be found by the dataset manager, the `ExampleDataset` class must be put in
a package with a specific `entrypoint` (defined in `setup.py`).

The entry point provides to the plugin to be discovered and used by DEEL dataset
manager project.
The name of the DEEL dataset manager entry point is unique:
`plugins.deel.dataset`.
It is possible to define many aliases for the same plugin by adding multiple
`alias = package:plugin class` entries in entry points list.

```python
# Assuming `ExampleDataset` is in `my_dataset/__init__.py`:
from setuptools import setup

setup(
    # Other `setup` arguments:
    ...

    # Entry points:
    entry_points={
        "plugins.deel.dataset": [
            "example = my_dataset:ExampleDataset",
            "my_dataset.example = my_dataset:ExampleDataset"
        ]
    }
)
```

A single plugin can expose multiple datasets through different entry points.

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
