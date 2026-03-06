"""
Guideline Ingestion Agent
Extracts structured constraints from scraped grant program data.
"""
import json
import logging
from jinja2 import Template
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm.provider import get_llm
from prompts.templates import GUIDELINE_EXTRACTION_PROMPT
from database import get_connection

logger = logging.getLogger(__name__)


def extract_guidelines(grant_data: dict, run_id: int) -> dict:
    """
    Extract structured guidelines from grant program data.

    Args:
        grant_data: Raw grant program information dict
        run_id: Pipeline run ID for persistence

    Returns:
        Structured guidelines dict with eligibility, criteria, etc.
    """
    llm = get_llm(temperature=0.3)

    template = Template(GUIDELINE_EXTRACTION_PROMPT)
    prompt = template.render(grant_data=json.dumps(grant_data, indent=2))

    logger.info(f"Extracting guidelines for: {grant_data.get('program_name', 'Unknown')}")

    response = llm.invoke(prompt)
    response_text = response.content if hasattr(response, 'content') else str(response)

    # Parse JSON from response
    try:
        # Try to find JSON in the response
        text = response_text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]

        guidelines = json.loads(text.strip())
    except json.JSONDecodeError:
        logger.warning("Failed to parse LLM response as JSON, creating structured fallback")
        guidelines = {
            "eligibility_rules": grant_data.get("eligibility", "").split(". "),
            "evaluation_criteria": [
                {"criterion": "Scientific Merit", "weight_percent": 30, "description": "Quality of research idea"},
                {"criterion": "Investigator Competence", "weight_percent": 25, "description": "Track record of PI"},
                {"criterion": "Methodology", "weight_percent": 20, "description": "Feasibility of approach"},
                {"criterion": "Impact", "weight_percent": 15, "description": "Expected significance"},
                {"criterion": "Budget", "weight_percent": 10, "description": "Financial planning"},
            ],
            "formatting_requirements": grant_data.get("proposal_requirements", "").split(", "),
            "funding_constraints": {
                "max_budget": grant_data.get("funding_limit", "Not specified"),
                "duration": "3 years",
                "equipment_limit": "30% of total budget",
                "other_constraints": [],
            },
            "rubric_weights": {
                "scientific_merit": 0.30,
                "investigator_competence": 0.25,
                "methodology": 0.20,
                "impact": 0.15,
                "budget": 0.10,
            },
            "required_sections": [
                "Title", "Abstract", "Background", "Objectives",
                "Methodology", "Expected Impact", "Deliverables"
            ],
            "key_focus_areas": ["Innovation", "Scientific rigor", "Feasibility"],
        }

    # Save to database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO guidelines (run_id, eligibility_rules, evaluation_criteria,
            formatting_requirements, funding_constraints, rubric_weights)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        run_id,
        json.dumps(guidelines.get("eligibility_rules", [])),
        json.dumps(guidelines.get("evaluation_criteria", [])),
        json.dumps(guidelines.get("formatting_requirements", [])),
        json.dumps(guidelines.get("funding_constraints", {})),
        json.dumps(guidelines.get("rubric_weights", {})),
    ))
    conn.commit()
    conn.close()

    logger.info("Guidelines extracted and saved successfully")
    return guidelines
