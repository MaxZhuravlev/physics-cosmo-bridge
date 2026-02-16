#!/usr/bin/env python3
"""
Systematic study of edge sign selection strategies for Lorentzian signature.

Tests 4 strategies on 20+ graph topologies to determine which mechanisms
produce exactly q=1 (one negative eigenvalue) in the mass tensor M.

Strategies:
  A: Bipartite Graph Coloring
  B: Fiedler Vector (Spectral Clustering)
  C: Information Flow Direction
  D: Maximum Spectral Gap (Oracle/Brute Force)

Author: Claude Code (Developer Agent)
Date: 2026-02-16
"""

import numpy as np
import scipy.linalg
import networkx as nx
from itertools import product, combinations
from typing import List, Tuple, Dict
import warnings
warnings.filterwarnings('ignore')


# ============================================================================
# FISHER MATRIX COMPUTATION (Ising Model)
# ============================================================================

def compute_exact_fisher_ising(n_vertices: int, edges: List[Tuple[int, int]], J: float) -> np.ndarray:
    """
    Compute exact Fisher information matrix for Ising model.

    Args:
        n_vertices: Number of vertices
        edges: List of edge tuples (i, j)
        J: Coupling strength

    Returns:
        F: Fisher information matrix (m × m), m = number of edges
    """
    m = len(edges)
    states = np.array(list(product([-1, 1], repeat=n_vertices)))

    # Compute sufficient statistics (edge products)
    phi = np.zeros((len(states), m))
    for idx, (i, j) in enumerate(edges):
        phi[:, idx] = states[:, i] * states[:, j]

    # Boltzmann weights
    energy = -J * phi.sum(axis=1)
    log_Z = np.log(np.sum(np.exp(-energy)))
    probs = np.exp(-energy - log_Z)

    # Fisher = covariance of sufficient statistics
    mean_phi = probs @ phi
    F = np.zeros((m, m))
    for a in range(m):
        for b in range(m):
            F[a, b] = np.sum(probs * phi[:, a] * phi[:, b]) - mean_phi[a] * mean_phi[b]

    return F


# ============================================================================
# SPECTRAL GAP COMPUTATION
# ============================================================================

def spectral_gap_weighting(F: np.ndarray, signs: np.ndarray) -> float:
    """
    Compute W = β_c × L_gap for given sign assignment.

    Args:
        F: Fisher information matrix (m × m)
        signs: Sign array (m,) with values ±1

    Returns:
        W: Spectral gap weighting (0 if not Lorentzian)
    """
    m = len(signs)
    S = np.diag(signs)

    # Compute eigenvalues of F^{1/2} S F^{1/2}
    F_sqrt = scipy.linalg.sqrtm(F)
    A = F_sqrt @ S @ F_sqrt
    eigs = np.sort(np.real(np.linalg.eigvalsh(A)))

    d1 = eigs[0]  # Most negative
    d2 = eigs[1]  # Second eigenvalue

    if d1 >= 0:
        return 0.0  # No Lorentzian transition

    beta_c = -d1
    L_gap = (d2 - d1) / abs(d1)
    W = beta_c * L_gap

    return W


def count_negative_eigenvalues(F: np.ndarray, signs: np.ndarray) -> int:
    """Count number of negative eigenvalues (q)."""
    S = np.diag(signs)
    F_sqrt = scipy.linalg.sqrtm(F)
    A = F_sqrt @ S @ F_sqrt
    eigs = np.real(np.linalg.eigvalsh(A))
    return np.sum(eigs < -1e-10)


# ============================================================================
# STRATEGY A: BIPARTITE GRAPH COLORING
# ============================================================================

def strategy_bipartite_coloring(G: nx.Graph, edges: List[Tuple[int, int]], F: np.ndarray) -> Tuple[np.ndarray, str]:
    """
    Strategy A: Use bipartite coloring to assign edge signs.

    Edges between different colors: s_e = -1
    Edges within same color: s_e = +1

    For non-bipartite: use approximate 2-coloring (min cut).
    """
    m = len(edges)
    signs = np.ones(m)

    if nx.is_bipartite(G):
        # Exact 2-coloring
        color = nx.bipartite.color(G)
        status = "bipartite_exact"

        for idx, (i, j) in enumerate(edges):
            if color[i] != color[j]:
                # Assign negative to one cross-partition edge (first one)
                if np.sum(signs == -1) == 0:
                    signs[idx] = -1
    else:
        # Approximate: use Fiedler vector to partition
        status = "bipartite_approx"
        if G.number_of_nodes() > 2:
            try:
                fiedler = nx.fiedler_vector(G)
                partition = fiedler > 0

                for idx, (i, j) in enumerate(edges):
                    if partition[i] != partition[j]:
                        if np.sum(signs == -1) == 0:
                            signs[idx] = -1
            except:
                # Fallback: assign first edge as negative
                signs[0] = -1
                status = "bipartite_fallback"
        else:
            signs[0] = -1
            status = "bipartite_fallback"

    return signs, status


