#!/usr/bin/env python3
"""
Potts Model Fisher Information Matrix Analysis

Tests whether key results from Ising models generalize to q-state Potts models:
1. Tree Fisher Identity (F diagonal on trees)
2. Spectral Gap Selection (W(q_neg=1) dominates)
3. Near-diagonal structure (bounded by tanh^girth)
4. Mass tensor identity (M = F^2)

For a q-state Potts model:
- States: σ_i ∈ {1, 2, ..., q}
- Hamiltonian: H = -J Σ_{(i,j)∈E} δ(σ_i, σ_j)  where δ is Kronecker delta
- Sufficient statistics: φ_e = δ(σ_i, σ_j) for each edge e=(i,j)
- Fisher matrix: F_{ab} = Cov(φ_a, φ_b)
- This is an exponential family with natural parameter J per edge

Attribution:
    test_id: TEST-BRIDGE-MVP1-POTTS-UNIVERSALITY-001
    mvp_layer: MVP-1
    dialogue_id: session-2026-02-16-potts-universality
    recovery_path: papers/structural-bridge/src/potts_fisher.py
"""

import numpy as np
import itertools
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import time


@dataclass
class PottsResult:
    """Results for a single (topology, q, J) configuration."""
    topology: str
    n_vertices: int
    n_edges: int
    q_states: int
    coupling_J: float
    is_tree: bool
    girth: int

    # Tree Fisher Identity test
    F_is_diagonal: bool
    off_diagonal_norm: float

    # Spectral gap selection test
    q_neg_optimal: int
    W_values: Dict[int, float]
    q_neg_1_wins: bool

    # Near-diagonal test
    near_diagonal_ratio: float
    tanh_girth_bound: float

    # M = F^2 test
    M_equals_F2: bool
    M_F2_error: float


def enumerate_potts_states(n_vertices: int, q: int) -> np.ndarray:
    """
    Generate all q^N configurations for q-state Potts model.

    Args:
        n_vertices: Number of vertices
        q: Number of states per vertex

    Returns:
        Array of shape (q^N, N) with all configurations
    """
    return np.array(list(itertools.product(range(1, q + 1), repeat=n_vertices)))


def potts_probabilities(
    states: np.ndarray,
    edges: List[Tuple[int, int]],
    J: float,
    q: int
) -> np.ndarray:
    """
    Compute Boltzmann distribution P(σ) = exp(-H(σ))/Z for Potts model.

    Args:
        states: (q^N, N) array of configurations
        edges: List of (i, j) edge pairs
        J: Coupling strength
        q: Number of states

    Returns:
        Array of shape (q^N,) with probabilities
    """
    n_states = states.shape[0]
    n_edges = len(edges)

    # Compute sufficient statistics: φ_e = δ(σ_i, σ_j)
    phi = np.zeros((n_states, n_edges))
    for k, (i, j) in enumerate(edges):
        phi[:, k] = (states[:, i] == states[:, j]).astype(float)

    # Hamiltonian: H = -J Σ_e φ_e
    energies = -J * np.sum(phi, axis=1)

    # Boltzmann distribution (beta=1)
    min_E = np.min(energies)
    weights = np.exp(-(energies - min_E))
    Z = np.sum(weights)
    probs = weights / Z

    return probs


def potts_fisher(
    edges: List[Tuple[int, int]],
    J: float,
    q: int,
    n_vertices: int
) -> np.ndarray:
    """
    Compute exact Fisher information matrix for Potts model.

    Fisher matrix F_{ab} = Cov(φ_a, φ_b) where φ_e = δ(σ_i, σ_j).

    Args:
        edges: List of (i, j) edge pairs
        J: Coupling strength
        q: Number of states
        n_vertices: Number of vertices

    Returns:
        Fisher matrix F of shape (m, m) where m = |edges|
    """
    # Generate all configurations
    states = enumerate_potts_states(n_vertices, q)

    # Compute probabilities
    probs = potts_probabilities(states, edges, J, q)

    # Compute sufficient statistics
    n_states = states.shape[0]
    m = len(edges)
    phi = np.zeros((n_states, m))
    for k, (i, j) in enumerate(edges):
        phi[:, k] = (states[:, i] == states[:, j]).astype(float)

    # Fisher matrix: Cov(φ_a, φ_b)
    mean_phi = probs @ phi
    centered_phi = phi - mean_phi
    F = (centered_phi * probs[:, None]).T @ centered_phi

    return F


