This project aims to ease the installation of DEEL's datasets.

# Install
NOTE : You need to have ssh key correctly setuped with forge.deel.ai

>  pip install git+ssh://git@forge.deel.ai:22012/bertrand.cayssiols/deel_dataset_manager.git

# How To Use:

## Exemple for blink dataset in pytorch

>  import deel.datasets.blink.pytorch as dataset
>  
>  myDataset = dataset.load()

## Exemple for generic dataset, just download and decompress

>  import deel.datasets.base as dataset
>  
>  myDataset = dataset.load("test")