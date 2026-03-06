"""
Refinement Agent
Analyzes evaluation report and improves weak sections of the proposal.
"""
import json
import logging
from jinja2 import Template
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm.provider import get_llm
from prompts.templates import REFINEMENT_PROMPT
from database import get_connection

logger = logging.getLogger(__name__)


def refine_proposal(
    proposal: dict,
    evaluation: dict,
    run_id: int,
    iteration: int,
) -> dict:
    """
    Refine proposal based on evaluation feedback.

    Args:
        proposal: Current proposal dict
        evaluation: Evaluation results dict
        run_id: Pipeline run ID
        iteration: Current iteration number

    Returns:
        Revised proposal dict with change_summary
    """
    llm = get_llm(temperature=0.6)

    weaknesses = evaluation.get("weaknesses", [])
    suggestions = evaluation.get("improvement_suggestions", [])

    template = Template(REFINEMENT_PROMPT)
    prompt = template.render(
        proposal=json.dumps(proposal, indent=2),
        evaluation=json.dumps({
            "total_score": evaluation.get("total_score", 0),
            "critique_report": evaluation.get("critique_report", ""),
            "rubric_breakdown": evaluation.get("rubric_breakdown", {}),
        }, indent=2),
        weaknesses=json.dumps(weaknesses, indent=2),
        suggestions=json.dumps(suggestions, indent=2),
    )

    logger.info(f"Refining proposal (iteration {iteration} → {iteration + 1})")

    response = llm.invoke(prompt)
    response_text = response.content if hasattr(response, 'content') else str(response)

    try:
        text = response_text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        refined = json.loads(text.strip())
    except json.JSONDecodeError:
        logger.warning("Failed to parse refinement JSON, returning original with notes")
        refined = {
            **proposal,
            "change_summary": [{"section": "all", "change": "Refinement parsing failed, manual review needed", "addresses": "N/A"}],
        }

    change_summary = refined.pop("change_summary", [])

    # Save refinement record
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO refinements (run_id, iteration, change_summary, sections_improved)
        VALUES (?, ?, ?, ?)
    """, (
        run_id, iteration,
        json.dumps(change_summary),
        json.dumps([c.get("section", "") for c in change_summary] if isinstance(change_summary, list) else []),
    ))
    conn.commit()
    conn.close()

    logger.info(f"Proposal refined with {len(change_summary) if isinstance(change_summary, list) else 0} changes")
    return {"proposal": refined, "change_summary": change_summary}
