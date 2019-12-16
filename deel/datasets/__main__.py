# -*- encoding: utf-8 -*-

import argparse

from .dataset import Dataset
from .settings import read_settings, get_default_settings
from .providers.local_provider import LocalProvider
from .providers.remote_provider import RemoteProvider


def list_datasets(args: argparse.Namespace):
    """ List the datasets as specified by `args`.

    Args:
        args: Arguments from the command line.
    """

    if args.config is None:
        settings = get_default_settings()
    else:
        settings = read_settings(args.config)

    provider = settings.make_provider()
    location = ""

    if isinstance(provider, RemoteProvider):
        if args.local:
            provider = provider.local_provider()
            location = str(provider.root_folder)
        else:
            location = provider.remote_url
    elif isinstance(provider, LocalProvider):
        location = str(provider.root_folder)

    print("Listing datasets at {}:".format(location))

    # List datasets:
    datasets = sorted(provider.list_datasets())
    for dataset in datasets:
        versions = sorted(provider.list_versions(dataset), reverse=True)
        latest = provider.get_version("latest", versions)
        print(
            "  {}: {}".format(
                dataset,
                ", ".join(v if v != latest else v + " [latest]" for v in versions),
            )
        )


def download_datasets(args: argparse.Namespace):
    """ Download the dataset specified by `args`.

    Args:
        args: Arguments from the command line.
    """

    if args.config is None:
        settings = get_default_settings()
    else:
        settings = read_settings(args.config)

    for dataset in args.datasets:
        print("Fetching {}... ".format(dataset))

        # Split name:version:
        parts = dataset.split(":")
        if len(parts) == 1:
            parts += ["latest"]
        name, version = parts

        # Download the dataset:
        path = Dataset(name, version, settings).load(force_update=args.force)

        print("Dataset {} stored at '{}'.".format(dataset, path))


parser = argparse.ArgumentParser(description="DEEL dataset manager")
parser.add_argument(
    "-c",
    "--config",
    type=argparse.FileType("r"),
    help="configuration file to use",
    default=None,
)

subparsers = parser.add_subparsers(help="sub-command help", dest="command")
subparsers.required = True

download_parser = subparsers.add_parser("list", help="list datasets")
download_parser.add_argument(
    "-l",
    "--local",
    action="store_true",
    help="for a non-local provider (e.g., WebDAV), list only local datasets",
)
download_parser.set_defaults(func=list_datasets)

download_parser = subparsers.add_parser("download", help="download datasets")
download_parser.add_argument(
    "datasets",
    type=str,
    nargs="+",
    help="datasets to download, format name:version with :version being optional",
)
download_parser.add_argument(
    "-f", "--force", action="store_true", help="force download"
)
download_parser.set_defaults(func=download_datasets)

args = parser.parse_args()
args.func(args)
