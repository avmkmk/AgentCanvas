# Deployment Guide — AgentCanvas

**Environments**: Local Dev | CI/CD | Production
**All environments use Docker Compose** — no bare-metal installs.

---

## Services

| Service | Port | Technology | Purpose |
|---------|------|-----------|---------|
| `backend` | 8080 | FastAPI + Uvicorn | REST API + WebSocket |
| `frontend` | 3000 | React + Vite | Web UI |
| `postgres` | 5432 | PostgreSQL 15 | Relational data |
| `mongodb` | 27017 | MongoDB 7 | Document data |
| `redis` | 6379 | Redis 7 | Cache + pub/sub |

---

## Local Development Setup

### Prerequisites
- Docker Desktop (with Compose v2)
- Git
- VS Code (recommended)

### First-Time Setup
```bash
# 1. Clone the repository
git clone <gitlab-repo-url>
cd AgentCanvas

# 2. Copy environment template
cp .env.example .env
# Edit .env — fill in your ANTHROPIC_API_KEY

# 3. Start all services
docker-compose up -d

# 4. Wait ~30 seconds for databases to initialize, then verify
curl http://localhost:8080/health       # → {"status": "healthy"}
curl http://localhost:3000              # → React app loads

# 5. Check all containers are running
docker-compose ps
```

### Daily Start
```bash
docker-compose up -d
docker-compose ps                    # All should show "healthy"
```

### Stopping
```bash
docker-compose down                  # Stop, keep data
docker-compose down -v               # Stop, DELETE all data (clean reset)
```

---

## Environment Variables

All variables defined in `.env` (copied from `.env.example`):

```env
# Required
ANTHROPIC_API_KEY=sk-ant-...
POSTGRES_USER=admin
POSTGRES_PASSWORD=changeme
POSTGRES_DB=orchestrator
MONGODB_USER=admin
MONGODB_PASSWORD=changeme
MONGODB_DB=orchestrator
REDIS_URL=redis://redis:6379/0

# Optional
API_KEY=dev-api-key-changeme
ALLOWED_ORIGINS=http://localhost:3000
LOG_LEVEL=info
MAX_LLM_RETRIES=3
LLM_TIMEOUT_SECONDS=30
```

**Rule**: Never commit `.env`. Only commit `.env.example` with placeholder values.

---

## Docker Compose Services

```yaml
# High-level structure of docker-compose.yml
services:
  backend:
    build: ./backend
    ports: ["8080:8080"]
    environment: [loaded from .env]
    depends_on: [postgres, mongodb, redis]
    volumes: [./backend:/app]           # Hot reload in dev
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    volumes: [./frontend/src:/app/src]  # Hot reload via Vite HMR
    command: npm run dev

  postgres:
    image: postgres:15-alpine
    volumes: [postgres_data:/var/lib/postgresql/data]
    environment: [POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]

  mongodb:
    image: mongo:7
    volumes: [mongo_data:/data/db, ./docker/mongodb/init.js:/docker-entrypoint-initdb.d/init.js]

  redis:
    image: redis:7-alpine
```

---

## Database Initialization

**PostgreSQL**: Schema applied automatically on first `docker-compose up` via init SQL script.

**MongoDB**: Collections and indexes created via `docker/mongodb/init.js` on first start.

### Manual Migration (if needed)
```bash
# PostgreSQL — apply migration manually
docker-compose exec postgres psql -U admin -d orchestrator -f /docker-entrypoint-initdb.d/001_initial.sql

# Check tables exist
docker-compose exec postgres psql -U admin -d orchestrator -c "\dt"
```

### Fresh Reset (drops all data)
```bash
docker-compose down -v
docker-compose up -d
```

---

## Viewing Logs
```bash
docker-compose logs -f              # All services
docker-compose logs -f backend      # Backend only
docker-compose logs -f frontend     # Frontend only
docker-compose logs -f postgres     # DB logs
```

---

## CI/CD Pipeline (GitLab CI)

Pipeline stages (defined in `.gitlab-ci.yml`):

```
build → lint → test → (manual) deploy
```

| Stage | What runs |
|-------|-----------|
| `build` | `docker build` for backend and frontend |
| `lint` | `ruff`, `black --check`, `mypy`, `eslint`, `tsc` |
| `test` | `pytest` + `vitest` with coverage gates |
| `deploy` | Manual trigger only — never auto-deploy |

### CI Environment Variables (set in GitLab CI/CD settings)
- `ANTHROPIC_API_KEY` — use a test/sandbox key
- `POSTGRES_*`, `MONGODB_*`, `REDIS_URL` — test database credentials

---

## Health Checks

```bash
# Backend
curl http://localhost:8080/health
# → {"status": "healthy", "postgres": "ok", "mongodb": "ok", "redis": "ok"}

# Frontend
curl http://localhost:3000
# → 200 OK (HTML)
```

If any service shows "unhealthy" in `docker-compose ps`:
1. Check logs: `docker-compose logs <service>`
2. Common fix: `docker-compose restart <service>`
3. Clean reset: `docker-compose down -v && docker-compose up -d`
