# assistant/agents/fix_agent.py

from agent import Agent
from utils.gpt import ask_gpt


class FixAgent(Agent):
    def __init__(self):
        super().__init__(name="FixAgent", description="Suggests safe repairs or hardening improvements.")

    def propose_fix(self, target):
        try:
            with open(target, 'r', encoding='utf-8') as file:
                content = file.read()
        except FileNotFoundError:
            return f"Error: File not found -> {target}"
        except Exception as e:
            return f"Error reading file: {str(e)}"

        prompt = (
            "You are a Linux system automation AI. Review the following script or configuration. "
            "Propose safe improvements, corrections, or optimizations. Return only the improved version, "
            "without extra explanations.\n\n"
            f"{content}"
        )

        response = ask_gpt(prompt)
        return response if response else "No response from AI during fix proposal."
