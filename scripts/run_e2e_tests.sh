#!/usr/bin/env bash
# =============================================================================
# AgentCanvas — End-to-End Test Runner
# =============================================================================
# Usage:
#   ./scripts/run_e2e_tests.sh                 # run everything
#   ./scripts/run_e2e_tests.sh --backend-only  # skip frontend checks
#   ./scripts/run_e2e_tests.sh --skip-rebuild  # skip docker build step
#
# Exit codes:
#   0  All checks passed
#   1  One or more checks failed (details printed to stdout)
#
# Requirements:
#   - docker and docker-compose on PATH
#   - .env file present at repo root (copy from .env.example)
# =============================================================================

set -euo pipefail

# ─── Colour helpers ────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'  # no colour

pass()  { echo -e "  ${GREEN}✔${NC}  $*"; }
fail()  { echo -e "  ${RED}✖${NC}  $*"; }
info()  { echo -e "  ${BLUE}→${NC}  $*"; }
warn()  { echo -e "  ${YELLOW}⚠${NC}  $*"; }
header(){ echo -e "\n${BOLD}${BLUE}══ $* ══${NC}"; }

# ─── Parse arguments ───────────────────────────────────────────────────────────
BACKEND_ONLY=false
SKIP_REBUILD=false
for arg in "$@"; do
  case "$arg" in
    --backend-only)  BACKEND_ONLY=true ;;
    --skip-rebuild)  SKIP_REBUILD=true ;;
    --help|-h)
      echo "Usage: $0 [--backend-only] [--skip-rebuild]"
      exit 0
      ;;
  esac
done

# ─── State tracking ────────────────────────────────────────────────────────────
PASS=0
FAIL=0
SKIP=0
REPORT=()   # array of "STATUS | label | detail" strings

record() {
  local status="$1" label="$2" detail="${3:-}"
  REPORT+=("$status|$label|$detail")
  if [[ "$status" == "PASS" ]]; then
    ((PASS++))
    pass "$label"
  elif [[ "$status" == "FAIL" ]]; then
    ((FAIL++))
    fail "$label  →  $detail"
  else
    ((SKIP++))
    warn "SKIP  $label  →  $detail"
  fi
}

# ─── Repo root ──────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

echo -e "\n${BOLD}AgentCanvas — E2E Test Suite${NC}"
echo "  Working dir : $ROOT"
echo "  Backend only: $BACKEND_ONLY"
echo "  Skip rebuild: $SKIP_REBUILD"

# ─── 1. Pre-flight checks ──────────────────────────────────────────────────────
header "Pre-flight"

if ! command -v docker &>/dev/null; then
  record FAIL "docker available" "docker not found on PATH — install Docker Desktop"
  echo -e "\n${RED}Cannot continue without Docker.${NC}" && exit 1
fi
record PASS "docker available" "$(docker --version | head -1)"

if [[ ! -f "$ROOT/.env" ]]; then
  record FAIL ".env file present" "Missing .env — run: cp .env.example .env and fill in values"
  echo -e "\n${RED}Cannot continue without .env.${NC}" && exit 1
fi
record PASS ".env file present"

# ─── 2. Build & start services ────────────────────────────────────────────────
header "Services"

if [[ "$SKIP_REBUILD" == "false" ]]; then
  info "Building backend image (may take ~60 s on first run)..."
  if docker compose build backend &>/tmp/ac_build_backend.log 2>&1; then
    record PASS "docker compose build backend"
  else
    record FAIL "docker compose build backend" "see /tmp/ac_build_backend.log"
  fi
else
  record SKIP "docker compose build backend" "--skip-rebuild set"
fi

info "Starting all services..."
if docker compose up -d &>/tmp/ac_compose_up.log 2>&1; then
  record PASS "docker compose up -d"
else
  record FAIL "docker compose up -d" "see /tmp/ac_compose_up.log"
fi

# Give services a moment to initialise
info "Waiting 8 s for services to become ready..."
sleep 8

# ─── 3. Service health checks ─────────────────────────────────────────────────
header "Service health"

_check_service() {
  local name="$1"
  local status
  status=$(docker compose ps --format json "$name" 2>/dev/null \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('Health','') or d.get('State',''))" 2>/dev/null || echo "unknown")
  # docker compose ps may return an array
  status=$(docker compose ps "$name" 2>/dev/null | tail -1 | awk '{print $NF}')
  if echo "$status" | grep -qi "healthy\|running\|Up"; then
    record PASS "service: $name" "status=$status"
  else
    record FAIL "service: $name" "status=$status — run: docker compose logs $name"
  fi
}

for svc in postgres mongodb redis backend frontend; do
  _check_service "$svc"
done

# ─── 4. Health endpoint ────────────────────────────────────────────────────────
header "API health endpoint"

BACKEND_PORT="${BACKEND_PORT:-8080}"
HEALTH_URL="http://localhost:${BACKEND_PORT}/health"

info "GET $HEALTH_URL ..."
HTTP_CODE=$(curl -s -o /tmp/ac_health_resp.json -w "%{http_code}" \
  --max-time 10 "$HEALTH_URL" 2>/dev/null || echo "000")

if [[ "$HTTP_CODE" == "200" ]]; then
  record PASS "GET /health → 200"
  # Validate response does not leak connection strings
  if grep -qiE "(postgresql|mongodb|redis)://" /tmp/ac_health_resp.json 2>/dev/null; then
    record FAIL "/health response — no connection strings" \
      "Response contains a connection string — security issue!"
  else
    record PASS "/health response — no connection strings"
  fi
