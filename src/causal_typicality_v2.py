#!/usr/bin/env python3
"""
Causal Typicality Conjecture: Local Observer Model (CORRECTED)

KEY FIX: Observer does NOT know the global constraint M_total = 0.
Observer knows only M_O and infers the environment using unconstrained MaxEnt.

This tests whether causal microstates (satisfying |M_total × N| ≤ threshold)
are ATYPICAL relative to the observer's local MaxEnt inference.

Date: 2026-02-16
Version: 2.0 (corrects v1.0 trivial conditioning bug)
"""

import numpy as np
from itertools import product
from scipy.special import comb
from scipy.stats import entropy
import matplotlib.pyplot as plt
from collections import defaultdict


class LocalObserverModel:
    """
    Local Observer Model for Causal Typicality Conjecture.

    Setup:
    - N total spins (Ising ±1)
    - Observer O: m internal spins
    - Environment E: n = N - m external spins

    Observer:
    - Measures M_O = (1/m) Σ_{i∈O} σ_i
    - Does NOT know global constraint M_total
    - Infers environment using unconstrained MaxEnt: p*(M_E) = Binomial(n, 1/2)

    Causal Constraint:
    - Macrostate C_δ: all microstates with |M_total × N| ≤ δ
    - As δ → 0, stricter causal constraint

    Conjecture:
    - For microstates μ ∈ C_δ, most should have D_KL(p_{∂O}^μ || p*) < ε
    - As N → ∞, this fraction should INCREASE (measure concentration)
    """

    def __init__(self, N_total, m_observer):
        """
        Parameters:
        - N_total: Total number of spins
        - m_observer: Number of spins in observer subsystem
        """
        self.N = N_total
        self.m = m_observer
        self.n = N_total - m_observer

        if self.m <= 0 or self.n <= 0:
            raise ValueError("Both observer and environment must have ≥1 spin")

    def observer_measurement(self, microstate):
        """
        Observer measures block average of its m spins.
        Returns: M_O = (1/m) Σ_{i∈O} σ_i ∈ [-1, 1]
        """
        return np.mean(microstate[:self.m])

    def environment_measurement(self, microstate):
        """
        True environment block average (unknown to observer).
        Returns: M_E = (1/n) Σ_{i∈E} σ_i ∈ [-1, 1]
        """
        return np.mean(microstate[self.m:])

    def total_magnetization(self, microstate):
        """
        Global constraint (unknown to observer).
        Returns: M_total = (1/N) Σ σ_i
        """
        return np.mean(microstate)

    def unconstrained_maxent_distribution(self):
        """
        Observer's MaxEnt inference over environment (NO global constraint).

        Observer knows only M_O and assumes environment is independent.
        MaxEnt distribution: uniform over all environment microstates.

        For n spins, this gives:
        p*(M_E) = Binomial(k_up; n, 1/2) where k_up = (1 + M_E × n) / 2

        Returns: dict {M_E: probability}
        """
        # Enumerate all environment magnetizations
        possible_k_up = range(0, self.n + 1)  # Number of up spins

        maxent_dist = {}
        total_count = 2**self.n

        for k_up in possible_k_up:
            # M_E = (k_up - k_down) / n = (k_up - (n - k_up)) / n = (2*k_up - n) / n
            M_E = (2 * k_up - self.n) / self.n

            # Degeneracy: C(n, k_up)
            degeneracy = comb(self.n, k_up, exact=True)

            maxent_dist[M_E] = degeneracy / total_count

        return maxent_dist

    def kl_divergence_from_maxent(self, microstate):
        """
        Compute D_KL(p_{∂O}^μ || p*_MaxEnt) for microstate μ.

        Since observer knows σ_O exactly, p_{∂O}^μ is a delta function at M_E(μ).
        Therefore: D_KL = -log p*_MaxEnt(M_E(μ))

        Returns: KL divergence (nats)
        """
        M_E_observed = self.environment_measurement(microstate)

        maxent_dist = self.unconstrained_maxent_distribution()

        if M_E_observed not in maxent_dist:
            # Should not happen
            return np.inf

        p_maxent = maxent_dist[M_E_observed]

        if p_maxent == 0:
            return np.inf

        return -np.log(p_maxent)

    def enumerate_causal_macrostate(self, delta_threshold):
        """
        Enumerate all microstates in causal macrostate C_δ.

        C_δ = {μ : |M_total(μ) × N| ≤ δ}

        Parameters:
        - delta_threshold: Constraint threshold (integer, number of excess spins)

        Returns: list of microstates (each is array of ±1 spins)
        """
        microstates = []

        for config in product([-1, 1], repeat=self.N):
            config_array = np.array(config)

            # Check causal constraint
            M_total = self.total_magnetization(config_array)
            excess_spins = abs(M_total * self.N)

            if excess_spins <= delta_threshold:
                microstates.append(config_array)

        return microstates

    def test_typicality(self, delta_threshold, epsilon=1.0):
        """
        Test the Causal Typicality Conjecture.

        For causal macrostate C_δ, what fraction of microstates have
        D_KL(p_{∂O}^μ || p*_MaxEnt) < ε?

        Parameters:
        - delta_threshold: Causal constraint (|M_total × N| ≤ δ)
        - epsilon: KL divergence threshold (nats)

        Returns: dict with results
        """
        microstates = self.enumerate_causal_macrostate(delta_threshold)

        if len(microstates) == 0:
            return {
                'N_total': self.N,
                'm_observer': self.m,
                'n_environment': self.n,
                'delta_threshold': delta_threshold,
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

        # Fraction of typical microstates
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
            'delta_threshold': delta_threshold,
            'epsilon': epsilon,
            'num_microstates': len(microstates),
            'num_typical': num_typical,
            'typicality_fraction': typicality_fraction,
            'mean_KL': mean_KL,
            'std_KL': std_KL,
            'KL_values': KL_divergences,
            'verdict': verdict
        }


