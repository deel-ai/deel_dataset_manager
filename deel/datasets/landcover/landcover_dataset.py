# -*- encoding: utf-8 -*-

from deel.datasets.base.dataset import Dataset
import os

class LandCoverDataset(Dataset):
    def __init__(self):
        super()
        self.urls = [
            'https://datasets.deel.ai/landcover/latest/landcover-1.0-20191015.h5'
        ]
    
    def load(self, forceDownload=False):
        super().load('landcover', forceDownload)
