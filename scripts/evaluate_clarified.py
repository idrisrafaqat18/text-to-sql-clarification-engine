import json
import os
import sys
from datetime import datetime

# Ensure project root is on Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.clarifier import analyze_query_ambiguity
from src.db import execute_read_only_query
from src.llm import generate_sql

EVAL_SET_PATH = "tests/eval_set.json"
RESULTS_OUTPUT_PATH = "tests/eval_clarified_results.json"


def run_clarified_evaluation():
    if not os.path.exists(EVAL_SET_PATH):
        print(f"Error: Evaluation dataset not found at '{EVAL_SET_PATH}'.")
        return

    with open(EVAL_SET_PATH, "r", encoding="utf-8") as f:
        eval_cases = json.load(f)

    results = []
    counts = {
        "PASS": 0,
        "INTERCEPTED_AMBIGUITY": 0,
        "FALSE_POSITIVE_AMBIGUITY": 0,
        "UNHANDLED_AMBIGUITY": 0,
        "NO_RESULTS": 0,
        "EXECUTION_ERROR": 0,
    }

    print("=" * 65)
    print("STARTING CLARIFIED PIPELINE EVALUATION")
    print("=" * 65)

    for case in eval_cases:
        test_id = case.get("id")
        
        # FIX 1: Safely handle 'question', 'query', or 'user_query'
        user_query = case.get("question") or case.get("query") or case.get("user_query")
        
        # FIX 2: Check both "type" string and "is_ambiguous" boolean
        query_type = case.get("type", "").lower()
        expected_ambiguous = (query_type == "ambiguous") or case.get("is_ambiguous", False)

        print(f"\n[Test #{test_id}] Query: '{user_query}'")

        # Step 1: Pass through clarifier module
        clarification = analyze_query_ambiguity(user_query)
        is_ambiguous = clarification.get("is_ambiguous", False)

        if is_ambiguous:
            if expected_ambiguous:
                outcome = "INTERCEPTED_AMBIGUITY"
                print(" -> [✓] Correctly Intercepted Ambiguous Query")
            else:
                outcome = "FALSE_POSITIVE_AMBIGUITY"
                print(" -> [!] False Positive Ambiguity Detected")

            print(f"    Reason: {clarification.get('ambiguity_reason')}")
            counts[outcome] += 1

            results.append({
                "id": test_id,
                "query": user_query,
                "expected_ambiguous": expected_ambiguous,
                "status": outcome,
                "ambiguity_reason": clarification.get("ambiguity_reason"),
                "clarification_question": clarification.get("clarification_question"),
                "options": clarification.get("options", []),
                "generated_sql": None,
                "execution_error": None,
            })
            continue

        # Check if ambiguity was missed by the clarifier
        if expected_ambiguous and not is_ambiguous:
            print(" -> [!] Missed Ambiguity (Passed directly to SQL generator)")

        # Step 2: Unambiguous pipeline (SQL Generation + Execution)
        sql_query = None
        exec_error = None

        try:
            sql_query = generate_sql(user_query)
            df = execute_read_only_query(sql_query)

            if df.empty:
                outcome = "NO_RESULTS"
                print(" -> Result: Query executed successfully (0 rows returned)")
            else:
                if expected_ambiguous:
                    outcome = "UNHANDLED_AMBIGUITY"
                else:
                    outcome = "PASS"
                print(f" -> Result: SUCCESS ({len(df)} rows returned)")

        except Exception as e:
            outcome = "EXECUTION_ERROR"
            exec_error = str(e)
            print(f" -> Result: EXECUTION ERROR ({exec_error})")

        counts[outcome] += 1

        results.append({
            "id": test_id,
            "query": user_query,
            "expected_ambiguous": expected_ambiguous,
            "status": outcome,
            "generated_sql": sql_query,
            "execution_error": exec_error,
        })

    total = len(eval_cases)
    successful_outcomes = counts["PASS"] + counts["INTERCEPTED_AMBIGUITY"]
    accuracy = (successful_outcomes / total) * 100 if total > 0 else 0.0

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total,
        "accuracy_percentage": round(accuracy, 2),
        "breakdown": counts,
        "details": results,
    }

    os.makedirs(os.path.dirname(RESULTS_OUTPUT_PATH), exist_ok=True)
    with open(RESULTS_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 65)
    print("EVALUATION SUMMARY")
    print("=" * 65)
    print(f"Total Test Cases:            {total}")
    print(f"Passed (Clean Execution):    {counts['PASS']}")
    print(f"Intercepted Ambiguities:     {counts['INTERCEPTED_AMBIGUITY']}")
    print(f"Unhandled Ambiguities:       {counts['UNHANDLED_AMBIGUITY']}")
    print(f"False Positives:             {counts['FALSE_POSITIVE_AMBIGUITY']}")
    print(f"Execution Errors:            {counts['EXECUTION_ERROR']}")
    print(f"Zero Result Set Queries:     {counts['NO_RESULTS']}")
    print("-" * 65)
    print(f"Overall Accuracy Score:      {accuracy:.2f}%")
    print("=" * 65)
    print(f"Detailed output saved to: {RESULTS_OUTPUT_PATH}\n")


if __name__ == "__main__":
    run_clarified_evaluation()