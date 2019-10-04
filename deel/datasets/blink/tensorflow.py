import os
import pathlib
from deel.datasets.blink.blink_dataset import DatasetBlink
import tensorflow as tf
import random
import numpy as np
import cv2

_BATCH_SIZE = 32
_NUM_CLASSES = 3
_IMAGE_SHAPE = (64,64,3)
def load(forceDownload=False):
    # Download Part
    deelDataset = DatasetBlink()
    paths = deelDataset.load(forceDownload)
    paths = deelDataset.getDownloadPAth()
    # Generation Part
    x_train, y_train, x_val, y_val, x_test, y_test, label_names = split_train_val_test(os.path.join(paths[0], "final_db_anonymous"), 40, 40)
    train_set = __tfdata_generator(x_train, y_train, is_training=True, batch_size=_BATCH_SIZE)
    valid_set  = __tfdata_generator(x_val, y_val, is_training=False, batch_size=_BATCH_SIZE)
    
    return train_set, valid_set, x_test, y_test, label_names

def split_train_val_test(data_dir, percent_train, percent_val):
  data_dir = pathlib.Path(data_dir)
  class_names = np.array([item.name for item in data_dir.glob('*')])
  class_names = [item for item in class_names if item not in ["anonymization_mapping.csv", "warnings"]]

  
  split = {}
  split["train"] = {"x":[], "y":[]}
  split["val"] = {"x":[], "y":[]}
  split["test"] = {"x":[], "y":[]}
  class_cpt = 0
  _NUM_CLASSES = len(class_names)
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

def __tfdata_generator(images, labels, is_training, batch_size=128):
    '''Construct a data generator using tf.Dataset'''

    dataset = tf.data.Dataset.from_tensor_slices((images, labels))
    if is_training:
        dataset = dataset.shuffle(5400)  # depends on sample size

    # Transform and batch data at the same time
    dataset = dataset.map(__preprocess_fn, 4)
    dataset = dataset.batch(_BATCH_SIZE, drop_remainder=True if is_training else False)

    # dataset = dataset.apply(tf.contrib.data.map_and_batch(
    #     __preprocess_fn, batch_size,
    #     num_parallel_batches=4,  # cpu cores
    #     drop_remainder=True if is_training else False))
    dataset = dataset.repeat()
    AUTOTUNE = 2
    dataset = dataset.prefetch(AUTOTUNE)

    return dataset

def __preprocess_fn(image, label):
    '''A transformation function to preprocess raw data into trainable input. '''
    x = __resize_image(image, _IMAGE_SHAPE)
    y = tf.one_hot(tf.cast(label, tf.uint8), _NUM_CLASSES)

    return x, y

def __resize_image(image, image_shape):
    x = tf.io.read_file(image)
    x = tf.image.decode_bmp(x, channels=image_shape[2])
    x = tf.image.resize(x, [image_shape[0], image_shape[1]])
    x = x / 255.0
    return x

# def __resize_image(image):
#     x = tf.io.read_file(image)
#     x = tf.image.decode_bmp(x, channels=_IMAGE_SHAPE[2])
#     x = tf.image.convert_image_dtype(x, tf.float32)
#     x = tf.image.resize(x, [_IMAGE_SHAPE[0], _IMAGE_SHAPE[1]])
#     # x = x / 255.0
    
#     return x