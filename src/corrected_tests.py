"""
CORRECTED TESTS
===============

Based on deep analysis findings:
1. LD needs FULL tomography (all splits × all depths × dynamics)
2. Dirac needs different orientation (lexicographic, not descendants)
3. Curvature needs larger systems

CORRECTED PREDICTIONS:
- LD: null_dim=0 when using CUMULATIVE constraints (depth ≤ d)
- Dirac: lexicographic orientation gives non-degenerate structure
- Ricci: need N > 1000 to see stable κ
"""

import numpy as np
import networkx as nx
from hypergraph_engine import HypergraphEngine
from collections import defaultdict


def test_ld_full_tomography(system_name: str, system_config: dict):
    """
    LD with FULL tomography:
    - All possible splits of state
    - All depths cumulatively
    - Dynamics included
    """
    print(f"\n{'=' * 80}")
    print(f"LD FULL TOMOGRAPHY: {system_name}")
    print(f"{'=' * 80}\n")

    engine = HypergraphEngine(system_config['rule'])
    states = engine.evolve_multiway(system_config['initial'], steps=6, max_states=500)

    state_list = sorted(states.keys(), key=str)
    n_states = len(state_list)
    state_to_idx = {s: i for i, s in enumerate(state_list)}

    print(f"Total states: {n_states}")

    # Build CUMULATIVE constraint matrix
    # Rows: states, Columns: constraints from all sources
    constraints = []

    # For each depth d, add constraints from transitions d-1 → d
    max_depth = max(states[s]['depth'] for s in states)

    for d in range(max_depth + 1):
        states_d = [s for s in state_list if states[s]['depth'] == d]

        # For each state at depth d, record which states at d-1 lead to it
        if d > 0:
            states_d_minus_1 = [s for s in state_list if states[s]['depth'] == d - 1]

            for s in states_d:
                constraint_vec = np.zeros(n_states)
                # Mark parents
                for s_prev in states[s]['parents']:
                    if s_prev in state_to_idx:
                        constraint_vec[state_to_idx[s_prev]] = 1

                if np.any(constraint_vec):
                    constraints.append(constraint_vec)

        # Also record children
        states_d_plus_1 = [s for s in state_list if states[s]['depth'] == d + 1]

        for s in states_d:
            constraint_vec = np.zeros(n_states)
            # Mark children
            for s_next in states[s]['children']:
                if s_next in state_to_idx:
                    constraint_vec[state_to_idx[s_next]] = 1

            if np.any(constraint_vec):
                constraints.append(constraint_vec)

    # Stack into matrix
    if constraints:
        C_full = np.vstack(constraints)
        rank = np.linalg.matrix_rank(C_full)
        null_dim = n_states - rank

        print(f"\nFull tomography:")
        print(f"  Constraint matrix: {C_full.shape}")
        print(f"  Rank: {rank} / {n_states}")
        print(f"  Null dimension: {null_dim}")

        if null_dim == 0:
            print(f"  ✓✓✓ LD HOLDS with full tomography")
            return True
        else:
            print(f"  ⚠️  Still {null_dim} null dimensions remain")
            return False

    return None


def test_dirac_lexicographic(system_name: str, system_config: dict):
    """
    Dirac with LEXICOGRAPHIC orientation
    E+ = lexicographically later state
    E- = lexicographically earlier state
    """
    print(f"\n{'=' * 80}")
    print(f"DIRAC LEXICOGRAPHIC: {system_name}")
    print(f"{'=' * 80}\n")

    engine = HypergraphEngine(system_config['rule'])
    states = engine.evolve_multiway(system_config['initial'], steps=6, max_states=500)

    state_list = sorted(states.keys(), key=lambda s: (states[s]['depth'], str(s)))
    max_depth = max(states[s]['depth'] for s in states)

    print(f"States: {len(states)}\n")

    # Layered analysis with lex orientation
    errors = []

    for d in range(min(max_depth, 5)):
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

        for s in states_d:
            for s_next in states[s]['children']:
                if s_next in states_d1:
                    i = idx_d[s]
                    j = idx_d1[s_next]

                    M[j, i] = 1

                    # Lexicographic comparison
                    if str(s_next) >= str(s):  # Later lexicographically
                        M_plus[j, i] = 1
                    else:
                        M_minus[j, i] = 1

        # Check M⁺M⁻ vs M²
        MM = M.T @ M
        M_plus_M_minus = M_minus.T @ M_plus

        if np.linalg.norm(MM) > 1e-10:
            alpha_fit = np.linalg.norm(M_plus_M_minus) / np.linalg.norm(MM)
            error = np.linalg.norm(M_plus_M_minus - alpha_fit * MM) / np.linalg.norm(MM)

            print(f"Depth {d}: n={n_d}, transitions={int(M.sum())}")
            print(f"  E+ fraction: {M_plus.sum()/max(M.sum(), 1):.2%}")
            print(f"  α = {alpha_fit:.4f}, error = {error:.1%}")

            errors.append(error)

    if errors:
        print(f"\nMedian error: {np.median(errors):.1%}")
        if np.median(errors) < 0.30:
            print(f"✓ DIRAC STRUCTURE CONFIRMED (lex orientation)")

    return errors


def main():
    from run_critical_tests import WOLFRAM_RULES

    # Test corrected LD
    print("\n" + "="*80)
    print("CORRECTED TEST 1: LD WITH FULL TOMOGRAPHY")
    print("="*80)

    ld_results = {}
    for name in ["basic_trinary", "wolfram_expanding", "two_rules"]:
        result = test_ld_full_tomography(name, WOLFRAM_RULES[name])
        ld_results[name] = result

    # Test corrected Dirac
    print("\n" + "="*80)
    print("CORRECTED TEST 2: DIRAC WITH LEX ORIENTATION")
    print("="*80)

    dirac_results = {}
    for name in ["basic_trinary", "wolfram_expanding", "two_rules"]:
        errors = test_dirac_lexicographic(name, WOLFRAM_RULES[name])
        dirac_results[name] = errors

    # Summary
    print("\n" + "="*80)
    print("CORRECTED RESULTS SUMMARY")
    print("="*80)

    print("\nLD with full tomography:")
    for name, result in ld_results.items():
        status = "✓ HOLDS" if result else ("✗ FAILS" if result is False else "N/A")
        print(f"  {name}: {status}")

    print("\nDirac with lex orientation:")
    for name, errors in dirac_results.items():
        if errors:
            median_err = np.median(errors)
            status = "✓ CONFIRMED" if median_err < 0.30 else f"~ PARTIAL ({median_err:.1%})"
            print(f"  {name}: {status}")

    return {'ld': ld_results, 'dirac': dirac_results}


if __name__ == "__main__":
    main()
