#!/bin/bash

# Script that creates a temporary file and writes to it

temp_dir="/tmp"
base_name="my_temp_file"
temp_file="$temp_dir/$base_name"

if [ -e "$temp_file" ]; then
  echo "Warning: Temporary file already exists!"
  exit 1
fi

echo "Writing data to $temp_file..."
echo "Important data" > "$temp_file"

# Simulate some processing time
sleep 5

echo "Data written. Now reading..."
cat "$temp_file"

# Cleanup
rm "$temp_file"