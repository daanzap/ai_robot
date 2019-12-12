import socket,sys
from time import time

import pygame
import cv2

#Create a var for storing an IP address:
ip = "192.168.178.25"

#Start PyGame:
pygame.init()
screen = pygame.display.set_mode((640,640))
pygame.display.set_caption('Remote Webcam Viewer')
font = pygame.font.SysFont("Arial",14)
#clock = pygame.time.Clock()
timer = 0
previousImage = ""
image = ""

try:
  print(time())
  # cap = cv2.VideoCapture("tcp://192.168.178.25:5001/")
  cap = cv2.VideoCapture()
  cap.set(cv2.CAP_PROP_BUFFERSIZE,3)
  cap.open("tcp://{}:5001/".format(ip))
except Exception as e:
  print(str(e))
#Main program loop:
while True:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      sys.exit()

  valid, frame = cap.read()
  if valid:
    image = frame
    previousImage = image

  #Convert image
    try:


      image = pygame.image.frombuffer(image.tostring(), image.shape[1::-1],"RGB")

  #Interupt
    except:
      image = previousImage
    output = image
    screen.blit(output,(0,0))
    #clock.tick(1000)
    pygame.display.flip()
  else:
    print('frame invalid')