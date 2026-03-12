"""
Proposal Drafting Agent — generates structured research proposals.
"""
from crewai import Agent, Task
from jinja2 import Template
from prompts.prompt_templates import PROPOSAL_DRAFTING_PROMPT


def create_proposal_agent(llm) -> Agent:
    return Agent(
        role="Senior Research Proposal Writer",
        goal="Write a complete, high-quality research grant proposal "
             "with all required sections",
        backstory="You are a distinguished academic researcher with 20 years of "
                  "experience writing successful grant proposals. You have helped "
                  "secure over ₹50 crores in research funding across multiple "
                  "disciplines. You write clearly, precisely, and persuasively.",
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )


def create_proposal_task(
    agent: Agent,
    research_topic: str,
    previous_proposal: str = "",
    critique: str = "",
) -> Task:
    template = Template(PROPOSAL_DRAFTING_PROMPT)
    prompt = template.render(
        research_topic=research_topic,
        previous_proposal=previous_proposal,
        critique=critique,
    )
    return Task(
        description=prompt,
        expected_output=(
            "A complete research proposal with sections: Title, Abstract, "
            "Background/Problem Statement, Objectives, Methodology, "
            "Expected Impact, and Deliverables. Each section must be "
            "substantive and written in professional academic language."
        ),
        agent=agent,
    )


def parse_proposal_output(raw_output: str) -> dict:
    """Parse the raw LLM output into structured proposal sections."""
    sections = {
        "title": "",
        "abstract": "",
        "background": "",
        "objectives": "",
        "methodology": "",
        "expected_impact": "",
        "deliverables": "",
    }

    section_markers = {
        "title": ["# title", "## title", "**title**", "1. title", "1. **title**"],
        "abstract": ["# abstract", "## abstract", "**abstract**", "2. abstract", "2. **abstract**"],
        "background": [
            "# background", "## background", "**background**",
            "# problem statement", "## problem statement",
            "3. background", "3. **background**",
            "# background / problem statement", "## background / problem statement",
        ],
        "objectives": ["# objectives", "## objectives", "**objectives**", "4. objectives", "4. **objectives**"],
        "methodology": ["# methodology", "## methodology", "**methodology**", "5. methodology", "5. **methodology**"],
        "expected_impact": [
            "# expected impact", "## expected impact", "**expected impact**",
            "6. expected impact", "6. **expected impact**",
        ],
        "deliverables": ["# deliverables", "## deliverables", "**deliverables**", "7. deliverables", "7. **deliverables**"],
    }

    lines = raw_output.split("\n")
    current_section = None

    for line in lines:
        line_lower = line.strip().lower().rstrip(":")
        # Remove markdown heading markers for comparison
        clean = line_lower.lstrip("#").strip().lstrip("*").rstrip("*").strip()

        matched = False
        for section_key, markers in section_markers.items():
            for marker in markers:
                marker_clean = marker.lstrip("#").strip().lstrip("*").rstrip("*").strip()
                if clean == marker_clean or line_lower.startswith(marker):
                    current_section = section_key
                    matched = True
                    break
            if matched:
                break

        if not matched and current_section:
            sections[current_section] += line + "\n"

    # Trim whitespace
    for key in sections:
        sections[key] = sections[key].strip()

    # If title is short, also try the first non‑empty line
    if not sections["title"]:
        for line in lines:
            stripped = line.strip().lstrip("#").strip()
            if stripped:
                sections["title"] = stripped
                break

    return sections
