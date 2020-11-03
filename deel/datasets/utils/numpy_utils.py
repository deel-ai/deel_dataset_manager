# -*- encoding: utf-8 -*-

from typing import List


def numpy_split_on_label(dataset, labels_in: List[int]):
    """
    Allows to split a numpy dataset in in-dataset and out-dataset according to labels_in
    Args:
        param dataset: a numpy dataset
        param labels_in: array of 'normal' labels
    return:
        a tuple of splited datasets (dataset_in, dataset_out),
    """
    import numpy as np

    if not isinstance(dataset, tuple):
        raise ValueError("Invalid dataset type")

    in_mask = np.isin(dataset[1], labels_in)

    train_in_labels = dataset[1][in_mask]
    train_in_images = dataset[0][in_mask]
    train_out_labels = dataset[1][~in_mask]
    train_out_images = dataset[0][~in_mask]

    return (
        (np.array(train_in_images), np.array(train_in_labels)),
        (np.array(train_out_images), np.array(train_out_labels)),
    )
