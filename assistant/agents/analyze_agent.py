# assistant/agents/analyze_agent.py

from agent import Agent
from utils.gpt import ask_gpt




class AnalyzeAgent(Agent):
    def __init__(self):
        super().__init__(name="AnalyzeAgent", description="Analyzes scripts, logs, and configurations.")

    def analyze(self, target):
        try:
            with open(target, 'r', encoding='utf-8') as file:
                content = file.read()
        except FileNotFoundError:
            return f"Error: File not found -> {target}"
        except Exception as e:
            return f"Error reading file: {str(e)}"

        prompt = (
            "You are a Linux sysadmin AI. Analyze the following content for bugs, inefficiencies, security risks, "
            "or structural problems. Summarize your findings clearly and concisely.\n\n"
            f"{content}"
        )

        response = ask_gpt(prompt)
        return response if response else "No response from AI during analysis."
