# -*- encoding: utf-8 -*-

import numpy as np
import pathlib
import struct

from collections import OrderedDict
from typing import Dict, List, Tuple

from .. import logger


class CostTable:

    """ Wrapper class to easily access the ACAS-Xu datatable. """

    # Size of a data block:
    BLOCK_SIZE = 0xB410817

    # Shape of the data to parse:
    SHAPE = (12, 12, 41, 41, 39, 10)

    # Orders of keys:
    KEYS = ("intrspeed", "ownspeed", "psi", "theta", "range", "vertical_tau")

    # Path to the file containing the data:
    path: pathlib.Path

    # Mapping from cut name to cut values:
    cuts: Dict[str, np.ndarray] = {}

    # Tables:
    tables: Dict[str, np.ndarray] = {}

    def __init__(self, path: pathlib.Path, load: bool = True):
        """
        Args:
            path: Path to the ACAS-Xu table file.
            load: Load the table or not. If False, you need to
            manually load the data using the `.load()` method.
        """
        self.path = path

        if load:
            self.load()

    def _parse_aux_data(self, data: bytes):
        """ Parse auxiliary data from the given byte array.

        Args:
            data: Buffer of data to parse.

        Returns:
            An `OrderedDict` mapping each cut name to the list of corresponding
            values, in the order they were read from the buffer.
        """

        # Number of dimension:
        ndim: int = struct.unpack_from("i", data)[0]

        # Number of cuts for each dimension:
        ncuts: Tuple[int, ...] = struct.unpack_from("i" * ndim, data, 4)

        # Offset of the data:
        offset = 4 + ndim * 4

        # Names of the cuts:
        cut_names: List[str] = []
        for _ in range(ndim):
            # Read the number of bytes in the name:
            nbytes: int = struct.unpack_from("B", data, offset)[0]

            # Read and decode the cut name:
            cut_names.append(data[offset + 1 : offset + 1 + nbytes].decode("utf-8"))

            # Increase offset:
            offset += 1 + nbytes

        # Values of the cut:
        cut_values: List[List[float]] = []
        for nvalues in ncuts:
            cut_values.append(list(struct.unpack_from("d" * nvalues, data, offset)))
            offset += nvalues * 8

        return OrderedDict(zip(cut_names, cut_values))

    def _parse_data(self, data):
        """ Parse a data block from the given buffer.

        Args:
            data: The buffer containing the data to parse.

        Returns:
            A numpy array containing the parsed data as int16 values.
        """
        return np.frombuffer(data, dtype="int16").reshape(CostTable.SHAPE)

    def load(self):

        """ Load the data from the underlying table file. """

        cost_cuts = []
        cost_values = []

        with open(self.path, "rb") as fp:
            for i in range(23):
                offset = i * CostTable.BLOCK_SIZE
                logger.info("Reading block {} at offset {:#x}... ".format(i, offset))

                fp.seek(offset)
                byte = fp.read(4)
                magic_number = struct.unpack("i", byte)[0]
                assert magic_number == 0x0662, (
                    "MagicNumber is not good 0x%X" % magic_number
                )

                fp.seek(offset + 25)
                aux_data_size = struct.unpack("i", fp.read(4))[0]
                assert aux_data_size == 0x524, (
                    "AuxDataSize is not good 0x%X" % aux_data_size
                )

                aux_data = fp.read(aux_data_size)
                cost_cuts.append(self._parse_aux_data(aux_data))

                fp.seek(offset + int(0x553))
                data_size = int(struct.unpack("I", fp.read(4))[0])
                assert data_size == 0x5A08160, "DataSize is not good 0x%X" % data_size

                # Not sure if the scale factor (first int32 of data segment) is part of
                # the data size.
                data = fp.read(data_size * 2)
                cost_values.append(self._parse_data(data))

        for cuts in cost_cuts:
            for k, v in cuts.items():
                self.cuts[k] = np.array(v)

        entries = {
            "COC": (0, 1, 2, 3, 4),
            "WR": (5, 6, 7, 8, 9),
            "WL": (5, 10, 11, 12, 13),
            "R": (14, 15, 16, 17, 18),
            "L": (14, 19, 20, 21, 22),
        }

        for k, v in entries.items():
            self.tables[k] = np.array([cost_values[i] for i in v])

    def get_round_idx(self, array: np.ndarray, value: float) -> int:

        """ Retrieve the index of the closest value from the given array.

        Args:
            array: Array of values to search from, must be sorted.
            value: Value to lookup.

        Returns:
            The index of the closest value to `value` in `array`.
        """

        idx: int = np.searchsorted(array, value)

        if idx == 0:
            return idx

        if idx == len(array):
            return idx - 1

        if abs(array[idx - 1] - value) < abs(array[idx] - value):
            return idx - 1

        return idx

    def get_cost(self, table: str, params: Dict[str, float]) -> np.ndarray:

        """ Retrieve the costs from the given table according to the given parameters.

        Args:
            table: Table to retrieve the costs from.
            params: Parameteres to retrieve the right costs from the table. Must
            contains a value for each key in `CostTable.KEYS`.

        Returns:
            A numpy array containing the costs.
        """

        # Get the table:
        data = self.tables[table]

        # Find indices:
        idx = (slice(data.shape[0]),) + tuple(
            self.get_round_idx(self.cuts[k], params[k]) for k in CostTable.KEYS
        )

        return data[idx]  # type: ignore
