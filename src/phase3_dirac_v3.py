"""
PHASE 3 v3: Dirac Structure on Wolfram Hypergraphs
===================================================

CORRECTED APPROACH:

Previous attempts: M+M- ~ alpha*M^2 where M = transition matrix.
Problem: With per-edge orientation, M+ and M- have disjoint targets
         --> M-^T M+ = 0 trivially --> alpha=0, error=0 (meaningless).

CORRECT FORMULATION:

The Dirac-Klein-Gordon relation is: D^2 = Delta (Laplacian)
where D is a SIGNED incidence matrix (the Dirac operator on the graph).

On a graph/simplicial complex:
  - The Dirac operator D is the boundary/coboundary operator: D = d + d*
  - D acts on differential forms (cochains)
  - D^2 = (d + d*)^2 = dd* + d*d = Hodge Laplacian

For the SPATIAL graph from Wolfram evolution:
  1. d: 0-forms -> 1-forms (signed incidence matrix)
  2. d*: 1-forms -> 0-forms (d transpose)
  3. D^2 = Laplacian on 0-forms = d*d = L (graph Laplacian)

For the Dirac PREDICTION (M+M- ~ alpha*M^2 with vertex orientation):
  The correct test uses the SPATIAL graph (not multiway).
  Orientation comes from the hyperedge vertex ordering (natural in Wolfram rules).

  Given a spatial hypergraph with oriented edges:
    e = (a,b) has natural direction a -> b (from tuple ordering)
    D_signed(e, v) = +1 if v = target(e), -1 if v = source(e)
    D_signed^2 should be the graph Laplacian

This is ALWAYS true for a signed incidence matrix (by construction).
The non-trivial content is: does the NATURAL orientation from Wolfram
hyperedge vertex ordering produce a CONSISTENT Dirac structure?

REFINED TEST:
  On the MULTIWAY graph, define:
    - Each state has a "chirality" based on its spatial graph properties
    - The multiway transition matrix M is decomposed as M = M+ + M-
      based on chirality change
    - Test: does M encode a Dirac-like operator?
      Specifically: does the spectrum of D = M+ - M- relate to
      the spectrum of L = M^T M (Klein-Gordon)?

  KEY INSIGHT: Use the SIGNED transition matrix D = M+ - M-
  where M+ are chirality-increasing transitions, M- are chirality-decreasing.
  Then test: eigenvalues of D^2 ~ eigenvalues of L = M^T M

  If yes: Dirac structure exists (D^2 ~ KG)
  If no: no Dirac structure at this scale
"""

import numpy as np
import networkx as nx
from collections import defaultdict
from typing import Dict, List, Tuple
import time
import json
import sys

sys.path.insert(0, '.')
from wolfram_engine_v2 import WolframEngineV2, hypergraph_to_graph, WOLFRAM_RULES_V2


