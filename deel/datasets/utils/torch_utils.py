# -*- encoding: utf-8 -*-

import pathlib
from typing import Callable, List, Optional, Sequence, Tuple

from PIL import Image
from torch.utils.data import Dataset


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


def torch_split_on_label(
    dataset: Dataset, labels_in: Sequence[int]
) -> Tuple[Dataset, Dataset]:
    """
    Allows to split a torch dataset in in-dataset and out-dataset according to labels_in
    Args:
        dataset: a torch dataset
        labels_in: array of 'normal' labels
    Returns:
        a tuple of split datasets (dataset_in, dataset_out),
    """
    from torch.utils.data import Subset
    import numpy as np

    if not isinstance(dataset, Subset):
        raise ValueError("Invalid dataset type")

    tmpset = dataset
    while not hasattr(tmpset, "labels") and hasattr(tmpset, "dataset"):
        tmpset = tmpset.dataset
    try:
        labels = tmpset.labels
    except AttributeError:
        raise ValueError("Cannot split torch dataset without explicit labels.")

    train_labels = [labels[index] for index in dataset.indices]
    mask = np.isin(train_labels, labels_in)

    return (Subset(dataset, np.where(mask)[0]), Subset(dataset, np.where(~mask)[0]))
