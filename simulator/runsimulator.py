import os
import json
import socket, sys
from threading import Thread
from queue import Queue
from random import randrange
import math

from imutils import perspective
import numpy as np
import time

import pygame
import cv2

from pygame.time import Clock

from strategies.auto_pilot import AutoSteer

# Start PyGame:
pygame.init()

display_width = 1100
display_height = 900
bounding_box_x = display_width - 400
bounding_box_y = display_height - 400

min_x = (display_width - bounding_box_x) / 2
max_x = display_width - min_x
min_y = (display_height - bounding_box_y) / 2
max_y = display_height - min_y

screen = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Robot simulator')
font = pygame.font.SysFont("Arial", 14)

clock = pygame.time.Clock()
robot_img = pygame.image.load('media/robot_for_sim.png')


def calculate_new_xy(old_xy,speed,angle_in_radians):
    new_x = old_xy[0] + (speed*math.cos(angle_in_radians))
    new_y = old_xy[1] - (speed*math.sin(angle_in_radians))
    return new_x, new_y

class Robot(pygame.sprite.Sprite):
    view_end = 400
    view_begin = 40

    def __init__(self, image, pos=(0, 0), size=(70, 70)):
        super(Robot, self).__init__()
        self.image_org = image
        self.image = self.image_org
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.angle = 0
        self.view_area = [(0,0),(0,0),(0,0),(0,0)]

    def update(self, angle, speed=0):
        self.angle = angle
        self.image = pygame.transform.rotate(self.image_org, angle)
        old_x, old_y = self.rect.center  # Save its current center.

        x,y = calculate_new_xy(self.rect.center,speed,math.radians(angle))
        if x < 0 or x > display_width:
            x = old_x
        if y < 0 or y > display_height:
            y = old_y

        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.rect.center = (x, y)  # Put the new rect's center at old center.

    def camera_view(self, surface, draw_camera_view=True):
        center_view = calculate_new_xy(self.rect.center,20,math.radians(self.angle))
        top_right = calculate_new_xy(center_view,self.view_end,math.radians((self.angle+30)%360))
        top_left = calculate_new_xy(center_view,self.view_end,math.radians((self.angle-30)%360))
        bottom_left = calculate_new_xy(center_view,self.view_begin,math.radians((self.angle-100)%360))
        bottom_right = calculate_new_xy(center_view,self.view_begin,math.radians((self.angle-260)%360))
        self.view_area = [top_right,top_left,bottom_left,bottom_right]

        raw_image = pygame.surfarray.array3d(surface)
        top_right_x , top_right_y = top_right
        top_left_x , top_left_y = top_left
        bottom_left_x , bottom_left_y = bottom_left
        bottom_right_x , bottom_right_y = bottom_right

        perspective_points = np.array([[top_right_x , top_right_y],
                              [top_left_x , top_left_y],
                              [bottom_right_x, bottom_right_y],
                              [bottom_left_x , bottom_left_y]
                              ])


        new_image = raw_image.astype(np.uint8)
        new_image = new_image.swapaxes(0,1)

        perspective_matrix = perspective_points
        if draw_camera_view:
            pygame.draw.polygon(surface, (255,0,0),self.view_area, 2)
            # pygame.draw.polygon(surface, (0, 0, 255), perspective_matrix, 2)

        screen_perspective = np.float32(perspective_matrix)
        w = 200
        h = 200
        screen_flattened = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
        # print screen_perspctive
        # print 'devider'
        # print screen_flattened
        M = cv2.getPerspectiveTransform(screen_perspective, screen_flattened)
        dst = cv2.warpPerspective(new_image, M, (w, h), borderMode=cv2.BORDER_REPLICATE)

        dst = cv2.transpose(dst)
        camera_surface = pygame.surfarray.make_surface(dst)
        pygame.draw.rect(surface,(0,0,0),(5,5,200,200),2)
        surface.blit(camera_surface, (5,5))
        dst = cv2.resize(dst,(100,100))
        return dst, surface





tile_size = 60
max_offset = 20
UP = 0
LEFT = 1
DOWN = 2
RIGHT = 3
direction = UP
second_up = False
first_pos = None
def in_bounding_box(x, y):
    return not (x < min_x or x > max_x or y < min_y or y > max_y)

def draw_tile(surface, x, y):
    rect = pygame.Rect(x-(.5*tile_size),y-(.5*tile_size),tile_size,tile_size)
    pygame.draw.rect(surface, (70,70,70), rect)

def get_random_offset(old_x, old_y):
    global existing_path,first_pos
    offset = randrange(max_offset * 2)
    boundary_avoindance = 1

    if offset > 20:
        offset = -1 * (offset- 20)
    else:
        offset = offset
    if direction == UP:
        if (old_x + (0.5*tile_size) + offset) > max_x:
            boundary_avoindance = -1
    if direction == LEFT:
        if (old_y - (0.5*tile_size) - offset) < min_y:
            boundary_avoindance = -1
    if direction == DOWN:
        if (old_x - (0.5*tile_size) - offset) < min_x:
            boundary_avoindance = -1
    if direction == RIGHT:
        if (old_y + (0.5*tile_size) + offset) > max_y:
            boundary_avoindance = 1



    return boundary_avoindance * offset


def work_towards_end(x, y):
    pass

