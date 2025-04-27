#!/bin/bash

# Script to rotate a log file

log_file="/var/log/myapp.log"
backup_dir="/var/log/backup"
date_suffix=$(date +%Y%m%d%H%M%S)

if [ ! -d "$backup_dir" ]; then
  mkdir -p "$backup_dir"
fi

mv "$log_file" "$backup_dir/$log_file.$date_suffix"

echo "Log file rotated."