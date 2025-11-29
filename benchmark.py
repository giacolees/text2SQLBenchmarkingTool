import argparse
import json
import time
import sys
import os
from functools import partial
from datetime import datetime
from pathlib import Path

# Custom Modules
from llm_connectors import get_sql_from_ai, clients
from db_handler import DBHandler
from config import (
    DB_PATH, 
    QUERIES_PATH, 
    RESULTS_DIR, 
    MODEL_REGISTRY, 
    VALID_GROUPS, 
    FEW_SHOT_EXAMPLES
)

# ==========================================
# HELPER: PROMPT BUILDER
# ==========================================
def build_system_prompt(schema: str, use_prompt: bool, reasoning: bool, technique: str) -> str:
    """Combines schema, instructions, and few-shot examples into one string."""
    prompt = ""
    
    # 1. Handle Reasoning Models (e.g., DeepSeek/O1 style)
    if not reasoning:
        prompt += "/no_think \n\n"
    
    # 2. Base Instructions
    if use_prompt:
        prompt += (
            f"You are an expert SQL developer. Given the following database schema:\n\n{schema}\n\n"
            "Generate a single, syntactically correct SQLite query for the user's question. "
            "Your response must begin directly with 'SELECT', 'WITH', or another SQL keyword. "
            "Return ONLY the SQL code, with no explanations or markdown formatting. "
        )
    else:
        prompt += f"Given the following database schema:\n\n{schema}\n\n"

    # 3. Add Examples (Few-Shot)
    prompt += "\n\n" + FEW_SHOT_EXAMPLES.get(technique, "")
    
    return prompt

# ==========================================
# HELPER: MODEL FILTERING
# ==========================================
def get_active_models(group: str, registry: list, available_clients: dict):
    """Returns a dict of {model_name: partial_function} based on the selected group."""
    filtered_models = {}
    
    # Logic to match group string to model tags
    def is_in_group(model, group_key):
        if group_key == "all": return True
        # Handle simple tags (e.g. "small")
        if group_key in model["tags"]: return True
        # Handle composite tags (e.g. "small-opensource")
        if "-" in group_key:
            parts = group_key.split('-')
            return all(part in model["tags"] for part in parts)
        return False

    for m in registry:
        client_name = m["client"]
        
        # Check availability and group match
        if client_name in available_clients and is_in_group(m, group):
            filtered_models[m["name"]] = partial(
                get_sql_from_ai, 
                model=m["id"], 
                client_name=client_name
            )
            
    return filtered_models

# ==========================================
# HELPERS: METRICS (PRESERVED)
# ==========================================
def normalize_row(row_dict):
    """Converts a dict row into a hashable tuple for comparison."""
    normalized_items = []
    for k, v in row_dict.items():
        val_str = str(v).strip()
        normalized_items.append((k.lower(), val_str))
    return tuple(sorted(normalized_items))

def calculate_accuracy(expected_dicts, actual_rows, actual_headers):
    """Calculates recall percentage of expected rows vs actual rows."""
    if not expected_dicts:
        return (100.0, 0, 0) if not actual_rows else (0.0, 0, 0)
    if actual_rows is None: 
        return (0.0, 0, len(expected_dicts))

    expected_set = {normalize_row(d) for d in expected_dicts}
    actual_set = set()
    
    for row in actual_rows:
        if len(row) == len(actual_headers):
            row_dict = dict(zip(actual_headers, row))
            actual_set.add(normalize_row(row_dict))
    
    matches = expected_set.intersection(actual_set)
    match_count = len(matches)
    total_expected = len(expected_set)

    return (match_count / total_expected) * 100.0, match_count, total_expected

