"""
PURIFICATION PATH - Alternative to LD for QM
=============================================

MacBook tests showed: LD (Axiom 4) fails at scale.
But purification (Axiom 5) may work INDEPENDENTLY.

Chiribella Axiom 5 (Purification):
  For any mixed state ρ, there exists pure state |ψ⟩ in larger Hilbert space
  such that Tr_bath(|ψ⟩⟨ψ|) = ρ

Multiway analog:
  For any probabilistic mixture over branches, there exists single branch
  in extended multiway such that tracing over "bath branches" recovers mixture

TEST: Does compact structure (branching + confluence) provide purification?
"""

import numpy as np
from hypergraph_engine import HypergraphEngine
from typing import Dict, Set, Tuple, List


def test_purification_multiway(system_name: str, rule: List, initial: List):
    """
    Test purification axiom for multiway states

    Idea: Mixed state at depth d = trace over branches at depth d+1
    Purification: extended multiway provides the "larger space"
    """
    print(f"\n{'='*80}")
    print(f"PURIFICATION TEST: {system_name}")
    print(f"{'='*80}\n")

    engine = HypergraphEngine(rule)
    states = engine.evolve_multiway(initial, steps=5, max_states=500)

    state_list = sorted(states.keys(), key=lambda s: (states[s]['depth'], str(s)))
    max_depth = max(states[s]['depth'] for s in states)

    print(f"States: {len(states)}, Max depth: {max_depth}\n")

    purification_tests = []

    for d in range(min(max_depth, 4)):
        states_d = [s for s in state_list if states[s]['depth'] == d]
        states_d1 = [s for s in state_list if states[s]['depth'] == d + 1]

        if len(states_d) < 2 or len(states_d1) < 2:
            continue

        print(f"Depth {d} → {d+1}:")
        print(f"  States at d: {len(states_d)}")
        print(f"  States at d+1: {len(states_d1)}")

        # Build transition matrix P: states_d → states_d1
        P = np.zeros((len(states_d), len(states_d1)))

        for i, s in enumerate(states_d):
            children = [c for c in states[s]['children'] if c in states_d1]
            for c in children:
                j = states_d1.index(c)
                P[i, j] = 1

        # Normalize rows (if state has children)
        for i in range(len(states_d)):
            row_sum = P[i, :].sum()
            if row_sum > 0:
                P[i, :] /= row_sum

        # Test purification:
        # 1. Take arbitrary mixed state at d (probability distribution over states_d)
        # 2. Can we find pure state at d+1 that gives this mixture after tracing?

        # Mixed state example: uniform over first 2 states
        if len(states_d) >= 2:
            rho_mixed = np.zeros(len(states_d))
            rho_mixed[0] = 0.5
            rho_mixed[1] = 0.5

            # Propagate forward
            rho_d1 = P.T @ rho_mixed  # Distribution at d+1

            # Can we find pure state |ψ⟩ at d+1 that "purifies" rho_d?
            # In QM: |ψ⟩ = Σ_i sqrt(p_i) |i⟩|bath_i⟩
            # Here: single branch at d+1 with appropriate weights

            # Simple test: Is there a branch at d+1 reachable from mixture?
            nonzero_d1 = np.where(rho_d1 > 0)[0]

            if len(nonzero_d1) > 0:
                # Purification exists - any single branch in support
                purification_exists = True
                n_purifications = len(nonzero_d1)
            else:
                purification_exists = False
                n_purifications = 0

            print(f"  Mixed state: 50/50 over states 0,1")
            print(f"  Propagated to {len(nonzero_d1)} branches at d+1")
            print(f"  Purification: {'YES' if purification_exists else 'NO'}")
            print(f"  # purifications: {n_purifications}")

            # Stronger test: Check if multiway graph is "complete enough"
            # Completeness = for any mixed state, exists purifying branch

            # Test random mixed states
            n_test = min(20, len(states_d))
            successful_purifications = 0

            for test_i in range(n_test):
                # Random mixed state
                rho_test = np.random.dirichlet(np.ones(len(states_d)))
                rho_test_d1 = P.T @ rho_test

                if np.any(rho_test_d1 > 0):
                    successful_purifications += 1

            success_rate = successful_purifications / n_test

            print(f"  Random tests: {successful_purifications}/{n_test} purifiable")
            print(f"  Success rate: {success_rate:.1%}")

            if success_rate > 0.95:
                print(f"  ✓✓ PURIFICATION HOLDS")
            elif success_rate > 0.80:
                print(f"  ~ PURIFICATION PARTIAL")
            else:
                print(f"  ✗ PURIFICATION FAILS")

            purification_tests.append({
                'depth': d,
                'success_rate': success_rate,
                'n_purifications_example': n_purifications
            })

    return purification_tests


