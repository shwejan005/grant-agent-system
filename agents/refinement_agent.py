"""
Refinement Agent — improves proposals based on evaluation feedback.
"""
from crewai import Agent, Task
from jinja2 import Template
from prompts.prompt_templates import REFINEMENT_PROMPT
from agents.proposal_agent import parse_proposal_output


def create_refinement_agent(llm) -> Agent:
    return Agent(
        role="Research Proposal Improvement Specialist",
        goal="Systematically improve research proposals by addressing "
             "every weakness identified in the evaluation",
        backstory="You are a senior research editor who specializes in "
                  "transforming good proposals into excellent ones. You have "
                  "a keen eye for weak arguments, vague methodology, and "
                  "missed opportunities for impact.",
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )


def create_refinement_task(
    agent: Agent,
    current_proposal: str,
    current_budget: str,
    total_score: float,
    critique_report: str,
    missing_sections: list[str],
    user_feedback: str = "",
) -> Task:
    template = Template(REFINEMENT_PROMPT)
    prompt = template.render(
        current_proposal=current_proposal,
        current_budget=current_budget,
        total_score=total_score,
        critique_report=critique_report,
        missing_sections=", ".join(missing_sections) if missing_sections else "None",
        user_feedback=user_feedback,
    )
    return Task(
        description=prompt,
        expected_output=(
            "An improved version of the research proposal addressing all "
            "weaknesses from the critique. Include all original sections "
            "(Title, Abstract, Background, Objectives, Methodology, "
            "Expected Impact, Deliverables) plus a CHANGE_SUMMARY listing "
            "specific improvements."
        ),
        agent=agent,
    )


def parse_refinement_output(raw_output: str) -> tuple[dict, str]:
    """
    Parse the refinement output into improved proposal + change summary.

    Returns:
        (proposal_dict, change_summary_text)
    """
    change_summary = ""
    proposal_text = raw_output

    # Extract change summary
    lower = raw_output.lower()
    idx = lower.rfind("change_summary")
    if idx == -1:
        idx = lower.rfind("change summary")
    if idx == -1:
        idx = lower.rfind("changes made")

    if idx != -1:
        change_summary = raw_output[idx:].strip()
        proposal_text = raw_output[:idx].strip()

        # Clean heading from change summary
        lines = change_summary.split("\n", 1)
        if len(lines) > 1:
            change_summary = lines[1].strip()

    proposal = parse_proposal_output(proposal_text)

    return proposal, change_summary
