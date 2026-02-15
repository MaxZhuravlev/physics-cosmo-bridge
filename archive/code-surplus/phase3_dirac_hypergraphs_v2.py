"""
PHASE 3: Dirac Structure on Wolfram Hypergraphs (Gap B)
=======================================================

THE SECOND CRITICAL TEST:
  M+M- ~ alpha*M^2 on real Wolfram hypergraphs

Previous results:
  - Descendants orientation: works on toy models (1-15% error) but DEGENERATE on hypergraphs
  - Edge count, lexicographic, entropy: all degenerate
  - Key problem: finite multiway systems have monotonic structural measures

NEW APPROACH in this session:
  We use VERTEX POSITION SIGNATURE as orientation.

  In a Wolfram rule {{1,2,3},{2,4,5}} -> {{5,6,1},{6,4,2},{4,5,3}},
  each rule application changes the local topology.
  We track HOW the topology changes:

  Orientation 1: "Expansion signature"
     For each state s -> s', compute:
     - Number of NEW vertices introduced
     - Ratio of new_vertices / shared_vertices
     E+ = creates more new vertices than median
     E- = creates fewer

  Orientation 2: "Connectivity change"
     E+ = average degree increases in transition neighborhood
     E- = average degree decreases

  Orientation 3: "Spectral gap change" (coarse)
     E+ = algebraic connectivity increases
     E- = algebraic connectivity decreases

  The key insight: spinor structure requires GEOMETRIC orientation,
  not just combinatorial counting.
"""

import numpy as np
import networkx as nx
from collections import defaultdict
from typing import Dict, List, Tuple, Set
import time
import json
import sys

sys.path.insert(0, '.')
from wolfram_engine_v2 import WolframEngineV2, hypergraph_to_graph, WOLFRAM_RULES_V2


def compute_state_features(state: Tuple, states_meta: Dict) -> Dict:
    """
    Compute geometric features of a multiway state.
    The state is a tuple of hyperedges.
    """
    hyperedges = list(state)
    if not hyperedges:
        return {}

    # Basic counts
    n_edges = len(hyperedges)
    vertices = set()
    for e in hyperedges:
        vertices.update(e)
    n_vertices = len(vertices)

    # Build graph
    G = hypergraph_to_graph(hyperedges)

    features = {
        'n_edges': n_edges,
        'n_vertices': n_vertices,
        'edge_vertex_ratio': n_edges / max(n_vertices, 1),
    }

    if G.number_of_nodes() > 1 and G.number_of_edges() > 0:
        degrees = [d for _, d in G.degree()]
        features['avg_degree'] = np.mean(degrees)
        features['max_degree'] = max(degrees)
        features['degree_variance'] = np.var(degrees)

        if nx.is_connected(G) and G.number_of_nodes() > 2:
            features['diameter'] = nx.diameter(G)
            # Algebraic connectivity (Fiedler value)
            try:
                L = nx.laplacian_matrix(G).toarray().astype(float)
                eigs = np.sort(np.linalg.eigvalsh(L))
                features['algebraic_connectivity'] = float(eigs[1]) if len(eigs) > 1 else 0
            except:
                pass
    else:
        features['avg_degree'] = 0

    return features


