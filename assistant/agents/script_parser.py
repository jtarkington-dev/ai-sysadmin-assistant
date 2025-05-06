#assistant/agents/script_parser.py

import re

class ScriptParser:
    def __init__(self):
        self.issues = []

    def parse(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except Exception as error:
            return f"Error reading file: {str(error)}"

        self.detect_unsanitized_read(lines)
        self.detect_dangerous_commands(lines)
        self.detect_toctou_patterns(lines)
        self.detect_unsafe_variable_expansion(lines)
        self.detect_path_traversal(lines)
        self.detect_tmpfile_race(lines)
        self.detect_unsafe_path_manipulation(lines) 
        self.detect_eval_from_external_input(lines)
        self.detect_sensitive_logging(lines)
        self.detect_pid_file_race(lines)
        self.detect_infinite_logging_loop(lines)
        self.detect_world_writable_files(lines)
        self.detect_delayed_self_destruct(lines)
        self.detect_background_lock_monitoring(lines)
        self.detect_caching_abuse_patterns(lines)
        self.detect_silent_failures(lines)
        self.detect_pid_masking_logic(lines)


        return self.issues

    def detect_unsanitized_read(self, lines):
        for idx, line in enumerate(lines):
            if "read " in line and not ("-r" in line or "--raw" in line):
                self.issues.append({
                    "severity": "Critical",
                    "type": "unsanitized_input",
                    "line_number": idx + 1,
                    "code": line.strip(),
                    "description": "Unsanitized 'read' input detected (possible command injection)"
                })

    def detect_dangerous_commands(self, lines):
        dangerous_keywords = [
            "rm -rf", "mkfs", "dd if=", "shutdown", "reboot", ":(){", "chmod 777", "chown root"
        ]
        for idx, line in enumerate(lines):
            for keyword in dangerous_keywords:
                if keyword in line:
                    self.issues.append({
                        "severity": "Critical",
                        "type": "dangerous_command",
                        "line_number": idx + 1,
                        "code": line.strip(),
                        "description": f"Dangerous command usage detected: {keyword}"
                    })

    def detect_toctou_patterns(self, lines):
        """
        Detect Time-Of-Check-Time-Of-Use (TOCTOU) vulnerabilities.
        (e.g., check for file existence, then operate without lock.)
        """
        file_checks = []
        for idx, line in enumerate(lines):
            if re.search(r'\[ -e .* \]', line):
                file_checks.append((idx, line.strip()))
            if ">" in line or "cat" in line or "rm " in line or "mv " in line:
                for check_idx, check in file_checks:
                    if idx > check_idx and idx - check_idx < 10:  # within vulnerable window
                        self.issues.append({
                            "severity": "Warning",
                            "type": "toctou_race",
                            "line_number": idx + 1,
                            "code": line.strip(),
                            "description": f"Potential TOCTOU race condition after check at line {check_idx + 1}"
                        })

    def detect_unsafe_variable_expansion(self, lines):
        """
        Detect unquoted variable usage (could lead to word splitting or globbing issues)
        """
        for idx, line in enumerate(lines):
            if "$" in line and '"' not in line and "'" not in line:
                self.issues.append({
                    "severity": "Info",
                    "type": "unsafe_variable_expansion",
                    "line_number": idx + 1,
                    "code": line.strip(),
                    "description": "Unquoted variable expansion detected (potential safety risk)"
                })
                
    def detect_path_traversal(self, lines):
        """
        Detect unsafe archive or file extraction that could allow path traversal.
        Example: tar -xvf "$archive" without path validation.
        """
        risky_extractors = ["tar -x", "tar -xf", "unzip", "cp", "rsync"]
        for idx, line in enumerate(lines):
            for extractor in risky_extractors:
                if extractor in line and "$" in line:
                    self.issues.append({
                        "type": "path_traversal_risk",
                        "line_number": idx + 1,
                        "code": line.strip(),
                        "description": "Potential path traversal vulnerability (user input in extraction/copy operation)"
                    })
                    
    def detect_tmpfile_race(self, lines):
        """
        Detect unsafe usage of temporary files without secure creation or locking.
        Example: using /tmp/ manually without mktemp or secure handling.
        """
        for idx, line in enumerate(lines):
            if "/tmp" in line and ("mktemp" not in line) and ("trap" not in line):
                self.issues.append({
                    "type": "tmpfile_race_risk",
                    "line_number": idx + 1,
                    "code": line.strip(),
                    "description": "Unsafe temp file usage without mktemp or file locking (possible race condition)"
                })
                
    def detect_unsafe_path_manipulation(self, lines):
        """
        Detect unsafe modifications to the PATH variable, especially adding the current directory ('.').
        """
        for idx, line in enumerate(lines):
            if "export PATH=" in line or "PATH=" in line:
                if "." in line.split("=")[-1].split(":")[0]:
                    self.issues.append({
                        "severity": "Critical",
                        "type": "unsafe_path_manipulation",
                        "line_number": idx + 1,
                        "code": line.strip(),
                        "description": "Current directory (.) is prioritized in PATH — potential security risk (PATH poisoning)"
                    })

    def detect_eval_from_external_input(self, lines):
        """
        Detect risky patterns where external or file-sourced input is later passed into eval.
        """
        external_sources = set()
        variable_assignments = {}

        for idx, line in enumerate(lines):
            # Track any variable assignment that reads from external source
            if any(cmd in line for cmd in ["grep", "cat", "awk", "sed", "cut", "tail", "head"]) and "=" in line:
                parts = line.split("=")
                if len(parts) >= 2:
                    var_name = parts[0].strip()
                    external_sources.add(var_name)
                    variable_assignments[var_name] = idx + 1  # Save the line where it was assigned

        for idx, line in enumerate(lines):
            if "eval" in line:
                # See if eval is used with an externally sourced variable
                for var in external_sources:
                    if var in line:
                        self.issues.append({
                            "severity": "Critical",
                            "type": "external_input_to_eval",
                            "line_number": idx + 1,
                            "code": line.strip(),
                            "description": f"External input from variable '{var}' (assigned at line {variable_assignments[var]}) used inside eval — command injection risk."
                        })
                # If no match, still flag any dynamic eval even if variable unknown
                if "$" in line:
                    self.issues.append({
                        "severity": "Warning",
                        "type": "eval_usage",
                        "line_number": idx + 1,
                        "code": line.strip(),
                        "description": "Use of eval detected with dynamic input — possible command injection risk."
                    })

    def detect_sensitive_logging(self, lines):
        """
        Detect unsafe logging of secrets, passwords, or sensitive information.
        """
        for idx, line in enumerate(lines):
            if re.search(r'echo.*SECRET|echo.*PASSWORD|echo.*TOKEN', line, re.IGNORECASE):
                self.issues.append({
                    "severity": "High",
                    "type": "sensitive_info_leak",
                    "line_number": idx + 1,
                    "code": line.strip(),
                    "description": "Sensitive information echoed or logged — potential information leak."
                })

    def detect_pid_file_race(self, lines):
        """
        Detect unsafe PID handling that could lead to race conditions or security issues.
        """
        pid_detected = False
        for idx, line in enumerate(lines):
            if "pid_file=" in line or "/var/run/" in line:
                pid_detected = True
            if pid_detected and ("kill" in line or "rm" in line) and "$old_pid" in line:
                self.issues.append({
                    "severity": "Warning",
                    "type": "pid_file_race_risk",
                    "line_number": idx + 1,
                    "code": line.strip(),
                    "description": "Possible PID reuse race condition — process ID may have changed before action."
                })

    def detect_infinite_logging_loop(self, lines):
        """
        Detect infinite loops that involve continuous writing to logs (potential DoS attack).
        """
        inside_loop = False
        for idx, line in enumerate(lines):
            if "while true" in line:
                inside_loop = True
            if inside_loop and ("echo" in line or ">>" in line):
                self.issues.append({
                    "severity": "Warning",
                    "type": "infinite_logging_risk",
                    "line_number": idx + 1,
                    "code": line.strip(),
                    "description": "Infinite loop detected writing to file — potential denial of service."
                })

    def detect_world_writable_files(self, lines):
        """
        Detect world-writable file permissions set using chmod.
        """
        for idx, line in enumerate(lines):
            if "chmod 666" in line or "chmod a+w" in line:
                self.issues.append({
                    "severity": "Warning",
                    "type": "world_writable_file",
                    "line_number": idx + 1,
                    "code": line.strip(),
                    "description": "World-writable file permissions detected — security risk."
                })

    def detect_delayed_self_destruct(self, lines):
        """
        Detect logic that delays execution of destructive actions like rm -rf
        until after conditional checks, especially from retrieved/cached values.
        """
        cache_used = False
        suspicious_trigger = False
        rm_detected = False
        cache_line = 0
        rm_line = 0

        for idx, line in enumerate(lines):
            if "retrieve_cached_data" in line or "cat" in line and "cache" in line:
                cache_used = True
                cache_line = idx + 1

            if re.search(r'(>|>>)\s*/dev/null', line) and "ping" in line:
                self.issues.append({
                    "severity": "Low",
                    "type": "silent_failure",
                    "line_number": idx + 1,
                    "code": line.strip(),
                    "description": "Silent network check (output fully suppressed) — may obscure critical failures."
                })

            if re.search(r'if.*\|.*grep.*[><=!]', line) or "if" in line and "retrieve_cached_data" in line:
                suspicious_trigger = True

            if "rm -rf" in line and "/" in line and "--no-preserve-root" in line:
                rm_detected = True
                rm_line = idx + 1

        if cache_used and suspicious_trigger and rm_detected:
            self.issues.append({
                "severity": "Critical",
                "type": "delayed_self_destruct",
                "line_number": rm_line,
                "code": lines[rm_line - 1].strip(),
                "description": f"Delayed self-destruct logic detected: `rm -rf` triggered by cached or delayed condition (see cache near line {cache_line})"
            })


    def detect_background_lock_monitoring(self, lines):
        """
        Detect background lock monitoring loops that periodically check for a 'locked' state.
        """
        for idx, line in enumerate(lines):
            if "is_system_locked" in line and "log_message" in lines[idx + 1] and "&" in lines[-1]:
                self.issues.append({
                    "severity": "Medium",
                    "type": "background_lock_monitor",
                    "line_number": idx + 1,
                    "code": line.strip(),
                    "description": "System lock state is being monitored in the background — could be part of hidden control logic."
                })

    def detect_caching_abuse_patterns(self, lines):
        """
        Detect caching patterns where benign-looking cache functions could hide or re-use dangerous output.
        """
        cache_writes = set()
        cache_reads = set()

        for idx, line in enumerate(lines):
            if "cache_data" in line and "(" not in line:  
                cache_writes.add(idx)
            if "retrieve_cached_data" in line:
                cache_reads.add(idx)

        for idx in cache_reads:
            if any(abs(idx - widx) > 5 for widx in cache_writes):  
                self.issues.append({
                    "severity": "High",
                    "type": "abuse_of_cache",
                    "line_number": idx + 1,
                    "code": lines[idx].strip(),
                    "description": "Cached data retrieved far from where it was stored — possible logic obfuscation or delayed execution vector."
                })

    def detect_silent_failures(self, lines):
        """
        Detect commands where output is fully suppressed, possibly masking failures (e.g., ping, curl, wget, systemctl).
        """
        suppressors = ["ping", "curl", "wget", "systemctl", "apt-get", "yum", "dnf"]
        for idx, line in enumerate(lines):
            if any(cmd in line for cmd in suppressors) and ">/dev/null" in line and "2>/dev/null" in line:
                self.issues.append({
                    "severity": "Medium",
                    "type": "silent_failure",
                    "line_number": idx + 1,
                    "code": line.strip(),
                    "description": "Command output and error fully suppressed — failures may go undetected."
                })

    def detect_pid_masking_logic(self, lines):
        """
        Detect logic where PID files are checked and script exits early,
        potentially preventing proper execution or masking stale state.
        """
        found_pid_check = False
        found_early_exit = False
        pid_var = ""

        for idx, line in enumerate(lines):
            # Capture the PID file variable
            if re.search(r'PID_FILE="?[^"]+"?', line):
                match = re.search(r'PID_FILE="?([^"]+)"?', line)
                if match:
                    pid_var = match.group(1)

            # Look for PID check logic
            if "kill -0" in line and "$(" in line and "cat" in line and ".pid" in line:
                found_pid_check = True
                pid_line = idx + 1

            if found_pid_check and ("exit" in line or "return" in line):
                found_early_exit = True
                self.issues.append({
                    "severity": "Warning",
                    "type": "pid_check_masking",
                    "line_number": idx + 1,
                    "code": line.strip(),
                    "description": f"Script exits early if PID exists — may block execution or mask stale PID issues (check near line {pid_line})"
                })
                found_pid_check = False  # Reset to avoid duplicate triggers











                        