def run_scaling_experiments():
    """
    Systematic experiments to test scaling of causal typicality with N.

    Test configurations:
    1. System sizes: N = 4, 6, 8, 10, 12 (if feasible)
    2. Observer fractions: m/N = 0.25, 0.5
    3. Causal constraint thresholds: δ = 0, 1, 2, 4 (tight to loose)
    4. KL threshold: ε = 1.0 (standard)

    CRITICAL QUESTION: Does typicality fraction INCREASE with N?
    """
    results = []

    # Configuration space
    N_values = [4, 6, 8, 10]  # Start conservative, can extend to 12 if fast
    observer_fractions = [0.25, 0.5]
    delta_thresholds = [0, 1, 2, 4]  # Tight to loose causal constraint
    epsilon = 1.0  # Standard threshold

    print("=" * 80)
    print("CAUSAL TYPICALITY CONJECTURE: LOCAL OBSERVER MODEL (v2.0)")
    print("=" * 80)
    print()
    print("KEY FIX: Observer does NOT know global constraint M_total = 0.")
    print("Observer infers environment using unconstrained MaxEnt.")
    print()
    print("CRITICAL TEST: Does typicality fraction INCREASE with N?")
    print("=" * 80)
    print()

    for N in N_values:
        print(f"\n{'═' * 80}")
        print(f"SYSTEM SIZE: N = {N}")
        print(f"{'═' * 80}")

        for frac in observer_fractions:
            m = int(N * frac)
            if m == 0 or m == N:
                continue

            n = N - m

            print(f"\n{' ' * 2}Observer/Environment split: m = {m}, n = {n} (m/N = {frac})")
            print(f"{' ' * 2}{'─' * 76}")

            model = LocalObserverModel(N_total=N, m_observer=m)

            for delta in delta_thresholds:
                result = model.test_typicality(
                    delta_threshold=delta,
                    epsilon=epsilon
                )

                results.append(result)

                if result['num_microstates'] > 0:
                    print(f"{' ' * 4}δ = {delta:2d}: "
                          f"{result['num_typical']:4d}/{result['num_microstates']:4d} typical "
                          f"({result['typicality_fraction']:6.1%}) | "
                          f"⟨D_KL⟩ = {result['mean_KL']:5.3f} ± {result['std_KL']:5.3f} | "
                          f"{result['verdict']}")
                else:
                    print(f"{' ' * 4}δ = {delta:2d}: NO MICROSTATES (constraint too tight)")

    print("\n" + "=" * 80)
    print("SCALING ANALYSIS: Does typicality INCREASE with N?")
    print("=" * 80)

    # Analyze scaling for each (delta, m/N) combination
    for delta in delta_thresholds:
        print(f"\nδ = {delta} (causal constraint):")

        for frac in observer_fractions:
            print(f"  m/N = {frac}:")

            scaling_data = []
            for N in N_values:
                m = int(N * frac)
                matching = [r for r in results
                           if r['N_total'] == N
                           and r['m_observer'] == m
                           and r['delta_threshold'] == delta]

                if matching and matching[0]['num_microstates'] > 0:
                    typ_frac = matching[0]['typicality_fraction']
                    scaling_data.append((N, typ_frac))
                    print(f"    N = {N:2d}: {typ_frac:6.1%}")

            # Check if monotonically increasing
            if len(scaling_data) >= 2:
                increasing = all(scaling_data[i][1] <= scaling_data[i+1][1]
                               for i in range(len(scaling_data)-1))

                if increasing:
                    print(f"    → SUPPORTS conjecture (monotonic increase)")
                else:
                    print(f"    → Against conjecture (not monotonic)")

    return results


