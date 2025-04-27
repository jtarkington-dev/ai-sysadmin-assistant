# assistant/agent.py

class Agent:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def analyze(self, target):
        raise NotImplementedError("This agent does not implement analyze().")

    def propose_fix(self, target):
        raise NotImplementedError("This agent does not implement propose_fix().")

    def execute_task(self, task):
        raise NotImplementedError("This agent does not implement execute_task().")

    def stabilize(self):
        raise NotImplementedError("This agent does not implement stabilize().")
