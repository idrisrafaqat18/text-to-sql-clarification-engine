# Docker Notes — Reference Guide

---

## Core Concepts

| Concept | Meaning | Example in this project |
|---------|---------|------------------------|
| **Image** | Read-only blueprint/template | `postgres:16` |
| **Container** | Running instance of an image (disposable) | `text2sql-db` |
| **Volume** | Storage OUTSIDE the container — survives container deletion; only dies when explicitly deleted | `pgdata` |
| **Docker Compose** | Declares full stack in a YAML file; one command recreates it | `docker-compose.yml` |
| **Docker Hub** | Registry where images come from | source of `postgres:16` |
| **Init scripts** | Scripts in `docker-entrypoint-initdb.d` run ONLY when data dir is empty (first startup) | our `seed.sql` |

---

## GUI (Docker Desktop) ↔ CLI Cheat Sheet

| GUI Action | CLI Equivalent |
|-----------|-----------------|
| Containers tab → start/stop | `docker start text2sql-db` / `docker stop text2sql-db` |
| Create stack from compose file (no GUI button) | `docker compose up -d` |
| Logs button | `docker logs text2sql-db` |
| Exec button (shell inside container) | `docker exec -it text2sql-db bash` |
| Delete container (trash icon) | `docker rm text2sql-db` |
| Delete volume (Volumes tab trash) | `docker volume rm <name>` |
| Full wipe: container + volume | GUI: delete both individually<br/>CLI: `docker compose down -v` ⚠️ **data gone** |
| Containers/Images lists | `docker ps -a` / `docker images` |
| Inspect running compose services | `docker compose ps` |
| PSQL directly in our DB | `docker exec -it text2sql-db psql -U intern -d companydb` |

---

## The Volume / `-v` Mental Model

```
┌─────────────────┐         ┌──────────────────┐
│  CONTAINER      │         │  VOLUME (pgdata) │
│  (postgres:16)  │◄──mount─┤  tables, rows    │
│  disposable 🗑️  │         │  persists 💾     │
└─────────────────┘         └──────────────────┘
```

- `docker compose down` → container deleted, volume **KEPT** → data safe
- `docker compose down -v` → container AND volume deleted → next `up` is a fresh install → `seed.sql` re-runs
- Init scripts (`seed.sql`) run **ONLY** on an empty data dir → fresh volume = seed loads; kept volume = seed ignored

---

## When to Use What

| Situation | Command |
|-----------|---------|
| Daily stop/start, keep data | `docker compose down` / `docker compose up -d` |
| Changed schema or seed, want fresh DB | `docker compose down -v && docker compose up -d` |
| Just restart | Docker Desktop Restart button / `docker restart text2sql-db` |
| Something misbehaves | **READ THE LOGS FIRST** (GUI Logs tab) |

---

## Port Mapping

`ports: "5432:5432"` means `host:container` — your laptop's port 5432 forwards into the container's port 5432. That's why Python connects to `localhost:5432` and ends up talking to Postgres inside the container.

---

## Dev Workflow Used in This Project

```bash
# Step 1: Regenerate seed.sql with new data
python scripts/generate_data.py

# Step 2: Wipe the old container and volume (so init script re-runs)
docker compose down -v

# Step 3: Bring up fresh DB with newly seeded data
docker compose up -d

# Step 4: Verify (optional)
docker exec -it text2sql-db psql -U intern -d companydb -c "SELECT COUNT(*) FROM customers;"
```

---

## Quick Troubleshooting

**Issue:** Container won't start or crashes immediately
- **Check:** `docker logs text2sql-db` (scroll to the error)
- **Common cause:** Port 5432 already in use, or bad compose file syntax

**Issue:** Data from old seed still appears after `docker compose up -d`
- **Check:** Did you run `docker compose down -v`? (the `-v` is crucial)
- **Fix:** `docker compose down -v && docker compose up -d`

**Issue:** `seed.sql` didn't load
- **Check:** Is it in the right directory? Compose file points to `./data/seed.sql`
- **Check:** Is the volume new (empty)? Init scripts only run on empty volumes
- **Fix:** `docker compose down -v && docker compose up -d`

**Issue:** Can't connect with `psql`
- **Check:** Is the container running? `docker ps`
- **Check:** Correct credentials? (user=`intern`, db=`companydb`)
- **Example:** `docker exec -it text2sql-db psql -U intern -d companydb`
