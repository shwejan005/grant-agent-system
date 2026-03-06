"""
Proposal Drafting Agent
Generates structured research proposals aligned with extracted grant guidelines.
"""
import json
import logging
from jinja2 import Template
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm.provider import get_llm
from prompts.templates import PROPOSAL_DRAFTING_PROMPT
from database import get_connection

logger = logging.getLogger(__name__)


def generate_proposal(
    research_topic: str,
    grant_data: dict,
    guidelines: dict,
    run_id: int,
    iteration: int,
) -> dict:
    """
    Generate a structured research proposal.

    Args:
        research_topic: User-provided research topic
        grant_data: Grant program info
        guidelines: Extracted guidelines from Guideline Agent
        run_id: Pipeline run ID
        iteration: Current iteration number

    Returns:
        Proposal dict with title, abstract, background, objectives, methodology, impact, deliverables
    """
    llm = get_llm(temperature=0.7)

    template = Template(PROPOSAL_DRAFTING_PROMPT)
    prompt = template.render(
        research_topic=research_topic,
        program_name=grant_data.get("program_name", ""),
        program_description=grant_data.get("description", ""),
        guidelines=json.dumps(guidelines, indent=2),
    )

    logger.info(f"Generating proposal iteration {iteration} for topic: {research_topic}")

    response = llm.invoke(prompt)
    response_text = response.content if hasattr(response, 'content') else str(response)

    # Parse JSON from response
    try:
        text = response_text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        proposal = json.loads(text.strip())
    except json.JSONDecodeError:
        logger.warning("Failed to parse proposal JSON, creating from raw text")
        proposal = {
            "title": f"Research Proposal: {research_topic}",
            "abstract": response_text[:500],
            "background": response_text[500:1500] if len(response_text) > 500 else "Background section pending.",
            "objectives": "1. Primary research objective\n2. Secondary research objective\n3. Tertiary research objective",
            "methodology": "Detailed methodology pending.",
            "expected_impact": "Impact assessment pending.",
            "deliverables": "Deliverables list pending.",
        }

    # Build full text for storage
    full_text = "\n\n".join([
        f"# {proposal.get('title', '')}",
        f"## Abstract\n{proposal.get('abstract', '')}",
        f"## Background\n{proposal.get('background', '')}",
        f"## Objectives\n{proposal.get('objectives', '')}",
        f"## Methodology\n{proposal.get('methodology', '')}",
        f"## Expected Impact\n{proposal.get('expected_impact', '')}",
        f"## Deliverables\n{proposal.get('deliverables', '')}",
    ])

    # Save to database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO proposals (run_id, iteration, title, abstract, background,
            objectives, methodology, expected_impact, deliverables, full_text)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        run_id, iteration,
        proposal.get("title", ""),
        proposal.get("abstract", ""),
        proposal.get("background", ""),
        json.dumps(proposal.get("objectives", "")) if isinstance(proposal.get("objectives"), list) else proposal.get("objectives", ""),
        proposal.get("methodology", ""),
        proposal.get("expected_impact", ""),
        json.dumps(proposal.get("deliverables", "")) if isinstance(proposal.get("deliverables"), list) else proposal.get("deliverables", ""),
        full_text,
    ))
    conn.commit()
    conn.close()

    logger.info(f"Proposal iteration {iteration} generated and saved")
    return proposal
