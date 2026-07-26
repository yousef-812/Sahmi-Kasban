#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="${GITHUB_WORKSPACE:-$(cd "$(dirname "$0")/../../.." && pwd)}"
PIP_CACHE_DIR="${PIP_CACHE_DIR:-$ROOT_DIR/.github/.cache/pip}"
CI_RESULTS_DIR="${CI_RESULTS_DIR:-$ROOT_DIR/.github/.ci-results}"
SUMMARY_FILE="${GITHUB_STEP_SUMMARY:-$CI_RESULTS_DIR/summary.md}"
RUN_MODE="${RUN_MODE:-tests}"

mkdir -p "$PIP_CACHE_DIR" "$CI_RESULTS_DIR"
export PIP_CACHE_DIR
cd "$ROOT_DIR"

run_check() {
  local label="$1"
  local log_name="$2"
  shift 2

  local log_path="$CI_RESULTS_DIR/$log_name"
  echo "::group::$label"

  set +e
  "$@" >"$log_path" 2>&1
  local status=$?
  set -e

  if [[ $status -eq 0 ]]; then
    echo "$label passed."
    printf -- "- ✅ %s\n" "$label" >> "$SUMMARY_FILE"
  else
    echo "::error::$label failed with exit code $status"
    echo "----- failure output: $log_name -----"
    tail -n 160 "$log_path"
    echo "----- end failure output -----"
    printf -- "- ❌ %s — exit code %s\n" "$label" "$status" >> "$SUMMARY_FILE"
  fi

  echo "::endgroup::"
  return "$status"
}

case "$RUN_MODE" in
  lint|tests) ;;
  *)
    echo "Unsupported RUN_MODE: $RUN_MODE" >&2
    exit 2
    ;;
esac

printf "## Sahmi Kasban repository-local CI\n\n" > "$SUMMARY_FILE"
printf "Mode: \`%s\`\n\n" "$RUN_MODE" >> "$SUMMARY_FILE"
printf "Cache directory: \`%s\`\n\n" "$PIP_CACHE_DIR" >> "$SUMMARY_FILE"

python - <<'PY'
import sys

if sys.version_info < (3, 11):
    raise SystemExit(f"Python 3.11+ is required, found {sys.version}")
print(f"Using Python {sys.version.split()[0]}")
PY

run_check "Install Python dependencies" "install.log" \
  python -m pip install --quiet --upgrade pip
run_check "Install project packages" "install-project.log" \
  python -m pip install --quiet -e ".[dev]" -e "backend[dev]"

if [[ "$RUN_MODE" == "lint" ]]; then
  run_check "Repository secret gate" "security-gate.log" \
    python backend/scripts/security_gate.py
  run_check "Backend high-severity Bandit" "backend-bandit.log" \
    python -m bandit -q -r backend/app -lll
  run_check "Core compile" "core-compile.log" \
    python -m compileall -q src tests
  run_check "Core Ruff" "core-ruff.log" \
    python -m ruff check src tests --output-format concise

  run_check "Backend compile" "backend-compile.log" \
    python -m compileall -q \
      backend/app backend/tests backend/alembic backend/scripts \
      backend/reusable_data_fetcher.py
  run_check "Backend Ruff" "backend-ruff.log" \
    python -m ruff check \
      backend/app backend/tests backend/alembic/env.py backend/scripts \
      backend/reusable_data_fetcher.py \
      --config backend/pyproject.toml \
      --output-format concise

  printf "\nLint logs were written under \`%s\`.\n" "$CI_RESULTS_DIR" >> "$SUMMARY_FILE"
  echo "Repository-local lint completed successfully."
  exit 0
fi

run_check "Python dependency audit" "dependency-audit.log" \
  python -m pip_audit --local --skip-editable
run_check "Core tests" "core-tests.log" \
  python -m pytest -q --tb=short tests
run_check "Backend tests" "backend-tests.log" \
  python -m pytest -q --tb=short backend/tests
run_check "Backend concurrent load smoke" "backend-load-smoke.log" \
  bash -lc "PYTHONPATH=backend python backend/scripts/load_quality_smoke.py"

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

printf "\nTest logs were written under \`%s\`.\n" "$CI_RESULTS_DIR" >> "$SUMMARY_FILE"
echo "Repository-local tests completed successfully."
