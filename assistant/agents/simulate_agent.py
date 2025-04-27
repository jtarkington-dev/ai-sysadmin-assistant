# assistant/agents/simulate_agent.py

from agent import Agent
from utils.gpt import ask_gpt
import random

class SimulateAgent(Agent):
    def __init__(self):
        super().__init__(name="SimulateAgent", description="Simulates disaster scenarios for recovery practice.")

    def start_simulation(self):
        """
        Start a random disaster simulation.
        """
        scenarios = [
            self.simulate_disk_full,
            self.simulate_network_outage,
            self.simulate_service_crash
        ]
        simulation = random.choice(scenarios)
        return simulation()

    def simulate_disk_full(self):
        return (
            "Simulation: Disk usage has reached 98%.\n"
            "Symptoms: System slowdowns, inability to write new files.\n"
            "Recovery Hint: Identify large files, clean temporary files, move old logs off the system."
        )

    def simulate_network_outage(self):
        return (
            "Simulation: Network connectivity lost.\n"
            "Symptoms: Unable to ping external hosts or resolve DNS.\n"
            "Recovery Hint: Restart networking service, check interfaces, inspect firewall rules."
        )

    def simulate_service_crash(self):
        return (
            "Simulation: Critical service (e.g., web server) has crashed.\n"
            "Symptoms: 502/503 errors, service unavailable warnings.\n"
            "Recovery Hint: Restart the service, check logs for crash reasons, verify config files."
        )
