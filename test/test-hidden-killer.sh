#!/bin/bash

# Script to manage and rotate application logs with potential hidden vulnerabilities.

APP_NAME="my_complex_app"
LOG_DIR="/var/log/$APP_NAME"
ARCHIVE_DIR="$LOG_DIR/archive"
MAX_LOG_SIZE=1048576 # 1MB
DATE_FORMAT="+%Y-%m-%d_%H-%M-%S"
CONFIG_FILE="/etc/$APP_NAME/config"

ensure_dirs() {
  mkdir -p "$LOG_DIR" "$ARCHIVE_DIR"
  if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "LOG_LEVEL=INFO" > "$CONFIG_FILE"
    echo "RETENTION_DAYS=7" >> "$CONFIG_FILE"
  fi
}

rotate_logs() {
  local log_file="$1"
  local timestamp=$(date "$DATE_FORMAT")
  local archived_log="$ARCHIVE_DIR/$(basename "$log_file").$timestamp.gz"

  if [[ -s "$log_file" && "$(du -b "$log_file" | awk '{print $1}')" -gt "$MAX_LOG_SIZE" ]]; then
    gzip -c "$log_file" > "$archived_log"
    truncate -s 0 "$log_file"
    echo "$(date) - Log rotated: $log_file to $archived_log" >> "$LOG_DIR/log_manager.log"
  fi
}

apply_config() {
  local log_level=$(grep "^LOG_LEVEL=" "$CONFIG_FILE" | cut -d'=' -f2)
  local retention_days=$(grep "^RETENTION_DAYS=" "$CONFIG_FILE" | cut -d'=' -f2)

  case "$log_level" in
    "DEBUG") set -x ;;
    "TRACE") set -v ;;
  esac

  find "$ARCHIVE_DIR" -type f -name "*.gz" -mtime +"$retention_days" -delete
}

monitor_log() {
  local log_file="$1"
  tail -n 0 -F "$log_file" |
  while IFS= read -r line; do
    process_log_entry "$line"
  done
}

process_log_entry() {
  local entry="$1"
  if [[ "$entry" =~ (ERROR|CRITICAL) ]]; then
    handle_error "$entry"
  elif [[ "$entry" =~ SECRET_(.*)=(.*) ]]; then
    local secret_name="${BASH_REMATCH[1]}"
    local secret_value="${BASH_REMATCH[2]}"
    log_secret "$secret_name" "$secret_value"
  fi
}

handle_error() {
  local error_msg="$1"
  local error_action=$(grep "^ERROR_ACTION=" "$CONFIG_FILE" 2>/dev/null | cut -d'=' -f2)
  if [[ -n "$error_action" ]]; then
    eval "$error_action"
  else
    echo "$(date) - Error detected: $error_msg" >> "$LOG_DIR/error.log"
  fi
}

log_secret() {
  local name="$1"
  local value="$2"
  local log_sensitive=$(grep "^LOG_SENSITIVE=" "$CONFIG_FILE" 2>/dev/null | cut -d'=' -f2)
  if [[ "$log_sensitive" == "true" ]]; then
    echo "$(date) - Sensitive data ($name): $value" >> "$LOG_DIR/sensitive.log"
  fi
}

cleanup_old_pid() {
  local pid_file="/var/run/$APP_NAME.pid"
  if [[ -f "$pid_file" ]]; then
    local old_pid=$(cat "$pid_file")
    if ! kill -0 "$old_pid" 2>/dev/null; then
      rm -f "$pid_file"
      echo "$(date) - Removed stale PID file: $pid_file" >> "$LOG_DIR/log_manager.log"
    fi
  fi
  echo "$$" > "$pid_file"
}

run_app() {
  # Simulate the application logging
  while true; do
    local log_level_app=$(grep "^APP_LOG_LEVEL=" "$CONFIG_FILE" 2>/dev/null | cut -d'=' -f2)
    local message="Application running - $(date)"
    if [[ "$log_level_app" == "DEBUG" ]]; then
      message="[DEBUG] $message - Extra details: $(ps -o comm= -p $$)"
    elif (( RANDOM % 5 == 0 )); then
      message="ERROR: Something unexpected happened - $(date)"
    elif (( RANDOM % 7 == 0 )); then
      message="SECRET_API_KEY=abcdef12345xyz"
    fi
    echo "$message" >> "$LOG_DIR/app.log"
    sleep $((RANDOM % 5 + 1))
  done
}

main() {
  ensure_dirs
  cleanup_old_pid

  if [[ "$1" == "rotate" ]]; then
    rotate_logs "$LOG_DIR/app.log"
  elif [[ "$1" == "config" ]]; then
    apply_config
  elif [[ "$1" == "monitor" ]]; then
    monitor_log "$LOG_DIR/app.log" &
    wait
  elif [[ "$1" == "run" ]]; then
    run_app &
    tail -f "$LOG_DIR/app.log"
  else
    echo "Usage: $0 [rotate|config|monitor|run]"
    exit 1
  fi
}

main "$@"