def spatial_dirac_test(hypergraph: List[Tuple]) -> Dict:
    """
    Test Dirac structure on the SPATIAL hypergraph.

    For a hypergraph, construct:
    1. Signed incidence matrix B (the boundary operator)
       B(e, v) = +1 if v is last vertex of e, -1 if v is first
    2. Graph Laplacian L = B^T B
    3. Verify L equals standard graph Laplacian (always true by construction)
    4. Compute spectral properties

    The REAL test: does the NATURAL vertex ordering in hyperedges
    produce a consistent orientation? Specifically:
    - Is the orientation "compatible" (no frustration)?
    - Does it define a spin structure?
    """
    G = hypergraph_to_graph(hypergraph)
    if G.number_of_nodes() < 3 or G.number_of_edges() < 3:
        return {'status': 'too_small'}

    # Build oriented edges from hyperedge vertex ordering
    oriented_edges = []
    for he in hypergraph:
        for i in range(len(he)):
            for j in range(i+1, len(he)):
                # Natural orientation: lower position -> higher position
                oriented_edges.append((he[i], he[j]))

    # Remove duplicates (keep first occurrence direction)
    seen = set()
    unique_oriented = []
    for u, v in oriented_edges:
        edge = frozenset([u, v])
        if edge not in seen:
            seen.add(edge)
            unique_oriented.append((u, v))

    # Build signed incidence matrix B
    nodes = sorted(G.nodes())
    n = len(nodes)
    m = len(unique_oriented)
    node_idx = {v: i for i, v in enumerate(nodes)}

    B = np.zeros((m, n))
    for e_idx, (u, v) in enumerate(unique_oriented):
        B[e_idx, node_idx[u]] = -1  # source
        B[e_idx, node_idx[v]] = +1  # target

    # Dirac operator: D = B (boundary operator, maps 0-cochains to 1-cochains)
    # D^2 in the sense of Hodge Laplacian: L = B^T B = D* D
    L_from_B = B.T @ B

    # Standard graph Laplacian for comparison
    L_standard = nx.laplacian_matrix(G).toarray().astype(float)

    # Check if L_from_B == L_standard (should be exactly equal)
    diff = np.linalg.norm(L_from_B - L_standard) / np.linalg.norm(L_standard)

    # Spectral analysis of B (the Dirac operator)
    # Singular values of B relate to eigenvalues of L = B^T B
    singular_values = np.linalg.svd(B, compute_uv=False)
    laplacian_eigs = np.sort(np.linalg.eigvalsh(L_from_B))

    # Check: sigma_i^2 = lambda_i (Dirac^2 = KG)
    sv_squared = np.sort(singular_values**2)[::-1]
    lap_eigs_sorted = np.sort(laplacian_eigs)[::-1]

    # Trim to same length (may differ)
    min_len = min(len(sv_squared), len(lap_eigs_sorted))
    sv_sq = sv_squared[:min_len]
    lap_e = lap_eigs_sorted[:min_len]

    # Correlation
    if min_len > 2:
        # They should be identical (by SVD theorem)
        spectral_match = np.corrcoef(sv_sq[sv_sq > 1e-10],
                                      lap_e[:len(sv_sq[sv_sq > 1e-10])])[0, 1]
    else:
        spectral_match = np.nan

    # Check frustration: is the orientation cycle-consistent?
    # A cycle is frustrated if the product of orientations around it is -1
    # For a simply-connected graph, frustration = 0 always
    # For graphs with cycles, frustration measures topological obstruction to spin structure
    frustration = 0
    n_cycles = 0

    # Check triangles
    for node in nodes:
        nbrs = list(G.neighbors(node))
        for i in range(len(nbrs)):
            for j in range(i+1, len(nbrs)):
                if G.has_edge(nbrs[i], nbrs[j]):
                    # Triangle: node, nbrs[i], nbrs[j]
                    # Check orientation consistency
                    n_cycles += 1
                    # Get orientations
                    edges_in_cycle = []
                    for u, v in [(node, nbrs[i]), (nbrs[i], nbrs[j]), (nbrs[j], node)]:
                        edge = frozenset([u, v])
                        for e_idx, (eu, ev) in enumerate(unique_oriented):
                            if frozenset([eu, ev]) == edge:
                                # +1 if aligned with cycle direction, -1 if opposed
                                if (eu, ev) == (u, v):
                                    edges_in_cycle.append(+1)
                                else:
                                    edges_in_cycle.append(-1)
                                break

                    if len(edges_in_cycle) == 3:
                        product = edges_in_cycle[0] * edges_in_cycle[1] * edges_in_cycle[2]
                        if product == -1:
                            frustration += 1

    frustration_ratio = frustration / n_cycles if n_cycles > 0 else 0

    return {
        'n_vertices': n,
        'n_oriented_edges': m,
        'laplacian_match': 1.0 - diff,
        'spectral_match': float(spectral_match) if not np.isnan(spectral_match) else None,
        'n_triangles': n_cycles,
        'frustration': frustration,
        'frustration_ratio': frustration_ratio,
        'spin_structure': frustration == 0,
        'nonzero_laplacian_eigs': int(np.sum(laplacian_eigs > 1e-10)),
        'spectral_gap': float(laplacian_eigs[laplacian_eigs > 1e-10][0]) if np.any(laplacian_eigs > 1e-10) else 0,
        'status': 'computed'
    }


