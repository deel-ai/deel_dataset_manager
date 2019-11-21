# -*- encoding: utf-8 -*-

from deel.datasets.base.dataset import Dataset


class LandCoverDataset(Dataset):

    h5_keys = ('patches', 'labels')
    h5_file = 'landcover-1.0-20191015.h5'

    def __init__(self):
        super()
        self.urls = [
            'https://datasets.deel.ai/landcover/latest/' + self.h5_file
        ]

    def load(self, forceDownload=False):
        super().load('landcover', forceDownload)


class LandCoverResolutionDataset(Dataset):

    h5_keys = ('patches', 'labels', 'sensibilities')
    h5_file = 'landcover-resolution-1.0-20191121.h5'

    def __init__(self):
        super()
        self.urls = [
            'https://datasets.deel.ai/landcover-resolution/latest/' + self.h5_file
        ]

    def load(self, forceDownload=False):
        super().load('landcover-resolution', forceDownload)
