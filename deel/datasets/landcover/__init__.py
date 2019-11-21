# -*- encoding: utf-8 -*-

import h5py
import os

from .landcover_dataset import LandCoverDataset, LandCoverResolutionDataset


def load(bias='distribution', framework=None, forceDownload=False):

    # Load the dataset
    if bias == 'distribution':
        dataset = LandCoverDataset()
    elif bias == 'resolution':
        dataset = LandCoverResolutionDataset()
    else:
        raise ValueError('Unknown bias for landcover dataset.')
    dataset.load(forceDownload)

    # No framework, load the dataset from the HDF5 file as numpy arrays
    if framework is None:
        path = os.path.join(
            dataset.unzippedPaths[0],  dataset.h5_file)
        hdf5 = h5py.File(path, 'r')
        data = tuple(hdf5[k][:] for k in dataset.h5_keys)
        hdf5.close()
        return data
