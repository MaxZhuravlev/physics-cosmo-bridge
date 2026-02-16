#!/usr/bin/env python3
"""
Gaussian Graphical Model Fisher Information Matrix

Tests universality of Fisher matrix structure across different exponential families:
- Exact Fisher formula for Gaussian models: F_{ab} = Σ_{a1,b1}Σ_{a2,b2} + Σ_{a1,b2}Σ_{a2,b1}
- Tree Fisher diagonality
- Spectral gap selection
- Near-diagonal structure vs girth
- Comparison to Ising/Potts patterns

Attribution:
    test_id: TEST-BRIDGE-MVP1-GAUSSIAN-FISHER-001
    mvp_layer: MVP-1
    dialogue_id: session-2026-02-16-gaussian-fisher
    purpose: Test whether Fisher structure patterns are universal across exponential families

Theoretical Background:
    Gaussian graphical model on graph G=(V,E):
    - X ~ N(0, Σ) where Σ = Λ^{-1} (precision matrix Λ)
    - Λ is sparse: Λ_{ij} = 0 unless (i,j) ∈ E or i=j
    - Natural parameters: θ_e = Λ_{ij} for edge e=(i,j)
    - Fisher matrix: F_{(i,j),(k,l)} = Σ_{ik}Σ_{jl} + Σ_{il}Σ_{jk}
    - Exponential family => M = F^2 (this is a general theorem)

Key Questions:
    1. Are Gaussian Fisher matrices diagonal on trees? (Unlike Ising!)
    2. Does spectral gap selection apply to Gaussian models?
    3. Is near-diagonal structure preserved across exponential families?
    4. What is the relationship between graph topology and Fisher structure?
"""

import numpy as np
import networkx as nx
from dataclasses import dataclass
from typing import List, Tuple, Dict
import itertools


@dataclass
class GaussianFisherResult:
    """Results for a single Gaussian graphical model configuration."""
    graph_name: str
    n_vertices: int
    n_edges: int
    girth: int
    coupling_J: float

    # Fisher matrix properties
    F_mean: float
    F_std: float
    F_min: float
    F_max: float

    # Diagonal properties
    diag_mean: float
    diag_std: float

    # Off-diagonal properties
    off_diag_rms: float
    off_diag_max: float

    # Norms
    F_op_norm: float
    diag_op_norm: float
    off_diag_op_norm: float

    # Near-diagonal ratio
    ratio: float  # ||F - diag(F)||_op / ||diag(F)||_op

    # Tree test (diagonal?)
    is_tree: bool
    tree_diagonal_error: float  # Max |F_ij| for i≠j

    # Spectral gap test
    beta_c: float
    L_gap: float
    W: float
    q_neg_optimal: int  # Number of negative eigenvalues at optimal S

    # Eigenvalue spectrum
    F_eigs: np.ndarray


def build_precision_matrix(n_vertices: int, edges: List[Tuple[int, int]], J: float, diag_val: float = 1.0) -> np.ndarray:
    """
    Build precision matrix Λ for Gaussian graphical model.

    Args:
        n_vertices: Number of vertices
        edges: List of (i,j) edge tuples
        J: Coupling strength (off-diagonal)
        diag_val: Diagonal value (default 1.0)

    Returns:
        Λ: (n, n) precision matrix

    Note:
        For positive definiteness, need |J| < 1/max_degree approximately.
        We use diag_val to ensure positive definiteness.
    """
    Lambda = np.eye(n_vertices) * diag_val

    for i, j in edges:
        Lambda[i, j] = J
        Lambda[j, i] = J

    # Ensure positive definiteness by checking eigenvalues
    eigvals = np.linalg.eigvalsh(Lambda)
    if np.min(eigvals) <= 1e-10:
        # Adjust diagonal to ensure positive definiteness
        adjustment = abs(np.min(eigvals)) + 0.1
        Lambda += adjustment * np.eye(n_vertices)

    return Lambda


