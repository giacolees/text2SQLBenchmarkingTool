# LLM to SQL Benchmark Suite

A Python framework for evaluating Large Language Models (LLMs) on their ability to generate accurate SQL queries from natural language questions. This tool supports both proprietary APIs (Gemini, OpenRouter) and local models (via LM Studio), providing a detailed accuracy report based on actual query execution results.

## 🚀 Features

*   **Multi-Backend Support**: Connects to OpenAI-compatible endpoints (OpenRouter, LM Studio) and Google Gemini.
*   **Execution-Based Evaluation**: Validates SQL not by string comparison, but by executing the query on a SQLite database and comparing the returned rows against ground truth.
*   **Flexible Grouping**: Run benchmarks on specific subsets of models (e.g., `small`, `opensource`, `proprietary`).
*   **Prompt Engineering**: Supports Zero-shot, Few-shot (1-5 examples), and reasoning toggle options.
*   **Detailed Reporting**: Generates JSON reports with latency metrics, generated SQL, and accuracy scores.

## 📂 Project Structure

```text
├── config.py             # Configuration: Paths, Model Registry, Prompt Templates
├── benchmark.py          # Entry point: Benchmark execution logic
├── db_handler.py         # Database context manager and execution
├── llm_connectors.py     # API client initialization and request handling
├── pyproject.toml        # Project dependencies (uv managed)
├── uv.lock               # Lockfile for reproducible environments
├── data/
│   └── library.db        # The SQLite database used for testing
├── test_cases/
│   └── queries.json      # Questions and expected ground truth results
└── results/              # Output directory for benchmark JSON reports
```

## 🛠️ Installation & Setup

This project uses [uv](https://github.com/astral-sh/uv) for fast dependency management and execution.

1.  **Install uv** (if you haven't already):
    ```bash
    # On macOS/Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # On Windows
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

2.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/llm-sql-benchmark.git
    cd llm-sql-benchmark
    ```

3.  **Sync Dependencies:**
    Initialize the environment and install dependencies defined in `pyproject.toml`:
    ```bash
    uv sync
    ```

4.  **Set up Environment Variables:**
    Create a `.env` file or export your API keys:
    ```bash
    export OPENROUTER_API_KEY="sk-or-..."
    export GEMINI_API_KEY="AIzaSy..."
    # OpenAI key if using standard OpenAI models
    export OPENAI_API_KEY="sk-..."
    ```

5.  **Local Models (LM Studio):**
    If testing local models:
    1.  Open **LM Studio**.
    2.  Load a model (e.g., `Llama-3-8B`).
    3.  Start the **Local Server** on port `1234`.

## 🏃 Usage

You can run the benchmark directly using `uv run`, which automatically handles the virtual environment.

### Basic Command
Run all models defined in the registry:
```bash
uv run benchmark.py --group all
```

### Command Line Arguments

| Argument | Description | Default | Options |
| :--- | :--- | :--- | :--- |
| `--group` | Which set of models to test. | `all` | `small`, `medium`, `large`, `opensource`, `proprietary`, `all` |
| `--prompt_technique` | Strategy for prompting the LLM. | `zero-shot` | `zero-shot`, `1-shot`, `2-shots`, `few-shots` |
| `--system_prompt` | Include the expert system prompt. | `True` | (Flag: omit to disable) |
| `--reasoning` | Enable/Disable reasoning tokens (e.g., `/no_think` for local models). | `True` | (Flag: omit to disable) |

### Examples

**Run only small, open-source models using 2-shot prompting:**
```bash
uv run benchmark.py --group small-opensource --prompt_technique 2-shots
```

**Run proprietary models without reasoning steps:**
```bash
uv run benchmark.py --group proprietary --no-reasoning
```

## ⚙️ Configuration

### Adding New Models
Open `config.py` and add an entry to the `MODEL_REGISTRY` list.

```python
MODEL_REGISTRY = [
    {
        "name": "My-New-Model-7B",       # Friendly name for reports
        "id": "vendor/model-name-v1",    # API Model ID
        "client": "OpenRouter",          # Must match a key in llm_connectors.py
        "tags": ["small", "opensource"]  # For --group filtering
    },
    # ...
]
```

### Adding Test Cases
Open `test_cases/queries.json`. Add a new object to the list. You must include the `question` and the `ground_truth_results` (the rows expected from the DB).

```json
[
  {
    "id": "q_new_01",
    "question": "How many books were published in 2020?",
    "difficulty": "easy",
    "ground_truth_results": [
       {"count": 5}
    ]
  }
]
```

## 📊 Results

Reports are saved to the `results/` directory as JSON files:
`benchmark_{group}_{technique}.json`.

**Example Output:**
```json
{
  "summary": {
    "model_performance": [
      {
        "model_name": "gemini-2.5-flash",
        "average_accuracy": 95.5,
        "queries_completed": 20
      },
      {
        "model_name": "Mistral-7B",
        "average_accuracy": 82.0,
        "queries_completed": 20
      }
    ]
  },
  "detailed_report": [ ... ]
}
```

## ⚖️ License

[MIT License](LICENSE)
