# Mass Tensor Origin Investigation Results

**Date**: 2026-02-16

**Purpose**: Identify physical origin of mass tensor M in Vanchurin's Type II framework

**Ground truth**: M = F² (exponential family theorem, Paper #1)

## Hypotheses Tested

- **H1**: Structural inertia — M = Hessian of log partition function = F (EXPECTED TO FAIL)
- **H2**: Accumulated Fisher — M = time-averaged Fisher along learning trajectory
- **H3**: Graph connectivity — M related to graph Laplacian
  - v1: M = L_edge² (edge Laplacian squared)
  - v2: M = B^T L² B (graph Laplacian squared, projected to edges)

## Summary Statistics

**Configurations tested**: 56
**Graph types**: Path, Star, Cycle, Complete, Random Tree
**N values**: 3-6 nodes
**J values**: 0.1, 0.3, 0.5, 1.0

### Average Errors (Best Scaling)

| Hypothesis | Avg Error | Interpretation |
|------------|-----------|----------------|
| H1 (M=F) | 0.0711 | PASSED |
| H2 (Accumulated) | 0.0761 | PASSED |
| H3_v1 (L_edge²) | 0.7321 | FAILED |
| H3_v2 (B^T L² B) | 0.7765 | FAILED |

### Ground Truth Verification

- ||M - F|| / ||M|| = 0.7703 (expect large, M ≠ F)
- ||M - F²|| / ||M|| = 0.0000 (expect ~0, M = F²)

## Detailed Results

| Config | J | N | m | H1_err | H2_err | H3_v1_err | H3_v2_err | Best |
|--------|---|---|---|--------|--------|-----------|-----------|------|
| Path_N3      | 0.1 | 3 | 2 | 0.000 | 0.000 | 0.625 | 0.680 | H1 |
| Path_N3      | 0.3 | 3 | 2 | 0.000 | 0.000 | 0.625 | 0.680 | H1 |
| Path_N3      | 0.5 | 3 | 2 | 0.000 | 0.000 | 0.625 | 0.680 | H1 |
| Path_N3      | 1.0 | 3 | 2 | 0.000 | 0.002 | 0.625 | 0.680 | H1 |
| Path_N4      | 0.1 | 4 | 3 | 0.000 | 0.000 | 0.662 | 0.731 | H1 |
| Path_N4      | 0.3 | 4 | 3 | 0.000 | 0.000 | 0.662 | 0.731 | H1 |
| Path_N4      | 0.5 | 4 | 3 | 0.000 | 0.001 | 0.662 | 0.731 | H1 |
| Path_N4      | 1.0 | 4 | 3 | 0.000 | 0.003 | 0.662 | 0.731 | H1 |
| Path_N5      | 0.1 | 5 | 4 | 0.000 | 0.000 | 0.675 | 0.742 | H1 |
| Path_N5      | 0.3 | 5 | 4 | 0.000 | 0.000 | 0.675 | 0.742 | H1 |
| Path_N5      | 0.5 | 5 | 4 | 0.000 | 0.002 | 0.675 | 0.742 | H1 |
| Path_N5      | 1.0 | 5 | 4 | 0.000 | 0.003 | 0.675 | 0.742 | H1 |
| Path_N6      | 0.1 | 6 | 5 | 0.000 | 0.000 | 0.680 | 0.746 | H1 |
| Path_N6      | 0.3 | 6 | 5 | 0.000 | 0.000 | 0.680 | 0.746 | H1 |
| Path_N6      | 0.5 | 6 | 5 | 0.000 | 0.001 | 0.680 | 0.746 | H1 |
| Path_N6      | 1.0 | 6 | 5 | 0.000 | 0.003 | 0.680 | 0.746 | H1 |
| Star_N4      | 0.1 | 4 | 3 | 0.000 | 0.000 | 0.762 | 0.804 | H1 |
| Star_N4      | 0.3 | 4 | 3 | 0.000 | 0.001 | 0.762 | 0.804 | H1 |
| Star_N4      | 0.5 | 4 | 3 | 0.000 | 0.001 | 0.762 | 0.804 | H1 |
| Star_N4      | 1.0 | 4 | 3 | 0.000 | 0.003 | 0.762 | 0.804 | H1 |
| Star_N5      | 0.1 | 5 | 4 | 0.000 | 0.000 | 0.829 | 0.859 | H1 |
| Star_N5      | 0.3 | 5 | 4 | 0.000 | 0.001 | 0.829 | 0.859 | H1 |
| Star_N5      | 0.5 | 5 | 4 | 0.000 | 0.001 | 0.829 | 0.859 | H1 |
| Star_N5      | 1.0 | 5 | 4 | 0.000 | 0.003 | 0.829 | 0.859 | H1 |
| Star_N6      | 0.1 | 6 | 5 | 0.000 | 0.000 | 0.868 | 0.890 | H1 |
| Star_N6      | 0.3 | 6 | 5 | 0.000 | 0.000 | 0.868 | 0.890 | H1 |
| Star_N6      | 0.5 | 6 | 5 | 0.000 | 0.001 | 0.868 | 0.890 | H1 |
| Star_N6      | 1.0 | 6 | 5 | 0.000 | 0.002 | 0.868 | 0.890 | H1 |
| Cycle_N4     | 0.1 | 4 | 4 | 0.017 | 0.018 | 0.708 | 0.788 | H1 |
| Cycle_N4     | 0.3 | 4 | 4 | 0.143 | 0.148 | 0.733 | 0.806 | H1 |
| Cycle_N4     | 0.5 | 4 | 4 | 0.275 | 0.283 | 0.802 | 0.854 | H1 |
| Cycle_N4     | 1.0 | 4 | 4 | 0.331 | 0.365 | 0.876 | 0.908 | H1 |
| Cycle_N5     | 0.1 | 5 | 5 | 0.002 | 0.002 | 0.697 | 0.746 | H1 |
| Cycle_N5     | 0.3 | 5 | 5 | 0.048 | 0.050 | 0.707 | 0.753 | H1 |
| Cycle_N5     | 0.5 | 5 | 5 | 0.172 | 0.180 | 0.755 | 0.792 | H1 |
| Cycle_N5     | 1.0 | 5 | 5 | 0.348 | 0.382 | 0.880 | 0.897 | H1 |
| Cycle_N6     | 0.1 | 6 | 6 | 0.000 | 0.000 | 0.697 | 0.754 | H1 |
| Cycle_N6     | 0.3 | 6 | 6 | 0.015 | 0.016 | 0.701 | 0.756 | H1 |
| Cycle_N6     | 0.5 | 6 | 6 | 0.089 | 0.094 | 0.725 | 0.776 | H1 |
| Cycle_N6     | 1.0 | 6 | 6 | 0.336 | 0.367 | 0.868 | 0.891 | H1 |
| Complete_K3  | 0.1 | 3 | 3 | 0.141 | 0.141 | 0.546 | 0.546 | H1 |
| Complete_K3  | 0.3 | 3 | 3 | 0.279 | 0.284 | 0.640 | 0.640 | H1 |
| Complete_K3  | 0.5 | 3 | 3 | 0.284 | 0.295 | 0.699 | 0.699 | H1 |
| Complete_K3  | 1.0 | 3 | 3 | 0.256 | 0.285 | 0.733 | 0.733 | H1 |
| Complete_K4  | 0.1 | 4 | 6 | 0.227 | 0.229 | 0.674 | 0.674 | H1 |
| Complete_K4  | 0.3 | 4 | 6 | 0.369 | 0.376 | 0.803 | 0.803 | H1 |
| Complete_K4  | 0.5 | 4 | 6 | 0.329 | 0.342 | 0.837 | 0.837 | H1 |
| Complete_K4  | 1.0 | 4 | 6 | 0.317 | 0.363 | 0.837 | 0.837 | H1 |
| RandomTree_N5 | 0.1 | 5 | 4 | 0.000 | 0.000 | 0.675 | 0.742 | H1 |
| RandomTree_N5 | 0.3 | 5 | 4 | 0.000 | 0.001 | 0.675 | 0.742 | H1 |
| RandomTree_N5 | 0.5 | 5 | 4 | 0.000 | 0.003 | 0.675 | 0.742 | H1 |
| RandomTree_N5 | 1.0 | 5 | 4 | 0.000 | 0.002 | 0.675 | 0.742 | H1 |
| RandomTree_N6 | 0.1 | 6 | 5 | 0.000 | 0.001 | 0.743 | 0.804 | H1 |
| RandomTree_N6 | 0.3 | 6 | 5 | 0.000 | 0.001 | 0.743 | 0.804 | H1 |
| RandomTree_N6 | 0.5 | 6 | 5 | 0.000 | 0.001 | 0.743 | 0.804 | H1 |
| RandomTree_N6 | 1.0 | 6 | 5 | 0.000 | 0.004 | 0.743 | 0.804 | H1 |

## Interpretation

### H2 (Accumulated Fisher): PASSED

Average error 0.0761 suggests M is related to time-averaged Fisher along learning trajectories. This is the most promising physical interpretation.

### H3 (Graph Connectivity): FAILED

Both variants have errors > 0.1. Graph Laplacian does not explain M = F².

## Conclusion

**Best hypothesis**: H1 (avg error: 0.0711)

Unexpected result: none of the hypotheses explain M = F² well.
Further investigation needed.

## Next Steps

1. If H2 passed: Derive analytic formula for M as integral of F(t) along gradient flow
2. If H3 passed: Prove rigorous relationship between M and graph Laplacian
3. Test on larger graphs (N=7-10) if computational budget allows
4. Compare to Vanchurin's Type II metric: is M_μν related to Laplacian on hypergraph?
