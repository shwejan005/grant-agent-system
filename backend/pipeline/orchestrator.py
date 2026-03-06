"""
Pipeline Orchestrator
Coordinates the closed-loop CrewAI agent workflow:
Scraper → Guideline → Proposal → Budget → Evaluation → Refinement → Repeat
"""
import json
import logging
import time
from typing import Dict, Any, Optional
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_connection
from config import SCORE_THRESHOLD, MAX_ITERATIONS
from scraper.scraper import SERBScraper
from agents.guideline_agent import extract_guidelines
from agents.proposal_agent import generate_proposal
from agents.budget_agent import generate_budget
from agents.evaluation_agent import evaluate_proposal
from agents.refinement_agent import refine_proposal

logger = logging.getLogger(__name__)

# In-memory store for pipeline run status (for real-time polling)
_pipeline_status: Dict[int, Dict[str, Any]] = {}


def get_pipeline_status(run_id: int) -> Optional[Dict[str, Any]]:
    """Get current pipeline status."""
    return _pipeline_status.get(run_id)


def run_pipeline(
    grant_id: int,
    research_topic: str,
    max_iterations: int = None,
    score_threshold: float = None,
) -> Dict[str, Any]:
    """
    Execute the full closed-loop pipeline.

    Args:
        grant_id: ID of the grant program to target
        research_topic: User's research topic
        max_iterations: Override for max iterations
        score_threshold: Override for score threshold

    Returns:
        Final pipeline results dict
    """
    max_iter = max_iterations or MAX_ITERATIONS
    threshold = score_threshold or SCORE_THRESHOLD

    # 1. Create pipeline run record
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pipeline_runs (grant_id, research_topic, max_iterations, status) VALUES (?, ?, ?, 'running')",
        (grant_id, research_topic, max_iter)
    )
    run_id = cursor.lastrowid
    conn.commit()
    conn.close()

    _pipeline_status[run_id] = {
        "run_id": run_id,
        "status": "running",
        "stage": "initializing",
        "iteration": 0,
        "max_iterations": max_iter,
        "scores": [],
        "message": "Pipeline started",
    }

    try:
        # 2. Get grant data
        _update_status(run_id, "fetching_grant", 0, "Loading grant program data...")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM grant_programs WHERE id = ?", (grant_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            raise ValueError(f"Grant program with ID {grant_id} not found")

        grant_data = {
            "program_name": row["program_name"],
            "description": row["description"],
            "eligibility": row["eligibility"],
            "evaluation_criteria": row["evaluation_criteria"],
            "funding_limit": row["funding_limit"],
            "proposal_requirements": row["proposal_requirements"],
            "application_guidelines": row["application_guidelines"],
            "deadlines": row["deadlines"],
        }

        # 3. Extract guidelines
        _update_status(run_id, "extracting_guidelines", 0, "Analyzing grant guidelines...")
        guidelines = extract_guidelines(grant_data, run_id)

        # 4. Iterative loop
        current_proposal = None
        current_budget = None
        current_evaluation = None
        all_iterations = []

        for iteration in range(1, max_iter + 1):
            logger.info(f"=== ITERATION {iteration}/{max_iter} ===")

            # Generate or refine proposal
            if iteration == 1:
                _update_status(run_id, "drafting_proposal", iteration, f"Generating initial proposal (iteration {iteration})...")
                current_proposal = generate_proposal(
                    research_topic, grant_data, guidelines, run_id, iteration
                )
            else:
                _update_status(run_id, "refining_proposal", iteration, f"Refining proposal (iteration {iteration})...")
                refinement = refine_proposal(
                    current_proposal, current_evaluation, run_id, iteration - 1
                )
                current_proposal = refinement["proposal"]

                # Save the refined version as a new proposal iteration
                from agents.proposal_agent import generate_proposal as _save
                conn = get_connection()
                cursor = conn.cursor()
                full_text = "\n\n".join([
                    f"# {current_proposal.get('title', '')}",
                    f"## Abstract\n{current_proposal.get('abstract', '')}",
                    f"## Background\n{current_proposal.get('background', '')}",
                    f"## Objectives\n{current_proposal.get('objectives', '')}",
                    f"## Methodology\n{current_proposal.get('methodology', '')}",
                    f"## Expected Impact\n{current_proposal.get('expected_impact', '')}",
                    f"## Deliverables\n{current_proposal.get('deliverables', '')}",
                ])
                cursor.execute("""
                    INSERT INTO proposals (run_id, iteration, title, abstract, background,
                        objectives, methodology, expected_impact, deliverables, full_text)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    run_id, iteration,
                    current_proposal.get("title", ""),
                    current_proposal.get("abstract", ""),
                    current_proposal.get("background", ""),
                    json.dumps(current_proposal.get("objectives", "")) if isinstance(current_proposal.get("objectives"), list) else current_proposal.get("objectives", ""),
                    current_proposal.get("methodology", ""),
                    current_proposal.get("expected_impact", ""),
                    json.dumps(current_proposal.get("deliverables", "")) if isinstance(current_proposal.get("deliverables"), list) else current_proposal.get("deliverables", ""),
                    full_text,
                ))
                conn.commit()
                conn.close()

            # Generate budget
            _update_status(run_id, "planning_budget", iteration, f"Creating budget & timeline (iteration {iteration})...")
            current_budget = generate_budget(
                current_proposal, grant_data, guidelines, run_id, iteration
            )

            # Evaluate
            _update_status(run_id, "evaluating", iteration, f"Evaluating proposal (iteration {iteration})...")
            current_evaluation = evaluate_proposal(
                current_proposal, current_budget, guidelines, run_id, iteration
            )

            score = current_evaluation.get("total_score", 0)
            _pipeline_status[run_id]["scores"].append(score)

            iteration_data = {
                "iteration": iteration,
                "proposal": current_proposal,
                "budget": current_budget,
                "evaluation": current_evaluation,
                "score": score,
            }
            all_iterations.append(iteration_data)

            logger.info(f"Iteration {iteration} score: {score}/{10} (threshold: {threshold})")

            # Check if threshold reached
            if score >= threshold:
                logger.info(f"Score threshold reached at iteration {iteration}")
                break

        # 5. Complete
        _update_status(run_id, "completed", len(all_iterations), "Pipeline completed!")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE pipeline_runs SET status = 'completed', current_iteration = ?, completed_at = CURRENT_TIMESTAMP WHERE id = ?",
            (len(all_iterations), run_id)
        )
        conn.commit()
        conn.close()

        result = {
            "run_id": run_id,
            "status": "completed",
            "grant_program": grant_data["program_name"],
            "research_topic": research_topic,
            "total_iterations": len(all_iterations),
            "final_score": all_iterations[-1]["score"] if all_iterations else 0,
            "score_history": [it["score"] for it in all_iterations],
            "iterations": all_iterations,
            "guidelines": guidelines,
        }

        _pipeline_status[run_id] = {
            **_pipeline_status[run_id],
            "status": "completed",
            "result": result,
        }

        return result

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        _update_status(run_id, "failed", 0, f"Pipeline failed: {str(e)}")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE pipeline_runs SET status = 'failed' WHERE id = ?",
            (run_id,)
        )
        conn.commit()
        conn.close()

        raise


def _update_status(run_id: int, stage: str, iteration: int, message: str):
    """Update in-memory pipeline status."""
    if run_id in _pipeline_status:
        _pipeline_status[run_id].update({
            "stage": stage,
            "iteration": iteration,
            "message": message,
        })
    logger.info(f"[Run {run_id}] {stage}: {message}")
