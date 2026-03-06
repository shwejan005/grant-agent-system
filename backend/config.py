import os
from pathlib import Path
from dotenv import load_dotenv

# Load env from project root
env_path = Path(__file__).parent.parent / ".env.local"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv(Path(__file__).parent.parent / ".env")

BASE_DIR = Path(__file__).parent
DATABASE_PATH = BASE_DIR / "grant_proposals.db"
SERB_URL = "https://serb.gov.in/page/english/research_grants"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")

SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD", "8.0"))
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "3"))
