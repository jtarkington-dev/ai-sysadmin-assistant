#!/bin/bash

# Script that takes user input and executes it (dangerous!)

echo "Enter a command to execute:"
read user_command

echo "Executing: $user_command"
eval "$user_command"

echo "Command finished."