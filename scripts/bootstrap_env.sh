#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-$ROOT_DIR/.venv}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
PIP_ARGS=()

if [[ "${OFFLINE:-0}" == "1" ]]; then
  PIP_ARGS+=(--no-index)
  echo "[bootstrap] OFFLINE=1 -> using --no-index"
fi

echo "[bootstrap] root: $ROOT_DIR"
echo "[bootstrap] venv: $VENV_DIR"

"$PYTHON_BIN" -m venv "$VENV_DIR"
if [[ "${OFFLINE:-0}" != "1" ]]; then
  "$VENV_DIR/bin/python" -m pip install --upgrade pip
else
  echo "[bootstrap] OFFLINE=1 -> skip pip self-upgrade"
fi
"$VENV_DIR/bin/pip" install "${PIP_ARGS[@]}" -r "$ROOT_DIR/requirements.txt"

KERNEL_CANDIDATE="/Applications/Wolfram Engine.app/Contents/MacOS/WolframKernel"
if [[ -x "$KERNEL_CANDIDATE" ]]; then
  echo "[bootstrap] Wolfram kernel detected: $KERNEL_CANDIDATE"
  echo "[bootstrap] Tip: export WOLFRAMSCRIPT_KERNELPATH='$KERNEL_CANDIDATE'"
fi

echo "[bootstrap] done."
