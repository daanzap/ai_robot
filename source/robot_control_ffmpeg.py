import socket,sys
import subprocess as sp
import numpy
import matplotlib.pyplot as plt
import pygame

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
# ffmpeg flags nobuffer -flags low_delay -framedrop -i "tcp://192.168.178.25:5001"
# -vcodec h264 -acodec none -strict experimental -

ffmpegCmd = ['ffmpeg',
             '-i', 'tcp://192.168.178.25:5001',
             '-flags', 'low_delay',
             '-fflags', 'nobuffer',
             '-vcodec', 'rawvideo',
             '-pix_fmt', 'rgb24',
             '-f', 'image2pipe',
              '-']

ffmpeg = sp.Popen(ffmpegCmd, stdout = sp.PIPE)

even = True
while True:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      sys.exit()
  raw_image = ffmpeg.stdout.read(640*480*3)
  if even:
      even = False
      continue
  else:
      even = True
  # print(len(raw_image))
  image = numpy.frombuffer(raw_image, dtype='uint8')
  image = image.reshape((480, 640, 3))

  #image = image[::-1]

  try:

    # print(image.shape)
    image = pygame.image.frombuffer(image.tostring(), (640,480),"RGB")

#Interupt
  except:
    image = previousImage
  output = image
  screen.blit(output,(0,0))
  #clock.tick(1000)
  pygame.display.flip()
