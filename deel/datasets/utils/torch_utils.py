# -*- encoding: utf-8 -*-

import pathlib

from typing import List, Optional, Callable

from torch.utils.data import Dataset
from PIL import Image


class ImageDataset(Dataset):
    def __init__(
        self,
        files: List[pathlib.Path],
        labels: List[int],
        transform: Optional[Callable[[Image.Image], Image.Image]] = None,
    ):
        self.files = files
        self.labels = labels
        self.transform = transform

    def loader(self, path):
        with open(path, "rb") as fp:
            return Image.open(fp).convert("RGB")

    def __len__(self):
        return len(self.files)

    # Copy from: torchvision.datasets.DatasetFolder
    def __getitem__(self, index):
        """
        Args:
            index (int): Index

        Returns:
            tuple: (sample, target) where target is class_index of the target class.
        """
        path, target = self.files[index], self.labels[index]
        sample = self.loader(path)

        if self.transform is not None:
            sample = self.transform(sample)

        return sample, target
