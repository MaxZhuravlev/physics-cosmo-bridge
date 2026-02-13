"""
Deep Analysis of Critical Test Results
=======================================

FINDINGS:
1. κ ≠ 0 on 2 systems → continual limit PARTIAL confirmation
2. Dirac α=0 → all transitions one-sided (need investigation)
3. LD violation at scale → MAJOR finding, contradicts exhaustive test
4. Gram PD holds → Axiom 2 solid

FOCUS: Understand LD violation and Dirac degeneracy
"""

import numpy as np
import networkx as nx
from hypergraph_engine import HypergraphEngine
from typing import Dict, List


def deep_ld_analysis(system_name: str, system_config: Dict):
    """
    Deep dive into WHY LD fails at scale

    Hypothesis: At large depths, states become equivalent under marginals
    but dynamics from earlier depths still distinguishes them
    """
    print(f"\n{'='*80}")
    print(f"DEEP LD ANALYSIS: {system_name}")
    print(f"{'='*80}\n")

    engine = HypergraphEngine(system_config['rule'])
    states = engine.evolve_multiway(system_config['initial'], steps=7, max_states=1000)

    print(f"Total states: {len(states)}")

    state_list = sorted(states.keys(), key=str)
    max_depth = max(states[s]['depth'] for s in states)

    print(f"Max depth: {max_depth}\n")

    # For each depth, analyze marginals vs full distribution
    for d in range(min(max_depth, 6)):  # Limit to first 6 depths
        states_d = [s for s in state_list if states[s]['depth'] == d]
        states_d1 = [s for s in state_list if states[s]['depth'] == d + 1]

        if not states_d or not states_d1:
            continue

        print(f"Depth {d} → {d+1}:")
        print(f"  States at d={d}: {len(states_d)}")
        print(f"  States at d+1={d+1}: {len(states_d1)}")

        # Build constraint matrix: rows=states_d, cols=states_d1
        C = np.zeros((len(states_d), len(states_d1)))

        for i, s in enumerate(states_d):
            for j, s_next in enumerate(states_d1):
                if s_next in states[s]['children']:
                    C[i, j] = 1

        rank = np.linalg.matrix_rank(C)
        null_dim = len(states_d) - rank

        print(f"  Constraint matrix: {C.shape}")
        print(f"  Rank: {rank}, Null dim: {null_dim}")

        if null_dim > 0:
            print(f"  ⚠️  NULL SPACE NON-TRIVIAL")

            # Which states are indistinguishable?
            # Find rows with identical patterns
            for i in range(len(states_d)):
                for j in range(i + 1, len(states_d)):
                    if np.array_equal(C[i], C[j]):
                        print(f"    States {i} and {j} have identical children distribution")
                        print(f"      State {i}: {len(states_d[i])} edges")
                        print(f"      State {j}: {len(states_d[j])} edges")
                        break  # Show first example only
                break

        else:
            print(f"  ✓ LD holds (full rank)")

        # Check if adding dynamics from d-1 helps
        if d > 0:
            states_d_minus_1 = [s for s in state_list if states[s]['depth'] == d - 1]

            # Augmented matrix: include parent information
            C_aug = np.zeros((len(states_d), len(states_d1) + len(states_d_minus_1)))
            C_aug[:, :len(states_d1)] = C  # Children

            # Add parent connections
            for i, s in enumerate(states_d):
                for k, s_prev in enumerate(states_d_minus_1):
                    if s in states[s_prev]['children']:
                        C_aug[i, len(states_d1) + k] = 1

            rank_aug = np.linalg.matrix_rank(C_aug)
            null_dim_aug = len(states_d) - rank_aug

            print(f"  With dynamics from d-1:")
            print(f"    Rank: {rank_aug}, Null dim: {null_dim_aug}")

            if null_dim_aug < null_dim:
                print(f"    ✓ Dynamics reduces null space: {null_dim} → {null_dim_aug}")

    return states


def deep_dirac_analysis(system_name: str, system_config: Dict):
    """
    Why α=0? Check if all transitions are one-sided
    """
    print(f"\n{'='*80}")
    print(f"DEEP DIRAC ANALYSIS: {system_name}")
    print(f"{'='*80}\n")

    engine = HypergraphEngine(system_config['rule'])
    states = engine.evolve_multiway(system_config['initial'], steps=6, max_states=500)
    causal_graph = engine.compute_causal_graph(states)

    # Compute descendants for each state
    descendants_count = {}
    for state in states.keys():
        if state in causal_graph:
            desc = nx.descendants(causal_graph, state)
            descendants_count[state] = len(desc)
        else:
            descendants_count[state] = 0

    print(f"States: {len(states)}")
    print(f"Descendants computed\n")

    # Analyze transitions by depth
    state_list = sorted(states.keys(), key=lambda s: (states[s]['depth'], str(s)))
    max_depth = max(states[s]['depth'] for s in states)

    for d in range(min(max_depth, 4)):
        states_d = [s for s in state_list if states[s]['depth'] == d]
        states_d1 = [s for s in state_list if states[s]['depth'] == d + 1]

        if not states_d or not states_d1:
            continue

        expanding = 0  # |desc(s')| > |desc(s)|
        contracting = 0  # |desc(s')| < |desc(s)|
        neutral = 0  # |desc(s')| = |desc(s)|

        for s in states_d:
            for s_next in states[s]['children']:
                if s_next in states_d1:
                    d_s = descendants_count.get(s, 0)
                    d_s_next = descendants_count.get(s_next, 0)

                    if d_s_next > d_s:
                        expanding += 1
                    elif d_s_next < d_s:
                        contracting += 1
                    else:
                        neutral += 1

        total = expanding + contracting + neutral

        if total > 0:
            print(f"Depth {d} → {d+1}: {total} transitions")
            print(f"  E+ (expanding): {expanding} ({expanding/total:.1%})")
            print(f"  E- (contracting): {contracting} ({contracting/total:.1%})")
            print(f"  E= (neutral): {neutral} ({neutral/total:.1%})")

            # Check for degeneracy
            if expanding == 0 or contracting == 0:
                print(f"  ⚠️  DEGENERATE: all transitions one-sided")
            else:
                # Compute actual M⁺M⁻ with these counts
                frac_plus = expanding / total
                frac_minus = contracting / total
                product = frac_plus * frac_minus
                print(f"  f(E+) × f(E-) = {product:.4f}")

    return states


def main():
    """Run deep analyses on key findings"""

    from run_critical_tests import WOLFRAM_RULES

    # Focus on systems that showed interesting behavior

    # 1. LD violation at scale - investigate
    print("\n" + "=" * 80)
    print(" INVESTIGATION 1: WHY LD FAILS AT SCALE")
    print("=" * 80)

    deep_ld_analysis("basic_trinary", WOLFRAM_RULES["basic_trinary"])

    # 2. Dirac degeneracy - investigate
    print("\n" + "=" * 80)
    print(" INVESTIGATION 2: WHY DIRAC α=0")
    print("=" * 80)

    deep_dirac_analysis("wolfram_expanding", WOLFRAM_RULES["wolfram_expanding"])

    # 3. Non-zero curvature systems - understand better
    print("\n" + "=" * 80)
    print(" INVESTIGATION 3: SYSTEMS WITH κ ≠ 0")
    print("=" * 80)

    for name in ["contracting", "binary_to_trinary"]:
        deep_dirac_analysis(name, WOLFRAM_RULES[name])


if __name__ == "__main__":
    main()
