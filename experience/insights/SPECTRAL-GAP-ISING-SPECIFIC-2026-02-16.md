# Spectral Gap Analysis: Ising Fisher Matrices

**Date:** 2026-02-16
**Attribution:** TEST-BRIDGE-MVP1-SPECTRAL-GAP-ISING-001

## Research Question

Do ISING FISHER MATRICES exhibit spectral gap weighting W(q) = beta_c(q) * L_gap(q) that favors q=1 (Lorentzian signature) over higher q values?

## Method

1. Compute exact Ising Fisher matrices for various graph topologies
2. For each q from 1 to m-1:
   - beta_c(q) = max over sign assignments with q negative of [-min_eig(F^{1/2}SF^{1/2})]
   - L_gap(q) = (d_2 - d_1)/|d_1| at optimal sign assignment
   - W(q) = beta_c(q) * L_gap(q)
3. Check if W(q=1) > max W(q>=2)

## Summary

**Total cases:** 70
**Cases where q=1 wins:** 63 (90.0%)

**CONCLUSION:** Ising Fisher matrices DO favor q=1 in most cases.

## Detailed Results

| Graph | N | m | J | q_win | W(q=1) | max W(q>=2) | q=1 wins? |
|-------|---|---|---|-------|--------|-------------|----------|
| complete_K3 | 3 | 3 | 0.10 | 1 | 1.8693 | 0.1858 | YES |
| complete_K3 | 3 | 3 | 0.30 | 1 | 1.4415 | 0.4080 | YES |
| complete_K3 | 3 | 3 | 0.50 | 1 | 0.9267 | 0.3935 | YES |
| complete_K3 | 3 | 3 | 0.80 | 1 | 0.3644 | 0.1980 | YES |
| complete_K3 | 3 | 3 | 1.00 | 1 | 0.1762 | 0.1019 | YES |
| complete_K4 | 4 | 6 | 0.10 | 1 | 1.7557 | 0.3615 | YES |
| complete_K4 | 4 | 6 | 0.30 | 1 | 1.0312 | 0.8736 | YES |
| complete_K4 | 4 | 6 | 0.50 | 5 | 0.3938 | 0.5882 | NO |
| complete_K4 | 4 | 6 | 0.80 | 5 | 0.0592 | 0.1202 | NO |
| complete_K4 | 4 | 6 | 1.00 | 5 | 0.0155 | 0.0348 | NO |
| complete_K5 | 5 | 10 | 0.10 | 1 | 1.7163 | 0.5909 | YES |
| complete_K5 | 5 | 10 | 0.30 | 9 | 0.7167 | 1.3610 | NO |
| complete_K5 | 5 | 10 | 0.50 | 9 | 0.1299 | 0.4473 | NO |
| complete_K5 | 5 | 10 | 0.80 | 9 | 0.0061 | 0.0335 | NO |
| complete_K5 | 5 | 10 | 1.00 | 6 | 0.0008 | 0.0061 | NO |
| path_P4 | 4 | 3 | 0.10 | 1 | 1.9801 | 0.0000 | YES |
| path_P4 | 4 | 3 | 0.30 | 1 | 1.8303 | 0.0000 | YES |
| path_P4 | 4 | 3 | 0.50 | 1 | 1.5729 | 0.0000 | YES |
| path_P4 | 4 | 3 | 0.80 | 1 | 1.1181 | 0.0000 | YES |
| path_P4 | 4 | 3 | 1.00 | 1 | 0.8399 | 0.0000 | YES |
| path_P5 | 5 | 4 | 0.10 | 1 | 1.9801 | 0.0000 | YES |
| path_P5 | 5 | 4 | 0.30 | 1 | 1.8303 | 0.0000 | YES |
| path_P5 | 5 | 4 | 0.50 | 1 | 1.5729 | 0.0000 | YES |
| path_P5 | 5 | 4 | 0.80 | 1 | 1.1181 | 0.0000 | YES |
| path_P5 | 5 | 4 | 1.00 | 1 | 0.8399 | 0.0000 | YES |
| path_P6 | 6 | 5 | 0.10 | 1 | 1.9801 | 0.0000 | YES |
| path_P6 | 6 | 5 | 0.30 | 1 | 1.8303 | 0.0000 | YES |
| path_P6 | 6 | 5 | 0.50 | 1 | 1.5729 | 0.0000 | YES |
| path_P6 | 6 | 5 | 0.80 | 1 | 1.1181 | 0.0000 | YES |
| path_P6 | 6 | 5 | 1.00 | 1 | 0.8399 | 0.0000 | YES |
| star_S4 | 4 | 3 | 0.10 | 1 | 1.9801 | 0.0000 | YES |
| star_S4 | 4 | 3 | 0.30 | 1 | 1.8303 | 0.0000 | YES |
| star_S4 | 4 | 3 | 0.50 | 1 | 1.5729 | 0.0000 | YES |
| star_S4 | 4 | 3 | 0.80 | 1 | 1.1181 | 0.0000 | YES |
| star_S4 | 4 | 3 | 1.00 | 1 | 0.8399 | 0.0000 | YES |
| star_S5 | 5 | 4 | 0.10 | 1 | 1.9801 | 0.0000 | YES |
| star_S5 | 5 | 4 | 0.30 | 1 | 1.8303 | 0.0000 | YES |
| star_S5 | 5 | 4 | 0.50 | 1 | 1.5729 | 0.0000 | YES |
| star_S5 | 5 | 4 | 0.80 | 1 | 1.1181 | 0.0000 | YES |
| star_S5 | 5 | 4 | 1.00 | 1 | 0.8399 | 0.0000 | YES |
| star_S6 | 6 | 5 | 0.10 | 1 | 1.9801 | 0.0000 | YES |
| star_S6 | 6 | 5 | 0.30 | 1 | 1.8303 | 0.0000 | YES |
| star_S6 | 6 | 5 | 0.50 | 1 | 1.5729 | 0.0000 | YES |
| star_S6 | 6 | 5 | 0.80 | 1 | 1.1181 | 0.0000 | YES |
| star_S6 | 6 | 5 | 1.00 | 1 | 0.8399 | 0.0000 | YES |
| cycle_C4 | 4 | 4 | 0.10 | 1 | 1.9699 | 0.0291 | YES |
| cycle_C4 | 4 | 4 | 0.30 | 1 | 1.7254 | 0.2026 | YES |
| cycle_C4 | 4 | 4 | 0.50 | 1 | 1.2772 | 0.3357 | YES |
| cycle_C4 | 4 | 4 | 0.80 | 1 | 0.5880 | 0.2579 | YES |
| cycle_C4 | 4 | 4 | 1.00 | 1 | 0.3004 | 0.1510 | YES |
| cycle_C5 | 5 | 5 | 0.10 | 1 | 1.9791 | 0.0039 | YES |
| cycle_C5 | 5 | 5 | 0.30 | 1 | 1.8010 | 0.0816 | YES |
| cycle_C5 | 5 | 5 | 0.50 | 1 | 1.4388 | 0.2260 | YES |
| cycle_C5 | 5 | 5 | 0.80 | 1 | 0.7523 | 0.2673 | YES |
| cycle_C5 | 5 | 5 | 1.00 | 1 | 0.4065 | 0.1813 | YES |
| cycle_C6 | 6 | 6 | 0.10 | 1 | 1.9800 | 0.0005 | YES |
| cycle_C6 | 6 | 6 | 0.30 | 1 | 1.8219 | 0.0300 | YES |
| cycle_C6 | 6 | 6 | 0.50 | 1 | 1.5120 | 0.1360 | YES |
| cycle_C6 | 6 | 6 | 0.80 | 1 | 0.8694 | 0.2460 | YES |
| cycle_C6 | 6 | 6 | 1.00 | 1 | 0.4956 | 0.1954 | YES |
| random_ER5_0.5 | 5 | 4 | 0.10 | 1 | 1.9801 | 0.0000 | YES |
| random_ER5_0.5 | 5 | 4 | 0.30 | 1 | 1.8303 | 0.0000 | YES |
| random_ER5_0.5 | 5 | 4 | 0.50 | 1 | 1.5729 | 0.0000 | YES |
| random_ER5_0.5 | 5 | 4 | 0.80 | 1 | 1.1181 | 0.0000 | YES |
| random_ER5_0.5 | 5 | 4 | 1.00 | 1 | 0.8399 | 0.0000 | YES |
| random_ER6_0.5 | 6 | 6 | 0.10 | 1 | 1.9702 | 0.0389 | YES |
| random_ER6_0.5 | 6 | 6 | 0.30 | 1 | 1.7466 | 0.2802 | YES |
| random_ER6_0.5 | 6 | 6 | 0.50 | 1 | 1.3780 | 0.4832 | YES |
| random_ER6_0.5 | 6 | 6 | 0.80 | 1 | 0.8207 | 0.3864 | YES |
| random_ER6_0.5 | 6 | 6 | 1.00 | 1 | 0.5520 | 0.2516 | YES |

