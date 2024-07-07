import numpy as np
from .auto_pilot import AutoSteer

import os

import tensorflow as tf
from tensorflow import keras
from joblib import load


class AutoSteerKeras(AutoSteer):

    ################## Keras deeplearning implementation ###################################
    def __init__(self):
        try:
            self.model = keras.models.load_model(os.path.join('..', 'models', 'my-keras-model.keras'))
            self.autopilot_load = True
        except Exception as e:
            print(e)
            self.autopilot_load = False


    def steer(self,view):
        if not self.autopilot_load:
            return "forward"
        reduce_camera_image = 5
        width = view.shape[1]
        height = view.shape[0]
        dim = (int(width / reduce_camera_image), int(height / reduce_camera_image))
        camera_view_reduced = view[::reduce_camera_image, ::reduce_camera_image]
        camera_view_reduced = np.array([camera_view_reduced.astype('float32') / 255])
        prediction = np.argmax(self.model.predict(camera_view_reduced))
        print(prediction)
        if prediction == 0:
            return 'forward'
        elif prediction == 1:
            return 'left'
        elif prediction == 2:
            return 'right'
        else:
            return 'forward'