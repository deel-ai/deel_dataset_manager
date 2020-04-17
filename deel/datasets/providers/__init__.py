# -*- encoding: utf-8 -*-

import logging
import pathlib
import typing

from .provider import Provider


logger = logging.getLogger(__name__)


def make_provider(
    provider_type: str,
    root_path: pathlib.Path,
    provider_options: typing.Dict[str, typing.Any] = {},
) -> Provider:

    """ Create a new provider using the given arguments.

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

    if provider_type == "local":
        from .local_provider import LocalProvider

        return LocalProvider(root_path)

    elif provider_type == "gcloud":
        from .gcloud_provider import GCloudProvider

        return GCloudProvider(root_path)

    elif provider_type == "webdav":
        from .webdav_provider import (
            WebDavProvider,
            WebDavAuthenticator,
            WebDavSimpleAuthenticator,
        )

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
                raise ValueError(
                    "Invalid authentication method '{}' for WebDAV provider.".format(
                        provider_options["auth"]["method"]
                    )
                )

        return WebDavProvider(
            root_path,
            remote_url=provider_options["url"],
            authenticator=webdav_authenticator,
        )

    elif provider_type == "ftp":
        from .ftp_providers import FtpProvider, FtpSimpleAuthenticator

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
                raise ValueError(
                    "Invalid authentication method '{}' for FTP provider.".format(
                        provider_options["auth"]["method"]
                    )
                )

        return FtpProvider(
            root_path,
            remote_url=provider_options["url"],
            authenticator=ftp_authenticator,
        )

    raise ValueError("Invalid provider type '{}'.".format(provider_type))
