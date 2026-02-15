"""
MULTIPLE SPATIAL PATTERNS - Ollivier-Ricci Curvature Tests
===========================================================

GOAL: Estimate whether κ departs from 0 across multiple small 2D/3D spatial
hypergraph patterns.

Strategy:
- Use Pure Python (full control)
- 5 different spatial patterns
- Compute Ollivier-Ricci with POT
- Check whether non-zero curvature appears beyond a single construction

Interpretation policy:
- Results are preliminary
- Results are not a formal proof of continuum limit
"""

from datetime import date
from typing import List, Tuple

import numpy as np
import json
from pathlib import Path
from collections import defaultdict, deque
from scipy.optimize import linprog

try:
    import networkx as nx
except Exception:  # pragma: no cover - optional dependency
    nx = None

try:
    import ot  # Python Optimal Transport
except Exception:  # pragma: no cover - optional dependency
    ot = None


class SimpleGraph:
    """Minimal undirected graph fallback when NetworkX is unavailable."""

    def __init__(self):
        self.adj = defaultdict(set)
        self._edge_count = 0

    def add_nodes_from(self, nodes):
        for node in nodes:
            _ = self.adj[node]

    def add_edge(self, u, v):
        if v not in self.adj[u]:
            self.adj[u].add(v)
            self.adj[v].add(u)
            self._edge_count += 1

    def neighbors(self, node):
        return self.adj.get(node, set())

    def edges(self):
        out = []
        seen = set()
        for u, nbrs in self.adj.items():
            for v in nbrs:
                key = (u, v) if u <= v else (v, u)
                if key in seen:
                    continue
                seen.add(key)
                out.append(key)
        return out

    def number_of_nodes(self):
        return len(self.adj)

    def number_of_edges(self):
        return self._edge_count

    def shortest_path_length(self, source, target):
        if source == target:
            return 0
        queue = deque([(source, 0)])
        visited = {source}
        while queue:
            node, dist = queue.popleft()
            for nbr in self.adj.get(node, ()):
                if nbr == target:
                    return dist + 1
                if nbr in visited:
                    continue
                visited.add(nbr)
                queue.append((nbr, dist + 1))
        raise ValueError("No path between nodes")


def _new_graph():
    if nx is not None:
        return nx.Graph()
    return SimpleGraph()


def _graph_edges(G):
    return list(G.edges())


def _graph_neighbors(G, node):
    return list(G.neighbors(node))


def _graph_shortest_path_length(G, source, target):
    if nx is not None:
        return nx.shortest_path_length(G, source, target)
    return G.shortest_path_length(source, target)


def _emd2(prob_u, prob_v, dist_matrix):
    """Compute Earth Mover's Distance squared (cost) with optional POT dependency."""
    if ot is not None:
        return float(ot.emd2(prob_u, prob_v, dist_matrix))

    n, m = dist_matrix.shape
    c = dist_matrix.reshape(-1)
    a_eq = []
    b_eq = []

    # Row constraints
    for i in range(n):
        row = np.zeros(n * m)
        row[i * m : (i + 1) * m] = 1.0
        a_eq.append(row)
        b_eq.append(prob_u[i])

    # Column constraints
    for j in range(m):
        col = np.zeros(n * m)
        col[j::m] = 1.0
        a_eq.append(col)
        b_eq.append(prob_v[j])

    res = linprog(
        c,
        A_eq=np.vstack(a_eq),
        b_eq=np.array(b_eq),
        bounds=(0, None),
        method="highs",
    )
    if not res.success:
        raise RuntimeError(f"Linear program failed: {res.message}")
    return float(res.fun)

def create_2d_triangle_mesh(size=3):
    """Create 2D triangular mesh hypergraph"""
    edges = []
    # Triangle mesh: each square splits into 2 triangles
    for i in range(size):
        for j in range(size):
            # Node indices
            n1 = i * (size+1) + j
            n2 = i * (size+1) + j + 1
            n3 = (i+1) * (size+1) + j
            n4 = (i+1) * (size+1) + j + 1

            # Two triangles per square
            edges.append((n1, n2, n3))
            edges.append((n2, n4, n3))

    return edges

def create_square_grid(size=3):
    """Create square grid (4-node squares)"""
    edges = []
    for i in range(size):
        for j in range(size):
            n1 = i * (size+1) + j
            n2 = i * (size+1) + j + 1
            n3 = (i+1) * (size+1) + j
            n4 = (i+1) * (size+1) + j + 1

            # Square hyperedge (4 nodes)
            edges.append((n1, n2, n3, n4))

    return edges

def create_hexagonal_mesh(size=2):
    """Create hexagonal mesh pattern"""
    edges = []
    for i in range(size):
        for j in range(size):
            center = i * size * 3 + j * 3
            # Hexagon around center
            for k in range(6):
                n1 = center + k
                n2 = center + (k+1) % 6
                n3 = center
                edges.append((n1, n2, n3))

    return edges

