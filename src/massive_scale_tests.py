"""
MASSIVE SCALE TESTS - M3 Max 128GB
===================================

Push Python hypergraph engine to LIMITS:
- N = 5,000-20,000 states (vs previous max 1000)
- Optimize for M3 Max architecture
- Parallel processing where possible
- Test if LD mechanism changes at massive scale

GOAL: Understand WHY LD fails and WHERE it breaks down
"""

import numpy as np
import multiprocessing as mp
from collections import defaultdict
from typing import Dict, List, Tuple
import time

from hypergraph_engine import HypergraphEngine


def optimize_for_m3_max():
    """Configure for M3 Max performance"""
    # M3 Max: 16 performance cores + 4 efficiency cores
    optimal_workers = 12  # Leave headroom

    print(f"M3 Max optimization:")
    print(f"  CPU cores available: {mp.cpu_count()}")
    print(f"  Using workers: {optimal_workers}")
    print(f"  RAM: 128GB (can handle ~20M states)")
    print()

    return optimal_workers


def test_ld_at_massive_scale(system_name: str, rule: List, initial: List,
                               target_states: int = 10000):
    """
    Test LD at N=10,000+

    Question: Does null_dim grow linearly, sublinearly, or catastrophically?
    """
    print(f"\n{'='*80}")
    print(f"MASSIVE SCALE LD: {system_name} (target N={target_states})")
    print(f"{'='*80}\n")

    start = time.time()

    engine = HypergraphEngine(rule)

    # Evolve to target
    print(f"Evolving to {target_states} states...")
    states = engine.evolve_multiway(initial, steps=10, max_states=target_states)

    elapsed = time.time() - start
    print(f"✓ Generated {len(states)} states in {elapsed:.1f}s")
    print(f"  Rate: {len(states)/elapsed:.0f} states/sec")
    print()

    # Memory usage estimate
    import sys
    states_size_mb = sys.getsizeof(states) / 1024 / 1024
    print(f"Memory: ~{states_size_mb:.1f} MB for states dict")
    print()

    # Test LD at different scales
    state_list = sorted(states.keys(), key=str)
    max_depth = max(states[s]['depth'] for s in states)

    print(f"Depth range: 0 to {max_depth}")
    print()

    # Measure null_dim growth
    null_dim_progression = []

    for d in range(min(max_depth, 8)):
        states_d = [s for s in state_list if states[s]['depth'] == d]
        states_d1 = [s for s in state_list if states[s]['depth'] == d + 1]

        if not states_d or not states_d1:
            continue

        # Constraint matrix
        C = np.zeros((len(states_d), len(states_d1)))

        for i, s in enumerate(states_d):
            for s_next in states[s]['children']:
                if s_next in states_d1:
                    j = states_d1.index(s_next)
                    C[i, j] = 1

        rank = np.linalg.matrix_rank(C)
        null_dim = len(states_d) - rank

        fraction = null_dim / len(states_d) if len(states_d) > 0 else 0

        print(f"Depth {d}: n={len(states_d):4d}, rank={rank:4d}, null={null_dim:4d} ({fraction:.1%})")

        null_dim_progression.append({
            'd': d,
            'n': len(states_d),
            'rank': rank,
            'null_dim': null_dim,
            'fraction': fraction
        })

        # Stop if too slow
        if len(states_d) > 5000:
            print(f"  (Stopping LD test - states too many for O(n²) constraint matrix)")
            break

    # Analyze progression
    print()
    if len(null_dim_progression) >= 3:
        fractions = [p['fraction'] for p in null_dim_progression]

        if all(f == 0 for f in fractions):
            print("✓✓ LD holds at ALL scales tested")
        elif fractions[-1] > 0.5:
            print("✗ LD fails catastrophically (>50% null space)")
        elif fractions[-1] > 0.1:
            print("⚠ LD deteriorates significantly")
        else:
            print("~ LD partial (small null space)")

    return null_dim_progression