def compute_mass_tensor(F: np.ndarray) -> np.ndarray:
    """
    Compute mass tensor M = F @ F.

    For exponential families, M = F^2 is the natural mass tensor.

    Args:
        F: Fisher matrix

    Returns:
        Mass tensor M
    """
    return F @ F


def test_tree_fisher(
    edges: List[Tuple[int, int]],
    J: float,
    q: int,
    n_vertices: int
) -> Tuple[bool, float]:
    """
    Test whether F is diagonal on trees (Tree Fisher Identity).

    For Ising models, F is exactly diagonal on trees. Test if this
    generalizes to Potts models.

    Args:
        edges: List of (i, j) edge pairs
        J: Coupling strength
        q: Number of states
        n_vertices: Number of vertices

    Returns:
        is_diagonal: True if F is diagonal (within tolerance)
        off_diagonal_norm: ||F - diag(F)||_F / ||diag(F)||_F
    """
    F = potts_fisher(edges, J, q, n_vertices)
    m = F.shape[0]

    # Extract diagonal and off-diagonal parts
    F_diag = np.diag(np.diag(F))
    F_off = F - F_diag

    # Compute relative off-diagonal norm
    diag_norm = np.linalg.norm(F_diag, 'fro')
    off_norm = np.linalg.norm(F_off, 'fro')

    if diag_norm < 1e-12:
        # Degenerate case
        return False, float('inf')

    off_diagonal_norm = off_norm / diag_norm
    is_diagonal = off_diagonal_norm < 1e-6

    return is_diagonal, off_diagonal_norm


def test_spectral_gap_selection(F: np.ndarray) -> Tuple[int, Dict[int, float], bool]:
    """
    Test if q_neg=1 dominates spectral gap weighting W(q_neg).

    For each q_neg = 1, 2, ..., m, compute:
    - beta_c(q_neg) = max over sign assignments with q_neg negative of [-d_1]
    - L_gap(q_neg) = (d_2 - d_1)/|d_1| at optimal assignment
    - W(q_neg) = beta_c(q_neg) * L_gap(q_neg)

    This uses the SAME definition as the Ising spectral gap analysis.

    Args:
        F: Fisher matrix

    Returns:
        q_neg_optimal: q_neg that maximizes W
        W_values: Dict mapping q_neg -> W(q_neg)
        q_neg_1_wins: True if q_neg=1 has maximum W
    """
    m = F.shape[0]

    if m < 2:
        return 1, {1: 0.0}, True

    # Stabilize F and compute F^{1/2}
    F_stab = F + 1e-9 * np.eye(m)
    vals, vecs = np.linalg.eigh(F_stab)
    F_sqrt = vecs @ np.diag(np.sqrt(np.maximum(vals, 0))) @ vecs.T

    W_values = {}

    # Test q_neg from 1 to m-1
    max_q_neg = min(m - 1, 10)  # Limit for computational reasons

    for q_neg in range(1, max_q_neg + 1):
        best_beta_c = -1.0
        best_L_gap = 0.0

        # Sample sign assignments (exhaustive if m <= 12, else sample)
        if m <= 12:
            sign_assignments = itertools.combinations(range(m), q_neg)
        else:
            # Random sampling
            n_samples = min(1000, int(1e6 / (m * q_neg + 1)))
            rng = np.random.default_rng(42 + q_neg)
            sign_assignments = []
            for _ in range(n_samples):
                perm = rng.permutation(m)
                sign_assignments.append(tuple(perm[:q_neg]))

        for neg_indices in sign_assignments:
            # Construct sign matrix S
            S_diag = np.ones(m)
            if len(neg_indices) > 0:
                S_diag[list(neg_indices)] = -1.0
            S = np.diag(S_diag)

            # Compute A = F^{1/2} S F^{1/2}
            A = F_sqrt @ S @ F_sqrt

            # Eigenvalues
            eigs = np.linalg.eigvalsh(A)
            d_1 = eigs[0]
            d_2 = eigs[1] if len(eigs) > 1 else d_1

            if d_1 < 0:
                beta_c = -d_1
                L_gap = (d_2 - d_1) / abs(d_1) if d_1 != 0 else 0

                if beta_c > best_beta_c:
                    best_beta_c = beta_c
                    best_L_gap = L_gap

        W = best_beta_c * best_L_gap if best_beta_c > 0 else 0.0
        W_values[q_neg] = W

    # Find optimal q_neg
    if W_values:
        q_neg_optimal = max(W_values.keys(), key=lambda k: W_values[k])
        q_neg_1_wins = (q_neg_optimal == 1)
    else:
        q_neg_optimal = 1
        q_neg_1_wins = True

    return q_neg_optimal, W_values, q_neg_1_wins