def load_test_cases(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading queries: {e}")
        return []

# ==========================================
# MAIN EXECUTION
# ==========================================
def main(group_name: str, use_system_prompt: bool, prompt_technique: str, reasoning: bool):
    print(f"\n--- Running Benchmark for Group: '{group_name.upper()}' ---")
    
    # 1. Setup Models
    llms = get_active_models(group_name, MODEL_REGISTRY, clients)
    if not llms:
        print(f"Error: No available models found for group '{group_name}'.")
        return

    # 2. Setup Data
    test_cases = load_test_cases(QUERIES_PATH)
    if not test_cases: return

    benchmark_report = []
    model_stats = {name: {"total_score": 0, "queries_run": 0} for name in llms}

    with DBHandler(DB_PATH) as db:
        db_schema = db.get_schema()
        print(f"Schema loaded. Benchmarking {len(test_cases)} queries across {len(llms)} models.\n")
        
        # Prepare system prompt once (it's constant for the schema/technique)
        sys_prompt = build_system_prompt(db_schema, use_system_prompt, reasoning, prompt_technique)

        for i, case in enumerate(test_cases):
            query_id = case.get('id', f'q_{i}')
            print(f"{'='*10} Test Case {i+1}: {query_id} {'='*10}")
            print(f"Q: {case['question']}")
            
            expected_data = case.get("ground_truth_results", [])
            print(f"Expected Rows: {len(expected_data)}")
            
            user_prompt = f"User Question: {case['question']}\n\n"

            for model_name, model_func in llms.items():
                print(f"  > Model: {model_name}...", end=" ", flush=True)

                start_time = time.time()
                try:
                    generated_sql = model_func(sys_prompt=sys_prompt, prompt=user_prompt)
                    clean_sql = generated_sql.replace('```sql', '').replace('```', '').strip()
                    
                    # Execute
                    ai_headers, ai_rows = db.execute_query(clean_sql)
                    error_msg = "None"
                except Exception as e:
                    print(f" [Err: {e}]", end="")
                    clean_sql = ""
                    ai_headers, ai_rows = [], None
                    error_msg = str(e)

                latency = time.time() - start_time
                
                # Metrics
                score, matched, total = calculate_accuracy(expected_data, ai_rows, ai_headers)
                
                model_stats[model_name]["total_score"] += score
                model_stats[model_name]["queries_run"] += 1
                
                status_icon = "✅" if score == 100 else "⚠️" if score > 0 else "❌"
                print(f"{status_icon} Score: {score:.1f}% ({matched}/{total}) - {latency:.2f}s")
                # print(f"    SQL: {clean_sql}") # Optional debug

                benchmark_report.append({
                    "timestamp": datetime.now().isoformat(),
                    "query_id": query_id,
                    "model": model_name,
                    "difficulty": case.get('difficulty'),
                    "match_percentage": score,
                    "rows_matched": matched,
                    "rows_expected": total,
                    "latency": latency,
                    "generated_sql": clean_sql,
                    "error": "SQL Execution Failed" if ai_rows is None else error_msg
                })
                time.sleep(5) 

    # 3. Save & Summarize
    save_and_print_summary(benchmark_report, model_stats, group_name, prompt_technique, use_system_prompt, len(test_cases))


def save_and_print_summary(report_data, stats, group, technique, use_sys, total_cases):
    # Construct Summary
    summary = {
        "metadata": {
            "timestamp_utc": datetime.utcnow().isoformat(),
            "model_group": group,
            "total_queries_run": total_cases,
            "prompt_technique": technique,
            "system_prompt_used": use_sys
        },
        "model_performance": []
    }

    for name, data in stats.items():
        avg = (data["total_score"] / data["queries_run"]) if data["queries_run"] > 0 else 0
        summary["model_performance"].append({
            "model_name": name,
            "average_accuracy": round(avg, 2),
            "queries_completed": data["queries_run"]
        })
    
    summary["model_performance"].sort(key=lambda x: x["average_accuracy"], reverse=True)

    # Save to JSON
    final_output = {"summary": summary, "detailed_report": report_data}
    
    try:
        os.makedirs(RESULTS_DIR, exist_ok=True)
        filename = f"benchmark_{group}_{technique}.json"
        filepath = RESULTS_DIR / filename
        
        with open(filepath, 'w') as f:
            json.dump(final_output, f, indent=2)
        print(f"\nBenchmark report saved to: {filepath}")
    except Exception as e:
        print(f"\nError saving report: {e}")

    # Console Table
    print("\n" + "#"*50)
    print("           BENCHMARK SUMMARY")
    print("#"*50)
    print(f"{'Model Name':<25} | {'Avg Accuracy':<15} | {'Queries'}")
    print("-" * 55)
    for m in summary["model_performance"]:
        print(f"{m['model_name']:<25} | {m['average_accuracy']:.2f}%{' ':<11} | {m['queries_completed']}")
    print("#"*50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # "all" is default, but allow any tag defined in logic
    parser.add_argument("--group", type=str, default="all", help=f"Choices: {', '.join(VALID_GROUPS)}")
    parser.add_argument("--system_prompt", action="store_true", default=True)
    parser.add_argument("--prompt_technique", type=str, default="zero-shot", choices=FEW_SHOT_EXAMPLES.keys() | {"zero-shot"})
    parser.add_argument("--reasoning", action="store_true", default=True)

    args = parser.parse_args()
    main(args.group, args.system_prompt, args.prompt_technique, args.reasoning)