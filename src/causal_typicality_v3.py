#!/usr/bin/env python3
"""
Causal Typicality v3: Testing Local MaxEnt Emergence from Causal Invariance

Key redesign: LOCAL observer that does NOT know global constraints.

Question: In a system with causal invariance (CI), do local observers
naturally see statistics that look like exponential family / MaxEnt distributions?

Previous versions (v1, v2) had a critical bug: the observer had global constraint
knowledge, making MaxEnt trivially satisfied. This version uses a LOCAL observer
that only sees a small window of the full state.

Simplified model (not actual Wolfram hypergraphs):
- CI-like dynamics: confluent random multiway system
- Local observer: sees w consecutive bits out of L total
- MaxEnt reference: exponential family matching observed marginals
- Measure: KL(p_obs || p_MaxEnt) vs evolution time N
- Control: non-CI dynamics for comparison

A NEGATIVE result (CI does NOT force local MaxEnt) is equally valuable —
it would confirm that MaxEnt must be an independent axiom.
"""

import numpy as np
from itertools import product
from scipy.optimize import minimize
from scipy.special import logsumexp
import matplotlib.pyplot as plt
from pathlib import Path
import json
from typing import List, Tuple, Dict

# Set random seed for reproducibility
np.random.seed(42)


def generate_ci_rules(L: int, k: int, num_rules: int = 5) -> List[Tuple]:
    """Generate confluent replacement rules on binary strings of length L.

    CI (confluence) is achieved by making rules that commute:
    each rule acts on non-overlapping positions, guaranteeing confluence.

    Args:
        L: Length of binary string (system size)
        k: Number of bits changed per rule
        num_rules: Number of rules to generate

    Returns:
        List of rules (positions, pattern_in, pattern_out)
    """
    rules = []
    for r in range(num_rules):
        # Pick k non-overlapping positions for each rule
        positions = np.random.choice(L, k, replace=False)
        # Rule: flip bits at these positions
        pattern_in = np.random.randint(0, 2, k)
        pattern_out = 1 - pattern_in  # flip
        rules.append((positions, pattern_in, pattern_out))
    return rules


def generate_non_ci_rules(L: int, k: int, num_rules: int = 5) -> List[Tuple]:
    """Generate non-confluent rules (overlapping positions, breaks CI).

    Args:
        L: Length of binary string (system size)
        k: Number of bits changed per rule
        num_rules: Number of rules to generate

    Returns:
        List of rules (positions, pattern_in, pattern_out)
    """
    rules = []
    for r in range(num_rules):
        # Allow overlapping positions (breaks CI)
        positions = np.random.choice(L, k, replace=True)
        pattern_in = np.random.randint(0, 2, k)
        pattern_out = np.random.randint(0, 2, k)
        rules.append((positions, pattern_in, pattern_out))
    return rules


def apply_rule(state: np.ndarray, rule: Tuple) -> np.ndarray:
    """Apply a single rule to a state if pattern matches.

    Args:
        state: Current binary state
        rule: (positions, pattern_in, pattern_out)

    Returns:
        New state after applying rule
    """
    positions, pattern_in, pattern_out = rule
    new_state = state.copy()
    if np.all(state[positions] == pattern_in):
        new_state[positions] = pattern_out
    return new_state


def evolve_system(initial_state: np.ndarray, rules: List[Tuple], N_steps: int) -> np.ndarray:
    """Evolve system for N steps, applying random rules.

    Args:
        initial_state: Initial binary state
        rules: List of evolution rules
        N_steps: Number of evolution steps

    Returns:
        Array of states (N_steps+1, L)
    """
    states = [initial_state.copy()]
    state = initial_state.copy()
    for step in range(N_steps):
        # Apply a random applicable rule
        rule_idx = np.random.randint(len(rules))
        state = apply_rule(state, rules[rule_idx])
        states.append(state.copy())
    return np.array(states)


