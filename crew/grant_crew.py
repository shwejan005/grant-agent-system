"""
CrewAI orchestration — runs the closed-loop proposal generation pipeline.

Flow:
  Proposal Drafting → Budget & Timeline → Evaluation → Refinement → repeat
"""
import uuid
import os
import io
import contextlib
from crewai import Crew

from agents.proposal_agent import (
    create_proposal_agent, create_proposal_task, parse_proposal_output,
)
from agents.budget_agent import (
    create_budget_agent, create_budget_task, parse_budget_output,
)
from agents.evaluation_agent import (
    create_evaluation_agent, create_evaluation_task, parse_evaluation_output,
)
from agents.refinement_agent import (
    create_refinement_agent, create_refinement_task, parse_refinement_output,
)
from db.database import (
    init_db, save_proposal, save_evaluation, save_iteration_log,
)
from config import DB_PATH, SCORE_THRESHOLD, MODEL_NAME, GEMINI_API_KEY


def _format_proposal_text(proposal: dict) -> str:
    """Combine proposal sections into readable text."""
    parts = []
    for key in ["title", "abstract", "background", "objectives",
                 "methodology", "expected_impact", "deliverables"]:
        value = proposal.get(key, "")
        if value:
            heading = key.replace("_", " ").title()
            parts.append(f"## {heading}\n{value}")
    return "\n\n".join(parts)


def _format_budget_text(budget: dict) -> str:
    """Combine budget sections into readable text."""
    parts = []
    for key in ["budget_table", "milestone_schedule", "cost_justification"]:
        value = budget.get(key, "")
        if value:
            heading = key.replace("_", " ").title()
            parts.append(f"### {heading}\n{value}")
    return "\n\n".join(parts)


def run_grant_crew(
    research_topic: str,
    max_iterations: int = 3,
    score_threshold: float = None,
    progress_callback=None,
    verbose: bool = False,
):
    """
    Execute the full grant proposal generation pipeline.

    Args:
        research_topic: The research topic/idea from the user.
        max_iterations: Maximum refinement iterations.
        score_threshold: Score at which to stop iterating.
        progress_callback: Optional callable(message: str) for progress updates.

    Returns:
        dict with keys: session_id, iterations (list of iteration data)
    """
    if score_threshold is None:
        score_threshold = SCORE_THRESHOLD

    # Set API key for CrewAI's LiteLLM integration
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

    session_id = str(uuid.uuid4())[:8]
    init_db(DB_PATH)

    llm = MODEL_NAME

    # Create agents
    proposal_agent = create_proposal_agent(llm)
    budget_agent = create_budget_agent(llm)
    evaluation_agent = create_evaluation_agent(llm)
    refinement_agent = create_refinement_agent(llm)

    iterations = []
    current_proposal = {}
    current_budget = {}
    previous_proposal_text = ""
    previous_critique = ""

    def _log(msg):
        if progress_callback:
            progress_callback(msg)

    def _run_crew(agents, tasks):
        """Run a crew, optionally capturing verbose output."""
        crew = Crew(agents=agents, tasks=tasks, verbose=verbose)
        if verbose:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                result = crew.kickoff()
            return result, buf.getvalue()
        else:
            result = crew.kickoff()
            return result, ""

    for iteration in range(1, max_iterations + 1):
        _log(f"**Iteration {iteration}/{max_iterations}** — Starting...")

        # ---- Step 1: Proposal Drafting ----
        if iteration == 1:
            _log("📝 Agent 1: Drafting initial proposal...")
            task = create_proposal_task(
                proposal_agent, research_topic
            )
        else:
            _log("📝 Agent 1: Redrafting proposal with feedback...")
            task = create_proposal_task(
                proposal_agent, research_topic,
                previous_proposal=previous_proposal_text,
                critique=previous_critique,
            )

        result, log_proposal = _run_crew([proposal_agent], [task])
        raw_proposal = str(result)
        current_proposal = parse_proposal_output(raw_proposal)
        proposal_text = _format_proposal_text(current_proposal)

        save_iteration_log(DB_PATH, session_id, iteration,
                           "proposal_drafted", current_proposal.get("title", ""))

        # ---- Step 2: Budget & Timeline ----
        _log("💰 Agent 2: Creating budget and timeline...")
        budget_task = create_budget_task(
            budget_agent, research_topic, proposal_text[:2000]
        )
        result, log_budget = _run_crew([budget_agent], [budget_task])
        raw_budget = str(result)
        current_budget = parse_budget_output(raw_budget)
        budget_text = _format_budget_text(current_budget)

        save_proposal(DB_PATH, session_id, iteration,
                      research_topic, current_proposal, current_budget)
        save_iteration_log(DB_PATH, session_id, iteration,
                           "budget_created", "Budget and timeline generated")

        # ---- Step 3: Evaluation ----
        _log("🔍 Agent 3: Evaluating proposal quality...")
        eval_task = create_evaluation_task(
            evaluation_agent, proposal_text, budget_text
        )
        result, log_eval = _run_crew([evaluation_agent], [eval_task])
        raw_eval = str(result)
        evaluation = parse_evaluation_output(
            raw_eval, current_proposal, current_budget
        )

        save_evaluation(DB_PATH, session_id, iteration, evaluation)
        save_iteration_log(DB_PATH, session_id, iteration,
                           "evaluation_completed",
                           f"Score: {evaluation['total_score']}/100")

        _log(f"📊 Score: **{evaluation['total_score']}/100**")

        iteration_data = {
            "iteration": iteration,
            "proposal": current_proposal.copy(),
            "budget": current_budget.copy(),
            "evaluation": evaluation.copy(),
            "change_summary": "",
            "agent_logs": {
                "Proposal Drafting Agent": log_proposal,
                "Budget & Timeline Agent": log_budget,
                "Evaluation Agent": log_eval,
                "Refinement Agent": "",
            },
        }

        # ---- Step 4: Check if we should continue ----
        if evaluation["total_score"] >= score_threshold:
            _log(f"✅ Score {evaluation['total_score']} meets threshold "
                 f"{score_threshold}.")

        if iteration >= max_iterations:
            _log(f"⏹ Completed all {max_iterations} iteration(s).")
            iterations.append(iteration_data)
            break

        # ---- Step 5: Refinement ----
        _log("🔧 Agent 4: Refining proposal based on feedback...")
        refine_task = create_refinement_task(
            refinement_agent,
            current_proposal=proposal_text,
            current_budget=budget_text,
            total_score=evaluation["total_score"],
            critique_report=evaluation["critique_report"],
            missing_sections=evaluation["missing_sections"],
        )
        result, log_refine = _run_crew([refinement_agent], [refine_task])
        raw_refined = str(result)
        refined_proposal, change_summary = parse_refinement_output(raw_refined)

        # Update state for next iteration
        current_proposal = refined_proposal
        previous_proposal_text = _format_proposal_text(current_proposal)
        previous_critique = evaluation["critique_report"]

        iteration_data["change_summary"] = change_summary
        iteration_data["agent_logs"]["Refinement Agent"] = log_refine
        save_evaluation(DB_PATH, session_id, iteration, evaluation, change_summary)
        save_iteration_log(DB_PATH, session_id, iteration,
                           "refinement_completed", change_summary[:500])

        iterations.append(iteration_data)
        _log(f"🔄 Iteration {iteration} complete. Moving to next round.\n")

    return {
        "session_id": session_id,
        "research_topic": research_topic,
        "iterations": iterations,
    }

