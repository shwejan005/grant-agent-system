"""
Evaluation & Scoring Agent
Hybrid scoring: Python rule-based engine + LLM critique.
"""
import json
import logging
from jinja2 import Template
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm.provider import get_llm
from prompts.templates import EVALUATION_CRITIQUE_PROMPT
from database import get_connection

logger = logging.getLogger(__name__)


def _rule_based_evaluation(proposal: dict, budget: dict, guidelines: dict) -> dict:
    """
    Python rule-based scoring engine.
    Checks required sections, guideline compliance, and budget constraints.
    """
    scores = {}
    missing_sections = []

    # Check required sections exist and have content
    required_sections = ["title", "abstract", "background", "objectives",
                         "methodology", "expected_impact", "deliverables"]

    section_score = 0
    for section in required_sections:
        content = proposal.get(section, "")
        if isinstance(content, list):
            content = json.dumps(content)
        if content and len(str(content).strip()) > 20:
            section_score += 1
        else:
            missing_sections.append(section)

    scores["section_completeness"] = {
        "score": round((section_score / len(required_sections)) * 10, 1),
        "max_score": 10.0,
        "feedback": f"Has {section_score}/{len(required_sections)} required sections"
            + (f". Missing: {', '.join(missing_sections)}" if missing_sections else ""),
    }

    # Check abstract length (should be ~250-500 words)
    abstract = str(proposal.get("abstract", ""))
    word_count = len(abstract.split())
    abstract_score = 10.0
    if word_count < 100:
        abstract_score = 4.0
    elif word_count < 200:
        abstract_score = 7.0
    elif word_count > 600:
        abstract_score = 6.0
    scores["abstract_quality"] = {
        "score": abstract_score,
        "max_score": 10.0,
        "feedback": f"Abstract is {word_count} words. Ideal range: 200-500 words.",
    }

    # Check methodology depth
    methodology = str(proposal.get("methodology", ""))
    method_words = len(methodology.split())
    method_score = min(10.0, max(3.0, method_words / 60))
    scores["methodology_depth"] = {
        "score": round(method_score, 1),
        "max_score": 10.0,
        "feedback": f"Methodology is {method_words} words. More detail generally strengthens the proposal.",
    }

    # Check budget compliance
    budget_score = 8.0  # Default reasonable
    budget_table = budget.get("budget_table", [])
    if not budget_table:
        budget_score = 3.0
    total_str = str(budget.get("total_budget", "0"))
    try:
        total_val = float(total_str.replace(",", "").replace("INR", "").strip())
        funding_limit = guidelines.get("funding_constraints", {})
        if isinstance(funding_limit, dict):
            max_budget_str = funding_limit.get("max_budget", "5000000")
        else:
            max_budget_str = "5000000"
        # Extract number from string
        import re
        numbers = re.findall(r'[\d.]+', str(max_budget_str).replace(",", ""))
        if numbers:
            max_val = float(numbers[0])
            # Convert lakhs/crores if mentioned
            if "lakh" in str(max_budget_str).lower():
                max_val *= 100000
            elif "crore" in str(max_budget_str).lower():
                max_val *= 10000000
            if total_val > max_val:
                budget_score = 4.0
        else:
            budget_score = 7.0
    except (ValueError, TypeError):
        budget_score = 6.0

    scores["budget_compliance"] = {
        "score": budget_score,
        "max_score": 10.0,
        "feedback": f"Budget total: {total_str}. Compliance check against funding limits.",
    }

    return {
        "scores": scores,
        "missing_sections": missing_sections,
    }


