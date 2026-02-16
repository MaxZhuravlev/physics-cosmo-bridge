#!/usr/bin/env python3
"""
Observer Complexity Phase Diagram

Maps how observer size (m edges), coupling strength (J), and graph density
determine emergent physics regimes (Lorentzian vs non-Lorentzian).

Research Question:
    What combinations of (m, J, graph_type) lead to q=1 spectral gap selection
    (Lorentzian signature) vs higher q (non-Lorentzian)?

Method:
    For each (m, J, graph_type) triple:
    1. Generate 10 random graphs with specified parameters
    2. Compute exact Ising Fisher matrix via Boltzmann enumeration
    3. Compute spectral gap metrics:
       - W(q=1) vs max W(q>=2) for Lorentzian selection
       - Near-diagonal ratio ||F - diag(F)|| / ||diag(F)||
       - beta_c = critical temperature for Lorentzian-Riemannian transition
       - Effective dimensionality
    4. Average over 10 random instances

Output:
    Phase diagram showing:
    - Fraction of J values where q=1 wins vs (m, graph_type)
    - Critical J_c for Lorentzian→non-Lorentzian transition
    - Near-diagonal ratio as function of parameters

Attribution:
    test_id: TEST-BRIDGE-MVP1-OBSERVER-PHASE-001
    mvp_layer: MVP-1
    vector_id: observer-complexity-regime-mapping
    dialogue_id: session-2026-02-16-phase-diagram
    recovery_path: output/observer_phase_diagram_results.md
"""

import numpy as np
import itertools
import networkx as nx
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
from collections import defaultdict
import time


@dataclass
class PhasePoint:
    """Single (m, J, graph_type) configuration result."""
    m: int  # Number of edges (observer parameters)
    J: float  # Coupling strength
    graph_type: str  # tree, sparse, dense
    n_vertices: int  # Number of vertices

    # Spectral gap metrics (averaged over random instances)
    q1_win_fraction: float  # Fraction where W(q=1) > max W(q>=2)
    mean_W_q1: float
    mean_W_max_higher: float
    mean_near_diagonal_ratio: float
    mean_beta_c: float
    mean_effective_dim: float

    # Standard deviations
    std_W_q1: float = 0.0
    std_near_diagonal: float = 0.0

    n_instances: int = 10  # Number of random graphs averaged


@dataclass
class PhaseResults:
    """Complete phase diagram results."""
    points: List[PhasePoint]

    def filter(self, m: Optional[int] = None,
               graph_type: Optional[str] = None) -> List[PhasePoint]:
        """Filter points by m and/or graph_type."""
        filtered = self.points
        if m is not None:
            filtered = [p for p in filtered if p.m == m]
        if graph_type is not None:
            filtered = [p for p in filtered if p.graph_type == graph_type]
        return filtered

    def get_critical_J(self, m: int, graph_type: str, threshold: float = 0.5) -> Optional[float]:
        """
        Find critical J where q1_win_fraction crosses threshold.

        Returns:
            J_c: Critical coupling (None if no crossing found)
        """
        points = sorted(
            [p for p in self.filter(m=m, graph_type=graph_type)],
            key=lambda p: p.J
        )

        if len(points) < 2:
            return None

        # Find first crossing
        for i in range(len(points) - 1):
            if points[i].q1_win_fraction >= threshold and points[i+1].q1_win_fraction < threshold:
                # Linear interpolation
                J1, f1 = points[i].J, points[i].q1_win_fraction
                J2, f2 = points[i+1].J, points[i+1].q1_win_fraction
                J_c = J1 + (threshold - f1) * (J2 - J1) / (f2 - f1)
                return J_c
            elif points[i].q1_win_fraction < threshold and points[i+1].q1_win_fraction >= threshold:
                J1, f1 = points[i].J, points[i].q1_win_fraction
                J2, f2 = points[i+1].J, points[i+1].q1_win_fraction
                J_c = J1 + (threshold - f1) * (J2 - J1) / (f2 - f1)
                return J_c

        return None


