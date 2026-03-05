#!/usr/bin/env bash
# Run all 62 backend unit tests locally (no Docker required).
# Usage:  bash scripts/run_local_tests.sh
#         bash scripts/run_local_tests.sh --coverage
set -euo pipefail

COVERAGE=${1:-}
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/backend"

echo "==> Installing backend dependencies..."
pip install -r requirements.txt --quiet

echo "==> Running unit tests..."
if [[ "$COVERAGE" == "--coverage" ]]; then
  python -m pytest tests/unit/ -v --cov=app --cov-report=term-missing
else
  python -m pytest tests/unit/ -v
fi
