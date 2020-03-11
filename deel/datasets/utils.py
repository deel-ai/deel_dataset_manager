# -*- encoding: utf-8 -*-

import pathlib

from typing import List, Tuple, Optional, Union, Dict, Callable


def load_tensorflow_image_dataset(
    folder: pathlib.Path,
    image_size: Optional[Tuple[int, int]] = None,
    train_split: Union[float, Tuple[float, float]] = 0.8,
    shuffle: Union[bool, int] = True,
    aggregate_fn: Callable[[str], Optional[str]] = lambda x: x,
    filter_fn: Callable[[str, pathlib.Path], bool] = lambda *args: True,
):
    """ Creates a tensorflow image dataset from the given folder and
    parameters.

    Args:
        folder: The folder containing the dataset. The folder should contain,
        for each classes, a subfolder with only images inside.
        image_size: The size of the image, or None to not resize images.
        train_split: One or two float values. If a single value is specified,
        two datasets will be returned, one for training (using a percentage
        `train_split` of data) and one for testing. If two values are specified,
        three datasets will be returned: a training dataset, a validation
        dataset and a testing dataset.
        shuffle: If True, shuffle images before spliting with the default seed.
        If an int is given, use it as the seed for shufling. If False, do not
        shuffle.
        False otherwize.
        aggregate_fn: Callable to aggregate classes. The function should take
        the name of an original class (subfolder) and returns the name of the
        "parent" class. If the call returns `None`, the class is discarded.
        filter_fn: A function to filter out images. This function should take
        a string (name of the file) and a path to the file and returns True
        if the image should be included, False if it should be excluded.

    Returns: Two or three datasets corresponding to training, validation and
    testing dataset.
    """

    # We only import tensorflow here to avoid breaking utils import when
    # tensorflow is not available.
    import tensorflow as tf

    # Mapping between class names and list of files:
    class_files: Dict[str, List[pathlib.Path]] = {}

    for sd in filter(pathlib.Path.is_dir, folder.iterdir()):

        # Aggregate:
        cname = aggregate_fn(sd.name)

        if cname is None:
            continue

        # Create list if it does not exists:
        if cname not in class_files:
            class_files[cname] = []

        # Append files to the list:
        class_files[cname].extend(filter(lambda p: filter_fn(p.name, p), sd.iterdir()))

    filenames: List[str] = []
    labels: List[int] = []
    for i, k in enumerate(sorted(class_files.keys())):
        filenames.extend(map(str, class_files[k]))
        labels.extend([i] * len(class_files[k]))

    n_images = len(filenames)  # The amount of images in the dataset
    dataset = tf.data.Dataset.from_tensor_slices(
        (filenames, tf.keras.utils.to_categorical(labels))
    )

    # Shuffle if needed:
    if shuffle is True:
        dataset = dataset.shuffle(n_images)
    elif isinstance(shuffle, int):
        dataset = dataset.shuffle(n_images, seed=shuffle)

    # Preprocess function to load, resize and scale the image to [0, 1].
    def preprocess(filename, label):
        x = tf.io.read_file(filename)
        x = tf.image.decode_image(x, channels=3, expand_animations=False)
        x = tf.image.convert_image_dtype(x, tf.float32)
        if image_size is not None:
            x = tf.image.resize(x, image_size)
        return x, label

    # Split dataset:
    if isinstance(train_split, float):
        return (
            dataset.map(preprocess).take(int(train_split * n_images)),
            dataset.map(preprocess).skip(int(train_split * n_images)),
        )
    else:
        return (
            dataset.map(preprocess).take(int(train_split[0] * n_images)),
            dataset.map(preprocess)
            .skip(int(train_split[0] * n_images))
            .take(int(train_split[1] * n_images)),
            dataset.map(preprocess)
            .skip(int(train_split[0] * n_images))
            .skip(int(train_split[1] * n_images)),
        )
