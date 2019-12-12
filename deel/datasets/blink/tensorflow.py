# -*- encoding: utf-8 -*-

import pathlib
import random
import tensorflow as tf
import typing

from . import BlinkDataset


class TensorflowData:

    # Root folder of the dataset:
    _path: pathlib.Path

    # Random object:
    _random: random.Random

    def __init__(self, path: pathlib.Path, random_seed: int):
        """
    Args:
        path: Root folder of the dataset.
    """
        self._path = path
        self._classes = [
            c.name
            for c in self._path.iterdir()
            if c.suffix != ".csv" and c.name != "warnings"
        ]
        self._classes.sort()

        self._random = random.Random(random_seed)

    def prepare(
        self,
        percent_train: int,
        percent_val: int,
        image_shape: typing.Tuple[int, int, int],
    ) -> typing.Tuple[
        tf.data.Dataset,
        tf.data.Dataset,
        typing.List[pathlib.Path],
        typing.List[int],
        typing.List[str],
    ]:
        train, validation, test = self._split_files(percent_train, percent_val)

        train_set = self._tfdata_generator(
            train[0], train[1], image_shape, is_training=True
        )
        valid_set = self._tfdata_generator(
            validation[0], validation[1], image_shape, is_training=False
        )

        return train_set, valid_set, test[0], test[1], self._classes

    def _split_files(
        self, percent_train: int, percent_val: int
    ) -> typing.Tuple[
        typing.Tuple[typing.List[pathlib.Path], typing.List[int]],
        typing.Tuple[typing.List[pathlib.Path], typing.List[int]],
        typing.Tuple[typing.List[pathlib.Path], typing.List[int]],
    ]:

        """ Split the files in the folder.

        Args:
            percent_train: Percentage ([0, 100]) of files in the training set.
            percent_val: Percentage ([0, 100]) of files in the validation set.

        Returns:
            A 3-tuple containing, for each set (training, validation, test),
            a 2-tuple (files, labels).
        """

        files: typing.Dict[
            str, typing.Tuple[typing.List[pathlib.Path], typing.List[int]]
        ] = {"train": ([], []), "validation": ([], []), "test": ([], [])}

        for iclass, classname in enumerate(self._classes):

            # List of files for the current class:
            class_files = list(self._path.joinpath(classname).glob("*.bmp"))

            # Shuffle the list:
            self._random.shuffle(class_files)

            # Train / Validation / Test indexes:
            nfiles = len(class_files)
            idx = {}
            idx["train"] = [0, int(nfiles * percent_train / 100)]
            idx["validation"] = [
                idx["train"][1],
                idx["train"][1] + int(nfiles * percent_val / 100),
            ]
            idx["test"] = [idx["validation"][1], nfiles]

            for t in ("train", "validation", "test"):
                tfiles = class_files[idx[t][0] : idx[t][1]]
                files[t][0].extend(tfiles)
                files[t][1].extend([iclass] * len(tfiles))

        return (files["train"], files["validation"], files["test"])

    def _tfdata_generator(
        self,
        images: typing.List[pathlib.Path],
        labels: typing.List[int],
        image_shape: typing.Tuple[int, int, int],
        is_training: bool,
    ) -> tf.data.Dataset:
        """
        Args:
            images: List of images to use.
            labels: List of labels for the image.
            image_shape: Shape of the image to use.
            is_training: Indicates if a training dataset should be returned.

        Returns: A tensorflow Dataset corresponding to the given images and labels.
        """

        # Create a dataset of strings:
        dataset = tf.data.Dataset.from_tensor_slices(([str(p) for p in images], labels))

        # Shuffle if training:
        if is_training:
            dataset = dataset.shuffle(5000)  # depends on sample size

        # Load / resize images:
        def preprocess_fn(image, label):
            x = self._resize_image(image, image_shape)
            y = tf.one_hot(tf.cast(label, tf.uint8), len(self._classes))
            return x, y

        return dataset.map(preprocess_fn, 4)

    def _resize_image(
        self, image_path: str, image_shape: typing.Tuple[int, int, int]
    ) -> tf.Tensor:
        """ Read the given image from the given file, resize it and returns a corresponding
      tensor.

      Args:
          image_path: Path to the image to read.
          image_shape: Shape of the final image.

      Returns:
          A Tensor of type float ([0, 1]) corresponding to the resized image.
      """
        x = tf.io.read_file(image_path)
        x = tf.image.decode_bmp(x, channels=image_shape[2])
        x = tf.image.resize(x, [image_shape[0], image_shape[1]])
        x = x / 255.0
        return x


def load(version: str = "latest", force_update: bool = False, **kargs):
    return BlinkDataset(version).load("tensorflow", force_update=force_update, **kargs)
