#!/bin/bash

# Script to set permissions on a list of files

file_list="$HOME/files_to_chmod.txt"

if [ ! -f "$file_list" ]; then
  echo "Error: File list not found: $file_list"
  exit 1
fi

while IFS= read -r file; do
  if [ -f "$file" ]; then
    echo "Setting executable permission on: $file"
    chmod +x "$file"
  else
    echo "Warning: File not found (skipping): $file"
  fi
done < "$file_list"

echo "Permissions updated."