def multiway_dirac_test(states: Dict, causal_graph: nx.DiGraph) -> Dict:
    """
    Test Dirac structure on the MULTIWAY graph.

    Approach: Define signed transition operator D = M_+ - M_-
    where M_+ counts transitions that INCREASE some geometric quantity
    and M_- counts transitions that DECREASE it.

    Test: spectrum of D^T D relates to spectrum of M^T M

    The KEY innovation here: instead of testing M+M- ~ alpha*M^2 entry-by-entry,
    we test the SPECTRAL relationship: eigenvalues of D^2 should be proportional
    to eigenvalues of the Laplacian (Klein-Gordon).
    """
    state_list = sorted(states.keys(), key=lambda s: (states[s]['depth'], str(s)))
    max_depth = max(states[s]['depth'] for s in states)

    # Compute geometric features
    features = {}
    for s in state_list:
        hyperedges = list(s)
        if not hyperedges:
            features[s] = {'n_vertices': 0, 'n_edges': 0}
            continue

        vertices = set()
        for e in hyperedges:
            vertices.update(e)

        G = hypergraph_to_graph(hyperedges)
        degrees = [d for _, d in G.degree()] if G.number_of_nodes() > 0 else [0]

        features[s] = {
            'n_vertices': len(vertices),
            'n_edges': len(hyperedges),
            'avg_degree': np.mean(degrees),
            'degree_std': np.std(degrees),
        }

    # Build full transition matrix and signed version
    n = len(state_list)
    state_idx = {s: i for i, s in enumerate(state_list)}

    M = np.zeros((n, n))
    D = np.zeros((n, n))  # Signed: +1 for "positive" transitions, -1 for "negative"

    for s in state_list:
        i = state_idx[s]
        for s_next in states[s]['children']:
            if s_next in state_idx:
                j = state_idx[s_next]
                M[j, i] = 1

                # Sign based on degree change (geometric chirality)
                deg_s = features[s]['avg_degree']
                deg_sn = features[s_next]['avg_degree']
                if deg_sn > deg_s + 0.001:
                    D[j, i] = +1
                elif deg_sn < deg_s - 0.001:
                    D[j, i] = -1
                else:
                    D[j, i] = 0  # Neutral

    # Laplacian = M^T M
    L = M.T @ M

    # "Dirac squared" = D^T D
    D2 = D.T @ D

    # Spectral comparison
    eigs_L = np.sort(np.linalg.eigvalsh(L))[::-1]
    eigs_D2 = np.sort(np.linalg.eigvalsh(D2))[::-1]

    # Correlation of nonzero eigenvalues
    nonzero_L = eigs_L[eigs_L > 1e-10]
    nonzero_D2 = eigs_D2[eigs_D2 > 1e-10]

    min_len = min(len(nonzero_L), len(nonzero_D2))
    if min_len >= 3:
        correlation = np.corrcoef(nonzero_L[:min_len], nonzero_D2[:min_len])[0, 1]

        # Best linear fit: D^2 ~ alpha * L
        alpha_spectral = np.sum(nonzero_D2[:min_len] * nonzero_L[:min_len]) / np.sum(nonzero_L[:min_len]**2)
        residual = np.linalg.norm(nonzero_D2[:min_len] - alpha_spectral * nonzero_L[:min_len])
        relative_error = residual / np.linalg.norm(nonzero_L[:min_len])
    else:
        correlation = np.nan
        alpha_spectral = np.nan
        relative_error = np.nan

    # Count +/- transitions
    n_positive = int(np.sum(D > 0))
    n_negative = int(np.sum(D < 0))
    n_neutral = int(np.sum(M > 0)) - n_positive - n_negative

    return {
        'n_states': n,
        'n_transitions': int(M.sum()),
        'n_positive': n_positive,
        'n_negative': n_negative,
        'n_neutral': n_neutral,
        'balance': min(n_positive, n_negative) / max(n_positive, n_negative, 1),
        'spectral_correlation': float(correlation) if not np.isnan(correlation) else None,
        'alpha_spectral': float(alpha_spectral) if not np.isnan(alpha_spectral) else None,
        'relative_error': float(relative_error) if not np.isnan(relative_error) else None,
        'rank_L': int(np.linalg.matrix_rank(L)),
        'rank_D2': int(np.linalg.matrix_rank(D2)),
        'top5_eigs_L': nonzero_L[:5].tolist() if len(nonzero_L) >= 5 else nonzero_L.tolist(),
        'top5_eigs_D2': nonzero_D2[:5].tolist() if len(nonzero_D2) >= 5 else nonzero_D2.tolist(),
    }


