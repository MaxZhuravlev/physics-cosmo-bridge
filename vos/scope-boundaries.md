# Scope Boundaries — structural-bridge-via-uniqueness-theorems

> Explicit scope for Paper #1 (conservative synthesis).

## IN SCOPE

```yaml
inputs:
  - "Gorard 2020: causal invariance <-> discrete general covariance"
  - "Lovelock 1971: uniqueness class in D=4"
  - "Vanchurin 2020: Onsager tensor motivation and open question"
  - "Project curvature artifacts (Python/Wolfram) as preliminary evidence"

processing:
  - "Formal synthesis chain and assumption bookkeeping"
  - "Critical wording review to prevent overclaiming"
  - "Reproducibility pipeline maintenance"

outputs:
  - "Conservative manuscript: output/latex/main.tex"
  - "Compiled PDF: output/latex/main.pdf"
  - "Quality artifacts and run scripts"
```

## OUT OF SCOPE

```yaml
excluded_for_paper1:
  - "Claiming new foundational theorems"
  - "Claiming rigorous proof of continuum limit"
  - "Claiming complete QM derivation"
  - "Claiming Amari-chain completeness in this manuscript"
  - "Claiming arrow-of-time proof from this project state"

methodological_exclusions:
  - "Cosmological-scale empirical simulation"
  - "Exhaustive rule-space proof across all Wolfram rules"
```

## DEPENDENCIES

```yaml
required:
  - "Python 3.10+ with dependencies from requirements.txt"
  - "LaTeX toolchain (tectonic preferred)"

optional:
  - "Wolfram Engine (for spatial critical test)"
```

## HARD CONSTRAINTS

```yaml
scientific:
  - "Continuum limit remains open"
  - "D=4 is assumed, not derived"
  - "Current curvature tests are limited and potentially selection-biased"

quality:
  - "All core docs must align with main.tex language"
  - "Claims must remain conditional where assumptions are unresolved"
```
