# Degeneracy Analysis: W(q=1) = W_max under H1' Construction

**Generated:** 2026-02-17
**Attribution:** TEST-BRIDGE-MVP1-DEGENERACY-ANALYSIS-001

## Executive Summary

The 240-configuration phase diagram showed W(q=1) = W(q>=2) for every
configuration (exact tie, 0% q=1 win rate). This investigation identifies
**two independent algebraic obstructions** that explain the degeneracy.

### Finding 1: Similarity Invariance (W(q) is q-independent)

The spectral gap computation applies a signature matrix Sig to the operator:
```
A_transformed = Sig * A_H1 * Sig
```
Since Sig is diagonal with +/-1 entries, Sig^{-1} = Sig. Therefore
`Sig * A * Sig = Sig * A * Sig^{-1}` is a **similarity transformation**,
which preserves ALL eigenvalues. This makes W(q) **identical** for all q.

This is an **exact algebraic identity**, not a numerical coincidence.

### Finding 2: PSD Obstruction (M = S*F^2*S cannot produce Lorentzian)

For the mass tensor M = S*F^2*S:
```
F^{-1/2} (S F^2 S) F^{-1/2} = (F^{-1/2} S F)(F^{-1/2} S F)^T = C * C^T
```
This is a Gram matrix, which is **always PSD** regardless of S.
Numerically verified across 200 random cases: CONFIRMED.

### Finding 3: Correct Approach

The signature q should be **determined** by the eigenvalue structure of
g = F^{-1/2} M F^{-1/2}, not optimized over using Sig*A*Sig. The number
of negative eigenvalues of g directly gives q. No optimization needed.

## Algebraic Proof: Similarity Invariance

**Theorem.** For any symmetric matrix A and any diagonal matrix
Sig = diag(s_1, ..., s_m) with s_i in {+1, -1}:
```
spec(Sig * A * Sig) = spec(A)
```

**Proof.**
1. Sig is diagonal with +/-1 entries => Sig^T = Sig
2. s_i^2 = 1 for all i => Sig^2 = I
3. Therefore Sig^{-1} = Sig
4. So Sig * A * Sig = Sig * A * Sig^{-1} (similarity transform)
5. Eigenvalues are invariant under similarity: spec(BAB^{-1}) = spec(A)
6. QED

**Consequence for the phase diagram code:**
Line 253 of `signed_edge_phase_diagram.py`:
```python
A_transformed = Sig @ A_H1 @ Sig
```
This operation preserves eigenvalues of A_H1 for all Sig, making
beta_c and L_gap (and therefore W) q-independent.

## PSD Obstruction for M = S*F^2*S

**Theorem.** F^{-1/2} (S F^2 S) F^{-1/2} is PSD for all diagonal S.

**Proof.**
```
Let C = F^{-1/2} S F
Note: (F S F^{-1/2})^T = F^{-1/2} S^T F^T = F^{-1/2} S F = C
Therefore:
  F^{-1/2} S F^2 S F^{-1/2}
  = (F^{-1/2} S F)(F S F^{-1/2})
  = C * C^T
```
C*C^T is a Gram matrix and always PSD. QED.

**Consequence:** The construction M = S*F^2*S gives q = 0 (Riemannian)
for ALL sign matrices S. To get Lorentzian (q > 0), one must use a
different mass tensor construction.

