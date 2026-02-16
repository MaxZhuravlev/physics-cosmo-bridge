#!/usr/bin/env python3
"""
General-n Spectral Gap Selection Theorem Verification

Extends the spectral gap selection theorem from n=2 to general n dimensions.

THEOREM (to prove): For an n-dimensional parameter space with positive definite
Fisher matrix F and signed-edge mass tensor M^{H1'}, the spectral gap weighting
W(q) = β_c(q) × L_gap(q) satisfies:
   (a) W(q=1) > 0 for any F with at least one negative eigenvalue in F^{-1/2} M^{H1'} F^{-1/2}
   (b) W(q=1) ≥ W(q) for all q ≥ 2, with strict inequality when F is near-diagonal

Attribution:
    test_id: TEST-BRIDGE-MVP1-GENERAL-N-SPECTRAL-GAP-001
    mvp_layer: MVP-1
    vector_id: open-problem-3-extension
    dialogue_id: session-2026-02-16-general-n-proof
    recovery_path: experience/insights/GENERAL-N-SPECTRAL-GAP-PROOF-2026-02-16.md
"""

import numpy as np
import itertools
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import time

# Import from existing modules
from spectral_gap_ising_analysis import (
    compute_exact_fisher_ising,
    create_graph_J_matrix,
)


@dataclass
class GeneralNResult:
    """Results for general-n spectral gap analysis."""
    n: int  # Dimension of parameter space
    m: int  # Number of edges (= n for trees, can be larger)
    graph_name: str
    topology: str  # path, star, cycle, random_tree, random_sparse
    coupling_J: float

    # Fisher matrix properties
    F_condition_number: float
    F_diagonality: float  # ||F - diag(F)||_F / ||F||_F

    # Results for each q
    W_values: Dict[int, float]  # q -> W(q)
    beta_c_values: Dict[int, float]  # q -> beta_c(q)
    L_gap_values: Dict[int, float]  # q -> L_gap(q)

    # Outcome
    q_max: int  # argmax_q W(q)
    W_q1: float
    W_max_higher: float
    margin: float  # W(q=1) - max(W(q>=2))
    margin_relative: float  # margin / W(q=1)

    q1_wins: bool


@dataclass
class TreeDiagonalProof:
    """Verification that tree graphs have diagonal Fisher matrices."""
    graph_name: str
    n: int
    m: int
    coupling_J: float

    # Diagonal structure
    F_diagonal: np.ndarray  # Diagonal entries
    F_off_diagonal_max: float  # max|F_ij| for i≠j

    # Expected value (Tree Fisher Identity)
    expected_diagonal: float  # sech²(J)
    diagonal_match_error: float  # ||diag(F) - expected||_∞

    # Spectral properties
    eigenvalues_signed: np.ndarray  # Eigenvalues of signed matrix for q=1
    q1_beta_c: float
    q1_L_gap: float
    q1_W: float

    # Higher q (should have W=0 for diagonal case)
    q2_W: float

    is_tree: bool
    is_diagonal: bool  # True if F_off_diagonal_max < 1e-6


def create_tree_graph(n: int, topology: str, J: float) -> Tuple[np.ndarray, str]:
    """
    Create tree graph with n vertices.

    Args:
        n: Number of vertices
        topology: 'path', 'star', or 'random_tree'
        J: Coupling strength

    Returns:
        J_matrix: (n, n) coupling matrix
        graph_name: Descriptive name
    """
    J_matrix = np.zeros((n, n))

    if topology == 'path':
        # Path graph: 0-1-2-...-n-1
        for i in range(n - 1):
            J_matrix[i, i+1] = J
            J_matrix[i+1, i] = J
        graph_name = f"path_P{n}"

    elif topology == 'star':
        # Star graph: 0 connected to all others
        for i in range(1, n):
            J_matrix[0, i] = J
            J_matrix[i, 0] = J
        graph_name = f"star_S{n}"

    elif topology == 'random_tree':
        # Random tree using Prüfer sequence
        import networkx as nx
        G = nx.random_labeled_tree(n, seed=42)
        for (i, j) in G.edges():
            J_matrix[i, j] = J
            J_matrix[j, i] = J
        graph_name = f"random_tree_T{n}"

    else:
        raise ValueError(f"Unknown topology: {topology}")

    return J_matrix, graph_name


