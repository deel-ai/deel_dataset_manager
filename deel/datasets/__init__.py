# -*- encoding: utf-8 -*-

import importlib
import logging

from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

from .providers.exceptions import DatasetNotFoundError  # noqa
from .settings import Settings  # noqa


# List of aliases module: [alias1, alias2, alias3, ...]. The name
# of the module is always an alias.
_aliases: Dict[str, List[str]] = {
    "blink": ["blink"],
    "landcover": ["landcover"],
    "landcover.resolution": ["landcover.resolution", "landcover-resolution"],
    "airbus.helicopter": ["helicopter", "vibration", "airbus-helicopter"],
    "elecboards.components": ["components", "elecboards-components"],
    "acas": ["acas.xu", "acas-xu"],
    "bde": ["braking-distance-estimation"],
}


def load(
    dataset: str,
    mode: Optional[str] = None,
    version: str = "latest",
    force_update: bool = False,
    settings: Settings = None,
    **kwargs
) -> Any:

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

    # Replace - with .:
    dataset = dataset.replace("-", ".")

    # Check if this is an alias:
    for k, v in _aliases.items():
        if dataset in v:
            dataset = k
            break

    # Create the dataset class name:
    dataset_class_name = (
        "".join(part.capitalize() for part in dataset.split(".")) + "Dataset"
    )

    # Find the module and the class:
    try:
        module = importlib.import_module("." + dataset, __name__)
        dataset_class = getattr(module, dataset_class_name)

        # Instantiate the class:
        dataset_object = dataset_class(version, settings)
    except (ImportError, AttributeError):

        # Default mode is then path:
        if mode is None:
            mode = "path"

        # If the module or class is not found, and the mode is not path, we throw:
        if mode != "path":
            raise DatasetNotFoundError(dataset)

        from .dataset import Dataset

        # Otherwize we can use the default dataset class:
        dataset_object = Dataset(dataset, version, settings)

    # If the dataset object is required, we must download
    # it:
    if mode == "dataset":
        dataset_object.load(mode="path", force_update=force_update, **kwargs)
        return dataset_object

    # Create the dataset object and load:
    return dataset_object.load(mode=mode, force_update=force_update, **kwargs)
