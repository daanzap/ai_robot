import numpy as np
from .auto_pilot import AutoSteer

import os

import tensorflow as tf
from tensorflow import keras
from joblib import load


class AutoSteerStudent(AutoSteer):


    # ######## skLearn implementation#################
    def __init__(self):
        try:
            self.clf = load(os.path.join('..', 'models', 'auto_pilot.joblib'))
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
        size_array = dim[0] * dim[1] * 3  # width height time 3 channels
        image_data = camera_view_reduced.reshape(1, size_array)
        prediction = self.clf.predict(image_data)
        print(prediction)
        if prediction[0] == 0:
            return 'forward'
        elif prediction[0] == 1:
            return 'left'
        elif prediction[0] == 2:
            return 'right'
        else:
            return 'forward'
