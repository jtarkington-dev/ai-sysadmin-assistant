# assistant/main.py

import argparse
from agents.analyze_agent import AnalyzeAgent
from agents.fix_agent import FixAgent
from agents.execute_agent import ExecuteAgent
from agents.stabilize_agent import StabilizeAgent
from agents.simulate_agent import SimulateAgent

def main():
    parser = argparse.ArgumentParser(description="AI SysAdmin Assistant CLI")

    parser.add_argument('--analyze', metavar='SCRIPT', help="Analyze a script or log file")
    parser.add_argument('--gpt', action='store_true', help="(Optional) Use GPT for explanation with --analyze")
    parser.add_argument('--fix', metavar='SCRIPT', help="Propose a fix for a script")
    parser.add_argument('--execute', metavar='TASK', help="Execute a system task")
    parser.add_argument('--stabilize', action='store_true', help="Run stabilization checks")
    parser.add_argument('--simulate', action='store_true', help="Launch a disaster simulation")

    args = parser.parse_args()

    if args.analyze:
        agent = AnalyzeAgent()
        result = agent.analyze_script(args.analyze, use_gpt=args.gpt)
        print(result)

    if args.fix:
        agent = FixAgent()
        result = agent.propose_fix(args.fix)
        print(result)

    if args.execute:
        agent = ExecuteAgent()
        result = agent.execute_task(args.execute)
        print(result)

    if args.stabilize:
        agent = StabilizeAgent()
        result = agent.stabilize_system()
        print(result)

    if args.simulate:
        agent = SimulateAgent()
        result = agent.start_simulation()
        print(result)

if __name__ == "__main__":
    main()
