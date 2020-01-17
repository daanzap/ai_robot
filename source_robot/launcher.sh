#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python server.py script, then back home

cd /
cd /home/pi/ai_robot/source_robot
python3 server.py
cd /