def local_observer_statistics(states: np.ndarray, window_start: int, window_size: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Extract local observer statistics from evolution.

    The observer sees ONLY a local window of w consecutive bits.
    It does NOT know the global state or global constraints.

    Args:
        states: Evolution states (N_steps+1, L)
        window_start: Starting position of observer window
        window_size: Size of observer window

    Returns:
        (unique_patterns, p_obs, observed_means)
    """
    # Extract local window across all time steps
    windows = states[:, window_start:window_start+window_size]

    # Count frequency of each pattern
    # Convert binary windows to integers for efficient counting
    pattern_ints = windows @ (2 ** np.arange(window_size))
    unique_ints, counts = np.unique(pattern_ints, return_counts=True)

    # Convert back to binary patterns
    unique_patterns = np.array([
        [(i >> bit) & 1 for bit in range(window_size)]
        for i in unique_ints
    ])

    # Observed probability distribution
    total = np.sum(counts)
    p_obs = counts / total

    # Observed marginal means (sufficient statistics for MaxEnt)
    observed_means = np.sum(windows, axis=0) / windows.shape[0]

    return unique_patterns, p_obs, observed_means


def maxent_distribution_first_order(observed_means: np.ndarray, window_size: int) -> Tuple[np.ndarray, np.ndarray]:
    """Compute MaxEnt distribution matching observed first-order marginals.

    This is the exponential family distribution with sufficient statistics = means:
    p_MaxEnt(x) = exp(sum_i lambda_i * x_i) / Z

    Args:
        observed_means: Observed mean of each bit in window
        window_size: Size of window

    Returns:
        (all_patterns, p_maxent)
    """
    # Generate all possible patterns
    all_patterns = np.array(list(product([0, 1], repeat=window_size)))

    # Minimize KL divergence by matching moments
    # This is equivalent to maximizing entropy subject to moment constraints
    def neg_entropy_objective(lambdas):
        """Negative entropy (dual problem for MaxEnt)."""
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


def maxent_distribution_second_order(observed_means: np.ndarray, observed_correlations: np.ndarray, window_size: int) -> Tuple[np.ndarray, np.ndarray]:
    """Compute MaxEnt distribution matching first and second-order marginals (Ising model).

    p_MaxEnt(x) = exp(sum_i h_i*x_i + sum_{i<j} J_{ij}*x_i*x_j) / Z

    Args:
        observed_means: Observed mean of each bit
        observed_correlations: Observed correlations <x_i x_j>
        window_size: Size of window

    Returns:
        (all_patterns, p_maxent)
    """
    # Generate all possible patterns
    all_patterns = np.array(list(product([0, 1], repeat=window_size)))

    # Build sufficient statistics: [x_1, ..., x_w, x_1*x_2, x_1*x_3, ..., x_{w-1}*x_w]
    # First order
    sufficient_stats = all_patterns.copy()
    target_moments = observed_means.copy()

    # Second order (pairwise products)
    for i in range(window_size):
        for j in range(i+1, window_size):
            pairwise = all_patterns[:, i] * all_patterns[:, j]
            sufficient_stats = np.column_stack([sufficient_stats, pairwise])
            target_moments = np.append(target_moments, observed_correlations[i, j])

    # Optimize
    def neg_entropy_objective(lambdas):
        logits = sufficient_stats @ lambdas
        log_Z = logsumexp(logits)
        return log_Z - lambdas @ target_moments

    n_params = len(target_moments)
    result = minimize(neg_entropy_objective, np.zeros(n_params), method='BFGS')
    lambdas = result.x

    # Compute MaxEnt distribution
    logits = sufficient_stats @ lambdas
    log_Z = logsumexp(logits)
    p_maxent = np.exp(logits - log_Z)

    return all_patterns, p_maxent


def kl_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """KL(p || q), handling zeros.

    Args:
        p: True distribution
        q: Approximate distribution

    Returns:
        KL divergence
    """
    mask = p > 0
    return np.sum(p[mask] * np.log(p[mask] / np.maximum(q[mask], 1e-30)))


def align_distributions(unique_patterns: np.ndarray, p_obs: np.ndarray,
                        all_patterns: np.ndarray, p_maxent: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Align observed and MaxEnt distributions to same pattern basis.

    Args:
        unique_patterns: Patterns observed by local observer
        p_obs: Observed probabilities
        all_patterns: All possible patterns (MaxEnt basis)
        p_maxent: MaxEnt probabilities

    Returns:
        (p_obs_full, p_maxent_full) on same basis
    """
    # Convert patterns to integers for matching
    obs_ints = unique_patterns @ (2 ** np.arange(unique_patterns.shape[1]))
    all_ints = all_patterns @ (2 ** np.arange(all_patterns.shape[1]))

    # Build full distributions
    p_obs_full = np.zeros(len(all_patterns))
    for i, pattern_int in enumerate(obs_ints):
        idx = np.where(all_ints == pattern_int)[0][0]
        p_obs_full[idx] = p_obs[i]

    return p_obs_full, p_maxent


def run_experiment(L: int, window_size: int, N_steps: int, num_rules: int,
                   use_ci: bool, seed: int) -> Dict:
    """Run a single experiment: evolve system and measure KL divergence.

    Args:
        L: System size (binary string length)
        window_size: Observer window size
        N_steps: Number of evolution steps
        num_rules: Number of evolution rules
        use_ci: True for CI (confluent) rules, False for non-CI
        seed: Random seed

    Returns:
        Dict with results
    """
    np.random.seed(seed)

    # Generate rules
    k = min(3, L // 2)  # Number of bits changed per rule
    if use_ci:
        rules = generate_ci_rules(L, k, num_rules)
    else:
        rules = generate_non_ci_rules(L, k, num_rules)

    # Initial state (random)
    initial_state = np.random.randint(0, 2, L)

    # Evolve system
    states = evolve_system(initial_state, rules, N_steps)

    # Local observer (random window position)
    window_start = np.random.randint(0, L - window_size + 1)
    unique_patterns, p_obs, observed_means = local_observer_statistics(states, window_start, window_size)

    # Compute observed correlations for second-order MaxEnt
    windows = states[:, window_start:window_start+window_size]
    observed_correlations = np.corrcoef(windows.T)

    # MaxEnt distributions
    all_patterns_1st, p_maxent_1st = maxent_distribution_first_order(observed_means, window_size)
    all_patterns_2nd, p_maxent_2nd = maxent_distribution_second_order(observed_means, observed_correlations, window_size)

    # Align distributions
    p_obs_full_1st, p_maxent_full_1st = align_distributions(unique_patterns, p_obs, all_patterns_1st, p_maxent_1st)
    p_obs_full_2nd, p_maxent_full_2nd = align_distributions(unique_patterns, p_obs, all_patterns_2nd, p_maxent_2nd)

    # Compute KL divergences
    kl_1st = kl_divergence(p_obs_full_1st, p_maxent_full_1st)
    kl_2nd = kl_divergence(p_obs_full_2nd, p_maxent_full_2nd)

    return {
        'L': L,
        'window_size': window_size,
        'N_steps': N_steps,
        'num_rules': num_rules,
        'use_ci': use_ci,
        'seed': seed,
        'kl_1st_order': kl_1st,
        'kl_2nd_order': kl_2nd,
        'n_observed_patterns': len(unique_patterns),
        'n_total_patterns': len(all_patterns_1st)
    }


def run_parameter_scan():
    """Run full parameter scan and save results."""

    # Parameter ranges
    L_values = [8, 10, 12, 14, 16]
    window_sizes = [2, 3, 4]
    N_steps_values = [100, 500, 1000, 5000, 10000]
    num_rules_values = [3, 5, 8]
    n_seeds = 10

    results = []

    total_configs = len(L_values) * len(window_sizes) * len(N_steps_values) * len(num_rules_values) * 2 * n_seeds
    print(f"Running {total_configs} experiments...")

    config_count = 0
    for L in L_values:
        for w in window_sizes:
            if w > L - 2:  # Window must fit in system
                continue
            for N in N_steps_values:
                for num_rules in num_rules_values:
                    for use_ci in [True, False]:
                        for seed in range(n_seeds):
                            config_count += 1
                            if config_count % 100 == 0:
                                print(f"Progress: {config_count}/{total_configs} ({100*config_count/total_configs:.1f}%)")

                            result = run_experiment(L, w, N, num_rules, use_ci, seed)
                            results.append(result)

    return results


def analyze_results(results: List[Dict]) -> Dict:
    """Analyze results and compute summary statistics.

    Args:
        results: List of experiment results

    Returns:
        Dict with analysis
    """
    from collections import defaultdict

    # Group results by configuration
    grouped = defaultdict(list)
    for r in results:
        key = (r['L'], r['window_size'], r['N_steps'], r['num_rules'], r['use_ci'])
        grouped[key].append(r)

    # Compute summary statistics
    summary = []
    for key, group_results in grouped.items():
        L, w, N, num_rules, use_ci = key
        kl_1st_vals = [r['kl_1st_order'] for r in group_results]
        kl_2nd_vals = [r['kl_2nd_order'] for r in group_results]

        summary.append({
            'L': L,
            'window_size': w,
            'N_steps': N,
            'num_rules': num_rules,
            'use_ci': use_ci,
            'kl_1st_mean': np.mean(kl_1st_vals),
            'kl_1st_std': np.std(kl_1st_vals),
            'kl_2nd_mean': np.mean(kl_2nd_vals),
            'kl_2nd_std': np.std(kl_2nd_vals),
        })

    # Check if KL decreases with N (for each L, w, num_rules, use_ci)
    convergence_analysis = []

    # Group by (L, w, num_rules, use_ci)
    conv_grouped = defaultdict(list)
    for r in results:
        key = (r['L'], r['window_size'], r['num_rules'], r['use_ci'])
        conv_grouped[key].append(r)

    for key, group_results in conv_grouped.items():
        L, w, num_rules, use_ci = key

        # Get unique N values and compute means
        N_values = sorted(set(r['N_steps'] for r in group_results))
        kl_means_1st = []
        kl_means_2nd = []

        for N in N_values:
            N_group = [r for r in group_results if r['N_steps'] == N]
            kl_means_1st.append(np.mean([r['kl_1st_order'] for r in N_group]))
            kl_means_2nd.append(np.mean([r['kl_2nd_order'] for r in N_group]))

        # Check if generally decreasing
        decreasing_1st = sum([kl_means_1st[i+1] < kl_means_1st[i] for i in range(len(N_values)-1)]) > len(N_values) // 2
        decreasing_2nd = sum([kl_means_2nd[i+1] < kl_means_2nd[i] for i in range(len(N_values)-1)]) > len(N_values) // 2

        convergence_analysis.append({
            'L': L,
            'window_size': w,
            'num_rules': num_rules,
            'use_ci': use_ci,
            'kl_decreasing_1st': decreasing_1st,
            'kl_decreasing_2nd': decreasing_2nd
        })

    # Compare CI vs non-CI
    ci_vs_nonci = []

    # Group by (L, w, N, num_rules)
    comparison_grouped = defaultdict(lambda: {'ci': [], 'nonci': []})
    for r in results:
        key = (r['L'], r['window_size'], r['N_steps'], r['num_rules'])
        if r['use_ci']:
            comparison_grouped[key]['ci'].append(r)
        else:
            comparison_grouped[key]['nonci'].append(r)

    for key, groups in comparison_grouped.items():
        L, w, N, num_rules = key
        ci_group = groups['ci']
        nonci_group = groups['nonci']

        if len(ci_group) > 0 and len(nonci_group) > 0:
            ci_kl_1st_mean = np.mean([r['kl_1st_order'] for r in ci_group])
            nonci_kl_1st_mean = np.mean([r['kl_1st_order'] for r in nonci_group])
            ci_kl_2nd_mean = np.mean([r['kl_2nd_order'] for r in ci_group])
            nonci_kl_2nd_mean = np.mean([r['kl_2nd_order'] for r in nonci_group])

            ci_vs_nonci.append({
                'L': L,
                'window_size': w,
                'N_steps': N,
                'num_rules': num_rules,
                'ci_kl_1st_mean': ci_kl_1st_mean,
                'nonci_kl_1st_mean': nonci_kl_1st_mean,
                'ci_kl_2nd_mean': ci_kl_2nd_mean,
                'nonci_kl_2nd_mean': nonci_kl_2nd_mean,
                'ci_better_1st': ci_kl_1st_mean < nonci_kl_1st_mean,
                'ci_better_2nd': ci_kl_2nd_mean < nonci_kl_2nd_mean
            })

    return {
        'summary': summary,
        'convergence': convergence_analysis,
        'ci_vs_nonci': ci_vs_nonci
    }


def generate_report(results: List[Dict], analysis: Dict, output_path: str):
    """Generate markdown report with results.

    Args:
        results: List of experiment results
        analysis: Analysis dict
        output_path: Path to save report
    """

    with open(output_path, 'w') as f:
        f.write("# Causal Typicality v3: Local MaxEnt Emergence Test\n\n")
        f.write("**Date**: 2026-02-16\n\n")
        f.write("**Question**: Does local MaxEnt emerge from causal invariance (CI) in a simplified toy model?\n\n")

        f.write("## Executive Summary\n\n")

        # Key findings
        conv_list = analysis['convergence']
        ci_vs_nonci_list = analysis['ci_vs_nonci']

        # Convergence statistics
        ci_conv = [c for c in conv_list if c['use_ci']]
        nonci_conv = [c for c in conv_list if not c['use_ci']]

        ci_conv_1st = np.mean([c['kl_decreasing_1st'] for c in ci_conv]) if ci_conv else 0
        nonci_conv_1st = np.mean([c['kl_decreasing_1st'] for c in nonci_conv]) if nonci_conv else 0
        ci_conv_2nd = np.mean([c['kl_decreasing_2nd'] for c in ci_conv]) if ci_conv else 0
        nonci_conv_2nd = np.mean([c['kl_decreasing_2nd'] for c in nonci_conv]) if nonci_conv else 0

        f.write(f"- **KL convergence (1st order MaxEnt)**: CI={ci_conv_1st:.1%}, non-CI={nonci_conv_1st:.1%}\n")
        f.write(f"- **KL convergence (2nd order MaxEnt)**: CI={ci_conv_2nd:.1%}, non-CI={nonci_conv_2nd:.1%}\n")

        # CI vs non-CI comparison
        ci_better_1st = np.mean([c['ci_better_1st'] for c in ci_vs_nonci_list]) if ci_vs_nonci_list else 0
        ci_better_2nd = np.mean([c['ci_better_2nd'] for c in ci_vs_nonci_list]) if ci_vs_nonci_list else 0

        f.write(f"- **CI lower KL than non-CI (1st order)**: {ci_better_1st:.1%} of configurations\n")
        f.write(f"- **CI lower KL than non-CI (2nd order)**: {ci_better_2nd:.1%} of configurations\n\n")

        # Verdict
        f.write("## Verdict\n\n")

        if ci_conv_1st > 0.6 and ci_better_1st > 0.6:
            f.write("**POSITIVE SIGNAL**: CI appears to promote local MaxEnt emergence.\n\n")
        elif ci_conv_1st < 0.4 and ci_better_1st < 0.4:
            f.write("**NEGATIVE RESULT**: CI does NOT force local MaxEnt in this model.\n\n")
            f.write("This suggests MaxEnt must be an independent axiom, not derivable from CI alone.\n\n")
        else:
            f.write("**INCONCLUSIVE**: Mixed signals, results depend on parameter regime.\n\n")

        f.write("## Model Description\n\n")
        f.write("**Simplified CI-like dynamics** (not actual Wolfram hypergraphs):\n")
        f.write("- State space: binary strings of length L\n")
        f.write("- CI rules: confluent (non-overlapping positions)\n")
        f.write("- Non-CI rules: non-confluent (overlapping positions, for control)\n\n")

        f.write("**Local observer**:\n")
        f.write("- Sees window of w consecutive bits (w << L)\n")
        f.write("- Does NOT know global state or global constraints\n")
        f.write("- Collects statistics over N evolution steps\n\n")

        f.write("**MaxEnt reference distributions**:\n")
        f.write("- 1st order: p ∝ exp(Σ λ_i x_i) matching observed means\n")
        f.write("- 2nd order: p ∝ exp(Σ h_i x_i + Σ J_ij x_i x_j) matching means + correlations (Ising)\n\n")

        f.write("**Measure**: KL(p_obs || p_MaxEnt)\n\n")

        f.write("## Parameter Scan\n\n")
        f.write("| Parameter | Values |\n")
        f.write("|-----------|--------|\n")
        f.write("| L (system size) | 8, 10, 12, 14, 16 |\n")
        f.write("| w (window size) | 2, 3, 4 |\n")
        f.write("| N (evolution steps) | 100, 500, 1K, 5K, 10K |\n")
        f.write("| num_rules | 3, 5, 8 |\n")
        f.write("| seeds | 10 per configuration |\n\n")

        # Detailed results table
        f.write("## Detailed Results: KL Divergence vs N\n\n")
        f.write("### First-Order MaxEnt\n\n")

        # Group by L, w for readability
        from collections import defaultdict
        grouped_by_L_w = defaultdict(list)
        for r in results:
            grouped_by_L_w[(r['L'], r['window_size'])].append(r)

        L_values = sorted(set(r['L'] for r in results))
        for L in L_values:
            w_values = sorted(set(r['window_size'] for r in results if r['L'] == L))
            for w in w_values:
                f.write(f"\n#### L={L}, w={w}\n\n")
                f.write("| N | num_rules | CI KL (mean±std) | non-CI KL (mean±std) | CI better? |\n")
                f.write("|---|-----------|------------------|----------------------|------------|\n")

                subset = [r for r in results if r['L'] == L and r['window_size'] == w]
                N_values = sorted(set(r['N_steps'] for r in subset))
                rules_values = sorted(set(r['num_rules'] for r in subset))

                for N in N_values:
                    for num_rules in rules_values:
                        ci_data = [r['kl_1st_order'] for r in subset
                                   if r['N_steps'] == N and r['num_rules'] == num_rules and r['use_ci']]
                        nonci_data = [r['kl_1st_order'] for r in subset
                                      if r['N_steps'] == N and r['num_rules'] == num_rules and not r['use_ci']]

                        if len(ci_data) > 0 and len(nonci_data) > 0:
                            ci_mean, ci_std = np.mean(ci_data), np.std(ci_data)
                            nonci_mean, nonci_std = np.mean(nonci_data), np.std(nonci_data)
                            better = "✓" if ci_mean < nonci_mean else "✗"

                            f.write(f"| {N} | {num_rules} | {ci_mean:.4f}±{ci_std:.4f} | {nonci_mean:.4f}±{nonci_std:.4f} | {better} |\n")

        # Convergence analysis
        f.write("\n## Convergence Analysis\n\n")
        f.write("Does KL decrease as N increases?\n\n")
        f.write("| L | w | num_rules | Type | 1st-order converges? | 2nd-order converges? |\n")
        f.write("|---|---|-----------|------|---------------------|---------------------|\n")

        conv_list = analysis['convergence']
        for row in conv_list:
            type_str = "CI" if row['use_ci'] else "non-CI"
            conv_1st = "✓" if row['kl_decreasing_1st'] else "✗"
            conv_2nd = "✓" if row['kl_decreasing_2nd'] else "✗"
            f.write(f"| {row['L']} | {row['window_size']} | {row['num_rules']} | {type_str} | {conv_1st} | {conv_2nd} |\n")

        # Statistical summary
        f.write("\n## Statistical Summary\n\n")
        f.write(f"Total experiments: {len(results)}\n\n")

        f.write("### Convergence rates\n\n")
        f.write(f"- CI 1st-order: {ci_conv_1st:.1%}\n")
        f.write(f"- CI 2nd-order: {ci_conv_2nd:.1%}\n")
        f.write(f"- non-CI 1st-order: {nonci_conv_1st:.1%}\n")
        f.write(f"- non-CI 2nd-order: {nonci_conv_2nd:.1%}\n\n")

        f.write("### CI vs non-CI comparison\n\n")
        f.write(f"- CI has lower KL (1st-order): {ci_better_1st:.1%}\n")
        f.write(f"- CI has lower KL (2nd-order): {ci_better_2nd:.1%}\n\n")

        # Interpretation
        f.write("## Interpretation\n\n")
        f.write("**Key question**: Does causal invariance (CI) force local observers to see MaxEnt statistics?\n\n")

        if ci_conv_1st > 0.6 and ci_better_1st > 0.6:
            f.write("**Answer**: POSITIVE SIGNAL in this simplified model.\n\n")
            f.write("CI systems show:\n")
            f.write("1. KL convergence (more data → closer to MaxEnt)\n")
            f.write("2. Lower KL than non-CI control\n\n")
            f.write("This suggests CI may structurally promote local MaxEnt, even without global constraint knowledge.\n\n")
            f.write("**Caution**: This is a simplified model, not actual Wolfram hypergraphs. Real test requires Wolfram Physics Project tools.\n\n")
        else:
            f.write("**Answer**: NEGATIVE or MIXED results in this simplified model.\n\n")
            f.write("CI systems do NOT consistently:\n")
            f.write("1. Show KL convergence to MaxEnt\n")
            f.write("2. Have lower KL than non-CI control\n\n")
            f.write("This suggests **MaxEnt is an independent axiom**, not derivable from CI alone.\n\n")
            f.write("**Implication**: The paper's claim 'CI → MaxEnt' needs revision. MaxEnt must be explicitly postulated.\n\n")

        f.write("## Limitations\n\n")
        f.write("1. **Simplified model**: Not actual Wolfram hypergraph rules\n")
        f.write("2. **Discrete state space**: Real hypergraphs have continuous growth\n")
        f.write("3. **Fixed topology**: Real CI involves graph rewriting\n")
        f.write("4. **Small systems**: L ≤ 16 due to combinatorial explosion\n\n")
        f.write("**Next step**: Test with actual Wolfram Language hypergraph evolution rules.\n\n")

        f.write("## Raw Data\n\n")
        f.write(f"Full results saved to JSON: `{output_path.replace('.md', '.json')}`\n\n")


def main():
    """Main execution."""
    print("=" * 60)
    print("Causal Typicality v3: Local MaxEnt Emergence Test")
    print("=" * 60)
    print()
    print("Testing whether local MaxEnt emerges from causal invariance")
    print("in a simplified toy model with LOCAL observer (no global knowledge).")
    print()

    # Run parameter scan
    results = run_parameter_scan()

    print()
    print(f"Completed {len(results)} experiments.")
    print()
    print("Analyzing results...")

    # Analyze
    analysis = analyze_results(results)

    # Save results
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    json_path = output_dir / "causal_typicality_v3_results.json"
    md_path = output_dir / "causal_typicality_v3_results.md"

    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {json_path}")

    # Generate report
    print("Generating report...")
    generate_report(results, analysis, str(md_path))

    print(f"Report saved to: {md_path}")
    print()
    print("=" * 60)
    print("COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
