# Wolfram-Vanchurin Bridge (Paper #1)

Conservative synthesis project connecting Wolfram causal-invariance physics and
Vanchurin neural-network cosmology via Lovelock's uniqueness theorem.

## Current Status

- Manuscript: `output/latex/main.tex`
- PDF: `output/latex/main.pdf`
- Quality automation: `Makefile`, `scripts/`, `.github/workflows/quality.yml`
- Scientific posture: conditional and skeptical (no overclaiming)

## Main Claim (Conservative)

The paper argues that if the continuum-limit step is valid, then the chain

`causal invariance -> discrete covariance -> diffeomorphism invariance -> Lovelock`

may constrain the symmetry structure of Vanchurin's Onsager tensor (Eq. 93).

## What This Project Does Not Claim

- No new theorem is proven.
- Continuum limit is not rigorously proven.
- No complete QM/Amari/arrow-of-time derivation is claimed in Paper #1.
- Numerical evidence is preliminary and potentially selection-biased.

## Repository Layout

- `output/latex/main.tex` - source-of-truth manuscript
- `output/latex/main.pdf` - compiled manuscript
- `src/` - curvature code used by Paper #1 support tests
- `scripts/` - bootstrap/update/quality scripts
- `vos/` - project value, scope, and integration contracts
- `reviews/` - critical review artifacts
- `experience/` - research history and lessons learned
- `archive/` - superseded materials retained for traceability

## Quick Start

```bash
# 1) Create/update local environment
make bootstrap

# 2) Run full local quality gate (Python + LaTeX)
make quality

# 3) Include Wolfram critical stage (optional)
QUALITY_RUN_WOLFRAM=1 make quality
```

Offline mode:

```bash
OFFLINE=1 bash scripts/bootstrap_env.sh
OFFLINE=1 bash scripts/update_deps.sh
```

## Quality Gate

`make quality` runs the reproducibility checks and manuscript build pipeline.
With `QUALITY_RUN_WOLFRAM=1`, it additionally runs
`src/SPATIAL_CRITICAL_TEST.wl` and refreshes spatial artifacts.

## Scientific Limitations

- Continuum limit remains an open problem.
- D=4 assumption is observationally motivated, not derived.
- Current curvature dataset is finite and spatial-rule focused.

These limits are explicit in `output/latex/main.tex` and must remain explicit
in all project-level docs.

## Primary References

- Gorard, J. (2020). Complex Systems 29(2), 599-654.
- Lovelock, D. (1971). Journal of Mathematical Physics 12(3), 498-501.
- Vanchurin, V. (2020). Entropy 22(11), 1210.

## Citation Placeholder

Until formal submission metadata is finalized, cite the manuscript path directly:

`output/latex/main.tex` (Working manuscript, February 2026).
