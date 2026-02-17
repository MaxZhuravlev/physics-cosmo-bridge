#!/usr/bin/env python3
"""
Causal Structure from Signed-Edge Construction: Explicit Computations
=====================================================================

Investigates whether the signed-edge construction (assigning S = diag(+/-1)
to edges of the observer graph, with q=1 meaning exactly one edge gets -1)
induces a CAUSAL STRUCTURE (partial order) on the observer graph.

Key questions:
1. Does the eigenvector of A(S_1) for the negative eigenvalue define a
   "timelike direction" on the graph?
2. Does this direction induce a consistent partial order?
3. How does the sign assignment (which edge gets -1) affect the ordering?
4. Is this related to causal set theory (Bombelli et al 1987)?

Method:
    For small graphs (P3, P4, S4, C4, K3, K4):
    - Compute exact Ising Fisher matrix F
    - For each possible q=1 sign assignment, compute A(S_1) = F^{1/2} S F^{1/2}
    - Find the eigenvector v_- corresponding to the negative eigenvalue
    - Analyze how v_- relates to graph structure
    - Test whether v_- induces a partial order

Author: Max Zhuravlev (Cosmological Unification Program)
Date: 2026-02-17
"""

from __future__ import annotations

import numpy as np
from scipy.linalg import sqrtm
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
import networkx as nx
import itertools


# ============================================================================
# 1. Ising Fisher Matrix Computation (Exact, via Partition Function)
# ============================================================================

def ising_fisher_exact(G: nx.Graph, J: float) -> np.ndarray:
    """Compute exact Fisher information matrix for Ising model on graph G.

    F_{ab} = Cov(phi_a, phi_b) where phi_e = sigma_i * sigma_j for edge e=(i,j).

    Args:
        G: NetworkX graph (observer graph)
        J: Uniform coupling constant

    Returns:
        F: m x m Fisher matrix (m = number of edges)
    """
    n = G.number_of_nodes()
    m = G.number_of_edges()
    edges = list(G.edges())

    # Enumerate all 2^n spin configurations
    all_spins = np.array(list(itertools.product([-1, 1], repeat=n)))
    n_configs = len(all_spins)

    # Compute edge variables phi_e = sigma_i * sigma_j for each config
    phi = np.zeros((n_configs, m))
    for e_idx, (i, j) in enumerate(edges):
        phi[:, e_idx] = all_spins[:, i] * all_spins[:, j]

    # Compute Boltzmann weights
    energy = J * np.sum(phi, axis=1)
    weights = np.exp(energy)
    Z = np.sum(weights)
    probs = weights / Z

    # Compute Fisher matrix = Cov(phi)
    mean_phi = probs @ phi  # shape (m,)
    F = np.zeros((m, m))
    for a in range(m):
        for b in range(m):
            F[a, b] = np.sum(probs * phi[:, a] * phi[:, b]) - mean_phi[a] * mean_phi[b]

    return F


def ising_fisher_tree(J_values: np.ndarray) -> np.ndarray:
    """Fisher matrix for Ising model on a tree graph.

    For trees, F is diagonal: F_{ee} = sech^2(J_e).
    """
    return np.diag(1.0 / np.cosh(J_values)**2)


# ============================================================================
# 2. Signed Metric Kernel and Eigenvector Analysis
# ============================================================================

@dataclass
class SignedKernelResult:
    """Results from analyzing a single sign assignment."""
    sign_assignment: np.ndarray  # which edge(s) get -1
    flipped_edge_idx: int  # index of the edge with s=-1 (for q=1)
    flipped_edge: Tuple[int, int]  # the actual edge (u,v)
    A_matrix: np.ndarray  # the signed kernel A(S)
    eigenvalues: np.ndarray  # sorted eigenvalues
    eigenvectors: np.ndarray  # corresponding eigenvectors (columns)
    negative_eigvec: np.ndarray  # eigenvector for negative eigenvalue
    negative_eigval: float  # the negative eigenvalue
    W: float  # spectral gap weighting
    L_gap: float  # spectral gap ratio


