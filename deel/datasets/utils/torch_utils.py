# -*- encoding: utf-8 -*-

import pathlib
from typing import Callable, List, Optional, Tuple

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


def torch_split_on_label(datasets: Tuple, labels_in: List[int]):
    """
    Allows to split datasets in in-dataset and out-dataset according to labels_in
    :param datasets: a tuple of train and test pytoch datasets
    :param labels_in: array of 'normal' labels
    :return: 2 tuple of splited train and test datasets (train_in, train_out),
     (test_in, test_out)
    """
    from torch.utils.data import DataLoader, Subset

    from . import InvalidDatasetModeError

    class DatasetFromSubset(Dataset):
        _subset: Subset

        def __init__(self, subset: Subset):
            self._subset = subset

        def __getitem__(self, index):
            return self._subset[index]

        def __len__(self):
            return len(self._subset)

    def _get_in_label_index(labels_in: List[int], targets):
        """
        Get the indices of labels that are included in targets.
        :param labels_in: array of normal labels
        :param targets: list/tuple of dataset labels
        :return: list with indices of target labels
        """

        in_lab_dataset = list()
        out_lab_dataset = list()
        index = 0
        for i in targets:
            if i in labels_in:
                in_lab_dataset.append(index)
            else:
                out_lab_dataset.append(index)
            index += 1

        return (
            in_lab_dataset,
            out_lab_dataset,
        )

    if isinstance(datasets[0], Subset) and isinstance(datasets[1], Subset):
        train_labels = []
        test_labels = []

        train_loader = DataLoader(datasets[0])
        test_loader = DataLoader(datasets[1])

        for _, labels in train_loader:
            train_labels.append(labels[0].item())

        for _, labels in test_loader:
            test_labels.append(labels[0].item())

        train_in_labs_index, train_out_labels_index = _get_in_label_index(
            labels_in, train_labels
        )
        test_in_labs_index, test_out_labels_index = _get_in_label_index(
            labels_in, test_labels
        )

        return (
            (
                Subset(DatasetFromSubset(datasets[0]), train_in_labs_index),
                Subset(DatasetFromSubset(datasets[0]), train_out_labels_index),
            ),
            (
                Subset(DatasetFromSubset(datasets[1]), test_in_labs_index),
                Subset(DatasetFromSubset(datasets[1]), test_out_labels_index),
            ),
        )
    else:
        raise InvalidDatasetModeError
