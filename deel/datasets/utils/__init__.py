# -*- encoding: utf-8 -*-

import pathlib
import random
import logging

from typing import List, Tuple, Optional, Union, Dict, Callable

from PIL import Image

log = logging.getLogger("deel.dataset.manager")


def load_python_image_dataset(
    folder: pathlib.Path,
    shuffle: Union[bool, int] = True,
    aggregate_fn: Callable[[str], Optional[str]] = lambda x: x,
    filter_fn: Callable[[str, pathlib.Path], bool] = lambda *args: True,
) -> Tuple[List[pathlib.Path], List[int], Dict[int, str]]:
    """ Load a python "dataset" from the given folder. This methods
    returns a list of paths, labels, and class names from the given folder.

    Args:
        folder: The folder containing the dataset. The folder should contain,
        for each class, a subfolder with only images inside.
        shuffle: If True, shuffle images with the default seed. If an int is given,
        use it as the seed for shufling. If False, do not shuffle. Shuffle is done
        using the standard `random.shuffle` module
        False otherwize.
        aggregate_fn: Callable to aggregate classes. The function should take
        the name of an original class (subfolder) and returns the name of the
        "parent" class. If the call returns `None`, the class is discarded.
        filter_fn: A function to filter out images. This function should take
        a string (name of the file) and a path to the file and returns True
        if the image should be included, False if it should be excluded.

    Returns: A 3-tuple `(paths, labels, classes)` where `paths` is a list of
    paths, `labels` is a list of labels (integers) and classes is a dictionary
    from labels to names.
    """
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

    # Class names (sorted):
    class_names = sorted(class_files.keys())

    filenames: List[pathlib.Path] = []
    labels: List[int] = []
    for i, k in enumerate(class_names):
        filenames.extend(class_files[k])
        labels.extend([i] * len(class_files[k]))

    # Shuffle if needed:
    idxs: List[int] = list(range(len(filenames)))
    if shuffle is True:
        random.shuffle(idxs)
    elif isinstance(shuffle, int):
        random.Random(shuffle).shuffle(idxs)

    return (
        [filenames[i] for i in idxs],
        [labels[i] for i in idxs],
        dict(enumerate(class_names)),
    )


def load_numpy_image_dataset(
    folder: pathlib.Path,
    image_size: Optional[Tuple[int, int]] = None,
    train_split: Union[float, Tuple[float, float]] = 0.8,
    shuffle: Union[bool, int] = True,
    aggregate_fn: Callable[[str], Optional[str]] = lambda x: x,
    filter_fn: Callable[[str, pathlib.Path], bool] = lambda *args: True,
):
    """ Creates a numpy image dataset from the given folder and
    parameters.

    The image dataset are 4-dimensional (N, H, W, C) numpy array where (H, W)
    is the image size, C the number of channels. The arrays contain `np.uint8`
    values between 0 and 255.

    Args:
        folder: The folder containing the dataset. The folder should contain,
        for each classes, a subfolder with only images inside.
        image_size: The size of the image, or None to not resize images. `None`
        is only supported if all the images already have the same size.
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

    Returns:
        A two-tuple whose first element is another tuple containing two or three
        2-tuple of numpy arrays corresponding to training, validation and testing
        dataset, and the second element is mapping from class labels to class names.
        Each dataset is a 2-tuple (x, y) where `x` is a 4-dimensional numpy array
        containing images and `y` a one-dimensional numpy array containing classes.
    """

    import numpy as np

    # Retrieve files:
    files, plabels, idx_to_class = load_python_image_dataset(
        folder, shuffle, aggregate_fn, filter_fn
    )

    # Load the images:
    def load_image(x: pathlib.Path):
        im: Image.Image = Image.open(str(x))
        if image_size is not None:
            im = im.resize(image_size)
        return np.array(im)

    images = np.array([load_image(p) for p in files])
    labels = np.array(plabels)

    # Add a channel dimension if missing:
    if len(images.shape) == 3:
        images = images[..., np.newaxis]

    # Convert files to filenames (str):
    n_images = len(files)

    # Split the arrays:
    if isinstance(train_split, float):
        train_n = int(n_images * train_split)
        return (
            (
                (images[:train_n], labels[:train_n]),
                (images[train_n:], labels[train_n:]),
            ),
            idx_to_class,
        )
    else:
        train_n = int(n_images * train_split[0])
        val_n = train_n + int(n_images * train_split[1])
        return (
            (
                (images[:train_n], labels[:train_n]),
                (images[train_n:val_n], labels[train_n:val_n]),
                (images[val_n:], labels[val_n:]),
            ),
            idx_to_class,
        )


