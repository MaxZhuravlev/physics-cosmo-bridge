#!/usr/bin/env python3
"""
Causal Typicality Corrected Model (Campaign 2026-02-17)

CAMPAIGN OBJECTIVE:
  Test whether CI + large N naturally produces MaxEnt statistics for
  a small persistent observer. This is the MOST IMPORTANT open question
  in the research program: does the logical chain
    CI -> exp family -> M=F^2 -> Lorentzian
  follow from MaxEnt as an emergent principle (not an axiom)?

DESIGN PHILOSOPHY (fixes previous bugs):
  - v1/v2 bug: Global constraint M_total=0 coupled O and E deterministically
    making MaxEnt trivial or the wrong reference.
  - v3 issue: Binary string rules didn't have genuine CI (confluence was
    approximate), and convergence was tested only over time steps, not
    over microstate ensemble.

THIS VERSION:
  - Uses string rewriting systems with genuine confluence (CI property)
  - Observer O = first m bits of string
  - Boundary = bits at positions m-1, m, m+1 (the interface)
  - Tests: Does p(O_internal | boundary) converge to MaxEnt as N -> inf?
  - Samples many independent initial conditions (ensemble approach)
  - Three CI rules: swap (trivially CI), 3-bit flip, bubble sort
  - Compares with non-CI control

KEY DISTINCTION FROM PREVIOUS VERSIONS:
  We sample an ENSEMBLE of independent initial conditions (microstates),
  fix boundary data, and measure how concentrated the observer distribution
  is around MaxEnt. This tests the typicality conjecture directly:
  "For most microstates in M_C, does p(O | boundary) ~ MaxEnt?"

PARAMETERS:
  m = 3  (observer size, fixed throughout)
  N = 8, 12, 16, 20, 30, 50, 100  (system size, varied)
  n_samples = 10000+  (ensemble size)
  n_steps = N * 5  (evolution steps, scales with system size)

OUTPUT:
  - KL divergence vs N for each rule
  - Scaling fit: KL ~ A * N^(-alpha) or A * exp(-B*N)
  - ExpFamily fit quality
  - Persistence test results
"""

import numpy as np
from collections import Counter, defaultdict
from scipy.special import rel_entr
from scipy.optimize import minimize, curve_fit
from scipy.special import logsumexp
from itertools import product as iter_product
from typing import List, Tuple, Dict, Optional
import json
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

np.random.seed(42)


# =============================================================================
# CI RULES (string rewriting systems)
# =============================================================================

def swap_rule(state: np.ndarray) -> np.ndarray:
    """
    Swap rule: "01" -> "10" at a random applicable position.

    This is trivially CI (confluent): adjacent swaps commute in the sense
    that all orders produce the same SORTED normal form (bubble sort limit).
    The causal graph is well-defined regardless of rewriting order.

    Physical meaning: This models "information diffusion" -- bits percolate
    toward their natural sorted positions. The normal form is the sorted string.
    """
    state = state.copy()
    # Find all positions where "01" appears
    positions = []
    for i in range(len(state) - 1):
        if state[i] == 0 and state[i+1] == 1:
            positions.append(i)
    if positions:
        pos = np.random.choice(positions)
        state[pos] = 1
        state[pos + 1] = 0
    return state


def flip3_rule(state: np.ndarray) -> np.ndarray:
    """
    3-bit flip rule: "110" -> "001" at a random applicable position.

    CI check: This rule at non-overlapping positions commutes. If two
    instances of "110" overlap (share a bit), they cannot both fire
    simultaneously. We handle this by applying at most one instance per step.
    The normal form depends on initial state -- rule is idempotent once "001"
    forms, so CI holds trivially.

    Physical meaning: 3-bit patterns represent causal triangles; the rule
    models causal triangle "orientation flipping" -- a symmetry of CI.
    """
    state = state.copy()
    positions = []
    for i in range(len(state) - 2):
        if state[i] == 1 and state[i+1] == 1 and state[i+2] == 0:
            positions.append(i)
    if positions:
        pos = np.random.choice(positions)
        state[pos] = 0
        state[pos + 1] = 0
        state[pos + 2] = 1
    return state


def xor_propagate_rule(state: np.ndarray) -> np.ndarray:
    """
    XOR propagation: a bit at position i flips if neighbors disagree.

    Rule: if state[i-1] != state[i+1], flip state[i] with probability 0.5.
    Apply to ONE random interior position per step.

    This is CI in a weak sense: the update is local and the statistical
    distribution of outcomes is invariant to the order of application
    at non-adjacent positions.

    Physical meaning: Represents local causal ambiguity resolution -- the
    XOR rule enforces causal consistency between neighbors.
    """
    state = state.copy()
    N = len(state)
    # Apply to random interior position
    if N > 2:
        i = np.random.randint(1, N - 1)
        if state[i-1] != state[i+1]:  # Neighbors disagree -> causal ambiguity
            state[i] = 1 - state[i]  # Resolve by flipping
    return state


def local_shuffle_ci_rule(state: np.ndarray) -> np.ndarray:
    """
    Local shuffle (adjacent transposition) rule: swap two adjacent bits.

    This is genuinely CI because transpositions at non-adjacent positions
    commute, and the Diamond Lemma applies: any two finite sequences of
    applicable transpositions on non-overlapping pairs commute.

    CRUCIALLY: This rule does NOT converge to a fixed point. It performs
    a random walk on the symmetric group, preserving the composition
    (number of 0s and 1s) but not the ordering. The stationary distribution
    is uniform over all permutations of the initial string.

    Physical meaning: Represents causal ambiguity in event ordering --
    the hyperedge can be updated in any order, CI ensures they all
    lead to the same causal graph. The random walk models the
    microstate exploration of the CI ensemble.

    This is the BEST CI analog for testing typicality because:
      1. Genuine CI (adjacent transpositions form a confluent reduction)
      2. Ergodic (reaches any permutation eventually)
      3. No fixed-point attractor (unlike bubble sort)
      4. Conservation law: preserves number of 0s and 1s (analog of causal macrostate)
    """
    state = state.copy()
    if len(state) < 2:
        return state
    # Swap two randomly chosen adjacent bits
    i = np.random.randint(0, len(state) - 1)
    state[i], state[i + 1] = state[i + 1].copy(), state[i].copy()
    return state


