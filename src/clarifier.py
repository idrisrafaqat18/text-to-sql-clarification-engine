# src/clarifier.py
import json
import os
from typing import Dict, Any
from dotenv import load_dotenv
from google import genai
from google.genai import types
from src.db import get_schema_context

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from environment variables.")

client = genai.Client(api_key=api_key)


def analyze_query_ambiguity(user_query: str) -> Dict[str, Any]:
    """
    Analyzes a user query against the schema to determine if clarification is needed.
    Returns a JSON dict indicating whether the query is ambiguous and possible options.
    """
    schema = get_schema_context()

    prompt = f"""
You are a database query assistant analyzing natural language requests for a PostgreSQL database.

### Database Schema:
{schema}

### Core Task:
Determine if the following user question is ambiguous or requires clarification before generating an exact SQL query.

Examples of ambiguity:
- Vague terms like "top customer" (could mean total spent, total orders, or recent activity).
- Unspecified metrics like "sales" (could mean sum of payment amounts or order count).
- Unclear timeframes like "recent" without explicit range constraints.

User Question: "{user_query}"

### Output Requirements:
Respond strictly in JSON format with NO markdown wrapper or extra text.

JSON Schema:
{{
  "is_ambiguous": boolean,
  "ambiguity_reason": "Explanation of why clarification is needed, or empty string if clear",
  "clarification_question": "Follow-up question to ask the user, or empty string if clear",
  "options": ["Option 1", "Option 2", "Option 3"]  // Empty list if clear
}}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt.strip(),
        config=types.GenerateContentConfig(
            temperature=0.0,
            tools=[]  # Explicitly disables automatic function calling warnings
        )
    )

    clean_json = response.text.strip().replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(clean_json)
    except json.JSONDecodeError:
        # Fallback if model output is improperly formatted
        return {
            "is_ambiguous": False,
            "ambiguity_reason": "",
            "clarification_question": "",
            "options": []
        }