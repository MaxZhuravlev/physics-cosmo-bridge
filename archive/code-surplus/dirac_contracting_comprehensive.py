"""
DIRAC CONTRACTING & MIXED RULES - Comprehensive Test
=====================================================

GOAL: Find non-degenerate Dirac structure M⁺M⁻ ≈ αM²

Strategy:
1. Test contracting hypergraph rules
2. Test mixed rules (both expanding and contracting)
3. Use descendants orientation (proven best from Session 12)
4. Check for non-degenerate structure (both E+ and E-)
5. If found: validate M⁺M⁻ ≈ αM² with error <30%

Uses Pure Python hypergraph engine (full control, no API issues)
"""

import numpy as np
from typing import List, Tuple, Set, Dict
from collections import defaultdict
import json

class HypergraphRule:
    """Hypergraph rewriting rule"""
    def __init__(self, lhs: List[Tuple], rhs: List[Tuple], name: str = ""):
        self.lhs = [tuple(sorted(edge)) for edge in lhs]
        self.rhs = [tuple(sorted(edge)) for edge in rhs]
        self.name = name

    def __repr__(self):
        return f"{self.name}: {self.lhs} → {self.rhs}"

def evolve_hypergraph(initial: List[Tuple], rules: List[HypergraphRule], steps: int = 5):
    """Evolve hypergraph multiway system"""

    # State = frozenset of edges
    states = [frozenset(tuple(sorted(e)) for e in initial)]
    transitions = defaultdict(set)  # state_idx → set of next state indices

    for step in range(steps):
        new_states = []

        for si, state in enumerate(states):
            state_list = list(state)

            # Try each rule
            for rule in rules:
                # Try to match LHS
                for i in range(len(state_list)):
                    # Simple matching (exact match for now)
                    if len(rule.lhs) == 1 and state_list[i] in rule.lhs:
                        # Apply rule
                        new_state = set(state_list)
                        new_state.remove(state_list[i])
                        new_state.update(rule.rhs)
                        new_state_frozen = frozenset(new_state)

                        # Add if new
                        if new_state_frozen not in states and new_state_frozen not in new_states:
                            new_states.append(new_state_frozen)
                            transitions[si].add(len(states) + len(new_states) - 1)

                    # Try multi-edge matches
                    if len(rule.lhs) > 1:
                        # Check if all LHS edges present
                        if all(edge in state for edge in rule.lhs):
                            new_state = set(state_list)
                            for edge in rule.lhs:
                                if edge in new_state:
                                    new_state.remove(edge)
                            new_state.update(rule.rhs)
                            new_state_frozen = frozenset(new_state)

                            if new_state_frozen not in states and new_state_frozen not in new_states:
                                new_states.append(new_state_frozen)
                                transitions[si].add(len(states) + len(new_states) - 1)

        states.extend(new_states)
        if not new_states:
            break

    return states, transitions

def build_causal_graph(states, transitions):
    """Build causal graph from transitions"""
    import networkx as nx

    G = nx.DiGraph()
    for i in range(len(states)):
        G.add_node(i)

    for src, targets in transitions.items():
        for tgt in targets:
            G.add_edge(src, tgt)

    return G

def compute_descendants(graph, node):
    """Count causal future (descendants)"""
    import networkx as nx
    try:
        desc = nx.descendants(graph, node)
        return len(desc)
    except:
        return 0