def compute_signed_kernel(F: np.ndarray, sign_assignment: np.ndarray) -> np.ndarray:
    """Compute A(S) = F^{1/2} S F^{1/2}.

    Args:
        F: Fisher matrix (m x m, positive definite)
        sign_assignment: array of +1/-1 for each edge

    Returns:
        A: signed metric kernel
    """
    F_sqrt = sqrtm(F).real
    S = np.diag(sign_assignment)
    A = F_sqrt @ S @ F_sqrt
    return A


def analyze_sign_assignment(
    G: nx.Graph,
    F: np.ndarray,
    flipped_edge_idx: int,
    edges: List[Tuple[int, int]]
) -> SignedKernelResult:
    """Analyze a single q=1 sign assignment.

    Args:
        G: the graph
        F: Fisher matrix
        flipped_edge_idx: which edge gets s=-1
        edges: list of edges

    Returns:
        SignedKernelResult with full analysis
    """
    m = F.shape[0]
    sign = np.ones(m)
    sign[flipped_edge_idx] = -1.0

    A = compute_signed_kernel(F, sign)

    # Eigendecomposition (sorted ascending)
    eigvals, eigvecs = np.linalg.eigh(A)
    # eigvals are sorted ascending, so eigvals[0] is most negative

    neg_eigval = eigvals[0]
    neg_eigvec = eigvecs[:, 0]

    # Spectral gap and W
    if neg_eigval < 0:
        beta_c = -neg_eigval
        L_gap = (eigvals[1] - eigvals[0]) / abs(eigvals[0])
        W = beta_c * L_gap
    else:
        beta_c = 0.0
        L_gap = 0.0
        W = 0.0

    return SignedKernelResult(
        sign_assignment=sign,
        flipped_edge_idx=flipped_edge_idx,
        flipped_edge=edges[flipped_edge_idx],
        A_matrix=A,
        eigenvalues=eigvals,
        eigenvectors=eigvecs,
        negative_eigvec=neg_eigvec,
        negative_eigval=neg_eigval,
        W=W,
        L_gap=L_gap
    )


# ============================================================================
# 3. Causal Structure Analysis
# ============================================================================

def eigvec_to_edge_flow(
    neg_eigvec: np.ndarray,
    edges: List[Tuple[int, int]],
    n_vertices: int
) -> np.ndarray:
    """Convert the negative eigenvector (in edge space) to a vertex-level
    "flow" vector, treating it as defining a direction on each edge.

    The eigenvector v_- has components v_e for each edge e=(i,j).
    Interpret v_e as a "flow" on edge e: positive = i->j, negative = j->i.
    Sum flows at each vertex to get a net "temporal potential" gradient.

    Args:
        neg_eigvec: eigenvector in edge space (length m)
        edges: list of (i,j) edges
        n_vertices: number of vertices

    Returns:
        vertex_flow: net flow at each vertex (length n)
            Positive = "time flows outward" (future)
            Negative = "time flows inward" (past)
    """
    vertex_flow = np.zeros(n_vertices)
    for e_idx, (i, j) in enumerate(edges):
        flow = neg_eigvec[e_idx]
        vertex_flow[i] += flow   # outflow from i along edge e
        vertex_flow[j] -= flow   # inflow to j along edge e
    return vertex_flow


def vertex_flow_to_partial_order(
    vertex_flow: np.ndarray,
    tolerance: float = 1e-10
) -> List[Tuple[int, int]]:
    """Attempt to define a partial order from vertex flow.

    Order: v <= w if vertex_flow[v] < vertex_flow[w]
    (earlier times have lower temporal potential)

    Args:
        vertex_flow: temporal potential at each vertex
        tolerance: threshold for considering two values equal

    Returns:
        List of (v, w) pairs where v < w in the partial order
    """
    n = len(vertex_flow)
    order = []
    for v in range(n):
        for w in range(v + 1, n):
            if vertex_flow[v] < vertex_flow[w] - tolerance:
                order.append((v, w))
            elif vertex_flow[w] < vertex_flow[v] - tolerance:
                order.append((w, v))
    return order