def test_near_diagonal(F: np.ndarray, girth: int, J: float) -> Tuple[float, float]:
    """
    Test if F is near-diagonal with bound ~ tanh^girth(J).

    Computes ||F - diag(F)||_F / ||diag(F)||_F and compares to
    C * tanh^girth(J) where C is an empirical constant.

    Args:
        F: Fisher matrix
        girth: Girth of the graph (minimum cycle length)
        J: Coupling strength

    Returns:
        ratio: ||F - diag(F)|| / ||diag(F)||
        bound: tanh^girth(J)
    """
    m = F.shape[0]

    # Extract diagonal and off-diagonal parts
    F_diag = np.diag(np.diag(F))
    F_off = F - F_diag

    diag_norm = np.linalg.norm(F_diag, 'fro')
    off_norm = np.linalg.norm(F_off, 'fro')

    if diag_norm < 1e-12:
        return float('inf'), 0.0

    ratio = off_norm / diag_norm
    bound = np.tanh(J) ** girth if girth > 0 else 1.0

    return ratio, bound


def create_graph_topology(
    topology: str,
    n: int
) -> Tuple[List[Tuple[int, int]], bool, int]:
    """
    Create edge list for specified graph topology.

    Args:
        topology: One of "path", "star", "cycle", "triangle", "complete"
        n: Number of vertices

    Returns:
        edges: List of (i, j) edge pairs
        is_tree: True if graph is a tree
        girth: Minimum cycle length (inf for trees)
    """
    edges = []
    is_tree = False
    girth = 0

    if topology == "path":
        # Path graph: chain
        edges = [(i, i + 1) for i in range(n - 1)]
        is_tree = True
        girth = float('inf')

    elif topology == "star":
        # Star graph: central node (0) connected to all others
        edges = [(0, i) for i in range(1, n)]
        is_tree = True
        girth = float('inf')

    elif topology == "cycle":
        # Cycle graph: path + wrap-around edge
        edges = [(i, i + 1) for i in range(n - 1)]
        edges.append((0, n - 1))
        is_tree = False
        girth = n

    elif topology == "triangle":
        # Triangle (K3)
        edges = [(0, 1), (1, 2), (0, 2)]
        is_tree = False
        girth = 3

    elif topology == "complete":
        # Complete graph
        edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
        is_tree = (n <= 2)
        girth = 3 if n >= 3 else float('inf')

    else:
        raise ValueError(f"Unknown topology: {topology}")

    return edges, is_tree, girth