def non_ci_random_rule(state: np.ndarray) -> np.ndarray:
    """
    Non-CI control: random bit flip at random position.
    No confluence property -- used as comparison baseline.
    """
    state = state.copy()
    pos = np.random.randint(len(state))
    state[pos] = 1 - state[pos]
    return state


RULES = {
    'swap_ci': swap_rule,          # Bubble sort CI (converges to fixed point)
    'flip3_ci': flip3_rule,        # 3-bit flip CI (partial convergence)
    'shuffle_ci': local_shuffle_ci_rule,  # Random walk CI (ergodic, no fixed point)
    'xor_ci': xor_propagate_rule,  # XOR propagation CI (quick randomization)
    'random_noci': non_ci_random_rule,    # Non-CI control (random flips)
}


# =============================================================================
# EVOLUTION ENGINE
# =============================================================================

def evolve(state: np.ndarray, rule_fn, n_steps: int) -> np.ndarray:
    """
    Evolve a binary string state for n_steps using the given rule.

    Args:
        state: Initial binary array of length N
        rule_fn: Rule function (state -> new_state)
        n_steps: Number of evolution steps

    Returns:
        Final state after n_steps
    """
    for _ in range(n_steps):
        state = rule_fn(state)
    return state


# =============================================================================
# OBSERVER AND BOUNDARY EXTRACTION
# =============================================================================

def extract_boundary_and_observer(state: np.ndarray, m: int) -> Tuple[tuple, tuple]:
    """
    Extract observer internal state and boundary data.

    Observer O = first m bits (positions 0..m-1)
    Boundary = bits at positions m-1, m, m+1 (the interface region)
    Observer internal = bits at positions 0..m-2 (excluding boundary bit)

    The KEY design choice: observer internal state should NOT include the
    boundary bit itself, so that the boundary genuinely constrains but does
    not determine the internal state.

    Args:
        state: Full system state of length N
        m: Observer size

    Returns:
        (boundary_data, observer_internal) as tuples of bits
    """
    N = len(state)
    # Boundary: the junction region
    b_start = max(0, m - 1)
    b_end = min(N, m + 2)  # Up to 3 bits
    boundary = tuple(state[b_start:b_end].tolist())

    # Observer internal: bits strictly inside observer (not including boundary)
    obs_internal = tuple(state[:max(1, m-1)].tolist())

    return boundary, obs_internal


# =============================================================================
# MAXENT DISTRIBUTION COMPUTATION
# =============================================================================

def compute_maxent_uniform(n_bits: int) -> np.ndarray:
    """
    MaxEnt distribution for unconstrained binary strings of length n_bits.

    For unconstrained binary strings, MaxEnt is the uniform distribution:
      p*(x) = 1 / 2^n_bits  for all x in {0,1}^n_bits

    This is the null hypothesis: if the observer sees exactly this,
    the CI conjecture is maximally supported.

    Args:
        n_bits: Length of observer internal state

    Returns:
        Uniform probability vector of length 2^n_bits
    """
    n_states = 2 ** n_bits
    return np.ones(n_states) / n_states


def compute_maxent_with_mean_constraint(observed_mean: float, n_bits: int) -> np.ndarray:
    """
    MaxEnt distribution for binary strings with constrained mean.

    p*(x) = exp(theta * sum(x)) / Z
    where theta is chosen so that E[sum(x)] = n_bits * observed_mean.

    This is the Boltzmann/Bernoulli exponential family with:
      T(x) = sum(x)  (total number of 1s)
      theta = log(p/(1-p)) where p = observed_mean

    Args:
        observed_mean: Observed mean bit value (between 0 and 1)
        n_bits: Length of observer internal state

    Returns:
        Probability vector of length 2^n_bits, indexed by binary integer
    """
    all_states = np.array(list(iter_product([0, 1], repeat=n_bits)))
    total_ones = all_states.sum(axis=1).astype(float)

    # Clamp to avoid log(0)
    p = np.clip(observed_mean, 1e-6, 1 - 1e-6)
    theta = np.log(p / (1 - p))

    logits = theta * total_ones
    log_Z = logsumexp(logits)
    return np.exp(logits - log_Z)


def compute_maxent_exponential_family(observed_means: np.ndarray, n_bits: int) -> np.ndarray:
    """
    MaxEnt distribution matching per-bit observed means (first-order).

    p*(x) = exp(sum_i theta_i * x_i) / Z
    where theta_i is chosen so that E_{p*}[x_i] = observed_means[i].

    This is the product of independent Bernoullis conditioned on each
    bit's marginal mean -- the first-order exponential family.

    Args:
        observed_means: Per-bit observed means, shape (n_bits,)
        n_bits: Length of observer internal state

    Returns:
        Probability vector of length 2^n_bits
    """
    all_states = np.array(list(iter_product([0, 1], repeat=n_bits)))

    def neg_log_Z_minus_moment(thetas):
        """Dual objective: log Z - theta . mu_target."""
        logits = all_states @ thetas
        log_Z = logsumexp(logits)
        return log_Z - thetas @ observed_means

    result = minimize(
        neg_log_Z_minus_moment,
        np.zeros(n_bits),
        method='BFGS',
        options={'gtol': 1e-8}
    )
    thetas = result.x
    logits = all_states @ thetas
    log_Z = logsumexp(logits)
    return np.exp(logits - log_Z)


# =============================================================================
# KL DIVERGENCE
# =============================================================================

def kl_divergence_safe(p: np.ndarray, q: np.ndarray) -> float:
    """
    KL(p || q) with safe handling of zeros.

    Uses the convention: 0 * log(0/q) = 0 (for p=0 entries).
    Adds small epsilon to q to avoid log(0) when p>0 but q~0.

    Args:
        p: True distribution (non-negative, sums to 1)
        q: Reference distribution (non-negative, sums to 1)

    Returns:
        KL divergence in nats (>= 0)
    """
    p = np.array(p, dtype=float)
    q = np.array(q, dtype=float)
    # Add tiny epsilon to q (not p) to avoid singularity
    q = np.maximum(q, 1e-12)
    # Standard KL using rel_entr: rel_entr(p, q) = p * log(p/q) (0 if p=0)
    kl = np.sum(rel_entr(p, q))
    return float(kl)


# =============================================================================
# MAIN MEASUREMENT: OBSERVER DISTRIBUTION GIVEN BOUNDARY
# =============================================================================

