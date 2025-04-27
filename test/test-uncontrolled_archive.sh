#!/bin/bash

# Script to extract a user-provided archive

if [ -z "$1" ]; then
  echo "Usage: $0 <archive_file>"
  exit 1
fi

archive_file="$1"

if [ ! -f "$archive_file" ]; then
  echo "Error: Archive file not found: $archive_file"
  exit 1
fi

echo "Extracting archive: $archive_file"

tar -xvf "$archive_file"

echo "Extraction complete."