def compute_exact_fisher_ising(G: nx.Graph, J: float) -> np.ndarray:
    """
    Compute exact Ising Fisher matrix via Boltzmann enumeration.

    Args:
        G: NetworkX graph
        J: Uniform coupling strength

    Returns:
        F: (m, m) Fisher information matrix where m = number of edges
    """
    edges = list(G.edges())
    m = len(edges)
    N = G.number_of_nodes()
    nodes = list(G.nodes())

    if N > 14:
        raise ValueError(f"Graph too large for exact enumeration: N={N} > 14")

    # Enumerate all 2^N spin configurations
    configs = list(itertools.product([-1, 1], repeat=N))

    # Sufficient statistics T_e = s_i * s_j for each edge
    T = np.zeros((len(configs), m))
    weights = np.zeros(len(configs))

    for idx, config in enumerate(configs):
        spins = np.array(config)
        for e_idx, (i, j) in enumerate(edges):
            # Map node labels to indices
            ni = nodes.index(i)
            nj = nodes.index(j)
            T[idx, e_idx] = spins[ni] * spins[nj]

        # Hamiltonian: H = -J * sum_{edges} s_i * s_j
        energy = -J * np.sum(T[idx])
        weights[idx] = np.exp(-energy)

    # Normalize to get probabilities
    Z = np.sum(weights)
    if Z == 0:
        return np.eye(m) * 1e-6  # Fallback
    probs = weights / Z

    # Fisher = Cov(T) under Boltzmann distribution
    mean_T = probs @ T
    T_centered = T - mean_T
    F = (T_centered * probs[:, None]).T @ T_centered

    # Stabilize
    F += 1e-9 * np.eye(m)

    return F


def compute_spectral_gap_q1(F: np.ndarray) -> Tuple[float, float, float]:
    """
    Compute spectral gap selection for q=1.

    Returns:
        W_q1: Spectral gap weighting for q=1
        W_max_higher: Maximum W(q) for q >= 2
        beta_c: Critical beta for q=1
    """
    m = F.shape[0]

    if m < 3:
        return 0.0, 0.0, 0.0

    # Stabilize F
    vals, vecs = np.linalg.eigh(F)
    vals = np.maximum(vals, 1e-10)
    F_sqrt = vecs @ np.diag(np.sqrt(vals)) @ vecs.T
    F_inv_sqrt = vecs @ np.diag(1.0 / np.sqrt(vals)) @ vecs.T

    # For exponential family: M = F^2
    M = F @ F

    # Compute beta_c(q) for all q
    W_values = {}
    beta_c_values = {}

    for q in range(1, min(m, 6)):  # Limit q to save computation
        best_beta_c = -1.0
        best_L_gap = 0.0

        # Sample sign assignments (exhaustive if m <= 10)
        if m <= 10:
            sign_assignments = list(itertools.combinations(range(m), q))
        else:
            # Random sampling
            rng = np.random.default_rng(42)
            sign_assignments = []
            for _ in range(min(500, 2**m)):
                perm = rng.permutation(m)
                sign_assignments.append(tuple(perm[:q]))

        for neg_indices in sign_assignments:
            S_diag = np.ones(m)
            if len(neg_indices) > 0:
                S_diag[list(neg_indices)] = -1.0

            S = np.diag(S_diag)

            # Transformed metric: g = M + beta*F with S signature
            # Eigenvalues of F^{-1/2} S M S F^{-1/2}
            A = F_inv_sqrt @ S @ M @ S @ F_inv_sqrt

            eigs = np.linalg.eigvalsh(A)
            min_eig = eigs[0]
            second_eig = eigs[1] if len(eigs) > 1 else min_eig

            if min_eig < 0:
                beta_c = -min_eig
                L_gap = (second_eig - min_eig) / abs(min_eig) if min_eig != 0 else 0.0

                if beta_c > best_beta_c:
                    best_beta_c = beta_c
                    best_L_gap = L_gap

        W = best_beta_c * best_L_gap if best_beta_c > 0 else 0.0
        W_values[q] = W
        beta_c_values[q] = best_beta_c

    W_q1 = W_values.get(1, 0.0)
    W_max_higher = max((W_values[q] for q in W_values if q >= 2), default=0.0)
    beta_c = beta_c_values.get(1, 0.0)

    return W_q1, W_max_higher, beta_c


