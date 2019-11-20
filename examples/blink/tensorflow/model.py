import tensorflow as tf
from tensorflow.keras.models import Sequential, model_from_json
from tensorflow.keras.layers import Activation, MaxPooling2D, Conv2D, Flatten, Dense, Dropout, Input, BatchNormalization

# from tensorflow.keras import callbacks
# import mlflow
# import mlflow.keras

from datetime import datetime
import os

class Model:
    def __init__(self):
        self.keras_model = None
        self._NUM_CLASSES = None
        self._EPOCHS = None
        self._IMAGE_SHAPE = None
        self._BATCH_SIZE = 32

    def train(self, train_set, valid_set, label_names, epochs):
        self._NUM_CLASSES = len(label_names)
        self._EPOCHS = epochs
        self._IMAGE_SHAPE = self.__compute_image_shape(train_set)
        train_set, self._TRAIN_SIZE = self.__prepare_dataset(train_set, is_training=True)
        valid_set, self._VALID_SIZE  = self.__prepare_dataset(valid_set, is_training=False)

        optimizer='adam'
        loss='categorical_crossentropy'

        self.keras_model = self.__build_keras_model()
        self.keras_model.compile(optimizer=optimizer, loss=loss, metrics=['acc'])

        tensorboard_callbacks = []
        # logdir = "logs/" + datetime.now().strftime("%Y%m%d-%H%M%S")
        # tensorboard_callbacks.append(callbacks.TensorBoard(log_dir=logdir))

        self.keras_model.fit(
            train_set,
            steps_per_epoch=self._TRAIN_SIZE // self._BATCH_SIZE,
            epochs=self._EPOCHS,
            validation_data=valid_set,
            validation_steps=self._VALID_SIZE // self._BATCH_SIZE,
            verbose = 2,
            callbacks=tensorboard_callbacks)

        # mlflow.log_param('_EPOCHS', self._EPOCHS)
        # mlflow.log_param('optimizer', optimizer)
        # mlflow.log_param('loss', loss)
        # mlflow.keras.log_model(self.keras_model, "models")

    def save(self, name):
        os.makedirs("modelSave", exist_ok=True)
        # serialize model to JSON
        model_json = self.keras_model.to_json()
        with open(os.path.join("modelSave", name + ".json"), "w") as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        self.keras_model.save_weights(os.path.join("modelSave", name + ".h5"))
        print("Saved model to disk")

    def load(self, name):
        # load json and create model
        json_file = open(os.path.join("modelSave", name + '.json'), 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.keras_model = model_from_json(loaded_model_json)
        # load weights into new model
        self.keras_model.load_weights(os.path.join("modelSave", name + ".h5"))
        print("Loaded model from disk")

        self._IMAGE_SHAPE = (self.keras_model.input.shape[1], self.keras_model.input.shape[2], self.keras_model.input.shape[3])

    def predict(self, img_path):
        def resize_image(image, image_shape):
            x = tf.io.read_file(image)
            x = tf.image.decode_bmp(x, channels=image_shape[2])
            x = tf.image.resize(x, [image_shape[0], image_shape[1]])
            x = x / 255.0
            return x
    
        img = resize_image(img_path, self._IMAGE_SHAPE)
        img = tf.expand_dims(img, 0)
        pred = self.keras_model.predict(img, 32, 0, 1)
        pred_index = pred[0].tolist().index(max(pred[0].tolist()))

        return pred_index

    def __compute_image_shape(self, dataset):
        item = dataset.__iter__().get_next()
        return item[0].shape

    def __prepare_dataset(self, dataset, is_training):

        nbItems = 0
        for __ in dataset:
            nbItems += 1

        dataset = dataset.batch(self._BATCH_SIZE, drop_remainder=True if is_training else False)
        dataset = dataset.repeat()
        AUTOTUNE = 2
        dataset = dataset.prefetch(AUTOTUNE)

        return dataset, nbItems

    def __build_keras_model(self):
        # mlflow.log_param('Model_Layer_Input', self._IMAGE_SHAPE)
        # mlflow.log_param('Model_Layer_Output', self._NUM_CLASSES)
        
        model = Sequential()

        model.add(Conv2D(32, kernel_size=(3, 3), strides=(1, 1), activation='relu', input_shape=self._IMAGE_SHAPE))
        model.add(BatchNormalization(input_shape=(32,)))
        model.add(MaxPooling2D(pool_size=(2, 2)))

        model.add(Conv2D(32, kernel_size=(3, 3), activation='relu'))
        model.add(BatchNormalization(input_shape=(32,)))
        model.add(MaxPooling2D(pool_size=(2, 2)))

        model.add(Conv2D(32, kernel_size=(3, 3), activation='relu'))
        model.add(BatchNormalization(input_shape=(32,)))
        model.add(MaxPooling2D(pool_size=(2, 2)))

        model.add(Flatten())
        model.add(Dropout(0.5))
        model.add(Dense(1052, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(128, activation='relu'))
        model.add(Dense(64, activation='relu'))

        model.add(Dense(self._NUM_CLASSES, activation='softmax'))

        return model
        