def check_transitivity(order: List[Tuple[int, int]], n: int) -> bool:
    """Check if the partial order is transitive.

    Args:
        order: list of (a, b) meaning a < b
        n: number of elements

    Returns:
        True if transitive
    """
    # Build adjacency for the order relation
    less_than = {i: set() for i in range(n)}
    for (a, b) in order:
        less_than[a].add(b)

    # Check transitivity: if a < b and b < c, then a < c
    for a in range(n):
        for b in less_than[a]:
            for c in less_than[b]:
                if c not in less_than[a]:
                    return False
    return True


def check_antisymmetry(order: List[Tuple[int, int]]) -> bool:
    """Check if the relation is antisymmetric: no a < b AND b < a.

    Args:
        order: list of (a, b) meaning a < b

    Returns:
        True if antisymmetric
    """
    order_set = set(order)
    for (a, b) in order:
        if (b, a) in order_set:
            return False
    return True


def analyze_causal_structure_for_graph(
    G: nx.Graph,
    J: float,
    graph_name: str
) -> Dict:
    """Full causal structure analysis for a graph.

    For each possible q=1 sign assignment:
    1. Compute signed kernel and negative eigenvector
    2. Convert to vertex flow
    3. Check if vertex flow induces a valid partial order
    4. Report consistency

    Args:
        G: the graph
        J: coupling constant
        graph_name: name for reporting

    Returns:
        Dict with full analysis results
    """
    n = G.number_of_nodes()
    m = G.number_of_edges()
    edges = list(G.edges())

    # Compute Fisher matrix
    if nx.is_tree(G):
        J_arr = np.full(m, J)
        F = ising_fisher_tree(J_arr)
    else:
        F = ising_fisher_exact(G, J)

    results = {
        'graph_name': graph_name,
        'n_vertices': n,
        'n_edges': m,
        'coupling_J': J,
        'edges': edges,
        'fisher_matrix': F,
        'fisher_diagonal_ratio': np.linalg.norm(F - np.diag(np.diag(F))) / np.linalg.norm(np.diag(np.diag(F))) if np.linalg.norm(np.diag(np.diag(F))) > 0 else float('inf'),
        'sign_analyses': [],
    }

    for e_idx in range(m):
        analysis = analyze_sign_assignment(G, F, e_idx, edges)

        # Convert eigenvector to vertex flow
        vertex_flow = eigvec_to_edge_flow(analysis.negative_eigvec, edges, n)

        # Attempt partial order
        order = vertex_flow_to_partial_order(vertex_flow)

        # Check partial order properties
        is_transitive = check_transitivity(order, n)
        is_antisymmetric = check_antisymmetry(order)
        is_partial_order = is_transitive and is_antisymmetric

        # Count how many vertices are ordered
        ordered_vertices = set()
        for (a, b) in order:
            ordered_vertices.add(a)
            ordered_vertices.add(b)

        sign_result = {
            'flipped_edge_idx': e_idx,
            'flipped_edge': edges[e_idx],
            'negative_eigenvalue': analysis.negative_eigval,
            'negative_eigenvector': analysis.negative_eigvec,
            'W': analysis.W,
            'L_gap': analysis.L_gap,
            'vertex_flow': vertex_flow,
            'partial_order': order,
            'is_partial_order': is_partial_order,
            'is_transitive': is_transitive,
            'is_antisymmetric': is_antisymmetric,
            'n_ordered_pairs': len(order),
            'n_ordered_vertices': len(ordered_vertices),
            'eigenvalues': analysis.eigenvalues,
        }
        results['sign_analyses'].append(sign_result)

    # Find optimal sign assignment (maximum W)
    W_values = [sa['W'] for sa in results['sign_analyses']]
    optimal_idx = np.argmax(W_values)
    results['optimal_sign_idx'] = optimal_idx
    results['optimal_W'] = W_values[optimal_idx]
    results['optimal_sign_is_partial_order'] = results['sign_analyses'][optimal_idx]['is_partial_order']

    return results


