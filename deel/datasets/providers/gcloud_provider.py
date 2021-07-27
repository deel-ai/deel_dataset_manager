# -*- encoding: utf-8 -*-

import psutil

from pathlib import Path

from . import logger
from .exceptions import InvalidConfigurationError
from .local_provider import LocalProvider


class GCloudProvider(LocalProvider):

    """The `GCloudProvider` is a simple alias for `LocalProvider`."""

    # Link to the GCloud drive:
    _GCLOUD_DRIVE_BASE_PATH = Path("/dev/disk/by-id/")

    def __init__(self, disk: str):
        super().__init__(self._find_gcloud_mount_path(disk))

    def _find_gcloud_mount_path(self, disk: str) -> Path:
        """
        -Try to find the GCloud datasets mount path.

        Returns:
            The mount path for the specified GCloud drive on the current machine.

        Raises:
            InvalidConfigurationError: If the disk does not exist or is not mounted.
        """
        _GCLOUD_DRIVE_PATH = self._GCLOUD_DRIVE_BASE_PATH.joinpath(disk)
        if not _GCLOUD_DRIVE_PATH.exists():
            raise InvalidConfigurationError(
                "Disk {} not found.".format(_GCLOUD_DRIVE_PATH)
            )

        # Find the actual drive:
        target_drive = _GCLOUD_DRIVE_PATH.resolve()
        logger.info("Disk {} targets {}.".format(_GCLOUD_DRIVE_PATH, target_drive))

        # List the mount points:
        for part in psutil.disk_partitions(True):
            if target_drive == Path(part.device):
                logger.info(
                    "Disk {} mounted to {}.".format(_GCLOUD_DRIVE_PATH, part.mountpoint)
                )
                return Path(part.mountpoint)

        raise InvalidConfigurationError("Disk {} not mounted.".format(target_drive))
