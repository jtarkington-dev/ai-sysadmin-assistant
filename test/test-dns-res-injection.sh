#!/bin/bash

# Script to resolve a hostname provided by the user

echo "Enter a hostname to resolve:"
read hostname

output=$(nslookup "$hostname")

echo "DNS information for $hostname:"
echo "$output"