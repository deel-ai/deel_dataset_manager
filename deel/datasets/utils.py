# -*- encoding: utf-8 -*-

import pathlib
import random
import logging

from typing import List, Tuple, Optional, Union, Dict, Callable

log = logging.getLogger("deel.dataset.manager.utils")


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
        for each classes, a subfolder with only images inside.
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

    Returns: Two or three 2-tuple of numpy arrays corresponding to training,
    validation and testing dataset. Each dataset is a 2-tuple (x, y) where
    `x` is a 4-dimensional numpy array containing images and `y` a
    one-dimensional numpy array containing classes.
    """

    import numpy as np
    from PIL import Image

    # Retrieve files:
    files, plabels, _ = load_python_image_dataset(
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
            (images[:train_n], labels[:train_n]),
            (images[train_n:], labels[train_n:]),
        )
    else:
        train_n = int(n_images * train_split[0])
        val_n = train_n + int(n_images * train_split[1])
        return (
            (images[:train_n], labels[:train_n]),
            (images[train_n:val_n], labels[train_n:val_n]),
            (images[val_n:], labels[val_n:]),
        )


def aggregate_pytorch_dataset(
    dataset, aggregate_fn: Callable[[str], Optional[str]] = None
):
    """ Aggregate classes in a pytorch image dataset from.

    Args:
        dataset: The dataset.
        aggregate_fn: Callable to aggregate classes. The function should take
        the name of an original class (subfolder) and returns the name of the
        "parent" class. If the call returns `None`, the class is discarded.

    Returns: The aggregated dataset.
    """
    if aggregate_fn:  # there is an aggregation filter function, so do aggregate
        # run aggregation function on classes
        new_classes = {cls: aggregate_fn(cls) for cls in dataset.classes}
        new_classes_list = list(set(new_classes.values()))
        if len(new_classes_list) < len(dataset.classes):
            log.debug(
                "aggregation changed classes count {} => {}".format(
                    len(dataset.classes), len(new_classes_list)
                )
            )
            # number of class is different, modify indices to reflect changes
            convert_old_class_new = {
                old_idx: new_classes_list.index(new_classes[dataset.classes[old_idx]])
                for old_idx in range(len(dataset.classes))
            }
            dataset.samples = dataset.imgs = [
                (img[0], convert_old_class_new[img[1]]) for img in dataset.imgs
            ]
            dataset.targets = [convert_old_class_new[cls] for cls in dataset.targets]

        # only names may have changed
        dataset.classes = new_classes_list
        dataset.class_to_idx = {cls: idx for idx, cls in enumerate(new_classes_list)}

    return dataset


def filter_pytorch_dataset(
    dataset, filter_fn: Callable[[str, pathlib.Path], bool] = None
):
    """ Filters a pytorch image dataset from.

    Args:
        dataset: The dataset.
        filter_fn: A function to filter out images. This function should take
        a string (name of the file) and a path to the file and returns True
        if the image should be included, False if it should be excluded.

    Returns: The filtered dataset.
    """
    if filter_fn:  # there is a filter function, so do filter
        modified = False
        imgs, targets = [], []

        # inverse dict dataset.class_to_idx
        idx_to_class_str = {v: k for k, v in dataset.class_to_idx.items()}
        log.debug("filtering {} elements".format(len(dataset)))
        for cls, img in zip(dataset.targets, dataset.imgs):
            if filter_fn(idx_to_class_str[cls], img[0]):
                targets.append(cls)
                imgs.append(img)
            else:
                modified = True
        if modified:
            all_classes_idx_new = list(set(targets))
            if len(all_classes_idx_new) < len(dataset.classes):
                log.debug(
                    "filtering changed classes count {} => {}".format(
                        len(dataset.classes), len(all_classes_idx_new)
                    )
                )
                # some classes were filtered out so we remove them and recompute indices
                convert_old_class_new = {
                    val: idx for idx, val in enumerate(all_classes_idx_new)
                }
                new_classes = [dataset.classes[cls] for cls in all_classes_idx_new]
                targets = [convert_old_class_new[cls] for cls in targets]
                imgs = [(img[0], convert_old_class_new[img[1]]) for img in imgs]
                dataset.classes = new_classes
                dataset.class_to_idx = {cls: idx for idx, cls in enumerate(new_classes)}

            dataset.samples = dataset.imgs = imgs
            dataset.targets = targets
            log.debug("filtered {} elements".format(len(dataset)))
        else:
            log.debug("No element filtered out")

        # log.debug("classes idx", set([el[1] for el in dataset.samples]))
        # log.debug("classes idx", set([el[1] for el in dataset.imgs]))
    return dataset


def split_pytorch_dataset(
    dataset,
    train_split: Union[float, Tuple[float, float]] = 0.8,
    shuffle: Union[bool, int] = True,
):
    """ Splits the pytorch image dataset into train, [valid,] test.

    Args:
        dataset: The dataset to split.
        train_split: One or two float values. If a single value is specified,
        two datasets will be returned, one for training (using a percentage
        `train_split` of data) and one for testing. If two values are specified,
        three datasets will be returned: a training dataset, a validation
        dataset and a testing dataset.
        shuffle: If True, shuffle images before spliting with the default seed.
        If an int is given, use it as the seed for shufling. If False, do not
        shuffle.
        False otherwize.

    Returns: Two or three datasets corresponding to training, validation and
    testing dataset.
    """
    import numpy as np
    from torch.utils.data import Subset

    # list the indices of the dataset
    dataset_size = len(dataset)
    indices = list(range(dataset_size))
    if shuffle:
        np.random.shuffle(indices)

    # Thank you tox for not accepting a simplier expression...
    if isinstance(train_split, float):
        train_splits = [
            train_split,
        ]
    else:
        train_splits = list(train_split)

    numbers = [int(np.floor(percent * dataset_size)) for percent in train_splits]
    splits = [0]
    split = 0
    for number in numbers:
        split += number
        splits.append(split)
    if splits[-1] < dataset_size:
        splits.append(dataset_size)

    all_indices = [
        indices[split_min:split_max]
        for split_min, split_max in zip(splits[:-1], splits[1:])
    ]

    return tuple(Subset(dataset, split_indices) for split_indices in all_indices)


def load_pytorch_image_dataset(
    folder: pathlib.Path,
    image_size: Optional[Tuple[int, int]] = None,
    train_split: Union[float, Tuple[float, float]] = 0.8,
    shuffle: Union[bool, int] = True,
    aggregate_fn: Callable[[str], Optional[str]] = None,
    filter_fn: Callable[[str, pathlib.Path], bool] = None,
    transform: Callable = None,
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

    Returns: Two or three datasets corresponding to training, validation and
    testing dataset.
    """
    from torchvision.datasets import ImageFolder

    # create PyTorch dataset from image folder
    dataset = ImageFolder(folder, transform=transform)
    # use filter
    if filter_fn:
        dataset = filter_pytorch_dataset(dataset, filter_fn=filter_fn)
    if aggregate_fn:
        dataset = aggregate_pytorch_dataset(dataset, aggregate_fn=aggregate_fn)

    # split the dataset
    return split_pytorch_dataset(dataset, train_split=train_split, shuffle=shuffle)


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

    # Retrieve files:
    files, labels, _ = load_python_image_dataset(
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
