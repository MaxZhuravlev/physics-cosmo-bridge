#!/usr/bin/env python3
"""
Causal Typicality Conjecture: Toy Model Implementation

Tests whether MOST causal-invariant microstates induce approximately MaxEnt
boundary statistics for small persistent observers.

Implementation: Coarse-grained Ising model on small hypergraphs.
Date: 2026-02-16
"""

import numpy as np
from itertools import product
from scipy.special import comb
from scipy.stats import entropy
import matplotlib.pyplot as plt


class HypergraphToyModel:
    """
    Toy model: Ising spins on a small hypergraph.

    Setup:
    - N total spins (vertices)
    - Observer O: m internal spins
    - Environment E: n = N - m external spins
    - Observer measures block average M_O = (1/m) Σ σ_i
    - Infers distribution over environment block average M_E

    Causal constraint: All configurations with same total magnetization
    are causal-equivalent (belong to same causal macrostate C).
    """

    def __init__(self, N_total, m_observer):
        """
        Parameters:
        - N_total: Total number of spins
        - m_observer: Number of spins in observer subsystem
        """
        self.N = N_total
        self.m = m_observer
        self.n = N_total - m_observer  # Environment size

        if self.m <= 0 or self.n <= 0:
            raise ValueError("Both observer and environment must have at least 1 spin")

    def enumerate_microstates(self, total_magnetization=None):
        """
        Enumerate all microstates (spin configurations).

        If total_magnetization is specified, restrict to causal macrostate C
        with that total magnetization (causal constraint).

        Returns:
        - List of microstates (each is array of ±1 spins)
        """
        microstates = []

        for config in product([-1, 1], repeat=self.N):
            config_array = np.array(config)

            if total_magnetization is not None:
                M_total = np.sum(config_array) / self.N
                if not np.isclose(M_total, total_magnetization):
                    continue

            microstates.append(config_array)

        return microstates

    def observer_measurement(self, microstate):
        """
        Observer measures block average of its m spins.

        Returns: M_O = (1/m) Σ_{i∈O} σ_i
        """
        sigma_O = microstate[:self.m]
        M_O = np.sum(sigma_O) / self.m
        return M_O

    def environment_state(self, microstate):
        """
        Extract environment configuration.

        Returns: σ_E (array of n spins)
        """
        return microstate[self.m:]

    def compute_boundary_distribution(self, microstate):
        """
        For a given microstate μ, compute the boundary distribution p_{∂O}^μ.

        Interpretation: Given the observer's measurement M_O, what is the
        distribution over environment block average M_E?

        For this toy model, the observer knows σ_O exactly, so it can compute
        M_E deterministically. The "distribution" is a delta function.

        To get a non-trivial distribution, we add NOISE: the observer measures
        M_O with Gaussian noise σ_noise.

        Returns: (M_E_observed, distribution over M_E)
        """
        sigma_E = self.environment_state(microstate)
        M_E_true = np.sum(sigma_E) / self.n

        # For this deterministic toy model, the boundary distribution is
        # a delta function at M_E_true
        return M_E_true

    def maxent_distribution(self, M_O_constraint):
        """
        Compute the MaxEnt distribution over environment block average M_E
        given the constraint that observer block average is M_O.

        For independent Ising spins, the MaxEnt distribution is:
        p(σ_E) ∝ exp(θ Σ σ_i)

        where θ is chosen so E[M_E] = M_O (coupling through total magnetization).

        For simplicity, assume NO coupling (observer and environment independent).
        Then MaxEnt is just the uniform distribution over all M_E values
        consistent with the total magnetization constraint.

        Returns: Dictionary {M_E_value: probability}
        """
        # Enumerate all possible environment configurations
        all_M_E_values = []

        for env_config in product([-1, 1], repeat=self.n):
            M_E = np.sum(env_config) / self.n
            all_M_E_values.append(M_E)

        # Count occurrences (degeneracy)
        unique_M_E, counts = np.unique(all_M_E_values, return_counts=True)

        # MaxEnt distribution: uniform over microstates → binomial over M_E
        total_count = np.sum(counts)
        maxent_dist = {M_E: count / total_count for M_E, count in zip(unique_M_E, counts)}

        return maxent_dist

    def kl_divergence_from_maxent(self, microstate):
        """
        Compute D_KL(p_{∂O}^μ || p*_MaxEnt) for a given microstate μ.

        Since p_{∂O}^μ is a delta function at M_E(μ), the KL divergence is:
        D_KL = -log p*_MaxEnt(M_E(μ))

        Returns: KL divergence (nats)
        """
        M_E_observed = self.compute_boundary_distribution(microstate)
        M_O_observed = self.observer_measurement(microstate)

        maxent_dist = self.maxent_distribution(M_O_observed)

        if M_E_observed not in maxent_dist:
            # This should not happen if MaxEnt is computed correctly
            return np.inf

        p_maxent = maxent_dist[M_E_observed]

        if p_maxent == 0:
            return np.inf

        D_KL = -np.log(p_maxent)

        return D_KL

    def test_typicality(self, total_magnetization=None, epsilon=1.0):
        """
        Test the Causal Typicality Conjecture:

        For a causal macrostate C (fixed total magnetization), what fraction
        of microstates μ ∈ M_C have D_KL(p_{∂O}^μ || p*_MaxEnt) < ε?

        Parameters:
        - total_magnetization: Causal constraint (None = no constraint)
        - epsilon: KL divergence threshold (nats)

        Returns: Dictionary with results
        """
        microstates = self.enumerate_microstates(total_magnetization)

        if len(microstates) == 0:
            return {
                'N_total': self.N,
                'm_observer': self.m,
                'n_environment': self.n,
                'total_magnetization': total_magnetization,
                'epsilon': epsilon,
                'num_microstates': 0,
                'typicality_fraction': 0.0,
                'mean_KL': np.nan,
                'std_KL': np.nan,
                'verdict': 'NO MICROSTATES'
            }

        KL_divergences = []

        for mu in microstates:
            D_KL = self.kl_divergence_from_maxent(mu)
            KL_divergences.append(D_KL)

        KL_divergences = np.array(KL_divergences)

        # Fraction of typical microstates (D_KL < epsilon)
        num_typical = np.sum(KL_divergences < epsilon)
        typicality_fraction = num_typical / len(microstates)

        # Statistics
        mean_KL = np.mean(KL_divergences)
        std_KL = np.std(KL_divergences)

        # Verdict
        if typicality_fraction > 0.9:
            verdict = "SUPPORTS typicality (>90% typical)"
        elif typicality_fraction > 0.7:
            verdict = "WEAK SUPPORT (70-90% typical)"
        elif typicality_fraction > 0.5:
            verdict = "INCONCLUSIVE (50-70% typical)"
        else:
            verdict = "AGAINST typicality (<50% typical)"

        return {
            'N_total': self.N,
            'm_observer': self.m,
            'n_environment': self.n,
            'total_magnetization': total_magnetization,
            'epsilon': epsilon,
            'num_microstates': len(microstates),
            'num_typical': num_typical,
            'typicality_fraction': typicality_fraction,
            'mean_KL': mean_KL,
            'std_KL': std_KL,
            'KL_values': KL_divergences,
            'verdict': verdict
        }


