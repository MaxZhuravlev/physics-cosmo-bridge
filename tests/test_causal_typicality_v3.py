#!/usr/bin/env python3
"""
Tests for causal_typicality_v3.py

Verifies:
1. CI rules are actually confluent (commutativity)
2. Non-CI rules can be non-confluent
3. Local observer has no global knowledge
4. MaxEnt distributions match constraints
5. KL divergence is non-negative
"""

import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from causal_typicality_v3 import (
    generate_ci_rules,
    generate_non_ci_rules,
    apply_rule,
    evolve_system,
    local_observer_statistics,
    maxent_distribution_first_order,
    kl_divergence,
    align_distributions
)


def test_ci_rules_commute():
    """Test that CI rules actually commute (confluence property)."""
    np.random.seed(42)

    L = 10
    k = 3
    rules = generate_ci_rules(L, k, num_rules=5)

    # Generate random initial state
    state = np.random.randint(0, 2, L)

    # Apply rules in two different orders
    state1 = state.copy()
    for rule in rules:
        state1 = apply_rule(state1, rule)

    state2 = state.copy()
    for rule in reversed(rules):
        state2 = apply_rule(state2, rule)

    # Should reach same final state (confluence)
    assert np.array_equal(state1, state2), "CI rules do not commute!"
    print("✓ CI rules commute (confluence verified)")


def test_non_ci_can_be_nonconfluent():
    """Test that non-CI rules CAN be non-confluent (though not guaranteed)."""
    np.random.seed(42)

    L = 10
    k = 3

    # Try multiple random seeds to find non-confluent example
    found_nonconfluent = False
    for seed in range(100):
        np.random.seed(seed)
        rules = generate_non_ci_rules(L, k, num_rules=5)
        state = np.random.randint(0, 2, L)

        state1 = state.copy()
        for rule in rules:
            state1 = apply_rule(state1, rule)

        state2 = state.copy()
        for rule in reversed(rules):
            state2 = apply_rule(state2, rule)

        if not np.array_equal(state1, state2):
            found_nonconfluent = True
            break

    assert found_nonconfluent, "Non-CI rules always confluent (unexpected!)"
    print("✓ Non-CI rules can be non-confluent")


def test_local_observer_window_size():
    """Test that local observer only sees its window."""
    np.random.seed(42)

    L = 16
    window_size = 4
    window_start = 5
    N_steps = 100

    # Generate evolution
    rules = generate_ci_rules(L, k=3, num_rules=5)
    initial_state = np.random.randint(0, 2, L)
    states = evolve_system(initial_state, rules, N_steps)

    # Extract local statistics
    unique_patterns, p_obs, observed_means = local_observer_statistics(
        states, window_start, window_size
    )

    # Check window size
    assert all(len(pattern) == window_size for pattern in unique_patterns), \
        "Patterns have wrong window size!"

    # Check probabilities sum to 1
    assert np.isclose(np.sum(p_obs), 1.0), \
        f"Probabilities don't sum to 1: {np.sum(p_obs)}"

    # Check observed means match window size
    assert len(observed_means) == window_size, \
        f"Observed means have wrong length: {len(observed_means)}"

    print("✓ Local observer window size correct")


def test_maxent_matches_constraints():
    """Test that MaxEnt distribution matches observed marginals."""
    np.random.seed(42)

    window_size = 3
    # Artificial observed means
    observed_means = np.array([0.3, 0.7, 0.5])

    # Compute MaxEnt
    all_patterns, p_maxent = maxent_distribution_first_order(observed_means, window_size)

    # Check probabilities sum to 1
    assert np.isclose(np.sum(p_maxent), 1.0), \
        f"MaxEnt probabilities don't sum to 1: {np.sum(p_maxent)}"

    # Check marginal means match
    computed_means = np.sum(all_patterns * p_maxent[:, None], axis=0)
    assert np.allclose(computed_means, observed_means, atol=1e-3), \
        f"MaxEnt doesn't match constraints: {computed_means} vs {observed_means}"

    print("✓ MaxEnt distribution matches constraints")


def test_kl_nonnegative():
    """Test that KL divergence is always non-negative."""
    np.random.seed(42)

    # Generate two random distributions
    p = np.random.dirichlet([1, 1, 1, 1])
    q = np.random.dirichlet([1, 1, 1, 1])

    kl = kl_divergence(p, q)

    assert kl >= 0, f"KL divergence is negative: {kl}"

    # Test KL(p || p) = 0
    kl_self = kl_divergence(p, p)
    assert np.isclose(kl_self, 0.0, atol=1e-6), \
        f"KL(p || p) != 0: {kl_self}"

    print("✓ KL divergence is non-negative")


def test_alignment_preserves_distribution():
    """Test that alignment doesn't change probabilities."""
    np.random.seed(42)

    window_size = 3

    # Generate some patterns
    unique_patterns = np.array([
        [0, 0, 1],
        [1, 0, 0],
        [1, 1, 1]
    ])
    p_obs = np.array([0.5, 0.3, 0.2])

    # All possible patterns
    from itertools import product
    all_patterns = np.array(list(product([0, 1], repeat=window_size)))
    p_maxent = np.random.dirichlet([1] * len(all_patterns))
    p_maxent /= np.sum(p_maxent)  # Normalize

    # Align
    p_obs_full, p_maxent_full = align_distributions(
        unique_patterns, p_obs, all_patterns, p_maxent
    )

    # Check that observed probabilities are preserved
    assert np.isclose(np.sum(p_obs_full), 1.0), \
        f"Aligned p_obs doesn't sum to 1: {np.sum(p_obs_full)}"

    # Check that original observed patterns have correct probabilities
    for i, pattern in enumerate(unique_patterns):
        # Find pattern in all_patterns
        pattern_int = pattern @ (2 ** np.arange(window_size))
        all_ints = all_patterns @ (2 ** np.arange(window_size))
        idx = np.where(all_ints == pattern_int)[0][0]

        assert np.isclose(p_obs_full[idx], p_obs[i]), \
            f"Pattern probability not preserved: {p_obs_full[idx]} vs {p_obs[i]}"

    print("✓ Alignment preserves distributions")


def test_evolution_deterministic():
    """Test that evolution is deterministic with fixed seed."""
    np.random.seed(42)

    L = 10
    rules = generate_ci_rules(L, k=3, num_rules=5)
    initial_state = np.random.randint(0, 2, L)

    # Run twice with same seed
    np.random.seed(100)
    states1 = evolve_system(initial_state, rules, 50)

    np.random.seed(100)
    states2 = evolve_system(initial_state, rules, 50)

    assert np.array_equal(states1, states2), \
        "Evolution is not deterministic!"

    print("✓ Evolution is deterministic")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Testing causal_typicality_v3.py")
    print("=" * 60)
    print()

    tests = [
        test_ci_rules_commute,
        test_non_ci_can_be_nonconfluent,
        test_local_observer_window_size,
        test_maxent_matches_constraints,
        test_kl_nonnegative,
        test_alignment_preserves_distribution,
        test_evolution_deterministic
    ]

    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            return False
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            return False

    print()
    print("=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
