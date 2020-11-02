# -*- encoding: utf-8 -*-

from typing import List, Tuple

from . import InvalidDatasetModeError


def tf_split_on_label(datasets: Tuple, labels_in: List[int]):
    """
    Allows to split datasets in in-dataset and out-dataset according to labels_in
    :param datasets: a tuple of train and test tensorflow datasets
    :param labels_in: array of 'normal' labels
    :return: 2 tuple of splited train and test datasets (train_in, train_out),
     (test_in, test_out)
    """
    import tensorflow as tf
    import numpy as np

    if isinstance(datasets[0], tf.data.Dataset) and isinstance(
        datasets[1], tf.data.Dataset
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
        for image, label in train_set:
            lab = np.argmax(label, axis=None, out=None)
            if lab in labels_in:
                train_in_images.append(image)
                train_in_labels.append(lab)
            else:
                train_out_images.append(image)
                train_out_labels.append(lab)

        for image, label in test_set:
            lab = np.argmax(label, axis=None, out=None)
            if lab in labels_in:
                test_in_images.append(image)
                test_in_labels.append(lab)
            else:
                test_out_images.append(image)
                test_out_labels.append(lab)

        train_in_images = tf.convert_to_tensor(train_in_images)
        train_in_labels = tf.convert_to_tensor(train_in_labels)
        train_out_images = tf.convert_to_tensor(train_out_images)
        train_out_labels = tf.convert_to_tensor(train_out_labels)
        test_in_images = tf.convert_to_tensor(test_in_images)
        test_in_labels = tf.convert_to_tensor(test_in_labels)
        test_out_images = tf.convert_to_tensor(test_out_images)
        test_out_labels = tf.convert_to_tensor(test_out_labels)

        train_in_ds = tf.data.Dataset.from_tensor_slices(
            (tf.constant(train_in_images), tf.constant(train_in_labels))
        )
        train_in_ds = train_in_ds.shuffle(len(train_in_images))

        train_out_ds = tf.data.Dataset.from_tensor_slices(
            (tf.constant(train_out_images), tf.constant(train_out_labels))
        )
        train_out_ds = train_out_ds.shuffle(len(train_out_images))

        test_in_ds = tf.data.Dataset.from_tensor_slices(
            (tf.constant(test_in_images), tf.constant(test_in_labels))
        )
        test_in_ds = test_in_ds.shuffle(len(test_in_images))

        test_out_ds = tf.data.Dataset.from_tensor_slices(
            (tf.constant(test_out_images), tf.constant(test_out_labels))
        )
        test_out_ds = test_out_ds.shuffle(len(test_out_images))

        return ((train_in_ds, train_out_ds), (test_in_ds, test_out_ds))
    else:
        raise InvalidDatasetModeError
