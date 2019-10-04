This project aims to ease the installation of DEEL's datasets.

# Installation

```
pip install git+ssh://git@forge.deel.ai:22012/bertrand.cayssiols/deel_dataset_manager.git
```

**Important:** You need correctly setup SSH keys on
[https://forge.deel.ai](https://forge.deel.ai).


# Usage

## Exemple for the blink dataset using pytorch

```
import deel.datasets.blink.pytorch as dataset

dataset = dataset.load()
```

## Exemple for generic dataset (download and decompress)

```
import deel.datasets.base as dataset

dataset = dataset.load('test')
```