## Pattern Analysis

### By Graph Topology

| Topology | q=1 wins | Total | Percentage |
|----------|----------|-------|------------|
| complete | 8 | 15 | 53.3% |
| cycle | 15 | 15 | 100.0% |
| path | 15 | 15 | 100.0% |
| random | 10 | 10 | 100.0% |
| star | 15 | 15 | 100.0% |

### By Coupling Strength

| J | q=1 wins | Total | Percentage |
|---|----------|-------|------------|
| 0.1 | 14 | 14 | 100.0% |
| 0.3 | 13 | 14 | 92.9% |
| 0.5 | 12 | 14 | 85.7% |
| 0.8 | 12 | 14 | 85.7% |
| 1.0 | 12 | 14 | 85.7% |

## Interpretation

The Ising Fisher matrices show MODERATE EVIDENCE FOR the Lorentzian selection hypothesis in most (but not all) cases.

**Implication:** The specific structure of Ising Fisher matrices (covariance of spin products) may provide some bias toward q=1, though exceptions exist.

## Next Steps

- Investigate which graph properties correlate with q=1 winning
- Test larger graphs (N > 6) with sampling
- Compare to other physics models (XY model, Heisenberg model)
- Theoretical analysis: can we prove conditions under which W(q=1) dominates?

---

*Generated by spectral_gap_ising_analysis.py*
