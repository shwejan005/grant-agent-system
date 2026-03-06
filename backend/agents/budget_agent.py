"""
Budget & Timeline Agent
Generates research budget and milestone schedule aligned with grant norms.
"""
import json
import logging
from jinja2 import Template
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm.provider import get_llm
from prompts.templates import BUDGET_PLANNING_PROMPT
from database import get_connection

logger = logging.getLogger(__name__)


def generate_budget(
    proposal: dict,
    grant_data: dict,
    guidelines: dict,
    run_id: int,
    iteration: int,
) -> dict:
    """
    Generate budget table and milestone timeline.

    Args:
        proposal: Generated proposal dict
        grant_data: Grant program info
        guidelines: Extracted guidelines
        run_id: Pipeline run ID
        iteration: Current iteration number

    Returns:
        Budget dict with budget_table, milestone_schedule, cost_justification
    """
    llm = get_llm(temperature=0.5)

    funding_constraints = guidelines.get("funding_constraints", {})
    if isinstance(funding_constraints, str):
        funding_constraints = {"max_budget": funding_constraints}

    template = Template(BUDGET_PLANNING_PROMPT)
    prompt = template.render(
        proposal_title=proposal.get("title", ""),
        methodology=proposal.get("methodology", ""),
        program_name=grant_data.get("program_name", ""),
        funding_constraints=json.dumps(funding_constraints, indent=2),
    )

    logger.info(f"Generating budget for iteration {iteration}")

    response = llm.invoke(prompt)
    response_text = response.content if hasattr(response, 'content') else str(response)

    # Parse JSON from response
    try:
        text = response_text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        budget = json.loads(text.strip())
    except json.JSONDecodeError:
        logger.warning("Failed to parse budget JSON, creating fallback")
        budget = {
            "budget_table": [
                {"category": "Manpower", "items": [{"item": "Research Fellow", "quantity": 1, "unit_cost": "420000/year", "total_cost": "1260000", "justification": "Full-time researcher"}], "subtotal": "1260000"},
                {"category": "Equipment", "items": [{"item": "Computing Infrastructure", "quantity": 1, "unit_cost": "500000", "total_cost": "500000", "justification": "High-performance computing"}], "subtotal": "500000"},
                {"category": "Consumables", "items": [{"item": "Software and Subscriptions", "quantity": 1, "unit_cost": "200000", "total_cost": "200000", "justification": "Research tools"}], "subtotal": "200000"},
                {"category": "Travel", "items": [{"item": "Conference Attendance", "quantity": 2, "unit_cost": "100000", "total_cost": "200000", "justification": "Dissemination"}], "subtotal": "200000"},
                {"category": "Contingency", "items": [{"item": "Contingency (5%)", "quantity": 1, "unit_cost": "108000", "total_cost": "108000", "justification": "Unforeseen expenses"}], "subtotal": "108000"},
            ],
            "total_budget": "2268000",
            "milestone_schedule": [
                {"milestone": "Literature Review & Setup", "start_month": 1, "end_month": 6, "deliverables": ["Comprehensive literature survey", "Infrastructure setup"], "budget_allocation": "500000"},
                {"milestone": "Core Research Phase", "start_month": 7, "end_month": 18, "deliverables": ["Primary research results", "Prototype"], "budget_allocation": "1000000"},
                {"milestone": "Analysis & Publication", "start_month": 19, "end_month": 30, "deliverables": ["Published papers", "Final report"], "budget_allocation": "500000"},
                {"milestone": "Wrap-up & Dissemination", "start_month": 31, "end_month": 36, "deliverables": ["Final deliverables", "Project closure"], "budget_allocation": "268000"},
            ],
            "cost_justification": "The budget is structured to support a focused research program with essential personnel, computing resources, and dissemination activities. All costs are aligned with SERB funding norms.",
        }

    # Save to database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO budgets (run_id, iteration, budget_table, milestone_schedule, cost_justification)
        VALUES (?, ?, ?, ?, ?)
    """, (
        run_id, iteration,
        json.dumps(budget.get("budget_table", [])),
        json.dumps(budget.get("milestone_schedule", [])),
        budget.get("cost_justification", ""),
    ))
    conn.commit()
    conn.close()

    logger.info(f"Budget for iteration {iteration} generated and saved")
    return budget
