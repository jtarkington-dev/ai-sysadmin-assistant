from agent import Agent
from utils.gpt import ask_gpt

class FixAgent(Agent):
    def __init__(self):
        super().__init__(name="FixAgent", description="Proposes safe fixes for scripts.")

    def propose_fix(self, target):
        try:
            with open(target, 'r', encoding='utf-8') as file:
                content = file.read()
        except FileNotFoundError:
            return f"Error: File not found -> {target}"
        except Exception as e:
            return f"Error reading file: {str(e)}"

        prompt = (
            "You are a Linux sysadmin AI. The following script may have issues or security risks. "
            "Propose a safer, improved version of it. "
            "Respond ONLY with the improved script — no explanations.\n\n"
            f"{content}"
        )

        response = ask_gpt(prompt)
        if response.startswith("```bash"):
            response = response.removeprefix("```bash").strip()
        if response.endswith("```"):
             response = response.removesuffix("```").stri   
        return response if response else "No response from AI during fix suggestion."
 