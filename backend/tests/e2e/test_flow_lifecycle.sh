#!/usr/bin/env bash
# =============================================================================
# E2E Test: Full Flow Lifecycle
# Tests: create → read → list → update → delete → verify 404
#
# Usage:
#   BASE_URL=http://localhost:8000 API_KEY=your-key bash test_flow_lifecycle.sh
#
# Requirements: curl, jq
#
# Exit codes:
#   0 — all tests passed
#   1 — one or more tests failed
#   2 — preflight check failed (backend unreachable or missing deps)
# =============================================================================
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
API_KEY="${API_KEY:-}"
PASS=0
FAIL=0

# ─── helpers ─────────────────────────────────────────────────────────────────

pass() {
  echo "  PASS: $1"
  PASS=$((PASS + 1))
}

fail() {
  echo "  FAIL: $1 -- $2"
  FAIL=$((FAIL + 1))
}

skip() {
  echo "  SKIP: $1"
}

# ─── dependency check ─────────────────────────────────────────────────────────

check_deps() {
  if ! command -v curl >/dev/null 2>&1; then
    echo "ERROR: curl not found — install curl and retry"
    exit 2
  fi
  if ! command -v jq >/dev/null 2>&1; then
    echo "ERROR: jq not found — install jq and retry"
    exit 2
  fi
  if [ -z "$API_KEY" ]; then
    echo "ERROR: API_KEY environment variable is not set"
    echo "       Set it with: export API_KEY=your-api-key"
    exit 2
  fi
}

# ─── preflight ────────────────────────────────────────────────────────────────

preflight() {
  echo ""
  echo "Preflight: checking backend at $BASE_URL/health ..."
  if ! curl -sf "$BASE_URL/health" >/dev/null; then
    echo "ERROR: backend not reachable at $BASE_URL"
    echo "       Start services with: docker-compose up -d"
    exit 2
  fi
  echo "  OK: backend is up"
}

# ─── test steps ───────────────────────────────────────────────────────────────

step1_create_flow() {
  echo ""
  echo "Step 1: Create flow"

  RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/flows" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{"name": "e2e-test-flow", "description": "E2E lifecycle test"}')

  HTTP_CODE=$(echo "$RESPONSE" | tail -1)
  BODY=$(echo "$RESPONSE" | head -1)

  if [ "$HTTP_CODE" = "201" ]; then
    FLOW_ID=$(echo "$BODY" | jq -r '.id')
    pass "Create flow returned 201, id=$FLOW_ID"
  else
    fail "Create flow" "Expected 201, got $HTTP_CODE. Body: $BODY"
    FLOW_ID=""
  fi
}

step2_get_flow() {
  echo ""
  echo "Step 2: Get flow by id"

  if [ -z "$FLOW_ID" ]; then
    skip "Get flow (skipped -- no flow id from step 1)"
    return
  fi

  RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/v1/flows/$FLOW_ID" \
    -H "X-API-Key: $API_KEY")

  HTTP_CODE=$(echo "$RESPONSE" | tail -1)
  BODY=$(echo "$RESPONSE" | head -1)

  if [ "$HTTP_CODE" = "200" ]; then
    NAME=$(echo "$BODY" | jq -r '.name')
    if [ "$NAME" = "e2e-test-flow" ]; then
      pass "Get flow returned correct name"
    else
      fail "Get flow" "Expected name 'e2e-test-flow', got '$NAME'"
    fi
  else
    fail "Get flow" "Expected 200, got $HTTP_CODE"
  fi
}

step3_list_flows() {
  echo ""
  echo "Step 3: List flows"

  RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/v1/flows?page=1&page_size=10" \
    -H "X-API-Key: $API_KEY")

  HTTP_CODE=$(echo "$RESPONSE" | tail -1)
  BODY=$(echo "$RESPONSE" | head -1)

  if [ "$HTTP_CODE" = "200" ]; then
    TOTAL=$(echo "$BODY" | jq -r '.total')
    if [ "$TOTAL" -ge "1" ]; then
      pass "List flows returned total=$TOTAL"
    else
      fail "List flows" "Expected total >= 1, got $TOTAL"
    fi
  else
    fail "List flows" "Expected 200, got $HTTP_CODE"
  fi
}

step4_update_flow() {
  echo ""
  echo "Step 4: Update flow name"

  if [ -z "$FLOW_ID" ]; then
    skip "Update flow (skipped -- no flow id from step 1)"
    return
  fi

  RESPONSE=$(curl -s -w "\n%{http_code}" -X PATCH "$BASE_URL/api/v1/flows/$FLOW_ID" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{"name": "e2e-test-flow-updated"}')

  HTTP_CODE=$(echo "$RESPONSE" | tail -1)
  BODY=$(echo "$RESPONSE" | head -1)

  if [ "$HTTP_CODE" = "200" ]; then
    NAME=$(echo "$BODY" | jq -r '.name')
    if [ "$NAME" = "e2e-test-flow-updated" ]; then
      pass "Update flow returned new name"
    else
      fail "Update flow" "Expected 'e2e-test-flow-updated', got '$NAME'"
    fi
  else
    fail "Update flow" "Expected 200, got $HTTP_CODE. Body: $BODY"
  fi
}

step5_delete_flow() {
  echo ""
  echo "Step 5: Delete flow"

  if [ -z "$FLOW_ID" ]; then
    skip "Delete flow (skipped -- no flow id from step 1)"
    return
  fi

  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE_URL/api/v1/flows/$FLOW_ID" \
    -H "X-API-Key: $API_KEY")

  if [ "$HTTP_CODE" = "204" ]; then
    pass "Delete flow returned 204"
  else
    fail "Delete flow" "Expected 204, got $HTTP_CODE"
  fi
}

step6_verify_404() {
  echo ""
  echo "Step 6: Verify 404 after delete"

  if [ -z "$FLOW_ID" ]; then
    skip "Verify 404 (skipped -- no flow id from step 1)"
    return
  fi

  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE_URL/api/v1/flows/$FLOW_ID" \
    -H "X-API-Key: $API_KEY")

  if [ "$HTTP_CODE" = "404" ]; then
    pass "Deleted flow returns 404"
  else
    fail "Verify 404" "Expected 404, got $HTTP_CODE"
  fi
}

# ─── summary ─────────────────────────────────────────────────────────────────

summary() {
  echo ""
  echo "============================================"
  echo "Results: $PASS passed, $FAIL failed"
  echo "============================================"
  if [ "$FAIL" -gt "0" ]; then
    exit 1
  fi
}

# ─── main ─────────────────────────────────────────────────────────────────────

FLOW_ID=""
check_deps
preflight
step1_create_flow
step2_get_flow
step3_list_flows
step4_update_flow
step5_delete_flow
step6_verify_404
summary