def get_next_tile_position(x, y):
    global direction, tile_size, second_up
    tile_size_to_use = tile_size
    org_x = x
    org_y = y
    direction_of_travel = y
    direction_of_offset = x
    if y < min_y+tile_size and x > max_x - (3* tile_size):
        direction = LEFT
    if x < min_x+tile_size and y < min_y + (3* tile_size):
        direction = DOWN
    if y > max_y - tile_size and x < min_x + (3* tile_size):
        direction = RIGHT
        second_up = True
    if x > max_x - tile_size and y > max_y - (3* tile_size):
        direction = UP

    # TODO: SWITCH X, Y FOR LEFT RIGHT MOTION UGLY HACK!!!!! CHANGE IN THE FUTURE!!!
    if direction == LEFT:
        direction_of_offset,direction_of_travel = y,x
    if direction == DOWN:
        tile_size_to_use = -tile_size_to_use
    if direction == RIGHT:
        direction_of_offset,direction_of_travel = y, x
        tile_size_to_use = -tile_size_to_use

    direction_of_travel = direction_of_travel - tile_size_to_use

    if direction == RIGHT and  direction_of_travel > max_x/2:
        if first_pos is not None:
            first_pos_x,first_pos_y = first_pos
            number_of_tiles_til_turn = int((first_pos_x-direction_of_travel)/tile_size)
            target_pos = first_pos_y - (5 * tile_size * -1)

            if number_of_tiles_til_turn == 0:
                offset = 0
            else:
                offset = ((target_pos-direction_of_offset)/number_of_tiles_til_turn) * -1
    elif direction == UP and second_up:
        if first_pos is not None:
            first_pos_x,first_pos_y = first_pos
            number_of_tiles_til_turn = int((first_pos_x-direction_of_travel)/tile_size)
            target_pos = first_pos_x

            if number_of_tiles_til_turn == 0:
                offset = 0
            else:
                offset = ((target_pos-direction_of_offset)/number_of_tiles_til_turn) * -1
    else:
        offset = get_random_offset(org_x,org_y)

    direction_of_offset = direction_of_offset - offset
    if direction in [LEFT,RIGHT]:
        x,y = direction_of_travel,direction_of_offset
    else:
        x, y = direction_of_offset, direction_of_travel
    return x,y



def draw_path(surface, existing_path=[]):
    global direction, second_up,first_pos
    direction = UP

    second_up = False
    surface.fill((255, 255, 255))
    # first start position
    if len(existing_path) > 0:
        for x,y in existing_path:
            draw_tile(surface, x, y)

    else:
        x = max_x - tile_size
        y = (max_y/2)
        first_pos = (x,y)
        draw_tile(surface,x,y)
        existing_path.append((x, y))
        for tile_number in range(0,80):
            x,y = get_next_tile_position(x,y)
            if not in_bounding_box(x,y):
                print("out of bounds")
            if direction == UP and second_up and y == existing_path[0][1]:
                second_up = False
                break
            draw_tile(surface,x,y)
            existing_path.append((x,y))

    return existing_path





surface = pygame.Surface((display_width,display_height))

existing_path = draw_path(surface)
direction_of_travel = 90
first_loop = True
pilot = AutoSteer()
camera_view = None
show_camera_view = False
recording = False
font = pygame.font.Font('freesansbold.ttf', 32)
white = (255, 255, 255)
green = (0, 255, 0)
blue = (0, 0, 128)
text = font.render('Using strategy', True, green, white)
textRect = text.get_rect()
textRect.center = (int(800 // 2), int(40 // 2))
file_open = False
while True:
    speed = 0
    auto_pilot = False
    auto_pilot_direction = ''
    speed_setting = 4
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                direction_of_travel = 90
                existing_path = draw_path(surface, existing_path=[])
                initial_position_robot = existing_path[0]
                robot = Robot(robot_img,pos=initial_position_robot)

            if event.key == pygame.K_c:
                show_camera_view = not show_camera_view

            if event.key == pygame.K_r:
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


    keys = pygame.key.get_pressed()
    command = 'stop'
    if keys[pygame.K_s]:
        auto_pilot = True
        auto_pilot_direction = pilot.steer(camera_view)
        speed_setting = 4
    if keys[pygame.K_LEFT] or auto_pilot_direction == 'left':
        direction_of_travel += 7
        command = 'left'
    if keys[pygame.K_RIGHT] or auto_pilot_direction == 'right':
        direction_of_travel -= 7
        command = 'right'


    direction_of_travel = direction_of_travel%360


    if keys[pygame.K_UP] or auto_pilot:
        speed = speed_setting
        command = "forward"
    if keys[pygame.K_DOWN]:
        speed = -speed_setting
        command = "backward"
    existing_path = draw_path(surface, existing_path=existing_path)
    if first_loop:
        first_loop = False
        initial_position_robot = existing_path[0]
        robot = Robot(robot_img, pos=initial_position_robot)

    screen.blit(surface, (0, 0))
    robot.update(direction_of_travel,speed=speed)
    camera_view,surface = robot.camera_view(surface, draw_camera_view=show_camera_view)
    width = camera_view.shape[1]
    height = camera_view.shape[0]
    dim = (width, height)
    if recording:
        print('recording')
        pygame.draw.circle(surface, (255,0,0), (display_width-30,30), 5)

        size_array = dim[0] * dim[1] * 3  # width height time 3 channels
        image_data = camera_view.reshape(1, size_array)
        image_string = ','.join([str(i) for i in image_data])
        log_String = ','.join(([command, image_string]))
        f.write(log_String + "\n")
    screen.blit(surface, (0, 0))
    screen.blit(robot.image,robot.rect)
    if auto_pilot:
        screen.blit(text, textRect)


    pygame.display.flip()
    clock.tick(50)


