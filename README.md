# Text-to-SQL with Clarification Engine

**Goal:** Let users ask questions in plain English over a company database (customers, orders, payments), backed by an engine that actively detects *ambiguous* questions and asks for targeted clari[...]

---

## Key Features

- **Ambiguity Detection:** Identifies under-specified queries (e.g., "Who are our best customers?" → By revenue, order volume, or frequency?) before running database code.
- **Ground Truth Seed Data:** Built-in Python generator produces realistic, messy, and deterministic synthetic database states for evaluation.
- **Containerized Infrastructure:** Single-command setup for a fully reproducible PostgreSQL 16 environment.

---

## Tech Stack

- **Language:** Python 3.10+
- **Database:** PostgreSQL 16 (via Docker Compose)
- **AI & Validation:** Gemini API, Pydantic
- **Data Generation:** Faker, `random`

---

## Database Schema Overview

The relational schema consists of three interconnected core business entities:

```
[ customers ] 1 --- * [ orders ] 1 --- * [ payments ]
```

- **`customers`**: `customer_id` (PK), `name`, `email` (UNIQUE), `city`, `signup_date`
- **`orders`**: `order_id` (PK), `customer_id` (FK), `order_date`, `status` (`delivered`, `shipped`, `cancelled`, `pending`)
- **`payments`**: `payment_id` (PK), `order_id` (FK), `amount`, `payment_date`, `method` (`card`, `cash`, `online`, `wallet`)

---

## Quickstart & Setup

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Python 3.10+

### Step-by-Step Instructions

1. **Spin up PostgreSQL:**
   ```bash
   docker compose up -d
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   ```
   
   **Activate (Windows):**
   ```bash
   venv\Scripts\Activate
   ```
   
   **Activate (macOS/Linux):**
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install faker pydantic google-generativeai python-dotenv psycopg2-binary
   ```

4. **Generate seed data and load into database:**
   ```bash
   python scripts/generate_data.py
   docker compose down -v
   docker compose up -d
   ```

---

## Project Structure

```
.
├── data/
│   └── seed.sql                 # Auto-generated database schema + seed data
├── scripts/
│   └── generate_data.py         # Deterministic data generation script
├── notes/
│   └── docker-notes.md          # Docker reference and cheat sheet
├── docker-compose.yml           # Postgres 16 container service definition
├── decisions.md                 # Project Decisions Log (What/Why/Trade-off)
├── PROGRESS.md                  # Progress tracking
└── README.md                    # This file
```

---

## Current Status

🚧 **In progress — Day 1: Infrastructure & Data Setup**

- [x] Step 1: Postgres via Docker
- [x] Step 2: Schema + dummy data
- [x] Step 3: Hand-written SQL practice (10 queries)
- [ ] Step 4: LLM text-to-SQL (no clarification)
- [ ] Step 5: Measure baseline accuracy
- [ ] Step 6: Add clarification engine
- [ ] Step 7: Measure again, compare, document

---

## Next Steps

1. Review `decisions.md` for project design rationale
2. Check `notes/docker-notes.md` for Docker troubleshooting
3. Explore the schema by connecting to the running database:
   ```bash
   docker exec -it text2sql-db psql -U user -d companydb
   ```
