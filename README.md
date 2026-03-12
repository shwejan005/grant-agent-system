# AI Research Grant Proposal Generator & Evaluator

A multi-agent AI system that transforms a simple research topic into a complete, evaluated, and iteratively refined research grant proposal.

## Architecture

- **CrewAI** — Multi-agent orchestration (4 specialized agents)
- **Streamlit** — Clean, minimalist web interface
- **Google Gemini** — LLM backbone
- **SQLite** — Persistent storage for proposals and evaluations

## Agents

| Agent | Role |
|-------|------|
| Proposal Drafting Agent | Generates structured research proposals |
| Budget & Timeline Agent | Creates realistic budgets and milestone schedules |
| Evaluation & Scoring Agent | Hybrid scoring (rule engine + LLM critique) |
| Refinement Agent | Improves proposals based on evaluation feedback |

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up API key
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 3. Run the app
streamlit run app.py
```

## Usage

1. Enter a research topic in the sidebar
2. Set the number of refinement iterations (1-5)
3. Click **Generate Proposal**
4. View results across tabs: Proposal, Budget, Evaluation, Iteration History

## Project Structure

```
app.py                  # Streamlit UI
config.py               # Centralized configuration
agents/
  proposal_agent.py     # Proposal drafting agent
  budget_agent.py       # Budget & timeline agent
  evaluation_agent.py   # Evaluation & scoring agent
  refinement_agent.py   # Refinement agent
crew/
  grant_crew.py         # CrewAI orchestration pipeline
prompts/
  prompt_templates.py   # Jinja2 prompt templates
scoring/
  rule_engine.py        # Rule-based scoring engine
db/
  database.py           # SQLite storage layer
```
