# -*- coding: utf-8 -*-
# Copyright IRT Antoine de Saint Exupéry et Université Paul Sabatier Toulouse III - All
# rights reserved. DEEL is a research program operated by IVADO, IRT Saint Exupéry,
# CRIAQ and ANITI - https://www.deel.ai/
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import pathlib
from typing import Callable, List, Optional, Sequence, Tuple

import torch
import torchvision.transforms.functional as F
from PIL import Image
from torch.utils.data import Dataset


class ImageDataset(Dataset):
    def __init__(
        self,
        files: List[pathlib.Path],
        labels: Optional[List[int]] = None,
        transform: Optional[Callable[[Image.Image], Image.Image]] = None,
    ):
        self.files = files
        self.labels = labels
        self.transform = transform

    def loader(self, path) -> Image.Image:
        with open(path, "rb") as fp:
            return Image.open(fp).convert("RGB")

    def __len__(self) -> int:
        return len(self.files)

    # Copy from: torchvision.datasets.DatasetFolder
    def __getitem__(self, index):
        """
        Args:
            index (int): Index

        Returns:
            tuple: (sample, target) where target is class_index of the target class.
        """
        path = self.files[index]
        sample = self.loader(path)

        if self.transform is not None:
            sample = self.transform(sample)

        if not self.labels:
            return sample

        return sample, self.labels[index]


class OptionalToTensor:

    """
    Optional call to ToTensor() if the object is not already a tensor.
    """

    def __call__(self, pic) -> torch.Tensor:
        if isinstance(pic, torch.Tensor):
            return pic
        return F.to_tensor(pic)  # type: ignore

    def __repr__(self):
        return self.__class__.__name__ + "()"


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
    import numpy as np
    from torch.utils.data import Subset

    if not isinstance(dataset, Subset):
        raise ValueError("Invalid dataset type")

    tmpset: Dataset = dataset
    while not hasattr(tmpset, "labels") and hasattr(tmpset, "dataset"):
        tmpset = tmpset.dataset  # type: ignore
    try:
        labels = tmpset.labels  # type: ignore
    except AttributeError:
        raise ValueError("Cannot split torch dataset without explicit labels.")

    train_labels = [labels[index] for index in dataset.indices]
    mask = np.isin(train_labels, labels_in)

    return (Subset(dataset, np.where(mask)[0]), Subset(dataset, np.where(~mask)[0]))
