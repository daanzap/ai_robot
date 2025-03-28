#!/bin/bash
echo "make sure no other vpn is running"
sudo openvpn --config client.conf --ifconfig 192.168.111.124 255.255.255.0 --data-ciphers-fallback 'AES-128-CBC' --route-gateway 192.168.111.1

