# -*- encoding: utf-8 -*-

import pathlib
import typing

from ...dataset import Dataset
from ...settings import Settings


class ElecboardsComponentsDataset(Dataset):

    # Default mode for the dataset (basic):
    _default_mode = "path"

    def __init__(
        self, version: str = "latest", settings: typing.Optional[Settings] = None
    ):
        """
        Args:
            version: Version of the dataset.
            settings: The settings to use for this dataset, or `None` to use the
            default settings.
        """
        super().__init__("elecboards-components", version, settings)

    def load_path(self, path: pathlib.Path) -> pathlib.Path:
        return path.joinpath("components")