def run_user_refinement_cycle(
    session_id: str,
    research_topic: str,
    current_proposal: dict,
    current_budget: dict,
    evaluation: dict,
    user_feedback: str,
    iteration: int,
    progress_callback=None,
    verbose: bool = False,
):
    """Run a single iteration driven by specific user feedback."""
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
    llm = MODEL_NAME
    
    def _log(msg):
        if progress_callback:
            progress_callback(msg)

    # 1. Refinement
    _log(f"🔧 Agent 4: Refining proposal based on user feedback...")
    refinement_agent = create_refinement_agent(llm)
    refine_task = create_refinement_task(
        refinement_agent,
        current_proposal=_format_proposal_text(current_proposal),
        current_budget=_format_budget_text(current_budget),
        total_score=evaluation["total_score"],
        critique_report=evaluation["critique_report"],
        missing_sections=evaluation["missing_sections"],
        user_feedback=user_feedback
    )
    crew = Crew(agents=[refinement_agent], tasks=[refine_task], verbose=verbose)
    if verbose:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            result = crew.kickoff()
        log_refine = buf.getvalue()
    else:
        result = crew.kickoff()
        log_refine = ""
    raw_refined = str(result)
    refined_proposal, change_summary = parse_refinement_output(raw_refined)
    
    save_proposal(DB_PATH, session_id, iteration, research_topic, refined_proposal, current_budget)
    save_iteration_log(DB_PATH, session_id, iteration, "user_refinement_completed", change_summary[:500])
    
    # 2. Re-evaluate
    _log("🔍 Agent 3: Evaluating refined proposal...")
    evaluation_agent = create_evaluation_agent(llm)
    eval_task = create_evaluation_task(
        evaluation_agent, 
        _format_proposal_text(refined_proposal), 
        _format_budget_text(current_budget)
    )
    crew = Crew(agents=[evaluation_agent], tasks=[eval_task], verbose=verbose)
    if verbose:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            result = crew.kickoff()
        log_eval = buf.getvalue()
    else:
        result = crew.kickoff()
        log_eval = ""
    new_evaluation = parse_evaluation_output(str(result), refined_proposal, current_budget)
    
    save_evaluation(DB_PATH, session_id, iteration, new_evaluation, change_summary)
    save_iteration_log(DB_PATH, session_id, iteration, "evaluation_completed", f"Score: {new_evaluation['total_score']}/100")
    
    _log(f"✅ Refinement complete. New Score: {new_evaluation['total_score']}/100")
    
    return {
        "iteration": iteration,
        "proposal": refined_proposal,
        "budget": current_budget,
        "evaluation": new_evaluation,
        "change_summary": change_summary,
        "agent_logs": {
            "Refinement Agent": log_refine,
            "Evaluation Agent": log_eval,
        },
    }