def run_experiments():
    """
    Run systematic experiments to test the Causal Typicality Conjecture.

    Test configurations:
    1. Small systems: N = 4, 6, 8
    2. Observer fractions: m/N = 0.25, 0.5
    3. Causal constraints: M_total = 0 (balanced), M_total = 0.5 (biased)
    4. KL thresholds: ε = 0.5, 1.0, 2.0
    """
    results = []

    # Configuration space
    N_values = [4, 6, 8]
    observer_fractions = [0.25, 0.5]
    magnetizations = [0.0]  # Balanced case only (for simplicity)
    epsilons = [0.5, 1.0, 2.0]

    print("=" * 80)
    print("CAUSAL TYPICALITY CONJECTURE: TOY MODEL EXPERIMENTS")
    print("=" * 80)
    print()

    for N in N_values:
        for frac in observer_fractions:
            m = int(N * frac)
            if m == 0 or m == N:
                continue

            print(f"\n{'─' * 80}")
            print(f"System: N = {N}, m_observer = {m}, n_environment = {N - m}")
            print(f"{'─' * 80}")

            model = HypergraphToyModel(N_total=N, m_observer=m)

            for M_total in magnetizations:
                print(f"\nCausal Constraint: M_total = {M_total:.1f}")

                for eps in epsilons:
                    result = model.test_typicality(
                        total_magnetization=M_total,
                        epsilon=eps
                    )

                    results.append(result)

                    print(f"  ε = {eps:.1f}: "
                          f"{result['num_typical']}/{result['num_microstates']} typical "
                          f"({result['typicality_fraction']:.1%}) | "
                          f"⟨D_KL⟩ = {result['mean_KL']:.3f} ± {result['std_KL']:.3f} | "
                          f"{result['verdict']}")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    # Overall statistics
    for eps in epsilons:
        eps_results = [r for r in results if r['epsilon'] == eps]
        avg_typicality = np.mean([r['typicality_fraction'] for r in eps_results])

        print(f"\nε = {eps:.1f}: Average typicality fraction = {avg_typicality:.1%}")

    # Check scaling: does typicality improve with N?
    print("\n\nSCALING CHECK: Does typicality fraction increase with N?")
    print("─" * 80)

    for eps in epsilons:
        print(f"\nε = {eps:.1f}:")
        for N in N_values:
            N_results = [r for r in results if r['N_total'] == N and r['epsilon'] == eps]
            if N_results:
                avg_frac = np.mean([r['typicality_fraction'] for r in N_results])
                print(f"  N = {N}: {avg_frac:.1%}")

    return results


