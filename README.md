
# AI SysAdmin Assistant

## Overview

**AI SysAdmin Assistant** is a command-line automation system focused on real-world Linux administration tasks — built to demonstrate **GenAI-enhanced agents, not just chatbot wrappers**.

Unlike typical "chatbot projects," this tool is designed to:

- Analyze system scripts and logs
- Propose automated fixes
- Execute safe, validated tasks
- Stabilize systems during issues
- Simulate incident responses

All actions are agent-driven, with GPT suggestions assisting — not replacing — system logic.

---

## Project Goals

- Replace manual script reviews with real AI-assisted diagnostics
- Allow hands-on system recovery simulations
- Provide fully agent-driven task management (not chat prompts)
- Prepare for real-world sysadmin disaster recovery and stabilization

---

## Core Agents

| Agent | Purpose |
|------|---------|
| **AnalyzeAgent** | Analyze scripts, logs, and configs for issues |
| **FixAgent** | Propose safe repairs and hardening suggestions |
| **ExecuteAgent** | Execute validated tasks after user approval |
| **StabilizeAgent** | Detect and mitigate system failures or errors |
| **SimulateAgent** | Run disaster recovery simulation scenarios |

---

## Setup Instructions

1. **Clone the repository:**
```bash
git clone https://github.com/jtarkington-dev/ai-sysadmin-assistant.git
cd ai-sysadmin-assistant
```

2. **Create and activate a virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create a `.env` file and add your OpenRouter API key:**
```ini
OPENROUTER_API_KEY=your_api_key_here
```

---

## Basic Usage

**Analyze a script:**
```bash
python3 main.py --analyze path/to/script.sh
```

**Validate a script:**
```bash
python3 main.py --validate path/to/script.sh
```

**Propose a fix:**
```bash
python3 main.py --propose-fix path/to/script.sh
```

**Execute an automated task:**
```bash
python3 main.py --execute-task "description of task"
```

**Launch a simulation:**
```bash
python3 main.py --simulate
```

---

## Future Additions

- Fully custom agent creation through CLI
- Real-time error diagnosis agent (auto-send history)
- Extended stabilization scenarios (hardware failure, DDOS, etc)
- GUI dashboard for monitoring agent actions

---

## Author

Built by **Jeremy Tarkington** to showcase **real-world GenAI automation** — where AI assists real command-line workflows, not just conversation.

[GitHub Repository](https://github.com/jtarkington-dev/ai-sysadmin-assistant)
