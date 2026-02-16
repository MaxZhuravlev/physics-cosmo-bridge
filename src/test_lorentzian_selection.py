#!/usr/bin/env python3
"""
Quick tests of Lorentzian signature selection for specific cases.

Tests the key prediction: does the framework naturally select exactly 1
timelike direction (Lorentzian) or arbitrary mixtures?
"""

import numpy as np
from beta_c_high_dim import (
    create_observer_topology,
    compute_beta_c_and_signature,
    analyze_ensemble
)


def test_specific_cases():
    """Test specific observer configurations for Lorentzian selection."""

    print("=" * 70)
    print("SPECIFIC TEST CASES: Lorentzian Signature Selection")
    print("=" * 70)
    print()

    # Test 1: Chain graphs (expect high Lorentzian rate - all timelike)
    print("Test 1: Chain graphs (all edges adjacent → all timelike)")
    print("-" * 70)
    for n in [3, 4, 5, 6]:
        topology = create_observer_topology(
            n_params=n,
            graph_type="chain",
            sign_mode="adjacency",
            n_vertices=n
        )
        theta = np.zeros(n)
        analysis = compute_beta_c_and_signature(topology, theta, n_vertices=n)

        print(f"n={n}: n_edges={len(topology.edges)}, "
              f"n_timelike={topology.n_timelike}, "
              f"n_negative={analysis.n_negative_A}, "
              f"β_c={analysis.beta_c:.3f}")

        if analysis.beta_c > 0:
            beta_test = analysis.beta_c * 0.5
            n_neg = np.sum(analysis.A_eigenvalues < -beta_test)
            is_lorentzian = (n_neg == 1)
            print(f"  → Signature at β={beta_test:.3f}: "
                  f"{'LORENTZIAN ✓' if is_lorentzian else f'{n_neg} negative eigenvalues'}")
    print()

    # Test 2: Complete graphs (mixed timelike/spacelike)
    print("Test 2: Complete graphs (mixed signatures)")
    print("-" * 70)
    for n in [3, 4, 5]:
        topology = create_observer_topology(
            n_params=n,
            graph_type="complete",
            sign_mode="adjacency",
            n_vertices=n
        )
        theta = np.zeros(n)
        analysis = compute_beta_c_and_signature(topology, theta, n_vertices=n)

        print(f"n={n}: n_edges={len(topology.edges)}, "
              f"n_timelike={topology.n_timelike}, "
              f"n_spacelike={topology.n_spacelike}")
        print(f"  A eigenvalues: {analysis.A_eigenvalues}")
        print(f"  β_c={analysis.beta_c:.3f}, n_negative={analysis.n_negative_A}")

        if analysis.n_negative_A >= 2:
            print(f"  Spectral gap: |d_2 - d_1| / |d_1| = {analysis.spectral_gap_ratio:.3f}")

    print()

    # Test 3: Random ensemble for n=4
    print("Test 3: Random ensemble statistics (n=4, 100 samples)")
    print("-" * 70)
    stats = analyze_ensemble(
        n_params=4,
        graph_type="random",
        n_samples=100,
        sign_mode="random"
    )

    print(f"Samples analyzed: {stats.n_samples}")
    print(f"Lorentzian fraction: {stats.lorentzian_fraction*100:.1f}%")
    print(f"Mean β_c: {stats.mean_beta_c:.3f} ± {stats.std_beta_c:.3f}")
    print()
    print("Signature distribution:")
    total = sum(stats.signature_distribution.values())
    for sig, count in sorted(stats.signature_distribution.items(),
                            key=lambda x: -x[1])[:10]:
        frac = count / total if total > 0 else 0
        print(f"  ({sig[0]}, {sig[1]}): {count:4d} ({frac*100:5.1f}%)")

    print()

    # Test 4: Spectral gap analysis for n=6
    print("Test 4: Spectral gap analysis (n=6, complete graph)")
    print("-" * 70)

    topology = create_observer_topology(
        n_params=6,
        graph_type="complete",
        sign_mode="random",
        n_vertices=6
    )

    theta = np.zeros(6)
    analysis = compute_beta_c_and_signature(topology, theta, n_vertices=6)

    print(f"Topology: {topology.name}")
    print(f"Edges: {len(topology.edges)}, timelike: {topology.n_timelike}, "
          f"spacelike: {topology.n_spacelike}")
    print()
    print("A eigenvalues (d_i):")
    for i, d in enumerate(analysis.A_eigenvalues):
        marker = " ← d_1" if i == 0 else ""
        print(f"  d_{i+1} = {d:+.6f}{marker}")

    print()
    print(f"β_c = {analysis.beta_c:.6f}")
    print(f"Number of negative eigenvalues: {analysis.n_negative_A}")

    if analysis.n_negative_A >= 2:
        print(f"Spectral gap: {analysis.spectral_gap_ratio:.3f}")
        print()
        print("Signature evolution as β increases:")
        for i, beta in enumerate(analysis.beta_samples[:10]):
            n_neg = analysis.n_negative_at_beta[i]
            print(f"  β = {beta:.4f}: {n_neg} negative eigenvalues")

    print()
    print("=" * 70)


if __name__ == "__main__":
    test_specific_cases()