def compute_near_diagonal_ratio(F: np.ndarray) -> float:
    """
    Compute ||F - diag(F)|| / ||diag(F)||.

    Returns:
        ratio: Near-diagonal ratio (0 = perfectly diagonal)
    """
    diag_F = np.diag(np.diag(F))
    off_diag = F - diag_F

    norm_diag = np.linalg.norm(diag_F, 'fro')
    norm_off = np.linalg.norm(off_diag, 'fro')

    if norm_diag == 0:
        return 1.0 if norm_off > 0 else 0.0

    return norm_off / norm_diag


def compute_effective_dim(F: np.ndarray, threshold: float = 1e-10) -> int:
    """
    Compute effective dimensionality = rank of F.

    Returns:
        rank: Number of eigenvalues > threshold * max_eigenvalue
    """
    eigs = np.linalg.eigvalsh(F)
    max_eig = np.max(eigs)
    if max_eig == 0:
        return 0
    return np.sum(eigs > threshold * max_eig)


def generate_random_graph(m: int, graph_type: str, seed: int) -> nx.Graph:
    """
    Generate random graph with approximately m edges.

    Args:
        m: Target number of edges
        graph_type: 'tree', 'sparse', 'dense'
        seed: Random seed

    Returns:
        G: NetworkX graph
    """
    rng = np.random.RandomState(seed)

    if graph_type == 'tree':
        # Random tree on N=m+1 vertices (exactly m edges)
        N = m + 1
        if N < 2:
            N = 2
        G = nx.random_labeled_tree(N, seed=seed)

    elif graph_type == 'sparse':
        # Random sparse graph with ~m edges
        # Use N vertices, add m edges randomly
        N = max(m + 1, 4)
        G = nx.Graph()
        G.add_nodes_from(range(N))

        # Ensure connected
        for i in range(N - 1):
            G.add_edge(i, i + 1)

        # Add remaining edges randomly
        edges_to_add = max(0, m - (N - 1))
        possible_edges = [(i, j) for i in range(N) for j in range(i+1, N) if not G.has_edge(i, j)]

        if len(possible_edges) > 0 and edges_to_add > 0:
            selected = rng.choice(len(possible_edges),
                                  size=min(edges_to_add, len(possible_edges)),
                                  replace=False)
            for idx in selected:
                i, j = possible_edges[idx]
                G.add_edge(i, j)

    elif graph_type == 'dense':
        # Dense graph: complete graph K_N where m ≈ N(N-1)/2
        # Solve N(N-1)/2 = m → N ≈ sqrt(2m)
        N = max(3, int(np.sqrt(2 * m)))
        if N * (N - 1) // 2 < m:
            N += 1
        G = nx.complete_graph(N)

    else:
        raise ValueError(f"Unknown graph_type: {graph_type}")

    return G


def analyze_phase_point(m: int, J: float, graph_type: str,
                        n_instances: int = 10) -> PhasePoint:
    """
    Analyze single phase point by averaging over random graph instances.

    Args:
        m: Number of edges (observer size)
        J: Coupling strength
        graph_type: 'tree', 'sparse', 'dense'
        n_instances: Number of random graphs to average

    Returns:
        PhasePoint with averaged metrics
    """
    q1_wins = []
    W_q1_values = []
    W_max_higher_values = []
    near_diag_values = []
    beta_c_values = []
    eff_dim_values = []

    n_vertices_list = []

    for instance in range(n_instances):
        seed = 42 + instance

        try:
            # Generate graph
            G = generate_random_graph(m, graph_type, seed)
            n_vertices = G.number_of_nodes()
            m_actual = G.number_of_edges()

            if n_vertices > 14:
                # Skip if too large
                continue

            n_vertices_list.append(n_vertices)

            # Compute Fisher matrix
            F = compute_exact_fisher_ising(G, J)

            if F.shape[0] < 3:
                continue

            # Spectral gap analysis
            W_q1, W_max_higher, beta_c = compute_spectral_gap_q1(F)

            # Other metrics
            near_diag = compute_near_diagonal_ratio(F)
            eff_dim = compute_effective_dim(F)

            # Record
            q1_wins.append(1.0 if W_q1 > W_max_higher else 0.0)
            W_q1_values.append(W_q1)
            W_max_higher_values.append(W_max_higher)
            near_diag_values.append(near_diag)
            beta_c_values.append(beta_c)
            eff_dim_values.append(eff_dim)

        except Exception as e:
            print(f"  Warning: Failed instance {instance} for m={m}, J={J:.2f}, {graph_type}: {e}")
            continue

    if len(q1_wins) == 0:
        # No valid instances
        return PhasePoint(
            m=m, J=J, graph_type=graph_type, n_vertices=0,
            q1_win_fraction=0.0, mean_W_q1=0.0, mean_W_max_higher=0.0,
            mean_near_diagonal_ratio=0.0, mean_beta_c=0.0, mean_effective_dim=0.0,
            std_W_q1=0.0, std_near_diagonal=0.0, n_instances=0
        )

    # Compute averages
    n_vertices_avg = int(np.mean(n_vertices_list)) if n_vertices_list else 0

    return PhasePoint(
        m=m,
        J=J,
        graph_type=graph_type,
        n_vertices=n_vertices_avg,
        q1_win_fraction=np.mean(q1_wins),
        mean_W_q1=np.mean(W_q1_values),
        mean_W_max_higher=np.mean(W_max_higher_values),
        mean_near_diagonal_ratio=np.mean(near_diag_values),
        mean_beta_c=np.mean(beta_c_values),
        mean_effective_dim=np.mean(eff_dim_values),
        std_W_q1=np.std(W_q1_values),
        std_near_diagonal=np.std(near_diag_values),
        n_instances=len(q1_wins)
    )


