# -*- encoding: utf-8 -*-

import typing

from ..dataset import Dataset
from ..settings import Settings
from ..providers.http_providers import HttpSingleFileProvider


class EurosatDataset(Dataset):

    """ Class for the blink dataset. """

    # URL of the remote file:
    EUROSAT_REMOTE_FILE = "http://madm.dfki.de/files/sentinel/EuroSAT.zip"

    _default_mode: str = "path"

    def __init__(
        self, version: str = "latest", settings: typing.Optional[Settings] = None
    ):
        """
        Args:
            version: Version of the dataset.
            settings: The settings to use for this dataset, or `None` to use the
            default settings.
        """
        super().__init__("eurosat", version, settings)

    def _get_provider(self) -> HttpSingleFileProvider:
        return HttpSingleFileProvider(
            self._settings.local_storage, EurosatDataset.EUROSAT_REMOTE_FILE, "eurosat"
        )
