# -*- encoding: utf-8 -*-

import typing

from ...dataset import Dataset
from ...settings import Settings
from ...providers.ftp_providers import FtpSimpleAuthenticator, FtpSingleFileProvider


class MvtecAdDataset(Dataset):

    """ Class for the blink dataset. """

    # URL of the remote file:
    MVTEC_AUTHENTICATOR = FtpSimpleAuthenticator("guest", "GU.205dldo")
    MVTEC_AD_REMOTE_FILE = (
        "ftp://ftp.softronics.ch/mvtec_anomaly_detection/mvtec_anomaly_detection.tar.xz"
    )

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
        super().__init__("mvtec-ad", version, settings)

    def _get_provider(self) -> FtpSingleFileProvider:
        return FtpSingleFileProvider(
            self._settings.local_storage,
            MvtecAdDataset.MVTEC_AD_REMOTE_FILE,
            "mvtec-ad",
            authenticator=MvtecAdDataset.MVTEC_AUTHENTICATOR,
        )