def run_phase_scan() -> PhaseResults:
    """
    Run complete phase diagram scan.

    Returns:
        PhaseResults object with all phase points
    """
    # Parameter ranges
    m_values = [2, 3, 4, 5, 6, 7, 8, 10, 12, 15]
    J_values = [0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0]
    graph_types = ['tree', 'sparse', 'dense']

    points = []
    total = len(m_values) * len(J_values) * len(graph_types)
    counter = 0

    print("=" * 80)
    print("OBSERVER COMPLEXITY PHASE DIAGRAM SCAN")
    print("=" * 80)
    print(f"\nTotal configurations: {total}")
    print(f"Parameters: m ∈ {m_values}, J ∈ {J_values}")
    print(f"Graph types: {graph_types}")
    print(f"Instances per point: 10\n")
    print("-" * 80)

    for m in m_values:
        for graph_type in graph_types:
            for J in J_values:
                counter += 1
                print(f"[{counter}/{total}] Analyzing m={m:2d}, J={J:.2f}, {graph_type:8s}...",
                      end=" ", flush=True)

                start_time = time.time()
                point = analyze_phase_point(m, J, graph_type, n_instances=10)
                elapsed = time.time() - start_time

                points.append(point)

                print(f"q1_win={point.q1_win_fraction:.2f}, W_q1={point.mean_W_q1:.3f} ({elapsed:.1f}s)")

    return PhaseResults(points=points)