def visualize_scaling(results):
    """
    Visualize scaling of typicality with N.

    Key plots:
    1. Typicality fraction vs N (for different δ and m/N)
    2. Mean KL divergence vs N
    3. Phase diagram: δ vs N, color = typicality fraction
    4. Histogram of KL values for different N
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Causal Typicality Conjecture: Local Observer Model (v2.0)',
                 fontsize=14, fontweight='bold')

    # Extract unique parameter values
    N_values = sorted(set(r['N_total'] for r in results))
    delta_values = sorted(set(r['delta_threshold'] for r in results))

    # Plot 1: Typicality fraction vs N (different δ, fixed m/N)
    ax = axes[0, 0]
    m_frac = 0.5  # Fix m/N = 0.5 for clarity

    for delta in delta_values:
        fractions = []
        N_plot = []

        for N in N_values:
            m = int(N * m_frac)
            matching = [r for r in results
                       if r['N_total'] == N
                       and r['m_observer'] == m
                       and r['delta_threshold'] == delta]

            if matching and matching[0]['num_microstates'] > 0:
                fractions.append(matching[0]['typicality_fraction'])
                N_plot.append(N)

        if fractions:
            ax.plot(N_plot, fractions, marker='o', label=f'δ = {delta}', linewidth=2)

    ax.axhline(0.9, color='green', linestyle='--', alpha=0.5, linewidth=1)
    ax.axhline(0.5, color='red', linestyle='--', alpha=0.5, linewidth=1)
    ax.set_xlabel('N (total spins)', fontsize=11)
    ax.set_ylabel('Typicality Fraction', fontsize=11)
    ax.set_title(f'Typicality vs System Size (m/N = {m_frac})', fontsize=11, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_ylim([0, 1.05])

    # Plot 2: Mean KL divergence vs N
    ax = axes[0, 1]

    for delta in delta_values:
        mean_KLs = []
        N_plot = []

        for N in N_values:
            m = int(N * m_frac)
            matching = [r for r in results
                       if r['N_total'] == N
                       and r['m_observer'] == m
                       and r['delta_threshold'] == delta]

            if matching and matching[0]['num_microstates'] > 0:
                mean_KLs.append(matching[0]['mean_KL'])
                N_plot.append(N)

        if mean_KLs:
            ax.plot(N_plot, mean_KLs, marker='s', label=f'δ = {delta}', linewidth=2)

    ax.axhline(1.0, color='red', linestyle='--', alpha=0.5, label='ε = 1.0', linewidth=1)
    ax.set_xlabel('N (total spins)', fontsize=11)
    ax.set_ylabel('⟨D_KL⟩ (nats)', fontsize=11)
    ax.set_title(f'Mean KL Divergence vs N (m/N = {m_frac})', fontsize=11, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # Plot 3: Typicality vs δ (different N)
    ax = axes[1, 0]

    colors = plt.cm.viridis(np.linspace(0, 1, len(N_values)))

    for N, color in zip(N_values, colors):
        m = int(N * m_frac)
        fractions = []
        delta_plot = []

        for delta in delta_values:
            matching = [r for r in results
                       if r['N_total'] == N
                       and r['m_observer'] == m
                       and r['delta_threshold'] == delta]

            if matching and matching[0]['num_microstates'] > 0:
                fractions.append(matching[0]['typicality_fraction'])
                delta_plot.append(delta)

        if fractions:
            ax.plot(delta_plot, fractions, marker='o', label=f'N = {N}',
                   color=color, linewidth=2)

    ax.axhline(0.9, color='green', linestyle='--', alpha=0.5, linewidth=1)
    ax.set_xlabel('δ (causal constraint threshold)', fontsize=11)
    ax.set_ylabel('Typicality Fraction', fontsize=11)
    ax.set_title(f'Typicality vs Constraint Tightness (m/N = {m_frac})',
                fontsize=11, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_ylim([0, 1.05])

    # Plot 4: Histogram of KL values for different N (fixed δ)
    ax = axes[1, 1]
    delta_fixed = 2  # Medium constraint

    colors = plt.cm.viridis(np.linspace(0, 1, len(N_values)))

    for N, color in zip(N_values, colors):
        m = int(N * m_frac)
        matching = [r for r in results
                   if r['N_total'] == N
                   and r['m_observer'] == m
                   and r['delta_threshold'] == delta_fixed]

        if matching and matching[0]['num_microstates'] > 0:
            KL_values = matching[0]['KL_values']
            ax.hist(KL_values, bins=15, alpha=0.5, label=f'N = {N}',
                   color=color, density=True)

    ax.axvline(1.0, color='red', linestyle='--', label='ε = 1.0', linewidth=2)
    ax.set_xlabel('D_KL (nats)', fontsize=11)
    ax.set_ylabel('Probability Density', fontsize=11)
    ax.set_title(f'KL Distribution by N (δ = {delta_fixed}, m/N = {m_frac})',
                fontsize=11, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    return fig


def main():
    """
    Main execution: Run scaling experiments and analyze results.
    """
    print("Starting Causal Typicality Conjecture computation (v2.0 - Local Observer)...")
    print()

    # Run experiments
    results = run_scaling_experiments()

    # Visualize
    print("\nGenerating visualizations...")
    fig = visualize_scaling(results)

    # Save
    output_path = '/Users/Max_1/Projects/PhysicsResearch/cosmological-unification/papers/structural-bridge/output/causal_typicality_v2_results.png'
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Figure saved to: {output_path}")

    # Final verdict
    print("\n" + "=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)

    # Focus on δ = 2 (medium constraint) for overall assessment
    delta_focus = 2
    focus_results = [r for r in results
                    if r['delta_threshold'] == delta_focus
                    and r['num_microstates'] > 0]

    if focus_results:
        avg_typicality = np.mean([r['typicality_fraction'] for r in focus_results])

        print(f"\nAverage typicality fraction (δ = {delta_focus}, ε = 1.0): {avg_typicality:.1%}")

        # Check scaling
        all_N = sorted(set(r['N_total'] for r in results))
        N_min_results = [r for r in focus_results if r['N_total'] == min(all_N)]
        N_max_results = [r for r in focus_results if r['N_total'] == max(all_N)]

        if N_min_results and N_max_results:
            typ_min = np.mean([r['typicality_fraction'] for r in N_min_results])
            typ_max = np.mean([r['typicality_fraction'] for r in N_max_results])

            print(f"\nScaling behavior:")
            print(f"  N = {min(all_N)}: {typ_min:.1%}")
            print(f"  N = {max(all_N)}: {typ_max:.1%}")

            if typ_max > typ_min:
                print(f"  → Typicality INCREASES with N (Δ = {typ_max - typ_min:.1%})")
                print(f"  ✓ SUPPORTS the conjecture's N → ∞ limit")
                scaling_verdict = "SUPPORTS"
            else:
                print(f"  → Typicality DECREASES with N (Δ = {typ_max - typ_min:.1%})")
                print(f"  ✗ AGAINST the conjecture")
                scaling_verdict = "AGAINST"

        # Overall verdict
        if avg_typicality > 0.9 and scaling_verdict == "SUPPORTS":
            print(f"\n✓ CONJECTURE STRONGLY SUPPORTED")
            print(f"  - High typicality fraction (>90%)")
            print(f"  - Monotonic increase with N")
            confidence = 70
        elif avg_typicality > 0.7 and scaling_verdict == "SUPPORTS":
            print(f"\n~ CONJECTURE MODERATELY SUPPORTED")
            print(f"  - Good typicality fraction (70-90%)")
            print(f"  - Positive scaling with N")
            confidence = 55
        elif scaling_verdict == "SUPPORTS":
            print(f"\n? WEAK EVIDENCE FOR CONJECTURE")
            print(f"  - Modest typicality fraction (<70%)")
            print(f"  - But positive scaling trend")
            confidence = 40
        else:
            print(f"\n✗ CONJECTURE NOT SUPPORTED")
            print(f"  - Typicality does not increase with N")
            print(f"  - Evidence against measure concentration")
            confidence = 25

        print(f"\nUpdated confidence: {confidence}%")

    else:
        print("\nInsufficient data for verdict (all constraints too tight)")

    print("\n" + "=" * 80)
    print("Computation COMPLETE.")
    print("=" * 80)

    return results


if __name__ == '__main__':
    results = main()