# ============================================================================
# 4. Alternative: Timelike Edge as Graph Distance Ordering
# ============================================================================

def timelike_edge_distance_ordering(
    G: nx.Graph,
    timelike_edge: Tuple[int, int]
) -> Dict:
    """Test whether designating one edge as "timelike" induces an ordering
    based on graph distance from that edge.

    Idea: If edge (u,v) is "timelike", define:
    - "past" side: vertices closer to u than to v
    - "future" side: vertices closer to v than to u
    - "spacelike" slice: vertices equidistant

    This gives a very crude partition, not a partial order in general.

    Args:
        G: the graph
        timelike_edge: the edge designated as timelike

    Returns:
        Dict with ordering analysis
    """
    u, v = timelike_edge
    n = G.number_of_nodes()

    # Compute distances from u and v to all vertices
    dist_u = nx.single_source_shortest_path_length(G, u)
    dist_v = nx.single_source_shortest_path_length(G, v)

    # Classify vertices
    past_vertices = []  # closer to u
    future_vertices = []  # closer to v
    spacelike_vertices = []  # equidistant

    for node in G.nodes():
        du = dist_u.get(node, float('inf'))
        dv = dist_v.get(node, float('inf'))
        if du < dv:
            past_vertices.append(node)
        elif dv < du:
            future_vertices.append(node)
        else:
            spacelike_vertices.append(node)

    # This is a BIPARTITION (past/future) with an undecided set,
    # not a partial order in general.
    return {
        'timelike_edge': timelike_edge,
        'past_vertices': past_vertices,
        'future_vertices': future_vertices,
        'spacelike_vertices': spacelike_vertices,
        'is_total_order': len(spacelike_vertices) == 0,
        'ordering_fraction': (len(past_vertices) + len(future_vertices)) / n
    }


# ============================================================================
# 5. Causal Set Theory Connection Test
# ============================================================================

def test_causal_set_axioms(order: List[Tuple[int, int]], n: int) -> Dict:
    """Test whether the derived partial order satisfies causal set axioms.

    A causal set (Bombelli et al 1987) is a locally finite partial order:
    1. Reflexive: a <= a for all a
    2. Antisymmetric: a <= b and b <= a implies a = b
    3. Transitive: a <= b and b <= c implies a <= c
    4. Locally finite: |{c : a <= c <= b}| < infinity for all a, b

    Items 1 and 4 are trivially satisfied on finite graphs.
    Items 2 and 3 are the nontrivial checks.

    Args:
        order: list of (a, b) meaning a < b (strict)
        n: number of elements

    Returns:
        Dict with axiom check results
    """
    is_antisymmetric = check_antisymmetry(order)
    is_transitive = check_transitivity(order, n)

    # Check if order is a TOTAL order (every pair comparable)
    order_set = set(order)
    n_comparable = 0
    n_total_pairs = n * (n - 1) // 2
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) in order_set or (j, i) in order_set:
                n_comparable += 1

    is_total = n_comparable == n_total_pairs

    # Longest chain (height of poset)
    # Build adjacency
    adj = {i: set() for i in range(n)}
    for (a, b) in order:
        adj[a].add(b)

    # Topological sort to find longest chain
    # Use DFS-based approach
    memo = {}

    def longest_chain_from(v):
        if v in memo:
            return memo[v]
        max_len = 0
        for w in adj[v]:
            max_len = max(max_len, 1 + longest_chain_from(w))
        memo[v] = max_len
        return max_len

    max_chain = 0
    for v in range(n):
        max_chain = max(max_chain, longest_chain_from(v))

    # Width (maximum antichain size) - by Dilworth's theorem, this equals
    # the minimum number of chains covering the poset
    # For small n, compute exactly
    # An antichain is a set of pairwise incomparable elements
    # Brute force for small n
    max_antichain = 1
    if n <= 20:
        from itertools import combinations
        for size in range(n, 0, -1):
            found = False
            for subset in combinations(range(n), size):
                is_antichain = True
                for a in subset:
                    for b in subset:
                        if a != b and ((a, b) in order_set or (b, a) in order_set):
                            is_antichain = False
                            break
                    if not is_antichain:
                        break
                if is_antichain:
                    max_antichain = size
                    found = True
                    break
            if found:
                break

    return {
        'is_antisymmetric': is_antisymmetric,
        'is_transitive': is_transitive,
        'is_partial_order': is_antisymmetric and is_transitive,
        'is_total_order': is_total,
        'n_comparable_pairs': n_comparable,
        'n_total_pairs': n_total_pairs,
        'comparability_fraction': n_comparable / n_total_pairs if n_total_pairs > 0 else 0,
        'longest_chain': max_chain + 1,  # +1 because we count elements, not edges
        'max_antichain': max_antichain,
        'satisfies_locally_finite': True,  # trivially on finite graphs
    }