# ============================================================================
# STRATEGY B: FIEDLER VECTOR (SPECTRAL CLUSTERING)
# ============================================================================

def strategy_fiedler_vector(G: nx.Graph, edges: List[Tuple[int, int]], F: np.ndarray) -> Tuple[np.ndarray, str]:
    """
    Strategy B: Use Fiedler vector to partition graph into timelike/spacelike.

    Edges crossing Fiedler partition: candidates for s_e = -1
    Select the one with highest Fisher information.
    """
    m = len(edges)
    signs = np.ones(m)

    if G.number_of_nodes() <= 2:
        signs[0] = -1
        return signs, "fiedler_trivial"

    try:
        fiedler = nx.fiedler_vector(G)
        partition = fiedler > 0

        # Find edges crossing partition
        crossing_edges = []
        for idx, (i, j) in enumerate(edges):
            if partition[i] != partition[j]:
                crossing_edges.append(idx)

        if len(crossing_edges) == 0:
            # No crossing edges, use first edge
            signs[0] = -1
            return signs, "fiedler_no_crossing"

        # Select crossing edge with highest Fisher diagonal
        F_diag = np.diag(F)
        best_idx = crossing_edges[np.argmax(F_diag[crossing_edges])]
        signs[best_idx] = -1

        return signs, "fiedler_success"

    except:
        # Fallback
        signs[0] = -1
        return signs, "fiedler_fallback"


# ============================================================================
# STRATEGY C: INFORMATION FLOW DIRECTION
# ============================================================================

def strategy_information_flow(G: nx.Graph, edges: List[Tuple[int, int]], F: np.ndarray) -> Tuple[np.ndarray, str]:
    """
    Strategy C: Assign s_e = -1 to edge with maximum Fisher diagonal.

    The most informative edge becomes "timelike".
    """
    m = len(edges)
    signs = np.ones(m)

    # Find edge with maximum Fisher information
    F_diag = np.diag(F)
    max_idx = np.argmax(F_diag)
    signs[max_idx] = -1

    return signs, "info_flow_success"


# ============================================================================
# STRATEGY D: BRUTE FORCE ORACLE (Maximum W)
# ============================================================================

def strategy_brute_force_oracle(G: nx.Graph, edges: List[Tuple[int, int]], F: np.ndarray) -> Tuple[np.ndarray, str]:
    """
    Strategy D: Try all possible q=1 sign assignments, select the one with maximum W.

    This is the oracle - it always finds the best q=1 configuration.
    """
    m = len(edges)
    best_W = -np.inf
    best_signs = None

    # Try each single-negative assignment
    for neg_idx in range(m):
        signs = np.ones(m)
        signs[neg_idx] = -1

        W = spectral_gap_weighting(F, signs)
        if W > best_W:
            best_W = W
            best_signs = signs.copy()

    return best_signs, "oracle_success"


# ============================================================================
# GRAPH TOPOLOGY GENERATORS
# ============================================================================

def generate_test_graphs() -> List[Tuple[str, nx.Graph]]:
    """Generate 20+ test graph topologies."""
    graphs = []

    # Trees: Paths
    for n in [3, 4, 5, 6]:
        graphs.append((f"Path_P{n}", nx.path_graph(n)))

    # Trees: Stars
    for n in [4, 5, 6]:
        graphs.append((f"Star_S{n}", nx.star_graph(n-1)))

    # Trees: Binary trees
    graphs.append(("BinaryTree_D2", nx.balanced_tree(2, 2)))
    graphs.append(("BinaryTree_D3", nx.balanced_tree(2, 3)))

    # Cycles
    for n in [4, 5, 6, 8]:
        graphs.append((f"Cycle_C{n}", nx.cycle_graph(n)))

    # Complete graphs
    for n in [3, 4, 5]:
        graphs.append((f"Complete_K{n}", nx.complete_graph(n)))

    # Lattices
    graphs.append(("Lattice_2x3", nx.grid_2d_graph(2, 3)))
    graphs.append(("Lattice_3x3", nx.grid_2d_graph(3, 3)))
    graphs.append(("Lattice_2x4", nx.grid_2d_graph(2, 4)))

    # Regular graphs
    graphs.append(("Petersen", nx.petersen_graph()))
    graphs.append(("Cube", nx.cubical_graph()))

    # Wheel
    graphs.append(("Wheel_W5", nx.wheel_graph(6)))

    # Complete bipartite
    graphs.append(("CompleteBipartite_K23", nx.complete_bipartite_graph(2, 3)))
    graphs.append(("CompleteBipartite_K33", nx.complete_bipartite_graph(3, 3)))

    # Random graphs (deterministic seeds)
    np.random.seed(42)
    for n, p in [(8, 0.3), (8, 0.5), (10, 0.3), (10, 0.5), (12, 0.3)]:
        seed = hash((n, p)) % 2**32
        G = nx.erdos_renyi_graph(n, p, seed=seed)
        if G.number_of_edges() > 0:
            graphs.append((f"Random_G{n}_p{p}", G))

    return graphs