def create_sparse_graph(n: int, topology: str, J: float, seed: int = 42) -> Tuple[np.ndarray, str]:
    """
    Create sparse graph with cycles.

    Args:
        n: Number of vertices
        topology: 'cycle' or 'random_sparse'
        J: Coupling strength
        seed: Random seed

    Returns:
        J_matrix: (n, n) coupling matrix
        graph_name: Descriptive name
    """
    J_matrix = np.zeros((n, n))

    if topology == 'cycle':
        # Cycle graph: 0-1-2-...-n-1-0
        for i in range(n):
            j = (i + 1) % n
            J_matrix[i, j] = J
            J_matrix[j, i] = J
        graph_name = f"cycle_C{n}"

    elif topology == 'random_sparse':
        # Random sparse: expected degree ~3
        rng = np.random.default_rng(seed)
        p = 3.0 / (n - 1) if n > 1 else 0

        for i in range(n):
            for j in range(i + 1, n):
                if rng.random() < p:
                    J_matrix[i, j] = J
                    J_matrix[j, i] = J
        graph_name = f"random_sparse_RS{n}_s{seed}"

    else:
        raise ValueError(f"Unknown topology: {topology}")

    return J_matrix, graph_name


def compute_spectral_gap_general_n(
    F: np.ndarray,
    q: int,
    max_samples: int = 5000
) -> Tuple[float, float, float, np.ndarray]:
    """
    Compute beta_c, L_gap, W for given q.

    For large m, uses random sampling instead of exhaustive search.

    Args:
        F: (m, m) positive definite Fisher matrix
        q: Number of negative signs
        max_samples: Maximum sign assignments to sample

    Returns:
        beta_c: Critical beta value
        L_gap: Spectral gap ratio
        W: Spectral gap weighting
        S_optimal: Optimal sign assignment
    """
    m = F.shape[0]

    if q < 1 or q >= m:
        return 0.0, 0.0, 0.0, np.ones(m)

    # F^{1/2} for transformation
    eig_vals, eig_vecs = np.linalg.eigh(F)
    F_sqrt = eig_vecs @ np.diag(np.sqrt(np.maximum(eig_vals, 1e-12))) @ eig_vecs.T

    # Determine if we should use exhaustive or sampling
    from scipy.special import comb
    n_total = comb(m, q, exact=True)
    use_sampling = n_total > max_samples

    best_beta_c = 0.0
    best_L_gap = 0.0
    best_W = 0.0
    best_S = np.ones(m)

    if use_sampling:
        # Random sampling
        rng = np.random.default_rng(42)

        for _ in range(max_samples):
            # Random q negative edges
            neg_indices = rng.choice(m, size=q, replace=False)
            S = np.ones(m)
            S[neg_indices] = -1
            S_diag = np.diag(S)

            # Compute A = F^{1/2} S F^{1/2}
            A = F_sqrt @ S_diag @ F_sqrt

            # Eigenvalues (sorted ascending)
            eigs = np.linalg.eigvalsh(A)
            d_1 = eigs[0]
            d_2 = eigs[1] if len(eigs) > 1 else eigs[0]

            # beta_c = -d_1 (if d_1 < 0)
            if d_1 < -1e-10:
                beta_c = -d_1
                L_gap = (d_2 - d_1) / abs(d_1) if abs(d_1) > 1e-10 else 0.0
                W = beta_c * L_gap

                if W > best_W:
                    best_W = W
                    best_beta_c = beta_c
                    best_L_gap = L_gap
                    best_S = S.copy()
    else:
        # Exhaustive search
        for neg_indices in itertools.combinations(range(m), q):
            S = np.ones(m)
            S[list(neg_indices)] = -1
            S_diag = np.diag(S)

            # Compute A = F^{1/2} S F^{1/2}
            A = F_sqrt @ S_diag @ F_sqrt

            # Eigenvalues (sorted ascending)
            eigs = np.linalg.eigvalsh(A)
            d_1 = eigs[0]
            d_2 = eigs[1] if len(eigs) > 1 else eigs[0]

            # beta_c = -d_1 (if d_1 < 0)
            if d_1 < -1e-10:
                beta_c = -d_1
                L_gap = (d_2 - d_1) / abs(d_1) if abs(d_1) > 1e-10 else 0.0
                W = beta_c * L_gap

                if W > best_W:
                    best_W = W
                    best_beta_c = beta_c
                    best_L_gap = L_gap
                    best_S = S.copy()

    return best_beta_c, best_L_gap, best_W, best_S


