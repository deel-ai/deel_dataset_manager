# -*- encoding: utf-8 -*-

import pathlib
import typing

from ..dataset import Dataset
from ..settings import Settings

from .table import CostTable


class AcasDataset(Dataset):

    """ Class for the blink dataset. """

    _default_mode: str = "basic"

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

    def load_path(self, path: pathlib.Path) -> pathlib.Path:
        return path.joinpath("q_xuhtrm_v5r0_23ec_allSplits_noMB.dat")

    def load_basic(self, path: pathlib.Path) -> CostTable:
        """ Load the ACAS-Xu dataset into a more suitable structure.

        Args:
            path: Path to the file containing the table.

        Returns:
            A `CostTable` instance from the given path.
        """
        return CostTable(self.load_path(path))
