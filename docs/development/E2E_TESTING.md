# End-to-End Testing Guide — AgentCanvas

**Applies to**: All contributors
**Script**: `scripts/run_e2e_tests.sh`
**When to run**: Before every PR merge, after every significant change

---

## Quick Start

```bash
# One-time: copy env file
cp .env.example .env   # fill in the required values (see Prerequisites)

# Full E2E run (builds images, starts services, runs all checks)
bash scripts/run_e2e_tests.sh

# Skip Docker build (faster on second run)
bash scripts/run_e2e_tests.sh --skip-rebuild

# Backend only (no frontend container required)
bash scripts/run_e2e_tests.sh --backend-only
```

**Expected output on a clean pass:**

```
AgentCanvas — E2E Test Suite

══ Pre-flight ══
  ✔  docker available
  ✔  .env file present

══ Services ══
  ✔  docker compose build backend
  ✔  docker compose up -d
  ✔  service: postgres
  ✔  service: mongodb
  ✔  service: redis
  ✔  service: backend
  ✔  service: frontend

══ API health endpoint ══
  ✔  GET /health → 200
  ✔  /health response — no connection strings

══ Backend static analysis ══
  ✔  ruff check app/
  ✔  mypy app/

══ Backend unit tests ══
  ✔  pytest tests/unit/ — 62 tests passed

══ Frontend static analysis ══
  ✔  npm run lint
  ✔  npm run type-check

══ Frontend unit tests ══
  ⚠  SKIP  vitest — No test files yet

══ Summary ══
  Total: 14  |  Pass: 13  |  Fail: 0  |  Skip: 1

E2E run PASSED.
```

---

## Prerequisites

### 1. Docker Desktop

Install from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop).

### 2. `.env` file

Copy the template and set the minimum required values:

```bash
cp .env.example .env
```

Required values for local dev (unit tests mock these — Docker needs them to start):

| Variable | Value |
|----------|-------|
| `POSTGRES_PASSWORD` | `localdev` (any string) |
| `POSTGRES_USER` | `admin` |
| `POSTGRES_DB` | `orchestrator` |
| `MONGODB_PASSWORD` | `localdev` (any string) |
| `API_KEY` | `dev-local-key` (any non-placeholder string) |
| `ANTHROPIC_API_KEY` | `sk-ant-fake` (unit tests mock this — no real key needed) |
| `ALLOWED_ORIGINS` | `http://localhost:3000` |

---

## What the Script Checks

| Stage | Check | Fails if |
|-------|-------|---------|
| Pre-flight | `docker` on PATH | Docker not installed |
| Pre-flight | `.env` file exists | `.env` missing |
| Services | `docker compose build backend` | Dockerfile syntax error or dep missing |
| Services | `docker compose up -d` | Compose config broken |
| Services | All 5 containers healthy | Container crash-loops |
| API | `GET /health` → 200 | Backend not running or schema broken |
| API | No connection strings in `/health` response | Security regression |
| Backend | `ruff check app/` | Lint error introduced |
| Backend | `mypy app/` | Type error introduced |
| Backend | `pytest tests/unit/` — all 62 pass | Test regression |
| Frontend | `npm run lint` | ESLint error introduced |
| Frontend | `npm run type-check` | TypeScript error introduced |
| Frontend | `vitest` | Test failure (SKIP when no test files yet) |

---

## Interpreting Failures

### `service: backend — status=Exiting`

The backend container started but crashed. Check the logs:

```bash
docker compose logs backend --tail 50
```

Most common cause: `.env` variables missing or misspelled. Ensure `API_KEY`,
`DATABASE_URL`, and `ANTHROPIC_API_KEY` are all set.

### `GET /health → 503`

Backend is running but at least one dependency (Postgres, Mongo, or Redis)
is not reachable. Check each service:

```bash
docker compose ps
docker compose logs postgres --tail 20
docker compose logs mongodb --tail 20
docker compose logs redis --tail 20
```

### `pytest tests/unit/ — N failure(s)`

```bash
# Run with full traceback
docker compose exec backend pytest tests/unit/ -v --tb=long
# Or open the log
cat /tmp/ac_pytest.log
```

Unit tests are fully isolated (in-memory SQLite, mocked LLM). Failures
indicate a code regression, not an infrastructure problem.

### `ruff check app/` or `mypy app/`

```bash
docker compose exec backend ruff check app/
docker compose exec backend python -m mypy app/ --ignore-missing-imports
```

Fix all errors before pushing. The CI gate will reject PRs with lint or
type failures.

### `npm run type-check` fails

```bash
docker compose exec frontend npm run type-check 2>&1 | head -40
```

Check `frontend/src/` for TypeScript errors. Ensure any new files
are included in `tsconfig.json`.

---

## Running Individual Checks

You can run any subset of checks directly without the full script:

```bash
# Backend only
docker compose exec backend pytest tests/unit/ -v
docker compose exec backend ruff check app/
docker compose exec backend python -m mypy app/ --ignore-missing-imports

# Frontend only
docker compose exec frontend npm run lint
docker compose exec frontend npm run type-check
docker compose exec frontend npm test

# Health endpoint only
curl -s http://localhost:8080/health | python3 -m json.tool
```

---

## Incremental Test Workflow (per Feature)

Follow this checklist every time a new feature lands:

```
[ ] Run: bash scripts/run_e2e_tests.sh --skip-rebuild
[ ] All existing 62 backend unit tests still pass
[ ] New tests written for any new validator / service / router
[ ] ruff + mypy pass with zero errors
[ ] eslint + tsc pass with zero errors
[ ] No test calls the real Anthropic API (mock_llm fixture only)
[ ] No test requires a live PostgreSQL connection (db_session fixture only)
```

See `docs/development/TESTING_STRATEGY.md` for the full test-writing guide.

---

## CI Integration

The script is designed to be used in CI pipelines. It exits `0` on full
pass and `1` on any failure, which is the standard convention for CI
scripts.

GitHub Actions example:

```yaml
name: E2E
on: [push, pull_request]
jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Copy env
        run: cp .env.example .env
      - name: Run E2E tests
        run: bash scripts/run_e2e_tests.sh
```

---

## Log Files

The script writes temporary log files to `/tmp/ac_*.log`:

| File | Contents |
|------|----------|
| `/tmp/ac_build_backend.log` | `docker compose build backend` output |
| `/tmp/ac_compose_up.log` | `docker compose up` output |
| `/tmp/ac_health_resp.json` | Raw JSON from `/health` |
| `/tmp/ac_ruff.log` | ruff output |
| `/tmp/ac_mypy.log` | mypy output |
| `/tmp/ac_pytest.log` | Full pytest output |
| `/tmp/ac_eslint.log` | ESLint output |
| `/tmp/ac_tsc.log` | TypeScript compiler output |
| `/tmp/ac_vitest.log` | Vitest output |

---

**Last Updated**: 2026-03-05
**Milestone**: M1 — Testing Infrastructure
