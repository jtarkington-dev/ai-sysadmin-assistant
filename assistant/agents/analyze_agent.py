from utils.gpt import ask_gpt
from agents.script_parser import ScriptParser
from agent import Agent
import subprocess

class AnalyzeAgent(Agent):
    def __init__(self):
        super().__init__(name="AnalyzeAgent", description="Analyzes scripts, logs, and configurations.")

    def analyze_script(self, target, use_gpt=False):
        parser = ScriptParser()
        issues = parser.parse(target)

        if not issues:
            return "No critical issues detected by parser."

        findings = []
        for issue in issues:
            finding_text = f"- [{issue['type']}] Line {issue['line_number']}: {issue['description']}\n    Code: {issue['code']}"
            findings.append(finding_text)

        report = "## Critical Findings\n" + "\n\n".join(findings)

        # ---- OPTIONAL: GPT Explanation ----
        if use_gpt:
            combined_prompt = (
                "You are a security auditing assistant. Explain why each of these Bash lines might be risky.\n"
                "Format your response as:\n"
                "Line <line_number>: <explanation>\n\n"
            )

            for issue in issues:
                combined_prompt += (
                    f"Line {issue['line_number']}:\n"
                    f"{issue['code']}\n"
                    f"Context: {issue['description']}\n\n"
                )

            print("[INFO] Sending batched GPT request for all lines...")
            explanation_response = ask_gpt(combined_prompt)

            if explanation_response:
                report += "\n\n## AI Explanations\n" + explanation_response
            else:
                report += "\n\n## AI Explanations\n(No response from AI)"

        return report

    def summarize_behavior(self, target):
        try:
            with open(target, 'r', encoding='utf-8') as file:
                content = file.read()
        except Exception as error:
            return f"Error reading file for behavior summary: {str(error)}"

        prompt = (
            "Summarize what this Bash script is trying to accomplish. "
            "Be objective, list each major action or behavior clearly, without suggesting corrections or improvements.\n\n"
            f"{content}"
        )
        behavior_summary = ask_gpt(prompt)
        if not behavior_summary:
            print("[ERROR] GPT returned no summary.", file=sys.stderr)
            return "(No behavior summary returned.)"
        return behavior_summary


