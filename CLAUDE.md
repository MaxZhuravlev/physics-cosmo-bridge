# CLAUDE.md — structural-bridge-via-uniqueness-theorems

> Reframed: Honest negative result about the Lovelock bridge + constructive Type II contributions.

## IDENTITY

```yaml
project: "structural-bridge-via-uniqueness-theorems"
short_name: "lovelock-bridge-reframed"
type: theoretical-physics-research
level: L2-project

purpose: |
  Paper #1 of the Cosmological Unification Program.
  REFRAMED (Session 20, 2026-02-16) from original Lovelock bridge
  synthesis into a two-part paper:
  Part I: Why the Lovelock bridge fails (negative results)
  Part II: Constructive Type II metric theory contributions

title: |
  "Where the Lovelock Bridge Breaks: Negative Results and New
  Directions for Connecting Discrete and Continuous Spacetime Emergence"

primary_claims:
  negative:
    - "Continuum limit falsified numerically for all dynamically interesting rules"
    - "Discrete-to-continuous symmetry barrier is fundamental"
    - "Vanchurin Type II bypasses the continuum limit entirely"
    - "Lovelock chain end-to-end probability: ~1%"
  constructive:
    - "Critical beta formula for Lorentzian-Riemannian transition"
    - "M = F^2 for exponential family models"
    - "PSD obstruction: standard M cannot produce Lorentzian signature"
    - "Signed-edge construction (H1') vs Vanchurin non-principal sqrt"
    - "Regime identification: natural gradient = alpha=1 in Type II"

non_claims:
  - "No claim that signed-edge construction is physically derived"
  - "No claim that Type II results supersede Vanchurin's work"
  - "No cross-program correlation (rho=0.47 retracted as spurious)"
  - "No claim about continuum limit being resolvable"

reframe_history: |
  Original (2026-02-13): Conservative Lovelock bridge synthesis note
  Crisis (2026-02-15): Vanchurin feedback + our own numerical falsification
  Reframe (2026-02-16): Option A — negative results + constructive Type II
  Decision basis: Weighted score 7.65/10 vs 3.70 (as-is) vs 6.45 (merge)
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
2. `output/latex/references.bib` — bibliography
3. `README.md` — practical project entrypoint
4. `vos/value-transformation.md` — value logic and deliverables

## CORE ARGUMENT (REFRAMED PAPER #1)

```yaml
part_I_negative:
  chain_examined:
    - "CI -> discrete covariance (Gorard 2020, THEOREM)"
    - "discrete covariance -> [continuum limit] -> diffeomorphism invariance (FALSIFIED)"
    - "diffeomorphism invariance -> Lovelock (D=4) -> Einstein (THEOREM, but assumptions unmet)"
  findings:
    - "13 rules tested: 0/6 expanding rules converge to nonzero curvature"
    - "kappa ~ 1/N for all dynamically interesting rules"
    - "Discrete permutation symmetry ≠ continuous Lorentz group"
    - "End-to-end probability: ~1%"

part_II_constructive:
  results:
    - "PSD obstruction theorem (confidence: 98%)"
    - "Critical beta formula: beta_c = -d_1 where d_1 = min eigenvalue of F^{-1/2}M^{H1'}F^{-1/2}"
    - "M = F^2 for exponential family (confidence: 90%)"
    - "Spectral purity condition under SRC (confidence: 85%)"
    - "H1' vs non-principal sqrt non-equivalence (confidence: 80%)"
    - "Regime identification: natural gradient = alpha=1 (confidence: 85%)"

novelty_estimate: "25-30%"
  negative_results: "10-15%"
  mass_fisher_structure: "10%"
  lorentzian_mechanism: "15-20%"
```

## CLAIM POLICY (STRICT)

- Continuum limit is FALSIFIED, not "unproven" or "open"
- Negative results are contributions, not failures
- Type II results are "contributions within Vanchurin's framework"
- Signed-edge construction is imposed, not derived
- Golden ratio / alpha_opt results belong to Paper #3, NOT here
- State confidence levels for all non-trivial claims
- Use conditional framing: "IF Model A governs..." / "conditional on..."

## CURRENT STATUS

```yaml
status: "major-rewrite-in-progress"
last_major_update: "2026-02-16"
reframe_decision: "Option A (weighted score 7.65/10)"

deliverables:
  - "Paper #1 LaTeX: output/latex/main.tex"
  - "Paper #1 bibliography: output/latex/references.bib"

source_documents:
  - "experience/insights/PAPER1-REFRAME-STRATEGY-2026-02-16.md"
  - "experience/insights/CROSS-PROGRAM-PREDICTION-FORMAL-ANALYSIS-2026-02-16.md"
  - "experience/insights/LORENTZIAN-MECHANISM-FORMAL-ANALYSIS-2026-02-16.md"
  - "experience/insights/MASS-TENSOR-FORMAL-ANALYSIS-2026-02-16.md"
  - "experience/insights/TYPE-II-FRAMEWORK-INTEGRATION.md"
  - "experience/insights/SCALING-STUDY-RESULTS.md (in operational-qm/output/)"
```

## WORKING PROTOCOL

1. Read `output/latex/main.tex` before changing scientific claims.
2. All negative results must cite specific evidence (13 rules, kappa~1/N, etc.).
3. All constructive results must state their confidence level.
4. Do not mix Paper #3 results (alpha_opt, convergence theorem) into this paper.
5. Maintain cross-references to companion papers (Paper #3 amari-chain).
6. Preserve reproducibility (scripts, deterministic outputs, clear commands).

## NEXT PRIORITIES

1. Complete major rewrite following Option A structure.
2. Adversarial review of rewritten manuscript.
3. Prepare figures (bridge diagram, curvature convergence, phase diagram).
4. Final proofread and bibliography normalization.
5. arXiv submission.

## META

```yaml
created: 2026-02-13
updated: 2026-02-16
reframed: 2026-02-16 (Session 20)
follows: "@uu Knowledge Pyramid (minimal)"
```
