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

# Load the raw data from the landcover dataset:
landcover = deel.datasets.load("landcover")

# Load the tensorflow version of the blink dataset:
blink_tf = deel.datasets.load("blink", framework="tensorflow")

# Load the pytorch version of the blink dataset:
blink_torch = deel.datasets.load("blink", framework="pytorch")
```

The `deel.datasets.load` function is a simple first interface for the datasets. If you
want more control on the datasets, you can lookup the `load` methods of the various
sub-modules.

The following files contain examples for the `blink` and `landcover` dataset:

- [examples/landcover/tensorflow_example.py](examples/landcover/tensorflow_example.py)
- [examples/landcover/load_example.py](examples/landcover/load_example.py)

## Configuration:

While a configuration file is not strictly needed right now, it is recommended to create
one. The configuration file specifies where the datasets should be downloaded from, or
if the datasets do no have to be downloaded (e.g. for GCloud).

The configuration file should be a `$HOME/.deel/config.yml` (the `DEEL_CONFIGURATION_FILE`
can be used to specify the location of the configuration file).

The configuration file is a YAML file:

```yaml
# Version of the configuration (currently 1):
version: 1

# Provider for the datasets:
provider:
    type: "webdav"
    url: "https://datasets.deel.ai"
    auth:
        method: "simple"
        username: "deel-datasets"
        password: "e]{qE/Pc65z'Nt?zLe-cK!_y?6f6"

# Local storage for the datasets:
storage: /data/datasets
```

### Providers

Currently available providers are `webdav` and `local`. The `webdav` provider is the
default-one and will fetch datasets from a WebDAV server and needs at least the `url`
configuration parameter (`auth` is not mandatory but required for the `https://datasets.deel.ai`
server). The `local` provider does not require any extra configuration and will simply
fetch data from the specified `storage`.

When using the `webdav` provider, the `storage` parameter indicates where the datasets
should be stored locally.
