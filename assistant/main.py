# assistant/main.py

import argparse
import sys
import shutil
import subprocess
import pydoc
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

    def print_or_page(text):
        try:
            with open("last_analysis_output.log", "w", encoding="utf-8") as f:
                f.write(text)
            pydoc.pager(text)
        except Exception as e:
            print(f"Paging failed: {e}")
            print(text)


    if args.analyze:
        agent = AnalyzeAgent()
        result = agent.analyze_script(args.analyze, use_gpt=args.gpt)

        if isinstance(result, str):
            print_or_page(result)

        elif isinstance(result, list):
            output_lines = ["## Critical Findings"]
            for issue in result:
                output_lines.append(f"- [{issue['type']}] Line {issue['line_number']}: {issue['description']}")
                output_lines.append(f"    Code: {issue['code']}\n")
            full_output = "\n".join(output_lines)

            if args.gpt and getattr(agent, 'last_behavior', None):
                    with open("debug_behavior_dump.txt", "w", encoding="utf-8") as debug_file:
                        debug_file.write(repr(agent.last_behavior))
                    full_output += "\n\n## Predicted Behavior\n" + agent.last_behavior.strip()

            print_or_page(full_output)
        else:
            print("Unexpected result format.")





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
