# -*- encoding: utf-8 -*-

import pathlib
import typing

from ...dataset import Dataset
from ...settings import Settings


class AirbusHelicopterDataset(Dataset):

    # Default mode for the dataset (basic):
    _default_mode = "basic"

    def __init__(
        self, version: str = "latest", settings: typing.Optional[Settings] = None
    ):
        """
        Args:
            version: Version of the dataset.
            settings: The settings to use for this dataset, or `None` to use the
            default settings.
        """
        super().__init__("airbus-helicopter", version, settings)

    def load_basic(self, path: pathlib.Path):

        import pandas as pd

        xtrain = pd.read_hdf(path.joinpath("dftrain.h5"))
        xvalid = pd.read_hdf(path.joinpath("dfvalid.h5"))
        xtest = pd.read_hdf(path.joinpath("dffinal.h5"))

        yvalid = pd.read_csv(path.joinpath("gt.csv"))
        yvalid.sort_values("seqID", inplace=True)
        assert len(yvalid) == len(xvalid)
        ytest = pd.read_csv(path.joinpath("gt_final.csv"))
        ytest.sort_values("seqID", inplace=True)
        assert len(ytest) == len(xtest)

        return (
            xtrain.values,
            xvalid.values,
            yvalid["anomaly"].values,
            xtest.values,
            ytest["anomaly"].values,
        )
