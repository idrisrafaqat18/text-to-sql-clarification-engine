# src/main.py
import sys
from src.clarifier import analyze_query_ambiguity
from src.llm import generate_sql
from src.db import execute_read_only_query


def process_user_query(user_query: str) -> None:
    print(f"\n==================================================")
    print(f"Incoming Request: '{user_query}'")
    print(f"==================================================\n")

    # Step 1: Pass query through clarification engine
    print(" Analyzing query for schema or business ambiguity...")
    clarification = analyze_query_ambiguity(user_query)

    active_query = user_query

    if clarification.get("is_ambiguous"):
        print("\n Ambiguity Detected!")
        print(f"Reason: {clarification.get('ambiguity_reason')}\n")
        print(f"Question: {clarification.get('clarification_question')}\n")

        options = clarification.get("options", [])
        for idx, option in enumerate(options, 1):
            print(f"  [{idx}] {option}")
        print("  [0] Type a custom clarification")

        try:
            choice = input("\nSelect an option number or type your response: ").strip()
            if choice.isdigit():
                choice_idx = int(choice)
                if 1 <= choice_idx <= len(options):
                    selected_option = options[choice_idx - 1]
                    active_query = f"{user_query} (Clarification: {selected_option})"
                else:
                    active_query = f"{user_query} (Clarification: Proceed with standard defaults)"
            elif choice:
                active_query = f"{user_query} (Clarification: {choice})"
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            sys.exit(0)

        print(f"\n Refined Query Context: '{active_query}'")

    # Step 2: Generate SQL from refined query
    print("\n Generating PostgreSQL query...")
    generated_sql = generate_sql(active_query)
    print(f"\nGenerated SQL:\n{generated_sql}\n")

    # Step 3: Safe execution against PostgreSQL
    print(" Executing query against PostgreSQL...")
    try:
        results = execute_read_only_query(generated_sql)
        print("\nQuery Results:")
        # FIX: Check if DataFrame is empty using .empty
        if results.empty:
            print("No records returned.")
        else:
            print(results.to_string(index=False))
    except Exception as e:
        print(f"\n Execution Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        query_input = " ".join(sys.argv[1:])
    else:
        query_input = input("Enter your natural language question: ")

    process_user_query(query_input)