def evaluate_proposal(
    proposal: dict,
    budget: dict,
    guidelines: dict,
    run_id: int,
    iteration: int,
) -> dict:
    """
    Hybrid evaluation: rule-based + LLM critique.

    Returns:
        Evaluation dict with total_score, rubric_breakdown, critique_report, missing_sections
    """
    logger.info(f"Evaluating proposal iteration {iteration}")

    # 1. Rule-based evaluation
    rule_results = _rule_based_evaluation(proposal, budget, guidelines)

    # 2. LLM critique evaluation
    llm = get_llm(temperature=0.3)

    template = Template(EVALUATION_CRITIQUE_PROMPT)
    prompt = template.render(
        proposal=json.dumps(proposal, indent=2),
        budget=json.dumps(budget, indent=2),
        guidelines=json.dumps(guidelines, indent=2),
    )

    response = llm.invoke(prompt)
    response_text = response.content if hasattr(response, 'content') else str(response)

    try:
        text = response_text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        llm_eval = json.loads(text.strip())
    except json.JSONDecodeError:
        logger.warning("Failed to parse LLM evaluation, using defaults")
        llm_eval = {
            "scores": {
                "relevance_to_funding_call": {"score": 7.0, "max_score": 10.0, "feedback": "Assessment pending"},
                "novelty_of_research": {"score": 6.0, "max_score": 10.0, "feedback": "Assessment pending"},
                "clarity_of_methodology": {"score": 6.5, "max_score": 10.0, "feedback": "Assessment pending"},
                "feasibility": {"score": 7.0, "max_score": 10.0, "feedback": "Assessment pending"},
                "expected_impact": {"score": 6.5, "max_score": 10.0, "feedback": "Assessment pending"},
                "budget_realism": {"score": 7.0, "max_score": 10.0, "feedback": "Assessment pending"},
            },
            "overall_critique": response_text[:500],
            "strengths": ["Proposal addresses the research topic"],
            "weaknesses": ["Could be strengthened with more detail"],
            "missing_elements": [],
            "improvement_suggestions": ["Add more specific methodology details"],
        }

    # 3. Combine scores
    all_scores = {}
    rule_scores = rule_results.get("scores", {})
    llm_scores = llm_eval.get("scores", {})

    # Rule-based scores (40% weight)
    for key, val in rule_scores.items():
        all_scores[f"rule_{key}"] = val

    # LLM scores (60% weight)
    for key, val in llm_scores.items():
        all_scores[f"llm_{key}"] = val

    # Calculate weighted total
    rule_total = sum(v.get("score", 0) for v in rule_scores.values())
    rule_max = sum(v.get("max_score", 10) for v in rule_scores.values())
    llm_total = sum(v.get("score", 0) for v in llm_scores.values())
    llm_max = sum(v.get("max_score", 10) for v in llm_scores.values())

    rule_normalized = (rule_total / rule_max * 10) if rule_max > 0 else 5.0
    llm_normalized = (llm_total / llm_max * 10) if llm_max > 0 else 5.0
    total_score = round(rule_normalized * 0.4 + llm_normalized * 0.6, 2)

    evaluation = {
        "total_score": total_score,
        "rubric_breakdown": all_scores,
        "critique_report": llm_eval.get("overall_critique", ""),
        "strengths": llm_eval.get("strengths", []),
        "weaknesses": llm_eval.get("weaknesses", []),
        "missing_sections": list(set(
            rule_results.get("missing_sections", []) +
            llm_eval.get("missing_elements", [])
        )),
        "improvement_suggestions": llm_eval.get("improvement_suggestions", []),
        "rule_score": round(rule_normalized, 2),
        "llm_score": round(llm_normalized, 2),
    }

    # Save to database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO evaluations (run_id, iteration, total_score, rubric_breakdown,
            critique_report, missing_sections, rule_scores, llm_scores)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        run_id, iteration,
        total_score,
        json.dumps(all_scores),
        llm_eval.get("overall_critique", ""),
        json.dumps(evaluation["missing_sections"]),
        json.dumps(rule_scores),
        json.dumps(llm_scores),
    ))
    conn.commit()
    conn.close()

    logger.info(f"Evaluation complete. Total score: {total_score}/10")
    return evaluation
