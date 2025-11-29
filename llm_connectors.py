"""
Module for handling connections and API calls to various Large Language Models.

Each function in this module is designed to take a prompt string as input
and return a generated SQL query string. It centralizes all API-specific logic,
including client initialization, request formatting, and error handling.
"""
import os
import openai
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GOOGLEAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# --- Client Initialization ---
# This dictionary holds all our pre-configured clients.
# It makes it easy to add new clients in one place.

clients = {}

if OPENAI_API_KEY:
    clients["OpenAI"] = openai.OpenAI(api_key=OPENAI_API_KEY)

if GEMINI_API_KEY:
    # Using the new OpenAI-compatible endpoint for Gemini
    clients["Gemini"] = openai.OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=GEMINI_API_KEY
    )

if OPENROUTER_API_KEY:
    clients["OpenRouter"] = openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY
    )

# The LM Studio client requires no API key.
clients["LM Studio"] = openai.OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="not-needed"
)

def get_sql_from_ai(prompt: str, sys_prompt: str, model: str, client_name: str) -> str:
    """
    Generates a SQL query from any pre-configured OpenAI-compatible client.

    Args:
        prompt (str): The user's natural language question.
        model (str): The model identifier to use (e.g., 'gpt-4-turbo', 'gemini/gemini-1.5-flash-latest').
        client_name (str): The key for the client in the `clients` dictionary.

    Returns:
        The generated SQL query as a string, or an error message.
    """
    if client_name not in clients:
        return f"Error: Client '{client_name}' is not configured or its API key is missing."

    client = clients[client_name]
    
    # OpenRouter requires special headers
    extra_headers = {}
    if client_name == "OpenRouter":
        extra_headers = {
            "HTTP-Referer": "http://localhost",
            "X-Title": "LLM SQL Benchmark"
        }

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            stream=False,
            extra_headers=extra_headers,
            timeout=40,
        )
        sql_query = completion.choices[0].message.content

        # Clean up potential code block markers
        if sql_query and sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query and sql_query.endswith("```"):
            sql_query = sql_query[:-3]
        return sql_query.strip()

    except openai.APIConnectionError as e:
        return f"Error: Could not connect to {client_name}. Is the server/service running? Details: {e}"
    except openai.AuthenticationError:
        return f"Error: Authentication failed for {client_name}. Check your API key."
    except openai.NotFoundError:
        return f"Error: Model '{model}' not found for client {client_name} or you lack access."
    except Exception as e:
        return f"Error: An unexpected error occurred with {client_name}: {e}"