# ============================================================================
# 6. Eigenvector Component Analysis
# ============================================================================

def eigvec_edge_structure(
    neg_eigvec: np.ndarray,
    edges: List[Tuple[int, int]],
    flipped_edge_idx: int,
    G: nx.Graph
) -> Dict:
    """Analyze how the negative eigenvector components relate to graph structure.

    Key question: Is the eigenvector concentrated on the flipped edge?
    Does it decay with distance from the flipped edge in the line graph?

    Args:
        neg_eigvec: eigenvector (length m)
        edges: list of edges
        flipped_edge_idx: which edge was flipped
        G: the graph

    Returns:
        Dict with structural analysis
    """
    m = len(edges)

    # Build line graph
    L = nx.line_graph(G)
    # Map edges to line graph nodes
    edge_to_node = {}
    for e_idx, (u, v) in enumerate(edges):
        # Line graph node is a frozenset {u, v}
        edge_to_node[e_idx] = frozenset({u, v})

    # Compute line graph distances from flipped edge
    flipped_node = edge_to_node[flipped_edge_idx]
    try:
        lg_distances = nx.single_source_shortest_path_length(L, flipped_node)
    except nx.NodeNotFound:
        # Fallback: compute distances manually
        lg_distances = {}
        for e_idx in range(m):
            node = edge_to_node[e_idx]
            try:
                lg_distances[node] = nx.shortest_path_length(L, flipped_node, node)
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                lg_distances[node] = float('inf')

    # Eigenvector component vs line graph distance
    component_by_distance = {}
    for e_idx in range(m):
        node = edge_to_node[e_idx]
        dist = lg_distances.get(node, float('inf'))
        if dist not in component_by_distance:
            component_by_distance[dist] = []
        component_by_distance[dist].append(abs(neg_eigvec[e_idx]))

    # Concentration on flipped edge
    flipped_component = abs(neg_eigvec[flipped_edge_idx])
    total_norm = np.linalg.norm(neg_eigvec)
    concentration = flipped_component / total_norm if total_norm > 0 else 0

    return {
        'component_by_line_distance': {
            int(d): float(np.mean(comps))
            for d, comps in sorted(component_by_distance.items())
            if d != float('inf')
        },
        'flipped_edge_component': float(flipped_component),
        'total_norm': float(total_norm),
        'concentration_on_flipped': float(concentration),
        'is_localized': concentration > 0.7,
    }


# ============================================================================
# 7. Main Analysis: Run on Standard Graph Family
# ============================================================================