def measure_observer_distribution_given_boundary(
    N: int,
    m: int,
    rule_name: str,
    n_samples: int = 10000,
    n_steps_per_sample: int = None
) -> Dict:
    """
    Core measurement: sample observer states from CI evolution ensemble.

    For each sample:
      1. Draw random initial state
      2. Evolve for n_steps under CI rule
      3. Extract boundary and observer internal state
      4. Record: boundary_data -> observer_internal_state

    Then for each boundary condition with sufficient statistics:
      5. Compute observed p(O_internal | boundary)
      6. Compute MaxEnt reference p*(O_internal | boundary)
      7. Compute KL(p_observed || p_maxent)

    This tests the typicality conjecture:
      "For large N, p(O_internal | boundary) concentrates around MaxEnt"

    Args:
        N: Total system size (number of bits)
        m: Observer size (bits 0..m-1)
        rule_name: Name of evolution rule
        n_samples: Number of independent samples
        n_steps_per_sample: Evolution steps per sample (default: N * 5)

    Returns:
        Dict with measurement results
    """
    if n_steps_per_sample is None:
        # N*2 is the optimal regime: enough mixing but not full convergence.
        # For bubble sort (swap_ci): N*2 is the transient regime where N matters.
        # For shuffle_ci: N*2 provides N^2 / N = N mixing time fraction.
        # Too few steps: under-mixed. Too many: converges to fixed point for swap_ci.
        n_steps_per_sample = max(N * 2, 20)

    rule_fn = RULES[rule_name]

    # n_bits_internal: bits strictly inside observer
    n_bits_internal = max(1, m - 1)

    # Collect (boundary, observer_internal) pairs
    boundary_observer_counts = defaultdict(Counter)

    for _ in range(n_samples):
        # Random initial state
        initial = np.random.randint(0, 2, size=N)

        # Evolve under CI rule
        final = evolve(initial, rule_fn, n_steps_per_sample)

        # Extract boundary and observer
        boundary, obs_internal = extract_boundary_and_observer(final, m)

        boundary_observer_counts[boundary][obs_internal] += 1

    # For each boundary condition, compute KL from MaxEnt
    kl_values = []
    n_boundary_conditions = 0
    boundary_results = {}

    for boundary, obs_counts in boundary_observer_counts.items():
        total = sum(obs_counts.values())
        if total < 20:  # Need enough samples for reliable estimate
            continue

        n_boundary_conditions += 1

        # Observed distribution over observer internal states
        all_obs_states = [tuple(s) for s in iter_product([0, 1], repeat=n_bits_internal)]
        n_obs_states = len(all_obs_states)

        p_observed = np.array([
            obs_counts.get(s, 0) / total for s in all_obs_states
        ])

        # MaxEnt reference: uniform over all observer internal states
        # This is the MaxEnt for unconstrained binary observer
        p_maxent_uniform = compute_maxent_uniform(n_bits_internal)

        # Also compute MaxEnt with mean constraint (using observed mean)
        observed_mean_per_bit = np.array([
            sum(s[i] * obs_counts.get(s, 0) for s in all_obs_states) / total
            for i in range(n_bits_internal)
        ])

        # MaxEnt with per-bit mean constraints (exponential family)
        try:
            p_maxent_expfam = compute_maxent_exponential_family(
                observed_mean_per_bit, n_bits_internal
            )
        except Exception:
            p_maxent_expfam = compute_maxent_uniform(n_bits_internal)

        # KL divergences
        kl_uniform = kl_divergence_safe(p_observed, p_maxent_uniform)

        # ExpFamily goodness-of-fit: KL(p_obs || p_maxent_expfam)
        # This is small if p_obs IS an exponential family (matches moments)
        kl_expfam = kl_divergence_safe(p_observed, p_maxent_expfam)

        kl_values.append({
            'boundary': boundary,
            'total_samples': total,
            'kl_uniform': kl_uniform,
            'kl_expfam': kl_expfam,
            'n_obs_states_seen': sum(1 for v in p_observed if v > 0),
        })

        boundary_results[str(boundary)] = {
            'total': total,
            'kl_uniform': kl_uniform,
            'kl_expfam': kl_expfam,
        }

    if not kl_values:
        return {
            'N': N, 'm': m, 'rule': rule_name,
            'n_boundary_conditions': 0,
            'mean_kl_uniform': float('nan'),
            'std_kl_uniform': float('nan'),
            'mean_kl_expfam': float('nan'),
            'std_kl_expfam': float('nan'),
            'n_samples': n_samples,
        }

    kl_uniform_vals = [r['kl_uniform'] for r in kl_values]
    kl_expfam_vals = [r['kl_expfam'] for r in kl_values]

    return {
        'N': N,
        'm': m,
        'rule': rule_name,
        'n_boundary_conditions': n_boundary_conditions,
        'mean_kl_uniform': float(np.mean(kl_uniform_vals)),
        'std_kl_uniform': float(np.std(kl_uniform_vals)),
        'mean_kl_expfam': float(np.mean(kl_expfam_vals)),
        'std_kl_expfam': float(np.std(kl_expfam_vals)),
        'n_samples': n_samples,
        'per_boundary': kl_values[:5],  # Save first 5 for debugging
    }


# =============================================================================
# N-SCALING STUDY
# =============================================================================

def run_n_scaling_study(
    N_values: List[int],
    m: int = 3,
    n_samples: int = 10000,
    rules: Optional[List[str]] = None
) -> Dict:
    """
    Run the N-scaling study for all rules and system sizes.

    Tests: KL(N) for N in N_values with fixed observer size m=3.
    Reports:
      - Mean KL vs N for each rule
      - Evidence for/against causal typicality conjecture

    Args:
        N_values: List of system sizes to test
        m: Observer size (fixed)
        n_samples: Samples per (N, rule) configuration
        rules: List of rule names (default: all 4 rules)

    Returns:
        Dict with complete scaling study results
    """
    if rules is None:
        rules = list(RULES.keys())

    all_results = []
    print(f"\nN-scaling study: m={m}, n_samples={n_samples}")
    print(f"Rules: {rules}")
    print(f"N values: {N_values}")
    print("-" * 60)

    for rule_name in rules:
        print(f"\nRule: {rule_name}")
        rule_results = []

        for N in N_values:
            if N < m + 2:  # System must be larger than observer + boundary
                print(f"  N={N}: SKIP (too small for m={m})")
                continue

            print(f"  N={N}: evolving {n_samples} samples...", end="", flush=True)

            result = measure_observer_distribution_given_boundary(
                N=N, m=m, rule_name=rule_name, n_samples=n_samples
            )

            rule_results.append(result)
            kl = result['mean_kl_uniform']
            kl_ef = result['mean_kl_expfam']
            n_bc = result['n_boundary_conditions']
            print(f" KL_uniform={kl:.4f}, KL_expfam={kl_ef:.4f}, boundaries={n_bc}")

        all_results.extend(rule_results)

    return {'scaling_results': all_results, 'parameters': {
        'N_values': N_values, 'm': m, 'n_samples': n_samples, 'rules': rules
    }}


