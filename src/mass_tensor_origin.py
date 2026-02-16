#!/usr/bin/env python3
"""
Mass Tensor Origin Investigation

Tests three hypotheses for the physical origin of the mass tensor M in Vanchurin's
Type II framework:

H1: Structural inertia (M = Hessian of log partition function)
H2: Accumulated Fisher (M = time-averaged Fisher along learning trajectory)
H3: Graph connectivity (M related to graph Laplacian)

For exponential family models, we proved M = F² (Paper #1, Theorem).
This script tests which hypothesis best explains this result.

Author: Research Program
Date: 2026-02-16
"""

import numpy as np
from itertools import product
import networkx as nx
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)


def compute_ising_quantities(G: nx.Graph, J: float) -> Dict[str, np.ndarray]:
    """
    Compute F, M=F², and predictions for each hypothesis.

    Args:
        G: NetworkX graph (observer structure)
        J: Coupling strength

    Returns:
        Dictionary with F, M_actual, M_H1, M_H3_v1, M_H3_v2, etc.
    """
    edges = list(G.edges())
    m = len(edges)
    N = G.number_of_nodes()
    nodes = list(G.nodes())

    if N > 10:
        raise ValueError(f"N={N} too large for exact enumeration (max 10)")

    # Enumerate all 2^N spin configurations
    configs = list(product([-1, 1], repeat=N))

    # Sufficient statistics: T[config_idx, edge_idx] = s_i * s_j
    T = np.zeros((len(configs), m))
    for idx, config in enumerate(configs):
        spins = np.array(config)
        for e_idx, (i, j_node) in enumerate(edges):
            ni, nj = nodes.index(i), nodes.index(j_node)
            T[idx, e_idx] = spins[ni] * spins[nj]

    # Natural parameters (uniform coupling)
    theta = J * np.ones(m)

    # Boltzmann distribution: p(s) ∝ exp(-E) = exp(theta · T(s))
    energies = -T @ theta
    weights = np.exp(-energies)
    Z = np.sum(weights)
    probs = weights / Z

    # Fisher information matrix: F = Cov[T(s)]
    mean_T = probs @ T
    T_centered = T - mean_T
    F = (T_centered * probs[:, None]).T @ T_centered

    # Actual M (exponential family theorem)
    M_actual = F @ F

    # =====================================================================
    # H1: Structural Inertia = Hessian of A(theta)
    # =====================================================================
    # A(theta) = log Z(theta) is the log partition function
    # dA/dtheta_a = E[T_a] (first moment)
    # d²A/dtheta_a dtheta_b = Cov[T_a, T_b] = F_ab
    # H1 predicts M = F (NOT F²!)
    M_H1 = F.copy()

    # =====================================================================
    # H3: Graph Connectivity
    # =====================================================================
    # Graph Laplacian: L = D - A (degree matrix - adjacency)
    L_graph = nx.laplacian_matrix(G).toarray().astype(float)

    # Incidence matrix: B[node_i, edge_k] = ±1 if node i touches edge k
    B = np.zeros((N, m))
    for e_idx, (i, j_node) in enumerate(edges):
        ni, nj = nodes.index(i), nodes.index(j_node)
        B[ni, e_idx] = 1
        B[nj, e_idx] = -1

    # Edge Laplacian: L_edge = B^T B
    L_edge = B.T @ B

    # H3 variants:
    # v1: Square of edge Laplacian
    M_H3_v1 = L_edge @ L_edge

    # v2: B^T L² B (graph Laplacian squared, projected to edges)
    M_H3_v2 = B.T @ (L_graph @ L_graph) @ B

    return {
        'F': F,
        'M_actual': M_actual,
        'M_H1': M_H1,
        'M_H3_v1': M_H3_v1,
        'M_H3_v2': M_H3_v2,
        'mean_T': mean_T,
        'theta': theta,
        'Z': Z,
        'probs': probs,
        'T': T,
    }