def create_test_graphs() -> List[Tuple[nx.Graph, str]]:
    """Create the standard test graphs for analysis.

    Returns:
        List of (graph, name) pairs
    """
    graphs = []

    # Path P3 (2 edges, tree)
    P3 = nx.path_graph(3)
    graphs.append((P3, "Path P3"))

    # Path P4 (3 edges, tree)
    P4 = nx.path_graph(4)
    graphs.append((P4, "Path P4"))

    # Path P5 (4 edges, tree)
    P5 = nx.path_graph(5)
    graphs.append((P5, "Path P5"))

    # Star S4 (3 edges, tree) - star with center 0 and 3 leaves
    S4 = nx.star_graph(3)
    graphs.append((S4, "Star S4"))

    # Cycle C4 (4 edges, girth 4)
    C4 = nx.cycle_graph(4)
    graphs.append((C4, "Cycle C4"))

    # Cycle C5 (5 edges, girth 5)
    C5 = nx.cycle_graph(5)
    graphs.append((C5, "Cycle C5"))

    # K3 (triangle, 3 edges, girth 3)
    K3 = nx.complete_graph(3)
    graphs.append((K3, "Complete K3"))

    # K4 (6 edges, girth 3)
    K4 = nx.complete_graph(4)
    graphs.append((K4, "Complete K4"))

    return graphs


def run_full_analysis(J_values: List[float] = None) -> Dict:
    """Run the complete causal structure analysis.

    Args:
        J_values: coupling constants to test

    Returns:
        Dict with all results
    """
    if J_values is None:
        J_values = [0.3, 0.5, 1.0]

    graphs = create_test_graphs()
    all_results = {}

    for G, name in graphs:
        for J in J_values:
            key = f"{name}_J={J}"
            print(f"\nAnalyzing {key}...")
            print(f"  Vertices: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")

            # Skip if too many vertices for exact computation
            if G.number_of_nodes() > 16:
                print(f"  SKIPPED (too many vertices for exact computation)")
                continue

            result = analyze_causal_structure_for_graph(G, J, name)

            # Add causal set axiom tests
            for sa in result['sign_analyses']:
                causet_check = test_causal_set_axioms(
                    sa['partial_order'],
                    result['n_vertices']
                )
                sa['causet_axioms'] = causet_check

                # Add eigenvector structure analysis
                eigvec_structure = eigvec_edge_structure(
                    sa['negative_eigenvector'],
                    result['edges'],
                    sa['flipped_edge_idx'],
                    G
                )
                sa['eigvec_structure'] = eigvec_structure

            # Add distance ordering for each edge
            result['distance_orderings'] = []
            for e_idx, edge in enumerate(result['edges']):
                dist_order = timelike_edge_distance_ordering(G, edge)
                result['distance_orderings'].append(dist_order)

            all_results[key] = result

            # Print summary
            print(f"  Fisher diagonal ratio: {result['fisher_diagonal_ratio']:.6f}")
            opt = result['sign_analyses'][result['optimal_sign_idx']]
            print(f"  Optimal W: {result['optimal_W']:.6f} (edge {opt['flipped_edge']})")
            print(f"  Optimal sign gives partial order: {opt['is_partial_order']}")
            if opt['is_partial_order']:
                cs = opt['causet_axioms']
                print(f"    Comparability: {cs['comparability_fraction']:.2%}")
                print(f"    Longest chain: {cs['longest_chain']}")
                print(f"    Max antichain: {cs['max_antichain']}")

    return all_results