# =============================================================================
# SCALING FIT
# =============================================================================

def fit_power_law(N_vals: List[int], kl_vals: List[float]) -> Dict:
    """
    Fit KL(N) = A * N^(-alpha) (power law decay).

    Positive alpha means KL decreases with N -> supports typicality.
    Negative alpha means KL increases with N -> against typicality.

    Args:
        N_vals: System sizes
        kl_vals: Mean KL values

    Returns:
        Dict with fit parameters and quality
    """
    N = np.array(N_vals, dtype=float)
    kl = np.array(kl_vals, dtype=float)

    # Remove NaN or infinite values
    mask = np.isfinite(kl) & (kl > 0) & np.isfinite(N)
    if mask.sum() < 3:
        return {'A': None, 'alpha': None, 'r_squared': None, 'verdict': 'insufficient_data'}

    N_clean = N[mask]
    kl_clean = kl[mask]

    # Log-linear fit: log(kl) = log(A) - alpha * log(N)
    log_N = np.log(N_clean)
    log_kl = np.log(kl_clean)

    # Linear regression in log-log space
    coeffs = np.polyfit(log_N, log_kl, 1)
    alpha = -coeffs[0]  # KL ~ N^(-alpha)
    log_A = coeffs[1]
    A = np.exp(log_A)

    # R^2 in log-log space
    log_kl_pred = np.polyval(coeffs, log_N)
    ss_res = np.sum((log_kl - log_kl_pred) ** 2)
    ss_tot = np.sum((log_kl - np.mean(log_kl)) ** 2)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

    # Verdict
    if alpha > 0.1 and r_squared > 0.5:
        verdict = f"POSITIVE (KL ~ N^(-{alpha:.2f}), supports typicality)"
    elif alpha < -0.1:
        verdict = f"NEGATIVE (KL increases with N, against typicality)"
    else:
        verdict = f"FLAT (alpha={alpha:.3f}, inconclusive)"

    return {
        'A': float(A),
        'alpha': float(alpha),
        'r_squared': float(r_squared),
        'verdict': verdict
    }


def fit_exponential(N_vals: List[int], kl_vals: List[float]) -> Dict:
    """
    Fit KL(N) = A * exp(-B*N) (exponential decay).

    Positive B means KL decays exponentially -> strong support for typicality.

    Args:
        N_vals: System sizes
        kl_vals: Mean KL values

    Returns:
        Dict with fit parameters and quality
    """
    N = np.array(N_vals, dtype=float)
    kl = np.array(kl_vals, dtype=float)

    mask = np.isfinite(kl) & (kl > 0) & np.isfinite(N)
    if mask.sum() < 3:
        return {'A': None, 'B': None, 'r_squared': None, 'verdict': 'insufficient_data'}

    N_clean = N[mask]
    kl_clean = kl[mask]

    try:
        popt, pcov = curve_fit(
            lambda x, A, B: A * np.exp(-B * x),
            N_clean, kl_clean,
            p0=[kl_clean[0], 0.01],
            maxfev=5000,
            bounds=([0, -1], [10, 1])
        )
        A, B = popt

        # R^2
        kl_pred = A * np.exp(-B * N_clean)
        ss_res = np.sum((kl_clean - kl_pred) ** 2)
        ss_tot = np.sum((kl_clean - np.mean(kl_clean)) ** 2)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

        if B > 0.01 and r_squared > 0.5:
            verdict = f"POSITIVE (KL ~ exp(-{B:.3f}*N), strong support)"
        elif B < -0.01:
            verdict = "NEGATIVE (KL grows exponentially)"
        else:
            verdict = f"FLAT (B={B:.4f}, inconclusive)"
    except Exception as e:
        return {'A': None, 'B': None, 'r_squared': None, 'verdict': f'fit_failed: {e}'}

    return {
        'A': float(A),
        'B': float(B),
        'r_squared': float(r_squared),
        'verdict': verdict
    }


# =============================================================================
# EXPONENTIAL FAMILY FIT TEST
# =============================================================================

def test_expfam_fit_quality(
    N_values: List[int],
    m: int = 3,
    n_samples: int = 5000,
    rule_name: str = 'swap_ci'
) -> List[Dict]:
    """
    Test: Does the observer marginal distribution p(O) converge to an
    exponential family?

    Method: Fit p(O) to best-fit first-order exponential family.
    Measure KL(p_obs || p_expfam_best_fit) -- this is the "excess entropy"
    beyond what the exp family can capture.

    If KL -> 0 as N -> inf: p(O) IS converging to an exp family.
    If KL is constant: p(O) is NOT an exp family.

    Args:
        N_values: System sizes to test
        m: Observer size
        n_samples: Samples per N
        rule_name: Which CI rule to use

    Returns:
        List of dicts with expfam fit results per N
    """
    print(f"\nExponential family fit test: rule={rule_name}, m={m}")
    print("-" * 60)
    results = []

    rule_fn = RULES[rule_name]

    for N in N_values:
        if N < m + 2:
            continue

        n_steps = max(N * 5, 50)
        n_bits_obs = m  # Full observer (including boundary bit)

        # Collect observer states from ensemble
        obs_counts = Counter()

        for _ in range(n_samples):
            initial = np.random.randint(0, 2, size=N)
            final = evolve(initial, rule_fn, n_steps)
            obs_state = tuple(final[:m].tolist())
            obs_counts[obs_state] += 1

        # Observed distribution over observer states
        all_obs = list(iter_product([0, 1], repeat=n_bits_obs))
        total = sum(obs_counts.values())
        p_obs = np.array([obs_counts.get(s, 0) / total for s in all_obs])

        # Per-bit observed means
        obs_means = np.array([
            sum(s[i] * obs_counts.get(s, 0) for s in all_obs) / total
            for i in range(n_bits_obs)
        ])

        # Best-fit first-order MaxEnt (exponential family)
        try:
            p_expfam = compute_maxent_exponential_family(obs_means, n_bits_obs)
            kl_from_expfam = kl_divergence_safe(p_obs, p_expfam)
        except Exception:
            kl_from_expfam = float('nan')
            p_expfam = np.ones(2**n_bits_obs) / (2**n_bits_obs)

        # Entropy of observed distribution
        p_pos = p_obs[p_obs > 0]
        entropy_obs = -np.sum(p_pos * np.log(p_pos))

        # MaxEnt (uniform) entropy = log(2^m) = m * log(2)
        entropy_maxent = n_bits_obs * np.log(2)

        print(f"  N={N:3d}: KL_to_expfam={kl_from_expfam:.4f}, "
              f"entropy={entropy_obs:.3f} (MaxEnt={entropy_maxent:.3f}), "
              f"obs_mean={obs_means.mean():.3f}")

        results.append({
            'N': N,
            'm': m,
            'rule': rule_name,
            'kl_to_expfam': float(kl_from_expfam),
            'entropy_obs': float(entropy_obs),
            'entropy_maxent': float(entropy_maxent),
            'entropy_fraction': float(entropy_obs / entropy_maxent) if entropy_maxent > 0 else float('nan'),
            'obs_mean': float(obs_means.mean()),
            'n_samples': n_samples,
        })

    return results


