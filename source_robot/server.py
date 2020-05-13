#serversend.py
import json
import socket
import time
from queue import Queue
from threading import Thread
import subprocess


from robot_motor_control import MotorControl

from settings_robot import robot_name

import logging

LOG_LEVEL = logging.INFO
LOG_FILE = "/var/log/ai_robot"
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, level=LOG_LEVEL)

logging.info('starting ai robot server')
# raspivid -v -w 640 -h 480 -fps 30 -n -t 0 -l -o tcp://0.0.0.0:5001
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def broadcast_info():
    logging.info('start broadcast server')
    host_name = socket.gethostname()
    msg = {
        'name': robot_name,
        'hostname': host_name,
        'ip':get_ip()
    }
    msg = json.dumps(msg).encode('utf-8')
    dest = ('<broadcast>', 10100)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    data = 'no data yet'
    while True:
        time.sleep(2)
        logging.info(msg)
        s.setblocking(0)
        s.sendto(msg, dest)

broadcast_server = Thread(target=broadcast_info, daemon=True)
broadcast_server.start()


q = Queue()
q_motor_control = Queue()

def motor_control_thread(q_in):
    logging.info('starting motor control thread')
    motor = MotorControl()
    commands = {
        'forward': motor.forward,
        'turn_left': motor.turn_left,
        'turn_right': motor.turn_right,
        'backward': motor.backward,
        'all_stop': motor.all_stop

    }
    previous_command = ''

    while True:
        logging.info('in motor control thread')
        command = q_in.get()
        logging.info(command)
        if command != previous_command:

            commands[str(command)[:-1]]()
            previous_command = command

motor_control = Thread(target=motor_control_thread, args=(q_motor_control,),daemon=True)
motor_control.start()

def main_robot_control(q_out):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to a public host, and a well-known port
    logging.info(get_ip())
    serversocket.bind(('', 9999))
    # become a server socket
    serversocket.listen(5)
    proc_id = None
    while True:
        c, addr = serversocket.accept()

        message = c.recv(1024)
        # message = 'Got connection from {}'.format(addr)
        if message == b'connection request':
            if proc_id is not None:
                proc_id.kill()
                time.sleep(2)
            proc_id = subprocess.Popen(["raspivid","-v","-w","640", "-h", "480", "-fps","30","-n","-t", "0", "-l", "-o", "tcp://0.0.0.0:5001"])
            time.sleep(2)
            c.send('connection ok'.encode('utf-8'))
        if message.startswith(b'robot_command'):
            command = str(message).split(':')
            q_out.put(command[1])



main_server = Thread(target=main_robot_control, args=(q_motor_control,), daemon=True)
main_server.start()

broadcast_server.join()
motor_control.join()
main_server.join()