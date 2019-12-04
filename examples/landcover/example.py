from deel.datasets.landcover.landcover_dataset import LandCoverDataset
import h5py
import numpy as np


if __name__ == '__main__':
	# Load the Land Cover dataset from the DEEL platform
	landcover_dataset = LandCoverDataset()
	landcover_dataset.load()
	
	# Open the HDF5 file downloaded by the DEEL dataset manager
	h5_file = landcover_dataset.urls[0].split('/')[-1]
	h5_file_fullpath = landcover_dataset.unzippedPaths[0] + '/' + h5_file
	dataset_h5_file = h5py.File(h5_file_fullpath, 'r')
	
	# Load patches (images) and labels (classes) from the dataset
	all_patches, all_labels = np.array(dataset_h5_file['patches']), np.array(dataset_h5_file['labels'])
	dataset_h5_file.close()
	
	print("Successfully loaded LandCover dataset !\nLandCover dataset contains 'patches' ({}) & 'labels' ({})"\
		.format(all_patches.shape, all_labels.shape))