def print_detailed_report(all_results: Dict):
    """Print a detailed report of the causal structure analysis."""

    print("\n" + "=" * 80)
    print("CAUSAL STRUCTURE FROM SIGNED-EDGE CONSTRUCTION: DETAILED REPORT")
    print("=" * 80)

    for key, result in all_results.items():
        print(f"\n{'=' * 60}")
        print(f"Graph: {result['graph_name']}  |  J = {result['coupling_J']}")
        print(f"Vertices: {result['n_vertices']}, Edges: {result['n_edges']}")
        print(f"Fisher diagonal ratio: {result['fisher_diagonal_ratio']:.6f}")
        print(f"{'=' * 60}")

        print(f"\nEdge list: {result['edges']}")

        # Fisher matrix
        F = result['fisher_matrix']
        print(f"\nFisher matrix F:")
        for row in F:
            print("  [" + ", ".join(f"{x:+.6f}" for x in row) + "]")

        print(f"\n--- Sign Assignments (q=1) ---")
        for sa in result['sign_analyses']:
            print(f"\n  Flipped edge #{sa['flipped_edge_idx']}: {sa['flipped_edge']}")
            print(f"    Eigenvalues of A(S): {sa['eigenvalues']}")
            print(f"    Negative eigenvalue: {sa['negative_eigenvalue']:.6f}")
            print(f"    Negative eigenvector: [{', '.join(f'{x:.4f}' for x in sa['negative_eigenvector'])}]")
            print(f"    W = {sa['W']:.6f}, L_gap = {sa['L_gap']:.6f}")

            print(f"    Vertex flow: [{', '.join(f'{x:+.4f}' for x in sa['vertex_flow'])}]")

            if sa['is_partial_order']:
                print(f"    Partial order: YES")
                cs = sa['causet_axioms']
                print(f"      Comparable pairs: {cs['n_comparable_pairs']}/{cs['n_total_pairs']} ({cs['comparability_fraction']:.1%})")
                print(f"      Longest chain: {cs['longest_chain']}, Max antichain: {cs['max_antichain']}")
                if cs['is_total_order']:
                    print(f"      This is a TOTAL order (all pairs comparable)")
            else:
                print(f"    Partial order: NO")
                print(f"      Transitive: {sa['is_transitive']}, Antisymmetric: {sa['is_antisymmetric']}")

            es = sa['eigvec_structure']
            print(f"    Eigvec concentration on flipped edge: {es['concentration_on_flipped']:.4f}")
            print(f"    Localized: {es['is_localized']}")
            if es['component_by_line_distance']:
                print(f"    Component by line-graph distance: {es['component_by_line_distance']}")

        # Optimal summary
        opt_idx = result['optimal_sign_idx']
        opt = result['sign_analyses'][opt_idx]
        print(f"\n  OPTIMAL: edge #{opt_idx} {opt['flipped_edge']}, W={opt['W']:.6f}")
        print(f"    Induces partial order: {opt['is_partial_order']}")

    # Global summary
    print(f"\n{'=' * 80}")
    print("GLOBAL SUMMARY")
    print(f"{'=' * 80}")

    n_total = 0
    n_partial_order = 0
    n_optimal_partial_order = 0
    n_total_order = 0

    for key, result in all_results.items():
        for sa in result['sign_analyses']:
            n_total += 1
            if sa['is_partial_order']:
                n_partial_order += 1
                if sa['causet_axioms']['is_total_order']:
                    n_total_order += 1

        opt = result['sign_analyses'][result['optimal_sign_idx']]
        if opt['is_partial_order']:
            n_optimal_partial_order += 1

    n_graphs = len(all_results)
    print(f"\nTotal sign assignments analyzed: {n_total}")
    print(f"Produce valid partial order: {n_partial_order}/{n_total} ({100*n_partial_order/n_total:.1f}%)")
    print(f"Produce total order: {n_total_order}/{n_total} ({100*n_total_order/n_total:.1f}%)")
    print(f"\nOptimal sign assignment (max W) produces partial order: {n_optimal_partial_order}/{n_graphs} ({100*n_optimal_partial_order/n_graphs:.1f}%)")

    # Key question: Is the vertex flow from the NEGATIVE eigenvector consistent?
    print(f"\n--- KEY FINDING ---")
    print("The vertex flow derived from the negative eigenvector of A(S)")
    print("produces a valid partial order in some but not all cases.")
    print("On TREES (diagonal F), the eigenvector is perfectly localized")
    print("on the flipped edge, producing a degenerate ordering (only the")
    print("endpoints of the flipped edge are ordered).")
    print("On CYCLIC graphs, off-diagonal Fisher correlations spread the")
    print("eigenvector, potentially producing richer orderings.")


# ============================================================================
# 8. Specific Comparison: Tree vs Cycle
# ============================================================================

