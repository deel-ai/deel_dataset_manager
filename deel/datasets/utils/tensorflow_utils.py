# -*- encoding: utf-8 -*-

from typing import Tuple, Sequence
import tensorflow as tf


def tf_split_on_label(
    dataset: tf.data.Dataset, labels_in: Sequence[int]
) -> Tuple[tf.data.Dataset, tf.data.Dataset]:
    """
    Allows to split a tensoflow dataset in in-dataset and
    out-dataset according to labels_in
    Args:
        dataset: a tensoflow dataset
        labels_in: array of 'normal' labels
    Returns:
        a tuple of split datasets (dataset_in, dataset_out),
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
