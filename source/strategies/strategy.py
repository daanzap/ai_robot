import os

import cv2
import numpy as np
from tensorflow.python.keras.models import load_model


class AutoSteer(object):
    ################## Keras deeplearning implementation ###################################
    def __init__(self):
        self.model_path = os.path.join('..', 'models', 'robot_model.h5')
        self.model = load_model(self.model_path)

    def reload(self):
        self.model = load_model(self.model_path)

    def steer(self,view):
        width = 64
        height = 64
        dim = (width, height)
        resized = cv2.resize(view, dim, interpolation=cv2.INTER_AREA)
        camera_view_reduced = np.array([resized.astype('float32') / 255 ])
        prediction = self.model.predict_classes(camera_view_reduced)[0]
        print(prediction)
        if prediction == 0:
            return 'forward'
        elif prediction == 1:
            return 'turn_left'
        elif prediction == 2:
            return 'turn_right'
        else:
            return 'forward'
