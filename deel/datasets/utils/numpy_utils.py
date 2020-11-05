# -*- encoding: utf-8 -*-

from typing import Sequence, Tuple
import numpy as np


def numpy_split_on_label(
    dataset: Tuple[np.ndarray, np.ndarray], labels_in: Sequence[int]
) -> Tuple[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]]:
    """
    Allows to split a numpy dataset in in-dataset and out-dataset according to labels_in
    Args:
        dataset: a numpy dataset
        labels_in: array of 'normal' labels
    Returns:
        a tuple of split datasets (dataset_in, dataset_out),
    """

    if not isinstance(dataset, tuple):
        raise ValueError("Invalid dataset type")

    in_mask = np.isin(dataset[1], labels_in)

    train_in_labels = dataset[1][in_mask]
    train_in_images = dataset[0][in_mask]
    train_out_labels = dataset[1][~in_mask]
    train_out_images = dataset[0][~in_mask]

    return (
        (train_in_images, train_in_labels),
        (train_out_images, train_out_labels),
    )
