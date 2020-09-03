import numpy as np


class AutoSteer(object):

    def flatten_image(self, image):
        flattened_image =  []
        for row in image:
            image_row =[]
            for pixel in row:
                image_row.append(np.sum(pixel))
            flattened_image.append(image_row)
        return np.array(flattened_image)


    def steer(self,view):
        if view is None:
            return ''
        flatview = self.flatten_image(view)

        left = flatview[:50,50:]
        right = flatview[50:,50:]
        sum_left = np.sum(left)
        sum_right = np.sum(right)
        if sum_left < sum_right:
            return 'left'
        elif sum_right < sum_left:
            return 'right'
        elif sum_left == sum_right :
            return 'forward'
        else:
            return ''


