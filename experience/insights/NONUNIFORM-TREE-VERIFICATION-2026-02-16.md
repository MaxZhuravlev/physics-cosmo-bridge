# Non-Uniform Tree Fisher Matrix Verification

**Date:** 2026-02-16
**Attribution:** TEST-BRIDGE-MVP1-NONUNIFORM-TREE-001

## Conjecture

For an Ising model on a tree with non-uniform couplings {J_e : e ∈ E}, the Fisher matrix in edge parameterization should be:

```
F = diag(sech²(J_1), sech²(J_2), ..., sech²(J_m))
```

## Reasoning

On a tree, the Hamiltonian H = -Σ_e J_e σ_e decomposes into independent terms in the edge variables σ_e (no cycle constraints). Therefore each σ_e should be an independent Bernoulli with parameter depending only on J_e.

## Method

1. Generate tree graphs (paths, stars, random trees)
2. Assign non-uniform couplings from various distributions
3. Compute exact Ising Fisher matrix
4. Verify F is diagonal (max |F_ij| < 1e-9 for i≠j)
5. Verify F_ii = sech²(J_i) (max error < 1e-9)

## Results

**Total configurations tested:** 49
**Configurations passing both checks:** 49/49 (100.0%)
**Maximum diagonal error:** 3.65e-16
**Maximum sech² error:** 1.89e-15

### Detailed Results

| Graph Type | N | m | Diagonal? | Sech²? | Diag Error | Sech Error |
|------------|---|---|-----------|--------|------------|------------|
| path       |  5 |  4 | ✓         | ✓      | 5.07e-17 | 1.11e-16 |
| path       | 10 |  9 | ✓         | ✓      | 1.46e-16 | 7.77e-16 |
| path       |  8 |  7 | ✓         | ✓      | 1.47e-16 | 3.33e-16 |
| path       |  8 |  7 | ✓         | ✓      | 1.72e-16 | 6.66e-16 |
| path       | 10 |  9 | ✓         | ✓      | 1.11e-16 | 1.89e-15 |
| path       |  9 |  8 | ✓         | ✓      | 1.02e-16 | 3.33e-16 |
| path       | 11 | 10 | ✓         | ✓      | 2.88e-16 | 8.33e-16 |
| path       |  7 |  6 | ✓         | ✓      | 2.78e-17 | 5.55e-16 |
| path       |  9 |  8 | ✓         | ✓      | 5.85e-17 | 3.33e-16 |
| path       |  9 |  8 | ✓         | ✓      | 4.39e-17 | 5.00e-16 |
| path       |  7 |  6 | ✓         | ✓      | 4.42e-17 | 5.55e-16 |
| path       |  7 |  6 | ✓         | ✓      | 2.78e-17 | 2.22e-16 |
| path       |  6 |  5 | ✓         | ✓      | 6.00e-17 | 3.33e-16 |
| path       |  7 |  6 | ✓         | ✓      | 6.35e-17 | 2.22e-16 |
| star       | 10 |  9 | ✓         | ✓      | 1.36e-16 | 1.33e-15 |
| star       |  8 |  7 | ✓         | ✓      | 1.70e-17 | 2.22e-16 |
| star       | 10 |  9 | ✓         | ✓      | 6.24e-17 | 8.88e-16 |
| star       |  7 |  6 | ✓         | ✓      | 4.29e-17 | 3.33e-16 |
| star       |  5 |  4 | ✓         | ✓      | 3.99e-17 | 1.11e-16 |
| star       |  5 |  4 | ✓         | ✓      | 1.33e-17 | 3.33e-16 |
| star       | 10 |  9 | ✓         | ✓      | 7.77e-17 | 6.66e-16 |
| star       |  8 |  7 | ✓         | ✓      | 7.13e-17 | 6.66e-16 |
| star       |  8 |  7 | ✓         | ✓      | 9.73e-17 | 3.33e-16 |
| star       |  7 |  6 | ✓         | ✓      | 7.29e-17 | 5.55e-16 |
| star       |  5 |  4 | ✓         | ✓      | 7.34e-18 | 1.67e-16 |
| star       | 10 |  9 | ✓         | ✓      | 3.65e-16 | 7.77e-16 |
| star       |  5 |  4 | ✓         | ✓      | 5.69e-17 | 2.22e-16 |
| star       | 10 |  9 | ✓         | ✓      | 1.26e-16 | 7.77e-16 |
| random_tree | 11 | 10 | ✓         | ✓      | 3.15e-16 | 1.33e-15 |
| random_tree |  5 |  4 | ✓         | ✓      | 2.00e-17 | 1.11e-16 |
| random_tree |  7 |  6 | ✓         | ✓      | 4.81e-17 | 1.11e-16 |
| random_tree | 11 | 10 | ✓         | ✓      | 2.30e-16 | 1.44e-15 |
| random_tree |  7 |  6 | ✓         | ✓      | 3.34e-17 | 1.67e-16 |
| random_tree | 10 |  9 | ✓         | ✓      | 1.80e-16 | 7.77e-16 |
| random_tree | 10 |  9 | ✓         | ✓      | 1.94e-16 | 1.44e-15 |
| random_tree | 10 |  9 | ✓         | ✓      | 1.12e-16 | 1.44e-15 |
| random_tree | 10 |  9 | ✓         | ✓      | 9.78e-17 | 7.77e-16 |
| random_tree |  7 |  6 | ✓         | ✓      | 5.04e-17 | 3.33e-16 |
| random_tree | 10 |  9 | ✓         | ✓      | 1.12e-16 | 7.22e-16 |
| random_tree | 10 |  9 | ✓         | ✓      | 1.95e-16 | 1.33e-15 |
| random_tree |  7 |  6 | ✓         | ✓      | 4.08e-17 | 6.66e-16 |
| random_tree |  7 |  6 | ✓         | ✓      | 7.26e-18 | 1.11e-16 |
| random_tree |  6 |  5 | ✓         | ✓      | 2.37e-17 | 2.22e-16 |
| random_tree | 10 |  9 | ✓         | ✓      | 1.65e-16 | 8.88e-16 |
| random_tree | 11 | 10 | ✓         | ✓      | 3.17e-16 | 1.33e-15 |
| random_tree | 11 | 10 | ✓         | ✓      | 1.20e-16 | 6.66e-16 |
| random_tree | 10 |  9 | ✓         | ✓      | 2.21e-16 | 5.55e-16 |
| random_tree |  5 |  4 | ✓         | ✓      | 3.84e-17 | 2.22e-16 |
| random_tree |  5 |  4 | ✓         | ✓      | 7.50e-17 | 2.22e-16 |

## Conclusion

**CONJECTURE VERIFIED** ✓

All tested tree configurations satisfy:
1. Fisher matrix is diagonal to machine precision
2. Diagonal entries match sech²(J_e) to machine precision

**Implication:** The Tree Fisher Identity (uniform case) extends naturally to non-uniform couplings. Each edge variable σ_e is independent with variance sech²(J_e), regardless of the coupling values on other edges.

**Next steps:**
- Formal proof of the extension
- Integration into spectral gap analysis
- Test weighted spectral gap W(q) for non-uniform case

---

*Generated by nonuniform_tree_verification.py*
