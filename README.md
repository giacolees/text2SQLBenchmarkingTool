# LLM Text-to-SQL Benchmark Tool

A Python-based tool for benchmarking the performance of various Large Language Models (LLMs) on Text-to-SQL tasks using a local SQLite database.

This tool allows you to systematically test different models—both local models via LM Studio and cloud-based models via APIs—against a predefined set of natural language questions and their correct SQL counterparts.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Setup and Installation](#setup-and-installation)
- [Configuration](#configuration)
- [How to Run the Benchmark](#how-to-run-the-benchmark)
- [Extending the Tool](#extending-the-tool)
  - [Adding New Test Cases](#adding-new-test-cases)
  - [Adding New LLMs](#adding-new-llms)
- [License](#license)

## Features

- **Multi-Model Benchmarking**: Test proprietary APIs (OpenAI, Gemini) and local open-source models (via LM Studio) with the same code.
- **Modular Design**: A clean separation of concerns makes the code easy to read, maintain, and extend.
-   - `db_handler.py` for all database interactions.
-   - `llm_connectors.py` for all API calls.
- **Data-Driven Tests**: Test cases are defined in a simple `queries.json` file, allowing you to add new tests without changing any Python code.
- **Result Validation**: Automatically executes the LLM-generated SQL and compares its output against the "ground truth" result.
- **Clear Reporting**: Provides console output detailing the generated SQL, execution status (success/failure), and result correctness for each model and query.

## Project Structure

The project is organized with a clear and scalable structure:

```
llm-sql-benchmark/
├── .gitignore          # Files to be ignored by Git
├── README.md           # This file
├── requirements.txt    # Python dependencies
├── .env                # For storing secret API keys (local only)
├── config.py           # Central configuration for paths and models
│
├── data/
│   └── Biblioteca.db   # The SQLite database
│
├── results/            # Directory for storing output reports
│
├── test_cases/
│   └── queries.json    # Test queries in JSON format
│
└── src/
    ├── __init__.py
    ├── benchmark.py      # Main script to run the benchmark
    ├── db_handler.py     # Handles all database operations
    └── llm_connectors.py # Handles all connections to LLMs
```

## Setup and Installation

Follow these steps to get the project running on your local machine.

**1. Prerequisites**
- Python 3.8+
- Git

**2. Clone the Repository**
```bash
git clone https://github.com/your-username/llm-sql-benchmark.git
cd llm-sql-benchmark
```

**3. Create a Virtual Environment (Recommended)**
This keeps your project dependencies isolated.
- For macOS/Linux:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```- For Windows:
  ```bash
  python -m venv venv
  .\venv\Scripts\activate
  ```

**4. Install Dependencies**
```bash
pip install -r requirements.txt
```

## Configuration

Sensitive information like API keys is managed using a `.env` file.

**1. Create the `.env` file**
Copy the example file to create your own local configuration:
```bash
cp .env.example .env
```
*(You may need to create an `.env.example` file first if it doesn't exist)*

**2. Edit the `.env` file**
Open the `.env` file and add your API keys for the services you want to use. The file is already listed in `.gitignore` to prevent it from being committed to version control.

```
# .env
OPENAI_API_KEY="sk-..."
GEMINI_API_KEY="..."
# Add other keys as needed
```

## How to Run the Benchmark

The main script `src/benchmark.py` orchestrates the entire process.

**1. To Test Local Models (via LM Studio):**
   a. Open the LM Studio application.
   b. Download the models you want to test from the "Search" tab.
   c. Go to the "Local Server" tab (icon: `<->`).
   d. Select a model from the dropdown at the top and wait for it to load.
   e. Click **Start Server**.
   f. Leave the server running.

**2. Run the Python Script**
Open your terminal (with the virtual environment activated) and run:
```bash
python src/benchmark.py
```

The script will loop through all the queries defined in `test_cases/queries.json`, send them to the configured LLMs, execute the returned SQL, and print a detailed report to the console.

## Extending the Tool

The tool is designed to be easily extensible.

### Adding New Test Cases

You can add more questions to the benchmark without modifying any code.

1.  Open the `test_cases/queries.json` file.
2.  Add a new JSON object to the main array. Follow the existing structure:

```json
{
  "id": "a_unique_query_id",
  "difficulty": "A descriptive category",
  "question": "Your new natural language question.",
  "ground_truth_sql": "The 100% correct SQL query that answers the question."
}
```

The benchmark script will automatically pick up the new query on its next run.

### Adding New LLMs

To add support for a new LLM (e.g., Anthropic's Claude):

1.  **Install the necessary library**: `pip install anthropic`
2.  **Add the API key** to your `.env` file (`ANTHROPIC_API_KEY="..."`).
3.  **Create a connector function** in `src/llm_connectors.py`:
    ```python
    # In src/llm_connectors.py
    import anthropic

    def get_sql_from_claude(prompt):
        # Your logic to call the Anthropic API
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        # ...
        return generated_sql
    ```
4.  **Add the new function to the main script** in `src/benchmark.py`:
    ```python
    # In src/benchmark.py
    from .llm_connectors import get_sql_from_gpt, get_sql_from_gemini, get_sql_from_claude

    llms_to_benchmark = {
        "GPT-4": get_sql_from_gpt,
        "Gemini-Pro": get_sql_from_gemini,
        "Claude-3": get_sql_from_claude, # Add the new model here
        "Local Model": get_sql_from_lmstudio
    }
    ```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