def create_tetrahedral_3d(size=2):
    """Create 3D tetrahedral mesh"""
    edges = []
    for i in range(size):
        for j in range(size):
            for k in range(size):
                # Base index
                base = i * size * size + j * size + k
                # Tetrahedron (4 vertices)
                n1 = base
                n2 = base + 1
                n3 = base + size
                n4 = base + size * size
                edges.append((n1, n2, n3, n4))

    return edges

def hypergraph_to_causal_graph(hyperedges):
    """Convert hypergraph to causal graph for curvature testing"""
    G = _new_graph()

    # Add all nodes
    nodes = set()
    for edge in hyperedges:
        nodes.update(edge)
    G.add_nodes_from(nodes)

    # Add edges: connect all nodes within each hyperedge
    for hedge in hyperedges:
        hedge_list = list(hedge)
        for i in range(len(hedge_list)):
            for j in range(i+1, len(hedge_list)):
                G.add_edge(hedge_list[i], hedge_list[j])

    return G

def compute_ollivier_ricci_curvature(G, sample_size=50, alpha=0.5):
    """
    Compute Ollivier-Ricci curvature for graph edges

    κ(x,y) = 1 - W(μ_x, μ_y) / d(x,y)
    where W = Wasserstein distance, μ = random walk measure
    """

    if G.number_of_nodes() < 3:
        return []

    edges = _graph_edges(G)
    if len(edges) == 0:
        return []

    # Sample edges if too many
    if len(edges) > sample_size:
        import random
        random.seed(42)
        edges = random.sample(edges, sample_size)

    curvatures = []

    for u, v in edges:
        try:
            # Get neighborhoods
            neighbors_u = _graph_neighbors(G, u) + [u]
            neighbors_v = _graph_neighbors(G, v) + [v]

            if len(neighbors_u) < 2 or len(neighbors_v) < 2:
                continue

            # Create probability distributions (uniform random walk)
            # For simplicity: uniform on neighbors
            p_u = np.ones(len(neighbors_u)) / len(neighbors_u)
            p_v = np.ones(len(neighbors_v)) / len(neighbors_v)

            # Distance matrix between neighborhoods
            # Use graph shortest paths
            dist_matrix = np.zeros((len(neighbors_u), len(neighbors_v)))

            for i, nu in enumerate(neighbors_u):
                for j, nv in enumerate(neighbors_v):
                    try:
                        dist_matrix[i, j] = _graph_shortest_path_length(G, nu, nv)
                    except:
                        dist_matrix[i, j] = 100  # Disconnected

            # Compute Wasserstein distance
            W_dist = _emd2(p_u, p_v, dist_matrix)

            # Graph distance d(u,v) = 1 (edge)
            d_uv = 1

            # Curvature: κ = 1 - W/d
            kappa = 1 - W_dist / d_uv

            curvatures.append(kappa)

        except Exception as e:
            # Skip problematic edges
            continue

    return curvatures

