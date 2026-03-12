"""
Evaluation & Scoring Agent — evaluates proposals using hybrid scoring.
Combines Python rule-engine scores with Gemini LLM critique.
"""
import re
from crewai import Agent, Task
from jinja2 import Template
from prompts.prompt_templates import EVALUATION_PROMPT
from scoring.rule_engine import evaluate_rules


def create_evaluation_agent(llm) -> Agent:
    return Agent(
        role="Research Grant Evaluation Expert",
        goal="Provide thorough, fair evaluation of research proposals "
             "with detailed scoring and constructive critique",
        backstory="You are a senior member of a national research funding "
                  "review panel. You have evaluated hundreds of grant proposals "
                  "and are known for your fair, detailed, and constructive "
                  "feedback that helps researchers improve their work.",
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )


def create_evaluation_task(
    agent: Agent, proposal_text: str, budget_text: str
) -> Task:
    template = Template(EVALUATION_PROMPT)
    prompt = template.render(
        proposal_text=proposal_text,
        budget_text=budget_text,
    )
    return Task(
        description=prompt,
        expected_output=(
            "Scores for each criterion (out of 10), a detailed critique "
            "report explaining strengths and weaknesses, and a list of "
            "missing or underdeveloped sections."
        ),
        agent=agent,
    )


def parse_evaluation_output(
    raw_output: str, proposal: dict, budget: dict,
    rule_max: float = 40, llm_max: float = 60,
) -> dict:
    """
    Parse LLM evaluation output and combine with rule-engine scores.

    Returns a dict with:
        total_score, rule_score, llm_score, rubric_breakdown,
        critique_report, missing_sections
    """
    # --- Rule engine ---
    rule_score, violations = evaluate_rules(proposal, budget)

    # --- Parse LLM scores ---
    rubric = {}
    criteria_patterns = [
        ("Research Relevance", r"research\s*relevance[:\s]*(\d+)"),
        ("Novelty & Originality", r"novelty\s*[&and]*\s*originality[:\s]*(\d+)"),
        ("Methodology Clarity", r"methodology\s*clarity[:\s]*(\d+)"),
        ("Feasibility", r"feasibility[:\s]*(\d+)"),
        ("Expected Impact", r"expected\s*impact[:\s]*(\d+)"),
        ("Budget Realism", r"budget\s*realism[:\s]*(\d+)"),
    ]

    for name, pattern in criteria_patterns:
        match = re.search(pattern, raw_output, re.IGNORECASE)
        if match:
            rubric[name] = min(int(match.group(1)), 10)
        else:
            rubric[name] = 5  # default

    # LLM score: sum of rubric (max 60) scaled from max 60
    raw_llm = sum(rubric.values())  # max 60
    llm_score = min(raw_llm, llm_max)

    total_score = rule_score + llm_score

    # --- Parse critique ---
    critique_report = ""
    critique_match = re.search(
        r"CRITIQUE[:\s]*(.*?)(?=MISSING_SECTIONS|$)",
        raw_output, re.DOTALL | re.IGNORECASE,
    )
    if critique_match:
        critique_report = critique_match.group(1).strip()

    if not critique_report:
        # Fallback: everything after scores
        lines = raw_output.split("\n")
        in_critique = False
        critique_lines = []
        for line in lines:
            if "critique" in line.lower() or in_critique:
                in_critique = True
                if "missing_section" in line.lower() or "missing section" in line.lower():
                    break
                critique_lines.append(line)
        critique_report = "\n".join(critique_lines).strip()

    # --- Parse missing sections ---
    missing_sections = []
    missing_match = re.search(
        r"MISSING.SECTIONS[:\s]*(.*?)$",
        raw_output, re.DOTALL | re.IGNORECASE,
    )
    if missing_match:
        text = missing_match.group(1).strip()
        if text.lower() != "none":
            for line in text.split("\n"):
                cleaned = line.strip().lstrip("-•*").strip()
                if cleaned and cleaned.lower() != "none":
                    missing_sections.append(cleaned)

    # Add rule violations to missing sections
    missing_sections.extend(violations)

    return {
        "total_score": round(total_score, 1),
        "rule_score": round(rule_score, 1),
        "llm_score": round(llm_score, 1),
        "rubric_breakdown": rubric,
        "critique_report": critique_report,
        "missing_sections": missing_sections,
    }
