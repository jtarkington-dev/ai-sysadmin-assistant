from utils.gpt import ask_gpt
from agents.script_parser import ScriptParser
from agent import Agent
import subprocess

class AnalyzeAgent(Agent):
    def __init__(self):
        super().__init__(name="AnalyzeAgent", description="Analyzes scripts, logs, and configurations.")

    def analyze_script(self, target):
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
        explain_with_gpt = True  # <--- TURN ON/OFF GPT EXPLANATIONS

        if explain_with_gpt:
            gpt_explanations = []
            for issue in issues:
                prompt = (
                    f"Explain why this Bash line might be risky:\n\n"
                    f"{issue['code']}\n\n"
                    f"Context: {issue['description']}\n\n"
                    f"Provide a short but detailed security explanation."
                )
                explanation = ask_gpt(prompt)
                if explanation:
                    gpt_explanations.append(f"Explanation for Line {issue['line_number']}:\n{explanation}")
                else:
                    gpt_explanations.append(f"Explanation for Line {issue['line_number']}:\n(No response from AI)")

            report += "\n\n## AI Explanations\n" + "\n\n".join(gpt_explanations)

        # ---- Script Predicted Behavior ----
        predicted_behavior = self.summarize_behavior(target)
        report += f"\n\n## Predicted Behavior\n{predicted_behavior}"

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
        return behavior_summary if behavior_summary else "(No behavior summary generated.)"
