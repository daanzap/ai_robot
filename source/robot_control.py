import copy
import os
import json
import socket, sys
from threading import Thread, Lock
from queue import Queue
from source.strategies.strategy import AutoSteer

import time

import pygame
import cv2

# Create a var for storing an IP address:
from pygame.time import Clock

ip = "192.168.178.25"

# Start PyGame:
pygame.init()
display_width = 640
display_height = 480
screen = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Remote Webcam Viewer')
font = pygame.font.SysFont("Arial", 14)
# clock = pygame.time.Clock()
timer = 0
previousImage = ""
image = ""
robots_broadcasting = {}
q = Queue()
q2 = Queue()
clock = Clock()
red = (255,0,0)
green = (0,255,0)
black = (0,0,0)
white = (255,255,255)
screen.fill(white)
server_socket = None
robot_selected = False
current_robot = {}

connection_in_progress = False


def find_robots(out_q):
    """connect to one of the robots"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 10100))
    robots_broadcasting = {}
    while (1):
        m = s.recvfrom(4096)
        m_data = json.loads(m[0])
        print(m_data)
        if m_data['name'] not in robots_broadcasting:
            robots_broadcasting[m_data['name']] = m_data
        out_q.put(robots_broadcasting)
        time.sleep(2)




def connect_to_robot(robot_info):
    global connection_in_progress
    global robot_selected
    global server_socket
    global current_robot
    global ip
    current_robot = robot_info
    if not connection_in_progress:
        connection_in_progress = True
        print('connection to {}'.format(robot_info['ip']))
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # now connect to the web server on port 80 - the normal http port
        server_socket.connect((robot_info['ip'], 9999))
        ip = robot_info['ip']
        server_socket.send('connection request'.encode('utf-8'))
        robot_response = server_socket.recv(1024)
        if robot_response == b'connection ok':
            q2.put('connection ok')
            robot_selected = True
        connection_in_progress = False


def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()

def draw_button(robot_name, robot_info, y_coord, screen):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if 250 > mouse[0] > 50 and y_coord + 50 > mouse[1] > y_coord:
        pygame.draw.rect(screen, green, (50, y_coord, 150, 50))
        if click[0] == 1:
            connect_to_robot(robot_info)
    else:
        pygame.draw.rect(screen, red, (50, y_coord, 150, 50))
    small_text = pygame.font.Font('freesansbold.ttf', 20)
    TextSurf, TextRect = text_objects(robot_name, small_text)
    TextRect.center = (125, y_coord + 25)
    screen.blit(TextSurf, TextRect)

def select_robot():

    polling_thread = Thread(target=find_robots, args=(q,), daemon=True)
    polling_thread.start()
    robot_data = None
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        try:
            if q2.get_nowait() == 'connection ok':
                break
        except Exception as e:
            pass
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        if robot_data == None:
            q_data = q.get()

            robot_data = copy.deepcopy(q_data)
        else:
            try:
                q_data = q.get_nowait()
                robot_data = copy.deepcopy(q_data)
            except Exception as e:
                pass



        y_coord = 50
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        for robot,robot_info in robot_data.items():

            draw_button(robot,robot_info, y_coord,screen)


            y_coord += 70
        pygame.display.update()

pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

axes = 0
has_joystick = False

if len(joysticks) > 0:
    has_joystick = True
    joystick = joysticks[0]
    joystick.init()
    axes = joystick.get_numaxes()


while True:
    for i in range(axes):
        axis = joystick.get_axis(i)
        print("{} = {}".format(i, axis))
    if not robot_selected:
        select_robot()
    else:
        break

# try:
#     # cap = cv2.VideoCapture("tcp://192.168.178.25:5001/")
#     cap = cv2.VideoCapture()
#     cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
#     cap.set(cv2.CAP_PROP_POS_FRAMES, 40)
#     cap.open("tcp://{}:5001/".format(ip))
#
# except Exception as e:
#     print(str(e))

current_frame = None
frame_lock = Lock()
def frame_grabber():
    global current_frame
    try:
        # cap = cv2.VideoCapture("tcp://192.168.178.25:5001/")
        cap = cv2.VideoCapture()
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_POS_FRAMES, 50)
        cap.open("udp://{}:5001/".format(ip))

    except Exception as e:
        print(str(e))
    time.sleep(2)
    while True:
        time.sleep(0.015)
        with frame_lock:
            local_current_frame = cap.read()
            if local_current_frame is not None:
                current_frame = local_current_frame


frame_grabber_thread = Thread(target=frame_grabber, args=(), daemon=True)
frame_grabber_thread.start()

previous_command = ''

def send_command(robot_info, command):
    global previous_command
    if command == previous_command:
        return command
    previous_command = command
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((robot_info['ip'], 9999))
    server_socket.send('robot_command:{}'.format(command).encode('utf-8'))
    return command

def is_turning():
    if has_joystick:
        if joystick.get_axis(0) < -0.5 or joystick.get_axis(0) > 0.5:
            return True
    else:

        return False

def get_joysitck_input(axis):
    if has_joystick:
        return joystick.get_axis(axis)
    else:
        return 0

recording = False
# Main program loop:
false_frames = 0
file_open = False
auto_pilot = AutoSteer()


while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            print('r pressed')
            recording = not recording
            if recording:
                file_open = True
                timestr = time.strftime("%Y%m%d-%H%M%S")
                filename = "{}.log".format(timestr)
                file_path = os.path.join('logs', filename)
                f = open(file_path, "w")
            else:
                if file_open:
                    f.close()
                    file_open = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            print('reload model')
            auto_pilot.reload()


    keys = pygame.key.get_pressed()
    any_control_key_pressed = False
    turning = False
    command = 'all_stop'
    if keys[pygame.K_s]:
        command = send_command(current_robot, auto_pilot.steer(frame))
    else:
        if keys[pygame.K_LEFT] or get_joysitck_input(0) < -0.5:
            any_control_key_pressed = True
            turning = True
            command = send_command(current_robot,'turn_left')
        if keys[pygame.K_RIGHT] or get_joysitck_input(0) > 0.5:
            any_control_key_pressed = True
            turning = True
            command = send_command(current_robot,'turn_right')
        if keys[pygame.K_UP] or get_joysitck_input(1) < -0.5 and not turning:
            any_control_key_pressed = True
            command = send_command(current_robot,'forward')
        if keys[pygame.K_DOWN] or get_joysitck_input(1) > 0.5 and not turning:
            any_control_key_pressed = True
            command = send_command(current_robot,'backward')

        if not any_control_key_pressed:
            command = send_command(current_robot,'all_stop')


    with frame_lock:
        if current_frame is not None:

            valid, frame = current_frame
        else:
            continue
    # valid, frame = cap.read()
    if valid:
        image = frame
        previousImage = image
        # scale_percent = 5  # percent of original size
        # width = int(image.shape[1] * scale_percent / 100)
        # height = int(image.shape[0] * scale_percent / 100)
        width = 64
        height = 64
        dim = (width, height)
        resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
        if recording:
            print('recording')
            cv2.circle(image, (30,30), 4, (255,0,0),thickness=-1)
            size_array = dim[0]*dim[1]*3 # width height time 3 channels
            image_data = resized.reshape(1,size_array)
            image_string = ','.join([str(i) for i in image_data[0]])
            log_String = ','.join(([command,image_string]))
            f.write(log_String+"\n")

        #image[10:height+10, 10:width+10] = resized
        # Convert image
        try:

            image = pygame.image.frombuffer(image.tostring(), image.shape[1::-1], "RGB")

        # Interupt
        except:
            image = previousImage
        output = image
        screen.blit(output, (0, 0))
        # clock.tick(1000)
        pygame.display.flip()
    else:
        false_frames += 1
        if false_frames == 10000:
            # select_robot()
            false_frames = 0
            print('frame invalid')
