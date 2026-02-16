# Ising vs Gaussian Fisher Matrix Comparison

**Purpose:** Direct comparison of Fisher matrix structure across exponential families
**Date:** 2026-02-16
**Scripts:** `src/gaussian_fisher.py`, `src/near_diagonal_fisher_verification.py`

---

## Executive Summary

Three Fisher matrix patterns tested across two exponential families (Ising and Gaussian):

1. **Tree Fisher Identity:** Diagonal F on trees?
   - Ising: ✓ YES (verified)
   - Gaussian: ✗ NO (falsified)
   - **Universal? NO**

2. **Spectral Gap Selection:** q_neg=1 maximizes W?
   - Ising: ✓ YES (>90%)
   - Gaussian: ✗ NO (~55%)
   - **Universal? NO**

3. **Near-Diagonal Structure:** ||off-diag|| ~ tanh^g(J)?
   - Ising: ✓ YES (r < -0.8)
   - Gaussian: ? UNCLEAR (r = -0.3)
   - **Universal? UNKNOWN**

---

## Model Specifications

### Ising Model

**Hamiltonian:**
```
H(s) = -J * sum_{(i,j) in E} s_i s_j
```
where s_i ∈ {-1, +1}

**Fisher Matrix:**
```
F_{ab} = Cov(σ_a, σ_b)
```
where σ_e = s_i s_j for edge e=(i,j)

**Computation:** Exact via 2^n enumeration (limited to n ≤ 20)

### Gaussian Graphical Model

**Distribution:**
```
X ~ N(0, Σ)   where Σ = Λ^{-1}
```

**Precision Matrix:**
```
Λ_{ij} = J    if (i,j) ∈ E
       = diag  if i = j
       = 0     otherwise
```

**Fisher Matrix:**
```
F_{(i,j),(k,l)} = Σ_{ik}Σ_{jl} + Σ_{il}Σ_{jk}
```

**Computation:** Exact closed-form (no enumeration, scales to n=1000+)

---

## Test 1: Tree Fisher Identity

### Definition

For exponential family model on tree graph T:
```
Is F diagonal?   (i.e., F_{ab} = 0 for a ≠ b)
```

### Ising Results

| Graph | Edges | J | Max |F_ij|| (i≠j) | Diagonal? |
|-------|-------|---|-----------------|-----------|
| Path P5 | 4 | 0.5 | 3.2e-16 | YES |
| Path P10 | 9 | 0.5 | 8.7e-16 | YES |
| Star S5 | 4 | 0.5 | 4.1e-16 | YES |
| Star S8 | 7 | 0.5 | 1.2e-15 | YES |

**Conclusion:** F is diagonal on trees (to machine precision)

### Gaussian Results

| Graph | Edges | J | Max |F_ij|| (i≠j) | Diagonal? |
|-------|-------|---|-----------------|-----------|
| Path P5 | 4 | 0.5 | 8.00 | NO |
| Path P10 | 9 | 0.5 | 39.7 | NO |
| Star S5 | 4 | 0.5 | 11.3 | NO |
| Star S8 | 7 | 0.5 | 6.63 | NO |

**Conclusion:** F is NOT diagonal on trees (large off-diagonal entries)

### Comparison

```
Tree Fisher Identity:
  Ising:    max error < 1e-15  ← DIAGONAL
  Gaussian: max error ~ 10-40  ← NON-DIAGONAL

  Universal? NO
```

### Why the Difference?

**Ising:** Edge variables σ_e = s_i s_j are conditionally independent on trees
```
Cov(σ_e, σ_f | {s_i}) = 0   for e ≠ f on trees
```

**Gaussian:** Edge parameters θ_e = Λ_{ij} affect entire covariance Σ
```
∂Σ/∂θ_e and ∂Σ/∂θ_f are correlated even on trees
```

---

## Test 2: Spectral Gap Selection

### Definition

For sign assignment S = diag(±1, ..., ±1):
```
A = F^{1/2} S F^{1/2}
d_1 ≤ d_2 ≤ ... ≤ d_m = eigenvalues of A
β_c = -d_1
L_gap = (d_2 - d_1) / |d_1|
W = β_c × L_gap

Does S with q_neg = 1 (Lorentzian) maximize W?
```

### Ising Results

- **Configurations tested:** 120+ (various graphs, J values)
- **Lorentzian preferred:** >90%
- **Interpretation:** Spectral gap mechanism strongly favors q_neg=1

### Gaussian Results

- **Configurations tested:** 51 (same graph types)
- **Lorentzian preferred:** 54.9%
- **Interpretation:** No significant preference (barely above 50% random chance)

### Comparison

```
Spectral Gap Selection:
  Ising:    q_neg=1 in >90% of cases  ← STRONG PREFERENCE
  Gaussian: q_neg=1 in ~55% of cases  ← NO PREFERENCE

  Universal? NO
```

### Interpretation

The signature selection mechanism described in Paper #1 appears **model-dependent**:
- For discrete spin models (Ising, Potts): favors Lorentzian
- For continuous models (Gaussian): no preference

This suggests the mechanism may be specific to **discrete spacetime models**.

---

## Test 3: Near-Diagonal Structure

### Definition

For graph with girth g:
```
ratio = ||F - diag(F)||_op / ||diag(F)||_op

Does ratio ~ C * tanh^g(J)?   (exponential decay with girth)
```

### Ising Results (J=0.5)

| Girth | N cases | Mean ratio | Correlation |
|-------|---------|------------|-------------|
| 3 | 5 | 0.421 | |
| 4 | 8 | 0.312 | |
| 5 | 3 | 0.187 | |
| 6 | 3 | 0.143 | |
| 8 | 3 | 0.092 | |
| 10 | 3 | 0.067 | |
| ∞ | 12 | <1e-14 | |

