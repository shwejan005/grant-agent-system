"""
Python rule-based scoring engine for proposal evaluation.
Checks structural completeness and formatting compliance.
Max score: 40 points (combined with LLM score of 60 for total 100).
"""


REQUIRED_SECTIONS = [
    "title",
    "abstract",
    "background",
    "objectives",
    "methodology",
    "expected_impact",
    "deliverables",
]

BUDGET_CATEGORIES = [
    "personnel",
    "equipment",
    "travel",
    "software",
    "compute",
    "consumable",
    "contingency",
]

MIN_SECTION_LENGTH = 80  # minimum characters per section


def evaluate_rules(proposal: dict, budget: dict) -> tuple[float, list[str]]:
    """
    Evaluate a proposal using deterministic rule checks.

    Returns:
        (score, list_of_violations)  where score is 0-40.
    """
    score = 0.0
    violations: list[str] = []

    # --- 1. Required sections present (5 pts each, max 35) ---
    for section in REQUIRED_SECTIONS:
        content = proposal.get(section, "").strip()
        if not content:
            violations.append(f"Missing required section: {section}")
        else:
            score += 3  # existence = 3 pts
            if len(content) >= MIN_SECTION_LENGTH:
                score += 2  # substantial content = 2 more pts
            else:
                violations.append(
                    f"Section '{section}' is too short "
                    f"({len(content)} chars, minimum {MIN_SECTION_LENGTH})"
                )

    # Cap section score at 35
    section_score = min(score, 35)

    # --- 2. Budget present and has categories (max 5) ---
    budget_score = 0.0
    budget_table = budget.get("budget_table", "").lower()
    milestone = budget.get("milestone_schedule", "").lower()

    if not budget_table:
        violations.append("Missing budget table")
    else:
        budget_score += 1
        found_categories = sum(
            1 for cat in BUDGET_CATEGORIES if cat in budget_table
        )
        if found_categories >= 3:
            budget_score += 2
        elif found_categories >= 1:
            budget_score += 1
        else:
            violations.append("Budget table lacks standard categories")

    if not milestone:
        violations.append("Missing milestone schedule")
    else:
        budget_score += 2

    budget_score = min(budget_score, 5)

    total = section_score + budget_score
    return round(total, 1), violations