def gaussian_fisher(n_vertices: int, edges: List[Tuple[int, int]], J: float) -> np.ndarray:
    """
    Compute exact Fisher information matrix for Gaussian graphical model.

    Args:
        n_vertices: Number of vertices
        edges: List of (i,j) edge tuples
        J: Coupling strength

    Returns:
        F: (m, m) Fisher matrix where m = len(edges)

    Formula:
        F_{(i,j),(k,l)} = Σ_{ik}Σ_{jl} + Σ_{il}Σ_{jk}
        where Σ = Λ^{-1} is the covariance matrix
    """
    m = len(edges)
    if m == 0:
        return np.zeros((0, 0))

    # Build precision matrix and compute covariance
    Lambda = build_precision_matrix(n_vertices, edges, J)
    Sigma = np.linalg.inv(Lambda)

    # Compute Fisher matrix using closed form
    F = np.zeros((m, m))

    for a, (i, j) in enumerate(edges):
        for b, (k, l) in enumerate(edges):
            # F_{ab} = Σ_{ik}Σ_{jl} + Σ_{il}Σ_{jk}
            F[a, b] = Sigma[i, k] * Sigma[j, l] + Sigma[i, l] * Sigma[j, k]

    return F


def compute_girth(G: nx.Graph) -> int:
    """
    Compute the girth (shortest cycle length) of graph G.

    Returns:
        girth: Shortest cycle length, or 999 if acyclic (tree)
    """
    if not nx.is_connected(G):
        raise ValueError("Graph must be connected")

    n = G.number_of_nodes()
    m = G.number_of_edges()

    # Trees have n-1 edges
    if m == n - 1:
        return 999  # Use 999 for infinity (tree)

    # Use BFS from each node to find shortest cycle
    min_cycle = float('inf')

    for start in G.nodes():
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
                    cycle_len = distances[u] + distances[v] + 1
                    min_cycle = min(min_cycle, cycle_len)

    return int(min_cycle) if min_cycle != float('inf') else 999


def test_tree_fisher(edges: List[Tuple[int, int]], J: float, n_vertices: int) -> Tuple[bool, float]:
    """
    Test whether Fisher matrix is diagonal on trees.

    For Gaussian models on trees, edges are NOT necessarily conditionally independent
    (unlike Ising models). The Fisher matrix may have off-diagonal entries.

    This is a KEY DIFFERENCE from Ising models and tests whether tree diagonality
    is a universal property or specific to discrete spin models.

    Args:
        edges: Edge list
        J: Coupling strength
        n_vertices: Number of vertices

    Returns:
        is_diagonal: True if max|F_ij| < 1e-8 for i≠j
        max_off_diag: Maximum |F_ij| for i≠j
    """
    F = gaussian_fisher(n_vertices, edges, J)
    m = len(edges)

    if m == 0:
        return True, 0.0

    # Extract off-diagonal entries
    off_diag_mask = ~np.eye(m, dtype=bool)
    off_diag_entries = np.abs(F[off_diag_mask])

    max_off_diag = np.max(off_diag_entries) if len(off_diag_entries) > 0 else 0.0
    is_diagonal = max_off_diag < 1e-8

    return is_diagonal, max_off_diag


