# -*- encoding: utf-8 -*-

from typing import List, Tuple
from . import InvalidDatasetModeError


def numpy_split_on_label(datasets: Tuple, labels_in: List[int]):
    """
    Allows to split datasets in in-dataset and out-dataset according to labels_in
    :param datasets: a tuple of train and test numpy datasets
    :param labels_in: array of 'normal' labels
    :return: 2 tuple of splited train and test datasets (train_in, train_out),
     (test_in, test_out)
    """
    import numpy as np

    if (
        isinstance(datasets[0][0], np.ndarray)
        and isinstance(datasets[0][1], np.ndarray)
        and isinstance(datasets[1][0], np.ndarray)
        and isinstance(datasets[1][1], np.ndarray)
    ):

        train_set = datasets[0]
        test_set = datasets[1]
        train_in_images = []
        train_out_images = []
        train_in_labels = []
        train_out_labels = []
        test_in_labels = []
        test_out_labels = []
        test_in_images = []
        test_out_images = []

        for i in range(len(train_set[0])):
            if train_set[1][i] in labels_in:
                train_in_images.append(train_set[0][i])
                train_in_labels.append(train_set[1][i])
            else:
                train_out_images.append(train_set[0][i])
                train_out_labels.append(train_set[1][i])

        for i in range(len(test_set[0])):
            if test_set[1][i] in labels_in:
                test_in_images.append(test_set[0][i])
                test_in_labels.append(test_set[1][i])
            else:
                test_out_images.append(test_set[0][i])
                test_out_labels.append(test_set[1][i])

        return (
            (
                (np.array(train_in_images), np.array(train_in_labels)),
                (np.array(train_out_images), np.array(train_out_labels)),
            ),
            (
                (np.array(test_in_images), np.array(test_in_labels)),
                (np.array(test_out_images), np.array(test_out_labels)),
            ),
        )
    else:
        raise InvalidDatasetModeError
