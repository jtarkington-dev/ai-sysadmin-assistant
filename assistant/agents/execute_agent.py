# assistant/agents/execute_agent.py

import subprocess
from agent import Agent
from utils.gpt import ask_gpt


class ExecuteAgent(Agent):
    def __init__(self):
        super().__init__(name="ExecuteAgent", description="Safely executes system tasks after confirmation.")

    def execute_command(self, command):
        if not isinstance(command, list):
            return "Error: Command must be a list of arguments."

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"Command failed with error:\n{e.stderr.strip()}"
        except Exception as e:
            return f"Unexpected error during execution:\n{str(e)}"