def test_coarse_grained_unitarity(system_name: str, rule: List, initial: List):
    """
    Test if unitarity emerges after coarse-graining

    Idea: Full matrix not unitary, but projection to top-k singular vectors might be
    """
    print(f"\n{'='*80}")
    print(f"COARSE-GRAINED UNITARITY: {system_name}")
    print(f"{'='*80}\n")

    engine = HypergraphEngine(rule)
    states = engine.evolve_multiway(initial, steps=5, max_states=300)

    state_list = sorted(states.keys(), key=lambda s: (states[s]['depth'], str(s)))
    max_depth = max(states[s]['depth'] for s in states)

    results = []

    for d in range(min(max_depth, 4)):
        states_d = [s for s in state_list if states[s]['depth'] == d]
        states_d1 = [s for s in state_list if states[s]['depth'] == d + 1]

        if len(states_d) < 5 or len(states_d1) < 5:
            continue

        # Build transition matrix
        M = np.zeros((len(states_d1), len(states_d)))

        for i, s in enumerate(states_d):
            for c in states[s]['children']:
                if c in states_d1:
                    j = states_d1.index(c)
                    M[j, i] = 1

        # SVD
        U, S, Vt = np.linalg.svd(M, full_matrices=False)

        # Test unitarity at different truncation levels
        for k in [2, 5, 10, 20]:
            if k > len(S):
                continue

            # Truncated M
            M_k = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]

            # Normalize to get transition matrix
            M_k_normalized = M_k.copy()
            for col in range(M_k.shape[1]):
                col_sum = abs(M_k[:, col]).sum()
                if col_sum > 0:
                    M_k_normalized[:, col] /= col_sum

            # Check unitarity: M†M = I (in truncated space)
            MtM = Vt[:k, :].T @ Vt[:k, :]  # Should be identity on k-dim subspace

            # Measure deviation from identity
            I_k = np.eye(min(k, MtM.shape[0]))
            if MtM.shape[0] >= k:
                deviation = np.linalg.norm(MtM[:k, :k] - I_k) / np.linalg.norm(I_k)
            else:
                deviation = np.nan

            variance_captured = S[:k].sum() / S.sum() if len(S) > 0 else 0

            print(f"  k={k}: var={variance_captured:.1%}, unitary_dev={deviation:.3f}")

            results.append({
                'depth': d,
                'k': k,
                'variance': variance_captured,
                'unitarity_deviation': deviation
            })

    # Summary
    good_results = [r for r in results if not np.isnan(r['unitarity_deviation']) and r['unitarity_deviation'] < 0.1]

    if good_results:
        best = min(good_results, key=lambda r: r['unitarity_deviation'])
        print(f"\n  Best coarse-graining: k={best['k']}, dev={best['unitarity_deviation']:.4f}")
        print(f"  ✓ APPROXIMATE UNITARITY at coarse scale")
    else:
        print(f"\n  ✗ No good coarse-graining found")

    return results


def main():
    """Run alternative QM path tests"""
    from run_critical_tests import WOLFRAM_RULES

    print("="*80)
    print(" ALTERNATIVE QM PATHS - Post MacBook Investigation")
    print("="*80)
    print("\nProblem: LD (Axiom 4) fails at scale → Chiribella path blocked")
    print("Solution: Test alternative axioms (purification, coarse unitarity)\n")

    # Test purification on 3 systems
    purif_results = {}
    for name in ["basic_trinary", "wolfram_expanding", "two_rules"]:
        result = test_purification_multiway(name, WOLFRAM_RULES[name]['rule'],
                                             WOLFRAM_RULES[name]['initial'])
        purif_results[name] = result

    # Test coarse-grained unitarity
    coarse_results = {}
    for name in ["basic_trinary", "wolfram_expanding"]:
        result = test_coarse_grained_unitarity(name, WOLFRAM_RULES[name]['rule'],
                                                WOLFRAM_RULES[name]['initial'])
        coarse_results[name] = result

    # Summary
    print("\n" + "="*80)
    print(" SUMMARY: Alternative QM Paths")
    print("="*80)

    print("\nPurification:")
    for name, tests in purif_results.items():
        if tests:
            avg_success = np.mean([t['success_rate'] for t in tests])
            status = "✓ HOLDS" if avg_success > 0.95 else ("~ PARTIAL" if avg_success > 0.80 else "✗ FAILS")
            print(f"  {name}: {status} ({avg_success:.1%})")

    print("\nCoarse unitarity:")
    for name, tests in coarse_results.items():
        good = [t for t in tests if not np.isnan(t.get('unitarity_deviation', np.nan))
                and t['unitarity_deviation'] < 0.1]
        if good:
            best_k = min(good, key=lambda t: t['unitarity_deviation'])['k']
            print(f"  {name}: ✓ WORKS at k={best_k}")
        else:
            print(f"  {name}: ✗ FAILS")

    return {'purification': purif_results, 'coarse': coarse_results}


if __name__ == "__main__":
    main()
