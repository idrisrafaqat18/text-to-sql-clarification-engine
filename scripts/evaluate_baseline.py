import json
import pandas as pd
from src.llm import generate_sql
from src.db import execute_read_only_query

def run_baseline_eval():
    with open("tests/eval_set.json", "r") as f:
        eval_cases = json.load(f)

    results = []

    for case in eval_cases:
        qid = case["id"]
        question = case["question"]
        qtype = case["type"]
        
        print(f"\n[Evaluating Q{qid}] ({qtype}): '{question}'")
        
        try:
            # 1. Generate SQL via LLM without clarification
            generated_sql = generate_sql(question)
            
            # 2. Attempt Execution
            df = execute_read_only_query(generated_sql)
            
            # 3. Categorize Outcome
            if qtype == "unambiguous":
                status = "PASS" if not df.empty else "NO_RESULTS"
            else:
                # Ambiguous queries generated without clarification are marked as unhandled assumptions
                status = "UNHANDLED_AMBIGUITY"

            results.append({
                "id": qid,
                "question": question,
                "type": qtype,
                "status": status,
                "generated_sql": generated_sql
            })

        except Exception as e:
            results.append({
                "id": qid,
                "question": question,
                "type": qtype,
                "status": "EXECUTION_ERROR",
                "error": str(e)
            })

    # Output Baseline Report
    eval_df = pd.DataFrame(results)
    print("\n" + "="*60)
    print("      BASELINE EVALUATION REPORT (Day 2 Pipeline)      ")
    print("="*60)
    print(eval_df[["id", "type", "status"]])
    
    # Calculate baseline metrics
    accuracy = (eval_df["status"] == "PASS").sum() / len(eval_df) * 100
    print(f"\nBaseline Execution Accuracy: {accuracy:.1f}%")

if __name__ == "__main__":
    run_baseline_eval()