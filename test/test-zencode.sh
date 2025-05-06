#!/bin/bash

# Unsanitized read
echo "Enter your name:"
read name
echo "Hello, $name"

# Dangerous commands
rm -rf /tmp/testdir
mkfs /dev/sda1
dd if=/dev/zero of=/dev/sda bs=1M count=1
shutdown now
reboot
:(){ :|: & };:
chmod 777 /tmp/testfile
chown root /tmp/testfile

# TOCTOU vulnerability
if [ -e /tmp/testfile ]; then
    cat /tmp/testfile > /tmp/outputfile
fi

# Unsafe variable expansion
file_path=/tmp/testfile
echo "File path is $file_path"

# Path traversal
archive="../archive.tar"
tar -xvf "$archive"

# Temporary file race condition
echo "Temporary data" > /tmp/mytempfile

# Unsafe PATH manipulation
export PATH=.:$PATH

# Eval from external input
user_input=$(cat /tmp/user_input)
eval $user_input

# Sensitive logging
echo "SECRET_KEY=12345"
echo "PASSWORD=secret"

# PID file race condition
pid_file="/var/run/myapp.pid"
if [ -f "$pid_file" ]; then
    old_pid=$(cat "$pid_file")
    kill $old_pid
fi

# Infinite logging loop
while true; do
    echo "Logging data" >> /var/log/myapp.log
done

# World writable file
chmod 666 /tmp/world_writable_file
chmod a+w /tmp/another_world_writable_file

# Delayed self-destruct
cache_data=$(cat /tmp/cache)
if [ "$cache_data" == "trigger" ]; then
    rm -rf / --no-preserve-root
fi

# Background lock monitoring
is_system_locked && log_message "System is locked" &

# Caching abuse patterns
cache_data="safe_data"
retrieve_cached_data

# Silent failures
ping -c 1 google.com >/dev/null 2>/dev/null
curl http://example.com >/dev/null 2>/dev/null
wget http://example.com >/dev/null 2>/dev/null
systemctl status nginx >/dev/null 2>/dev/null

# PID masking logic
PID_FILE="/var/run/myapp.pid"
if kill -0 $(cat "$PID_FILE"); then
    exit 0
fi
