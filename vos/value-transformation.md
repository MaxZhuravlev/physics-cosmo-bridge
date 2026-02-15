# Value Transformation — structural-bridge-via-uniqueness-theorems

> What value this project creates and how it creates it.

## VALUE FORMULA

```yaml
FROM:
  - "Two independent cosmology programs with no explicit bridge"
  - "Open question in Vanchurin 2020 (§9): first-principles origin of Onsager symmetries"
  - "Fragmented evidence across literature and code"

TO:
  - "Conservative synthesis note linking Wolfram and Vanchurin through Lovelock"
  - "Explicit conditional answer: Onsager symmetries may be constrained if continuum limit holds"
  - "Reproducible numerical appendix with clear caveats"

VIA:
  - "Literature chain: Gorard 2020 + Lovelock 1971 + Vanchurin 2020"
  - "Curvature experiments (Python + Wolfram) as preliminary support"
  - "Strict claim discipline and explicit limitations"
```

## TERMINAL VALUE

```yaml
primary_output: "Paper #1 conservative manuscript (output/latex/main.tex)"
scientific_value: |
  The contribution is synthesis and clarification: it makes a possible
  structural bridge explicit, states assumptions openly, and identifies
  where formal work is still required.

who_benefits:
  - "Researchers in Wolfram Physics"
  - "Researchers in neural-network cosmology"
  - "Reviewers who need a concise, auditable bridge argument"
```

## DELIVERABLES

```yaml
D1_manuscript:
  format: "LaTeX + PDF"
  path: "output/latex/main.tex"
  status: ready_for_review

D2_reproducible_results:
  format: "Text/JSON artifacts"
  paths:
    - "output/spatial_critical_results.txt"
    - "output/multiple_spatial_curvature_results.json"
  status: available

D3_quality_automation:
  format: "Makefile + scripts + CI workflow"
  paths:
    - "Makefile"
    - "scripts/run_full_quality.sh"
    - ".github/workflows/quality.yml"
  status: active
```

## SUCCESS CRITERIA

```yaml
correctness:
  - "No project-level claim contradicts output/latex/main.tex"
  - "Assumptions are explicit (continuum limit, D=4)"
  - "References are accurate and traceable"

reproducibility:
  - "make quality passes locally"
  - "QUALITY_RUN_WOLFRAM=1 make quality passes when Wolfram is available"

integrity:
  - "No unconditional language for conditional steps"
  - "Limitations section remains explicit and central"
```