def write_results(results: PhaseResults, output_path: str):
    """Write comprehensive phase diagram results to markdown."""

    with open(output_path, 'w') as f:
        f.write("# Observer Complexity Phase Diagram Results\n\n")
        f.write("**Generated:** 2026-02-16\n")
        f.write("**Attribution:** TEST-BRIDGE-MVP1-OBSERVER-PHASE-001\n\n")

        f.write("## Research Question\n\n")
        f.write("How do observer size (m edges), coupling strength (J), and graph topology ")
        f.write("determine emergent physics regimes (Lorentzian q=1 vs non-Lorentzian q≥2)?\n\n")

        f.write("## Method\n\n")
        f.write("1. For each (m, J, graph_type) triple, generate 10 random graph instances\n")
        f.write("2. Compute exact Ising Fisher matrix via Boltzmann enumeration (2^N configs)\n")
        f.write("3. Compute spectral gap metrics:\n")
        f.write("   - W(q=1) vs max W(q≥2) for Lorentzian selection\n")
        f.write("   - Near-diagonal ratio: ||F - diag(F)|| / ||diag(F)||\n")
        f.write("   - beta_c: Critical temperature for Lorentzian-Riemannian transition\n")
        f.write("   - Effective dimensionality: rank of F\n")
        f.write("4. Average metrics over 10 random instances\n\n")

        f.write("## Summary Statistics\n\n")

        # Overall statistics
        all_points = results.points
        total = len(all_points)
        mean_q1_fraction = np.mean([p.q1_win_fraction for p in all_points])

        f.write(f"**Total configurations analyzed:** {total}\n")
        f.write(f"**Mean q=1 win fraction:** {mean_q1_fraction:.3f}\n\n")

        # By graph type
        f.write("### By Graph Type\n\n")
        f.write("| Graph Type | Mean q=1 Win Fraction | Std Dev |\n")
        f.write("|------------|----------------------|----------|\n")

        for gtype in ['tree', 'sparse', 'dense']:
            filtered = results.filter(graph_type=gtype)
            if len(filtered) > 0:
                fractions = [p.q1_win_fraction for p in filtered]
                mean_frac = np.mean(fractions)
                std_frac = np.std(fractions)
                f.write(f"| {gtype:10s} | {mean_frac:20.3f} | {std_frac:8.3f} |\n")

        f.write("\n")

        # By observer size m
        f.write("### By Observer Size (m)\n\n")
        f.write("| m | Mean q=1 Win Fraction | Mean Near-Diagonal Ratio |\n")
        f.write("|---|----------------------|-------------------------|\n")

        m_values = sorted(set(p.m for p in all_points))
        for m in m_values:
            filtered = results.filter(m=m)
            if len(filtered) > 0:
                fractions = [p.q1_win_fraction for p in filtered]
                near_diag = [p.mean_near_diagonal_ratio for p in filtered]
                mean_frac = np.mean(fractions)
                mean_nd = np.mean(near_diag)
                f.write(f"| {m:2d} | {mean_frac:20.3f} | {mean_nd:23.3f} |\n")

        f.write("\n")

        # Critical J analysis
        f.write("### Critical Coupling J_c (50% threshold)\n\n")
        f.write("Critical J where q=1 win fraction crosses 50%.\n\n")
        f.write("| m | tree | sparse | dense |\n")
        f.write("|---|------|--------|-------|\n")

        for m in m_values:
            row = f"| {m:2d} |"
            for gtype in ['tree', 'sparse', 'dense']:
                J_c = results.get_critical_J(m, gtype, threshold=0.5)
                if J_c is not None:
                    row += f" {J_c:4.2f} |"
                else:
                    row += "  N/A |"
            f.write(row + "\n")

        f.write("\n")

        # Detailed results table
        f.write("## Detailed Results\n\n")
        f.write("| m | J | Graph | N | q1_win | W(q=1) | W_max | Near-Diag | beta_c | eff_dim |\n")
        f.write("|---|---|-------|---|--------|--------|-------|-----------|--------|----------|\n")

        # Sort by m, graph_type, J
        sorted_points = sorted(all_points, key=lambda p: (p.m, p.graph_type, p.J))

        for p in sorted_points:
            f.write(f"| {p.m:2d} | {p.J:3.1f} | {p.graph_type:7s} | {p.n_vertices:2d} | "
                   f"{p.q1_win_fraction:6.2f} | {p.mean_W_q1:6.3f} | {p.mean_W_max_higher:6.3f} | "
                   f"{p.mean_near_diagonal_ratio:8.3f} | {p.mean_beta_c:6.3f} | "
                   f"{p.mean_effective_dim:7.1f} |\n")

        f.write("\n")

        # Interpretation
        f.write("## Interpretation\n\n")

        if mean_q1_fraction > 0.6:
            f.write("**FINDING:** Observer complexity generally favors Lorentzian signature (q=1) ")
            f.write(f"in {mean_q1_fraction*100:.1f}% of configurations.\n\n")
            f.write("The spectral gap selection mechanism successfully identifies q=1 as dominant ")
            f.write("for typical observer parameter regimes.\n\n")
        elif mean_q1_fraction > 0.4:
            f.write("**FINDING:** Lorentzian signature (q=1) selection is MIXED, winning in ")
            f.write(f"{mean_q1_fraction*100:.1f}% of configurations.\n\n")
            f.write("Both Lorentzian and non-Lorentzian regimes are accessible depending on ")
            f.write("observer complexity (m), coupling (J), and topology.\n\n")
        else:
            f.write("**FINDING:** Non-Lorentzian signatures (q≥2) DOMINATE, with q=1 winning in only ")
            f.write(f"{mean_q1_fraction*100:.1f}% of configurations.\n\n")
            f.write("This is a NEGATIVE RESULT for the universal Lorentzian selection hypothesis.\n\n")

        # Topology dependence
        tree_frac = np.mean([p.q1_win_fraction for p in results.filter(graph_type='tree')])
        sparse_frac = np.mean([p.q1_win_fraction for p in results.filter(graph_type='sparse')])
        dense_frac = np.mean([p.q1_win_fraction for p in results.filter(graph_type='dense')])

        f.write("**Topology dependence:**\n")
        f.write(f"- Tree graphs: {tree_frac*100:.1f}% q=1 win rate\n")
        f.write(f"- Sparse graphs: {sparse_frac*100:.1f}% q=1 win rate\n")
        f.write(f"- Dense graphs: {dense_frac*100:.1f}% q=1 win rate\n\n")

        if tree_frac > max(sparse_frac, dense_frac) + 0.1:
            f.write("Tree topology shows strongest Lorentzian preference, consistent with ")
            f.write("diagonal Fisher matrix theorem.\n\n")
        elif dense_frac > max(tree_frac, sparse_frac) + 0.1:
            f.write("Dense graphs favor Lorentzian signature more than sparse, suggesting ")
            f.write("correlation structure plays a role.\n\n")

        # Observer size scaling
        small_m = [p for p in all_points if p.m <= 5]
        large_m = [p for p in all_points if p.m >= 10]

        if len(small_m) > 0 and len(large_m) > 0:
            small_frac = np.mean([p.q1_win_fraction for p in small_m])
            large_frac = np.mean([p.q1_win_fraction for p in large_m])

            f.write("**Observer size scaling:**\n")
            f.write(f"- Small observers (m≤5): {small_frac*100:.1f}% q=1 win rate\n")
            f.write(f"- Large observers (m≥10): {large_frac*100:.1f}% q=1 win rate\n\n")

            if abs(small_frac - large_frac) > 0.15:
                if small_frac > large_frac:
                    f.write("Smaller observers favor Lorentzian signature more strongly.\n\n")
                else:
                    f.write("Larger observers favor Lorentzian signature more strongly.\n\n")

        f.write("## Next Steps\n\n")
        f.write("1. Theoretical analysis: What graph properties predict q=1 selection?\n")
        f.write("2. Larger observers: Extend to m > 15 using approximate methods\n")
        f.write("3. Non-uniform couplings: Test heterogeneous J_{ij}\n")
        f.write("4. Other models: XY, Heisenberg, continuous spin systems\n")
        f.write("5. Connect to physical observables: What does q=1 win/loss mean for emergent spacetime?\n\n")

        f.write("---\n\n")
        f.write("*Generated by observer_phase_diagram.py*\n")


