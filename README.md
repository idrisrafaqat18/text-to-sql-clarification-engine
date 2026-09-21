# Text-to-SQL with Clarification Engine

**Goal:** Allow users to ask natural-language questions over a company database (`customers`, `orders`, and `payments`) while actively detecting ambiguous business questions and requesting targeted clarification before SQL execution.

## Key Features

- **Ambiguity detection:** Identifies under-specified questions such as *"Who is our top customer?"* and asks whether "top" means revenue, order volume, or recent activity.
- **Deterministic ground-truth data:** Generates realistic, messy, reproducible synthetic data for evaluation.
- **Containerized infrastructure:** Provides a reproducible PostgreSQL 16 environment through Docker Compose.
- **Automated benchmarking:** Compares direct Text-to-SQL execution with pre-execution ambiguity interception.

## Tech Stack

- **Language:** Python 3.10+
- **Database:** PostgreSQL 16 via Docker Compose
- **AI and validation:** Gemini API (`google-genai`) and Pydantic
- **Data generation and execution:** Faker, Pandas, SQLAlchemy, and Psycopg2

## Database Schema

```text
[ customers ] 1 --- * [ orders ] 1 --- * [ payments ]
```

- **`customers`**: `customer_id` (PK), `name`, `email` (UNIQUE), `city`, `signup_date`
- **`orders`**: `order_id` (PK), `customer_id` (FK), `order_date`, `status` (`delivered`, `shipped`, `cancelled`, `pending`)
- **`payments`**: `payment_id` (PK), `order_id` (FK), `amount`, `payment_date`, `method` (`card`, `cash`, `upi`, `wallet`)

## Quickstart

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Python 3.10+
- A Gemini API key for LLM-powered SQL generation

### 1. Configure environment variables

Copy `.env.example` to `.env` and adjust the values if needed. The defaults match `docker-compose.yml`:

```dotenv
POSTGRES_USER=user
POSTGRES_PASSWORD=123
POSTGRES_DB=companydb
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\Activate
```

Activate it on macOS/Linux:

```bash
source venv/bin/activate
```

Install the pinned project dependencies:

```bash
pip install -r requirements.txt
```

### 3. Generate and load the database

The generator writes the schema and deterministic seed data to `data/seed.sql`. Recreate the database volume so PostgreSQL runs the generated initialization script:

```bash
python scripts/generate_data.py
docker compose down -v
docker compose up -d
```

### 4. Run the Text-to-SQL CLI

```bash
python -m src.main "Who is our top customer?"
```

For an ambiguous question, the clarification engine intercepts the request before SQL execution and presents structured options to the user.

## Evaluation and Benchmarks

Run the clarified-pipeline benchmark with:

```bash
python scripts/evaluate_clarified.py
```

The evaluation uses `tests/eval_set.json` and writes results to `tests/eval_clarified_results.json`.

### Reported benchmark results

| Metric | Result | Breakdown |
| --- | --- | --- |
| Total test cases | 4 | 2 unambiguous, 2 ambiguous |
| Overall accuracy | 100.0% | 4 / 4 passed |
| Direct SQL execution | PASS | 2 / 2 executed successfully |
| Ambiguity interception | PASS | 2 / 2 intercepted before execution |
| False positives | 0 | No unambiguous queries incorrectly flagged |
| Unhandled ambiguities | 0 | No ambiguous queries ran blindly |
| Execution errors | 0 | No SQL or driver exceptions |

### Example evaluation cases

**Unambiguous query — direct execution**

> Show me all delivered orders from last month

```sql
SELECT *
FROM orders
WHERE status = 'delivered'
  AND order_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
  AND order_date < DATE_TRUNC('month', CURRENT_DATE);
```

**Ambiguous query — clarification required**

> Who is our top customer?

Possible interpretations:

- Total amount spent
- Total number of orders
- Most recent activity

**Unambiguous query — direct execution**

> How many pending orders do we have?

```sql
SELECT COUNT(*) FROM orders WHERE status = 'pending';
```

**Ambiguous query — clarification required**

> Show me sales by payment method

Possible interpretations:

- Total amount
- Number of payments
- Number of orders

## Project Structure

```text
.
├── data/
│   └── seed.sql                    # Generated schema and deterministic seed data
├── src/
│   ├── db.py                       # Database connection and schema extraction
│   ├── clarifier.py                # Ambiguity detection engine
│   ├── llm.py                      # Text-to-SQL generation
│   └── main.py                     # CLI runner
├── scripts/
│   ├── generate_data.py            # Reproducible data generation
│   ├── evaluate_baseline.py        # Baseline benchmark runner
│   └── evaluate_clarified.py       # Clarified-pipeline benchmark runner
├── tests/
│   ├── eval_set.json               # Ground-truth evaluation suite
│   └── eval_clarified_results.json  # Clarified benchmark output
├── notes/
│   └── docker-notes.md             # Docker reference notes
├── docker-compose.yml              # PostgreSQL 16 service definition
├── requirements.txt                # Pinned Python dependencies
├── .env.example                    # Environment-variable template
├── decisions.md                    # Architectural decisions and trade-offs
├── PROGRESS.md                     # Milestone tracking
└── README.md                       # Project documentation
```

## Useful Commands

Run the baseline benchmark:

```bash
python scripts/evaluate_baseline.py
```

Review architectural decisions:

```text
decisions.md
```

Connect directly to PostgreSQL:

```bash
docker exec -it text2sql-db psql -U user -d companydb
```
