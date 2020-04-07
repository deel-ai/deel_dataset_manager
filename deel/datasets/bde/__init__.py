# -*- encoding: utf-8 -*-

import pathlib
import typing

from ..dataset import Dataset
from ..settings import Settings


class BdeDataset(Dataset):

    """
    The Braking Distance Estimation (BDE) dataset contains data that comes from
    of simulation code that simulates the braking phase of an A/C on the runway.
    The output of the simulation code is the necessary distance to stop the vehicle.
    Inputs of the simulation code contains 8 parameters that are important for the
    computation.

    Dataset provides value of inputs and the associated braking distance value
    computed by the simulation code. Due to intellectual property, name of inputs
    in dataset are anonymised (`Input_01`, `Input_02`, ...) and are rescaled.
    The output value is the true value returned by the simulation code.

    Inputs may be numerical or categorical. Numerical inputs are linked to physical
    parameters that directly impact the braking distance. Categorical are linked to
    environemental state or configuration of the vehicle.

    Three modes are availabe for the dataset:
    - `full`: This mode contains 6 numerical parameters and two categorical
    inputs. Numerical inputs are rescaled, and categorical inputs are anonymsed.
    - `one-state.rand`: This mode contains only the 6 numerical parameters. This
    is generated for one unique state of categorical inputs. The parameters are
    generated randomly inside the input hyper-rectangle.
    - `one-state.grid`: This mode contains only the 6 numerical parameters. This
    is generated for one unique state of categorical inputs. The parameters are
    generated among a grid.
    """

    # Default mode for the dataset (basic):
    _default_mode = "full"

    def __init__(
        self, version: str = "latest", settings: typing.Optional[Settings] = None
    ):
        """
        Args:
            version: Version of the dataset.
            settings: The settings to use for this dataset, or `None` to use the
            default settings.
        """
        super().__init__("bde", version, settings)

    def _load_csv(self, path: pathlib.Path):
        """ Read the CSV file pointed out by `path` and returns a
        `pandas.DataFrame` corresponding object.

        Args:
            path: Path to the CSV file.

        Returns: A `pandas.DataFrame` object corresponding to the content
        of the CSV file.
        """
        import pandas as pd

        return pd.read_csv(path, sep=";", index_col=0)

    def load_full(self, path: pathlib.Path):
        return self._load_csv(path.joinpath("BDE_Full.csv"))

    def load_one_state_rand(self, path: pathlib.Path):
        return self._load_csv(path.joinpath("BDE_OneState_rand.csv"))

    def load_one_state_grid(self, path: pathlib.Path):
        return self._load_csv(path.joinpath("BDE_OneState_grid.csv"))
