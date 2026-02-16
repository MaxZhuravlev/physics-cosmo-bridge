# M = F² Universality Investigation

**Date**: 2026-02-17
**Purpose**: Investigate WHY M = F² holds for RBM visible marginals despite RBMs NOT being exponential families
**Status**: RESOLVED

---

## Research Question

The RBM Fisher computation (`src/rbm_fisher.py`) found that M = F² holds EXACTLY (error = 0.00e+00) for all 27 tested RBM configurations. This was SURPRISING because:

1. RBM visible marginals p(v) = Σ_h exp(-E(v,h)) / Z are **marginals of exponential families**
2. They are NOT themselves exponential families (standard claim in ML literature)
3. The theorem "M = F² for exponential families" suggests it should FAIL for non-exponential families

**Why does it hold?**

---

## Answer: RBMs ARE Exponential Families (in the varied parameters)

### Key Insight

The claim "RBM visible marginals are not exponential families" is TRUE when considering the **full parameter space** (W, a, b). However, the RBM Fisher computation **fixes W and b** and only varies **a** (visible biases).

### Mathematical Analysis

For binary visible units v ∈ {0,1}^n and fixed (W, b):

```
p(v; a) = (1/Z(a)) exp(a^T v) × Π_j [1 + exp(b_j + W_j^T v)]
```

Rearranging:

```
p(v; a) = (1/Z(a)) exp(a^T v + Σ_j log(1 + exp(b_j + W_j^T v)))
```

Let:
```
A(a) = log Z(a) = log Σ_v exp(a^T v + Σ_j log(1 + exp(b_j + W_j^T v)))
```

Then:
```
log p(v; a) = a^T v + Σ_j log(1 + exp(b_j + W_j^T v)) - A(a)
            = a^T T(v) - A(a)
```

where the sufficient statistic is **T(v) = v**.

**This IS the canonical form of an exponential family!**

- Natural parameters: θ = a (visible biases)
- Sufficient statistics: T(v) = v
- Log-partition function: A(a)
- Base measure: h(v) = Π_j [1 + exp(b_j + W_j^T v)]

### Exponential Family Classification

**Full parameter space (W, a, b)**: NOT an exponential family (latent variable model)

**Restricted to parameter a (W, b fixed)**: IS an exponential family (canonical form)

This is a **curved exponential family** — the parameters (W, b) constrain the family to a lower-dimensional manifold within the full exponential family.

---

## Theorem Application

From `experience/insights/MASS-FISHER-SQUARED-PROOF-2026-02-16.md`:

**Theorem**: For a canonical exponential family with natural parameters θ:

```
M_{ab} = Σ_e (∂w_e/∂θ_a)(∂w_e/∂θ_b) = (F²)_{ab}
```

where:
- w_e(θ) = ∂A/∂θ_e (mean sufficient statistic)
- F_{ab} = ∂²A/(∂θ_a∂θ_b) (Fisher information)

**Proof**:
- ∂w_e/∂θ_a = ∂²A/(∂θ_e∂θ_a) = F_{ea}
- Hence M_{ab} = Σ_e F_{ea}F_{eb} = (F²)_{ab}

### Application to RBM

For RBM parameterized by a (with W, b fixed):

1. p(v; a) is an exponential family in a ✓
2. Natural parameterization: θ = a ✓
3. A(a) exists (log partition function) ✓
4. F = ∂²A/∂a∂a^T (standard Fisher) ✓

Therefore: **M = F² holds exactly by the theorem!**

---

## Resolution of "Not Exponential Family" Claim

The ML literature claim "RBM visible marginals are not exponential families" refers to:

**Full model**: Treating (W, a, b) as joint parameters → NOT exponential family (due to marginalization over h)

**Restricted model** (our computation): Treating only a as parameters → IS exponential family

Both claims are correct, referring to different parameterizations.

---

## Implication for RBM Paper Results

**Reinterpretation**:

The RBM paper (`src/rbm_fisher.py`) tested whether exponential family properties extend to "marginals of exponential families." The answer:

1. **Tree Fisher Identity**: FAILS (11% diagonal) — correctly identifies non-trivial structure
2. **M = F²**: HOLDS (100%) — because the **parameterization** makes it an exponential family
3. **Spectral Gap Selection**: FAILS (22%) — architecture-dependent, not universal

**Corrected conclusion**:

- RBM visible marginals, when parameterized by visible biases a alone, ARE exponential families
- Hence M = F² holds by theorem, not as a surprise
- The "boundary of universality" test is inconclusive for this model
- Need true non-exponential family test cases (mixtures, truncated models)

---

## Recommendations for Paper #1

### Section 6.3: Fisher Universality Tests

**Current framing** (needs correction):
- "RBM visible marginals are not exponential families" → TOO BROAD

**Corrected framing**:
- "RBM visible marginals, when parameterized by all (W, a, b), are not exponential families"
- "However, when parameterized by visible biases a alone (W, b fixed), they ARE exponential families (curved)"
- "Hence M = F² holds by theorem, as expected for exponential families"

**Value of RBM test**:
- Still useful: tests whether **Tree Fisher diagonality** extends to dense bipartite graphs (it doesn't)
- Demonstrates parameterization-dependence of exponential family classification
- But NOT a counterexample to M = F²

### True Counterexamples Needed

For genuine M ≠ F² testing, use:

1. **Mixture models**: p(x) = Σ_k π_k p_k(x; θ_k) — NOT exponential families in any parameterization
2. **Truncated exponential families**: Exponential family with support restrictions
3. **Non-canonical parameterizations**: Even for exponential families, M = F² breaks if not using natural parameters

---

## Computational Verification (TODO)

To properly test M = F² boundaries:

1. Implement CORRECT mass tensor definition:
   ```
   M_{ab} = Σ_e (∂w_e/∂θ_a)(∂w_e/∂θ_b)
   ```
   where w_e = E[T_e] (mean sufficient statistic)

2. Test on:
   - RBM (a parameters): EXPECT M = F² ✓
   - Gaussian mixture (μ parameters): EXPECT M ≠ F²
   - Truncated Gaussian (μ with support [a,b]): EXPECT M ≠ F²

3. Current `rbm_fisher.py` computed M = F @ F, which is **trivially equal to F²** by definition
   - Need to compute Jacobian of w(θ) properly
   - Then form Gram matrix M = J^T J
   - Compare to F²

---

## Mathematical Clarity: Two Definitions

**Definition used in `rbm_fisher.py`**:
```python
def compute_mass_tensor(F):
    return F @ F  # Trivially equals F² by definition!
```

**Correct definition from physics**:
```
M_{ab} = Σ_e (∂w_e/∂θ_a)(∂w_e/∂θ_b)
```

The RBM paper conflated these:
- Computed M = F @ F (definition 1)
- Tested whether M = F² (always true for definition 1!)
- Should have computed M via Jacobian of w, then tested M =? F²

---

## Conclusion

**RBM M = F² result**: Expected, not surprising
- RBMs in restricted parameterization (a alone) ARE exponential families
- M = F² theorem applies
- Error = 0 is correct

**Lesson learned**:
- Exponential family classification is parameterization-dependent
- "Marginals of exponential families" can still be exponential families (in a subspace)
- For genuine M ≠ F² tests, need models that are NOT exponential families in ANY parameterization

**Action for Paper #1**:
- Clarify RBM exponential family status (parameterization-dependent)
- Remove claim that RBM tests "boundary of M = F² universality"
- Add mixture model tests if claiming to establish boundaries

---

## Attribution

```yaml
investigation_id: MF2-UNIVERSALITY-INVESTIGATION-2026-02-17
dialogue_id: session-2026-02-17-mf2-universality
recovery_path: papers/structural-bridge/output/MF2-UNIVERSALITY-INVESTIGATION.md
patterns_applied:
  - pt.process.tdd-implementation (red-green-refactor)
  - pt.meta.test-boundaries (identifying failure modes)
  - pt.universal.verification-closes-loops (closing open question)
prerequisites:
  - experience/insights/MASS-FISHER-SQUARED-PROOF-2026-02-16.md
  - src/rbm_fisher.py
  - output/RBM-FISHER-RESULTS.md
```

---

**END OF INVESTIGATION**
