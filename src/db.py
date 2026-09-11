import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

# Build connection string from environment variables
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "postgres")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def execute_read_only_query(sql_query: str) -> pd.DataFrame:
    """"Executes a SQL query in a read-only transaction block with a 5-second timeout."""
    with engine.connect() as connection:
        # Enforce read-only state and query execution timeout
        connection.execute(text("SET TRANSACTION READ ONLY;"))
        connection.execute(text("SET statement_timeout = 5000;"))  # 5 seconds timeout

        result = pd.read_sql_query(text(sql_query), con=connection)
        return result
    
def get_schema_context() -> str:
    """Extracts column metadata and relationships to serve as LLM context."""
    schema_query = """
    SELECT
        table_name,
        column_name,
        data_type
    FROM information_schema.columns
    WHERE table_schema = 'public'
    ORDER BY table_name, ordinal_position;
    """
    df = execute_read_only_query(schema_query)

    schema_text = ""
    for table, group in df.groupby("table_name"):
        schema_text += f"\nTable: {table}\n"
        for _, row in group.iterrows():
            schema_text += f" - {row['column_name']} ({row['data_type']})\n"

    return schema_text.strip()

if __name__ == "__main__":
    # Test connection and schema extraction
    print("--- Database Schema Context ---")
    print(get_schema_context())