elif [[ "$HTTP_CODE" == "000" ]]; then
  record FAIL "GET /health" "Could not connect — is backend running on port $BACKEND_PORT?"
else
  record FAIL "GET /health → $HTTP_CODE" "$(cat /tmp/ac_health_resp.json 2>/dev/null | head -c 200)"
fi

# ─── 5. Backend lint + type-check ─────────────────────────────────────────────
header "Backend static analysis"

info "Running ruff..."
if docker compose exec -T backend ruff check app/ \
    > /tmp/ac_ruff.log 2>&1; then
  record PASS "ruff check app/"
else
  LINES=$(wc -l < /tmp/ac_ruff.log)
  record FAIL "ruff check app/" "$LINES error line(s) — see /tmp/ac_ruff.log"
fi

info "Running mypy..."
if docker compose exec -T backend python -m mypy app/ --ignore-missing-imports \
    > /tmp/ac_mypy.log 2>&1; then
  record PASS "mypy app/"
else
  LINES=$(wc -l < /tmp/ac_mypy.log)
  record FAIL "mypy app/" "$LINES line(s) — see /tmp/ac_mypy.log"
fi

# ─── 6. Backend unit tests ────────────────────────────────────────────────────
header "Backend unit tests"

info "Running pytest tests/unit/ ..."
if docker compose exec -T backend pytest tests/unit/ -v \
    --tb=short --no-header \
    > /tmp/ac_pytest.log 2>&1; then
  PASSED=$(grep -c "PASSED" /tmp/ac_pytest.log || true)
  record PASS "pytest tests/unit/ — $PASSED tests passed"
else
  FAILED=$(grep -c "FAILED\|ERROR" /tmp/ac_pytest.log || true)
  record FAIL "pytest tests/unit/" "$FAILED failure(s) — see /tmp/ac_pytest.log"
  echo ""
  echo "  Last 20 lines of pytest output:"
  tail -20 /tmp/ac_pytest.log | sed 's/^/    /'
fi

# ─── 7. Frontend checks ───────────────────────────────────────────────────────
if [[ "$BACKEND_ONLY" == "true" ]]; then
  record SKIP "frontend lint" "--backend-only set"
  record SKIP "frontend type-check" "--backend-only set"
  record SKIP "frontend tests" "--backend-only set"
else
  header "Frontend static analysis"

  info "Running eslint..."
  if docker compose exec -T frontend npm run lint \
      > /tmp/ac_eslint.log 2>&1; then
    record PASS "npm run lint"
  else
    LINES=$(wc -l < /tmp/ac_eslint.log)
    record FAIL "npm run lint" "$LINES line(s) — see /tmp/ac_eslint.log"
  fi

  info "Running tsc --noEmit..."
  if docker compose exec -T frontend npm run type-check \
      > /tmp/ac_tsc.log 2>&1; then
    record PASS "npm run type-check"
  else
    LINES=$(wc -l < /tmp/ac_tsc.log)
    record FAIL "npm run type-check" "$LINES line(s) — see /tmp/ac_tsc.log"
  fi

  header "Frontend unit tests"

  info "Running vitest..."
  if docker compose exec -T frontend npm test \
      > /tmp/ac_vitest.log 2>&1; then
    # "No test files found" is OK at M1 — just means no tests written yet
    if grep -qi "no test files found\|no tests" /tmp/ac_vitest.log 2>/dev/null; then
      record SKIP "vitest" "No test files yet — create src/__tests__/ to add tests"
    else
      PASSED=$(grep -c "✓\|passed" /tmp/ac_vitest.log || true)
      record PASS "vitest — $PASSED test(s) passed"
    fi
  else
    LINES=$(wc -l < /tmp/ac_vitest.log)
    record FAIL "vitest" "$LINES line(s) — see /tmp/ac_vitest.log"
  fi
fi

# ─── 8. Final report ──────────────────────────────────────────────────────────
TOTAL=$((PASS + FAIL + SKIP))
header "Summary"

echo ""
printf "  %-40s  %s\n" "Check" "Result"
printf "  %-40s  %s\n" "$(printf '%.0s─' {1..40})" "──────"
for entry in "${REPORT[@]}"; do
  IFS='|' read -r status label detail <<< "$entry"
  case "$status" in
    PASS) sym="${GREEN}PASS${NC}" ;;
    FAIL) sym="${RED}FAIL${NC}" ;;
    *)    sym="${YELLOW}SKIP${NC}" ;;
  esac
  printf "  %-40s  %b\n" "$label" "$sym"
done

echo ""
echo -e "  ${BOLD}Total: $TOTAL  |  ${GREEN}Pass: $PASS${NC}${BOLD}  |  ${RED}Fail: $FAIL${NC}${BOLD}  |  ${YELLOW}Skip: $SKIP${NC}"
echo ""

if [[ $FAIL -gt 0 ]]; then
  echo -e "${RED}${BOLD}E2E run FAILED ($FAIL check(s) failed).${NC}"
  echo "  Logs written to /tmp/ac_*.log"
  exit 1
else
  echo -e "${GREEN}${BOLD}E2E run PASSED.${NC}"
  exit 0
fi
