#serversend.py
import json
import socket
import time

robot_name = 'robat'

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

host_name = socket.gethostname()
msg = {
    'name': robot_name,
    'hostname': host_name,
    'ip':get_ip()
}
msg = json.dumps(msg).encode('utf-8')
dest = ('<broadcast>', 10100)



while True:
    print(msg)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(msg, dest)
    time.sleep(1)

