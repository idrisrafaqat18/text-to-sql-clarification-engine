# Docker Notes — Idris's Reference

## Core Concepts

| Concept | Meaning | Example in this project |
|---|---|---|
| **Image** | Read-only blueprint/template | `postgres:16` |
| **Container** | Running instance of an image (disposable) | `text2sql-db` |
| **Volume** | Storage OUTSIDE the container — survives container DELETION; only dies when explicitly deleted | `pgdata` |
| **Docker Compose** | Declares full stack in a YAML file; one command recreates it | `docker-compose.yml` |
| **Docker Hub** | Registry where images come from | source of `postgres:16` |
| **Init scripts** | Scripts in `docker-entrypoint-initdb.d` run ONLY when data dir is empty (first startup) | our `seed.sql` |

## GUI (Docker Desktop) ↔ CLI Cheat Sheet

| GUI Action | CLI Equivalent |
|---|---|
| Containers tab → start/stop | `docker start text2sql-db` / `docker stop text2sql-db` |
| Create stack from compose file (no GUI button) | `docker compose up -d` |
| Logs button | `docker logs text2sql-db` |
| Exec button (shell inside container) | `docker exec -it text2sql-db bash` |
| Delete container (trash icon) | `docker rm text2sql-db` |
| Delete volume (Volumes tab trash) | `docker volume rm <name>` |
| Full wipe: container + volume | GUI: delete both individually<br>CLI: `docker compose down -v` ⚠️ data gone |
| Containers/Images lists | `docker ps -a` / `docker images` |
| Inspect running compose services | `docker compose ps` |
| PSQL directly in our DB | `docker exec -it text2sql-db psql -U user -d companydb` |

## The Volume / `-v` Mental Model

┌─────────────────┐         ┌──────────────────┐
│  CONTAINER      │         │  VOLUME (pgdata) │
│  (postgres:16)  │◄──mount─┤  tables, rows    │
│  disposable 🗑️  │         │  persists 💾     │
└─────────────────┘         └──────────────────┘

- `docker compose down` → container deleted, volume KEPT → data safe
- `docker compose down -v` → container AND volume deleted → next `up` is a fresh install → `seed.sql` re-runs
- Init scripts (`seed.sql`) run ONLY on an empty data dir → fresh volume = seed loads; kept volume = seed ignored

## When to Use What

| Situation | Command |
|---|---|
| Daily stop/start, keep data | `docker compose down` / `docker compose up -d` |
| Changed schema or seed, want fresh DB | `docker compose down -v && docker compose up -d` |
| Just restart | Docker Desktop Restart button / `docker restart text2sql-db` |
| Something misbehaves | READ THE LOGS FIRST (GUI Logs tab) |

## Port Mapping
`ports: "5432:5432"` means `host:container` — my laptop's 5432 forwards into the container's 5432. That's why Python connects to `localhost:5432` and ends up talking to Postgres inside the container.

## Dev Workflow Used in This Project
```bash
python scripts/generate_data.py     # regenerate seed.sql (run from project root!)
docker compose down -v              # wipe (so init script re-runs)
docker compose up -d                # fresh DB + seed loaded
# verify in Exec: psql counts