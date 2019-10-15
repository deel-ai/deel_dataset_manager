# -*- encoding: utf-8 -*-

import h5py
import os

from .landcover_dataset import LandCoverDataset

def load(framework=None, forceDownload=False):

    # Load the dataset
    dataset = LandCoverDataset()
    dataset.load(forceDownload)

    # No framework, load the dataset from the HDF5 file as numpy arrays
    if framework is None:
        path = os.path.join(dataset.unzippedPaths[0], 'landcover-1.0-20191015.h5')
        hdf5 = h5py.File(path, 'r')
        patches = hdf5['patches'][:]
        labels = hdf5['labels'][:]
        hdf5.close()
        return patches, labels
