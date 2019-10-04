from deel.datasets.base import Dataset
from deel.datasets.blink import DatasetBlink

def load(name):
    aDataset = None
    if (name == "blink"):
        aDataset = DatasetBlink()
        aDataset.load()
        
    else:
        # In case of an unknown dataset, use the download feature.
        aDataset = Dataset()
        aDataset.load(name)

    return aDataset