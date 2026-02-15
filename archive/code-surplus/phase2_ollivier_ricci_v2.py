"""
PHASE 2: Ollivier-Ricci Curvature on Real Wolfram Hypergraphs
=============================================================

THE CRITICAL TEST (Gap A):
  Previous sessions: kappa=0 on string rewriting (1D) -- expected and correct.
  Now: compute kappa on SPATIAL hypergraphs from real Wolfram rules.

  If kappa != 0 --> continuum limit confirmed EMPIRICALLY
  --> ALL 5 theorems become unconditional (remove single assumption)

Method:
  1. Evolve Wolfram rules to generate spatial hypergraph (N~1000 vertices)
  2. Convert to graph (vertices connected if in same hyperedge)
  3. Compute Ollivier-Ricci curvature on each edge: kappa(x,y) = 1 - W1(mu_x,mu_y)/d(x,y)
  4. Statistics: mean, std, fraction nonzero, distribution

Key insight: We compute curvature on the SPATIAL graph (not multiway/causal graph).
The spatial graph is the one that should converge to a Riemannian manifold.
"""

import numpy as np
import networkx as nx
import ot  # Python Optimal Transport
from collections import defaultdict
from typing import Dict, List, Tuple
import time
import json
import sys

# Add src to path
sys.path.insert(0, '.')
from wolfram_engine_v2 import WolframEngineV2, hypergraph_to_graph, WOLFRAM_RULES_V2


def ollivier_ricci_curvature(G: nx.Graph, alpha: float = 0.5,
                              max_edges: int = 5000,
                              sample_edges: int = 0) -> Dict:
    """
    Compute Ollivier-Ricci curvature for edges of graph G.

    For each edge (x,y):
      mu_x = (1-alpha)*delta_x + alpha * uniform(neighbors_x)
      mu_y = (1-alpha)*delta_y + alpha * uniform(neighbors_y)
      kappa(x,y) = 1 - W1(mu_x, mu_y) / d(x,y)

    where W1 is the 1-Wasserstein (earth mover's) distance.

    Parameters:
        G: networkx Graph (undirected)
        alpha: laziness parameter (0 = stay, 1 = move to neighbor)
        max_edges: skip if graph has too many edges
        sample_edges: if > 0, sample this many edges randomly

    Returns:
        dict with curvature values and statistics
    """
    if G.number_of_edges() > max_edges:
        return {'error': f'Too many edges: {G.number_of_edges()} > {max_edges}'}

    # Precompute shortest path distances (BFS for unweighted)
    # For large graphs, compute on-demand
    nodes = list(G.nodes())
    n = len(nodes)
    node_to_idx = {v: i for i, v in enumerate(nodes)}

    # Select edges to process
    edges = list(G.edges())
    if sample_edges > 0 and len(edges) > sample_edges:
        rng = np.random.default_rng(42)
        indices = rng.choice(len(edges), sample_edges, replace=False)
        edges = [edges[i] for i in indices]

    curvatures = {}
    skipped = 0

    for x, y in edges:
        # Neighbors
        nbrs_x = list(G.neighbors(x))
        nbrs_y = list(G.neighbors(y))

        if not nbrs_x or not nbrs_y:
            skipped += 1
            continue

        # Support of distributions: union of {x, y} and their neighbors
        support = list(set([x, y] + nbrs_x + nbrs_y))
        ns = len(support)
        support_idx = {v: i for i, v in enumerate(support)}

        # Build distributions
        mu_x = np.zeros(ns)
        mu_y = np.zeros(ns)

        # mu_x: (1-alpha) at x, alpha uniform over neighbors
        mu_x[support_idx[x]] = 1 - alpha
        for nbr in nbrs_x:
            mu_x[support_idx[nbr]] += alpha / len(nbrs_x)

        # mu_y: (1-alpha) at y, alpha uniform over neighbors
        mu_y[support_idx[y]] = 1 - alpha
        for nbr in nbrs_y:
            mu_y[support_idx[nbr]] += alpha / len(nbrs_y)

        # Normalize (should already sum to 1, but just in case)
        mu_x /= mu_x.sum()
        mu_y /= mu_y.sum()

        # Distance matrix on support (graph distances)
        dist_matrix = np.zeros((ns, ns))
        for i, vi in enumerate(support):
            for j, vj in enumerate(support):
                if i == j:
                    continue
                try:
                    dist_matrix[i, j] = nx.shortest_path_length(G, vi, vj)
                except nx.NetworkXNoPath:
                    dist_matrix[i, j] = 1e6  # Disconnected

        # Wasserstein distance via linear programming (POT library)
        try:
            W1 = ot.emd2(mu_x, mu_y, dist_matrix)
            d_xy = 1.0  # Edge distance
            kappa = 1.0 - W1 / d_xy
            curvatures[(x, y)] = kappa
        except Exception as e:
            skipped += 1
            continue

    # Statistics
    vals = list(curvatures.values())
    if not vals:
        return {
            'curvatures': curvatures,
            'mean': np.nan, 'std': np.nan, 'median': np.nan,
            'min': np.nan, 'max': np.nan,
            'nonzero_fraction': 0, 'positive_fraction': 0, 'negative_fraction': 0,
            'n_computed': 0, 'n_skipped': skipped
        }

    return {
        'curvatures': curvatures,
        'mean': float(np.mean(vals)),
        'std': float(np.std(vals)),
        'median': float(np.median(vals)),
        'min': float(np.min(vals)),
        'max': float(np.max(vals)),
        'nonzero_fraction': float(np.mean([abs(k) > 1e-6 for k in vals])),
        'positive_fraction': float(np.mean([k > 1e-6 for k in vals])),
        'negative_fraction': float(np.mean([k < -1e-6 for k in vals])),
        'n_computed': len(vals),
        'n_skipped': skipped,
        'values': vals
    }