def verify_tree_diagonal_theorem(n: int, topology: str, J: float) -> TreeDiagonalProof:
    """
    Verify that tree graphs have diagonal Fisher matrices.

    Tree Fisher Identity: F = sech²(J) × I_m

    Args:
        n: Number of vertices
        topology: Tree topology ('path', 'star', 'random_tree')
        J: Coupling strength

    Returns:
        TreeDiagonalProof with verification results
    """
    J_matrix, graph_name = create_tree_graph(n, topology, J)

    # Compute Fisher matrix
    F, edges = compute_exact_fisher_ising(J_matrix)
    m = len(edges)

    if m < 2:
        # Degenerate case
        return TreeDiagonalProof(
            graph_name=graph_name,
            n=n,
            m=m,
            coupling_J=J,
            F_diagonal=np.array([]),
            F_off_diagonal_max=0.0,
            expected_diagonal=0.0,
            diagonal_match_error=0.0,
            eigenvalues_signed=np.array([]),
            q1_beta_c=0.0,
            q1_L_gap=0.0,
            q1_W=0.0,
            q2_W=0.0,
            is_tree=True,
            is_diagonal=True
        )

    # Check diagonal structure
    F_diag = np.diag(F)
    F_off_diag_mask = ~np.eye(m, dtype=bool)
    F_off_diag_max = np.max(np.abs(F[F_off_diag_mask])) if m > 1 else 0.0

    # Expected diagonal value (Tree Fisher Identity)
    expected_diag = 1.0 / np.cosh(J)**2  # sech²(J)
    diag_error = np.max(np.abs(F_diag - expected_diag))

    is_diagonal = F_off_diag_max < 1e-6

    # Compute q=1 spectral properties
    beta_c_q1, L_gap_q1, W_q1, S_q1 = compute_spectral_gap_general_n(F, q=1)

    # For diagonal F, eigenvalues of F^{1/2} S F^{1/2} = F^{1/2} diag(S) F^{1/2}
    # = diag(sqrt(F_ii) * S_i * sqrt(F_ii)) = diag(F_ii * S_i)
    # So eigenvalues are just {F_ii * S_i} with appropriate signs
    S_diag_q1 = np.diag(S_q1)
    eigenvalues_signed = F_diag * np.diag(S_diag_q1)

    # Compute q=2 (should have W=0 for diagonal case)
    beta_c_q2, L_gap_q2, W_q2, S_q2 = compute_spectral_gap_general_n(F, q=2)

    return TreeDiagonalProof(
        graph_name=graph_name,
        n=n,
        m=m,
        coupling_J=J,
        F_diagonal=F_diag,
        F_off_diagonal_max=F_off_diag_max,
        expected_diagonal=expected_diag,
        diagonal_match_error=diag_error,
        eigenvalues_signed=eigenvalues_signed,
        q1_beta_c=beta_c_q1,
        q1_L_gap=L_gap_q1,
        q1_W=W_q1,
        q2_W=W_q2,
        is_tree=True,
        is_diagonal=is_diagonal
    )


