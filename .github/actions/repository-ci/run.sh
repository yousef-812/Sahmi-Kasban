#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../../.." && pwd)}"
PIP_CACHE_DIR="${PIP_CACHE_DIR:-$ROOT_DIR/.github/.cache/pip}"
CI_RESULTS_DIR="${CI_RESULTS_DIR:-$ROOT_DIR/.github/.ci-results}"
SUMMARY_FILE="${GITHUB_STEP_SUMMARY:-$CI_RESULTS_DIR/summary.md}"

mkdir -p "$PIP_CACHE_DIR" "$CI_RESULTS_DIR"
export PIP_CACHE_DIR
cd "$ROOT_DIR"

exec > >(tee "$CI_RESULTS_DIR/full.log") 2>&1

run_check() {
  local label="$1"
  local log_name="$2"
  shift 2

  echo "::group::$label"
  set +e
  "$@" 2>&1 | tee "$CI_RESULTS_DIR/$log_name"
  local status=${PIPESTATUS[0]}
  set -e
  echo "::endgroup::"

  if [[ $status -eq 0 ]]; then
    printf -- "- ✅ %s\n" "$label" >> "$SUMMARY_FILE"
  else
    printf -- "- ❌ %s — exit code %s\n" "$label" "$status" >> "$SUMMARY_FILE"
    return "$status"
  fi
}

printf "## Sahmi Kasban repository-local CI\n\n" > "$SUMMARY_FILE"
printf "Cache directory: \`%s\`\n\n" "$PIP_CACHE_DIR" >> "$SUMMARY_FILE"

python - <<'PY'
import sys

if sys.version_info < (3, 11):
    raise SystemExit(f"Python 3.11+ is required, found {sys.version}")
print(f"Using Python {sys.version.split()[0]}")
PY

run_check "Install Python dependencies" "install.log" \
  python -m pip install --upgrade pip
run_check "Install project packages" "install-project.log" \
  python -m pip install -e ".[dev]" -e "backend[dev]"

run_check "Core compile" "core-compile.log" \
  python -m compileall -q src tests
run_check "Core Ruff" "core-ruff.log" \
  python -m ruff check src tests
run_check "Core tests" "core-tests.log" \
  python -m pytest -q tests

run_check "Backend compile" "backend-compile.log" \
  python -m compileall -q \
    backend/app backend/tests backend/alembic backend/scripts \
    backend/reusable_data_fetcher.py
run_check "Backend Ruff" "backend-ruff.log" \
  python -m ruff check \
    backend/app backend/tests backend/alembic/env.py backend/scripts \
    backend/reusable_data_fetcher.py \
    --config backend/pyproject.toml
run_check "Backend tests" "backend-tests.log" \
  python -m pytest -q backend/tests

run_check "Alembic upgrade" "alembic-upgrade.log" \
  bash -lc "cd backend && python -m alembic upgrade head"
run_check "Alembic downgrade" "alembic-downgrade.log" \
  bash -lc "cd backend && python -m alembic downgrade base"
run_check "Alembic rebuild" "alembic-rebuild.log" \
  bash -lc "cd backend && python -m alembic upgrade head"

if [[ "${RUN_LIVE_SMOKE:-false}" == "true" ]]; then
  run_check "TradingView live COMI smoke" "tradingview-live.log" \
    bash -lc "PYTHONPATH=backend python backend/scripts/tradingview_smoke.py"
else
  printf -- "- ⏭️ TradingView live COMI smoke skipped\n" >> "$SUMMARY_FILE"
fi

printf "\nAll logs were written under \`%s\` during this job.\n" "$CI_RESULTS_DIR" >> "$SUMMARY_FILE"
echo "Repository-local CI completed successfully."
