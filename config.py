# config.py
import os
from pathlib import Path

# ==========================================
# PATHS & DIRECTORIES
# ==========================================
# Project root directory
ROOT_DIR = Path(__file__).resolve().parent

# Paths
DB_PATH = ROOT_DIR / "data" / "library.db"
QUERIES_PATH = ROOT_DIR / "test_cases" / "queries.json"
RESULTS_DIR = ROOT_DIR / "results"

# ==========================================
# MODEL REGISTRY
# ==========================================
# "id": The string passed to the API (OpenRouter/LM Studio/Gemini)
# "name": Friendly name for reports/logs
# "client": Must match keys in your llm_connectors.clients dict
# "tags": Used for grouping (size, license, specific collections)

MODEL_REGISTRY = [
    # --- SMALL MODELS ---
    {"name": "lfm2-1.2b", "id": "liquid/lfm2-1.2b", "client": "LM Studio", "tags": ["small", "opensource", "LM-Studio-Local"]},
    {"name": "qwen3-4b-2507", "id": "qwen/qwen3-4b-2507", "client": "LM Studio", "tags": ["small", "opensource", "LM-Studio-Local"]},
    {"name": "phi-4-mini", "id": "microsoft/phi-4-mini", "client": "LM Studio", "tags": ["small", "opensource", "LM-Studio-Local"]},
    {"name": "gemma-3n-4b", "id": "google/gemma-3n-4b", "client": "LM Studio", "tags": ["small", "opensource", "LM-Studio-Local"]},
    {"name": "olmo-3-7b", "id": "allenai/olmo-3-7b", "client": "LM Studio", "tags": ["small", "opensource", "LM-Studio-Local"]},
    {"name": "granite-4-h-tiny", "id": "ibm/granite-4-h-tiny", "client": "LM Studio", "tags": ["small", "opensource", "LM-Studio-Local"]},
    {"name": "Mistral-7B", "id": "mistralai/mistral-7b-instruct:free", "client": "OpenRouter", "tags": ["small", "opensource", "OR-Mistral-7B"]},
    {"name": "nemotron-nano-9b-v2", "id": "nvidia/nemotron-nano-9b-v2:free", "client": "OpenRouter", "tags": ["small", "opensource"]},

    # --- MEDIUM MODELS ---
    {"name": "gemini-2.5-flash-lite", "id": "gemini-2.5-flash-lite", "client": "Gemini", "tags": ["medium", "proprietary", "Gemini-1.5-Flash"]},
    {"name": "gemma-3-27b-it", "id": "google/gemma-3-27b-it:free", "client": "OpenRouter", "tags": ["medium", "opensource"]},
    {"name": "llama-3.3-70b-instruct", "id": "meta-llama/llama-3.3-70b-instruct:free", "client": "OpenRouter", "tags": ["medium", "opensource", "OR-Llama3-8B"]},

    # --- LARGE MODELS ---
    {"name": "gemini-2.5-flash", "id": "gemini-2.5-flash", "client": "Gemini", "tags": ["large", "proprietary"]},
    {"name": "kat-coder-pro", "id": "kwaipilot/kat-coder-pro:free", "client": "OpenRouter", "tags": ["large", "proprietary"]},
    {"name": "grok-4.1-fast", "id": "x-ai/grok-4.1-fast:free", "client": "OpenRouter", "tags": ["large", "proprietary"]},
]

# Valid groups for argparse
VALID_GROUPS = ["all", "small", "medium", "large", "opensource", "proprietary"]

# ==========================================
# PROMPT TEMPLATES
# ==========================================
FEW_SHOT_EXAMPLES = {
    "1-shot": (
        "Example:\nQ: List all book titles.\nA: SELECT title FROM BOOK;\n\n"
    ),
    "2-shots": (
        "Example 1:\nQ: List all book titles.\nA: SELECT title FROM BOOK;\n\n"
        "Example 2:\nQ: Find the names of all authors.\nA: SELECT name, surname FROM AUTHOR;\n\n"
    ),
    "few-shots": (
        "Example 1:\nQ: List all book titles.\nA: SELECT title FROM BOOK;\n\n"
        "Example 2:\nQ: Find the names of all authors.\nA: SELECT name, surname FROM AUTHOR;\n\n"
        "Example 3:\nQ: How many books are there?\nA: SELECT COUNT(*) FROM BOOK;\n\n"
        "Example 4:\nQ: What are the names of readers who have borrowed books?\n"
        "A: SELECT DISTINCT R.name, R.surname FROM READER R JOIN BOOK_LOAN BL ON R.reader_id = BL.reader_id;\n\n"
        "Example 5:\nQ: List all publishers located in 'New York'.\nA: SELECT name FROM PUBLISHER WHERE city = 'New York';\n\n"
    )
}