def run_all_dirac_tests():
    """Run both spatial and multiway Dirac tests"""

    print("=" * 80)
    print(" PHASE 3 v3: DIRAC STRUCTURE - CORRECTED APPROACH")
    print("=" * 80)
    print()
    print("Two tests:")
    print("  A. Spatial graph: natural orientation from hyperedge vertex ordering")
    print("     -> D^2 = Laplacian (always true), frustration check (spin structure)")
    print("  B. Multiway graph: signed transition operator D = M+ - M-")
    print("     -> spectral test: eigenvalues of D^2 ~ eigenvalues of L")
    print()

    all_results = {}

    for name, spec in WOLFRAM_RULES_V2.items():
        print(f"\n{'='*60}")
        print(f" [{name}] {spec['description']}")
        print(f"{'='*60}")

        engine = WolframEngineV2(spec['rules'])

        # ============================================
        # A. Spatial Dirac test
        # ============================================
        print("\n  A. SPATIAL GRAPH DIRAC:")
        try:
            spatial = engine.evolve_spatial(spec['initial'], steps=100, max_edges=2000)
            spatial_result = spatial_dirac_test(spatial)

            if spatial_result['status'] == 'too_small':
                print("     Too small for analysis")
            else:
                print(f"     Vertices: {spatial_result['n_vertices']}, "
                      f"Oriented edges: {spatial_result['n_oriented_edges']}")
                print(f"     Laplacian match: {spatial_result['laplacian_match']:.6f} "
                      f"(should be 1.0)")
                print(f"     Triangles: {spatial_result['n_triangles']}")
                print(f"     Frustration: {spatial_result['frustration']}/{spatial_result['n_triangles']} "
                      f"({spatial_result['frustration_ratio']:.1%})")

                if spatial_result['spin_structure']:
                    print(f"     SPIN STRUCTURE: YES (frustration-free)")
                else:
                    print(f"     SPIN STRUCTURE: NO (frustrated)")

                print(f"     Spectral gap: {spatial_result['spectral_gap']:.4f}")
        except Exception as e:
            print(f"     Error: {e}")
            spatial_result = {'status': 'error', 'error': str(e)}

        # ============================================
        # B. Multiway Dirac test
        # ============================================
        print("\n  B. MULTIWAY DIRAC (Spectral):")
        try:
            multiway = engine.evolve_multiway(spec['initial'], steps=6, max_states=500)
            causal = engine.build_causal_graph(multiway)

            if len(multiway) < 5:
                print("     Too few states")
                mw_result = {'status': 'too_small'}
            else:
                mw_result = multiway_dirac_test(multiway, causal)

                print(f"     States: {mw_result['n_states']}, "
                      f"Transitions: {mw_result['n_transitions']}")
                print(f"     D+: {mw_result['n_positive']}, D-: {mw_result['n_negative']}, "
                      f"Neutral: {mw_result['n_neutral']}")
                print(f"     Balance: {mw_result['balance']:.2f}")
                print(f"     Rank(L): {mw_result['rank_L']}, Rank(D^2): {mw_result['rank_D2']}")

                if mw_result['spectral_correlation'] is not None:
                    print(f"     Spectral correlation: {mw_result['spectral_correlation']:.4f}")
                    print(f"     Alpha (D^2 ~ alpha*L): {mw_result['alpha_spectral']:.4f}")
                    print(f"     Relative error: {mw_result['relative_error']:.1%}")

                    if mw_result['spectral_correlation'] > 0.9:
                        print(f"     >>> DIRAC-KG SPECTRAL RELATION DETECTED <<<")
                    elif mw_result['spectral_correlation'] > 0.7:
                        print(f"     ~ Moderate spectral correlation")
                    else:
                        print(f"     Weak/no spectral correlation")
                else:
                    print(f"     Insufficient nonzero eigenvalues for comparison")

        except Exception as e:
            print(f"     Error: {e}")
            mw_result = {'status': 'error', 'error': str(e)}

        all_results[name] = {
            'spatial': spatial_result,
            'multiway': mw_result
        }

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print(" SUMMARY: DIRAC STRUCTURE v3")
    print("=" * 80)
    print()

    print("  A. SPATIAL GRAPHS (spin structure from vertex ordering):")
    for name, res in all_results.items():
        sr = res.get('spatial', {})
        if sr.get('status') == 'computed':
            spin = "SPIN" if sr.get('spin_structure') else "FRUSTRATED"
            frust = sr.get('frustration_ratio', 0)
            print(f"     [{name:25s}] {spin:10s} | "
                  f"frustration={frust:.0%} | "
                  f"triangles={sr.get('n_triangles', 0)}")

    print()
    print("  B. MULTIWAY GRAPHS (spectral D^2 ~ L):")
    for name, res in all_results.items():
        mr = res.get('multiway', {})
        if mr.get('spectral_correlation') is not None:
            corr = mr['spectral_correlation']
            alpha = mr.get('alpha_spectral', 0)
            err = mr.get('relative_error', 1)
            status = "D^2~L" if corr > 0.9 else ("partial" if corr > 0.7 else "weak")
            print(f"     [{name:25s}] {status:8s} | "
                  f"corr={corr:.3f} | alpha={alpha:.4f} | err={err:.1%}")
        else:
            print(f"     [{name:25s}] insufficient data")

    return all_results


if __name__ == "__main__":
    results = run_all_dirac_tests()

    output_path = "/Users/Max_1/Projects/PhysicsResearch/cosmological-unification/structural-bridge-via-uniqueness-theorems/output/phase3_dirac_v3_results.json"

    # Serialize
    serializable = {}
    for name, res in results.items():
        serializable[name] = {}
        for key, val in res.items():
            if isinstance(val, dict):
                serializable[name][key] = {k: v for k, v in val.items()
                                            if not isinstance(v, np.ndarray)}
            else:
                serializable[name][key] = val

    with open(output_path, 'w') as f:
        json.dump(serializable, f, indent=2, default=str)
    print(f"\nResults saved to: {output_path}")