def compute_dirac_geometric_orientation(states: Dict, causal_graph: nx.DiGraph) -> List[Dict]:
    """
    Compute Dirac operators using GEOMETRIC orientation.

    Multiple orientation strategies tested:
    1. Vertex count change (expansion/contraction in vertex space)
    2. Edge density change
    3. Average degree change
    4. Combined geometric signature

    For each orientation, test M+M- ~ alpha*M^2
    """
    state_list = sorted(states.keys(), key=lambda s: (states[s]['depth'], str(s)))
    max_depth = max(states[s]['depth'] for s in states)

    # Precompute features for all states
    print("    Computing state features...")
    features = {}
    for s in state_list:
        features[s] = compute_state_features(s, states)

    # Define orientation functions
    def orient_vertex_count(s, s_next):
        """E+ if more vertices, E- if fewer"""
        n_s = features[s].get('n_vertices', 0)
        n_sn = features[s_next].get('n_vertices', 0)
        return +1 if n_sn > n_s else (-1 if n_sn < n_s else 0)

    def orient_avg_degree(s, s_next):
        """E+ if avg degree increases, E- if decreases"""
        d_s = features[s].get('avg_degree', 0)
        d_sn = features[s_next].get('avg_degree', 0)
        return +1 if d_sn > d_s + 0.01 else (-1 if d_sn < d_s - 0.01 else 0)

    def orient_edge_density(s, s_next):
        """E+ if edge/vertex ratio increases"""
        r_s = features[s].get('edge_vertex_ratio', 0)
        r_sn = features[s_next].get('edge_vertex_ratio', 0)
        return +1 if r_sn > r_s + 0.01 else (-1 if r_sn < r_s - 0.01 else 0)

    def orient_degree_variance(s, s_next):
        """E+ if degree heterogeneity increases"""
        v_s = features[s].get('degree_variance', 0)
        v_sn = features[s_next].get('degree_variance', 0)
        return +1 if v_sn > v_s + 0.01 else (-1 if v_sn < v_s - 0.01 else 0)

    orientations = {
        'vertex_count': orient_vertex_count,
        'avg_degree': orient_avg_degree,
        'edge_density': orient_edge_density,
        'degree_variance': orient_degree_variance,
    }

    all_results = {}

    for orient_name, orient_fn in orientations.items():
        results_per_depth = []

        for d in range(min(max_depth, 8)):
            states_d = [s for s in state_list if states[s]['depth'] == d]
            states_d1 = [s for s in state_list if states[s]['depth'] == d + 1]

            if len(states_d) < 2 or len(states_d1) < 2:
                continue

            n_d = len(states_d)
            n_d1 = len(states_d1)

            M = np.zeros((n_d1, n_d))
            M_plus = np.zeros((n_d1, n_d))
            M_minus = np.zeros((n_d1, n_d))

            idx_d = {s: i for i, s in enumerate(states_d)}
            idx_d1 = {s: i for i, s in enumerate(states_d1)}

            n_plus = 0
            n_minus = 0
            n_neutral = 0

            for s in states_d:
                for s_next in states[s]['children']:
                    if s_next in idx_d1:
                        i = idx_d[s]
                        j = idx_d1[s_next]

                        M[j, i] = 1

                        orient = orient_fn(s, s_next)
                        if orient > 0:
                            M_plus[j, i] = 1
                            n_plus += 1
                        elif orient < 0:
                            M_minus[j, i] = 1
                            n_minus += 1
                        else:
                            n_neutral += 1

            total = n_plus + n_minus + n_neutral
            if total == 0:
                continue

            # Check degeneracy
            degenerate = (n_plus == 0) or (n_minus == 0)

            # Compute M+M- vs alpha*M^2
            if M.sum() > 0 and not degenerate:
                MM = M.T @ M
                MpMm = M_minus.T @ M_plus

                norm_MM = np.linalg.norm(MM)
                if norm_MM > 1e-10:
                    alpha_fit = np.linalg.norm(MpMm) / norm_MM
                    error = np.linalg.norm(MpMm - alpha_fit * MM) / norm_MM

                    results_per_depth.append({
                        'depth': d,
                        'n_states_d': n_d,
                        'n_states_d1': n_d1,
                        'n_transitions': total,
                        'n_plus': n_plus,
                        'n_minus': n_minus,
                        'n_neutral': n_neutral,
                        'balance': min(n_plus, n_minus) / max(n_plus, n_minus) if max(n_plus, n_minus) > 0 else 0,
                        'alpha': float(alpha_fit),
                        'error': float(error),
                        'degenerate': False
                    })
                else:
                    results_per_depth.append({
                        'depth': d,
                        'n_transitions': total,
                        'n_plus': n_plus, 'n_minus': n_minus,
                        'degenerate': True,
                        'reason': 'zero_norm_MM'
                    })
            else:
                results_per_depth.append({
                    'depth': d,
                    'n_transitions': total,
                    'n_plus': n_plus, 'n_minus': n_minus,
                    'degenerate': degenerate,
                    'reason': 'one_sided' if degenerate else 'no_transitions'
                })

        all_results[orient_name] = results_per_depth

    return all_results


