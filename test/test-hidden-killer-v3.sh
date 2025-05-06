#!/bin/bash


SYSTEM_INFO_DIR="/etc/system_info"
HEALTH_LOG="/var/log/health_monitor.log"
RESOURCE_THRESHOLD_FILE="$SYSTEM_INFO_DIR/.resource_limits"
LOCK_TIMEOUT=300 
PID_FILE="/var/run/healthd.pid"

acquire_exclusive_access() {
  local lock_fd
  exec {lock_fd}>"$PID_FILE".lock
  flock "$lock_fd"
  echo "$$" > "$PID_FILE"
  echo "$lock_fd"
}

release_exclusive_access() {
  local fd="$1"
  flock -u "$fd"
  exec {fd}>&-
  rm -f "$PID_FILE" "$PID_FILE".lock
}

log_health() {
  local message="$1"
  echo "$(date '+%Y-%m-%d %H:%M:%S') - HEALTH: $message" >> "$HEALTH_LOG"
}

get_resource_limit() {
  local resource="$1"
  awk -v res="$resource" '$1 == res {print $2}' "$RESOURCE_THRESHOLD_FILE" 2>/dev/null
}

check_disk_space() {
  local threshold=$(get_resource_limit "DISK_PERCENT_FULL")
  local usage=$(df / | tail -n 1 | awk '{print $5}' | sed 's/%//')
  if [[ -n "$threshold" && "$usage" -gt "$threshold" ]]; then
    log_health "Disk space nearing critical levels ($usage%)."
    trigger_action "low_disk_space"
  fi
}

check_memory_usage() {
  local threshold=$(get_resource_limit "MEMORY_PERCENT_USED")
  local used=$(free | awk '/Mem:/ {print ($3/$2) * 100}')
  if [[ -n "$threshold" && $(printf "%.0f" "$used") -gt "$threshold" ]]; then
    log_health "Memory usage nearing critical levels ($(printf "%.0f" "$used")%)."
    trigger_action "high_memory_usage"
  fi
}

check_cpu_load() {
  local threshold=$(get_resource_limit "CPU_LOAD_AVERAGE")
  local load=$(cat /proc/loadavg | awk '{print $1}')
  if [[ -n "$threshold" && $(echo "$load > $threshold" | bc -l) -eq 1 ]]; then
    log_health "CPU load average exceeding threshold ($load)."
    trigger_action "high_cpu_load"
  fi
}

trigger_action() {
  local event="$1"
  local action=$(awk -v evt="$event" '$1 == "ON_" evt {print $2}' "$SYSTEM_INFO_DIR/.event_actions" 2>/dev/null)
  if [[ -n "$action" ]]; then
 
    local current_minute=$(date +%M)
    local trigger_minute=$((RANDOM % 60))
    if [[ "$current_minute" -eq "$trigger_minute" ]]; then
      eval "$action"
    fi
  fi
}

delayed_cleanup() {
 
  sleep $((RANDOM % 3600 + 3600)) 
  if is_system_locked; then
    log_health "Performing delayed cleanup (potential disruption)."
    find /var/log -type f -name "*.old" -delete
    find /tmp -type f -atime +7 -delete
  fi
}

initialize_config() {
  mkdir -p "$SYSTEM_INFO_DIR"
  if [[ ! -f "$RESOURCE_THRESHOLD_FILE" ]]; then
    echo "DISK_PERCENT_FULL 90" > "$RESOURCE_THRESHOLD_FILE"
    echo "MEMORY_PERCENT_USED 95" >> "$RESOURCE_THRESHOLD_FILE"
    echo "CPU_LOAD_AVERAGE 5.0" >> "$RESOURCE_THRESHOLD_FILE"
  fi
  if [[ ! -f "$SYSTEM_INFO_DIR/.event_actions" ]]; then
    echo "ON_low_disk_space echo 'Warning: Disk space low!' >> /dev/pts/$(who am i | awk '{print $2}')" > "$SYSTEM_INFO_DIR/.event_actions"
    echo "ON_high_memory_usage echo 'Warning: Memory pressure!' >> /dev/pts/$(who am i | awk '{print $2}')" >> "$SYSTEM_INFO_DIR/.event_actions"
    echo "ON_high_cpu_load echo 'Warning: High CPU load!' >> /dev/pts/$(who am i | awk '{print $2}')" >> "$SYSTEM_INFO_DIR/.event_actions"
  fi
  if [[ ! -f "$CRITICAL_FLAG" ]]; then
    unlock_system 
  fi
}

main() {
  initialize_config
  local lock_fd=$(acquire_exclusive_access)

  if [[ -z "$lock_fd" ]]; then
    log_health "Could not acquire exclusive access. Another instance might be running."
    exit 1
  fi

  check_disk_space &
  check_memory_usage &
  check_cpu_load &
  delayed_cleanup & 
  monitor_status &   

  wait

  release_exclusive_access "$lock_fd"
  log_health "Health monitoring завершено."
}

main