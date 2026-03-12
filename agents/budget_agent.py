"""
Budget & Timeline Agent — creates project budgets and milestone schedules.
"""
from crewai import Agent, Task
from jinja2 import Template
from prompts.prompt_templates import BUDGET_TIMELINE_PROMPT


def create_budget_agent(llm) -> Agent:
    return Agent(
        role="Research Project Financial Planner",
        goal="Create detailed, realistic research budgets and milestone timelines",
        backstory="You are an experienced research project manager who has "
                  "planned budgets for over 100 funded research projects. "
                  "You understand academic funding norms, equipment costs, "
                  "personnel hiring, and research timelines.",
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )


def create_budget_task(agent: Agent, research_topic: str, proposal_summary: str) -> Task:
    template = Template(BUDGET_TIMELINE_PROMPT)
    prompt = template.render(
        research_topic=research_topic,
        proposal_summary=proposal_summary,
    )
    return Task(
        description=prompt,
        expected_output=(
            "A detailed budget table with categories (Personnel, Equipment, "
            "Consumables, Travel, Software/Compute, Contingency) and year-wise "
            "breakdown in INR. A quarterly milestone schedule over 3 years. "
            "Cost justifications for each major category."
        ),
        agent=agent,
    )


def parse_budget_output(raw_output: str) -> dict:
    """Parse the budget agent output into structured components."""
    budget = {
        "budget_table": "",
        "milestone_schedule": "",
        "cost_justification": "",
    }

    lines = raw_output.split("\n")
    current_section = None

    budget_markers = ["budget table", "budget breakdown", "budget"]
    milestone_markers = ["milestone schedule", "milestone timeline", "milestone", "timeline"]
    justification_markers = ["cost justification", "justification", "budget justification"]

    for line in lines:
        line_lower = line.strip().lower().rstrip(":")
        clean = line_lower.lstrip("#").strip().lstrip("*").rstrip("*").strip()

        if any(clean == m or clean.startswith(m) for m in justification_markers):
            current_section = "cost_justification"
            continue
        elif any(clean == m or clean.startswith(m) for m in milestone_markers):
            current_section = "milestone_schedule"
            continue
        elif any(clean == m or clean.startswith(m) for m in budget_markers):
            current_section = "budget_table"
            continue

        if current_section:
            budget[current_section] += line + "\n"

    for key in budget:
        budget[key] = budget[key].strip()

    # Fallback: if nothing was parsed, put everything in budget_table
    if not any(budget.values()):
        budget["budget_table"] = raw_output.strip()

    return budget