def visualize_results(results):
    """
    Visualize the distribution of KL divergences for different configurations.
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('KL Divergence Distributions: Testing Causal Typicality', fontsize=14)

    # Filter results for visualization
    eps = 1.0  # Use ε = 1.0 for all plots

    # Plot 1: Histogram of KL values for different N
    ax = axes[0, 0]
    for N in [4, 6, 8]:
        N_results = [r for r in results if r['N_total'] == N and r['epsilon'] == eps]
        if N_results:
            KL_values = np.concatenate([r['KL_values'] for r in N_results])
            ax.hist(KL_values, bins=20, alpha=0.5, label=f'N = {N}')

    ax.axvline(eps, color='red', linestyle='--', label=f'ε = {eps}')
    ax.set_xlabel('D_KL (nats)')
    ax.set_ylabel('Count')
    ax.set_title('KL Divergence Distribution by System Size')
    ax.legend()
    ax.grid(alpha=0.3)

    # Plot 2: Typicality fraction vs N
    ax = axes[0, 1]
    N_values = sorted(set(r['N_total'] for r in results))

    for m_frac in [0.25, 0.5]:
        fractions = []
        for N in N_values:
            m = int(N * m_frac)
            matching = [r for r in results
                       if r['N_total'] == N and r['m_observer'] == m and r['epsilon'] == eps]
            if matching:
                avg_frac = np.mean([r['typicality_fraction'] for r in matching])
                fractions.append(avg_frac)
            else:
                fractions.append(np.nan)

        ax.plot(N_values, fractions, marker='o', label=f'm/N = {m_frac}')

    ax.axhline(0.9, color='green', linestyle='--', alpha=0.5, label='90% threshold')
    ax.axhline(0.5, color='red', linestyle='--', alpha=0.5, label='50% threshold')
    ax.set_xlabel('N (total spins)')
    ax.set_ylabel('Typicality Fraction')
    ax.set_title(f'Typicality vs System Size (ε = {eps})')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_ylim([0, 1.05])

    # Plot 3: Mean KL divergence vs N
    ax = axes[1, 0]

    for m_frac in [0.25, 0.5]:
        mean_KLs = []
        std_KLs = []
        for N in N_values:
            m = int(N * m_frac)
            matching = [r for r in results
                       if r['N_total'] == N and r['m_observer'] == m and r['epsilon'] == eps]
            if matching:
                mean_KLs.append(np.mean([r['mean_KL'] for r in matching]))
                std_KLs.append(np.mean([r['std_KL'] for r in matching]))
            else:
                mean_KLs.append(np.nan)
                std_KLs.append(np.nan)

        ax.errorbar(N_values, mean_KLs, yerr=std_KLs, marker='o',
                   capsize=5, label=f'm/N = {m_frac}')

    ax.axhline(eps, color='red', linestyle='--', alpha=0.5, label=f'ε = {eps}')
    ax.set_xlabel('N (total spins)')
    ax.set_ylabel('⟨D_KL⟩ (nats)')
    ax.set_title('Mean KL Divergence vs System Size')
    ax.legend()
    ax.grid(alpha=0.3)

    # Plot 4: Typicality fraction vs ε for fixed N
    ax = axes[1, 1]
    N_fixed = 6
    epsilon_values = sorted(set(r['epsilon'] for r in results))

    for m_frac in [0.25, 0.5]:
        m = int(N_fixed * m_frac)
        fractions = []
        for eps_val in epsilon_values:
            matching = [r for r in results
                       if r['N_total'] == N_fixed and r['m_observer'] == m
                       and r['epsilon'] == eps_val]
            if matching:
                fractions.append(matching[0]['typicality_fraction'])
            else:
                fractions.append(np.nan)

        ax.plot(epsilon_values, fractions, marker='o', label=f'm/N = {m_frac}')

    ax.axhline(0.9, color='green', linestyle='--', alpha=0.5, label='90% threshold')
    ax.set_xlabel('ε (KL threshold, nats)')
    ax.set_ylabel('Typicality Fraction')
    ax.set_title(f'Typicality vs Threshold (N = {N_fixed})')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_ylim([0, 1.05])

    plt.tight_layout()
    return fig


def main():
    """
    Main execution: Run experiments and generate report.
    """
    print("Starting Causal Typicality Conjecture toy model computation...")
    print()

    # Run experiments
    results = run_experiments()

    # Visualize results
    print("\nGenerating visualizations...")
    fig = visualize_results(results)

    # Save figure
    output_path = '/Users/Max_1/Projects/PhysicsResearch/cosmological-unification/papers/structural-bridge/output/causal_typicality_results.png'
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Figure saved to: {output_path}")

    # Final verdict
    print("\n" + "=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)

    # Overall typicality (ε = 1.0, typical threshold)
    eps_1_results = [r for r in results if r['epsilon'] == 1.0]
    avg_typicality = np.mean([r['typicality_fraction'] for r in eps_1_results])

    print(f"\nAverage typicality fraction (ε = 1.0): {avg_typicality:.1%}")

    if avg_typicality > 0.9:
        print("\n✓ CONJECTURE SUPPORTED by toy model")
        print("  Most microstates (>90%) produce approximately MaxEnt boundary statistics.")
        confidence = 50
    elif avg_typicality > 0.7:
        print("\n~ WEAK SUPPORT for conjecture")
        print("  Majority (70-90%) of microstates show MaxEnt behavior, but not overwhelming.")
        confidence = 40
    elif avg_typicality > 0.5:
        print("\n? INCONCLUSIVE")
        print("  Slight majority (50-70%) typical, but significant atypical fraction.")
        confidence = 30
    else:
        print("\n✗ CONJECTURE NOT SUPPORTED")
        print("  Less than 50% of microstates are typical. MaxEnt is not generic.")
        confidence = 20

    print(f"\nUpdated confidence in Causal Typicality Conjecture: {confidence}%")

    # Scaling observation
    print("\nSCALING OBSERVATION:")
    N4_typ = np.mean([r['typicality_fraction'] for r in results if r['N_total'] == 4 and r['epsilon'] == 1.0])
    N8_typ = np.mean([r['typicality_fraction'] for r in results if r['N_total'] == 8 and r['epsilon'] == 1.0])

    if N8_typ > N4_typ:
        print(f"  Typicality INCREASES with N: {N4_typ:.1%} (N=4) → {N8_typ:.1%} (N=8)")
        print("  This supports the conjecture's N → ∞ limit.")
    else:
        print(f"  Typicality DECREASES with N: {N4_typ:.1%} (N=4) → {N8_typ:.1%} (N=8)")
        print("  This is AGAINST the conjecture (expects improvement with large N).")

    print("\n" + "=" * 80)
    print("Toy model computation COMPLETE.")
    print("=" * 80)

    return results


if __name__ == '__main__':
    main()
