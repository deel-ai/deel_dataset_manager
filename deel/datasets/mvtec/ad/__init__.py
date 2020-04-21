# -*- encoding: utf-8 -*-

import pathlib
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
        super().__init__("mvtec-ad", version, settings)

    def _get_provider(self) -> FtpSingleFileProvider:
        return FtpSingleFileProvider(
            self._settings.local_storage,
            MvtecAdDataset.MVTEC_AD_REMOTE_FILE,
            "mvtec-ad",
            authenticator=MvtecAdDataset.MVTEC_AUTHENTICATOR,
        )

    def _dispatch_fn(
        self, path: pathlib.Path
    ) -> typing.Optional[typing.Tuple[typing.List[str], str]]:
        parts = path.parts

        if parts[1] == "train":
            return ["train"], parts[0]

        elif parts[1] == "test":

            if parts[2] == "good":
                return ["test"], parts[0]
            else:
                return ["unknown"], "{}_{}".format(parts[0], parts[-1])

        else:
            return ["ground_truth"], "{}_{}".format(parts[0], parts[-1])

    def load_pytorch(
        self,
        path: pathlib.Path,
        image_size: typing.Tuple[int, int] = (64, 64),
        unique_labels: bool = False,
        transform: typing.Callable = None,
    ):
        """ Load method for the `pytorch` mode.
        """
        from ...utils import load_hierarchical_pytorch_image_dataset

        return load_hierarchical_pytorch_image_dataset(
            path, self._dispatch_fn, image_size=image_size, unique_labels=unique_labels
        )
