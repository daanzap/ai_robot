import time                                  #import the time module
import piplates.MOTORplate as MOTOR          #import the MOTORplate module

class MotorControl(object):

    FORWARD = 'ccw'
    BACKWARD = 'cw'
    LEFT_TRACK = 2
    RIGHT_TRACK = 1
    
    def move_track(self,motor_number,direction,speed):
        MOTOR.dcSTOP(0,motor_number)
        MOTOR.dcCONFIG(0,motor_number,direction,speed,0)
        MOTOR.dcSTART(0,motor_number)

    def left_forward(self, speed=80.0):
        self.move_track(self.LEFT_TRACK,direction=self.FORWARD,speed=speed)

    def right_forward(self, speed=80.0):
        self.move_track(self.RIGHT_TRACK,direction=self.FORWARD,speed=speed)

    def left_backward(self, speed=80.0):
        self.move_track(self.LEFT_TRACK,direction=self.BACKWARD,speed=speed)

    def right_backward(self, speed=80.0):
        self.move_track(self.RIGHT_TRACK,direction=self.BACKWARD,speed=speed)

    def forward(self):
        self.left_forward()
        self.right_forward(
)
    def backward(self):
        self.left_backward()
        self.right_backward()

    def turn_left(self):
        self.left_backward()
        self.right_forward()

    def turn_right(self):
        self.right_backward()
        self.left_forward()

    def left_stop(self):
        MOTOR.dcSTOP(0,self.LEFT_TRACK)

    def right_stop(self):
        MOTOR.dcSTOP(0,self.RIGHT_TRACK)

    def all_stop(self):
        self.left_stop()
        self.right_stop()

        
if __name__ == "__main__":
    mc = MotorControl()
    print('forward')
    mc.forward()
    time.sleep(2)
    print('turn left')
    mc.turn_left()
    time.sleep(2)
    print('turn right')
    mc.turn_right()
    time.sleep(2)
    mc.all_stop()
    print('backwards')
    mc.backward()
    time.sleep(3)
    mc.all_stop()

