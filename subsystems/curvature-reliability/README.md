# Curvature Reliability Subsystem

This subsystem hardens the "solid" part of Paper #1 by adding explicit,
machine-checkable acceptance criteria for curvature evidence and claim hygiene.

## Scope

- In scope:
  - multi-pattern curvature robustness checks
  - alpha-sensitivity sweep (`alpha = 0.25, 0.50, 0.75`)
  - 1D-like control diagnostic constraint
  - overclaim phrase detection in live project files

- Out of scope:
  - formal proof of continuum limit
  - theorem-level derivations
  - non-gravity sectors (QM/Amari/arrow)

## Gate Definition

The gate is implemented in `src/curvature_reliability_gate.py` and is executed by:

```bash
make quality
```

A run fails if any of the following fails:
- insufficient significant patterns in alpha sweep
- low overall mean curvature signal
- 1D-control mean outside tolerance
- banned overclaim phrase found in live files

## Outputs

- `output/curvature_reliability_report.json`

This artifact is designed for auditability and skeptical review.