def analyze_general_n_scaling(
    n_values: List[int],
    topologies: List[str],
    J_values: List[float],
    max_q: Optional[int] = None
) -> List[GeneralNResult]:
    """
    Analyze spectral gap selection across multiple dimensions n.

    Args:
        n_values: List of parameter space dimensions
        topologies: List of graph topologies
        J_values: List of coupling strengths
        max_q: Maximum q to test (default: min(m-1, 10))

    Returns:
        List of GeneralNResult objects
    """
    results = []

    print(f"{'Graph':<20} {'n':<4} {'m':<4} {'J':<6} {'F_diag':<8} "
          f"{'q_max':<6} {'W(q=1)':<10} {'W_max_higher':<12} {'margin':<10} {'q=1 wins?'}")
    print("-" * 110)

    for n in n_values:
        for topology in topologies:
            for J in J_values:
                try:
                    # Create graph
                    if topology in ['path', 'star', 'random_tree']:
                        J_matrix, graph_name = create_tree_graph(n, topology, J)
                    elif topology in ['cycle', 'random_sparse']:
                        J_matrix, graph_name = create_sparse_graph(n, topology, J)
                    else:
                        continue

                    # Compute Fisher matrix
                    F, edges = compute_exact_fisher_ising(J_matrix)
                    m = len(edges)

                    if m < 3:
                        continue

                    # Fisher matrix properties
                    eig_vals_F = np.linalg.eigvalsh(F)
                    F_cond = eig_vals_F[-1] / eig_vals_F[0] if eig_vals_F[0] > 1e-12 else np.inf

                    F_diag = np.diag(np.diag(F))
                    F_off = F - F_diag
                    F_diagonality = np.linalg.norm(F_off, 'fro') / np.linalg.norm(F, 'fro')

                    # Compute W(q) for each q
                    q_max_test = max_q if max_q is not None else min(m - 1, 10)

                    W_values = {}
                    beta_c_values = {}
                    L_gap_values = {}

                    for q in range(1, q_max_test + 1):
                        beta_c, L_gap, W, S = compute_spectral_gap_general_n(F, q)
                        W_values[q] = W
                        beta_c_values[q] = beta_c
                        L_gap_values[q] = L_gap

                    # Determine winner
                    q_max_W = max(W_values.keys(), key=lambda q: W_values[q])
                    W_q1 = W_values[1]
                    W_max_higher = max((W_values[q] for q in W_values if q >= 2), default=0.0)

                    margin = W_q1 - W_max_higher
                    margin_rel = margin / W_q1 if W_q1 > 1e-10 else 0.0
                    q1_wins = W_q1 > W_max_higher

                    result = GeneralNResult(
                        n=n,
                        m=m,
                        graph_name=graph_name,
                        topology=topology,
                        coupling_J=J,
                        F_condition_number=F_cond,
                        F_diagonality=F_diagonality,
                        W_values=W_values,
                        beta_c_values=beta_c_values,
                        L_gap_values=L_gap_values,
                        q_max=q_max_W,
                        W_q1=W_q1,
                        W_max_higher=W_max_higher,
                        margin=margin,
                        margin_relative=margin_rel,
                        q1_wins=q1_wins
                    )

                    results.append(result)

                    wins = "YES" if q1_wins else "NO"
                    print(f"{graph_name:<20} {n:<4} {m:<4} {J:<6.2f} {F_diagonality:<8.4f} "
                          f"{q_max_W:<6} {W_q1:<10.4f} {W_max_higher:<12.4f} {margin:<10.4f} {wins}")

                except Exception as e:
                    print(f"Error on {topology} n={n} J={J}: {e}")
                    continue

    return results


