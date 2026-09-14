# src/llm.py
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from src.db import get_schema_context

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from environment variables.")

client = genai.Client(api_key=api_key)


def generate_sql(user_query: str) -> str:
    """Calls Gemini via Chat interface to convert plain English to SQL without AFC logs."""
    schema = get_schema_context()
    
    system_instruction = (
        "You are a PostgreSQL expert. Given the database schema, generate a valid SQL query "
        "to answer the user's question. Output ONLY executable SQL without markdown formatting, "
        "backticks, or explanatory text."
    )
    
    prompt = f"Database Schema:\n{schema}\n\nUser Question: {user_query}"
    
    # Use client.chats.create to conform to SDK recommendations
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.0
        )
    )
    
    response = chat.send_message(prompt)
    
    # Sanitize output by stripping markdown blocks
    raw_sql = response.text.strip()
    clean_sql = raw_sql.replace("```sql", "").replace("```", "").strip()
    return clean_sql


if __name__ == "__main__":
    test_question = "Show me all delivered orders from last month"
    print(f"Question: {test_question}\n")
    print("Generated SQL:")
    print(generate_sql(test_question))