def simulate_learning(G: nx.Graph, J_target: float,
                     n_steps: int = 1000, lr: float = 0.01) -> Tuple[np.ndarray, np.ndarray]:
    """
    Simulate natural gradient learning and accumulate Fisher matrix.

    Args:
        G: NetworkX graph
        J_target: Target coupling strength to learn
        n_steps: Number of learning steps
        lr: Learning rate

    Returns:
        (M_H2, theta_final): Accumulated Fisher / n_steps, final parameters
    """
    edges = list(G.edges())
    m = len(edges)
    N = G.number_of_nodes()
    nodes = list(G.nodes())

    if N > 10:
        raise ValueError(f"N={N} too large for exact enumeration (max 10)")

    # Enumerate configurations
    configs = list(product([-1, 1], repeat=N))
    T = np.zeros((len(configs), m))
    for idx, config in enumerate(configs):
        spins = np.array(config)
        for e_idx, (i, j_node) in enumerate(edges):
            ni, nj = nodes.index(i), nodes.index(j_node)
            T[idx, e_idx] = spins[ni] * spins[nj]

    # Target distribution
    theta_target = J_target * np.ones(m)
    energies_target = -T @ theta_target
    w_target = np.exp(-energies_target)
    p_target = w_target / np.sum(w_target)
    mean_T_target = p_target @ T

    # Initialize at random theta
    theta = np.random.randn(m) * 0.1

    # Accumulate Fisher along trajectory
    F_accumulated = np.zeros((m, m))

    for step in range(n_steps):
        # Current distribution
        energies = -T @ theta
        w = np.exp(-energies)
        Z = np.sum(w)
        p = w / Z

        # Current Fisher
        mean_T_curr = p @ T
        T_centered = T - mean_T_curr
        F_curr = (T_centered * p[:, None]).T @ T_centered

        # Accumulate
        F_accumulated += F_curr

        # Gradient: direction toward target distribution
        grad = mean_T_target - mean_T_curr

        # Natural gradient step (for exponential family, Fisher is metric)
        theta += lr * grad

    M_H2 = F_accumulated / n_steps

    return M_H2, theta


def relative_error(M_pred: np.ndarray, M_true: np.ndarray) -> float:
    """Compute relative Frobenius norm error."""
    return np.linalg.norm(M_pred - M_true, 'fro') / np.linalg.norm(M_true, 'fro')


def best_scaling_error(M_pred: np.ndarray, M_true: np.ndarray) -> Tuple[float, float]:
    """
    Find best proportionality constant c minimizing ||M_true - c*M_pred||.

    Returns:
        (best_c, relative_error)
    """
    # Least squares: argmin_c ||M_true - c*M_pred||²
    # Solution: c = tr(M_true^T M_pred) / tr(M_pred^T M_pred)
    c_best = np.trace(M_true.T @ M_pred) / np.trace(M_pred.T @ M_pred)
    err = relative_error(c_best * M_pred, M_true)
    return c_best, err