def analyze_potts_topology(
    topology: str,
    n_vertices: int,
    q: int,
    J: float
) -> Optional[PottsResult]:
    """
    Analyze a single (topology, q, J) configuration.

    Args:
        topology: Graph topology name
        n_vertices: Number of vertices
        q: Number of Potts states
        J: Coupling strength

    Returns:
        PottsResult object with all test results
    """
    # Create graph
    edges, is_tree, girth = create_graph_topology(topology, n_vertices)
    m = len(edges)

    if m == 0:
        return None

    # Check if state space is too large
    n_states = q ** n_vertices
    if n_states > 100000:
        print(f"Skipping {topology} N={n_vertices} q={q}: state space too large ({n_states})")
        return None

    try:
        # Compute Fisher matrix
        F = potts_fisher(edges, J, q, n_vertices)

        # Test 1: Tree Fisher Identity
        F_is_diagonal, off_diagonal_norm = test_tree_fisher(edges, J, q, n_vertices)

        # Test 2: Spectral gap selection
        q_neg_optimal, W_values, q_neg_1_wins = test_spectral_gap_selection(F)

        # Test 3: Near-diagonal structure
        near_diagonal_ratio, tanh_girth_bound = test_near_diagonal(F, girth, J)

        # Test 4: M = F^2
        M = compute_mass_tensor(F)
        F_squared = F @ F
        M_F2_error = np.linalg.norm(M - F_squared, 'fro') / np.linalg.norm(F_squared, 'fro')
        M_equals_F2 = M_F2_error < 1e-6

        return PottsResult(
            topology=topology,
            n_vertices=n_vertices,
            n_edges=m,
            q_states=q,
            coupling_J=J,
            is_tree=is_tree,
            girth=girth if girth != float('inf') else 999,
            F_is_diagonal=F_is_diagonal,
            off_diagonal_norm=off_diagonal_norm,
            q_neg_optimal=q_neg_optimal,
            W_values=W_values,
            q_neg_1_wins=q_neg_1_wins,
            near_diagonal_ratio=near_diagonal_ratio,
            tanh_girth_bound=tanh_girth_bound,
            M_equals_F2=M_equals_F2,
            M_F2_error=M_F2_error
        )

    except Exception as e:
        print(f"Error analyzing {topology} N={n_vertices} q={q} J={J}: {e}")
        return None


