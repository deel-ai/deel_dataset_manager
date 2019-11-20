import os
import pathlib
from deel.datasets.blink.blink_dataset import DatasetBlink
import tensorflow as tf
import random
import numpy as np
import cv2

def load(forceDownload=False, percent_train=40, percent_val=40, image_shape=(64,64,3)):
  # Download Part
  deelDataset = DatasetBlink()
  deelDataset.load(forceDownload)
  paths = deelDataset.getDownloadPAth()

  # Generation Part
  tfData = TensorflowData(paths)

  return tfData.prepare(percent_train, percent_val, image_shape)

class TensorflowData:
  def __init__(self, paths):
    self._IMAGE_SHAPE = None
    self._NUM_CLASSES = None
    self.paths = paths

  def prepare(self, percent_train, percent_val, image_shape):
    self._IMAGE_SHAPE = image_shape
    x_train, y_train, x_val, y_val, x_test, y_test, label_names = self.split_train_val_test(os.path.join(self.paths[0], "final_db_anonymous"), percent_train, percent_val)

    train_set = self.__tfdata_generator(x_train, y_train, is_training=True)
    valid_set  = self.__tfdata_generator(x_val, y_val, is_training=False)

    return train_set, valid_set, x_test, y_test, label_names

  def split_train_val_test(self, data_dir, percent_train, percent_val):
    data_dir = pathlib.Path(data_dir)
    class_names = np.array([item.name for item in data_dir.glob('*')])
    class_names = [item for item in class_names if item not in ["anonymization_mapping.csv", "warnings"]]
    class_names.sort()

    split = {}
    split["train"] = {"x":[], "y":[]}
    split["val"] = {"x":[], "y":[]}
    split["test"] = {"x":[], "y":[]}
    class_cpt = 0
    self._NUM_CLASSES = len(class_names)
    for cur_class in class_names:
      cur_class_file_list = list(data_dir.glob(cur_class + '/*.bmp'))
      random.Random(4).shuffle(cur_class_file_list)
      cpt = 0
      cur_class_length = len(cur_class_file_list)
      for cur_class_file in cur_class_file_list:
        if (cpt < cur_class_length * (percent_train / 100)):
          split["train"]["x"].append(str(cur_class_file))
          split["train"]["y"].append(class_cpt)
        elif ((cpt < cur_class_length * ((percent_train + percent_val)/ 100))
          and (cpt >= cur_class_length * (percent_train / 100))):
          split["val"]["x"].append(str(cur_class_file))
          split["val"]["y"].append(class_cpt)
        else:
          split["test"]["x"].append(str(cur_class_file))
          split["test"]["y"].append(class_cpt)
        cpt += 1
      class_cpt += 1

    return split["train"]["x"], split["train"]["y"], split["val"]["x"], split["val"]["y"], split["test"]["x"], split["test"]["y"], class_names

  def __tfdata_generator(self, images, labels, is_training):
      dataset = tf.data.Dataset.from_tensor_slices((images, labels))
      if is_training:
        dataset = dataset.shuffle(5000)  # depends on sample size

      dataset = dataset.map(self.__preprocess_fn, 4)

      return dataset

  def __preprocess_fn(self, image, label):
      '''A transformation function to preprocess raw data into trainable input. '''
      x = self.__resize_image(image, self._IMAGE_SHAPE)
      y = tf.one_hot(tf.cast(label, tf.uint8), self._NUM_CLASSES)

      return x, y

  def __resize_image(self, image, image_shape):
      x = tf.io.read_file(image)
      x = tf.image.decode_bmp(x, channels=image_shape[2])
      x = tf.image.resize(x, [image_shape[0], image_shape[1]])
      x = x / 255.0
      return x