This project aims to ease the installation of DEEL's datasets.

# Installation

```
pip install git+ssh://git@forge.deel.ai:22012/devops/deel_dataset_manager.git
or
pip install git+https://forge.deel.ai/devops/deel_dataset_manager.git
```

**Important:** You need correctly setup SSH keys on
[https://forge.deel.ai](https://forge.deel.ai).


# Usage

## Exemple for the blink dataset using tensorflow

```
git clone https://forge.deel.ai/DevOps/deel_dataset_manager.git
or
ssh://git@forge.deel.ai:22012/DevOps/deel_dataset_manager.git
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
>NOTES :  
    - Tensorflow 2 required  
    - Number of epoch is set to 1 : do not expect a good prediction :)  
&nbsp;&nbsp;&rarr; epochs set to 30 starts to have :  
&nbsp;&nbsp;&nbsp;&nbsp;- 95% of accurracy on train dataset  
&nbsp;&nbsp;&nbsp;&nbsp;- 90% of accurracy on valid dataset
