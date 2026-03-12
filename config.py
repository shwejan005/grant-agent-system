"""
Centralized configuration for the Grant Proposal Agent System.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = "gemini/gemini-2.5-flash"

# --- Pipeline Defaults ---
DEFAULT_MAX_ITERATIONS = 3
SCORE_THRESHOLD = 75  # out of 100

# --- Database ---
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "grant_proposals.db")

# --- Rule Engine Weights ---
RULE_ENGINE_MAX_SCORE = 40   # max points from rule checks
LLM_EVAL_MAX_SCORE = 60     # max points from LLM evaluation
