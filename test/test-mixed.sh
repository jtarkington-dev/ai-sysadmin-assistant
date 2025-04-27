#!/bin/bash
USERDIR="/home/$USER"
cd $USERDIR/Documents
cp -r * /tmp/

if [ $? -eq 0 ]; then
  echo "Files moved"
else
  echo "Failed"
fi 
