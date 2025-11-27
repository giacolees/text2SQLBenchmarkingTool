# config.py
from pathlib import Path

# Project root directory
ROOT_DIR = Path(__file__).parent

# Paths
DB_PATH = ROOT_DIR / "data" / "Biblioteca.db"
QUERIES_PATH = ROOT_DIR / "test_cases" / "queries.json"
RESULTS_DIR = ROOT_DIR / "results"

# Models
LM_STUDIO_URL = "http://localhost:1234/v1"
OPENAI_MODEL = "gpt-4"
