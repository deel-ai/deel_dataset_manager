# -*- encoding: utf-8 -*-

import pathlib
import tensorflow as tf
import typing

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    BatchNormalization,
    Conv2D,
    Dense,
    Dropout,
    Flatten,
    MaxPooling2D,
)

from deel.datasets import load as load_dataset


class Model:

    # Input image shape:
    _image_shape: typing.Tuple[int, int, int]

    # Number of classes:
    _nclasses: int

    # The keras model:
    _model: Sequential

    def __init__(self, image_shape: typing.Tuple[int, int, int], num_classes: int):
        """
        Args:
            image_shape: Shape of the inputs image.
            num_classes: Number of classes.
        """
        self._nclasses = num_classes
        self._image_shape = image_shape

        self._model = self.build_model()

        optimizer = "adam"
        loss = "categorical_crossentropy"
        self._model.compile(optimizer=optimizer, loss=loss, metrics=["acc"])

    def train(
        self,
        train_set: tf.data.Dataset,
        validation_set: tf.data.Dataset,
        batch_size: int = 32,
        nepochs: int = 100,
    ):
        """ Train the model using the given sets and parameters.

        Args:
            train_set: Training set to use.
            validation_set: Validation set to use.
            batch_size: Size of the batch to use.
            nepochs: Number of epochs to train.
        """

        train_set, train_size = self._prepare_dataset(
            train_set, batch_size, is_training=True
        )
        valid_set, valid_size = self._prepare_dataset(
            validation_set, batch_size, is_training=False
        )

        self._model.fit(
            train_set,
            steps_per_epoch=train_size // batch_size,
            epochs=nepochs,
            validation_data=valid_set,
            validation_steps=valid_size // batch_size,
            verbose=2,
        )

    def predict(self, path: pathlib.Path):
        """ Predict the label of the image.

        Args:
            path: Path to the image to predict a label for.

        Returns:
            Prediction for the image (index of the class).
        """

        x = tf.io.read_file(str(path))
        x = tf.image.decode_bmp(x, channels=self._image_shape[2])
        x = tf.image.resize(x, [self._image_shape[0], self._image_shape[1]])
        x = x / 255.0

        pred = self._model.predict(tf.expand_dims(x, 0), 32, 0, 1)
        return pred[0].tolist().index(max(pred[0].tolist()))

    def _prepare_dataset(self, dataset, batch_size, is_training):

        nbItems = 0
        for _ in dataset:
            nbItems += 1

        dataset = dataset.batch(
            batch_size, drop_remainder=True if is_training else False
        )
        dataset = dataset.repeat()
        AUTOTUNE = 2
        dataset = dataset.prefetch(AUTOTUNE)

        return dataset, nbItems

    def build_model(self) -> Sequential:

        model = Sequential()

        model.add(
            Conv2D(
                32,
                kernel_size=(3, 3),
                strides=(1, 1),
                activation="relu",
                input_shape=self._image_shape,
            )
        )
        model.add(BatchNormalization(input_shape=(32,)))
        model.add(MaxPooling2D(pool_size=(2, 2)))

        model.add(Conv2D(32, kernel_size=(3, 3), activation="relu"))
        model.add(BatchNormalization(input_shape=(32,)))
        model.add(MaxPooling2D(pool_size=(2, 2)))

        model.add(Conv2D(32, kernel_size=(3, 3), activation="relu"))
        model.add(BatchNormalization(input_shape=(32,)))
        model.add(MaxPooling2D(pool_size=(2, 2)))

        model.add(Flatten())
        model.add(Dropout(0.5))
        model.add(Dense(1052, activation="relu"))
        model.add(Dropout(0.5))
        model.add(Dense(128, activation="relu"))
        model.add(Dense(64, activation="relu"))

        model.add(Dense(self._nclasses, activation="softmax"))

        return model


# Tensorflow is the default mode for blink so mode="tensorflow" is not required:
train_set, valid_set, x_test, y_test, label_names = load_dataset(
    "blink", mode="tensorflow", percent_train=40, percent_val=40
)

model = Model(train_set.element_spec[0].shape, len(label_names))
model.train(train_set, valid_set, nepochs=1)

# Prediction on the first image:
img_path = x_test[0]
pred_index = model.predict(img_path)
print("{}: {}".format(img_path, label_names[pred_index]))