def test_spatial_pattern(pattern_name, create_func, size):
    """Test Ollivier-Ricci on one spatial pattern"""

    print(f"Testing: {pattern_name} (size={size})")
    print("-" * 60)

    try:
        # Create hypergraph
        hyperedges = create_func(size)
        print(f"  Hyperedges: {len(hyperedges)}")

        # Convert to graph
        G = hypergraph_to_causal_graph(hyperedges)
        print(f"  Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

        # Compute curvatures
        curvatures = compute_ollivier_ricci_curvature(G, sample_size=100)

        if len(curvatures) == 0:
            print(f"  ✗ No curvatures computed")
            return None

        kappa_mean = np.mean(curvatures)
        kappa_median = np.median(curvatures)
        kappa_std = np.std(curvatures)
        nonzero_frac = np.sum(np.array(curvatures) != 0) / len(curvatures)

        print(f"  Curvatures computed: {len(curvatures)}")
        print(f"  Mean κ:   {kappa_mean:.4f}")
        print(f"  Median κ: {kappa_median:.4f}")
        print(f"  Std κ:    {kappa_std:.4f}")
        print(f"  Non-zero: {nonzero_frac*100:.1f}%")
        print()

        # Assessment
        if kappa_mean > 0.1:
            print(f"  ✓✓ SIGNIFICANT CURVATURE (κ={kappa_mean:.3f})")
            status = "significant"
        elif kappa_mean > 0.01:
            print(f"  ✓ MODERATE CURVATURE (κ={kappa_mean:.3f})")
            status = "moderate"
        else:
            print(f"  ~ WEAK CURVATURE (κ={kappa_mean:.3f})")
            status = "weak"

        print()

        return {
            'pattern': pattern_name,
            'size': size,
            'hyperedges': len(hyperedges),
            'nodes': G.number_of_nodes(),
            'graph_edges': G.number_of_edges(),
            'curvatures_computed': len(curvatures),
            'mean_kappa': float(kappa_mean),
            'median_kappa': float(kappa_median),
            'std_kappa': float(kappa_std),
            'nonzero_frac': float(nonzero_frac),
            'status': status
        }

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None

def main():
    print("=" * 80)
    print(" MULTIPLE SPATIAL PATTERNS - Ollivier-Ricci Curvature")
    print(" Verifying κ≠0 robustness across different 2D/3D structures")
    print("=" * 80)
    print()

    results = []

    # Test 1: Triangle mesh (2D)
    r1 = test_spatial_pattern("Triangle Mesh 2D", create_2d_triangle_mesh, size=3)
    if r1: results.append(r1)

    # Test 2: Square grid
    r2 = test_spatial_pattern("Square Grid 2D", create_square_grid, size=3)
    if r2: results.append(r2)

    # Test 3: Hexagonal
    r3 = test_spatial_pattern("Hexagonal Mesh", create_hexagonal_mesh, size=2)
    if r3: results.append(r3)

    # Test 4: Triangle larger
    r4 = test_spatial_pattern("Triangle Mesh 2D (large)", create_2d_triangle_mesh, size=4)
    if r4: results.append(r4)

    # Test 5: Tetrahedral 3D
    r5 = test_spatial_pattern("Tetrahedral 3D", create_tetrahedral_3d, size=2)
    if r5: results.append(r5)

    # SUMMARY
    print("=" * 80)
    print(" SUMMARY ACROSS ALL PATTERNS")
    print("=" * 80)
    print()

    if len(results) == 0:
        print("✗ No successful tests")
        return

    # Aggregate statistics
    all_kappas = [r['mean_kappa'] for r in results]
    overall_mean = np.mean(all_kappas)
    overall_std = np.std(all_kappas)

    significant = [r for r in results if r['status'] == 'significant']
    moderate = [r for r in results if r['status'] == 'moderate']

    print(f"Patterns tested: {len(results)}")
    print(f"Significant (κ>0.1): {len(significant)}")
    print(f"Moderate (κ>0.01): {len(moderate)}")
    print()

    print(f"Overall statistics:")
    print(f"  Mean κ across all patterns: {overall_mean:.4f}")
    print(f"  Std κ across patterns: {overall_std:.4f}")
    print(f"  Range: [{min(all_kappas):.4f}, {max(all_kappas):.4f}]")
    print()

    # Compare with Wolfram result
    wolfram_kappa = 0.67
    print(f"Comparison with Wolfram SetReplace result:")
    print(f"  Wolfram (triangle completion): κ=0.67")
    print(f"  Python (average across patterns): κ={overall_mean:.4f}")

    if abs(overall_mean - wolfram_kappa) < 0.2:
        print(f"  ~ Numerically close on this small-scale comparison")
    else:
        print(f"  ~ Different scales/rules/methods (expected)")
    print()

    # Assessment
    if len(significant) >= 3:
        print("VERDICT: PRELIMINARY SUPPORT (strong within tested set)")
        print("  Non-zero curvature appears across multiple 2D/3D patterns")
        print("  Continuum-limit proof remains open")
        assessment = "preliminary_support_strong"
    elif len(significant) >= 1:
        print("VERDICT: PRELIMINARY SUPPORT (limited)")
        print("  Non-zero curvature appears on a subset of patterns")
        print("  Continuum-limit proof remains open")
        assessment = "preliminary_support_limited"
    else:
        print("VERDICT: INCONCLUSIVE")
        print("  Weak/near-zero curvature dominates tested patterns")
        print("  Continuum-limit proof remains open")
        assessment = "inconclusive"

    print()

    # Save
    output_file = Path(__file__).resolve().parents[1] / "output" / "multiple_spatial_curvature_results.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open('w') as f:
        json.dump({
            'test_date': date.today().isoformat(),
            'method': 'Pure Python + POT (Ollivier-Ricci)',
            'patterns_tested': len(results),
            'overall_mean_kappa': float(overall_mean),
            'overall_std_kappa': float(overall_std),
            'significant_count': len(significant),
            'assessment': assessment,
            'comparison_wolfram': {
                'wolfram_kappa': 0.67,
                'python_mean': float(overall_mean),
                'consistent': bool(abs(overall_mean - 0.67) < 0.2)
            },
            'results': results
        }, f, indent=2)

    print(f"✓ Results saved: {output_file}")
    print()

    return results, assessment

if __name__ == "__main__":
    print()
    print("NOTE: This supplements manuscript Section 2.2 with additional")
    print("      small-scale curvature checks across several spatial patterns.")
    print("      Interpretation is preliminary and non-theorem-level.")
    print()

    out = main()
    if out is None:
        raise SystemExit(1)
    results, assessment = out

    print("=" * 80)
    print(" FINAL VERDICT")
    print("=" * 80)
    print()
    print("Wolfram SetReplace reference: κ=0.67 (triangle completion)")
    print(f"Python POT/fallback LP (this test): κ={np.mean([r['mean_kappa'] for r in results]):.4f} (multiple patterns)")
    print()
    print("Combined interpretation: preliminary evidence for non-trivial")
    print("discrete curvature on tested spatial constructions.")
    print("Continuum-limit proof remains an open problem.")
    print()
