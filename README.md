# ai_robot
robotsoftware  for ai-robot course

 cd bitofpepper/ai_robot/
.git/            media/           simulator/       source_robot/
.idea/           openvpn_netgear/ source/          
daan@daan-GL702VSK:~$ cd bitofpepper/ai_robot/openvpn_netgear/
daan@daan-GL702VSK:~/bitofpepper/ai_robot/openvpn_netgear$ ls
ca.crt       client.crt  dhcp-client-request.sh
client.conf  client.key  start_vpn.sh
daan@daan-GL702VSK:~/bitofpepper/ai_robot/openvpn_netgear$ ./start_vpn.sh 


robot start robot service

root@raspberrypi:/lib/systemd/system# 
ai_robot.service
```
[Unit]
Description=Run robot server
Wants=network-online.target
After=network-online.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/ai_robot/source_robot/server.py
StandardOutput=inherit
StandardInput=inherit
User=pi

[Install]
WantedBy=multi-user.target
```
root@raspberrypi:/etc/wpa_supplicant# less wpa_supplicant.conf 
```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=NL

network={
        ssid="NETGEAR00"
        psk="dynamicviolet293"
}

```


