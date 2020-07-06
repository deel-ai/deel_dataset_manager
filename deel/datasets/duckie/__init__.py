# -*- encoding: utf-8 -*-

import pathlib
import typing

from ..dataset import Dataset
from ..settings import Settings


class DuckieDataset(Dataset):

    """ Class for the Duckie dataset. """

    _default_mode: str = "pytorch"

    def __init__(
        self, version: str = "latest", settings: typing.Optional[Settings] = None
    ):
        """
        Args:
            version: Version of the dataset.
            settings: The settings to use for this dataset, or `None` to use the
            default settings.
        """
        super().__init__("duckie", version, settings)

    def load_path(self, path: pathlib.Path) -> pathlib.Path:
        return path.joinpath("source")

    def load_pytorch(
        self, path: pathlib.Path, nstack: int = 4, transform: typing.Callable = None,
    ):
        """ Load method for the `pytorch` mode.

        Args:
            nstack: Number of images to stack for each sample.
            transform: Transform to apply to the image.

        Returns:
            A pytorch Dataset object representing the dataset.
        """
        from .torch import SourceDataSet

        return SourceDataSet(self.load_path(path), nstack, transform)
