# -*- encoding: utf-8 -*-

import psutil
import typing

from pathlib import Path

from .settings import logger

# Link to the GCloud drive:
_GCLOUD_DRIVE_PATH = Path("/dev/disk/by-id/google-deel-datasets")


def find_gcloud_mount_path() -> typing.Optional[Path]:
    """
    -Try to find the GCloud datasets mount path.

    Returns:
        The mount path for the deel-datasets GCloud drive on the
        current machine, or `None` if the path was not found.
    """

    if not _GCLOUD_DRIVE_PATH.exists():
        logger.warning("Disk {} not available.".format(_GCLOUD_DRIVE_PATH))
        return None

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

    logger.warning("Disk {} not mounted.".format(target_drive))
    return None


if __name__ == "__main__":
    print(find_gcloud_mount_path())
