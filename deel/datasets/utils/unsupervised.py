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
import logging
import pathlib
import random
from collections import defaultdict
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Tuple, TypeVar, Union

from PIL import Image

log = logging.getLogger("deel.dataset.manager")


if TYPE_CHECKING:
    import numpy as np
    import tensorflow as tf
    import torch

    DatasetType = TypeVar(
        "DatasetType",
        Tuple[np.ndarray, np.ndarray],
        tf.data.Dataset,
        torch.utils.data.Dataset,
    )


def load_hierarchical_python_image_dataset(
    folder: pathlib.Path,
    dispatch_fn: Callable[[pathlib.Path], Optional[List[str]]],
):
    """
    Walk the given folder applying the given function to
    find to which dataset and class each file should be associated
    to.

    The function should returns a list of parts. The number of
    parts can be different for each file.

    Args:
        folder: The folder to look for files.
        dispatch_fn: A function that should return a list of str
            representing the dataset (e.g, `["train", "a"]`) to represent
            the dataset `train/a`.

    Returns:
        A dictionary mapping dataset hierarchy to list of paths (a dictionary
        of dictionary, indexed by string, whose leaves are list of paths).
    """

    classes: Dict[Tuple[str, ...], List[pathlib.Path]] = defaultdict(list)
    for path in filter(pathlib.Path.is_file, folder.glob("*/**/*")):

        # The "class" path:
        if path.name.endswith(".txt"):
            continue

        cpath = dispatch_fn(path.parent.relative_to(folder))

        if cpath is not None:
            classes[tuple(cpath)].append(path)

    # Create the datasets:
    datasets: Dict = {}
    for pathlist, data in classes.items():
        dt = datasets
        for t in pathlist[:-1]:
            if t not in dt:
                dt[t] = {}
        dt[pathlist[-1]] = data

    return datasets


def load_python_image_dataset(
    folder: pathlib.Path,
    shuffle: Union[bool, int] = True,
    filter_fn: Callable[[str, pathlib.Path], bool] = lambda *args: True,
) -> List[pathlib.Path]:
    """
    Load a python "dataset" from the given folder. This methods
    returns a list of paths from the given folder.

    Args:
        folder: The folder containing the dataset. The folder should contain,
            for each class, a subfolder with only images inside.
        shuffle: If True, shuffle images with the default seed. If an int is given,
            use it as the seed for shuffling. If False, do not shuffle. Shuffle is done
            using the standard `random.shuffle` module
            False otherwise.
        filter_fn: A function to filter out images. This function should take
            a string (name of the file) and a path to the file and returns True
            if the image should be included, False if it should be excluded.

    Returns: A 3-tuple `(paths, labels, classes)` where `paths` is a list of
    paths, `labels` is a list of labels (integers) and classes is a dictionary
    from labels to names.
    """
    # List of files
    files: List[pathlib.Path] = [
        filepath
        for filepath in folder.glob("**/*")
        if filter_fn(filepath.name, filepath)
    ]

    # Shuffle if needed:
    idxs: List[int] = list(range(len(files)))
    if shuffle is True:
        random.shuffle(idxs)
    elif isinstance(shuffle, int):
        random.Random(shuffle).shuffle(idxs)

    return [files[i] for i in idxs]


def load_numpy_image_dataset(
    folder: pathlib.Path,
    image_size: Optional[Tuple[int, int]] = None,
    train_split: Union[float, Tuple[float, float]] = 0.8,
    shuffle: Union[bool, int] = True,
    filter_fn: Callable[[str, pathlib.Path], bool] = lambda *args: True,
):
    """
    Creates a numpy image dataset from the given folder and
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
            If an int is given, use it as the seed for shuffling. If False, do not
            shuffle.
            False otherwise.
        filter_fn: A function to filter out images. This function should take
            a string (name of the file) and a path to the file and returns True
            if the image should be included, False if it should be excluded.

    Returns:
        A tuple containing two or three numpy arrays corresponding to training,
        validation and testing datasets.
    """

    import numpy as np

    # Retrieve files:
    files = load_python_image_dataset(folder, shuffle, filter_fn)

    # Load the images:
    def load_image(x: pathlib.Path):
        im: Image.Image = Image.open(str(x))
        if image_size is not None:
            im = im.resize(image_size)
        return np.array(im)

    images = np.array([load_image(p) for p in files])

    # Add a channel dimension if missing:
    if len(images.shape) == 3:
        images = images[..., np.newaxis]

    # Convert files to filenames (str):
    n_images = len(files)

    # Split the arrays:
    if isinstance(train_split, float):
        train_n = int(n_images * train_split)
        return (images[:train_n], images[train_n:])
    else:
        train_n = int(n_images * train_split[0])
        val_n = train_n + int(n_images * train_split[1])
        return (images[:train_n], images[train_n:val_n], images[val_n:])


