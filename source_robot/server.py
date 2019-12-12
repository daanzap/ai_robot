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
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a well-known port
serversocket.bind((socket.gethostname(), 9999))
# become a server socket
serversocket.listen(5)

data = 'no data yet'
while True:
    print(msg)
    s.setblocking(0)
    s.sendto(msg, dest)
    try:
        c, addr = serversocket.accept()
        print('Got connection from {}'.format(addr))
        c.send('Connecting with {}'.format(robot_name))
        c.recv(1024)
    except Exception as e:
        print(e)
    print(data)

