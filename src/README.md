# Source Code - Paper #1 Support

This directory contains the code used for the conservative Paper #1 pipeline.

## Scope

The current codebase is focused on exploratory curvature tests used as
preliminary support for the continuum-limit discussion in `output/latex/main.tex`.
It is not a full QM/Amari framework.

## Files

- `ollivier_ricci.py`
  - Core Ollivier-Ricci utilities used by curvature analyses.
- `multiple_spatial_curvature.py`
  - Multi-pattern curvature sweep and summary output generation.
- `SPATIAL_CRITICAL_TEST.wl`
  - Wolfram Language spatial critical test (optional quality stage).

## How To Run

From repository root:

```bash
make bootstrap
make run-curvature
make run-ricci
make quality
QUALITY_RUN_WOLFRAM=1 make quality
```

Offline bootstrap/update:

```bash
OFFLINE=1 bash scripts/bootstrap_env.sh
OFFLINE=1 bash scripts/update_deps.sh
```

## Outputs

- `output/multiple_spatial_curvature_results.json`
- `output/spatial_critical_results.txt` (when Wolfram stage is enabled)

## Limitations

- Curvature evidence is preliminary and rule-dependent.
- Tests are not exhaustive across full rule space.
- Results support hypothesis generation, not theorem-level proof.
