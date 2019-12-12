# -*- encoding: utf-8 -*-

import importlib
import logging
import typing


logger = logging.getLogger(__name__)


def load(
    dataset: str,
    mode: typing.Optional[str] = None,
    version: str = "latest",
    force_update: bool = False,
    **kwargs
) -> typing.Any:

    """ Load the given dataset using the given arguments.

    Args:
        dataset: Dataset to load.
        mode: Mode to use. The `"path"` mode is always available and will
        simply returns the path to the local dataset. Each dataset have its
        own sets of available modes.
        version: Version of the dataset.
        force_update: Force update of the local dataset if possible.
        **kwargs: Extra arguments for the given dataset and mode.

    Returns:
        The dataset in the format specified by `mode`.

    Raises:
        ValueError: If the `dataset` does not exist.
    """

    # Find the module:
    try:
        module = importlib.import_module("." + dataset, __name__)
    except ImportError:
        raise ValueError("Dataset '{}' not found.".format(dataset))

    # Create the dataset class name:
    dataset_class_name = (
        "".join(part.capitalize() for part in dataset.split(".")) + "Dataset"
    )

    # Check that the class exists:
    if not hasattr(module, dataset_class_name):
        raise ValueError("Dataset '{}' not found.".format(dataset))

    # Retrieve the class:
    dataset_class = getattr(module, dataset_class_name)

    # Create the dataset object and load:
    return dataset_class(version).load(mode=mode, force_update=force_update, **kwargs)