# =============================================================================
# PERSISTENCE TEST
# =============================================================================

def test_persistence_effect(
    N_values: List[int],
    m: int = 3,
    n_samples: int = 5000,
    p_flip: float = 0.1,
    rule_name: str = 'swap_ci'
) -> List[Dict]:
    """
    Test: Does observer PERSISTENCE accelerate MaxEnt convergence?

    Persistence model: After each evolution step, with probability (1 - p_flip),
    the observer bits revert to their previous state (inertia).

    Hypothesis: Persistent observers (low p_flip) are better coupled to the
    environment's typical state, thus showing lower KL from MaxEnt.

    Args:
        N_values: System sizes to test
        m: Observer size
        n_samples: Samples per N
        p_flip: Probability that observer bit adopts new state (1=no inertia, 0=frozen)
        rule_name: Which CI rule to use

    Returns:
        List of dicts comparing persistent vs non-persistent observers
    """
    print(f"\nPersistence test: rule={rule_name}, p_flip={p_flip}")
    print("-" * 60)
    results = []

    rule_fn = RULES[rule_name]

    for N in N_values:
        if N < m + 2:
            continue

        n_steps = max(N * 5, 50)
        n_bits_internal = max(1, m - 1)

        # --- Non-persistent observer (standard) ---
        bc_nonpers = defaultdict(Counter)
        for _ in range(n_samples):
            initial = np.random.randint(0, 2, size=N)
            final = evolve(initial, rule_fn, n_steps)
            boundary, obs_int = extract_boundary_and_observer(final, m)
            bc_nonpers[boundary][obs_int] += 1

        # --- Persistent observer ---
        # The observer has inertia: it only updates with probability p_flip per step
        bc_pers = defaultdict(Counter)
        for _ in range(n_samples):
            state = np.random.randint(0, 2, size=N)
            observer_memory = state[:m].copy()  # Observer's remembered state

            for step in range(n_steps):
                state = rule_fn(state)
                # Observer only updates with probability p_flip
                for i in range(m):
                    if np.random.random() < p_flip:
                        observer_memory[i] = state[i]
                    # else: observer keeps its previous value (inertia)

            # Use observer_memory (not state[:m]) for classification
            # But boundary is from the actual state
            final_boundary = tuple(state[max(0, m-1):min(N, m+2)].tolist())
            final_obs_int = tuple(observer_memory[:max(1, m-1)].tolist())
            bc_pers[final_boundary][final_obs_int] += 1

        # Compute KL for both
        def compute_mean_kl(boundary_counts):
            kl_vals = []
            p_maxent = compute_maxent_uniform(n_bits_internal)
            for boundary, obs_counts in boundary_counts.items():
                total = sum(obs_counts.values())
                if total < 15:
                    continue
                all_obs = list(iter_product([0, 1], repeat=n_bits_internal))
                p_obs = np.array([obs_counts.get(s, 0) / total for s in all_obs])
                kl_vals.append(kl_divergence_safe(p_obs, p_maxent))
            return np.mean(kl_vals) if kl_vals else float('nan')

        kl_nonpers = compute_mean_kl(bc_nonpers)
        kl_pers = compute_mean_kl(bc_pers)
        improvement = (kl_nonpers - kl_pers) / kl_nonpers if kl_nonpers > 0 else float('nan')

        print(f"  N={N:3d}: KL_standard={kl_nonpers:.4f}, KL_persistent={kl_pers:.4f}, "
              f"improvement={improvement:+.1%}")

        results.append({
            'N': N,
            'm': m,
            'rule': rule_name,
            'p_flip': p_flip,
            'kl_nonpersistent': float(kl_nonpers),
            'kl_persistent': float(kl_pers),
            'improvement_fraction': float(improvement),
            'persistence_helps': bool(kl_pers < kl_nonpers),
            'n_samples': n_samples,
        })

    return results


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """
    Main execution: run full causal typicality campaign.

    Steps:
      1. N-scaling study (main test)
      2. Exponential family fit test
      3. Persistence test
      4. Scaling fit analysis
      5. Write comprehensive results
    """
    print("=" * 70)
    print("CAUSAL TYPICALITY CAMPAIGN: 2026-02-17")
    print("Testing: CI + large N -> MaxEnt observers?")
    print("=" * 70)

    # Output directory
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    # ----- STEP 1: N-scaling study -----
    # Main test: fix m=3, vary N, measure KL(p_actual || p_MaxEnt)
    # Rule choice: shuffle_ci is most important (genuine CI, ergodic, no fixed point)
    # swap_ci shows interesting transient behavior
    N_values = [8, 12, 16, 20, 30, 50, 100]
    m = 3
    n_samples = 10000

    print(f"\nSTEP 1: N-scaling study")
    print(f"  Observer size m={m} (fixed)")
    print(f"  N values: {N_values}")
    print(f"  Samples per (N, rule): {n_samples}")
    print(f"  Steps per sample: N*2 (optimal transient regime)")

    scaling_study = run_n_scaling_study(
        N_values=N_values,
        m=m,
        n_samples=n_samples,
        rules=['swap_ci', 'flip3_ci', 'shuffle_ci', 'xor_ci', 'random_noci']
    )

    # ----- STEP 2: Scaling fit analysis -----
    print(f"\nSTEP 2: Scaling fit analysis")
    fit_results = {}

    for rule in ['swap_ci', 'flip3_ci', 'shuffle_ci', 'xor_ci', 'random_noci']:
        rule_data = [r for r in scaling_study['scaling_results']
                     if r['rule'] == rule and not np.isnan(r.get('mean_kl_uniform', float('nan')))]

        if len(rule_data) < 3:
            print(f"  {rule}: insufficient data")
            continue

        Ns = [r['N'] for r in rule_data]
        kls = [r['mean_kl_uniform'] for r in rule_data]

        power_fit = fit_power_law(Ns, kls)
        exp_fit = fit_exponential(Ns, kls)

        print(f"  {rule}:")
        print(f"    Power law: A={power_fit.get('A', 'N/A'):.3f}, alpha={power_fit.get('alpha', 'N/A'):.3f}, R^2={power_fit.get('r_squared', 'N/A'):.3f}")
        print(f"    Verdict: {power_fit['verdict']}")

        fit_results[rule] = {
            'N_values': Ns,
            'kl_values': kls,
            'power_law': power_fit,
            'exponential': exp_fit
        }

    # ----- STEP 3: Exponential family fit test -----
    print(f"\nSTEP 3: Exponential family fit test")
    N_small = [n for n in N_values if n <= 50]  # Use smaller N for this test
    expfam_results = {}
    for rule in ['shuffle_ci', 'swap_ci']:
        expfam_results[rule] = test_expfam_fit_quality(
            N_values=N_small, m=m, n_samples=5000, rule_name=rule
        )

    # ----- STEP 4: Persistence test -----
    print(f"\nSTEP 4: Persistence test")
    N_persistence = [n for n in N_values if n <= 50]
    persistence_results = test_persistence_effect(
        N_values=N_persistence, m=m, n_samples=5000,
        p_flip=0.1, rule_name='shuffle_ci'
    )

    # ----- STEP 5: Synthesis and write results -----
    print(f"\nSTEP 5: Writing results")

    all_data = {
        'campaign': 'CAUSAL-TYPICALITY-2026-02-17',
        'parameters': {'m': m, 'N_values': N_values, 'n_samples': n_samples},
        'scaling_study': scaling_study,
        'fit_results': fit_results,
        'expfam_results': expfam_results,
        'persistence_results': persistence_results,
    }

    # Save JSON
    json_path = output_dir / "causal_typicality_corrected_results.json"
    with open(json_path, 'w') as f:
        json.dump(all_data, f, indent=2, default=str)
    print(f"  JSON saved: {json_path}")

    # Generate comprehensive markdown report
    report_path = (
        Path(__file__).parent.parent.parent.parent.parent.parent
        / "experience" / "insights"
        / "CAUSAL-TYPICALITY-CAMPAIGN-2026-02-17.md"
    )
    _write_comprehensive_report(all_data, fit_results, expfam_results, persistence_results, report_path)
    print(f"  Report saved: {report_path}")

    print("\n" + "=" * 70)
    print("CAMPAIGN COMPLETE")
    print("=" * 70)

    # Print final verdict
    _print_verdict(fit_results)


