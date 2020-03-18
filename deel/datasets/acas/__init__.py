# -*- encoding: utf-8 -*-

import pathlib
import typing

from ..dataset import Dataset
from ..settings import Settings

from .table import CostTable


class AcasDataset(Dataset):

    """ Class for the blink dataset. """

    _default_mode: str = "table"

    _single_file: bool = True

    def __init__(
        self, version: str = "latest", settings: typing.Optional[Settings] = None
    ):
        """
        Args:
            version: Version of the dataset.
            settings: The settings to use for this dataset, or `None` to use the
            default settings.
        """
        super().__init__("acas-xu", version, settings)

    def load_basic(self, path: pathlib.Path) -> CostTable:
        """ See `load_table`. """
        return self.load_table(path)

    def load_table(self, path: pathlib.Path) -> CostTable:
        """ Load the ACAS-Xu dataset into a more suitable structure.

        Args:
            path: Path to the file containing the table.

        Returns:
            A `CostTable` instance from the given path.
        """
        return CostTable(path)
