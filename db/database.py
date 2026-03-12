"""
SQLite database layer for storing proposals, evaluations, and iteration logs.
"""
import sqlite3
import json
import os
from datetime import datetime


def _get_connection(db_path: str) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    conn = _get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proposals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            iteration INTEGER NOT NULL,
            research_topic TEXT NOT NULL,
            title TEXT,
            abstract TEXT,
            background TEXT,
            objectives TEXT,
            methodology TEXT,
            expected_impact TEXT,
            deliverables TEXT,
            budget_table TEXT,
            milestone_schedule TEXT,
            cost_justification TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            iteration INTEGER NOT NULL,
            total_score REAL,
            rule_score REAL,
            llm_score REAL,
            rubric_breakdown TEXT,
            critique_report TEXT,
            missing_sections TEXT,
            change_summary TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS iteration_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            iteration INTEGER NOT NULL,
            event TEXT NOT NULL,
            details TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_proposal(db_path: str, session_id: str, iteration: int,
                   research_topic: str, proposal: dict, budget: dict) -> None:
    conn = _get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO proposals
        (session_id, iteration, research_topic, title, abstract, background,
         objectives, methodology, expected_impact, deliverables,
         budget_table, milestone_schedule, cost_justification, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id, iteration, research_topic,
        proposal.get("title", ""),
        proposal.get("abstract", ""),
        proposal.get("background", ""),
        proposal.get("objectives", ""),
        proposal.get("methodology", ""),
        proposal.get("expected_impact", ""),
        proposal.get("deliverables", ""),
        budget.get("budget_table", ""),
        budget.get("milestone_schedule", ""),
        budget.get("cost_justification", ""),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()


def save_evaluation(db_path: str, session_id: str, iteration: int,
                     evaluation: dict, change_summary: str = "") -> None:
    conn = _get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO evaluations
        (session_id, iteration, total_score, rule_score, llm_score,
         rubric_breakdown, critique_report, missing_sections, change_summary, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id, iteration,
        evaluation.get("total_score", 0),
        evaluation.get("rule_score", 0),
        evaluation.get("llm_score", 0),
        json.dumps(evaluation.get("rubric_breakdown", {})),
        evaluation.get("critique_report", ""),
        json.dumps(evaluation.get("missing_sections", [])),
        change_summary,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()


def save_iteration_log(db_path: str, session_id: str, iteration: int,
                        event: str, details: str = "") -> None:
    conn = _get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO iteration_logs (session_id, iteration, event, details, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (session_id, iteration, event, details, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_proposals(db_path: str, session_id: str) -> list[dict]:
    conn = _get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM proposals WHERE session_id = ? ORDER BY iteration",
        (session_id,)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_evaluations(db_path: str, session_id: str) -> list[dict]:
    conn = _get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM evaluations WHERE session_id = ? ORDER BY iteration",
        (session_id,)
    )
    rows = cursor.fetchall()
    result = []
    for row in rows:
        d = dict(row)
        d["rubric_breakdown"] = json.loads(d.get("rubric_breakdown", "{}"))
        d["missing_sections"] = json.loads(d.get("missing_sections", "[]"))
        result.append(d)
    conn.close()
    return result


def get_iteration_logs(db_path: str, session_id: str) -> list[dict]:
    conn = _get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM iteration_logs WHERE session_id = ? ORDER BY iteration, id",
        (session_id,)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows
