#!/usr/bin/env python3
"""
Dimensionality Selection Study for Information Geometry

Research Question:
    Does information geometry select a preferred spatial dimension d?
    Specifically, do Ising observers on d-dimensional lattices show
    non-trivial dependence on d, particularly whether d=3 or d=4 is special?

Method:
    1. Generate Ising observers on d-dimensional lattice graphs for d=1,2,3,4,5
    2. For each (d, J) configuration:
       - Compute exact Fisher matrix F
       - Measure near-diagonal ratio ||F - diag(F)||_op / ||diag(F)||_op
       - Measure spectral gap ratio W(q=1) / max W(q>=2)
       - Measure effective rank
       - Compute critical beta beta_c
       - Record graph girth
    3. Look for:
       - Non-trivial d-dependence (especially if d=3 or d=4 is special)
       - Whether near-diagonal structure varies systematically with d
       - Whether spectral gap selection differs by dimension
       - Phase transitions or crossovers as function of d

Limitations:
    - N limited to ≤16 vertices (2^16 = 65536 states feasible)
    - d=1: L=9 (chain with 9 vertices)
    - d=2: L=3 (3x3 grid, 9 vertices)
    - d=3: L=2 (2x2x2 cube, 8 vertices)
    - d=4: L=2 (2x2x2x2 hypercube, 16 vertices)
    - d=5: Skipped (2^32 states infeasible, smaller lattices too sparse)

Attribution:
    test_id: TEST-BRIDGE-MVP1-DIMENSION-SELECTION-001
    mvp_layer: MVP-1
    dialogue_id: session-2026-02-16-dimension-selection
"""

import numpy as np
import itertools
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import networkx as nx


@dataclass
class DimensionResult:
    """Results for a single (dimension, linear_size, J) configuration."""
    dimension: int
    linear_size: int
    n_vertices: int
    n_edges: int
    girth: int
    coupling_J: float

    # Fisher matrix structure
    near_diagonal_ratio: float
    diag_mean: float
    diag_std: float
    off_diag_rms: float

    # Spectral properties
    spectral_gap_W_q1: float
    spectral_gap_W_max_higher: float
    spectral_gap_ratio: float  # W(q=1) / max W(q>=2)
    q1_wins: bool

    # Effective rank
    effective_rank: int
    rank_ratio: float  # effective_rank / m

    # Critical beta
    beta_c: float

    # Full eigenvalue spectrum
    F_eigenvalues: np.ndarray


def create_lattice_graph(dimension: int, linear_size: int) -> nx.Graph:
    """
    Create d-dimensional lattice graph.

    Args:
        dimension: Spatial dimension (1, 2, 3, 4, 5)
        linear_size: Linear size L (lattice has L^d vertices)

    Returns:
        NetworkX graph representing the lattice
    """
    if dimension == 1:
        # 1D chain
        return nx.path_graph(linear_size)

    elif dimension == 2:
        # 2D square lattice
        return nx.grid_2d_graph(linear_size, linear_size)

    elif dimension == 3:
        # 3D cubic lattice
        G = nx.Graph()
        # Add vertices
        for i in range(linear_size):
            for j in range(linear_size):
                for k in range(linear_size):
                    G.add_node((i, j, k))

        # Add edges (nearest neighbors)
        for i in range(linear_size):
            for j in range(linear_size):
                for k in range(linear_size):
                    # x-direction
                    if i < linear_size - 1:
                        G.add_edge((i, j, k), (i+1, j, k))
                    # y-direction
                    if j < linear_size - 1:
                        G.add_edge((i, j, k), (i, j+1, k))
                    # z-direction
                    if k < linear_size - 1:
                        G.add_edge((i, j, k), (i, j, k+1))

        return G

    elif dimension == 4:
        # 4D hypercubic lattice
        G = nx.Graph()
        # Add vertices
        for i in range(linear_size):
            for j in range(linear_size):
                for k in range(linear_size):
                    for l in range(linear_size):
                        G.add_node((i, j, k, l))

        # Add edges (nearest neighbors)
        for i in range(linear_size):
            for j in range(linear_size):
                for k in range(linear_size):
                    for l in range(linear_size):
                        # w-direction
                        if i < linear_size - 1:
                            G.add_edge((i, j, k, l), (i+1, j, k, l))
                        # x-direction
                        if j < linear_size - 1:
                            G.add_edge((i, j, k, l), (i, j+1, k, l))
                        # y-direction
                        if k < linear_size - 1:
                            G.add_edge((i, j, k, l), (i, j, k+1, l))
                        # z-direction
                        if l < linear_size - 1:
                            G.add_edge((i, j, k, l), (i, j, k, l+1))

        return G

    elif dimension == 5:
        # 5D hypercubic lattice (only for small L)
        G = nx.Graph()
        # Add vertices
        for i in range(linear_size):
            for j in range(linear_size):
                for k in range(linear_size):
                    for l in range(linear_size):
                        for m in range(linear_size):
                            G.add_node((i, j, k, l, m))

        # Add edges (nearest neighbors)
        for i in range(linear_size):
            for j in range(linear_size):
                for k in range(linear_size):
                    for l in range(linear_size):
                        for m in range(linear_size):
                            # 5 directions
                            if i < linear_size - 1:
                                G.add_edge((i, j, k, l, m), (i+1, j, k, l, m))
                            if j < linear_size - 1:
                                G.add_edge((i, j, k, l, m), (i, j+1, k, l, m))
                            if k < linear_size - 1:
                                G.add_edge((i, j, k, l, m), (i, j, k+1, l, m))
                            if l < linear_size - 1:
                                G.add_edge((i, j, k, l, m), (i, j, k, l+1, m))
                            if m < linear_size - 1:
                                G.add_edge((i, j, k, l, m), (i, j, k, l, m+1))

        return G

    else:
        raise ValueError(f"Unsupported dimension: {dimension}")


def compute_exact_fisher_ising(G: nx.Graph, J: float = 1.0) -> Tuple[np.ndarray, List[Tuple]]:
    """
    Compute exact Fisher Information Matrix for Ising model on graph G.

    H(s) = -J * sum_{(i,j) in E} s_i s_j
    P(s) = exp(-H(s)) / Z

    Returns:
        F: (m, m) Fisher matrix in edge parameterization
        edges: List of edge tuples
    """
    # Get edges and nodes
    edges = list(G.edges())
    m = len(edges)
    n = G.number_of_nodes()

    if m == 0:
        return np.zeros((0, 0)), []

    # Create node index mapping
    nodes = list(G.nodes())
    node_to_idx = {node: idx for idx, node in enumerate(nodes)}

    # Convert edges to index pairs
    edges_idx = [(node_to_idx[u], node_to_idx[v]) for u, v in edges]

    # Generate all 2^n spin configurations
    states = np.array(list(itertools.product([-1, 1], repeat=n)))

    # Compute edge variables sigma_e = s_i * s_j for each configuration
    sigma = np.zeros((2**n, m))
    for k, (i, j) in enumerate(edges_idx):
        sigma[:, k] = states[:, i] * states[:, j]

    # Compute energies
    energies = -J * np.sum(sigma, axis=1)

    # Boltzmann probabilities (beta=1)
    min_E = np.min(energies)
    weights = np.exp(-(energies - min_E))
    Z = np.sum(weights)
    probs = weights / Z

    # Fisher matrix = Cov(sigma)
    mean_sigma = probs @ sigma
    centered_sigma = sigma - mean_sigma
    F = (centered_sigma * probs[:, None]).T @ centered_sigma

    return F, edges


def compute_girth(G: nx.Graph) -> int:
    """
    Compute the girth (shortest cycle length) of graph G.

    Returns:
        girth: Shortest cycle length, or 999 if acyclic (tree)
    """
    if not nx.is_connected(G):
        # For disconnected graphs, compute girth of largest component
        components = list(nx.connected_components(G))
        largest_component = max(components, key=len)
        G = G.subgraph(largest_component).copy()

    n = G.number_of_nodes()
    m = G.number_of_edges()

    # Trees have n-1 edges
    if m == n - 1:
        return 999  # Use large number for trees

    # Use BFS from each node to find shortest cycle
    min_cycle = float('inf')

    for start in G.nodes():
        # BFS to find shortest cycle through start
        distances = {start: 0}
        parent = {start: None}
        queue = [start]

        while queue:
            u = queue.pop(0)
            for v in G.neighbors(u):
                if v not in distances:
                    distances[v] = distances[u] + 1
                    parent[v] = u
                    queue.append(v)
                elif parent[u] != v:
                    # Found a cycle
                    cycle_len = distances[u] + distances[v] + 1
                    min_cycle = min(min_cycle, cycle_len)

    return int(min_cycle) if min_cycle != float('inf') else 999


