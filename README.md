# Text-to-SQL with Clarification Engine

**Goal:** Let users ask questions in plain English over a company database (customers, orders, payments), backed by an engine that actively detects *ambiguous* questions and asks for targeted clarification before generating SQL — bridging the gap between tutorial AI and production AI.

---

## Key Features
* **Ambiguity Detection:** Identifies under-specified queries (e.g., "Who are our best customers?" $\rightarrow$ *By revenue, order volume, or frequency?*) before running database code.
* **Ground Truth Seed Data:** Built-in Python generator produces realistic, messy, and deterministic synthetic database states for evaluation.
* **Containerized Infrastructure:** Single-command setup for a fully reproducible PostgreSQL 16 environment.

---

## Tech Stack
* **Language:** Python 3.10+
* **Database:** PostgreSQL 16 (via Docker Compose)
* **AI & Validation:** Gemini API, Pydantic
* **Data Generation:** Faker, `random`

---

## Database Schema Overview
The relational schema consists of three interconnected core business entities:

[ customers ] 1 --- * [ orders ] 1 --- * [ payments ]

* **`customers`**: `customer_id` (PK), `name`, `email` (UNIQUE), `city`, `signup_date`
* **`orders`**: `order_id` (PK), `customer_id` (FK), `order_date`, `status` (`delivered`, `shipped`, `cancelled`, `pending`)
* **`payments`**: `payment_id` (PK), `order_id` (FK), `amount`, `payment_date`, `method` (`card`, `cash`, `online`, `wallet`)

---

## Quickstart & Setup

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
* Python 3.10+

### Step-by-Step Instructions

1. **Spin up PostgreSQL:**
   ```bash
   docker compose up -d

   python -m venv venv
# Activate (Windows)
venv\Scripts\Activate
# Activate (macOS/Linux)
# source venv/bin/activate

pip install faker

Project Structure

.
├── data/
│   └── seed.sql             # Auto-generated database schema + seed data
├── scripts/
│   └── generate_data.py     # Deterministic data generation script
├── docker-compose.yml       # Postgres 16 container service definition
├── decisions.md             # Project Decisions Log (What/Why/Trade-off)
└── README.md

Current Status

🚧 In progress — Day 1: Infrastructure & Data Setup


<FollowUp label="Would you like to draft the docker-compose.yml file to back up this setup?" query="Write a production-ready docker-compose.yml file for Postgres 16 that mounts data/seed.sql into docker-entrypoint-initdb.d."/>