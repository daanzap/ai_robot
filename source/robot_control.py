import json
import socket, sys
from threading import Thread
from queue import Queue

import time

import pygame
import cv2

# Create a var for storing an IP address:
from pygame.time import Clock

ip = "192.168.178.25"

# Start PyGame:
pygame.init()
display_width = 640
display_height = 640
screen = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Remote Webcam Viewer')
font = pygame.font.SysFont("Arial", 14)
# clock = pygame.time.Clock()
timer = 0
previousImage = ""
image = ""
robots_broadcasting = {}
q = Queue()
clock = Clock()
red = (255,0,0)
green = (0,255,0)
black = (0,0,0)
white = (255,255,255)
screen.fill(white)


robot_selected = False

connection_in_progress = False

def find_robots(out_q):
    """connect to one of the robots"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 10100))
    robots_broadcasting = {}
    while (1):
        m = s.recvfrom(4096)
        m_data = json.loads(m[0])
        if m_data['name'] not in robots_broadcasting:
            robots_broadcasting[m_data['name']] = m_data
        out_q.put(robots_broadcasting)
        time.sleep(2)




def connect_to_robot(robot_info):
    global connection_in_progress
    if not connection_in_progress:
        connection_in_progress = True
        print('connection to {}'.format(robot_info['name']))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # now connect to the web server on port 80 - the normal http port
        s.connect((robot_info['ip'], 9999))
        s.send('connection request'.encode('utf-8'))
        robot_response = s.recv(1024)
        print(robot_response)
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
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        if robot_data == None:
            q_data = q.get()
            robot_data = q_data
        else:
            try:
                q_data = q.get_nowait()
                robot_data = q_data
            except Exception as e:
                pass




        y_coord = 50
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        for robot,robot_info in robot_data.items():

            draw_button(robot,robot_info, y_coord,screen)


            y_coord += 150

        pygame.display.update()



while True:
    if not robot_selected:
        select_robot()
    else:
        break

try:
    print(time())
    # cap = cv2.VideoCapture("tcp://192.168.178.25:5001/")
    cap = cv2.VideoCapture()
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
    cap.open("tcp://{}:5001/".format(ip))

except Exception as e:
    print(str(e))
# Main program loop:
while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    valid, frame = cap.read()
    if valid:
        image = frame
        previousImage = image

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
        print('frame invalid')
