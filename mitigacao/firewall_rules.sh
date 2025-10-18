#!/bin/bash
# Limita 10 conexões por IP na porta 30303
sudo iptables -A INPUT -p tcp --dport 30303 -m connlimit --connlimit-above 10 -j DROP
