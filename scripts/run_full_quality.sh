#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-$ROOT_DIR/.venv}"
PYTHON="$VENV_DIR/bin/python"

if [[ ! -x "$PYTHON" ]]; then
  echo "[quality] Python venv not found. Bootstrapping..."
  bash "$ROOT_DIR/scripts/bootstrap_env.sh"
fi

echo "[quality] running Python static compile checks..."
"$PYTHON" -m py_compile "$ROOT_DIR/src/multiple_spatial_curvature.py" "$ROOT_DIR/src/ollivier_ricci.py"

echo "[quality] running curvature suite..."
"$PYTHON" "$ROOT_DIR/src/multiple_spatial_curvature.py"

echo "[quality] running ricci sanity test..."
"$PYTHON" "$ROOT_DIR/src/ollivier_ricci.py"

WOLFRAM_KERNEL="${WOLFRAM_KERNEL:-/Applications/Wolfram Engine.app/Contents/MacOS/WolframKernel}"
if [[ "${QUALITY_RUN_WOLFRAM:-0}" == "1" ]]; then
  if command -v wolframscript >/dev/null 2>&1 && [[ -x "$WOLFRAM_KERNEL" ]]; then
    echo "[quality] wolframscript found. Checking activation..."
    if wolframscript -l "$WOLFRAM_KERNEL" -code 'Quit[]' >/dev/null 2>&1; then
      echo "[quality] running Wolfram critical test..."
      wolframscript -l "$WOLFRAM_KERNEL" -file "$ROOT_DIR/src/SPATIAL_CRITICAL_TEST.wl" > "$ROOT_DIR/output/spatial_critical_results.txt" 2>&1
    else
      echo "[quality] Wolfram kernel is not activated/configured. Skipping Wolfram run."
      echo "          Activate with: wolframscript -activate"
    fi
  else
    echo "[quality] wolframscript or Wolfram kernel not found. Skipping Wolfram run."
  fi
else
  echo "[quality] Wolfram test skipped by default."
  echo "          Run with QUALITY_RUN_WOLFRAM=1 make quality"
fi

if command -v pdflatex >/dev/null 2>&1; then
  echo "[quality] pdflatex found. Building LaTeX..."
  (
    cd "$ROOT_DIR/output/latex"
    pdflatex -interaction=nonstopmode -halt-on-error main.tex
  )
elif command -v tectonic >/dev/null 2>&1; then
  echo "[quality] pdflatex not found. Building LaTeX via tectonic..."
  (
    cd "$ROOT_DIR/output/latex"
    tectonic --keep-logs main.tex
  )
else
  echo "[quality] No LaTeX engine found (pdflatex/tectonic). Skipping LaTeX build."
fi

echo "[quality] done."
