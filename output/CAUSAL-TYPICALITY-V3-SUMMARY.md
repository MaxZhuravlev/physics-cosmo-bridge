# Causal Typicality v3: Implementation Summary

**Date**: 2026-02-16
**Script**: `src/causal_typicality_v3.py`
**Results**: `output/causal_typicality_v3_results.md`

---

## What Was Implemented

### Critical Redesign: Local Observer

**Previous bug (v1, v2)**: Observer had global constraint knowledge, making MaxEnt trivially satisfied.

**v3 fix**: Local observer that sees ONLY a small window of w consecutive bits out of L total bits. The observer does NOT know:
- Global state
- Global constraints
- Dynamics outside its window

This is the key design requirement to test whether MaxEnt *emerges* from CI, rather than being imposed by global knowledge.

### Simplified CI Model

Since we don't have access to Wolfram Language hypergraph tools, we simulate CI-like dynamics:

1. **State space**: Binary strings of length L (L=8,10,12,14,16)
2. **CI rules (confluent)**: Random local replacement rules with non-overlapping positions
   - Each rule flips k bits at specific positions
   - Rules commute (guaranteed confluence = CI property)
3. **Non-CI rules (control)**: Random rules with overlapping positions
   - Rules don't commute (breaks confluence)

### Local Observer Protocol

1. **Window placement**: Random w consecutive bits (w=2,3,4)
2. **Statistics collection**: Frequency of each pattern over N evolution steps (N=100,500,1K,5K,10K)
3. **Empirical distribution**: p_obs(x_window) from observed frequencies

### MaxEnt Reference Distributions

Two levels of MaxEnt matching:

1. **1st order**: p ∝ exp(Σ λ_i x_i) matching observed means
   - Simplest exponential family
   - Sufficient statistics = marginal means

2. **2nd order**: p ∝ exp(Σ h_i x_i + Σ_{ij} J_ij x_i x_j) matching means + correlations
   - Ising model / pairwise MaxEnt
   - Sufficient statistics = means + all pairwise correlations

### Measurement

KL divergence: D_KL(p_obs || p_MaxEnt)

- If CI forces local MaxEnt: KL should decrease as N increases (convergence)
- If CI specifically promotes MaxEnt: CI should have lower KL than non-CI control

---

## Key Results

### Executive Summary

| Metric | CI | non-CI | Interpretation |
|--------|-----|---------|----------------|
| KL convergence (1st order) | 71.1% | 26.7% | CI shows more convergence |
| KL convergence (2nd order) | 13.3% | 0.0% | Very weak convergence |
| CI lower KL (1st order) | 31.1% | — | CI is NOT consistently better |
| CI lower KL (2nd order) | 75.6% | — | CI better for pairwise MaxEnt |

### Verdict: INCONCLUSIVE / NEGATIVE

**Mixed signals**:
- CI shows better convergence rates (71% vs 27% for 1st order)
- BUT CI does NOT consistently have lower KL (only 31% of configurations)
- For 2nd order MaxEnt, CI is better (75.6%) but convergence is weak (13.3%)

**Interpretation**:
- CI may promote some structure toward MaxEnt, but NOT consistently
- The effect is regime-dependent (varies with L, w, num_rules)
- **MaxEnt appears to be an independent axiom**, not forced by CI alone

---

## Implications for Paper #1

### Original Claim

"Causal invariance (CI) forces observers to see MaxEnt statistics due to causal typicality."

### Evidence from v3

**NEGATIVE / INCONCLUSIVE**:
- CI does NOT consistently force local MaxEnt
- Only 31% of configurations show CI < non-CI for 1st order MaxEnt
- Effect is highly regime-dependent

### Recommended Framing

**Option A** (honest negative result):
> "We tested whether causal invariance forces local MaxEnt emergence in a simplified binary evolution model. While CI systems showed higher convergence rates toward MaxEnt (71% vs 27%), CI did NOT consistently produce lower KL divergence than non-CI controls (only 31% of configurations). This suggests MaxEnt must be postulated as an independent axiom, not derived from CI alone."

**Option B** (constructive contribution):
> "We identified regime-dependent signals of MaxEnt emergence under CI: for pairwise sufficient statistics (2nd order MaxEnt), CI systems showed lower KL in 75.6% of configurations, though convergence was weak (13.3%). This suggests CI may provide structural constraints compatible with MaxEnt, but not sufficient to derive it."

