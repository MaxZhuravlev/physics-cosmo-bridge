# Next Falsifiable Experiments (High ROI)

These are the highest-leverage checks to improve scientific reliability,
not just software quality.

## 1) CI-Conditioned Rule-Space Audit

Question:
- Does non-trivial curvature persist in a broad sample when rules are stratified
  by causal-invariance status?

Protocol:
- Sample large rule families with fixed random seed and preregistered bins.
- Split into CI-satisfying vs CI-breaking classes.
- Compare curvature distributions with the same metrics and sample sizes.

Pass condition:
- CI class remains statistically shifted from flat controls after correction.

Fail condition:
- Signal vanishes under unbiased sampling, implying current evidence is mostly selection.

## 2) Scale Trajectory Test (N-growth)

Question:
- Does mean curvature remain non-trivial as system size increases?

Protocol:
- For each selected rule, run N-grid (e.g., 10^2, 10^3, 10^4 where feasible).
- Estimate trend and confidence intervals for mean/variance of kappa.

Pass condition:
- Non-zero signal remains bounded away from 0 on at least a subset of CI rules.

Fail condition:
- Signal collapses toward 0 systematically with scale.

## 3) Counterexample Search for Bridge Fragility

Question:
- Can we find CI-compatible systems that break the expected bridge constraints?

Protocol:
- Search for CI-satisfying constructions with near-flat curvature and/or
  incompatible effective gravitational behavior.
- Treat one robust counterexample as a critical falsification event for strong claims.

Pass condition:
- No counterexamples found in preregistered search budget.

Fail condition:
- Counterexample found; bridge claim must be narrowed.

## Output Discipline

- Every run writes machine-readable artifacts.
- Negative results are first-class outputs, not hidden.
- Claims in manuscript update only after thresholded tests pass.