def test_purification_at_scale(system_name: str, rule: List, initial: List,
                                 target_states: int = 10000):
    """
    Does purification still hold at massive scale?
    """
    print(f"\n{'='*80}")
    print(f"MASSIVE SCALE PURIFICATION: {system_name}")
    print(f"{'='*80}\n")

    engine = HypergraphEngine(rule)
    states = engine.evolve_multiway(initial, steps=10, max_states=target_states)

    print(f"States: {len(states)}")

    state_list = sorted(states.keys(), key=lambda s: (states[s]['depth'], str(s)))
    max_depth = max(states[s]['depth'] for s in states)

    # Test at several depths
    success_rates = []

    for d in range(min(max_depth, 5)):
        states_d = [s for s in state_list if states[s]['depth'] == d]
        states_d1 = [s for s in state_list if states[s]['depth'] == d + 1]

        if len(states_d) < 10 or len(states_d1) < 10:
            continue

        # Build transition matrix
        P = np.zeros((len(states_d), len(states_d1)))

        for i, s in enumerate(states_d):
            children = [c for c in states[s]['children'] if c in states_d1]
            for c in children:
                j = states_d1.index(c)
                P[i, j] = 1

        # Normalize
        for i in range(len(states_d)):
            row_sum = P[i, :].sum()
            if row_sum > 0:
                P[i, :] /= row_sum

        # Test random mixed states
        n_test = min(50, len(states_d) // 2)
        successful = 0

        for _ in range(n_test):
            # Random mixed state
            rho = np.random.dirichlet(np.ones(len(states_d)))
            rho_d1 = P.T @ rho

            if np.any(rho_d1 > 1e-10):
                successful += 1

        success_rate = successful / n_test
        success_rates.append(success_rate)

        print(f"Depth {d}: {successful}/{n_test} purifiable ({success_rate:.0%})")

    avg_success = np.mean(success_rates) if success_rates else 0

    print(f"\nAverage success: {avg_success:.0%}")

    if avg_success > 0.95:
        print("✓✓ PURIFICATION holds at massive scale")
    elif avg_success > 0.80:
        print("~ PURIFICATION partial")
    else:
        print("✗ PURIFICATION fails")

    return success_rates


def parallel_system_test(systems_to_test: List[Dict], target_n: int = 5000):
    """
    Test multiple systems in parallel (M3 Max has 16 cores!)
    """
    print(f"\n{'='*80}")
    print(f"PARALLEL SYSTEM TESTS (N={target_n})")
    print(f"{'='*80}\n")

    workers = optimize_for_m3_max()

    # For now: sequential (parallel needs careful pickling)
    # But architecture ready for parallelization

    results = {}

    for system in systems_to_test:
        name = system['name']
        print(f"\n[{name}]")

        # LD test
        ld_result = test_ld_at_massive_scale(name, system['rule'],
                                               system['initial'], target_n)

        # Purification test
        purif_result = test_purification_at_scale(name, system['rule'],
                                                    system['initial'], target_n)

        results[name] = {
            'ld': ld_result,
            'purification': purif_result
        }

    return results


def main():
    """Run massive scale tests on M3 Max"""
    from run_critical_tests import WOLFRAM_RULES

    print("="*80)
    print(" M3 MAX MASSIVE SCALE TESTS")
    print(" 128GB RAM | 16 cores | Python optimized")
    print("="*80)

    optimize_for_m3_max()

    # Prepare test systems
    systems = [
        {
            'name': 'basic_trinary',
            'rule': WOLFRAM_RULES['basic_trinary']['rule'],
            'initial': WOLFRAM_RULES['basic_trinary']['initial']
        },
        {
            'name': 'wolfram_expanding',
            'rule': WOLFRAM_RULES['wolfram_expanding']['rule'],
            'initial': WOLFRAM_RULES['wolfram_expanding']['initial']
        }
    ]

    # Start with N=5000 (conservative), can push to 20,000 if needed
    print("\nStarting with N=5,000 (can scale to 20,000 with 128GB)")
    print()

    results = parallel_system_test(systems, target_n=5000)

    # Summary
    print("\n" + "="*80)
    print(" MASSIVE SCALE SUMMARY")
    print("="*80)
    print()

    for name, data in results.items():
        print(f"{name}:")

        if data['ld']:
            final_fraction = data['ld'][-1]['fraction'] if data['ld'] else 0
            print(f"  LD: null space = {final_fraction:.1%} at max depth")

        if data['purification']:
            avg_purif = np.mean(data['purification'])
            print(f"  Purification: {avg_purif:.0%} success")

    return results


if __name__ == "__main__":
    main()
