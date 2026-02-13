"""
Ollivier-Ricci Curvature for Hypergraphs
Tests continual limit: κ ≠ 0 means discrete geometry → Riemannian
"""

import numpy as np
import networkx as nx
from scipy.spatial.distance import cdist
import ot  # Python Optimal Transport

def compute_ollivier_ricci_hypergraph(causal_graph: nx.DiGraph, alpha: float = 0.5) -> Dict[Tuple, float]:
    """
    Compute Ollivier-Ricci curvature for edges in causal graph

    κ(x,y) = 1 - W(μ_x, μ_y) / d(x,y)
    where W = Wasserstein distance, μ_x = probability measure at x

    Returns: {(x,y): curvature_value}
    """
    curvatures = {}

    # For each edge in causal graph
    for x, y in causal_graph.edges():
        # Define probability measures at x and y
        # μ_x: (1-α) at x, α distributed among neighbors
        neighbors_x = set(causal_graph.successors(x)) | set(causal_graph.predecessors(x))
        neighbors_y = set(causal_graph.successors(y)) | set(causal_graph.predecessors(y))

        if not neighbors_x or not neighbors_y:
            continue

        # Build distributions
        all_nodes = neighbors_x | neighbors_y | {x, y}
        node_list = sorted(all_nodes, key=str)  # Stable ordering
        n = len(node_list)
        node_to_idx = {node: i for i, node in enumerate(node_list)}

        mu_x = np.zeros(n)
        mu_y = np.zeros(n)

        # Distribution at x
        mu_x[node_to_idx[x]] = 1 - alpha
        if neighbors_x:
            for neighbor in neighbors_x:
                if neighbor in node_to_idx:
                    mu_x[node_to_idx[neighbor]] = alpha / len(neighbors_x)

        # Distribution at y
        mu_y[node_to_idx[y]] = 1 - alpha
        if neighbors_y:
            for neighbor in neighbors_y:
                if neighbor in node_to_idx:
                    mu_y[node_to_idx[neighbor]] = alpha / len(neighbors_y)

        # Normalize
        mu_x /= mu_x.sum() if mu_x.sum() > 0 else 1
        mu_y /= mu_y.sum() if mu_y.sum() > 0 else 1

        # Distance matrix (graph distance)
        dist_matrix = np.zeros((n, n))
        for i, node_i in enumerate(node_list):
            for j, node_j in enumerate(node_list):
                try:
                    if node_i == node_j:
                        dist_matrix[i, j] = 0
                    elif causal_graph.has_edge(node_i, node_j):
                        dist_matrix[i, j] = 1
                    else:
                        # Shortest path in undirected version
                        undirected = causal_graph.to_undirected()
                        if nx.has_path(undirected, node_i, node_j):
                            dist_matrix[i, j] = nx.shortest_path_length(undirected, node_i, node_j)
                        else:
                            dist_matrix[i, j] = 100  # Disconnected
                except:
                    dist_matrix[i, j] = 100

        # Wasserstein distance via POT
        try:
            wasserstein = ot.emd2(mu_x, mu_y, dist_matrix)
            d_xy = 1  # Edge distance

            kappa = 1 - wasserstein / d_xy
            curvatures[(x, y)] = kappa
        except:
            curvatures[(x, y)] = np.nan

    return curvatures


def analyze_curvature_statistics(curvatures: Dict[Tuple, float]) -> Dict:
    """Analyze curvature distribution"""
    valid = [k for k in curvatures.values() if not np.isnan(k)]

    if not valid:
        return {'mean': np.nan, 'std': np.nan, 'nonzero_fraction': 0, 'n': 0}

    return {
        'mean': np.mean(valid),
        'std': np.std(valid),
        'median': np.median(valid),
        'nonzero_fraction': np.mean([abs(k) > 1e-6 for k in valid]),
        'n': len(valid),
        'values': valid
    }


def test_ricci_on_string_systems():
    """Test that string rewriting gives κ=0 (1D, expected flat)"""
    from hypergraph_engine import HypergraphEngine

    # Simple string substitution (1D)
    rules = [
        ((1, 2), [(3, 1), (2, 3)])
    ]

    engine = HypergraphEngine(rules)
    initial = [(1, 2), (2, 3)]

    states = engine.evolve_multiway(initial, steps=4, max_states=200)
    causal_graph = engine.compute_causal_graph(states)

    curvatures = compute_ollivier_ricci_hypergraph(causal_graph, alpha=0.5)
    stats = analyze_curvature_statistics(curvatures)

    print(f"String system (1D, expect κ≈0):")
    print(f"  Mean κ: {stats['mean']:.6f}")
    print(f"  Std: {stats['std']:.6f}")
    print(f"  Non-zero: {stats['nonzero_fraction']:.1%}")

    return stats


if __name__ == "__main__":
    test_ricci_on_string_systems()