def load_hierarchical_pytorch_image_dataset(
    folder: pathlib.Path,
    dispatch_fn: Callable[[pathlib.Path], Optional[List[str]]],
    image_size: Optional[Tuple[int, int]] = None,
    transform: Optional[Callable[[Image.Image], Image.Image]] = None,
):
    """
    Creates a pytorch image dataset from the given folder and
    parameters.

    Args:
        folder: The folder containing the dataset. The folder should contain,
            for each classes, a subfolder with only images inside.
        dispatch_fn: A function that should return a list of str
            representing the dataset (e.g, `["train", "a"]`) to represent
            the dataset `train/a`.
        image_size: The size of the image, or None to not resize images.
        transform: Transformation to apply to the image before the conversion
            to a torch tensor via `ToTensor()`. If `image_size` is not None, the
            resize transform will be applied before these, if you want to do the
            opposite, simply pass `None` as `image_size` and add the resize
            transformation manually.


    Returns:
        A tuple containing two or three datasets corresponding to training, validation
        and testing dataset.
    """

    import torchvision.transforms

    from .torch_utils import ImageDataset, OptionalToTensor

    # Retrieve files:
    py_datasets = load_hierarchical_python_image_dataset(folder, dispatch_fn)

    # Create the transform:
    transforms: List[Callable[[Image.Image], Image.Image]] = []
    if image_size is not None:
        transforms.append(torchvision.transforms.Resize(image_size))
    if transform is not None:
        transforms.append(transform)
    transforms.append(OptionalToTensor())
    transform = torchvision.transforms.Compose(transforms)

    def create_dict(from_):
        if isinstance(from_, dict):
            return {k: create_dict(v) for k, v in from_.items()}
        else:
            return ImageDataset(from_, None, transform)

    return create_dict(py_datasets)


def load_pytorch_image_dataset(
    folder: pathlib.Path,
    image_size: Optional[Tuple[int, int]] = None,
    train_split: Union[float, Tuple[float, float]] = 0.8,
    shuffle: Union[bool, int] = True,
    aggregate_fn: Callable[[str], Optional[str]] = lambda x: x,
    filter_fn: Callable[[str, pathlib.Path], bool] = lambda *args: True,
    transform: Optional[Callable[[Image.Image], Image.Image]] = None,
):
    """
    Creates a pytorch image dataset from the given folder and
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
            If an int is given, use it as the seed for shuffling. If False, do not
            shuffle.
        filter_fn: A function to filter out images. This function should take
            a string (name of the file) and a path to the file and returns True
            if the image should be included, False if it should be excluded.
        transform: Transformation to apply to the image before the conversion
            to a torch tensor via `ToTensor()`. If `image_size` is not None, the
            resize transform will be applied before these, if you want to do the
            opposite, simply pass `None` as `image_size` and add the resize
            transformation manually.


    Returns:
        A tuple containing two or three datasets corresponding to training, validation
        and testing datasets.
    """

    import torchvision.transforms
    from torch.utils.data import Subset

    from .torch_utils import ImageDataset, OptionalToTensor

    # Retrieve files:
    files = load_python_image_dataset(folder, shuffle, filter_fn)

    # Create the transform:
    transforms: List[Callable[[Image.Image], Image.Image]] = []
    if image_size is not None:
        transforms.append(torchvision.transforms.Resize(image_size))
    if transform is not None:
        transforms.append(transform)
    transforms.append(OptionalToTensor())
    transform = torchvision.transforms.Compose(transforms)

    # Create the dataset:
    dataset = ImageDataset(files, None, transform)

    # Split dataset:
    if isinstance(train_split, float):
        i1 = int(train_split * len(dataset))
        return (
            (
                Subset(dataset, range(i1)),
                Subset(dataset, range(i1, len(dataset))),
            ),
        )
    else:
        i1 = int(train_split[0] * len(dataset))
        i2 = i1 + int(train_split[1] * len(dataset))
        return (
            Subset(dataset, range(i1)),
            Subset(dataset, range(i1, i2)),
            Subset(dataset, range(i2, len(dataset))),
        )


def load_tensorflow_image_dataset(
    folder: pathlib.Path,
    image_size: Optional[Tuple[int, int]] = None,
    train_split: Union[float, Tuple[float, float]] = 0.8,
    shuffle: Union[bool, int] = True,
    aggregate_fn: Callable[[str], Optional[str]] = lambda x: x,
    filter_fn: Callable[[str, pathlib.Path], bool] = lambda *args: True,
):
    """
    Creates a tensorflow image dataset from the given folder and
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
            If an int is given, use it as the seed for shuffling. If False, do not
            shuffle.
            False otherwise.
        filter_fn: A function to filter out images. This function should take
            a string (name of the file) and a path to the file and returns True
            if the image should be included, False if it should be excluded.

    Returns:
        A tuple containing two or three datasets corresponding to training, validation
        and testing datasets.
    """

    # We only import tensorflow here to avoid breaking utils import when
    # tensorflow is not available.
    import tensorflow as tf

    # Retrieve files:
    files = load_python_image_dataset(folder, shuffle, filter_fn)

    # Convert files to filenames (str):
    filenames = [str(f) for f in files]
    n_images = len(files)

    # Create the tensorflow dataset:
    dataset = tf.data.Dataset.from_tensor_slices(filenames)

    # Preprocess function to load, resize and scale the image to [0, 1].
    def preprocess(filename):
        x = tf.io.read_file(filename)
        x = tf.image.decode_image(x, channels=3, expand_animations=False)
        x = tf.image.convert_image_dtype(x, tf.float32)
        if image_size is not None:
            x = tf.image.resize(x, image_size)
        return x

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
