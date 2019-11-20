from deel.datasets.base.dataset import Dataset
import os

class DatasetBlink(Dataset):
    def __init__(self):
        super()
        self.urls = [
            'https://datasets.deel.ai/blink/latest/blink-3.0.1-20191120.zip'
        ]
    
    def load(self, forceDownload=False):
        super().load("blink", forceDownload)