def test_spectral_gap_selection(F: np.ndarray) -> Tuple[float, float, float, int]:
    """
    Test spectral gap selection mechanism for Gaussian Fisher matrix.

    Same definition as Ising/Potts:
    1. For each sign assignment S (diagonal matrix with ±1)
    2. Compute A = F^{1/2} S F^{1/2}
    3. Find eigenvalues d_1 <= d_2 <= ... <= d_m
    4. Define β_c = -d_1, L_gap = (d_2-d_1)/|d_1|, W = β_c × L_gap
    5. Check if q_neg=1 (Lorentzian) maximizes W

    Args:
        F: Fisher matrix

    Returns:
        beta_c: Critical inverse temperature
        L_gap: Landscape gap
        W: Winnability
        q_neg_optimal: Number of negative eigenvalues at optimal S
    """
    m = F.shape[0]
    if m == 0:
        return 0.0, 0.0, 0.0, 0

    # Compute F^{1/2}
    eigvals, eigvecs = np.linalg.eigh(F)
    eigvals = np.maximum(eigvals, 1e-12)  # Ensure positive
    F_sqrt = eigvecs @ np.diag(np.sqrt(eigvals)) @ eigvecs.T

    best_W = -np.inf
    best_beta_c = 0.0
    best_L_gap = 0.0
    best_q_neg = 0

    # Test all 2^m sign assignments (limited to m <= 15 for tractability)
    if m > 15:
        # For large m, sample random sign patterns
        n_samples = 1000
        for _ in range(n_samples):
            signs = np.random.choice([-1, 1], size=m)
            S = np.diag(signs)
            A = F_sqrt @ S @ F_sqrt

            eigs = np.linalg.eigvalsh(A)
            eigs = np.sort(eigs)

            d_1 = eigs[0]
            d_2 = eigs[1] if m > 1 else eigs[0]

            beta_c = -d_1
            L_gap = (d_2 - d_1) / abs(d_1) if abs(d_1) > 1e-12 else 0.0
            W = beta_c * L_gap

            if W > best_W:
                best_W = W
                best_beta_c = beta_c
                best_L_gap = L_gap
                best_q_neg = np.sum(eigs < 0)
    else:
        # Enumerate all sign assignments
        for sign_pattern in itertools.product([-1, 1], repeat=m):
            S = np.diag(sign_pattern)
            A = F_sqrt @ S @ F_sqrt

            eigs = np.linalg.eigvalsh(A)
            eigs = np.sort(eigs)

            d_1 = eigs[0]
            d_2 = eigs[1] if m > 1 else eigs[0]

            beta_c = -d_1
            L_gap = (d_2 - d_1) / abs(d_1) if abs(d_1) > 1e-12 else 0.0
            W = beta_c * L_gap

            if W > best_W:
                best_W = W
                best_beta_c = beta_c
                best_L_gap = L_gap
                best_q_neg = np.sum(eigs < 0)

    return best_beta_c, best_L_gap, best_W, best_q_neg


def test_near_diagonal(F: np.ndarray, girth: int) -> float:
    """
    Test near-diagonal structure: ratio = ||F - diag(F)||_op / ||diag(F)||_op

    For Gaussian models, we expect similar girth-dependent decay as Ising models
    IF the near-diagonal structure is a universal property of sparse exponential families.

    Args:
        F: Fisher matrix
        girth: Graph girth

    Returns:
        ratio: Off-diagonal to diagonal ratio
    """
    m = F.shape[0]
    if m == 0:
        return 0.0

    diag_F = np.diag(np.diag(F))
    off_diag_F = F - diag_F

    diag_op_norm = np.linalg.norm(diag_F, ord=2)
    off_diag_op_norm = np.linalg.norm(off_diag_F, ord=2)

    ratio = off_diag_op_norm / diag_op_norm if diag_op_norm > 1e-12 else 0.0

    return ratio


def analyze_gaussian_fisher(
    G: nx.Graph,
    graph_name: str,
    J: float
) -> GaussianFisherResult:
    """
    Comprehensive analysis of Gaussian Fisher matrix structure.

    Args:
        G: NetworkX graph
        graph_name: Descriptive name
        J: Coupling strength

    Returns:
        GaussianFisherResult with all measurements
    """
    edges = list(G.edges())
    n = G.number_of_nodes()
    m = len(edges)

    # Compute Fisher matrix
    F = gaussian_fisher(n, edges, J)

    # Compute girth
    girth = compute_girth(G)

    # Fisher matrix statistics
    F_mean = np.mean(F)
    F_std = np.std(F)
    F_min = np.min(F)
    F_max = np.max(F)

    # Diagonal statistics
    diag_entries = np.diag(F)
    diag_mean = np.mean(diag_entries)
    diag_std = np.std(diag_entries)

    # Off-diagonal statistics
    off_diag_mask = ~np.eye(m, dtype=bool)
    off_diag_entries = F[off_diag_mask]
    off_diag_rms = np.sqrt(np.mean(off_diag_entries**2))
    off_diag_max = np.max(np.abs(off_diag_entries)) if len(off_diag_entries) > 0 else 0.0

    # Norms
    F_op_norm = np.linalg.norm(F, ord=2)
    diag_F = np.diag(np.diag(F))
    diag_op_norm = np.linalg.norm(diag_F, ord=2)
    off_diag_F = F - diag_F
    off_diag_op_norm = np.linalg.norm(off_diag_F, ord=2)

    # Near-diagonal ratio
    ratio = test_near_diagonal(F, girth)

    # Tree test
    is_tree = (girth == 999)
    _, tree_diagonal_error = test_tree_fisher(edges, J, n)

    # Spectral gap test
    beta_c, L_gap, W, q_neg_optimal = test_spectral_gap_selection(F)

    # Eigenvalue spectrum
    F_eigs = np.linalg.eigvalsh(F)

    return GaussianFisherResult(
        graph_name=graph_name,
        n_vertices=n,
        n_edges=m,
        girth=girth,
        coupling_J=J,
        F_mean=F_mean,
        F_std=F_std,
        F_min=F_min,
        F_max=F_max,
        diag_mean=diag_mean,
        diag_std=diag_std,
        off_diag_rms=off_diag_rms,
        off_diag_max=off_diag_max,
        F_op_norm=F_op_norm,
        diag_op_norm=diag_op_norm,
        off_diag_op_norm=off_diag_op_norm,
        ratio=ratio,
        is_tree=is_tree,
        tree_diagonal_error=tree_diagonal_error,
        beta_c=beta_c,
        L_gap=L_gap,
        W=W,
        q_neg_optimal=q_neg_optimal,
        F_eigs=F_eigs
    )


