# -*- encoding: utf-8 -*-

from typing import List

import tensorflow as tf


def tf_split_on_label(dataset, labels_in: List[int]):
    """
    Allows to split a tensoflow dataset in in-dataset and
    out-dataset according to labels_in
    Args:
        param dataset: a tensoflow dataset
        param labels_in: array of 'normal' labels
    return:
        a tuple of splited datasets (dataset_in, dataset_out),
    """

    if not isinstance(dataset, tf.data.Dataset):
        raise ValueError("Invalid dataset type")

    return (
        dataset.filter(
            lambda x, y: tf.reduce_max(tf.gather(y, tf.constant(labels_in))) == 1
        ),
        dataset.filter(
            lambda x, y: tf.reduce_max(tf.gather(y, tf.constant(labels_in))) == 0
        ),
    )