def compute_spectral_gap_for_q(
    F: np.ndarray,
    q: int,
    exhaustive_threshold: int = 12
) -> Tuple[float, float, float]:
    """
    Compute beta_c(q), L_gap(q), W(q) for given q.

    Returns:
        beta_c: Maximum beta_c for this q
        L_gap: Spectral gap at optimal assignment
        W: Weighting W(q) = beta_c * L_gap
    """
    m = F.shape[0]

    if q < 0 or q > m:
        raise ValueError(f"q must be in [0, m], got q={q}, m={m}")

    # Stabilize F
    F_stab = F + 1e-9 * np.eye(m)
    vals, vecs = np.linalg.eigh(F_stab)
    F_sqrt = vecs @ np.diag(np.sqrt(np.maximum(vals, 0))) @ vecs.T

    best_beta_c = -1.0
    best_L_gap = 0.0

    # Generate sign assignments
    if m <= exhaustive_threshold:
        # Exhaustive enumeration
        sign_assignments = itertools.combinations(range(m), q)
    else:
        # Random sampling (1000 samples)
        n_samples = 1000
        rng = np.random.default_rng(42)
        indices_list = []
        for _ in range(n_samples):
            perm = rng.permutation(m)
            indices_list.append(tuple(perm[:q]))
        sign_assignments = indices_list

    for neg_indices in sign_assignments:
        S_diag = np.ones(m)
        if len(neg_indices) > 0:
            S_diag[list(neg_indices)] = -1.0

        S_mat = np.diag(S_diag)
        A = F_sqrt @ S_mat @ F_sqrt

        eigs = np.linalg.eigvalsh(A)
        min_eig = eigs[0]
        second_eig = eigs[1] if len(eigs) > 1 else min_eig

        if min_eig < 0:
            beta_c = -min_eig
            L_gap = (second_eig - min_eig) / abs(min_eig) if min_eig != 0 else 0

            if beta_c > best_beta_c:
                best_beta_c = beta_c
                best_L_gap = L_gap

    W = best_beta_c * best_L_gap if best_beta_c > 0 else 0.0

    return best_beta_c, best_L_gap, W


def compute_effective_rank(eigenvalues: np.ndarray, threshold: float = 0.01) -> int:
    """
    Compute effective rank: number of eigenvalues > threshold * max eigenvalue.
    """
    max_eig = np.max(eigenvalues)
    if max_eig < 1e-10:
        return 0
    return int(np.sum(eigenvalues > threshold * max_eig))