def load_pytorch_image_dataset(
    folder: pathlib.Path,
    image_size: Optional[Tuple[int, int]] = None,
    train_split: Union[float, Tuple[float, float]] = 0.8,
    shuffle: Union[bool, int] = True,
    aggregate_fn: Callable[[str], Optional[str]] = lambda x: x,
    filter_fn: Callable[[str, pathlib.Path], bool] = lambda *args: True,
    transform: Optional[Callable[[Image.Image], Image.Image]] = None,
):
    """ Creates a pytorch image dataset from the given folder and
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
        transform: Transformation to apply to the image before the conversion
        to a torch tensor via `ToTensor()`. If `image_size` is not None, the
        resize transform will be applied before these, if you want to do the
        opposite, simply pass `None` as `image_size` and add the resize
        transformation manually.


    Returns:
        A two-tuple whose first element is another tuple containing two or three
        datasets corresponding to training, validation and testing dataset, and the
        second element is mapping from class labels to class names.
    """

    from torch.utils.data import Subset
    import torchvision.transforms

    from .torch_utils import ImageDataset

    # Retrieve files:
    files, labels, idx_to_class = load_python_image_dataset(
        folder, shuffle, aggregate_fn, filter_fn
    )

    # Create the transform:
    transforms: List[Callable[[Image.Image], Image.Image]] = []
    if image_size is not None:
        transforms.append(torchvision.transforms.Resize(image_size))
    if transform is not None:
        transforms.append(transform)
    transforms.append(torchvision.transforms.ToTensor())

    transform = torchvision.transforms.Compose(transforms)

    # Create the dataset:
    dataset = ImageDataset(files, labels, transform)

    # Split dataset:
    if isinstance(train_split, float):
        i1 = int(train_split * len(dataset))
        return (
            (Subset(dataset, range(i1)), Subset(dataset, range(i1, len(dataset))),),
            idx_to_class,
        )
    else:
        i1 = int(train_split[0] * len(dataset))
        i2 = i1 + int(train_split[1] * len(dataset))
        return (
            (
                Subset(dataset, range(i1)),
                Subset(dataset, range(i1, i2)),
                Subset(dataset, range(i2, len(dataset))),
            ),
            idx_to_class,
        )


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

    Returns:
        A two-tuple whose first element is another tuple containing two or three
        datasets corresponding to training, validation and testing dataset, and the
        second element is mapping from class labels to class names.
    """

    # We only import tensorflow here to avoid breaking utils import when
    # tensorflow is not available.
    import tensorflow as tf

    # Retrieve files:
    files, labels, idx_to_class = load_python_image_dataset(
        folder, shuffle, aggregate_fn, filter_fn
    )

    # Convert files to filenames (str):
    filenames = [str(f) for f in files]
    n_images = len(files)

    # Create the tensorflow dataset:
    dataset = tf.data.Dataset.from_tensor_slices(
        (filenames, tf.keras.utils.to_categorical(labels))
    )

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
            (
                dataset.map(preprocess).take(int(train_split * n_images)),
                dataset.map(preprocess).skip(int(train_split * n_images)),
            ),
            idx_to_class,
        )
    else:
        return (
            (
                dataset.map(preprocess).take(int(train_split[0] * n_images)),
                dataset.map(preprocess)
                .skip(int(train_split[0] * n_images))
                .take(int(train_split[1] * n_images)),
                dataset.map(preprocess)
                .skip(int(train_split[0] * n_images))
                .skip(int(train_split[1] * n_images)),
            ),
            idx_to_class,
        )