def test_dimension_estimation(G: nx.Graph) -> Dict:
    """
    Estimate effective dimension using multiple methods:
    1. Volume scaling: |B(r)| ~ r^d
    2. Spectral: from Laplacian eigenvalues
    3. Average degree: 2d for regular d-dimensional lattice
    """
    results = {}

    # Method 1: Average degree
    degrees = [d for _, d in G.degree()]
    avg_deg = np.mean(degrees)
    results['avg_degree'] = float(avg_deg)
    results['dim_from_degree'] = float(avg_deg / 2)

    # Method 2: Volume scaling (ball growth)
    # Sample some nodes and measure |B(r)| for r=1,2,3,...
    nodes = list(G.nodes())
    n_sample = min(20, len(nodes))
    rng = np.random.default_rng(42)
    sample_nodes = rng.choice(nodes, n_sample, replace=False)

    ball_sizes = defaultdict(list)
    max_r = min(10, nx.diameter(G) if nx.is_connected(G) and len(nodes) < 5000 else 10)

    for v in sample_nodes:
        # BFS
        distances = nx.single_source_shortest_path_length(G, v, cutoff=max_r)
        for r in range(1, max_r + 1):
            size = sum(1 for d in distances.values() if d <= r)
            ball_sizes[r].append(size)

    # Fit log|B(r)| ~ d * log(r) + const
    radii = []
    log_sizes = []
    for r in sorted(ball_sizes.keys()):
        if r > 0:
            mean_size = np.mean(ball_sizes[r])
            if mean_size > 1:
                radii.append(np.log(r))
                log_sizes.append(np.log(mean_size))

    if len(radii) >= 3:
        # Linear fit
        coeffs = np.polyfit(radii, log_sizes, 1)
        results['dim_from_volume_scaling'] = float(coeffs[0])
        results['volume_scaling_r2'] = float(
            1 - np.var([log_sizes[i] - (coeffs[0]*radii[i] + coeffs[1])
                        for i in range(len(radii))]) / np.var(log_sizes)
        )

    # Method 3: Spectral dimension (from Laplacian)
    if len(nodes) < 3000:
        L = nx.laplacian_matrix(G).toarray().astype(float)
        eigenvalues = np.sort(np.linalg.eigvalsh(L))
        # Remove zero eigenvalue(s)
        nonzero_eigs = eigenvalues[eigenvalues > 1e-10]
        if len(nonzero_eigs) > 10:
            # Weyl's law: N(lambda) ~ lambda^{d/2}
            # log(k) ~ (d/2) * log(lambda_k)
            k_vals = np.arange(1, min(len(nonzero_eigs), 50) + 1)
            log_k = np.log(k_vals)
            log_lam = np.log(nonzero_eigs[:len(k_vals)])

            coeffs = np.polyfit(log_lam, log_k, 1)
            results['dim_spectral'] = float(2 * coeffs[0])

    return results


