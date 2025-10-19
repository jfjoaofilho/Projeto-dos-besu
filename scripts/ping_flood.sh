#!/bin/bash
IP_CONTAINER=$(sudo docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' besu-node)
echo "Enviando pacotes ICMP para $IP_CONTAINER"
ping -f -s 1400 $IP_CONTAINER