def main():
    """Run general-n spectral gap analysis."""

    print("=" * 110)
    print("GENERAL-N SPECTRAL GAP SELECTION THEOREM VERIFICATION")
    print("=" * 110)
    print()
    print("Testing n = 3, 4, 5, 6, 8, 10, 15, 20")
    print("Topologies: path, star, cycle, random_tree, random_sparse")
    print()

    # Test parameters
    n_values = [3, 4, 5, 6, 8, 10, 15, 20]
    topologies = ['path', 'star', 'cycle', 'random_tree', 'random_sparse']
    J_values = [0.1, 0.5, 1.0]

    print("\n" + "=" * 110)
    print("PART 1: Tree Diagonal Theorem Verification")
    print("=" * 110)
    print()

    tree_results = []
    for n in [3, 5, 8, 12, 20]:
        for topology in ['path', 'star', 'random_tree']:
            for J in [0.5]:
                result = verify_tree_diagonal_theorem(n, topology, J)
                tree_results.append(result)

                print(f"{result.graph_name}: "
                      f"diagonal={result.is_diagonal}, "
                      f"off_diag_max={result.F_off_diagonal_max:.2e}, "
                      f"diag_error={result.diagonal_match_error:.2e}, "
                      f"W(q=1)={result.q1_W:.4f}, "
                      f"W(q=2)={result.q2_W:.4f}")

    print("\n" + "=" * 110)
    print("PART 2: General-n Scaling Analysis")
    print("=" * 110)
    print()

    results = analyze_general_n_scaling(
        n_values=n_values,
        topologies=topologies,
        J_values=J_values,
        max_q=None  # Auto-determine based on m
    )

    # Summary statistics
    print("\n" + "=" * 110)
    print("SUMMARY STATISTICS")
    print("=" * 110)
    print()

    total = len(results)
    q1_wins_count = sum(1 for r in results if r.q1_wins)
    percentage = 100 * q1_wins_count / total if total > 0 else 0

    print(f"Total cases: {total}")
    print(f"q=1 wins: {q1_wins_count} ({percentage:.1f}%)")
    print()

    # By topology
    print("By topology:")
    for topology in topologies:
        topo_results = [r for r in results if r.topology == topology]
        if topo_results:
            topo_total = len(topo_results)
            topo_q1_wins = sum(1 for r in topo_results if r.q1_wins)
            topo_pct = 100 * topo_q1_wins / topo_total
            print(f"  {topology:<15}: {topo_q1_wins:3}/{topo_total:3} ({topo_pct:5.1f}%)")
    print()

    # By n
    print("By dimension n:")
    for n in sorted(set(r.n for r in results)):
        n_results = [r for r in results if r.n == n]
        if n_results:
            n_total = len(n_results)
            n_q1_wins = sum(1 for r in n_results if r.q1_wins)
            n_pct = 100 * n_q1_wins / n_total
            print(f"  n={n:2}: {n_q1_wins:3}/{n_total:3} ({n_pct:5.1f}%)")
    print()

    # Diagonality correlation
    near_diagonal = [r for r in results if r.F_diagonality < 0.1]
    if near_diagonal:
        nd_total = len(near_diagonal)
        nd_q1_wins = sum(1 for r in near_diagonal if r.q1_wins)
        nd_pct = 100 * nd_q1_wins / nd_total
        print(f"Near-diagonal (F_diag < 0.1): {nd_q1_wins}/{nd_total} ({nd_pct:.1f}%)")

    far_diagonal = [r for r in results if r.F_diagonality >= 0.1]
    if far_diagonal:
        fd_total = len(far_diagonal)
        fd_q1_wins = sum(1 for r in far_diagonal if r.q1_wins)
        fd_pct = 100 * fd_q1_wins / fd_total
        print(f"Far-from-diagonal (F_diag >= 0.1): {fd_q1_wins}/{fd_total} ({fd_pct:.1f}%)")

    print("\n" + "=" * 110)
    print("ANALYSIS COMPLETE")
    print("=" * 110)

    return results, tree_results


if __name__ == "__main__":
    results, tree_results = main()