def _print_verdict(fit_results: Dict):
    """Print human-readable verdict on typicality conjecture."""
    print("\nFINAL VERDICT:")
    print("-" * 60)

    positive_count = 0
    negative_count = 0

    for rule, fit_data in fit_results.items():
        if rule in ('random_noci', 'xor_ci'):
            continue  # Skip trivial control rules for verdict
        power = fit_data.get('power_law', {})
        alpha = power.get('alpha')
        if alpha is not None:
            if alpha > 0.1:
                positive_count += 1
                verdict = "POSITIVE"
            elif alpha < -0.1:
                negative_count += 1
                verdict = "NEGATIVE"
            else:
                verdict = "INCONCLUSIVE"
            print(f"  {rule}: alpha={alpha:.3f} -> {verdict}")

    total = positive_count + negative_count
    if total == 0:
        print("  Overall: INCONCLUSIVE (insufficient data)")
    elif positive_count > total / 2:
        print(f"\n  OVERALL: POSITIVE EVIDENCE for causal typicality")
        print(f"  {positive_count}/{total} CI rules show KL decreasing with N")
        print(f"  Confidence update: 25-35% -> POSSIBLY 40-50%")
    elif negative_count > total / 2:
        print(f"\n  OVERALL: NEGATIVE EVIDENCE against causal typicality")
        print(f"  {negative_count}/{total} CI rules show KL NOT decreasing with N")
        print(f"  Confidence update: 25-35% -> POSSIBLY 15-25%")
    else:
        print(f"\n  OVERALL: MIXED EVIDENCE")
        print(f"  Some CI rules support, some don't. Rule-dependent phenomenon.")


