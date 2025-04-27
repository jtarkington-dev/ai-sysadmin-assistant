#!/bin/bash

# Backup /etc to /backup/etc
SRC="/etc"
DEST="/backup/etc"

mkdir -p "$DEST"
cp -r "$SRC" "$DEST"

echo "Backup complete." 
