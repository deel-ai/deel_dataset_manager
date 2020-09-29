# -*- encoding: utf-8 -*-

import logging
import pathlib
import typing

from .provider import Provider
from .exceptions import InvalidConfigurationError


logger = logging.getLogger(__name__)


def make_provider(
    provider_type: str,
    root_path: pathlib.Path,
    provider_options: typing.Dict[str, typing.Any] = {},
) -> Provider:

    """
    Create a new provider using the given arguments.

    Args:
        provider_type: Type of the provider.
        root_path: Local path for the datasets.
        provider_options: Extra options to pass to the provider
        constructor.

    Returns:
        A provider corresponding to the given arguments.

    Raises:
        ValueError: If the given `provider_type` is invalid or if the
        given options do not match the given provider.
    """
    print("=============>0 webdav_provider")
    if provider_type == "local":
        from .local_provider import LocalProvider
        if "source" in provider_options:
            root_path = provider_options["source"]

        return LocalProvider(root_path)

    elif provider_type == "gcloud":
        from .gcloud_provider import GCloudProvider

        if "disk" not in provider_options:
            raise InvalidConfigurationError("No disk specified for gcloud provider.")

        return GCloudProvider(disk="google-" + provider_options["disk"])

    elif provider_type == "webdav":
        print("=============> webdav_provider")
        from .webdav_provider import (
            WebDavProvider,
            WebDavAuthenticator,
            WebDavSimpleAuthenticator,
        )

        # Remote path:
        remote_path = ""
        if "folder" in provider_options:
            remote_path = provider_options["folder"]

        # If authentication is required:
        webdav_authenticator: typing.Optional[WebDavAuthenticator] = None
        if "auth" in provider_options:

            # We currently only support simple authentication:
            if provider_options["auth"]["method"] == "simple":
                webdav_authenticator = WebDavSimpleAuthenticator(
                    provider_options["auth"]["username"],
                    provider_options["auth"]["password"],
                )
            else:
                raise InvalidConfigurationError(
                    "Invalid authentication method '{}' for WebDAV provider.".format(
                        provider_options["auth"]["method"]
                    )
                )

        return WebDavProvider(
            root_path,
            remote_url=provider_options["url"],
            remote_path=remote_path,
            authenticator=webdav_authenticator,
        )

    elif provider_type == "ftp":
        print("=============> ftp_providers")
        from .ftp_providers import (
            FtpProvider,
            FtpSimpleAuthenticator,
        )
        print("=============>2 ftp_providers")
        # If authentication is required:
        ftp_authenticator: typing.Optional[FtpSimpleAuthenticator] = None
        if "auth" in provider_options:

            # We currently only support simple authentication:
            if provider_options["auth"]["method"] == "simple":
                ftp_authenticator = FtpSimpleAuthenticator(
                    provider_options["auth"]["username"],
                    provider_options["auth"]["password"],
                )
            else:
                raise InvalidConfigurationError(
                    "Invalid authentication method '{}' for FTP provider.".format(
                        provider_options["auth"]["method"]
                    )
                )

        return FtpProvider(
            root_path,
            remote_url=provider_options["url"],
            authenticator=ftp_authenticator,
        )

    raise InvalidConfigurationError("Invalid provider type '{}'.".format(provider_type))
