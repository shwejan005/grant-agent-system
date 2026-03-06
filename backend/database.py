import sqlite3
from pathlib import Path
from config import DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS grant_programs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        program_name TEXT NOT NULL,
        description TEXT,
        eligibility TEXT,
        evaluation_criteria TEXT,
        funding_limit TEXT,
        proposal_requirements TEXT,
        application_guidelines TEXT,
        deadlines TEXT,
        raw_json TEXT,
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS pipeline_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        grant_id INTEGER NOT NULL,
        research_topic TEXT NOT NULL,
        max_iterations INTEGER DEFAULT 3,
        current_iteration INTEGER DEFAULT 0,
        status TEXT DEFAULT 'pending',
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (grant_id) REFERENCES grant_programs(id)
    );

    CREATE TABLE IF NOT EXISTS guidelines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        eligibility_rules TEXT,
        evaluation_criteria TEXT,
        formatting_requirements TEXT,
        funding_constraints TEXT,
        rubric_weights TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (run_id) REFERENCES pipeline_runs(id)
    );

    CREATE TABLE IF NOT EXISTS proposals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        iteration INTEGER NOT NULL,
        title TEXT,
        abstract TEXT,
        background TEXT,
        objectives TEXT,
        methodology TEXT,
        expected_impact TEXT,
        deliverables TEXT,
        full_text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (run_id) REFERENCES pipeline_runs(id)
    );

    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        iteration INTEGER NOT NULL,
        budget_table TEXT,
        milestone_schedule TEXT,
        cost_justification TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (run_id) REFERENCES pipeline_runs(id)
    );

    CREATE TABLE IF NOT EXISTS evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        iteration INTEGER NOT NULL,
        total_score REAL,
        rubric_breakdown TEXT,
        critique_report TEXT,
        missing_sections TEXT,
        rule_scores TEXT,
        llm_scores TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (run_id) REFERENCES pipeline_runs(id)
    );

    CREATE TABLE IF NOT EXISTS refinements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        iteration INTEGER NOT NULL,
        change_summary TEXT,
        sections_improved TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (run_id) REFERENCES pipeline_runs(id)
    );
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DATABASE_PATH}")
