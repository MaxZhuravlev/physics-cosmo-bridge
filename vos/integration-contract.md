# Integration Contract — structural-bridge-via-uniqueness-theorems

> What this project guarantees to consumers.

## INTERFACES

```yaml
I1_manuscript_interface:
  format: "LaTeX/PDF"
  paths:
    - "output/latex/main.tex"
    - "output/latex/main.pdf"
  guarantee: "Conservative synthesis claims consistent with cited sources"

I2_reproducibility_interface:
  format: "Make targets + scripts"
  paths:
    - "Makefile"
    - "scripts/bootstrap_env.sh"
    - "scripts/run_full_quality.sh"
  guarantee: "Single-command quality run with optional Wolfram stage"

I3_data_interface:
  format: "Text/JSON outputs"
  paths:
    - "output/spatial_critical_results.txt"
    - "output/multiple_spatial_curvature_results.json"
  guarantee: "Artifacts match current code paths and can be regenerated"
```

## GUARANTEES

```yaml
scientific_integrity:
  - "No unconditional claim where assumptions are unresolved"
  - "Known limitations remain explicit"
  - "Project docs stay synchronized with main.tex"

engineering_quality:
  - "Repository has automated quality gate"
  - "Core scripts support offline bootstrap/update mode"
```

## NON-GUARANTEES

```yaml
not_guaranteed:
  - "Formal proof of continuum limit"
  - "Journal acceptance or external endorsement"
  - "Completion of QM/Amari program inside Paper #1 scope"
  - "Universality of curvature behavior across full rule space"
```
