import torchvision
import os
from deel.datasets.blink.blink_dataset import DatasetBlink

def load(forceDownload=False):
    deelDataset = DatasetBlink()
    deelDataset.load(forceDownload)
    dataset = torchvision.datasets.ImageFolder(os.path.join(deelDataset.unzippedPaths[0], "final_db_anonymous"))
    return dataset
