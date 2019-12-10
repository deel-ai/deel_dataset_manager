# -*- encoding: utf-8 -*-

import logging
import typing


logger = logging.getLogger(__name__)


def load(
    dataset: str,
    framework: typing.Optional[str] = None,
    version: str = "latest",
    force_update: bool = False,
) -> typing.Any:

    """ Load the given dataset.

    This is a basic method that load datasets with standard parameters.

    This
    function splits the given datasets on '.' and use the various parts to
    select the dataset to load. The first part corresponds to the global dataset
    (e.g., landcover), and the other parts are the first arguments to the load method.
    For instance, `load("landcover.resolution") will use `landcover.load("resolution").

    Args:
        dataset: Dataset to load.
        framework: Framework to use ("pytorch" or "tensorflow").
        version: Version of the dataset.
        force_update: Force update of the local dataset if possible.

    Returns:
        The dataset in the format specified by `framework`.

    Raises:
        ValueError: If the `dataset` or `framework` is invalid.
    """

    # Split the dataset in parts:
    parts = dataset.split(".")

    load_fn: typing.Callable
    if parts[0] == "landcover":
        from .landcover import load as load_landcover

        load_fn = load_landcover
    elif parts[0] == "blink":
        from .blink import load as load_blink

        load_fn = load_blink
    else:
        raise ValueError("Dataset '{}' does not exists.".format(dataset))

    return load_fn(
        *parts[1:], framework=framework, version=version, force_update=force_update
    )