def run_dirac_tests():
    """Main test: Dirac structure on Wolfram hypergraphs"""

    print("=" * 80)
    print(" PHASE 3: DIRAC STRUCTURE ON WOLFRAM HYPERGRAPHS")
    print("=" * 80)
    print()
    print("CRITICAL TEST: M+M- ~ alpha*M^2 on real hypergraphs")
    print("Previous: works on toy models (1-15%), degenerate on hypergraphs")
    print("New: GEOMETRIC orientations (degree, density, variance)")
    print()

    all_results = {}

    for name, spec in WOLFRAM_RULES_V2.items():
        print(f"\n{'='*60}")
        print(f" [{name}] {spec['description']}")
        print(f"{'='*60}")

        engine = WolframEngineV2(spec['rules'])

        # Multiway evolution
        t0 = time.time()
        try:
            multiway = engine.evolve_multiway(spec['initial'], steps=6, max_states=1000)
        except Exception as e:
            print(f"  Multiway evolution failed: {e}")
            continue
        t_evolve = time.time() - t0

        causal_graph = engine.build_causal_graph(multiway)
        n_states = len(multiway)
        max_depth = max(multiway[s]['depth'] for s in multiway)

        print(f"  Multiway: {n_states} states, max_depth={max_depth} ({t_evolve:.2f}s)")

        if n_states < 5:
            print(f"  Too few states, skipping")
            continue

        # Compute Dirac with multiple orientations
        t0 = time.time()
        orient_results = compute_dirac_geometric_orientation(multiway, causal_graph)
        t_dirac = time.time() - t0

        print(f"  Dirac computation: {t_dirac:.2f}s")
        print()

        # Report results for each orientation
        for orient_name, results in orient_results.items():
            non_degenerate = [r for r in results if not r.get('degenerate', True)]

            if not non_degenerate:
                print(f"    [{orient_name:20s}] ALL DEGENERATE ({len(results)} layers)")
                continue

            errors = [r['error'] for r in non_degenerate]
            alphas = [r['alpha'] for r in non_degenerate]
            balances = [r['balance'] for r in non_degenerate]

            median_err = np.median(errors) if errors else float('nan')
            median_alpha = np.median(alphas) if alphas else float('nan')
            mean_balance = np.mean(balances) if balances else 0

            status = "CONFIRMED" if median_err < 0.30 else "PARTIAL" if median_err < 0.50 else "WEAK"

            print(f"    [{orient_name:20s}] {status:10s} | "
                  f"err={median_err:.1%} | alpha={median_alpha:.4f} | "
                  f"balance={mean_balance:.2f} | "
                  f"layers={len(non_degenerate)}/{len(results)}")

            if non_degenerate:
                best = min(non_degenerate, key=lambda r: r['error'])
                print(f"      Best: depth={best['depth']}, err={best['error']:.1%}, "
                      f"alpha={best['alpha']:.4f}, "
                      f"E+={best['n_plus']}, E-={best['n_minus']}")

        all_results[name] = orient_results

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print(" SUMMARY: DIRAC STRUCTURE RESULTS")
    print("=" * 80)
    print()

    # Find best orientation across all rules
    best_orient = None
    best_score = float('inf')

    orient_scores = defaultdict(list)

    for name, orient_results in all_results.items():
        for orient_name, results in orient_results.items():
            non_deg = [r for r in results if not r.get('degenerate', True)]
            if non_deg:
                median_err = np.median([r['error'] for r in non_deg])
                orient_scores[orient_name].append(median_err)

    print("  Orientation rankings (lower error = better):")
    for orient_name, scores in sorted(orient_scores.items(), key=lambda x: np.mean(x[1])):
        mean_score = np.mean(scores)
        print(f"    {orient_name:20s}: mean_error={mean_score:.1%} "
              f"(across {len(scores)} rules)")
        if mean_score < best_score:
            best_score = mean_score
            best_orient = orient_name

    print()
    if best_orient and best_score < 0.30:
        print(f"  BEST ORIENTATION: {best_orient} (error {best_score:.1%})")
        print(f"  --> DIRAC STRUCTURE CONFIRMED on hypergraphs")
        print(f"  --> M+M- ~ alpha*M^2 with geometric orientation")
    elif best_orient and best_score < 0.50:
        print(f"  BEST ORIENTATION: {best_orient} (error {best_score:.1%})")
        print(f"  --> Partial Dirac structure detected")
    else:
        print(f"  No orientation gives <50% error consistently")
        print(f"  --> Dirac structure remains PRELIMINARY (toy models only)")

    return all_results


def save_results(results: Dict, output_path: str):
    """Save results to JSON"""
    serializable = {}
    for name, orient_results in results.items():
        serializable[name] = {}
        for orient_name, layer_results in orient_results.items():
            serializable[name][orient_name] = layer_results

    with open(output_path, 'w') as f:
        json.dump(serializable, f, indent=2, default=str)
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    results = run_dirac_tests()

    output_path = "/Users/Max_1/Projects/PhysicsResearch/cosmological-unification/structural-bridge-via-uniqueness-theorems/output/phase3_dirac_results.json"
    save_results(results, output_path)
