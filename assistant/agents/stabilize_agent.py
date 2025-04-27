# assistant/agents/stabilize_agent.py

from agent import Agent
from utils.gpt import ask_gpt


class StabilizeAgent(Agent):
    def __init__(self):
        super().__init__(name="StabilizeAgent", description="Detects system issues and suggests stabilization actions.")

    def detect_issue(self, system_state):
        """
        Analyze provided system state information and identify issues.
        system_state: dict containing simulated or real system metrics
        """
        issues = []

        if system_state.get("disk_usage", 0) > 90:
            issues.append("High disk usage detected. Consider cleaning up unnecessary files.")
        
        if system_state.get("memory_free", 100) < 10:
            issues.append("Low available memory. Investigate memory leaks or heavy processes.")

        if system_state.get("network_status") == "down":
            issues.append("Network connectivity lost. Check cables, services, or firewall settings.")

        if not issues:
            return "No immediate stabilization actions required."

        return "\n".join(issues)

    def suggest_actions(self, detected_issues):
        """
        Propose stabilization actions based on detected issues.
        """
        suggestions = []
        for issue in detected_issues.splitlines():
            if "disk usage" in issue:
                suggestions.append("Run cleanup scripts or move large files to external storage.")
            elif "memory" in issue:
                suggestions.append("Restart memory-intensive services or reboot the server.")
            elif "Network" in issue:
                suggestions.append("Restart network services or check router/firewall configurations.")

        if not suggestions:
            return "No actions to suggest."

        return "\n".join(suggestions)
