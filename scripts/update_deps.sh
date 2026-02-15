#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-$ROOT_DIR/.venv}"
PIP_ARGS=()

if [[ "${OFFLINE:-0}" == "1" ]]; then
  PIP_ARGS+=(--no-index)
  echo "[update-deps] OFFLINE=1 -> using --no-index"
fi

if [[ ! -x "$VENV_DIR/bin/pip" ]]; then
  echo "[update-deps] venv not found at $VENV_DIR"
  echo "[update-deps] run: bash scripts/bootstrap_env.sh"
  exit 1
fi

if [[ "${OFFLINE:-0}" != "1" ]]; then
  "$VENV_DIR/bin/python" -m pip install --upgrade pip
else
  echo "[update-deps] OFFLINE=1 -> skip pip self-upgrade"
fi
"$VENV_DIR/bin/pip" install --upgrade "${PIP_ARGS[@]}" -r "$ROOT_DIR/requirements.txt"

echo "[update-deps] dependencies upgraded."
