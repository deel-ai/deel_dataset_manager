# DEEL dataset manager
[![PyPI](https://img.shields.io/pypi/v/deel-datasets.svg)](https://pypi.org/project/deel-datasets)
[![Python](https://img.shields.io/pypi/pyversions/deel-datasets.svg)](https://pypi.org/project/deel-datasets)
[![Documentation](https://img.shields.io/badge/doc-url-blue.svg)](https://deel-ai.github.io/deel-datasets)
[![Tests](https://github.com/deel-ai/deel-datasets/actions/workflows/python-tests.yml/badge.svg?branch=master)](https://github.com/deel-ai/deel_dataset_manager/actions/workflows/python-tests.yml)
[![Linters](https://github.com/deel-ai/deel-datasets/actions/workflows/python-lints.yml/badge.svg?branch=master)](https://github.com/deel-ai/deel_dataset_manager/actions/workflows/python-lints.yml)
[![License](https://img.shields.io/github/license/deel-ai/deel-datasets.svg)](https://github.com/deel-ai/deel_dataset_manager/blob/master/LICENSE)

[deel-datasets manager](https://deel-ai.github.io/deel-datasets) project aims to ease the installation and usage of self-hosted or public datasets. It is an open framework to manage any dataset through a plugin mechanism.

## Installation

The latest release can be installed from pypi. All needed python packages will also be installed as a dependency.

```bash
pip install deel-datasets
```

Otherwize the HTTPS version should work but you will have to enter your credentials manually:

```bash
pip install git+https://github.com/deel-ai/deel_dataset_manager.git
```

## Configuration

The configuration file specifies how the datasets should be downloaded, or
if the datasets do no have to be downloaded (e.g. on Google Cloud).

It allows to define a list of datasets providers.

The configuration file should be by default at `$HOME/.deel/config.yml`:

- On Windows system it is `C:\Users\$USERNAME\.deel\config.yml` unless you
  have set the `HOME` environment variable.
- The `DEEL_CONFIGURATION_FILE` environment variable can be used to specify the
  location of the configuration file if you do not want to use the default one.

The configuration file is a **YAML** file.

Two two root nodes are mandatory in configuration file:
- `providers:` (value = list of providers)
- `path`: local destination directory path (by default = ${HOME}/.deel/datasets)

      providers:
        |-provider1
        |-provider2
        .
        .
        |-providerN
      path: local destination path

`providers` is the root node of the provider configurations list.
Each child node of `providers` node define a provider configuration.
The name of child node is the name of the provider.
It may be used in command line to specify the provider (e.g., option `-p` for `download`).

Currently the following types of provider are implemented: `webdav`, `ftp`, `http`, `local` and `gcloud`.

- The `webdav` provider will fetch datasets from a WebDAV server and needs at least the `url`
configuration parameter.
The WebDAV provider supports basic authentication (see example below).
If the datasets are not at the root of the WebDAV server, the `folder` configuration can be used to
specify the remote path (see example below).

- The `ftp` provider is similar to the `webdav` provider except that it will fetch datasets
from a FTP server instead of a WebDAV one and needs at least the `url` configuration parameter.

- The `local` provider does not require any extra configuration and will simply
fetch data from the specified `path`. The `copy`configuation (true or false) allows to specify
if dataset must be copied from `path` to destination `path` or not. `copy`is false by default.

- The `gcloud` provider is similar to the `local` provider, except that it will try to
locate the dataset storage location automatically based on a mounted drive.
The `disk` configuration parameter is mandatory and specify the name of the GCloud drive.

`path` parameter indicates where the datasets should be stored locally when using remote providers such as `webdav`, `http` or `ftp` provider.

#### Configuration example

Below is an example of a configuration for the DEEL dataset manager:

```yaml
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
    path: /data/dataset/
    copy: true

  # An FTP provider.
  ftp:
    type: ftp
    # The "url" parameter contains the full path (server + folder):
    url: ftp://<server_name>/<dataset path on ftp server>
    # or folder to set the the path to dataset remote directory
    # folder: <dataset path on ftp server>
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
# by default ${HOME}/.deel/datasets
path: ${HOME}/.deel/datasets
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

Without plugins, DEEL datasets manager is only able to download a dataset and returns the path to
the local folder containing it (after download).
By installing plugins, you gain access to automatic way of loading datasets or pre-processing
data.

### Plugins installation

Plugins can be installed using `pip`.

Some plugins are available on [github.com/deel-ai](https://github.com/deel-ai) and can be installed.

For DEEL project members, private plugins for DEEL project datasets are available on
[here](https://forge.deel.ai/DevOps/datasets).

They can browse [here](https://forge.deel.ai/DevOps/datasets/all) for the list of available datasets.

    # SSH version (with proper SSH key setup):
    pip install git+ssh://git@forge.deel.ai:<port>/DevOps/datasets/all.git

    # HTTPS version:
    pip install git+https://forge.deel.ai/DevOps/datasets/all.git

## Examples of usage

### Basic usage

To load a dataset, you can simply do:

```python
import deel.datasets

# Load the default mode of dataset-a dataset:
dataset-a-lpath = deel.datasets.load("dataset-a")

# dataset-c plugin is installed with tensorflow mode implemented
# Load the tensorflow version of the dataset-b dataset (default mode for dataset-b):
dataset-b-tf = deel.datasets.load("dataset-b", mode="tensorflow")
#or tensorflow mode is default mode
dataset-b-pt = deel.datasets.load("dataset-b")

# If dataset-c plugin is installed with pytorch mode implemented,
# load the pytorch version of the dataset-b dataset:
dataset-c-pt = deel.datasets.load("dataset-c", mode="pytorch")
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
dataset-b-lpath, info = deel.datasets.load("dataset-b", mode="tensorflow", with_info=True)

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

- `list` &mdash; List the available datasets on all providers in configuration file.
If the `-p` option is used to specify a provider, this will list the datasets available on it.

To list the dataset already downloaded, you can use the `--local` option.

```bash
$ python -m deel.datasets list
Listing datasets at https://datasets.server1:
  dataset-a: 3.0.1 [latest], 3.0.0
  dataset-b: 1.0 [latest]
  dataset-c: 1.0 [latest]
$ python -m deel.datasets list --local
Listing datasets at ${HOME}/.deel/datasets:
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
Dataset dataset-a:3.0.0 stored at '${HOME}/.deel/datasets/dataset-a/3.0.0'.
```

- `remove NAME[:VERSION]` &mdash; Remove the specified dataset from the local storage (if
  possible). If `:VERSION` is omitted, the whole dataset corresponding to `NAME` is
  deleted. If the `--all` option is used, all datasets are removed from the local storage.

## Adding a new dataset

### Deel dataset plugin implementation

A deel dataset plugin is an extension of the `Dataset` class defined in the DEEL dataset manager project.
It allows to access to specific dataset files using the load method of defined modes.

#### The dataset class

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

    return dataset, {"classes": ["foo", "bar"]}
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

#### Packaging the dataset(s)

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

## License

Copyright IRT Antoine de Saint Exupéry et Université Paul Sabatier Toulouse III - All
rights reserved. DEEL is a research program operated by IVADO, IRT Saint Exupéry, CRIAQ
and ANITI - https://www.deel.ai/

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

## Acknowledgments

This project received funding from the French "Investing for the Future – PIA3" program
within the Artiﬁcial and Natural Intelligence Toulouse Institute (ANITI). The authors
gratefully acknowledge the support of the [DEEL project](https://www.deel.ai/).
