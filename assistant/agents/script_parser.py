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






                        