def main():
    """Run phase diagram scan and write results."""

    # Set random seed for reproducibility
    np.random.seed(42)

    print("\n" + "=" * 80)
    print("OBSERVER COMPLEXITY PHASE DIAGRAM")
    print("=" * 80)
    print("\nMapping emergent physics regimes as function of:")
    print("  - Observer size m (number of parameters)")
    print("  - Coupling strength J")
    print("  - Graph topology (tree, sparse, dense)")
    print("\nOutput: Phase diagram showing Lorentzian vs non-Lorentzian selection\n")

    # Run scan
    start_time = time.time()
    results = run_phase_scan()
    total_time = time.time() - start_time

    print("\n" + "=" * 80)
    print(f"Scan complete! Total time: {total_time:.1f}s")
    print("=" * 80)

    # Write results
    output_path = "/Users/Max_1/Projects/PhysicsResearch/cosmological-unification/papers/structural-bridge/output/observer_phase_diagram_results.md"
    write_results(results, output_path)

    print(f"\nResults written to:\n  {output_path}")
    print("\n" + "=" * 80)

    # Quick summary
    all_points = results.points
    mean_q1_fraction = np.mean([p.q1_win_fraction for p in all_points])

    print("\nQUICK SUMMARY:")
    print(f"  Total configurations: {len(all_points)}")
    print(f"  Mean q=1 win fraction: {mean_q1_fraction:.3f}")

    if mean_q1_fraction > 0.6:
        print("  → Lorentzian signature (q=1) DOMINATES")
    elif mean_q1_fraction > 0.4:
        print("  → MIXED regime (both q=1 and q≥2 accessible)")
    else:
        print("  → Non-Lorentzian (q≥2) DOMINATES (negative result)")

    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