def test_dirac_structure(states, transitions, causal_graph, system_name):
    """Test M⁺M⁻ ≈ αM² with descendants orientation"""

    n = len(states)
    if n < 5:
        return {'status': 'too_small', 'n': n}

    # Build transition matrix M
    M = np.zeros((n, n))
    for src, targets in transitions.items():
        for tgt in targets:
            if src < n and tgt < n:
                M[src, tgt] = 1

    # Compute descendants for each state
    descendants = [compute_descendants(causal_graph, i) for i in range(n)]

    # Build M+ (expanding) and M- (contracting)
    Mplus = np.zeros((n, n))
    Mminus = np.zeros((n, n))

    eplus_count = 0
    eminus_count = 0

    for i in range(n):
        for j in range(n):
            if M[i, j] > 0:
                # Transition i → j exists
                if descendants[j] >= descendants[i]:
                    Mplus[i, j] = M[i, j]
                    eplus_count += 1
                else:
                    Mminus[i, j] = M[i, j]
                    eminus_count += 1

    # Check degeneracy
    total_trans = eplus_count + eminus_count
    if total_trans == 0:
        return {'status': 'no_transitions', 'n': n}

    eplus_frac = eplus_count / total_trans
    eminus_frac = eminus_count / total_trans

    # Degenerate if all one type
    if eminus_count == 0:
        return {
            'status': 'degenerate_expanding',
            'n': n,
            'E+': eplus_count,
            'E-': 0,
            'E+_frac': 1.0
        }
    if eplus_count == 0:
        return {
            'status': 'degenerate_contracting',
            'n': n,
            'E+': 0,
            'E-': eminus_count,
            'E-_frac': 1.0
        }

    # Non-degenerate! Test M⁺M⁻ ≈ αM²
    print(f"  ✓ NON-DEGENERATE: E+={eplus_count}, E-={eminus_count}")
    print(f"    Ratio: {eplus_frac:.2f} / {eminus_frac:.2f}")

    # Compute products
    MplusMminus = Mplus @ Mminus
    M2 = M @ M

    # Find best α
    # M⁺M⁻ ≈ α·M² → minimize ||M⁺M⁻ - α·M²||

    numerator = np.sum(MplusMminus * M2)
    denominator = np.sum(M2 * M2)

    if denominator > 0:
        alpha_best = numerator / denominator
    else:
        alpha_best = 0

    # Compute error
    diff = MplusMminus - alpha_best * M2
    error = np.linalg.norm(diff) / (np.linalg.norm(M2) + 1e-10)

    print(f"    α = {alpha_best:.4f}")
    print(f"    Error = {error:.4f}")

    if error < 0.30:
        print(f"    ✓✓ DIRAC STRUCTURE CONFIRMED (error < 30%)")
        status = 'confirmed'
    elif error < 0.50:
        print(f"    ✓ DIRAC STRUCTURE PRESENT (error < 50%)")
        status = 'partial'
    else:
        print(f"    ✗ DIRAC STRUCTURE WEAK (error > 50%)")
        status = 'weak'

    return {
        'status': status,
        'n': n,
        'E+': eplus_count,
        'E-': eminus_count,
        'E+_frac': eplus_frac,
        'E-_frac': eminus_frac,
        'alpha': alpha_best,
        'error': error,
        'system': system_name
    }