def test_configuration(G: nx.Graph, J: float, config_name: str) -> Dict:
    """
    Test all hypotheses for a given graph configuration.

    Returns:
        Dictionary with errors for each hypothesis
    """
    print(f"\n{'='*60}")
    print(f"Testing: {config_name}, J={J:.2f}")
    print(f"{'='*60}")

    # Compute ground truth and hypothesis predictions
    quantities = compute_ising_quantities(G, J)
    M_actual = quantities['M_actual']
    F = quantities['F']

    # H1: Structural inertia (predicts M = F)
    M_H1 = quantities['M_H1']
    err_H1 = relative_error(M_H1, M_actual)
    c_H1, err_H1_scaled = best_scaling_error(M_H1, M_actual)

    # H2: Accumulated Fisher (learn toward equilibrium)
    print("  Running learning simulation for H2...")
    M_H2, theta_final = simulate_learning(G, J, n_steps=2000, lr=0.02)
    err_H2 = relative_error(M_H2, M_actual)
    c_H2, err_H2_scaled = best_scaling_error(M_H2, M_actual)

    # H3: Graph connectivity
    M_H3_v1 = quantities['M_H3_v1']
    M_H3_v2 = quantities['M_H3_v2']
    err_H3_v1 = relative_error(M_H3_v1, M_actual)
    err_H3_v2 = relative_error(M_H3_v2, M_actual)
    c_H3_v1, err_H3_v1_scaled = best_scaling_error(M_H3_v1, M_actual)
    c_H3_v2, err_H3_v2_scaled = best_scaling_error(M_H3_v2, M_actual)

    # Additional diagnostics
    err_F_vs_actual = relative_error(F, M_actual)  # Should be large (M ≠ F)
    err_F2_vs_actual = relative_error(F @ F, M_actual)  # Should be small (M = F²)

    # Print results
    print(f"\n  Ground truth checks:")
    print(f"    ||M - F|| / ||M|| = {err_F_vs_actual:.4f}  (expect large, M ≠ F)")
    print(f"    ||M - F²|| / ||M|| = {err_F2_vs_actual:.4f}  (expect small, M = F²)")

    print(f"\n  H1 (Structural inertia, predicts M=F):")
    print(f"    ||M - M_H1|| / ||M|| = {err_H1:.4f}")
    print(f"    Best scaling: c={c_H1:.4f}, error={err_H1_scaled:.4f}")

    print(f"\n  H2 (Accumulated Fisher):")
    print(f"    ||M - M_H2|| / ||M|| = {err_H2:.4f}")
    print(f"    Best scaling: c={c_H2:.4f}, error={err_H2_scaled:.4f}")

    print(f"\n  H3 (Graph connectivity):")
    print(f"    v1 (L_edge²): error={err_H3_v1:.4f}, best_c={c_H3_v1:.4f}, scaled_err={err_H3_v1_scaled:.4f}")
    print(f"    v2 (B^T L² B): error={err_H3_v2:.4f}, best_c={c_H3_v2:.4f}, scaled_err={err_H3_v2_scaled:.4f}")

    return {
        'config': config_name,
        'J': J,
        'N': G.number_of_nodes(),
        'm': len(G.edges()),
        'err_F_vs_M': err_F_vs_actual,
        'err_F2_vs_M': err_F2_vs_actual,
        'H1_err': err_H1,
        'H1_c': c_H1,
        'H1_scaled_err': err_H1_scaled,
        'H2_err': err_H2,
        'H2_c': c_H2,
        'H2_scaled_err': err_H2_scaled,
        'H3_v1_err': err_H3_v1,
        'H3_v1_c': c_H3_v1,
        'H3_v1_scaled_err': err_H3_v1_scaled,
        'H3_v2_err': err_H3_v2,
        'H3_v2_c': c_H3_v2,
        'H3_v2_scaled_err': err_H3_v2_scaled,
    }


def generate_test_graphs() -> List[Tuple[nx.Graph, str]]:
    """Generate test graph configurations."""
    graphs = []

    # Path graphs
    for N in [3, 4, 5, 6]:
        graphs.append((nx.path_graph(N), f"Path_N{N}"))

    # Star graphs
    for N in [4, 5, 6]:
        graphs.append((nx.star_graph(N-1), f"Star_N{N}"))

    # Cycle graphs
    for N in [4, 5, 6]:
        graphs.append((nx.cycle_graph(N), f"Cycle_N{N}"))

    # Complete graphs
    for N in [3, 4]:
        graphs.append((nx.complete_graph(N), f"Complete_K{N}"))

    # Random trees
    for N in [5, 6]:
        G = nx.random_labeled_tree(N, seed=42+N)
        graphs.append((G, f"RandomTree_N{N}"))

    return graphs


