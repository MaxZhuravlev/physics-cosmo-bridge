# CLAUDE.md — structural-bridge-via-uniqueness-theorems

> Conservative research workspace for a Lovelock-based synthesis bridge between Wolfram and Vanchurin cosmologies.

## IDENTITY

```yaml
project: "structural-bridge-via-uniqueness-theorems"
short_name: "wolfram-vanchurin-bridge"
type: theoretical-physics-research
level: L2-project

purpose: |
  Produce a conservative synthesis note (Paper #1) that connects
  Wolfram causal invariance and Vanchurin neural-network cosmology
  through Gorard 2020 + Lovelock 1971, with explicit assumptions.

primary_claim: |
  If the continuum-limit step is valid, then causal invariance may
  constrain the symmetry form of Vanchurin's Onsager tensor (Eq. 93).

non_claims:
  - "No new theorem is claimed"
  - "No formal proof of continuum limit is claimed"
  - "No full QM/Amari/arrow-of-time derivation in this paper"
```

## POSITION

```
PhysicsResearch/
└── cosmological-unification/
    └── structural-bridge-via-uniqueness-theorems/
        ├── CLAUDE.md
        ├── README.md
        ├── vos/
        │   ├── value-transformation.md
        │   ├── scope-boundaries.md
        │   └── integration-contract.md
        ├── src/
        ├── scripts/
        ├── output/
        │   └── latex/main.tex
        └── reviews/
```

## KEY FILES

1. `output/latex/main.tex` — submission manuscript (source of truth for claims)
2. `README.md` — practical project entrypoint
3. `vos/value-transformation.md` — value logic and deliverables
4. `vos/scope-boundaries.md` — explicit in/out scope
5. `vos/integration-contract.md` — guarantees and non-guarantees
6. `reviews/PEER_REVIEW_CRITICAL.md` — critical review baseline

## CORE ARGUMENT (PAPER #1)

```yaml
chain:
  - "Causal invariance -> discrete general covariance (Gorard 2020)"
  - "Assumed continuum limit -> diffeomorphism invariance"
  - "Lovelock theorem in D=4 -> Einstein form uniqueness class"
  - "Possible constraint on Vanchurin Eq. 93 symmetry structure"

numerical_support:
  - "Preliminary curvature evidence from spatial hypergraph tests"
  - "Evidence is suggestive, not a proof"
```

## CLAIM POLICY (STRICT)

- Use `may`, `could`, `potential`, `preliminary` for conditional steps.
- Never write unconditional statements about continuum-limit proof.
- Do not claim "5 theorems proven" in project-level docs.
- Keep exploratory QM/learning lines in archive/experience only.

## CURRENT STATUS

```yaml
status: "manuscript-ready, conservative synthesis"
last_major_update: "2026-02-15"

deliverables:
  - "Paper #1 LaTeX: output/latex/main.tex"
  - "Paper #1 PDF: output/latex/main.pdf"
  - "Curvature outputs: output/spatial_critical_results.txt"
  - "Curvature outputs: output/multiple_spatial_curvature_results.json"

quality:
  automation: "Makefile + scripts + CI workflow"
  command: "QUALITY_RUN_WOLFRAM=1 make quality"
```

## WORKING PROTOCOL

1. Read `output/latex/main.tex` before changing scientific claims.
2. Keep VOS documents synchronized with manuscript wording.
3. Treat numerical evidence as supportive, not definitive.
4. Record limitations and open problems explicitly.
5. Preserve reproducibility (scripts, deterministic outputs, clear commands).

## NEXT PRIORITIES

1. Final proofreading and bibliography polish for submission.
2. Scale studies for curvature across broader rule families.
3. Formal work on discrete-covariance -> diffeomorphism step.
4. Optional future paper for QM/operational track in separate scope.

## META

```yaml
created: 2026-02-13
updated: 2026-02-15
follows: "@uu Knowledge Pyramid (minimal)"
```
