"""
Pipeline API routes.
"""
import json
import threading
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection
from pipeline.orchestrator import run_pipeline, get_pipeline_status

router = APIRouter()


class PipelineStartRequest(BaseModel):
    grant_id: int
    topic: str
    max_iterations: Optional[int] = 3
    score_threshold: Optional[float] = 8.0


@router.post("/start")
async def start_pipeline(request: PipelineStartRequest):
    """Start the proposal generation pipeline."""
    # Verify grant exists
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM grant_programs WHERE id = ?", (request.grant_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Grant program not found. Run /api/grants/scrape first.")

    # Create a pipeline run and start in background
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pipeline_runs (grant_id, research_topic, max_iterations, status) VALUES (?, ?, ?, 'starting')",
        (request.grant_id, request.topic, request.max_iterations)
    )
    run_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Run pipeline in background thread
    def _run():
        try:
            # Delete the placeholder record since orchestrator creates its own
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM pipeline_runs WHERE id = ?", (run_id,))
            conn.commit()
            conn.close()

            run_pipeline(
                grant_id=request.grant_id,
                research_topic=request.topic,
                max_iterations=request.max_iterations,
                score_threshold=request.score_threshold,
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Pipeline run failed: {e}", exc_info=True)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()

    return {
        "message": "Pipeline started",
        "run_id": run_id,
        "status": "starting",
    }


@router.get("/status/{run_id}")
async def pipeline_status(run_id: int):
    """Get current pipeline status."""
    status = get_pipeline_status(run_id)
    if status:
        return status

    # Check database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pipeline_runs WHERE id = ?", (run_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Pipeline run not found")

    return {
        "run_id": row["id"],
        "status": row["status"],
        "iteration": row["current_iteration"],
        "max_iterations": row["max_iterations"],
    }


@router.get("/results/{run_id}")
async def pipeline_results(run_id: int):
    """Get full pipeline results including all iterations."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get pipeline run
    cursor.execute("SELECT * FROM pipeline_runs WHERE id = ?", (run_id,))
    run = cursor.fetchone()
    if not run:
        conn.close()
        raise HTTPException(status_code=404, detail="Pipeline run not found")

    # Get grant info
    cursor.execute("SELECT * FROM grant_programs WHERE id = ?", (run["grant_id"],))
    grant = cursor.fetchone()

    # Get guidelines
    cursor.execute("SELECT * FROM guidelines WHERE run_id = ?", (run_id,))
    guideline_row = cursor.fetchone()
    guidelines = None
    if guideline_row:
        guidelines = {
            "eligibility_rules": json.loads(guideline_row["eligibility_rules"] or "[]"),
            "evaluation_criteria": json.loads(guideline_row["evaluation_criteria"] or "[]"),
            "formatting_requirements": json.loads(guideline_row["formatting_requirements"] or "[]"),
            "funding_constraints": json.loads(guideline_row["funding_constraints"] or "{}"),
            "rubric_weights": json.loads(guideline_row["rubric_weights"] or "{}"),
        }

    # Get all proposals
    cursor.execute("SELECT * FROM proposals WHERE run_id = ? ORDER BY iteration", (run_id,))
    proposals = []
    for row in cursor.fetchall():
        proposals.append({
            "iteration": row["iteration"],
            "title": row["title"],
            "abstract": row["abstract"],
            "background": row["background"],
            "objectives": row["objectives"],
            "methodology": row["methodology"],
            "expected_impact": row["expected_impact"],
            "deliverables": row["deliverables"],
            "full_text": row["full_text"],
        })

    # Get all budgets
    cursor.execute("SELECT * FROM budgets WHERE run_id = ? ORDER BY iteration", (run_id,))
    budgets = []
    for row in cursor.fetchall():
        budgets.append({
            "iteration": row["iteration"],
            "budget_table": json.loads(row["budget_table"] or "[]"),
            "milestone_schedule": json.loads(row["milestone_schedule"] or "[]"),
            "cost_justification": row["cost_justification"],
        })

    # Get all evaluations
    cursor.execute("SELECT * FROM evaluations WHERE run_id = ? ORDER BY iteration", (run_id,))
    evaluations = []
    for row in cursor.fetchall():
        evaluations.append({
            "iteration": row["iteration"],
            "total_score": row["total_score"],
            "rubric_breakdown": json.loads(row["rubric_breakdown"] or "{}"),
            "critique_report": row["critique_report"],
            "missing_sections": json.loads(row["missing_sections"] or "[]"),
            "rule_scores": json.loads(row["rule_scores"] or "{}"),
            "llm_scores": json.loads(row["llm_scores"] or "{}"),
        })

    # Get all refinements
    cursor.execute("SELECT * FROM refinements WHERE run_id = ? ORDER BY iteration", (run_id,))
    refinements = []
    for row in cursor.fetchall():
        refinements.append({
            "iteration": row["iteration"],
            "change_summary": json.loads(row["change_summary"] or "[]"),
            "sections_improved": json.loads(row["sections_improved"] or "[]"),
        })

    conn.close()

    score_history = [e["total_score"] for e in evaluations]

    return {
        "run_id": run_id,
        "status": run["status"],
        "grant_program": grant["program_name"] if grant else "Unknown",
        "research_topic": run["research_topic"],
        "total_iterations": len(proposals),
        "final_score": score_history[-1] if score_history else 0,
        "score_history": score_history,
        "guidelines": guidelines,
        "iterations": [
            {
                "iteration": i + 1,
                "proposal": proposals[i] if i < len(proposals) else None,
                "budget": budgets[i] if i < len(budgets) else None,
                "evaluation": evaluations[i] if i < len(evaluations) else None,
                "refinement": refinements[i] if i < len(refinements) else None,
            }
            for i in range(len(proposals))
        ],
    }


@router.get("/runs")
async def list_runs():
    """List all pipeline runs."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT pr.*, gp.program_name
        FROM pipeline_runs pr
        LEFT JOIN grant_programs gp ON pr.grant_id = gp.id
        ORDER BY pr.started_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    runs = []
    for row in rows:
        runs.append({
            "run_id": row["id"],
            "grant_program": row["program_name"],
            "research_topic": row["research_topic"],
            "status": row["status"],
            "max_iterations": row["max_iterations"],
            "current_iteration": row["current_iteration"],
            "started_at": row["started_at"],
            "completed_at": row["completed_at"],
        })

    return {"runs": runs, "count": len(runs)}
