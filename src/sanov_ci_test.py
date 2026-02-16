#!/usr/bin/env python3
"""
Sanov CI Test: Testing MaxEnt Emergence via Large Deviations in Multiway Systems

This script tests the Sanov route to MaxEnt: IF multiway branches provide
effectively independent samples, THEN MaxEnt should emerge via large deviations
concentration (Sanov's theorem).

Key Tests:
1. Correlation decay: Does inter-branch correlation decrease with depth?
2. KL convergence: Does KL(empirical || MaxEnt) decrease with number of branches?
3. Mixing effect: Do more independent branches converge faster to MaxEnt?

Model: Simplified binary tree branching (not full Wolfram hypergraph, but
captures the essential structure: exponential branching + local interactions).

Expected Result:
- IF Sanov mechanism active: exponential correlation decay + exponential KL convergence
- IF not active: constant correlation + no KL convergence
"""

import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp
from itertools import product
import matplotlib.pyplot as plt
from pathlib import Path
import json
from typing import Tuple, List, Dict

# Set random seed for reproducibility
np.random.seed(42)


class BinaryTreeSystem:
    """
    Simplified multiway system with binary tree branching.

    At each depth d, system evolves to 2^d branches. Each branch has a local
    state (binary string) that evolves via local rules + optional mixing.
    """

    def __init__(self, L: int, mixing_alpha: float = 0.3):
        """
        Args:
            L: System size (binary string length)
            mixing_alpha: Mixing parameter in [0,1].
                          0 = independent branches, 1 = fully correlated
        """
        self.L = L
        self.mixing_alpha = mixing_alpha

    def initial_state(self) -> np.ndarray:
        """Random initial binary state."""
        return np.random.randint(0, 2, self.L)

    def evolve_branch(self, parent_state: np.ndarray, branch_index: int,
                     depth: int, total_depth: int) -> np.ndarray:
        """
        Evolve a single branch from parent state.

        Args:
            parent_state: Parent branch state
            branch_index: Index of this branch (0 to 2^depth - 1)
            depth: Current depth
            total_depth: Target depth

        Returns:
            Final state after evolution
        """
        state = parent_state.copy()

        # Apply local update based on branch_index (encodes path in binary tree)
        # Extract bits of branch_index to determine which positions to flip
        for d in range(depth, total_depth):
            bit = (branch_index >> d) & 1

            # Local update: flip positions based on bit
            # Add mixing: some dependence on parent state
            if bit == 1:
                # Flip first half (plus mixing from parent)
                flip_positions = np.random.rand(self.L // 2) > self.mixing_alpha
                state[:self.L // 2][flip_positions] = 1 - state[:self.L // 2][flip_positions]
            else:
                # Flip second half (plus mixing from parent)
                flip_positions = np.random.rand(self.L // 2) > self.mixing_alpha
                state[self.L // 2:][flip_positions] = 1 - state[self.L // 2:][flip_positions]

            # Add noise to simulate stochastic dynamics
            noise_positions = np.random.rand(self.L) < 0.1 * (1 - self.mixing_alpha)
            state[noise_positions] = 1 - state[noise_positions]

        return state

    def generate_branches(self, depth: int) -> np.ndarray:
        """
        Generate all branches at given depth.

        Args:
            depth: Depth of binary tree (number of branches = 2^depth)

        Returns:
            Array of shape (2^depth, L) with branch states
        """
        num_branches = 2 ** depth
        initial = self.initial_state()

        branches = np.zeros((num_branches, self.L), dtype=int)
        for i in range(num_branches):
            branches[i] = self.evolve_branch(initial, i, 0, depth)

        return branches


def local_statistics(branches: np.ndarray, window_start: int,
                     window_size: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extract local observer statistics from branches.

    Observer sees a window of consecutive bits and measures mean + variance.

    Args:
        branches: Array of shape (num_branches, L)
        window_start: Start position of observer window
        window_size: Size of observer window

    Returns:
        (patterns, counts) where patterns is (num_patterns, window_size)
        and counts is (num_patterns,) with frequency of each pattern
    """
    windows = branches[:, window_start:window_start+window_size]

    # Convert binary patterns to integers for counting
    pattern_ints = windows @ (2 ** np.arange(window_size))
    unique_ints, counts = np.unique(pattern_ints, return_counts=True)

    # Convert back to binary
    patterns = np.array([
        [(i >> bit) & 1 for bit in range(window_size)]
        for i in unique_ints
    ])

    return patterns, counts


def empirical_distribution(branches: np.ndarray, window_start: int,
                           window_size: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute empirical distribution over observer window.

    Returns:
        (all_patterns, p_empirical) where all_patterns is (2^w, w) and
        p_empirical is (2^w,) with probability of each pattern
    """
    patterns, counts = local_statistics(branches, window_start, window_size)

    # Build full distribution over all possible patterns
    all_patterns = np.array(list(product([0, 1], repeat=window_size)))
    p_emp = np.zeros(len(all_patterns))

    # Convert patterns to integers for matching
    obs_ints = patterns @ (2 ** np.arange(window_size))
    all_ints = all_patterns @ (2 ** np.arange(window_size))

    for i, pattern_int in enumerate(obs_ints):
        idx = np.where(all_ints == pattern_int)[0][0]
        p_emp[idx] = counts[i]

    p_emp /= p_emp.sum()

    return all_patterns, p_emp


def maxent_distribution(observed_means: np.ndarray,
                        window_size: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute MaxEnt distribution matching observed means (canonical exponential family).

    Args:
        observed_means: Mean of each bit position (length w)
        window_size: Size of window

    Returns:
        (all_patterns, p_maxent)
    """
    all_patterns = np.array(list(product([0, 1], repeat=window_size)))

    # Minimize KL divergence by matching moments
    def neg_entropy_objective(lambdas):
        logits = all_patterns @ lambdas
        log_Z = logsumexp(logits)
        return log_Z - lambdas @ observed_means

    # Optimize
    result = minimize(neg_entropy_objective, np.zeros(window_size), method='BFGS')
    lambdas = result.x

    # Compute MaxEnt distribution
    logits = all_patterns @ lambdas
    log_Z = logsumexp(logits)
    p_maxent = np.exp(logits - log_Z)

    return all_patterns, p_maxent


def kl_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """KL(p || q), handling zeros."""
    mask = p > 0
    return np.sum(p[mask] * np.log(p[mask] / np.maximum(q[mask], 1e-30)))


def branch_correlation(branches: np.ndarray, window_start: int,
                       window_size: int) -> float:
    """
    Compute average correlation between branch statistics.

    Returns:
        Average pairwise correlation coefficient
    """
    windows = branches[:, window_start:window_start+window_size]

    # Compute means for each branch
    means = windows.mean(axis=1)

    # Pairwise correlations
    num_branches = len(branches)
    if num_branches < 2:
        return 0.0

    correlations = []
    for i in range(min(100, num_branches)):  # Sample to avoid O(N^2)
        for j in range(i+1, min(100, num_branches)):
            corr = np.corrcoef(windows[i], windows[j])[0, 1]
            if not np.isnan(corr):
                correlations.append(corr)

    return np.mean(np.abs(correlations)) if correlations else 0.0


def test_correlation_decay(L: int = 16, window_size: int = 4,
                           depths: List[int] = None,
                           mixing_alpha: float = 0.3) -> Dict:
    """
    Test 1: Does correlation decay with depth?

    Prediction: C(d) ~ exp(-alpha * d) if branches become independent.
    """
    if depths is None:
        depths = [5, 7, 9, 11, 13]

    results = []

    print(f"\n{'='*70}")
    print(f"TEST 1: CORRELATION DECAY (mixing_alpha={mixing_alpha})")
    print(f"{'='*70}")
    print(f"{'Depth':>6} {'Branches':>12} {'Avg Corr':>12} {'KL to MaxEnt':>15}")
    print(f"{'-'*70}")

    for depth in depths:
        system = BinaryTreeSystem(L, mixing_alpha)
        branches = system.generate_branches(depth)

        window_start = L // 2 - window_size // 2

        # Correlation
        corr = branch_correlation(branches, window_start, window_size)

        # KL divergence
        all_patterns, p_emp = empirical_distribution(branches, window_start, window_size)
        observed_means = (branches[:, window_start:window_start+window_size]).mean(axis=0)
        _, p_maxent = maxent_distribution(observed_means, window_size)

        kl = kl_divergence(p_emp, p_maxent)

        num_branches = 2 ** depth
        print(f"{depth:>6} {num_branches:>12} {corr:>12.4f} {kl:>15.6f}")

        results.append({
            'depth': depth,
            'num_branches': num_branches,
            'correlation': corr,
            'kl_divergence': kl
        })

    return results


def test_mixing_effect(L: int = 16, window_size: int = 4, depth: int = 10,
                       mixing_alphas: List[float] = None) -> Dict:
    """
    Test 2: Does more independence (lower mixing) give faster MaxEnt convergence?

    Prediction: KL should decrease with mixing_alpha.
    """
    if mixing_alphas is None:
        mixing_alphas = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

    results = []

    print(f"\n{'='*70}")
    print(f"TEST 2: MIXING EFFECT (depth={depth})")
    print(f"{'='*70}")
    print(f"{'Mixing α':>10} {'Avg Corr':>12} {'KL to MaxEnt':>15} {'Convergence':>15}")
    print(f"{'-'*70}")

    for alpha in mixing_alphas:
        system = BinaryTreeSystem(L, alpha)
        branches = system.generate_branches(depth)

        window_start = L // 2 - window_size // 2

        # Correlation
        corr = branch_correlation(branches, window_start, window_size)

        # KL divergence
        all_patterns, p_emp = empirical_distribution(branches, window_start, window_size)
        observed_means = (branches[:, window_start:window_start+window_size]).mean(axis=0)
        _, p_maxent = maxent_distribution(observed_means, window_size)

        kl = kl_divergence(p_emp, p_maxent)

        # Convergence quality (relative to alpha=1.0 baseline)
        baseline_kl = results[0]['kl_divergence'] if results else kl
        improvement = (baseline_kl - kl) / baseline_kl if baseline_kl > 0 else 0

        status = "✓" if kl < 0.1 else ("~" if kl < 0.2 else "✗")
        print(f"{alpha:>10.2f} {corr:>12.4f} {kl:>15.6f} {status:>15}")

        results.append({
            'mixing_alpha': alpha,
            'correlation': corr,
            'kl_divergence': kl,
            'improvement': improvement
        })

    return results


def test_convergence_rate(L: int = 16, window_size: int = 4,
                          depths: List[int] = None,
                          mixing_alpha: float = 0.3) -> Dict:
    """
    Test 3: Quantify convergence rate.

    Fit: KL(d) = A * exp(-lambda * d) + C
    """
    if depths is None:
        depths = list(range(5, 16))

    results = test_correlation_decay(L, window_size, depths, mixing_alpha)

    # Fit exponential decay
    depths_arr = np.array([r['depth'] for r in results])
    kl_arr = np.array([r['kl_divergence'] for r in results])
    corr_arr = np.array([r['correlation'] for r in results])

    # Log-linear fit: log(KL) = log(A) - lambda * d + log(C)
    # Simplified: fit log(KL - C) where C is minimum KL
    C_kl = kl_arr.min() if kl_arr.min() > 0 else 1e-6
    C_corr = corr_arr.min() if corr_arr.min() > 0 else 1e-6

    # Fit KL decay rate
    log_kl = np.log(kl_arr - C_kl + 1e-9)
    kl_fit = np.polyfit(depths_arr, log_kl, 1)
    lambda_kl = -kl_fit[0]

    # Fit correlation decay rate
    log_corr = np.log(corr_arr - C_corr + 1e-9)
    corr_fit = np.polyfit(depths_arr, log_corr, 1)
    lambda_corr = -corr_fit[0]

    print(f"\n{'='*70}")
    print(f"TEST 3: CONVERGENCE RATE ANALYSIS")
    print(f"{'='*70}")
    print(f"KL divergence decay:    λ = {lambda_kl:.4f} (KL ~ exp(-{lambda_kl:.3f} * d))")
    print(f"Correlation decay:      λ = {lambda_corr:.4f} (C ~ exp(-{lambda_corr:.3f} * d))")
    print(f"Asymptotic KL floor:    {C_kl:.6f}")
    print(f"Asymptotic Corr floor:  {C_corr:.6f}")

    # Verdict
    print(f"\n{'='*70}")
    print(f"VERDICT:")
    print(f"{'='*70}")

    if lambda_kl > 0.2 and lambda_corr > 0.2:
        verdict = "POSITIVE: Exponential decay observed (Sanov mechanism active)"
        confidence = "HIGH (λ > 0.2 for both KL and correlation)"
    elif lambda_kl > 0.1 and lambda_corr > 0.1:
        verdict = "WEAK POSITIVE: Decay observed but slow"
        confidence = "MODERATE (λ > 0.1)"
    else:
        verdict = "NEGATIVE: No significant decay"
        confidence = "LOW (λ < 0.1)"

    print(verdict)
    print(confidence)

    return {
        'results': results,
        'lambda_kl': lambda_kl,
        'lambda_corr': lambda_corr,
        'C_kl': C_kl,
        'C_corr': C_corr,
        'verdict': verdict,
        'confidence': confidence
    }


def generate_plots(test1_results: List[Dict], test2_results: List[Dict],
                   test3_results: Dict, output_dir: Path):
    """Generate visualization plots."""

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Plot 1: Correlation vs Depth
    ax = axes[0, 0]
    depths = [r['depth'] for r in test1_results]
    corrs = [r['correlation'] for r in test1_results]

    ax.plot(depths, corrs, 'o-', linewidth=2, markersize=8, label='Observed')

    # Fit exponential
    lambda_corr = test3_results['lambda_corr']
    C_corr = test3_results['C_corr']
    depths_fit = np.linspace(min(depths), max(depths), 100)
    corr_fit = np.exp(-(lambda_corr * depths_fit)) + C_corr
    ax.plot(depths_fit, corr_fit, '--', color='red', linewidth=1.5,
            label=f'Fit: exp(-{lambda_corr:.2f}*d)')

    ax.set_xlabel('Depth d', fontsize=12)
    ax.set_ylabel('Avg Correlation', fontsize=12)
    ax.set_title('Test 1: Correlation Decay with Depth', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_yscale('log')

    # Plot 2: KL vs Depth
    ax = axes[0, 1]
    kls = [r['kl_divergence'] for r in test1_results]

    ax.plot(depths, kls, 's-', linewidth=2, markersize=8, label='Observed', color='green')

    # Fit exponential
    lambda_kl = test3_results['lambda_kl']
    C_kl = test3_results['C_kl']
    kl_fit = np.exp(-(lambda_kl * depths_fit)) + C_kl
    ax.plot(depths_fit, kl_fit, '--', color='red', linewidth=1.5,
            label=f'Fit: exp(-{lambda_kl:.2f}*d)')

    ax.set_xlabel('Depth d', fontsize=12)
    ax.set_ylabel('KL(empirical || MaxEnt)', fontsize=12)
    ax.set_title('Test 1: KL Convergence to MaxEnt', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_yscale('log')

    # Plot 3: Mixing Effect
    ax = axes[1, 0]
    alphas = [r['mixing_alpha'] for r in test2_results]
    kls_mix = [r['kl_divergence'] for r in test2_results]

    ax.plot(alphas, kls_mix, 'o-', linewidth=2, markersize=8, color='purple')
    ax.axhline(0.1, color='red', linestyle='--', linewidth=1, label='Target: KL < 0.1')

    ax.set_xlabel('Mixing α (0=independent, 1=correlated)', fontsize=12)
    ax.set_ylabel('KL(empirical || MaxEnt)', fontsize=12)
    ax.set_title('Test 2: Mixing Effect on MaxEnt Convergence', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # Plot 4: Correlation vs KL (scatter)
    ax = axes[1, 1]
    all_corrs = [r['correlation'] for r in test1_results]
    all_kls = [r['kl_divergence'] for r in test1_results]

    ax.scatter(all_corrs, all_kls, s=100, alpha=0.6, c=depths, cmap='viridis')

    # Add trend line
    z = np.polyfit(all_corrs, all_kls, 1)
    p = np.poly1d(z)
    corr_range = np.linspace(min(all_corrs), max(all_corrs), 100)
    ax.plot(corr_range, p(corr_range), "r--", alpha=0.5, linewidth=2, label='Linear fit')

    ax.set_xlabel('Correlation', fontsize=12)
    ax.set_ylabel('KL Divergence', fontsize=12)
    ax.set_title('Correlation vs KL (color = depth)', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    cbar = plt.colorbar(ax.collections[0], ax=ax)
    cbar.set_label('Depth', fontsize=10)

    plt.tight_layout()

    plot_path = output_dir / "sanov_ci_test_results.png"
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    print(f"\nPlot saved to: {plot_path}")
    plt.close()


def main():
    """Main execution."""
    print("=" * 70)
    print("SANOV CI TEST: MaxEnt Emergence via Large Deviations")
    print("=" * 70)
    print("\nTesting whether multiway branches provide effective independence")
    print("such that Sanov's theorem drives MaxEnt emergence.")
    print()

    # Configuration
    L = 16
    window_size = 4
    mixing_alpha_default = 0.3

    # Test 1: Correlation decay
    depths_test1 = [5, 7, 9, 11, 13]
    test1_results = test_correlation_decay(L, window_size, depths_test1, mixing_alpha_default)

    # Test 2: Mixing effect
    mixing_alphas = [0.0, 0.2, 0.4, 0.6, 0.8]
    test2_results = test_mixing_effect(L, window_size, depth=10, mixing_alphas=mixing_alphas)

    # Test 3: Convergence rate analysis
    depths_test3 = list(range(5, 14))
    test3_results = test_convergence_rate(L, window_size, depths_test3, mixing_alpha_default)

    # Save results
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    results_dict = {
        'test1_correlation_decay': test1_results,
        'test2_mixing_effect': test2_results,
        'test3_convergence_analysis': {
            'lambda_kl': test3_results['lambda_kl'],
            'lambda_corr': test3_results['lambda_corr'],
            'C_kl': test3_results['C_kl'],
            'C_corr': test3_results['C_corr'],
            'verdict': test3_results['verdict'],
            'confidence': test3_results['confidence']
        },
        'configuration': {
            'L': L,
            'window_size': window_size,
            'mixing_alpha_default': mixing_alpha_default,
            'depths_test1': depths_test1,
            'depths_test3': depths_test3,
            'mixing_alphas': mixing_alphas
        }
    }

    json_path = output_dir / "sanov_ci_test_results.json"
    with open(json_path, 'w') as f:
        json.dump(results_dict, f, indent=2)

    print(f"\nResults saved to: {json_path}")

    # Generate plots
    generate_plots(test1_results, test2_results, test3_results, output_dir)

    # Final summary
    print(f"\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"Model: Binary tree branching (L={L}, window={window_size})")
    print(f"Mixing: α={mixing_alpha_default} (0=independent, 1=correlated)")
    print()
    print(f"KL decay rate:     λ = {test3_results['lambda_kl']:.4f}")
    print(f"Corr decay rate:   λ = {test3_results['lambda_corr']:.4f}")
    print()
    print(f"Verdict: {test3_results['verdict']}")
    print(f"Confidence: {test3_results['confidence']}")
    print()
    print("Interpretation:")
    print("  IF λ > 0.2: Strong evidence for Sanov mechanism (exponential convergence)")
    print("  IF 0.1 < λ < 0.2: Weak evidence (slow convergence)")
    print("  IF λ < 0.1: No evidence (no convergence)")
    print()

    if test3_results['lambda_kl'] > 0.2 and test3_results['lambda_corr'] > 0.2:
        print("✓ POSITIVE RESULT: Binary tree model shows Sanov mechanism.")
        print("  → Branches become effectively independent with depth")
        print("  → MaxEnt emerges via large deviations concentration")
        print("  → Supports Sanov route to closing CI → ExpFamily gap")
        print()
        print("  Caveat: This is a simplified toy model, not full Wolfram hypergraphs.")
        print("  Full verification requires Wolfram Physics Project implementation.")
    else:
        print("✗ NEGATIVE RESULT: No clear Sanov mechanism in this model.")
        print("  → Either model is too simple or mixing is too strong")
        print("  → Does NOT support Sanov route")

    print()
    print("=" * 70)
    print("COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