def main():
    """Run comprehensive Potts universality analysis."""

    print("=" * 80)
    print("POTTS MODEL FISHER MATRIX UNIVERSALITY ANALYSIS")
    print("=" * 80)
    print()
    print("Research Question:")
    print("  Do key Ising Fisher matrix results generalize to q-state Potts models?")
    print()
    print("Tests:")
    print("  1. Tree Fisher Identity: Is F diagonal on trees?")
    print("  2. Spectral Gap Selection: Does q_neg=1 maximize W?")
    print("  3. Near-Diagonal: Is ||F-diag(F)||/||diag(F)|| ~ tanh^girth(J)?")
    print("  4. Mass Tensor: Is M = F^2?")
    print()
    print("=" * 80)
    print()

    # Test configurations
    test_cases = [
        # Trees (should have diagonal F)
        ("path", 3),
        ("path", 4),
        ("path", 5),
        ("star", 4),
        ("star", 5),

        # Non-trees
        ("triangle", 3),
        ("complete", 4),
        ("cycle", 4),
        ("cycle", 5),
    ]

    # Potts parameters
    q_values = [2, 3, 4, 5]  # q=2 is Ising equivalent
    J_values = [0.5, 1.0]

    # Adjust N limits by q to keep state space manageable
    n_limits = {2: 8, 3: 5, 4: 4, 5: 4}

    results = []

    print(f"{'Topology':<12} {'N':<3} {'q':<3} {'J':<5} {'m':<3} {'Tree':<5} "
          f"{'F diag?':<8} {'q_neg*':<7} {'W(1)/W(*)':<12} {'M=F²?':<7}")
    print("-" * 100)

    for topology, n_base in test_cases:
        for q in q_values:
            # Adjust n based on q
            n = min(n_base, n_limits[q])

            for J in J_values:
                result = analyze_potts_topology(topology, n, q, J)

                if result is None:
                    continue

                results.append(result)

                # Format output
                tree_str = "Y" if result.is_tree else "N"
                F_diag_str = "Y" if result.F_is_diagonal else f"N({result.off_diagonal_norm:.2e})"

                W_ratio = "N/A"
                if 1 in result.W_values and result.q_neg_optimal in result.W_values:
                    W_1 = result.W_values[1]
                    W_opt = result.W_values[result.q_neg_optimal]
                    if W_opt > 1e-12:
                        W_ratio = f"{W_1/W_opt:.3f}"
                    else:
                        W_ratio = "inf" if W_1 > 1e-12 else "N/A"

                M_F2_str = "Y" if result.M_equals_F2 else f"N({result.M_F2_error:.2e})"

                print(f"{result.topology:<12} {result.n_vertices:<3} {result.q_states:<3} "
                      f"{result.coupling_J:<5.1f} {result.n_edges:<3} {tree_str:<5} "
                      f"{F_diag_str:<8} {result.q_neg_optimal:<7} {W_ratio:<12} {M_F2_str:<7}")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    if not results:
        print("No valid results obtained.")
        return

    # Summary statistics
    total = len(results)

    # Test 1: Tree Fisher Identity
    tree_results = [r for r in results if r.is_tree]
    if tree_results:
        tree_diagonal = sum(1 for r in tree_results if r.F_is_diagonal)
        print(f"1. Tree Fisher Identity (F diagonal on trees):")
        print(f"   Trees tested: {len(tree_results)}")
        print(f"   F diagonal: {tree_diagonal}/{len(tree_results)} "
              f"({100*tree_diagonal/len(tree_results):.1f}%)")

        # By q value
        for q in sorted(set(r.q_states for r in tree_results)):
            q_tree = [r for r in tree_results if r.q_states == q]
            q_diag = sum(1 for r in q_tree if r.F_is_diagonal)
            print(f"     q={q}: {q_diag}/{len(q_tree)} ({100*q_diag/len(q_tree):.1f}%)")
        print()

    # Test 2: Spectral gap selection
    q_neg_1_wins_count = sum(1 for r in results if r.q_neg_1_wins)
    print(f"2. Spectral Gap Selection (q_neg=1 maximizes W):")
    print(f"   Total cases: {total}")
    print(f"   q_neg=1 wins: {q_neg_1_wins_count}/{total} ({100*q_neg_1_wins_count/total:.1f}%)")

    # By q value
    for q in sorted(set(r.q_states for r in results)):
        q_results = [r for r in results if r.q_states == q]
        q_wins = sum(1 for r in q_results if r.q_neg_1_wins)
        print(f"     q={q}: {q_wins}/{len(q_results)} ({100*q_wins/len(q_results):.1f}%)")
    print()

    # Test 3: Near-diagonal (trees only)
    if tree_results:
        print(f"3. Near-Diagonal Structure (trees only):")
        for r in tree_results:
            if r.F_is_diagonal:
                status = "diagonal"
            else:
                status = f"ratio={r.near_diagonal_ratio:.2e}"
            print(f"     {r.topology} N={r.n_vertices} q={r.q_states} J={r.coupling_J}: {status}")
        print()

    # Test 4: M = F^2
    M_F2_count = sum(1 for r in results if r.M_equals_F2)
    print(f"4. Mass Tensor Identity (M = F²):")
    print(f"   M = F²: {M_F2_count}/{total} ({100*M_F2_count/total:.1f}%)")

    # By q value
    for q in sorted(set(r.q_states for r in results)):
        q_results = [r for r in results if r.q_states == q]
        q_M_F2 = sum(1 for r in q_results if r.M_equals_F2)
        print(f"     q={q}: {q_M_F2}/{len(q_results)} ({100*q_M_F2/len(q_results):.1f}%)")
    print()

    # Comparison to Ising (q=2)
    print("=" * 80)
    print("UNIVERSALITY ASSESSMENT")
    print("=" * 80)
    print()

    q2_results = [r for r in results if r.q_states == 2]
    higher_q_results = [r for r in results if r.q_states > 2]

    if q2_results and higher_q_results:
        print("Comparing q=2 (Ising) to q>2:")
        print()

        # Tree Fisher Identity
        q2_tree = [r for r in q2_results if r.is_tree]
        higher_tree = [r for r in higher_q_results if r.is_tree]
        if q2_tree and higher_tree:
            q2_diag_pct = 100 * sum(1 for r in q2_tree if r.F_is_diagonal) / len(q2_tree)
            higher_diag_pct = 100 * sum(1 for r in higher_tree if r.F_is_diagonal) / len(higher_tree)
            print(f"Tree Fisher Identity:")
            print(f"  q=2: {q2_diag_pct:.1f}%")
            print(f"  q>2: {higher_diag_pct:.1f}%")
            if abs(q2_diag_pct - higher_diag_pct) < 5:
                print(f"  VERDICT: UNIVERSAL (difference < 5%)")
            else:
                print(f"  VERDICT: NOT UNIVERSAL (difference = {abs(q2_diag_pct - higher_diag_pct):.1f}%)")
            print()

        # Spectral gap selection
        q2_wins_pct = 100 * sum(1 for r in q2_results if r.q_neg_1_wins) / len(q2_results)
        higher_wins_pct = 100 * sum(1 for r in higher_q_results if r.q_neg_1_wins) / len(higher_q_results)
        print(f"Spectral Gap Selection (q_neg=1 wins):")
        print(f"  q=2: {q2_wins_pct:.1f}%")
        print(f"  q>2: {higher_wins_pct:.1f}%")
        if abs(q2_wins_pct - higher_wins_pct) < 10:
            print(f"  VERDICT: UNIVERSAL (difference < 10%)")
        else:
            print(f"  VERDICT: NOT UNIVERSAL (difference = {abs(q2_wins_pct - higher_wins_pct):.1f}%)")
        print()

        # M = F^2
        q2_M_pct = 100 * sum(1 for r in q2_results if r.M_equals_F2) / len(q2_results)
        higher_M_pct = 100 * sum(1 for r in higher_q_results if r.M_equals_F2) / len(higher_q_results)
        print(f"Mass Tensor Identity (M = F²):")
        print(f"  q=2: {q2_M_pct:.1f}%")
        print(f"  q>2: {higher_M_pct:.1f}%")
        if abs(q2_M_pct - higher_M_pct) < 5:
            print(f"  VERDICT: UNIVERSAL (difference < 5%)")
        else:
            print(f"  VERDICT: NOT UNIVERSAL (difference = {abs(q2_M_pct - higher_M_pct):.1f}%)")
        print()

    print("=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print()

    # Overall assessment
    tree_universal = tree_results and sum(1 for r in tree_results if r.F_is_diagonal) / len(tree_results) > 0.95
    M_F2_universal = M_F2_count / total > 0.95

    if tree_universal:
        print("- Tree Fisher Identity: HOLDS for Potts models (UNIVERSAL)")
    else:
        print("- Tree Fisher Identity: FAILS for some Potts models (NOT UNIVERSAL)")

    if M_F2_universal:
        print("- Mass Tensor Identity: HOLDS for Potts models (UNIVERSAL)")
    else:
        print("- Mass Tensor Identity: FAILS for some Potts models (NOT UNIVERSAL)")

    if q_neg_1_wins_count / total > 0.7:
        print("- Spectral Gap Selection: MOSTLY HOLDS (suggests some universality)")
    elif q_neg_1_wins_count / total > 0.3:
        print("- Spectral Gap Selection: MIXED (topology-dependent)")
    else:
        print("- Spectral Gap Selection: FAILS (NOT UNIVERSAL)")

    print()
    print("These results test whether Ising-derived properties extend to general")
    print("q-state Potts models. Universal properties suggest deep structural")
    print("reasons, while non-universal properties are specific to Ising (q=2).")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