**Correlation(girth, ratio):** -0.83 (strong negative)

**Conclusion:** Clear exponential decay with girth

### Gaussian Results (J=0.5)

| Girth | N cases | Mean ratio | Correlation |
|-------|---------|------------|-------------|
| 3 | 10 | 1.208 | |
| 4 | 9 | 2.847 | |
| 5 | 3 | 0.344 | |
| 6 | 3 | 1.056 | |
| 8 | 3 | 0.989 | |
| 10 | 3 | 0.921 | |
| ∞ | 20 | 1.197 | |

**Correlation(girth, ratio):** -0.297 (weak negative)

**Conclusion:** No clear exponential decay

### Comparison

```
Near-Diagonal Structure:
  Ising:    ratio ~ tanh^g(J), r=-0.83  ← EXPONENTIAL DECAY
  Gaussian: no clear pattern, r=-0.30   ← NO DECAY

  Universal? UNKNOWN (insufficient data)
```

### Notes

- Gaussian shows high variance in ratio
- No consistent trend with girth
- May need larger sample or different parameterization
- Trees NOT diagonal (unlike Ising), so limiting behavior different

---

## Summary Table

| Property | Ising | Gaussian | Universal? | Confidence |
|----------|-------|----------|------------|------------|
| **Tree F diagonal** | YES | NO | **NO** | 99%+ |
| **Spectral gap → q_neg=1** | YES (>90%) | NO (~55%) | **NO** | 95%+ |
| **Near-diagonal decay** | YES (r=-0.83) | NO (r=-0.30) | **UNKNOWN** | 70% |
| **M = F^2** | YES | YES | **YES** | 99%+ |
| **F is PSD** | YES | YES | **YES** | 99%+ |

**Legend:**
- YES: Pattern holds with high confidence
- NO: Pattern falsified
- UNKNOWN: Insufficient data or unclear result

---

## Scientific Implications

### For Paper #1

**Claims to Modify:**

1. **Tree Fisher Identity (Theorem 5.7):**
   - OLD: "For exponential families on trees, F is diagonal"
   - NEW: "For discrete spin models on trees, F is diagonal (not universal)"

2. **Signature Selection:**
   - OLD: "Spectral gap mechanism selects Lorentzian signature"
   - NEW: "For discrete spacetime models, spectral gap favors Lorentzian (q_neg=1)"

3. **Near-Diagonal Structure:**
   - OLD: "F is near-diagonal for large girth"
   - NEW: "For discrete spin models, F is near-diagonal for large girth"

**Claims to Keep (Universal):**

1. **M = F^2 for exponential families** ← Still valid
2. **PSD obstruction for standard M** ← Still valid
3. **Critical beta formula** ← Model-independent definition
4. **Signed-edge construction H1'** ← Mathematical construction

### Broader Impact

**Positive:** Paper becomes stronger by:
- Providing comparative analysis
- Distinguishing universal vs model-specific results
- Demonstrating scientific rigor through negative results

**Opens Questions:**
- What model properties lead to tree Fisher diagonality?
- Is signature selection specific to discrete graph models?
- Can near-diagonal structure be characterized graph-theoretically?

---

## Computational Notes

### Performance Comparison

**Ising:**
- Enumeration: O(2^n) exponential
- Max n ≈ 20 (practical limit)
- Runtime: seconds to minutes

**Gaussian:**
- Closed-form: O(n^3) for matrix inversion
- Max n ≈ 1000+ (memory limited only)
- Runtime: milliseconds to seconds

### Accuracy

**Ising:**
- Exact (finite state space)
- Numerical precision: machine epsilon

**Gaussian:**
- Exact (closed-form formula)
- Numerical precision: matrix inversion stability

Both methods produce **exact** Fisher matrices (no sampling, no approximation).

---

## Reproducibility

### Ising Tests

```bash
cd papers/structural-bridge
python3 src/near_diagonal_fisher_verification.py
```

Output: `experience/insights/NEAR-DIAGONAL-FISHER-VERIFICATION-2026-02-16.md`

### Gaussian Tests

```bash
cd papers/structural-bridge
python3 src/gaussian_fisher.py
```

Output: Console + `experience/insights/GAUSSIAN-FISHER-UNIVERSALITY-TEST-2026-02-16.md`

### Unit Tests

```bash
python3 tests/test_gaussian_fisher.py
```

Expected: All 8 tests pass

---

## Recommendations

### For Publication

1. **Include comparative table** (Ising vs Gaussian) in Paper #1
2. **State model-specific caveats** for Tree Fisher Identity
3. **Acknowledge non-universality** of signature selection
4. **Emphasize universal results** (M=F^2, PSD obstruction)

### For Future Work

1. **Test additional exponential families:**
   - Poisson graphical models
   - Exponential copulas
   - Higher-state Potts models (q>2)

2. **Characterize conditional independence:**
   - When does tree → diagonal F?
   - Connection to graph separability?

3. **Scaling studies:**
   - Gaussian allows n=1000+
   - Phase transitions?
   - Asymptotic behavior?

---

## Conclusion

The Gaussian graphical model comparison provides **crucial falsification** of universality claims:

1. ✗ Tree Fisher Identity is **NOT universal** (model-specific)
2. ✗ Spectral gap selection is **NOT universal** (model-dependent)
3. ? Near-diagonal structure **UNCLEAR** (needs more data)

But exponential family properties ARE universal:
1. ✓ M = F^2 (general theorem)
2. ✓ F is PSD (general property)

**Impact:** Strengthens Paper #1 by distinguishing universal from model-specific results through comparative analysis.

---

*Comparison based on exact computations for both models*
*No approximations, no sampling, fully reproducible*
*Attribution: TEST-BRIDGE-MVP1-GAUSSIAN-FISHER-001*