def main():
    """
    Comprehensive test suite for Gaussian graphical model Fisher matrices.

    Tests:
    1. Tree graphs (P3-P10, stars) - diagonal Fisher?
    2. Cycles (C4-C10) - near-diagonal structure?
    3. Complete graphs (K3-K5) - dense structure
    4. Lattices (3x3, 4x4) - intermediate
    5. Random sparse graphs (N=10,15,20) - general case
    6. Comparison to Ising patterns
    """

    print("=" * 80)
    print("GAUSSIAN GRAPHICAL MODEL FISHER MATRIX ANALYSIS")
    print("=" * 80)
    print()
    print("Testing universality of Fisher structure patterns:")
    print("  1. Tree diagonality (is F diagonal on trees?)")
    print("  2. Spectral gap selection (does q_neg=1 maximize W?)")
    print("  3. Near-diagonal structure (ratio ~ tanh^g(J)?)")
    print("  4. Comparison to Ising/Potts patterns")
    print()
    print("=" * 80)
    print()

    results = []

    # Test configurations
    J_values = [0.1, 0.3, 0.5]  # Keep |J| < 1/max_degree for positive definiteness

    # 1. Path graphs (trees)
    print("=" * 80)
    print("1. PATH GRAPHS (Trees, girth = ∞)")
    print("=" * 80)
    print()
    print("KEY QUESTION: Is Fisher diagonal on trees for Gaussian models?")
    print("(For Ising models: YES. For Gaussian models: ???)")
    print()

    for n in [3, 4, 5, 6, 8, 10]:
        G = nx.path_graph(n)
        graph_name = f"path_P{n}"

        for J in [0.3, 0.5]:
            result = analyze_gaussian_fisher(G, graph_name, J)
            results.append(result)

            diag_status = "DIAGONAL" if result.tree_diagonal_error < 1e-8 else "NON-DIAGONAL"
            print(f"{graph_name:12s} J={J:.2f} tree_err={result.tree_diagonal_error:.2e} "
                  f"ratio={result.ratio:.6f} {diag_status}")

    print()

    # 2. Star graphs (trees)
    print("=" * 80)
    print("2. STAR GRAPHS (Trees, girth = ∞)")
    print("=" * 80)
    print()

    for n in [4, 5, 6, 8]:
        G = nx.star_graph(n - 1)  # star_graph(k) has k+1 vertices
        graph_name = f"star_S{n}"

        for J in [0.3, 0.5]:
            result = analyze_gaussian_fisher(G, graph_name, J)
            results.append(result)

            diag_status = "DIAGONAL" if result.tree_diagonal_error < 1e-8 else "NON-DIAGONAL"
            print(f"{graph_name:12s} J={J:.2f} tree_err={result.tree_diagonal_error:.2e} "
                  f"ratio={result.ratio:.6f} {diag_status}")

    print()

    # 3. Cycle graphs
    print("=" * 80)
    print("3. CYCLE GRAPHS (girth = n)")
    print("=" * 80)
    print()
    print("Testing near-diagonal structure vs girth")
    print()

    for n in [4, 5, 6, 8, 10]:
        G = nx.cycle_graph(n)
        graph_name = f"cycle_C{n}"

        for J in J_values:
            result = analyze_gaussian_fisher(G, graph_name, J)
            results.append(result)

            print(f"{graph_name:12s} g={result.girth:3d} J={J:.2f} "
                  f"ratio={result.ratio:.6f} diag_mean={result.diag_mean:.4f}")

    print()

    # 4. Complete graphs (dense)
    print("=" * 80)
    print("4. COMPLETE GRAPHS (Dense, girth = 3)")
    print("=" * 80)
    print()

    for n in [3, 4, 5]:
        G = nx.complete_graph(n)
        graph_name = f"complete_K{n}"

        for J in [0.1, 0.3]:  # Smaller J for dense graphs
            result = analyze_gaussian_fisher(G, graph_name, J)
            results.append(result)

            print(f"{graph_name:12s} g={result.girth:3d} J={J:.2f} "
                  f"ratio={result.ratio:.6f} diag_mean={result.diag_mean:.4f}")

    print()

    # 5. Lattice graphs
    print("=" * 80)
    print("5. LATTICE GRAPHS (girth = 4)")
    print("=" * 80)
    print()

    for size in [3, 4]:
        G = nx.grid_2d_graph(size, size)
        # Relabel nodes to 0..n-1
        G = nx.convert_node_labels_to_integers(G)
        graph_name = f"lattice_{size}x{size}"

        for J in [0.3, 0.5]:
            result = analyze_gaussian_fisher(G, graph_name, J)
            results.append(result)

            print(f"{graph_name:12s} g={result.girth:3d} J={J:.2f} "
                  f"ratio={result.ratio:.6f} diag_mean={result.diag_mean:.4f}")

    print()

    # 6. Random sparse graphs
    print("=" * 80)
    print("6. RANDOM SPARSE GRAPHS")
    print("=" * 80)
    print()

    np.random.seed(42)
    for n in [10, 15, 20]:
        # Generate random sparse graph with avg degree ~3
        p = 3.0 / (n - 1)
        G = nx.erdos_renyi_graph(n, p, seed=42)

        # Ensure connected
        while not nx.is_connected(G):
            G = nx.erdos_renyi_graph(n, p)

        graph_name = f"random_N{n}"

        for J in [0.3, 0.5]:
            result = analyze_gaussian_fisher(G, graph_name, J)
            results.append(result)

            girth = compute_girth(G)
            print(f"{graph_name:12s} n={n:2d} m={result.n_edges:3d} g={girth:3d} J={J:.2f} "
                  f"ratio={result.ratio:.6f}")

    print()
    print("=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print()

    # Analyze tree diagonality
    print("1. TREE DIAGONALITY TEST")
    print("-" * 80)
    print()

    tree_results = [r for r in results if r.is_tree]
    if tree_results:
        max_tree_err = max(r.tree_diagonal_error for r in tree_results)
        mean_tree_err = np.mean([r.tree_diagonal_error for r in tree_results])

        print(f"Trees tested: {len(tree_results)}")
        print(f"Max off-diagonal error: {max_tree_err:.2e}")
        print(f"Mean off-diagonal error: {mean_tree_err:.2e}")
        print()

        if max_tree_err < 1e-8:
            print("RESULT: Fisher matrices ARE diagonal on trees (like Ising)")
            print("CONCLUSION: Tree Fisher Identity is UNIVERSAL across exponential families")
        else:
            print("RESULT: Fisher matrices are NOT diagonal on trees (unlike Ising)")
            print("CONCLUSION: Tree Fisher Identity is SPECIFIC to discrete spin models")

    print()

    # Analyze spectral gap selection
    print("2. SPECTRAL GAP SELECTION TEST")
    print("-" * 80)
    print()

    lorentzian_count = sum(1 for r in results if r.q_neg_optimal == 1)
    total_count = len(results)

    print(f"Configurations with q_neg=1 (Lorentzian): {lorentzian_count}/{total_count} "
          f"({100*lorentzian_count/total_count:.1f}%)")
    print()

    if lorentzian_count / total_count > 0.8:
        print("RESULT: Spectral gap selection FAVORS Lorentzian signature (q_neg=1)")
        print("CONCLUSION: Signature selection mechanism is UNIVERSAL")
    else:
        print("RESULT: Spectral gap selection does NOT consistently favor Lorentzian")
        print("CONCLUSION: Signature selection is model-dependent")

    print()

    # Analyze near-diagonal structure
    print("3. NEAR-DIAGONAL STRUCTURE VS GIRTH")
    print("-" * 80)
    print()

    # Group by girth
    girth_groups = {}
    for r in results:
        g = r.girth
        if g not in girth_groups:
            girth_groups[g] = []
        girth_groups[g].append(r)

    print(f"{'Girth':<10} {'N_cases':<10} {'Mean Ratio':<15} {'Max Ratio':<15}")
    print("-" * 60)

    for g in sorted(girth_groups.keys()):
        cases = girth_groups[g]
        mean_ratio = np.mean([r.ratio for r in cases])
        max_ratio = np.max([r.ratio for r in cases])
        print(f"{g:<10} {len(cases):<10} {mean_ratio:<15.6f} {max_ratio:<15.6f}")

    print()

    # Test exponential decay
    finite_girth_results = [r for r in results if r.girth < 100 and abs(r.coupling_J - 0.5) < 0.01]
    if len(finite_girth_results) > 3:
        girths = np.array([r.girth for r in finite_girth_results])
        ratios = np.array([r.ratio for r in finite_girth_results])

        # Check if ratio decreases with girth
        correlation = np.corrcoef(girths, ratios)[0, 1]

        print(f"Correlation(girth, ratio) at J=0.5: {correlation:.3f}")
        print()

        if correlation < -0.5:
            print("RESULT: Ratio DECREASES with girth (negative correlation)")
            print("CONCLUSION: Near-diagonal structure is UNIVERSAL (sparse graphs)")
        else:
            print("RESULT: Ratio does NOT consistently decrease with girth")
            print("CONCLUSION: Near-diagonal structure may be model-dependent")

    print()

    # Summary comparison to Ising
    print("=" * 80)
    print("COMPARISON TO ISING/POTTS PATTERNS")
    print("=" * 80)
    print()

    print("Pattern                        | Ising | Gaussian | Universal?")
    print("-------------------------------|-------|----------|------------")

    # Tree diagonality
    tree_diagonal = max_tree_err < 1e-8 if tree_results else False
    print(f"Tree Fisher diagonal           | YES   | {'YES' if tree_diagonal else 'NO':<8s} | "
          f"{'YES' if tree_diagonal else 'NO'}")

    # Spectral gap selection
    spectral_gap_universal = lorentzian_count / total_count > 0.8
    print(f"Spectral gap selects q_neg=1   | YES   | {'YES' if spectral_gap_universal else 'NO':<8s} | "
          f"{'YES' if spectral_gap_universal else 'NO'}")

    # Near-diagonal structure
    near_diagonal_universal = correlation < -0.5 if len(finite_girth_results) > 3 else False
    print(f"Near-diagonal (sparse, large g)| YES   | {'YES' if near_diagonal_universal else 'NO':<8s} | "
          f"{'YES' if near_diagonal_universal else 'UNKNOWN'}")

    print()
    print("=" * 80)
    print("CONCLUSIONS")
    print("=" * 80)
    print()

    print("Gaussian graphical models provide an independent test of Fisher structure patterns.")
    print()

    if tree_diagonal:
        print("✓ Tree Fisher Identity: UNIVERSAL (holds for both Ising and Gaussian)")
    else:
        print("✗ Tree Fisher Identity: NOT UNIVERSAL (holds for Ising, fails for Gaussian)")

    print()

    if spectral_gap_universal:
        print("✓ Spectral Gap Selection: UNIVERSAL (Lorentzian signature preferred)")
    else:
        print("✗ Spectral Gap Selection: Model-dependent (not universal)")

    print()

    if near_diagonal_universal:
        print("✓ Near-Diagonal Structure: UNIVERSAL (sparse graphs favor diagonal Fisher)")
    else:
        print("? Near-Diagonal Structure: Needs more data to confirm universality")

    print()
    print("=" * 80)
    print(f"Total configurations tested: {len(results)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
