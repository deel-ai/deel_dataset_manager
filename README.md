This project aims to ease the installation of DEEL's datasets.

# Installation

```
pip install git+ssh://git@forge.deel.ai:22012/devops/deel_dataset_manager.git
```

**Important:** You need correctly setup SSH keys on
[https://forge.deel.ai](https://forge.deel.ai).


# Usage

## Exemple for the blink dataset using tensorflow

```
git clone https://forge.deel.ai/DevOps/deel_dataset_manager.git
cd deel_dataset_manager/examples/blink/tensorflow
python example.py
```
This example is running following steps :
- download dataset
- decompress dataset
- parse dataset 
- run a training
- save the builded model
- execute some predictions


## Exemple for generic dataset (download and decompress)

```
import deel.datasets.base as dataset

dataset = dataset.load('test')
```
