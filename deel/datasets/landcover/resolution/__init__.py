# -*- encoding: utf-8 -*-

import typing

from ...dataset import Dataset
from ...settings import Settings

from .. import LandcoverDataset


class LandcoverResolutionDataset(LandcoverDataset):

    h5_keys: typing.List[str] = ["patches", "labels", "sensibilities"]

    def __init__(
        self, version: str = "latest", settings: typing.Optional[Settings] = None
    ):
        """
        Args:
            version: Version of the dataset.
            settings: The settings to use for this dataset, or `None` to use the
            default settings.
        """
        Dataset.__init__(self, "landcover-resolution", version, settings)