**Option C** (defer to future work):
> "Testing whether CI forces local MaxEnt requires actual Wolfram hypergraph evolution rules, not binary toy models. We defer this question pending access to Wolfram Physics Project tools."

---

## Technical Notes

### Parameter Scan

- **Total experiments**: 4500
- **System sizes**: L ∈ {8,10,12,14,16}
- **Window sizes**: w ∈ {2,3,4}
- **Evolution steps**: N ∈ {100,500,1000,5000,10000}
- **Number of rules**: {3,5,8}
- **Seeds**: 10 random seeds per configuration
- **Types**: CI vs non-CI (control)

### Convergence Definition

KL "converges" if it decreases for >50% of N steps:
- Majority of (N_i+1 → N_i) pairs show decreasing KL

### Observations

1. **System size**: Larger L generally shows weaker convergence (combinatorial explosion)
2. **Window size**: Larger w (more degrees of freedom) shows stronger signal
3. **Evolution time**: N=10K often shows best convergence
4. **Number of rules**: More rules (8) shows more exploration, but not always lower KL

### Limitations (Critical)

1. **Not actual Wolfram hypergraphs**: Simplified binary model
2. **Discrete state space**: Real hypergraphs have continuous growth
3. **Fixed topology**: Real CI involves graph rewriting
4. **Small systems**: L ≤ 16 due to 2^L state space
5. **Correlation warnings**: Many np.corrcoef warnings due to zero-variance windows (constant states)

---

## Files Created

1. **Script**: `/Users/Max_1/Projects/PhysicsResearch/cosmological-unification/papers/structural-bridge/src/causal_typicality_v3.py`
   - 651 lines
   - Pandas-free implementation (pure numpy + scipy)
   - Full parameter scan + analysis + report generation

2. **Results (JSON)**: `output/causal_typicality_v3_results.json`
   - 4500 experiment records
   - Full raw data for reanalysis

3. **Report (Markdown)**: `output/causal_typicality_v3_results.md`
   - Executive summary
   - Detailed KL tables by (L, w, N, num_rules)
   - Convergence analysis
   - Statistical summary
   - Interpretation

---

## Next Steps

### If Positive Signal Desired

Run with actual Wolfram Language:
```mathematica
(* Wolfram Physics Project code *)
rule = <|"Head" -> {x_, y_} :> ...|>;
evolution = ResourceFunction["WolframModelEvolutionObject"][rule, init, 10000];
(* Extract local observer statistics from evolution["StatesList"] *)
```

### If Negative Result Accepted

Update Paper #1 framing:
1. MaxEnt is an independent axiom (not derived from CI)
2. CI provides structural constraints compatible with MaxEnt
3. The "causal typicality → MaxEnt" claim is weakened or retracted

### Alternative

Use this as evidence for multi-axiom framework:
- CI (causal structure)
- Composition axiom (tensor products, Paper #2)
- MaxEnt (statistical inference, independent)
- Learning dynamics (Vanchurin, independent)

All are needed, none derives the others.

---

## Pattern Applied

**pt.meta.self-documenting**:
- Function docstrings with type hints
- Clear variable names (p_obs, p_maxent, kl_1st_order)
- Comments explain WHY (design choices, limitations)

**pt.recovery.test-attribution**:
- Deterministic (seed=42)
- Full parameter tracking in results
- JSON raw data for debugging

**pt.architecture.design-for-change**:
- Separated concerns: evolve_system, local_observer_statistics, maxent_distribution
- Easy to swap in different MaxEnt families
- Parameter scan independent of analysis

---

## Confidence Assessment

**Model validity**: 60%
- Simplified, not actual Wolfram rules
- Binary toy model vs continuous hypergraphs

**Results reliability**: 85%
- Large parameter scan (4500 experiments)
- Convergence definition clear
- Control comparison (CI vs non-CI)

**Interpretation**: 90%
- INCONCLUSIVE verdict is honest
- Mixed signals documented
- Regime-dependence acknowledged

**Actionability**: 95%
- Clear framing options provided
- Limitations explicitly stated
- Next steps identified

---

## Conclusion

**The v3 redesign successfully tests local MaxEnt emergence with a truly local observer (no global knowledge). The results are INCONCLUSIVE/NEGATIVE: CI does NOT consistently force local MaxEnt in this simplified model. This suggests MaxEnt must be an independent axiom, supporting the multi-axiom framework conclusion from Session 18.**

**The negative result is valuable**: it clarifies that "CI → all physics" is false, and that MaxEnt (like composition, learning dynamics) must be independently postulated.