def analyze_dimension(
    dimension: int,
    linear_size: int,
    coupling_J: float,
    exhaustive_threshold: int = 12
) -> Optional[DimensionResult]:
    """
    Analyze a single (d, L, J) configuration.

    Returns:
        DimensionResult with all measurements
    """
    # Create lattice graph
    G = create_lattice_graph(dimension, linear_size)
    n = G.number_of_nodes()
    m = G.number_of_edges()

    if n > 16:
        print(f"WARNING: d={dimension}, L={linear_size} has N={n} > 16 vertices. Skipping.")
        return None

    if m < 3:
        print(f"WARNING: d={dimension}, L={linear_size} has only {m} edges. Skipping.")
        return None

    # Compute Fisher matrix
    F, edges = compute_exact_fisher_ising(G, coupling_J)

    # Girth
    girth = compute_girth(G)

    # Near-diagonal ratio
    diag_F = np.diag(np.diag(F))
    off_diag_F = F - diag_F

    diag_entries = np.diag(F)
    diag_mean = np.mean(diag_entries)
    diag_std = np.std(diag_entries)

    off_diag_entries = F[np.triu_indices(m, k=1)]
    off_diag_rms = np.sqrt(np.mean(off_diag_entries**2))

    diag_op_norm = np.linalg.norm(diag_F, ord=2)
    off_diag_op_norm = np.linalg.norm(off_diag_F, ord=2)

    near_diagonal_ratio = off_diag_op_norm / diag_op_norm if diag_op_norm > 0 else 0.0

    # Spectral gap analysis (q=1 vs q>=2)
    W_q1 = 0.0
    W_max_higher = 0.0

    try:
        _, _, W_q1 = compute_spectral_gap_for_q(F, 1, exhaustive_threshold)

        # Sample a few higher q values
        q_values = [2, 3, min(m//2, 5)]
        for q in q_values:
            if q < m:
                _, _, W = compute_spectral_gap_for_q(F, q, exhaustive_threshold)
                W_max_higher = max(W_max_higher, W)
    except Exception as e:
        print(f"  Spectral gap computation failed for d={dimension}, L={linear_size}, J={coupling_J}: {e}")
        W_q1 = 0.0
        W_max_higher = 0.0

    spectral_gap_ratio = W_q1 / W_max_higher if W_max_higher > 1e-10 else float('inf')
    q1_wins = W_q1 > W_max_higher

    # Effective rank
    F_eigs = np.linalg.eigvalsh(F)
    eff_rank = compute_effective_rank(F_eigs, threshold=0.01)
    rank_ratio = eff_rank / m if m > 0 else 0.0

    # Critical beta (for q=1 Lorentzian signature)
    try:
        beta_c, _, _ = compute_spectral_gap_for_q(F, 1, exhaustive_threshold)
    except:
        beta_c = 0.0

    return DimensionResult(
        dimension=dimension,
        linear_size=linear_size,
        n_vertices=n,
        n_edges=m,
        girth=girth,
        coupling_J=coupling_J,
        near_diagonal_ratio=near_diagonal_ratio,
        diag_mean=diag_mean,
        diag_std=diag_std,
        off_diag_rms=off_diag_rms,
        spectral_gap_W_q1=W_q1,
        spectral_gap_W_max_higher=W_max_higher,
        spectral_gap_ratio=spectral_gap_ratio,
        q1_wins=q1_wins,
        effective_rank=eff_rank,
        rank_ratio=rank_ratio,
        beta_c=beta_c,
        F_eigenvalues=F_eigs
    )


def main():
    """Run dimensionality selection study."""

    print("=" * 80)
    print("DIMENSIONALITY SELECTION STUDY")
    print("=" * 80)
    print()
    print("Research Question:")
    print("  Does information geometry select a preferred spatial dimension d?")
    print("  Are d=3 or d=4 special?")
    print()
    print("Method:")
    print("  - Generate d-dimensional lattice graphs for d=1,2,3,4")
    print("  - Compute exact Ising Fisher matrices")
    print("  - Measure: near-diagonal ratio, spectral gap, effective rank, beta_c, girth")
    print("  - Look for non-trivial d-dependence")
    print()
    print("=" * 80)
    print()

    # Test configurations
    configs = [
        # (dimension, linear_size)
        (1, 9),   # 1D chain: 9 vertices, 8 edges
        (2, 3),   # 2D grid: 9 vertices, 12 edges
        (3, 2),   # 3D cube: 8 vertices, 12 edges
        (4, 2),   # 4D hypercube: 16 vertices, 32 edges
        # d=5 skipped (2^32 states infeasible)
    ]

    # Coupling strengths
    J_values = [0.3, 0.5, 0.7, 1.0]

    results = []

    print(f"{'d':<4} {'L':<4} {'N':<4} {'m':<6} {'g':<6} {'J':<6} {'diag_ratio':<12} "
          f"{'W(q=1)':<12} {'W_ratio':<10} {'eff_rank':<10} {'beta_c':<10}")
    print("-" * 100)

    for dimension, linear_size in configs:
        for J in J_values:
            try:
                result = analyze_dimension(dimension, linear_size, J, exhaustive_threshold=12)
                if result is None:
                    continue

                results.append(result)

                print(f"{result.dimension:<4} {result.linear_size:<4} {result.n_vertices:<4} "
                      f"{result.n_edges:<6} {result.girth:<6} {result.coupling_J:<6.2f} "
                      f"{result.near_diagonal_ratio:<12.4f} {result.spectral_gap_W_q1:<12.4f} "
                      f"{result.spectral_gap_ratio:<10.2f} {result.effective_rank:<10} "
                      f"{result.beta_c:<10.4f}")

            except Exception as e:
                print(f"ERROR on d={dimension}, L={linear_size}, J={J}: {e}")
                continue

    print()
    print("=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print()

    if not results:
        print("No valid results obtained.")
        return

    # Group by dimension
    dim_groups = {}
    for r in results:
        d = r.dimension
        if d not in dim_groups:
            dim_groups[d] = []
        dim_groups[d].append(r)

    print("1. NEAR-DIAGONAL RATIO vs DIMENSION")
    print()
    print(f"{'d':<4} {'N_cases':<10} {'Mean Ratio':<15} {'Std Ratio':<15}")
    print("-" * 50)

    for d in sorted(dim_groups.keys()):
        cases = dim_groups[d]
        ratios = [r.near_diagonal_ratio for r in cases]
        mean_ratio = np.mean(ratios)
        std_ratio = np.std(ratios)
        print(f"{d:<4} {len(cases):<10} {mean_ratio:<15.6f} {std_ratio:<15.6f}")

    print()
    print("2. SPECTRAL GAP (q=1 wins) vs DIMENSION")
    print()
    print(f"{'d':<4} {'N_cases':<10} {'q=1 wins':<12} {'Percentage':<12}")
    print("-" * 50)

    for d in sorted(dim_groups.keys()):
        cases = dim_groups[d]
        q1_wins_count = sum(1 for r in cases if r.q1_wins)
        percentage = 100 * q1_wins_count / len(cases) if len(cases) > 0 else 0
        print(f"{d:<4} {len(cases):<10} {q1_wins_count:<12} {percentage:<12.1f}%")

    print()
    print("3. EFFECTIVE RANK vs DIMENSION")
    print()
    print(f"{'d':<4} {'N_cases':<10} {'Mean Eff Rank':<15} {'Mean Rank Ratio':<15}")
    print("-" * 50)

    for d in sorted(dim_groups.keys()):
        cases = dim_groups[d]
        eff_ranks = [r.effective_rank for r in cases]
        rank_ratios = [r.rank_ratio for r in cases]
        mean_eff_rank = np.mean(eff_ranks)
        mean_rank_ratio = np.mean(rank_ratios)
        print(f"{d:<4} {len(cases):<10} {mean_eff_rank:<15.2f} {mean_rank_ratio:<15.4f}")

    print()
    print("4. CRITICAL BETA vs DIMENSION")
    print()
    print(f"{'d':<4} {'N_cases':<10} {'Mean beta_c':<15} {'Std beta_c':<15}")
    print("-" * 50)

    for d in sorted(dim_groups.keys()):
        cases = dim_groups[d]
        beta_cs = [r.beta_c for r in cases]
        mean_beta_c = np.mean(beta_cs)
        std_beta_c = np.std(beta_cs)
        print(f"{d:<4} {len(cases):<10} {mean_beta_c:<15.6f} {std_beta_c:<15.6f}")

    print()
    print("5. GIRTH vs DIMENSION")
    print()
    print(f"{'d':<4} {'Linear Size L':<15} {'Girth':<10}")
    print("-" * 40)

    for d in sorted(dim_groups.keys()):
        cases = dim_groups[d]
        # Get girth (same for all cases with same d, L)
        if len(cases) > 0:
            print(f"{d:<4} {cases[0].linear_size:<15} {cases[0].girth:<10}")

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print()

    # Check if there's non-trivial d-dependence
    ratios_by_d = {d: np.mean([r.near_diagonal_ratio for r in dim_groups[d]])
                   for d in dim_groups.keys()}

    max_ratio = max(ratios_by_d.values())
    min_ratio = min(ratios_by_d.values())
    variation = (max_ratio - min_ratio) / max_ratio if max_ratio > 0 else 0

    print(f"Near-diagonal ratio variation across dimensions: {variation:.2%}")

    if variation > 0.3:
        print("  → SIGNIFICANT d-dependence detected")
        # Check if d=3 or d=4 is special
        if 3 in ratios_by_d and 4 in ratios_by_d:
            if ratios_by_d[3] < ratios_by_d[2] and ratios_by_d[3] < ratios_by_d[4]:
                print("  → d=3 shows MINIMUM near-diagonal ratio (most diagonal)")
            elif ratios_by_d[4] < ratios_by_d[3] and ratios_by_d[4] < ratios_by_d[2]:
                print("  → d=4 shows MINIMUM near-diagonal ratio (most diagonal)")
    else:
        print("  → NO significant d-dependence (within factor of 2)")

    print()

    # Check spectral gap selection
    q1_wins_by_d = {d: sum(1 for r in dim_groups[d] if r.q1_wins) / len(dim_groups[d])
                    for d in dim_groups.keys()}

    print(f"Spectral gap q=1 winning rate by dimension:")
    for d in sorted(q1_wins_by_d.keys()):
        print(f"  d={d}: {q1_wins_by_d[d]:.1%}")

    print()

    # Write detailed results
    write_detailed_results(results)

    print("=" * 80)
    print("Detailed results written to:")
    print("  experience/insights/DIMENSION-SELECTION-STUDY-2026-02-16.md")
    print("=" * 80)


def write_detailed_results(results: List[DimensionResult]):
    """Write detailed results to markdown file."""

    output_path = "/Users/Max_1/Projects/PhysicsResearch/cosmological-unification/papers/structural-bridge/experience/insights/DIMENSION-SELECTION-STUDY-2026-02-16.md"

    with open(output_path, "w") as f:
        f.write("# Dimensionality Selection Study\n\n")
        f.write("**Date:** 2026-02-16\n")
        f.write("**Attribution:** TEST-BRIDGE-MVP1-DIMENSION-SELECTION-001\n\n")

        f.write("## Research Question\n\n")
        f.write("Does information geometry select a preferred spatial dimension d? ")
        f.write("Specifically, do Ising observers on d-dimensional lattices show ")
        f.write("non-trivial dependence on d, particularly whether d=3 or d=4 is special?\n\n")

        f.write("## Method\n\n")
        f.write("1. Generate d-dimensional lattice graphs for d=1,2,3,4\n")
        f.write("2. Compute exact Ising Fisher matrices\n")
        f.write("3. Measure: near-diagonal ratio, spectral gap, effective rank, beta_c, girth\n")
        f.write("4. Look for non-trivial d-dependence\n\n")

        f.write("## Configurations\n\n")
        f.write("- d=1: 1D chain, L=9 (N=9 vertices, m=8 edges)\n")
        f.write("- d=2: 2D square lattice, L=3 (N=9 vertices, m=12 edges)\n")
        f.write("- d=3: 3D cubic lattice, L=2 (N=8 vertices, m=12 edges)\n")
        f.write("- d=4: 4D hypercubic lattice, L=2 (N=16 vertices, m=32 edges)\n")
        f.write("- d=5: Skipped (2^32 states infeasible)\n\n")

        f.write(f"**Total configurations tested:** {len(results)}\n\n")

        # Summary table
        f.write("## Detailed Results\n\n")
        f.write("| d | L | N | m | g | J | diag_ratio | W(q=1) | W_ratio | eff_rank | beta_c |\n")
        f.write("|---|---|---|---|---|---|------------|--------|---------|----------|--------|\n")

        for r in results:
            f.write(f"| {r.dimension} | {r.linear_size} | {r.n_vertices} | {r.n_edges} | "
                   f"{r.girth} | {r.coupling_J:.2f} | {r.near_diagonal_ratio:.6f} | "
                   f"{r.spectral_gap_W_q1:.4f} | {r.spectral_gap_ratio:.2f} | "
                   f"{r.effective_rank} | {r.beta_c:.4f} |\n")

        # Group by dimension
        dim_groups = {}
        for r in results:
            d = r.dimension
            if d not in dim_groups:
                dim_groups[d] = []
            dim_groups[d].append(r)

        f.write("\n## Analysis by Dimension\n\n")

        f.write("### Near-Diagonal Ratio\n\n")
        f.write("| d | N cases | Mean Ratio | Std Ratio |\n")
        f.write("|---|---------|------------|-----------|\n")

        for d in sorted(dim_groups.keys()):
            cases = dim_groups[d]
            ratios = [r.near_diagonal_ratio for r in cases]
            mean_ratio = np.mean(ratios)
            std_ratio = np.std(ratios)
            f.write(f"| {d} | {len(cases)} | {mean_ratio:.6f} | {std_ratio:.6f} |\n")

        f.write("\n### Spectral Gap (q=1 wins)\n\n")
        f.write("| d | N cases | q=1 wins | Percentage |\n")
        f.write("|---|---------|----------|------------|\n")

        for d in sorted(dim_groups.keys()):
            cases = dim_groups[d]
            q1_wins_count = sum(1 for r in cases if r.q1_wins)
            percentage = 100 * q1_wins_count / len(cases) if len(cases) > 0 else 0
            f.write(f"| {d} | {len(cases)} | {q1_wins_count} | {percentage:.1f}% |\n")

        f.write("\n### Effective Rank\n\n")
        f.write("| d | N cases | Mean Eff Rank | Mean Rank Ratio |\n")
        f.write("|---|---------|---------------|----------------|\n")

        for d in sorted(dim_groups.keys()):
            cases = dim_groups[d]
            eff_ranks = [r.effective_rank for r in cases]
            rank_ratios = [r.rank_ratio for r in cases]
            mean_eff_rank = np.mean(eff_ranks)
            mean_rank_ratio = np.mean(rank_ratios)
            f.write(f"| {d} | {len(cases)} | {mean_eff_rank:.2f} | {mean_rank_ratio:.4f} |\n")

        f.write("\n### Critical Beta\n\n")
        f.write("| d | N cases | Mean beta_c | Std beta_c |\n")
        f.write("|---|---------|-------------|------------|\n")

        for d in sorted(dim_groups.keys()):
            cases = dim_groups[d]
            beta_cs = [r.beta_c for r in cases]
            mean_beta_c = np.mean(beta_cs)
            std_beta_c = np.std(beta_cs)
            f.write(f"| {d} | {len(cases)} | {mean_beta_c:.6f} | {std_beta_c:.6f} |\n")

        f.write("\n## Interpretation\n\n")

        # Check d-dependence
        ratios_by_d = {d: np.mean([r.near_diagonal_ratio for r in dim_groups[d]])
                       for d in dim_groups.keys()}

        max_ratio = max(ratios_by_d.values())
        min_ratio = min(ratios_by_d.values())
        variation = (max_ratio - min_ratio) / max_ratio if max_ratio > 0 else 0

        f.write(f"**Near-diagonal ratio variation:** {variation:.2%}\n\n")

        if variation > 0.3:
            f.write("**RESULT:** SIGNIFICANT d-dependence detected.\n\n")
            # Check if d=3 or d=4 is special
            if 3 in ratios_by_d and 4 in ratios_by_d:
                if ratios_by_d[3] < ratios_by_d[2] and ratios_by_d[3] < ratios_by_d[4]:
                    f.write("d=3 shows MINIMUM near-diagonal ratio (most diagonal structure).\n")
                    f.write("This could indicate that 3+1 spacetime is information-geometrically preferred.\n\n")
                elif ratios_by_d[4] < ratios_by_d[3] and ratios_by_d[4] < ratios_by_d[2]:
                    f.write("d=4 shows MINIMUM near-diagonal ratio (most diagonal structure).\n")
                    f.write("This could indicate that 4D space (or 4+1 spacetime) is preferred.\n\n")
        else:
            f.write("**RESULT:** NO significant d-dependence detected.\n\n")
            f.write("The near-diagonal ratio does not vary strongly with dimension. ")
            f.write("Information geometry does NOT appear to select a preferred spatial dimension ")
            f.write("based on this metric.\n\n")

        f.write("## Limitations\n\n")
        f.write("- Small system sizes (N ≤ 16 vertices) due to exact enumeration constraint\n")
        f.write("- Different linear sizes L for different dimensions (L=9 for d=1, L=2 for d=4)\n")
        f.write("- Finite-size effects may obscure genuine d-dependence\n")
        f.write("- d=5 not tested (too many states for exact enumeration)\n\n")

        f.write("## Next Steps\n\n")
        f.write("- Test larger systems using sampling methods\n")
        f.write("- Use equal edge counts m across dimensions for fair comparison\n")
        f.write("- Investigate other metrics (entropy production, complexity measures)\n")
        f.write("- Theoretical analysis: are there information-geometric principles ")
        f.write("that constrain spatial dimension?\n\n")

        f.write("---\n\n")
        f.write("*Generated by dimension_selection.py*\n")


if __name__ == "__main__":
    main()
