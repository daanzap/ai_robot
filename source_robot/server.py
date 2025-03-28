# serversend.py
import json
import queue
import socket
import time
from queue import Queue
from threading import Thread
import subprocess
import sys

from robot_motor_control import MotorControl

from settings_robot import robot_name

import logging

LOG_LEVEL = logging.INFO
LOG_FILE = "/var/log/ai_robot"
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

logging.info('starting ai robot server')

connection_alive = False


# raspivid -v -w 640 -h 480 -fps 30 -n -t 0 -l -o tcp://0.0.0.0:5001
def get_ip():
    number_of_tries = 40
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while number_of_tries > 0:
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
            break
        except Exception as e:

            logging.info(e)
            time.sleep(2)
            number_of_tries -= 1
            IP = '127.0.0.1'

    s.close()
    return IP


def broadcast_info():
    global connection_alive
    logging.info('start broadcast server')
    host_name = socket.gethostname()
    msg = {
        'name': robot_name,
        'hostname': host_name,
        'ip': get_ip()
    }
    msg = json.dumps(msg).encode('utf-8')
    dest = ('<broadcast>', 10100)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    data = 'no data yet'
    while True:
        time.sleep(2)
        if not connection_alive:
            logging.info(msg)
            s.setblocking(0)
            s.sendto(msg, dest)


broadcast_server = Thread(target=broadcast_info, daemon=True)
broadcast_server.start()

q = Queue()
q_motor_control = Queue()


def motor_control_thread(q_in):
    global connection_alive
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
    last_ping = int(time.time())
    while True:
        logging.info('in motor control thread')
        try:
            command = q_in.get(timeout=3)
        except queue.Empty:
            if time.time() - last_ping > 20:
                connection_alive = False
            continue

        last_ping = int(time.time())
        if str(command)[:-1] == "ping":
            logging.info("ping registered")
            continue
        if command != previous_command:
            commands[str(command)[:-1]]()
            previous_command = command


motor_control = Thread(target=motor_control_thread, args=(q_motor_control,), daemon=True)


def main_robot_control(q_out):
    global motor_control
    global connection_alive
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
            if connection_alive:
                c.send(b'connection already in use')
                continue
            connection_alive = True
            if not motor_control.is_alive():
                motor_control.start()

            if proc_id is not None:
                # proc_id.kill()
                time.sleep(2)
            else:


                # proc_id = subprocess.Popen(["raspivid","-v","-w","640", "-h", "480", "-fps","30","-n","-t", "0", "-l", "-o","tcp://0.0.0.0:5001","-fl"])
                command = ["rpicam-vid", "-t", "0", "--framerate", "30", "--width", "640", "--height", "480", "--codec",
                     "h264", "--inline", "-o", "udp://{}:5555".format(addr[0])]
                print(' '.join(command))
                proc_id = subprocess.Popen(command, stdout=sys.stdout, stderr=sys.stderr)
                # proc_id = subprocess.Popen(["rpicam-vid","-t","0","--framerate","15","--width","640","--height","480","--codec","h264","--inline","--listen","-o","tcp://0.0.0.0:5555".format(addr[0])])


            print("conection to {} established".format(addr[0]))
            c.send('connection ok'.encode('utf-8'))
        if message.startswith(b'robot_command'):
            command = str(message).split(':')
            q_out.put(command[1])


main_server = Thread(target=main_robot_control, args=(q_motor_control,), daemon=True)
main_server.start()

broadcast_server.join()
motor_control.join()
main_server.join()