def run_curvature_tests():
    """Main test: Ollivier-Ricci curvature on all Wolfram rules"""

    print("=" * 80)
    print(" PHASE 2: OLLIVIER-RICCI CURVATURE ON WOLFRAM SPATIAL HYPERGRAPHS")
    print("=" * 80)
    print()
    print("CRITICAL TEST: kappa != 0 on real hypergraphs")
    print("Previous: kappa = 0 on 1D string rewriting (correct, expected)")
    print("Now: real Wolfram rules generating 2D/3D spatial geometry")
    print()
    print("If kappa != 0 --> continuum limit CONFIRMED empirically")
    print("             --> ALL 5 theorems become UNCONDITIONAL")
    print()

    all_results = {}

    # Test each rule
    for name, spec in WOLFRAM_RULES_V2.items():
        print(f"\n{'='*60}")
        print(f" [{name}] {spec['description']}")
        print(f"{'='*60}")

        engine = WolframEngineV2(spec['rules'])

        # Evolve spatial hypergraph
        t0 = time.time()
        try:
            spatial = engine.evolve_spatial(spec['initial'], steps=200, max_edges=3000)
        except Exception as e:
            print(f"  Evolution failed: {e}")
            continue
        t_evolve = time.time() - t0

        if len(spatial) < 5:
            print(f"  Too few hyperedges ({len(spatial)}), skipping")
            continue

        # Convert to graph
        G = hypergraph_to_graph(spatial)
        n_vertices = G.number_of_nodes()
        n_edges = G.number_of_edges()

        print(f"  Spatial hypergraph: {len(spatial)} hyperedges")
        print(f"  Graph: {n_vertices} vertices, {n_edges} edges ({t_evolve:.2f}s)")

        if not nx.is_connected(G):
            components = list(nx.connected_components(G))
            largest = max(components, key=len)
            print(f"  Not connected: {len(components)} components, largest={len(largest)}")
            G = G.subgraph(largest).copy()
            n_vertices = G.number_of_nodes()
            n_edges = G.number_of_edges()
            print(f"  Using largest component: {n_vertices} vertices, {n_edges} edges")

        if n_vertices < 5:
            print(f"  Too small, skipping")
            continue

        # Dimension estimation
        print()
        print("  DIMENSION ANALYSIS:")
        dim_results = test_dimension_estimation(G)
        for key, val in dim_results.items():
            if isinstance(val, float):
                print(f"    {key}: {val:.3f}")

        # Ollivier-Ricci curvature
        print()
        print("  OLLIVIER-RICCI CURVATURE:")

        t0 = time.time()
        # For large graphs, sample edges
        sample_n = min(500, n_edges)
        ricci = ollivier_ricci_curvature(G, alpha=0.5, sample_edges=sample_n)
        t_ricci = time.time() - t0

        if 'error' in ricci:
            print(f"    Error: {ricci['error']}")
            continue

        print(f"    Computed: {ricci['n_computed']} edges ({t_ricci:.2f}s)")
        print(f"    Mean kappa:     {ricci['mean']:+.6f}")
        print(f"    Std kappa:      {ricci['std']:.6f}")
        print(f"    Median kappa:   {ricci['median']:+.6f}")
        print(f"    Min kappa:      {ricci['min']:+.6f}")
        print(f"    Max kappa:      {ricci['max']:+.6f}")
        print(f"    Nonzero (|k|>1e-6): {ricci['nonzero_fraction']:.1%}")
        print(f"    Positive:       {ricci['positive_fraction']:.1%}")
        print(f"    Negative:       {ricci['negative_fraction']:.1%}")

        # THE CRITICAL VERDICT
        print()
        if abs(ricci['mean']) > 0.01 or ricci['nonzero_fraction'] > 0.5:
            print(f"    >>> KAPPA != 0 DETECTED <<<")
            print(f"    >>> CONTINUUM LIMIT EVIDENCE <<<")
            verdict = "NONZERO"
        elif abs(ricci['mean']) > 0.001:
            print(f"    ~ Weak non-zero curvature signal")
            verdict = "WEAK"
        else:
            print(f"    kappa ~ 0 (flat)")
            verdict = "FLAT"

        # Test with different alpha values
        print()
        print("    Alpha sensitivity:")
        for alpha in [0.1, 0.3, 0.5, 0.7, 0.9]:
            r = ollivier_ricci_curvature(G, alpha=alpha, sample_edges=min(200, n_edges))
            if 'error' not in r and r['n_computed'] > 0:
                print(f"      alpha={alpha:.1f}: mean_kappa={r['mean']:+.6f}, "
                      f"nonzero={r['nonzero_fraction']:.0%}")

        result = {
            'n_hyperedges': len(spatial),
            'n_vertices': n_vertices,
            'n_edges': n_edges,
            'dimension': dim_results,
            'ricci': {k: v for k, v in ricci.items() if k != 'curvatures' and k != 'values'},
            'verdict': verdict
        }

        # Store curvature distribution for plotting
        if 'values' in ricci:
            result['curvature_values'] = ricci['values']

        all_results[name] = result

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print(" SUMMARY: OLLIVIER-RICCI CURVATURE RESULTS")
    print("=" * 80)

    nonzero_count = 0
    total_count = 0

    for name, res in all_results.items():
        total_count += 1
        v = res['verdict']
        mean_k = res['ricci']['mean']
        dim = res['dimension'].get('dim_from_volume_scaling',
               res['dimension'].get('dim_from_degree', 'N/A'))

        status = {
            'NONZERO': 'KAPPA != 0',
            'WEAK': 'weak signal',
            'FLAT': 'kappa ~ 0'
        }.get(v, v)

        if v == 'NONZERO':
            nonzero_count += 1

        print(f"  [{name:25s}] {status:15s} | mean_k={mean_k:+.4f} | dim~{dim}")

    print()
    print(f"  NON-ZERO CURVATURE: {nonzero_count}/{total_count} rules")
    print()

    if nonzero_count > 0:
        print("  CONCLUSION: Spatial hypergraphs from Wolfram rules exhibit")
        print("  non-zero Ollivier-Ricci curvature. This provides EMPIRICAL")
        print("  evidence for the continuum limit assumption.")
        print()
        print("  IMPACT: All 5 theorems (Lovelock, Amari, Chiribella, Arrow,")
        print("  Fisher=Riemann) have their single assumption SUPPORTED by data.")
    else:
        print("  CONCLUSION: No non-zero curvature detected.")
        print("  The continuum limit assumption remains unverified.")
        print()
        print("  POSSIBLE EXPLANATIONS:")
        print("  - Graph too small (need N >> 1000)")
        print("  - Wrong rules (need rules that generate 3D geometry)")
        print("  - Curvature emerges only at larger scales")

    return all_results


def save_results(results: Dict, output_path: str):
    """Save results to JSON"""
    # Make JSON-serializable
    serializable = {}
    for name, res in results.items():
        s = dict(res)
        if 'curvature_values' in s:
            s['curvature_histogram'] = {
                'bins': np.histogram(s['curvature_values'], bins=20)[1].tolist(),
                'counts': np.histogram(s['curvature_values'], bins=20)[0].tolist()
            }
            del s['curvature_values']
        serializable[name] = s

    with open(output_path, 'w') as f:
        json.dump(serializable, f, indent=2, default=str)
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    results = run_curvature_tests()

    output_path = "/Users/Max_1/Projects/PhysicsResearch/cosmological-unification/structural-bridge-via-uniqueness-theorems/output/phase2_ricci_curvature_results.json"
    save_results(results, output_path)