# ============================================================================
# MAIN EVALUATION
# ============================================================================

def evaluate_strategies():
    """Run systematic evaluation of all strategies on all graphs."""

    strategies = {
        'A_Bipartite': strategy_bipartite_coloring,
        'B_Fiedler': strategy_fiedler_vector,
        'C_InfoFlow': strategy_information_flow,
        'D_Oracle': strategy_brute_force_oracle,
    }

    J_values = [0.5, 1.0]

    print("=" * 120)
    print("SYSTEMATIC SIGN SELECTION STUDY")
    print("=" * 120)
    print()
    print(f"{'Strategy':<15} {'Topology':<25} {'J':<6} {'q_prod':<7} {'W_strat':<10} {'W_oracle':<10} {'Quality':<10} {'Status':<20}")
    print("-" * 120)

    results = []

    for graph_name, G in generate_test_graphs():
        # Convert to simple graph with integer labels
        G = nx.convert_node_labels_to_integers(G)

        # Skip graphs that are too large for exact Fisher
        if G.number_of_nodes() > 12:
            continue

        # Skip disconnected graphs
        if not nx.is_connected(G):
            continue

        edges = list(G.edges())
        m = len(edges)

        if m == 0:
            continue

        for J in J_values:
            # Compute Fisher matrix
            try:
                F = compute_exact_fisher_ising(G.number_of_nodes(), edges, J)
            except:
                continue

            # First get oracle result
            oracle_signs, oracle_status = strategies['D_Oracle'](G, edges, F)
            W_oracle = spectral_gap_weighting(F, oracle_signs)
            q_oracle = count_negative_eigenvalues(F, oracle_signs)

            # Test each strategy
            for strategy_name, strategy_func in strategies.items():
                signs, status = strategy_func(G, edges, F)

                q_prod = count_negative_eigenvalues(F, signs)
                W_strat = spectral_gap_weighting(F, signs)

                quality_ratio = W_strat / W_oracle if W_oracle > 1e-10 else 0.0

                print(f"{strategy_name:<15} {graph_name:<25} {J:<6.1f} {q_prod:<7} {W_strat:<10.4f} {W_oracle:<10.4f} {quality_ratio:<10.4f} {status:<20}")

                results.append({
                    'strategy': strategy_name,
                    'topology': graph_name,
                    'J': J,
                    'q_produced': q_prod,
                    'W_strategy': W_strat,
                    'W_oracle': W_oracle,
                    'quality_ratio': quality_ratio,
                    'status': status,
                    'n_vertices': G.number_of_nodes(),
                    'n_edges': m,
                })

    print("=" * 120)
    print()

    # Summary statistics
    print("SUMMARY STATISTICS BY STRATEGY")
    print("=" * 120)
    print(f"{'Strategy':<15} {'Success Rate':<15} {'Mean Quality':<15} {'Median Quality':<15} {'Total Tests':<12}")
    print("-" * 120)

    for strategy_name in strategies.keys():
        strategy_results = [r for r in results if r['strategy'] == strategy_name]

        if len(strategy_results) == 0:
            continue

        # Success rate: fraction producing q=1
        success_count = sum(1 for r in strategy_results if r['q_produced'] == 1)
        success_rate = success_count / len(strategy_results)

        # Quality metrics
        qualities = [r['quality_ratio'] for r in strategy_results if r['q_produced'] == 1]
        mean_quality = np.mean(qualities) if len(qualities) > 0 else 0.0
        median_quality = np.median(qualities) if len(qualities) > 0 else 0.0

        print(f"{strategy_name:<15} {success_rate:<15.3f} {mean_quality:<15.3f} {median_quality:<15.3f} {len(strategy_results):<12}")

    print("=" * 120)
    print()

    # Per-strategy breakdown
    print("DETAILED BREAKDOWN")
    print("=" * 120)

    for strategy_name in ['A_Bipartite', 'B_Fiedler', 'C_InfoFlow']:
        print(f"\nStrategy {strategy_name}:")
        print("-" * 60)

        strategy_results = [r for r in results if r['strategy'] == strategy_name]

        # Group by q_produced
        for q_val in sorted(set(r['q_produced'] for r in strategy_results)):
            q_results = [r for r in strategy_results if r['q_produced'] == q_val]
            print(f"  q={q_val}: {len(q_results)} cases ({len(q_results)/len(strategy_results)*100:.1f}%)")

            if q_val == 1 and len(q_results) > 0:
                qualities = [r['quality_ratio'] for r in q_results]
                print(f"    Quality ratio: mean={np.mean(qualities):.3f}, median={np.median(qualities):.3f}, min={np.min(qualities):.3f}, max={np.max(qualities):.3f}")

        # Status breakdown
        print("  Status breakdown:")
        statuses = {}
        for r in strategy_results:
            status = r['status']
            statuses[status] = statuses.get(status, 0) + 1
        for status, count in sorted(statuses.items()):
            print(f"    {status}: {count}")

    print()
    print("=" * 120)


if __name__ == '__main__':
    evaluate_strategies()