def _write_comprehensive_report(
    all_data: Dict,
    fit_results: Dict,
    expfam_results: Dict,
    persistence_results: List[Dict],
    report_path: Path
):
    """Write comprehensive markdown report to insights file."""

    report_path.parent.mkdir(parents=True, exist_ok=True)

    scaling_results = all_data['scaling_study']['scaling_results']

    lines = []
    lines.append("# Causal Typicality Campaign: Results")
    lines.append("")
    lines.append("**Date**: 2026-02-17")
    lines.append("**Campaign**: CAUSAL TYPICALITY AND MAXENT CONVERGENCE")
    lines.append("**Status**: COMPUTATIONAL RESULTS")
    lines.append("**Prior confidence**: 25-35% (that CI + persistence -> MaxEnt via typicality)")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 0. Executive Summary")
    lines.append("")
    lines.append("**The Question**: Does CI + large N naturally produce MaxEnt boundary statistics")
    lines.append("for a small persistent observer? This would close the critical gap:")
    lines.append("")
    lines.append("```")
    lines.append("CI -> [typicality] -> MaxEnt -> exp family -> M=F^2 -> Lorentzian")
    lines.append("```")
    lines.append("")
    lines.append("**Model**: Binary string rewriting systems with genuine confluence (CI property).")
    lines.append("Observer O = first m=3 bits. Boundary = interface region.")
    lines.append("Test: Does KL(p_actual || p_MaxEnt) decrease as N increases?")
    lines.append("")

    # Collect verdict
    positive_rules = []
    negative_rules = []
    trivial_rules = {'random_noci', 'xor_ci'}  # These are trivially uniform or near-uniform
    for rule, fit_data in fit_results.items():
        if rule in trivial_rules:
            continue
        alpha = fit_data.get('power_law', {}).get('alpha')
        if alpha is not None and alpha > 0.1:
            positive_rules.append(rule)
        elif alpha is not None and alpha < -0.1:
            negative_rules.append(rule)

    if len(positive_rules) > len(negative_rules):
        overall = "POSITIVE SIGNAL"
        confidence_update = "35% -> POSSIBLY 45-50%"
    elif len(negative_rules) > len(positive_rules):
        overall = "NEGATIVE EVIDENCE"
        confidence_update = "35% -> POSSIBLY 20-25%"
    else:
        overall = "MIXED / INCONCLUSIVE"
        confidence_update = "35% -> unchanged"

    lines.append(f"**Overall Verdict**: {overall}")
    lines.append(f"**Confidence Update**: {confidence_update}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Scaling results table
    lines.append("## 1. N-Scaling Study Results")
    lines.append("")
    lines.append("### Raw Data: KL(p_actual || p_MaxEnt) vs N")
    lines.append("")
    lines.append("Fixed observer size m=3. MaxEnt reference = uniform (MaxEnt for unconstrained binary).")
    lines.append("")

    for rule in ['swap_ci', 'flip3_ci', 'shuffle_ci', 'xor_ci', 'random_noci']:
        rule_data = [r for r in scaling_results if r['rule'] == rule]
        if not rule_data:
            continue

        type_label = "(CI)" if 'ci' in rule else "(non-CI control)"
        lines.append(f"#### {rule} {type_label}")
        lines.append("")
        lines.append("| N | Boundaries sampled | Mean KL_uniform | Std KL | Mean KL_expfam |")
        lines.append("|---|--------------------|-----------------|---------| ---------------|")

        for r in rule_data:
            kl_u = r.get('mean_kl_uniform', float('nan'))
            std_u = r.get('std_kl_uniform', float('nan'))
            kl_e = r.get('mean_kl_expfam', float('nan'))
            n_bc = r.get('n_boundary_conditions', 0)
            N = r['N']

            kl_u_str = f"{kl_u:.4f}" if not np.isnan(kl_u) else "N/A"
            std_u_str = f"{std_u:.4f}" if not np.isnan(std_u) else "N/A"
            kl_e_str = f"{kl_e:.4f}" if not np.isnan(kl_e) else "N/A"
            lines.append(f"| {N} | {n_bc} | {kl_u_str} | {std_u_str} | {kl_e_str} |")

        lines.append("")

    # Scaling fit results
    lines.append("## 2. Scaling Fit Analysis")
    lines.append("")
    lines.append("Fitting KL(N) = A * N^(-alpha).")
    lines.append("Positive alpha: KL DECREASES with N -> supports typicality.")
    lines.append("Negative alpha: KL INCREASES with N -> against typicality.")
    lines.append("")
    lines.append("| Rule | A | alpha | R^2 | Verdict |")
    lines.append("|------|---|-------|-----|---------|")

    for rule, fit_data in fit_results.items():
        power = fit_data.get('power_law', {})
        A = power.get('A')
        alpha = power.get('alpha')
        r2 = power.get('r_squared')
        verdict = power.get('verdict', 'N/A')

        A_str = f"{A:.3f}" if A is not None else "N/A"
        alpha_str = f"{alpha:.3f}" if alpha is not None else "N/A"
        r2_str = f"{r2:.3f}" if r2 is not None else "N/A"
        lines.append(f"| {rule} | {A_str} | {alpha_str} | {r2_str} | {verdict[:60]} |")

    lines.append("")

    # ExpFam fit results
    lines.append("## 3. Exponential Family Fit Quality")
    lines.append("")
    lines.append("Does p(O) converge to an exponential family as N increases?")
    lines.append("Metric: KL(p_obs || p_best_fit_expfam). Lower = closer to exp family.")
    lines.append("")

    for rule, ef_results in expfam_results.items():
        lines.append(f"#### {rule}")
        lines.append("")
        lines.append("| N | KL to exp family | Entropy (obs) | Entropy (MaxEnt) | Fraction |")
        lines.append("|---|------------------|---------------|------------------|---------|")

        for r in ef_results:
            N = r['N']
            kl_ef = r.get('kl_to_expfam', float('nan'))
            ent_obs = r.get('entropy_obs', float('nan'))
            ent_max = r.get('entropy_maxent', float('nan'))
            frac = r.get('entropy_fraction', float('nan'))

            kl_ef_str = f"{kl_ef:.4f}" if not np.isnan(kl_ef) else "N/A"
            ent_obs_str = f"{ent_obs:.3f}" if not np.isnan(ent_obs) else "N/A"
            ent_max_str = f"{ent_max:.3f}" if not np.isnan(ent_max) else "N/A"
            frac_str = f"{frac:.3f}" if not np.isnan(frac) else "N/A"

            lines.append(f"| {N} | {kl_ef_str} | {ent_obs_str} | {ent_max_str} | {frac_str} |")
        lines.append("")

    # Persistence results
    lines.append("## 4. Persistence Test")
    lines.append("")
    lines.append("Does observer persistence (inertia) accelerate MaxEnt convergence?")
    lines.append(f"Persistent: observer bits update with probability p_flip=0.1 per step.")
    lines.append("")
    lines.append("| N | KL_standard | KL_persistent | Improvement | Persistence helps? |")
    lines.append("|---|-------------|---------------|-------------|-------------------|")

    for r in persistence_results:
        N = r['N']
        kl_np = r.get('kl_nonpersistent', float('nan'))
        kl_p = r.get('kl_persistent', float('nan'))
        imp = r.get('improvement_fraction', float('nan'))
        helps = r.get('persistence_helps', False)

        kl_np_str = f"{kl_np:.4f}" if not np.isnan(kl_np) else "N/A"
        kl_p_str = f"{kl_p:.4f}" if not np.isnan(kl_p) else "N/A"
        imp_str = f"{imp:+.1%}" if not np.isnan(imp) else "N/A"
        helps_str = "YES" if helps else "NO"

        lines.append(f"| {N} | {kl_np_str} | {kl_p_str} | {imp_str} | {helps_str} |")
    lines.append("")

    # Interpretation
    lines.append("## 5. Interpretation")
    lines.append("")
    lines.append("### 5.1 What the Results Mean")
    lines.append("")

    if len(positive_rules) > 0:
        lines.append(f"**Positive signal** (KL decreasing with N): {positive_rules}")
        lines.append("")
        lines.append("For these rules, the causal typicality conjecture receives empirical support.")
        lines.append("The observer's boundary statistics become MORE uniform (closer to MaxEnt)")
        lines.append("as the system size N increases with fixed observer size m=3.")
        lines.append("")

    if len(negative_rules) > 0:
        lines.append(f"**Negative signal** (KL NOT decreasing): {negative_rules}")
        lines.append("")
        lines.append("For these rules, the conjecture is NOT supported. The observer's")
        lines.append("boundary statistics do not converge to MaxEnt as N grows.")
        lines.append("")

    lines.append("### 5.2 Model Limitations")
    lines.append("")
    lines.append("1. **Simplified CI rules**: Not actual Wolfram hypergraph rewriting.")
    lines.append("   The 'swap' rule is bubble sort (trivially CI), the 'flip3' and 'xor'")
    lines.append("   rules are approximations of CI. Real Wolfram rules have richer structure.")
    lines.append("")
    lines.append("2. **Binary string space**: Real CI hypergraphs are higher-dimensional.")
    lines.append("   Binary strings of length N are a 1D approximation.")
    lines.append("")
    lines.append("3. **Small observer**: m=3 bits -> 4 internal states. Real observers")
    lines.append("   have more degrees of freedom. The m->inf limit is unexplored.")
    lines.append("")
    lines.append("4. **Finite N**: N <= 100 may not be in the asymptotic regime.")
    lines.append("   The conjecture predicts N -> inf behavior; we test finite N.")
    lines.append("")
    lines.append("5. **Boundary definition**: The 3-bit boundary window is a choice.")
    lines.append("   Different boundary definitions may give different results.")
    lines.append("")

    lines.append("### 5.3 Confidence Assessment")
    lines.append("")
    lines.append("| Aspect | Prior | Updated | Reason |")
    lines.append("|--------|-------|---------|--------|")
    lines.append("| Typicality conjecture (strong form) | 25% | TBD | See results |")
    lines.append("| Typicality conjecture (weak form) | 40% | TBD | See results |")
    lines.append("| MaxEnt as independent axiom | 60% | TBD | See results |")
    lines.append("| CI -> exp family (via typicality) | 30% | TBD | See results |")
    lines.append("")

    if len(positive_rules) > len(negative_rules):
        lines.append("**Updated assessment**: Moderate POSITIVE signal.")
        lines.append("")
        lines.append("The results provide some empirical support for the typicality conjecture,")
        lines.append("though limited by model simplifications. The conjecture is NOT falsified")
        lines.append("and may hold in more realistic settings.")
        lines.append("")
        lines.append("**Confidence update**: 25-35% -> 35-45% (tentative, model-dependent)")
    elif len(negative_rules) > len(positive_rules):
        lines.append("**Updated assessment**: NEGATIVE results.")
        lines.append("")
        lines.append("The results suggest the typicality conjecture does not hold in this")
        lines.append("simplified model. This supports the conclusion that MaxEnt must be")
        lines.append("postulated as an independent axiom (not derived from CI alone).")
        lines.append("")
        lines.append("**Confidence update**: 25-35% -> 15-25% (model-dependent)")
    else:
        lines.append("**Updated assessment**: MIXED / INCONCLUSIVE.")
        lines.append("")
        lines.append("Results are rule-dependent. Some CI rules support typicality, others don't.")
        lines.append("This suggests the typicality conjecture may hold for SOME CI systems but")
        lines.append("not all. The physical question: which CI rules are relevant for the")
        lines.append("cosmological setting?")
        lines.append("")
        lines.append("**Confidence update**: 25-35% -> unchanged")

    lines.append("")
    lines.append("## 6. Relation to Proof Strategies")
    lines.append("")
    lines.append("### Strategy A: Levy's Lemma (Concentration on Sphere)")
    lines.append("")
    lines.append("The computational test is a DISCRETE analog of the Levy's lemma approach.")
    lines.append("If KL ~ N^(-alpha) with alpha > 0, this is consistent with concentration")
    lines.append("of measure in a space of dimension ~ N.")
    lines.append("")
    lines.append("The effective dimension of the boundary statistics variation scales as:")
    lines.append("- If KL ~ N^(-1): effective dimension ~ N (strong concentration)")
    lines.append("- If KL ~ constant: no concentration (Levy's lemma not applicable)")
    lines.append("")
    lines.append("### Strategy B: Information-Theoretic (AEP)")
    lines.append("")
    lines.append("The exp family fit test (Section 3) directly tests whether the observer")
    lines.append("distribution IS an exponential family. If KL_to_expfam decreases with N,")
    lines.append("this supports the PKD route: CI provides fixed-dim sufficient statistics.")
    lines.append("")
    lines.append("### Strategy C: Large Deviations")
    lines.append("")
    lines.append("Exponential decay KL ~ exp(-B*N) would be the STRONGEST evidence,")
    lines.append("consistent with a large deviations rate function I(eps) > 0.")
    lines.append("")

    lines.append("## Meta")
    lines.append("")
    lines.append("```yaml")
    lines.append("document: CAUSAL-TYPICALITY-CAMPAIGN-2026-02-17.md")
    lines.append("created: 2026-02-17")
    lines.append("type: computational-results")
    lines.append("campaign: CAUSAL TYPICALITY AND MAXENT CONVERGENCE")
    lines.append("")
    lines.append("model:")
    lines.append("  type: binary string rewriting (simplified CI)")
    lines.append("  observer_size: m=3")
    lines.append(f"  N_values: {all_data['parameters']['N_values']}")
    lines.append(f"  n_samples: {all_data['parameters']['n_samples']}")
    lines.append("  rules: [swap_ci, flip3_ci, xor_ci, random_noci]")
    lines.append("")
    lines.append("code: papers/structural-bridge/src/causal_typicality_corrected.py")
    lines.append("data: papers/structural-bridge/output/causal_typicality_corrected_results.json")
    lines.append("")
    lines.append("cross_references:")
    lines.append("  - CAUSAL-TYPICALITY-CONJECTURE-2026-02-16.md")
    lines.append("  - CAUSAL-TYPICALITY-FORMALIZATION-2026-02-16.md")
    lines.append("  - CI-EXPONENTIAL-FAMILY-ANALYSIS-2026-02-16.md")
    lines.append("```")

    with open(report_path, 'w') as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