def main():
    print("=" * 80)
    print(" DIRAC CONTRACTING & MIXED RULES - Pure Python")
    print("=" * 80)
    print()

    results = []

    # TEST 1: Pure Contracting (Triangle Collapse)
    print("TEST 1: TRIANGLE COLLAPSE (Pure Contracting)")
    print("-" * 80)

    rule1 = HypergraphRule(
        lhs=[('A', 'B'), ('B', 'C'), ('C', 'A')],
        rhs=[('A', 'C')],
        name="TriangleCollapse"
    )

    initial1 = [('1', '2'), ('2', '3'), ('3', '1')]
    states1, trans1 = evolve_hypergraph(initial1, [rule1], steps=5)
    graph1 = build_causal_graph(states1, trans1)

    print(f"States: {len(states1)}")
    print(f"Transitions: {sum(len(t) for t in trans1.values())}")
    print()

    result1 = test_dirac_structure(states1, trans1, graph1, "triangle_collapse")
    results.append(result1)
    print()

    # TEST 2: Edge Merge (Contracting)
    print("TEST 2: EDGE MERGE (Contracting)")
    print("-" * 80)

    rule2 = HypergraphRule(
        lhs=[('A', 'B'), ('B', 'C')],
        rhs=[('A', 'C')],
        name="EdgeMerge"
    )

    initial2 = [('1', '2'), ('2', '3'), ('3', '4')]
    states2, trans2 = evolve_hypergraph(initial2, [rule2], steps=5)
    graph2 = build_causal_graph(states2, trans2)

    print(f"States: {len(states2)}")
    print(f"Transitions: {sum(len(t) for t in trans2.values())}")
    print()

    result2 = test_dirac_structure(states2, trans2, graph2, "edge_merge")
    results.append(result2)
    print()

    # TEST 3: Node Removal (Contracting)
    print("TEST 3: NODE REMOVAL (Contracting)")
    print("-" * 80)

    rule3 = HypergraphRule(
        lhs=[('A', 'B', 'C')],
        rhs=[('A', 'C')],
        name="NodeRemoval"
    )

    initial3 = [('1', '2', '3'), ('2', '3', '4')]
    states3, trans3 = evolve_hypergraph(initial3, [rule3], steps=4)
    graph3 = build_causal_graph(states3, trans3)

    print(f"States: {len(states3)}")
    print(f"Transitions: {sum(len(t) for t in trans3.values())}")
    print()

    result3 = test_dirac_structure(states3, trans3, graph3, "node_removal")
    results.append(result3)
    print()

    # TEST 4: MIXED (Expansion + Contraction alternating)
    print("TEST 4: MIXED DYNAMICS (Both Types)")
    print("-" * 80)

    # Combine expanding and contracting
    rule4a = HypergraphRule(
        lhs=[('A', 'B')],
        rhs=[('A', 'C'), ('C', 'B')],
        name="Expand"
    )
    rule4b = HypergraphRule(
        lhs=[('A', 'B'), ('B', 'A')],
        rhs=[('A', 'B')],
        name="Contract"
    )

    initial4 = [('1', '2'), ('2', '1'), ('2', '3')]
    states4, trans4 = evolve_hypergraph(initial4, [rule4a, rule4b], steps=6)
    graph4 = build_causal_graph(states4, trans4)

    print(f"States: {len(states4)}")
    print(f"Transitions: {sum(len(t) for t in trans4.values())}")
    print()

    result4 = test_dirac_structure(states4, trans4, graph4, "mixed_dynamics")
    results.append(result4)
    print()

    # SUMMARY
    print("=" * 80)
    print(" SUMMARY")
    print("=" * 80)
    print()

    confirmed = [r for r in results if r.get('status') == 'confirmed']
    partial = [r for r in results if r.get('status') == 'partial']
    degenerate = [r for r in results if 'degenerate' in r.get('status', '')]

    print(f"Confirmed (error <30%): {len(confirmed)}")
    print(f"Partial (error <50%): {len(partial)}")
    print(f"Degenerate (one-sided): {len(degenerate)}")
    print()

    if confirmed:
        print("✓✓ DIRAC STRUCTURE CONFIRMED on:")
        for r in confirmed:
            print(f"  - {r['system']}: α={r['alpha']:.3f}, error={r['error']:.1%}")
        print()
        print("IMPACT: Unique prediction VERIFIED (+20% publication)")
    elif partial:
        print("✓ DIRAC STRUCTURE PRESENT (partial) on:")
        for r in partial:
            print(f"  - {r['system']}: α={r['alpha']:.3f}, error={r['error']:.1%}")
        print()
        print("IMPACT: Evidence for structure (+10% publication)")
    else:
        print("✗ All rules degenerate or weak")
        print("  → Dirac remains open question")
        print("  → Flag as future work (spatial embedding)")

    print()

    # Save results
    output_file = '../output/dirac_contracting_results.json'
    with open(output_file, 'w') as f:
        # Convert to JSON-serializable
        results_json = []
        for r in results:
            r_copy = dict(r)
            for k, v in r_copy.items():
                if isinstance(v, (np.integer, np.int64)):
                    r_copy[k] = int(v)
                elif isinstance(v, (np.floating, np.float64)):
                    r_copy[k] = float(v)
            results_json.append(r_copy)

        json.dump({
            'test_date': '2026-02-14',
            'method': 'Pure Python hypergraph engine',
            'orientation': 'descendants',
            'systems_tested': len(results),
            'confirmed': len(confirmed),
            'partial': len(partial),
            'degenerate': len(degenerate),
            'results': results_json
        }, f, indent=2)

    print(f"✓ Results saved: {output_file}")
    print()

    return results, confirmed

if __name__ == "__main__":
    results, confirmed = main()

    if confirmed:
        print("=" * 80)
        print(" DIRAC PREDICTION: CONFIRMED ✓✓✓")
        print("=" * 80)
        print()
        print("M⁺M⁻ ≈ αM² structure found on contracting/mixed hypergraph rules.")
        print("This is UNIQUE prediction - not in Wolfram OR Vanchurin separately.")
        print()
        print("Publication impact: +20% (new physics from bridge)")
    else:
        print("=" * 80)
        print(" DIRAC: Remains Open Question")
        print("=" * 80)
        print()
        print("All tested rules degenerate (expanding-only or contracting-only).")
        print("Future work: Spatial embedding orientation (coordinate-based).")
        print()
        print("Publication impact: None (flag as preliminary)")