def main():
    """Run mass tensor origin investigation."""
    print("="*60)
    print("MASS TENSOR ORIGIN INVESTIGATION")
    print("="*60)
    print("\nTesting three hypotheses:")
    print("  H1: Structural inertia (M = Hessian of log Z)")
    print("  H2: Accumulated Fisher (M = time-averaged F)")
    print("  H3: Graph connectivity (M related to Laplacian)")
    print("\nGround truth: M = F² (exponential family theorem)")
    print("="*60)

    # Test configurations
    graphs = generate_test_graphs()
    J_values = [0.1, 0.3, 0.5, 1.0]

    results = []

    for G, name in graphs:
        for J in J_values:
            result = test_configuration(G, J, name)
            results.append(result)

    # Generate summary report
    print("\n\n" + "="*60)
    print("SUMMARY REPORT")
    print("="*60)

    # Aggregate statistics
    avg_H1_err = np.mean([r['H1_err'] for r in results])
    avg_H2_err = np.mean([r['H2_err'] for r in results])
    avg_H3_v1_err = np.mean([r['H3_v1_err'] for r in results])
    avg_H3_v2_err = np.mean([r['H3_v2_err'] for r in results])

    avg_H1_scaled = np.mean([r['H1_scaled_err'] for r in results])
    avg_H2_scaled = np.mean([r['H2_scaled_err'] for r in results])
    avg_H3_v1_scaled = np.mean([r['H3_v1_scaled_err'] for r in results])
    avg_H3_v2_scaled = np.mean([r['H3_v2_scaled_err'] for r in results])

    print(f"\nAverage errors (over {len(results)} configurations):")
    print(f"\n  Ground truth verification:")
    print(f"    M vs F:  {np.mean([r['err_F_vs_M'] for r in results]):.4f} (expect large)")
    print(f"    M vs F²: {np.mean([r['err_F2_vs_M'] for r in results]):.4f} (expect small)")

    print(f"\n  Hypothesis errors (unscaled):")
    print(f"    H1: {avg_H1_err:.4f}")
    print(f"    H2: {avg_H2_err:.4f}")
    print(f"    H3_v1: {avg_H3_v1_err:.4f}")
    print(f"    H3_v2: {avg_H3_v2_err:.4f}")

    print(f"\n  Hypothesis errors (best scaling):")
    print(f"    H1: {avg_H1_scaled:.4f}")
    print(f"    H2: {avg_H2_scaled:.4f}")
    print(f"    H3_v1: {avg_H3_v1_scaled:.4f}")
    print(f"    H3_v2: {avg_H3_v2_scaled:.4f}")

    # Best hypothesis
    errors = {
        'H1': avg_H1_scaled,
        'H2': avg_H2_scaled,
        'H3_v1': avg_H3_v1_scaled,
        'H3_v2': avg_H3_v2_scaled,
    }
    best = min(errors.items(), key=lambda x: x[1])

    print(f"\n  BEST HYPOTHESIS: {best[0]} (avg scaled error: {best[1]:.4f})")

    # Save detailed results
    output_path = "/Users/Max_1/Projects/PhysicsResearch/cosmological-unification/papers/structural-bridge/output/mass_tensor_origin_results.md"

    with open(output_path, 'w') as f:
        f.write("# Mass Tensor Origin Investigation Results\n\n")
        f.write("**Date**: 2026-02-16\n\n")
        f.write("**Purpose**: Identify physical origin of mass tensor M in Vanchurin's Type II framework\n\n")
        f.write("**Ground truth**: M = F² (exponential family theorem, Paper #1)\n\n")

        f.write("## Hypotheses Tested\n\n")
        f.write("- **H1**: Structural inertia — M = Hessian of log partition function = F (EXPECTED TO FAIL)\n")
        f.write("- **H2**: Accumulated Fisher — M = time-averaged Fisher along learning trajectory\n")
        f.write("- **H3**: Graph connectivity — M related to graph Laplacian\n")
        f.write("  - v1: M = L_edge² (edge Laplacian squared)\n")
        f.write("  - v2: M = B^T L² B (graph Laplacian squared, projected to edges)\n\n")

        f.write("## Summary Statistics\n\n")
        f.write(f"**Configurations tested**: {len(results)}\n")
        f.write(f"**Graph types**: Path, Star, Cycle, Complete, Random Tree\n")
        f.write(f"**N values**: 3-6 nodes\n")
        f.write(f"**J values**: 0.1, 0.3, 0.5, 1.0\n\n")

        f.write("### Average Errors (Best Scaling)\n\n")
        f.write("| Hypothesis | Avg Error | Interpretation |\n")
        f.write("|------------|-----------|----------------|\n")
        f.write(f"| H1 (M=F) | {avg_H1_scaled:.4f} | {'FAILED' if avg_H1_scaled > 0.1 else 'PASSED'} |\n")
        f.write(f"| H2 (Accumulated) | {avg_H2_scaled:.4f} | {'FAILED' if avg_H2_scaled > 0.1 else 'PASSED'} |\n")
        f.write(f"| H3_v1 (L_edge²) | {avg_H3_v1_scaled:.4f} | {'FAILED' if avg_H3_v1_scaled > 0.1 else 'PASSED'} |\n")
        f.write(f"| H3_v2 (B^T L² B) | {avg_H3_v2_scaled:.4f} | {'FAILED' if avg_H3_v2_scaled > 0.1 else 'PASSED'} |\n\n")

        f.write("### Ground Truth Verification\n\n")
        f.write(f"- ||M - F|| / ||M|| = {np.mean([r['err_F_vs_M'] for r in results]):.4f} (expect large, M ≠ F)\n")
        f.write(f"- ||M - F²|| / ||M|| = {np.mean([r['err_F2_vs_M'] for r in results]):.4f} (expect ~0, M = F²)\n\n")

        f.write("## Detailed Results\n\n")
        f.write("| Config | J | N | m | H1_err | H2_err | H3_v1_err | H3_v2_err | Best |\n")
        f.write("|--------|---|---|---|--------|--------|-----------|-----------|------|\n")

        for r in results:
            best_h = min([
                ('H1', r['H1_scaled_err']),
                ('H2', r['H2_scaled_err']),
                ('H3_v1', r['H3_v1_scaled_err']),
                ('H3_v2', r['H3_v2_scaled_err']),
            ], key=lambda x: x[1])[0]

            f.write(f"| {r['config']:<12} | {r['J']:.1f} | {r['N']} | {r['m']} | "
                   f"{r['H1_scaled_err']:.3f} | {r['H2_scaled_err']:.3f} | "
                   f"{r['H3_v1_scaled_err']:.3f} | {r['H3_v2_scaled_err']:.3f} | {best_h} |\n")

        f.write("\n## Interpretation\n\n")

        if avg_H1_scaled > 0.1:
            f.write("### H1 (Structural Inertia): FAILED\n\n")
            f.write("H1 predicts M = F (Hessian of log partition function), but ground truth is M = F². ")
            f.write(f"Average error {avg_H1_scaled:.4f} confirms this hypothesis is incorrect.\n\n")

        if avg_H2_scaled < 0.1:
            f.write("### H2 (Accumulated Fisher): PASSED\n\n")
            f.write(f"Average error {avg_H2_scaled:.4f} suggests M is related to time-averaged Fisher ")
            f.write("along learning trajectories. This is the most promising physical interpretation.\n\n")
        else:
            f.write("### H2 (Accumulated Fisher): FAILED\n\n")
            f.write(f"Average error {avg_H2_scaled:.4f} is too high. Learning dynamics may not explain M = F².\n\n")

        if avg_H3_v1_scaled < 0.1 or avg_H3_v2_scaled < 0.1:
            f.write("### H3 (Graph Connectivity): PASSED\n\n")
            best_v3 = 'v1' if avg_H3_v1_scaled < avg_H3_v2_scaled else 'v2'
            best_v3_err = min(avg_H3_v1_scaled, avg_H3_v2_scaled)
            f.write(f"H3_{best_v3} achieved error {best_v3_err:.4f}, suggesting M is related to ")
            f.write("graph Laplacian structure. This is a geometric interpretation.\n\n")
        else:
            f.write("### H3 (Graph Connectivity): FAILED\n\n")
            f.write(f"Both variants have errors > 0.1. Graph Laplacian does not explain M = F².\n\n")

        f.write("## Conclusion\n\n")
        f.write(f"**Best hypothesis**: {best[0]} (avg error: {best[1]:.4f})\n\n")

        if best[0] == 'H2':
            f.write("The accumulated Fisher hypothesis suggests that M represents **historical learning**:\n")
            f.write("the mass tensor encodes how much the system has 'learned' or adapted, integrated over time.\n")
            f.write("This aligns with Vanchurin's interpretation of spacetime as emergent from learning dynamics.\n\n")
        elif best[0].startswith('H3'):
            f.write("The graph connectivity hypothesis suggests that M represents **structural rigidity**:\n")
            f.write("the mass tensor is determined by the observer's graph topology (Laplacian).\n")
            f.write("This is a more geometric, static interpretation.\n\n")
        else:
            f.write("Unexpected result: none of the hypotheses explain M = F² well.\n")
            f.write("Further investigation needed.\n\n")

        f.write("## Next Steps\n\n")
        f.write("1. If H2 passed: Derive analytic formula for M as integral of F(t) along gradient flow\n")
        f.write("2. If H3 passed: Prove rigorous relationship between M and graph Laplacian\n")
        f.write("3. Test on larger graphs (N=7-10) if computational budget allows\n")
        f.write("4. Compare to Vanchurin's Type II metric: is M_μν related to Laplacian on hypergraph?\n")

    print(f"\nResults saved to:\n  {output_path}")


if __name__ == "__main__":
    main()