**Important distinction:** F^{1/2} S F^{1/2} CAN have negative eigenvalues.
This is the correct object for testing Lorentzian signature. However,
it is NOT the same as F^{-1/2} M^{H1'} F^{-1/2}.

## Numerical Verification

### Similarity Invariance

| m | J | Graph | Max Eigenvalue Deviation | Algebraic? |
|---|---|-------|------------------------|------------|
| 3 | 0.5 | tree | 0.00e+00 | YES |
| 4 | 1.0 | sparse | 0.00e+00 | YES |
| 4 | 0.3 | dense | 0.00e+00 | YES |
| 5 | 0.5 | tree | 0.00e+00 | YES |
| 5 | 1.0 | dense | 0.00e+00 | YES |

### Eigenvalue Structure (A = F^{1/2} S F^{1/2})

| m | J | Graph | n_neg_signs | A eigenvalues | Has neg eig? |
|---|---|-------|------------|---------------|-------------|
| 3 | 0.5 | tree | 0 | [0.7864, 0.7864, 0.7864] | NO |
| 4 | 1.0 | sparse | 1 | [-0.4200, 0.4200, 0.4200, 0.4200] | YES |
| 4 | 0.3 | dense | 3 | [-1.1310, -0.5067, -0.5067, 0.5067, 0.5067, 1.1310] | YES |
| 5 | 0.5 | tree | 1 | [-0.7864, 0.7864, 0.7864, 0.7864, 0.7864] | YES |
| 5 | 1.0 | dense | 3 | [-0.0367, -0.0072, -0.0072, 0.0072, 0.0072, 0.0367] | YES |

### W(q) Values (showing q-independence)

**Config: m=3, J=0.5, tree:**

| q | W(q) | beta_c | L_gap |
|---|------|--------|-------|
| 0 | 0.000000 | -1.000000 | 0.000000 |
| 1 | 0.000000 | -1.000000 | 0.000000 |
| 2 | 0.000000 | -1.000000 | 0.000000 |
| 3 | 0.000000 | -1.000000 | 0.000000 |

**Config: m=4, J=1.0, sparse:**

| q | W(q) | beta_c | L_gap |
|---|------|--------|-------|
| 0 | 0.839949 | 0.419974 | 2.000000 |
| 1 | 0.839949 | 0.419974 | 2.000000 |
| 2 | 0.839949 | 0.419974 | 2.000000 |
| 3 | 0.839949 | 0.419974 | 2.000000 |
| 4 | 0.839949 | 0.419974 | 2.000000 |

**Config: m=4, J=0.3, dense:**

| q | W(q) | beta_c | L_gap |
|---|------|--------|-------|
| 0 | 0.624272 | 1.130984 | 0.551972 |
| 1 | 0.624272 | 1.130984 | 0.551972 |
| 2 | 0.624272 | 1.130984 | 0.551972 |
| 3 | 0.624272 | 1.130984 | 0.551972 |
| 4 | 0.624272 | 1.130984 | 0.551972 |
| 5 | 0.624272 | 1.130984 | 0.551972 |
| 6 | 0.624272 | 1.130984 | 0.551972 |

**Config: m=5, J=0.5, tree:**

| q | W(q) | beta_c | L_gap |
|---|------|--------|-------|
| 0 | 1.572895 | 0.786448 | 2.000000 |
| 1 | 1.572895 | 0.786448 | 2.000000 |
| 2 | 1.572895 | 0.786448 | 2.000000 |
| 3 | 1.572895 | 0.786448 | 2.000000 |
| 4 | 1.572895 | 0.786448 | 2.000000 |
| 5 | 1.572895 | 0.786448 | 2.000000 |

**Config: m=5, J=1.0, dense:**

| q | W(q) | beta_c | L_gap |
|---|------|--------|-------|
| 0 | 0.029499 | 0.036716 | 0.803456 |
| 1 | 0.029499 | 0.036716 | 0.803456 |
| 2 | 0.029499 | 0.036716 | 0.803456 |
| 3 | 0.029499 | 0.036716 | 0.803456 |
| 4 | 0.029499 | 0.036716 | 0.803456 |
| 5 | 0.029499 | 0.036716 | 0.803456 |
| 6 | 0.029499 | 0.036716 | 0.803456 |

## Alternative Mass Tensor Constructions

Testing whether alternative constructions break the W(q) degeneracy.

### Summary Table

| Construction | Degeneracy Broken? | Has Negative Eigs? | Notes |
|-------------|-------------------|-------------------|-------|
| M = S*F*S (linear) | NO | False | |
| M = S*(F+0.01I)^2*S | NO | False | |
| M = S*(F+0.1I)^2*S | NO | False | |
| M = S*(F+0.5I)^2*S | NO | False | |
| M = S*F^0.5*S | NO | False | |
| M = S*F^1.0*S | NO | False | |
| M = S*F^1.5*S | NO | False | |
| M = S*F^3.0*S | NO | False | |
| M = F*S*F | NO | False | |
| Use Sig*A (asymmetric, eigenvalues q-dependent) | YES | N/A | |
| M_q with signature in F-eigenbasis (q-dependent M) | YES | N/A | |

### Config: m=3, J=0.5, tree

**M = S*F*S (linear):**
- Eigenvalues: [1.000000, 1.000000, 1.000000]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000
- Degeneracy broken: False

**M = S*(F+0.01I)^2*S:**
- Eigenvalues: [0.806575, 0.806575, 0.806575]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000
- Degeneracy broken: False

**M = S*(F+0.1I)^2*S:**
- Eigenvalues: [0.999163, 0.999163, 0.999163]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000
- Degeneracy broken: False

**M = S*(F+0.5I)^2*S:**
- Eigenvalues: [2.104333, 2.104333, 2.104333]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000
- Degeneracy broken: False

**M = S*F^0.5*S:**
- Eigenvalues: [1.127626, 1.127626, 1.127626]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000
- Degeneracy broken: False

**M = S*F^1.0*S:**
- Eigenvalues: [1.000000, 1.000000, 1.000000]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000
- Degeneracy broken: False

**M = S*F^1.5*S:**
- Eigenvalues: [0.886819, 0.886819, 0.886819]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000
- Degeneracy broken: False

**M = S*F^3.0*S:**
- Eigenvalues: [0.618500, 0.618500, 0.618500]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000
- Degeneracy broken: False

**M = F*S*F:**
- Eigenvalues: [0.786448, 0.786448, 0.786448]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000
- Degeneracy broken: False

**Use Sig*A (asymmetric, eigenvalues q-dependent):**
- W(q): q=0:0.000000, q=1:2.000000, q=2:0.000000, q=3:0.000000
- Degeneracy broken: True

**M_q with signature in F-eigenbasis (q-dependent M):**
- W(q): q=0:0.000000, q=1:2.000000, q=2:0.000000, q=3:0.000000
- Degeneracy broken: True

### Config: m=4, J=1.0, sparse

**M = S*F*S (linear):**
- Eigenvalues: [1.000000, 1.000000, 1.000000, 1.000000]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000
- Degeneracy broken: False

**M = S*(F+0.01I)^2*S:**
- Eigenvalues: [0.440212, 0.440212, 0.440212, 0.440212]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000
- Degeneracy broken: False

**M = S*(F+0.1I)^2*S:**
- Eigenvalues: [0.643785, 0.643785, 0.643785, 0.643785]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000
- Degeneracy broken: False

**M = S*(F+0.5I)^2*S:**
- Eigenvalues: [2.015249, 2.015249, 2.015249, 2.015249]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000
- Degeneracy broken: False

**M = S*F^0.5*S:**
- Eigenvalues: [1.543081, 1.543081, 1.543081, 1.543081]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000
- Degeneracy broken: False

**M = S*F^1.0*S:**
- Eigenvalues: [1.000000, 1.000000, 1.000000, 1.000000]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000
- Degeneracy broken: False

**M = S*F^1.5*S:**
- Eigenvalues: [0.648054, 0.648054, 0.648054, 0.648054]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000
- Degeneracy broken: False

**M = S*F^3.0*S:**
- Eigenvalues: [0.176378, 0.176378, 0.176378, 0.176378]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000
- Degeneracy broken: False

**M = F*S*F:**
- Eigenvalues: [-0.419974, 0.419974, 0.419974, 0.419974]
- W(q): q=0:0.839949, q=1:0.839949, q=2:0.839949, q=3:0.839949, q=4:0.839949
- Degeneracy broken: False

**Use Sig*A (asymmetric, eigenvalues q-dependent):**
- W(q): q=0:2.000000, q=1:0.000000, q=2:2.000000, q=3:0.000000, q=4:0.000000
- Degeneracy broken: True

**M_q with signature in F-eigenbasis (q-dependent M):**
- W(q): q=0:0.000000, q=1:2.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000
- Degeneracy broken: True

### Config: m=4, J=0.3, dense

**M = S*F*S (linear):**
- Eigenvalues: [0.365751, 0.548812, 0.548812, 1.822119, 1.822119, 2.734097]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000, q=6:0.000000
- Degeneracy broken: False

**M = S*(F+0.01I)^2*S:**
- Eigenvalues: [0.217136, 0.217136, 0.257539, 1.283019, 1.283019, 5.167846]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000, q=6:0.000000
- Degeneracy broken: False

**M = S*(F+0.1I)^2*S:**
- Eigenvalues: [0.328668, 0.330396, 0.330396, 1.637374, 1.637374, 5.674458]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000, q=6:0.000000
- Degeneracy broken: False

**M = S*(F+0.5I)^2*S:**
- Eigenvalues: [0.749605, 1.120328, 1.120328, 3.734418, 3.734418, 8.212618]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000, q=6:0.000000
- Degeneracy broken: False

**M = S*F^0.5*S:**
- Eigenvalues: [0.442243, 0.895750, 0.895750, 1.999319, 2.203190, 2.203190]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000, q=6:0.000000
- Degeneracy broken: False

**M = S*F^1.0*S:**
- Eigenvalues: [0.365751, 0.548812, 0.548812, 1.822119, 1.822119, 2.734097]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000, q=6:0.000000
- Degeneracy broken: False

**M = S*F^1.5*S:**
- Eigenvalues: [0.302490, 0.336248, 0.336248, 1.506959, 1.506959, 3.738915]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000, q=6:0.000000
- Degeneracy broken: False

**M = S*F^3.0*S:**
- Eigenvalues: [0.077334, 0.077334, 0.171114, 0.852464, 0.852464, 9.561825]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000, q=6:0.000000
- Degeneracy broken: False

**M = F*S*F:**
- Eigenvalues: [-1.130984, -0.506712, -0.506712, 0.506712, 0.506712, 1.130984]
- W(q): q=0:0.624272, q=1:0.624272, q=2:0.624272, q=3:0.624272, q=4:0.624272, q=5:0.624272, q=6:0.624272
- Degeneracy broken: False

**Use Sig*A (asymmetric, eigenvalues q-dependent):**
- W(q): q=0:0.551972, q=1:0.479852, q=2:1.661436, q=3:0.052635, q=4:1.661436, q=5:0.479852, q=6:0.551972
- Degeneracy broken: True

**M_q with signature in F-eigenbasis (q-dependent M):**
- W(q): q=0:0.000000, q=1:2.000000, q=2:0.799271, q=3:0.799271, q=4:0.634249, q=5:0.634249, q=6:0.634249
- Degeneracy broken: True

### Config: m=5, J=0.5, tree

**M = S*F*S (linear):**
- Eigenvalues: [1.000000, 1.000000, 1.000000, 1.000000, 1.000000]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000
- Degeneracy broken: False

**M = S*(F+0.01I)^2*S:**
- Eigenvalues: [0.806575, 0.806575, 0.806575, 0.806575, 0.806575]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000
- Degeneracy broken: False

**M = S*(F+0.1I)^2*S:**
- Eigenvalues: [0.999163, 0.999163, 0.999163, 0.999163, 0.999163]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000
- Degeneracy broken: False

**M = S*(F+0.5I)^2*S:**
- Eigenvalues: [2.104333, 2.104333, 2.104333, 2.104333, 2.104333]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000
- Degeneracy broken: False

**M = S*F^0.5*S:**
- Eigenvalues: [1.127626, 1.127626, 1.127626, 1.127626, 1.127626]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000
- Degeneracy broken: False

**M = S*F^1.0*S:**
- Eigenvalues: [1.000000, 1.000000, 1.000000, 1.000000, 1.000000]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000
- Degeneracy broken: False

**M = S*F^1.5*S:**
- Eigenvalues: [0.886819, 0.886819, 0.886819, 0.886819, 0.886819]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000
- Degeneracy broken: False

**M = S*F^3.0*S:**
- Eigenvalues: [0.618500, 0.618500, 0.618500, 0.618500, 0.618500]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000
- Degeneracy broken: False

**M = F*S*F:**
- Eigenvalues: [-0.786448, 0.786448, 0.786448, 0.786448, 0.786448]
- W(q): q=0:1.572895, q=1:1.572895, q=2:1.572895, q=3:1.572895, q=4:1.572895, q=5:1.572895
- Degeneracy broken: False

**Use Sig*A (asymmetric, eigenvalues q-dependent):**
- W(q): q=0:2.000000, q=1:0.000000, q=2:2.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000
- Degeneracy broken: True

**M_q with signature in F-eigenbasis (q-dependent M):**
- W(q): q=0:0.000000, q=1:2.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000
- Degeneracy broken: True

### Config: m=5, J=1.0, dense

**M = S*F*S (linear):**
- Eigenvalues: [0.135335, 0.135335, 0.285436, 3.503414, 7.389054, 7.389054]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000, q=6:0.000000
- Degeneracy broken: False

**M = S*(F+0.01I)^2*S:**
- Eigenvalues: [0.008164, 0.008164, 0.012763, 0.315929, 0.330392, 0.330392]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000, q=6:0.000000
- Degeneracy broken: False

**M = S*(F+0.1I)^2*S:**
- Eigenvalues: [0.208200, 0.537220, 0.537220, 1.451239, 5.389644, 5.389644]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000, q=6:0.000000
- Degeneracy broken: False

**M = S*(F+0.5I)^2*S:**
- Eigenvalues: [3.928868, 12.880531, 12.880531, 16.489014, 101.706279, 101.706279]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000, q=6:0.000000
- Degeneracy broken: False

**M = S*F^0.5*S:**
- Eigenvalues: [2.038007, 2.626653, 2.626653, 13.364197, 52.757713, 52.757713]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000, q=6:0.000000
- Degeneracy broken: False

**M = S*F^1.0*S:**
- Eigenvalues: [0.135335, 0.135335, 0.285436, 3.503414, 7.389054, 7.389054]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000, q=6:0.000000
- Degeneracy broken: False

**M = S*F^1.5*S:**
- Eigenvalues: [0.006973, 0.006973, 0.039977, 0.918417, 1.034884, 1.034884]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000, q=6:0.000000
- Degeneracy broken: False

**M = S*F^3.0*S:**
- Eigenvalues: [0.000001, 0.000001, 0.000110, 0.002843, 0.002843, 0.016546]
- W(q): q=0:0.000000, q=1:0.000000, q=2:0.000000, q=3:0.000000, q=4:0.000000, q=5:0.000000, q=6:0.000000
- Degeneracy broken: False

**M = F*S*F:**
- Eigenvalues: [-0.036716, -0.007216, -0.007216, 0.007216, 0.007216, 0.036716]
- W(q): q=0:0.029499, q=1:0.029499, q=2:0.029499, q=3:0.029499, q=4:0.029499, q=5:0.029499, q=6:0.029499
- Degeneracy broken: False

**Use Sig*A (asymmetric, eigenvalues q-dependent):**
- W(q): q=0:0.803456, q=1:0.766573, q=2:1.342307, q=3:0.130419, q=4:1.342307, q=5:0.766573, q=6:0.803456
- Degeneracy broken: True

**M_q with signature in F-eigenbasis (q-dependent M):**
- W(q): q=0:0.000000, q=1:2.000000, q=2:0.961370, q=3:0.961370, q=4:0.714564, q=5:0.714564, q=6:0.714564
- Degeneracy broken: True

## Correct Spectral Selection

Instead of optimizing over Sig (which is trivially similarity-invariant),
the correct approach is to determine q from the signature of g = F^{-1/2} M F^{-1/2}.

| Construction | q (from eigenvalue signature) | Eigenvalues |
|-------------|------------------------------|-------------|
| M=F^2 | 0 | [0.7864, 0.7864, 0.7864] |
| M=SF^2S | 0 | [0.7864, 0.7864, 0.7864] |
| A=F^{1/2}SF^{1/2} | 0 | [0.7864, 0.7864, 0.7864] |
| M=SFS | 0 | [1.0000, 1.0000, 1.0000] |
| M=FSF | 0 | [0.7864, 0.7864, 0.7864] |

## Physical Interpretation and Implications for Paper #1

### Root Cause of the Degeneracy

The degeneracy has **two independent causes**:

1. **Similarity invariance**: The Sig*A*Sig construction used to vary q
   is a similarity transformation and cannot change eigenvalues. This means
   the W(q) metric as currently defined is q-independent for ANY matrix A.
   This is a bug in the spectral gap computation, not a feature of the
   H1' construction specifically.

2. **PSD obstruction for S*F^2*S**: Even if the W(q) computation were fixed,
   the mass tensor M = S*F^2*S gives F^{-1/2}MF^{-1/2} = CC^T which is
   always PSD. So this specific mass tensor cannot produce Lorentzian
   signature regardless of S.

### What DOES Work

1. **F^{1/2} S F^{1/2}** (the A_H1 matrix): This CAN have negative eigenvalues
   when S has appropriate signs. The number of negative eigenvalues directly
   determines the signature. For Lorentzian, we need exactly 1 negative eigenvalue.

2. **M = S*F*S** (linear construction): F^{-1/2}(SFS)F^{-1/2} is NOT guaranteed
   PSD, so this construction can in principle produce Lorentzian signature.

3. **M = F*S*F**: F^{-1/2}(FSF)F^{-1/2} = F^{1/2} S F^{1/2}, which is the
   same as A_H1. This is the natural construction where M = F*S*F and
   the spectral test gives the correct Lorentzian signature.

### Implications for Paper #1

1. **The W(q) computation needs a different mechanism for q-dependence.**
   The Sig*A*Sig construction is fundamentally flawed because it's a similarity
   transform. The correct approach: q is determined by how many eigenvalues of
   A = F^{1/2} S F^{1/2} are negative.

2. **The PSD obstruction for M = S*F^2*S is a genuine negative result.**
   This should be stated clearly: the quadratic construction cannot produce
   Lorentzian signature. Only the linear constructions (M = SFS or M = FSF)
   or the direct A = F^{1/2} S F^{1/2} formulation can.

3. **The phrase 'beta_c > 0 but W(q=1) = W_max' is misleading.**
   It should be 'the signature of A_H1 determines q; the Sig*A*Sig
   construction adds no information because it preserves eigenvalues.'

4. **The Fiedler sign method result (beta_c > 0) remains valid.**
   A = F^{1/2} S F^{1/2} does have negative eigenvalues when S has
   Fiedler-based signs. The issue is only with how W(q) is defined.

---

*Generated by degeneracy_analysis.py*