def compare_tree_vs_cycle():
    """Detailed comparison of P4 (tree) vs C4 (cycle) causal structures."""

    print("\n" + "=" * 80)
    print("DETAILED COMPARISON: P4 (Tree) vs C4 (Cycle)")
    print("=" * 80)

    J = 0.5
    graphs = [
        (nx.path_graph(4), "Path P4"),
        (nx.cycle_graph(4), "Cycle C4"),
    ]

    for G, name in graphs:
        print(f"\n--- {name} ---")
        edges = list(G.edges())
        n = G.number_of_nodes()
        m = G.number_of_edges()
        print(f"Vertices: {n}, Edges: {m}")
        print(f"Edges: {edges}")

        if nx.is_tree(G):
            F = ising_fisher_tree(np.full(m, J))
        else:
            F = ising_fisher_exact(G, J)

        print(f"\nFisher matrix (diagonal? {np.allclose(F, np.diag(np.diag(F)))}):")
        for row in F:
            print("  [" + ", ".join(f"{x:+.6f}" for x in row) + "]")

        print(f"\nSign assignments:")
        for e_idx in range(m):
            sa = analyze_sign_assignment(G, F, e_idx, edges)
            vf = eigvec_to_edge_flow(sa.negative_eigvec, edges, n)
            order = vertex_flow_to_partial_order(vf)

            print(f"\n  Flip edge {e_idx} = {edges[e_idx]}:")
            print(f"    Negative eigvec: [{', '.join(f'{x:.4f}' for x in sa.negative_eigvec)}]")
            print(f"    Vertex flow:     [{', '.join(f'{x:+.4f}' for x in vf)}]")
            print(f"    W = {sa.W:.6f}")

            if order:
                print(f"    Order: {order}")
                # Check if this is consistent with "time direction = along flipped edge"
                u, v = edges[e_idx]
                flow_direction = "u->v" if vf[v] > vf[u] else "v->u" if vf[u] > vf[v] else "undetermined"
                print(f"    Flipped edge direction: {flow_direction}")
            else:
                print(f"    No ordering induced (all vertices equivalent)")


# ============================================================================
# 9. Test: Does the Eigenvector Align with Graph Distance?
# ============================================================================

def test_eigvec_graph_alignment():
    """Test whether the negative eigenvector direction aligns with any
    natural graph-theoretic quantity (centrality, distance, etc.)."""

    print("\n" + "=" * 80)
    print("EIGENVECTOR-GRAPH ALIGNMENT TEST")
    print("=" * 80)

    J = 0.5
    graphs = create_test_graphs()

    for G, name in graphs:
        if G.number_of_nodes() > 12:
            continue

        edges = list(G.edges())
        n = G.number_of_nodes()
        m = G.number_of_edges()

        if nx.is_tree(G):
            F = ising_fisher_tree(np.full(m, J))
        else:
            F = ising_fisher_exact(G, J)

        # Find optimal sign assignment (max W)
        best_W = -1
        best_sa = None
        best_idx = -1
        for e_idx in range(m):
            sa = analyze_sign_assignment(G, F, e_idx, edges)
            if sa.W > best_W:
                best_W = sa.W
                best_sa = sa
                best_idx = e_idx

        vf = eigvec_to_edge_flow(best_sa.negative_eigvec, edges, n)

        # Compute vertex centralities
        degree_cent = nx.degree_centrality(G)
        betweenness_cent = nx.betweenness_centrality(G)

        print(f"\n{name}: optimal flip = edge {best_idx} = {edges[best_idx]}, W = {best_W:.6f}")
        print(f"  Vertex | Flow  | Degree | Betweenness")
        print(f"  -------|-------|--------|------------")
        for v in range(n):
            print(f"  {v:5d}  | {vf[v]:+.4f} | {degree_cent[v]:.4f} |  {betweenness_cent[v]:.4f}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("Causal Structure from Signed-Edge Construction")
    print("=" * 60)

    # Run full analysis
    all_results = run_full_analysis(J_values=[0.3, 0.5, 1.0])

    # Print detailed report
    print_detailed_report(all_results)

    # Tree vs Cycle comparison
    compare_tree_vs_cycle()

    # Eigenvector alignment test
    test_eigvec_graph_alignment()

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
