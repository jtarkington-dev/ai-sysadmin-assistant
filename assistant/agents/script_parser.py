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



