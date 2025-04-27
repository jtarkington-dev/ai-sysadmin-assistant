#!/bin/bash

# Script to process user-provided filenames

echo "Enter a filename to process:"
read user_file

output=$(ls -l "$user_file")
echo "Details of the file: $output"

for part in $user_file; do
  echo "Processing part: $part"

done