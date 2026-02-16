#!/usr/bin/env python3
"""
CI -> Exponential Family Test: Toy Model
=========================================

Tests whether causal invariance (CI) constrains observer statistics
toward exponential families.

MODEL:
  - A string rewriting system with confluence (CI analog)
  - An "observer" sub-region that collects statistics
  - We measure whether the observer's empirical distribution
    converges to an exponential family form

APPROACH:
  We build a toy confluent rewriting system on a 1D lattice of symbols.
  The observer is a small sub-region of the lattice. We:
  1. Run the rewriting in random orders (exploiting CI: all orders
     produce the same causal graph)
  2. Collect boundary statistics of the observer sub-region
  3. Test whether the empirical distribution is well-fit by an
     exponential family (Boltzmann/Ising) vs a non-exp-family model (mixture)
  4. Compare CI systems vs non-CI systems

METRICS:
  - AIC/BIC for exp-family vs mixture fits
  - KL divergence from MaxEnt distribution
  - Sufficient statistic dimensionality test (KPD-inspired)

Author: Research program CI-exponential-family investigation
Date: 2026-02-16
"""

import numpy as np
from itertools import combinations
from collections import Counter
from scipy.optimize import minimize
from scipy.special import logsumexp
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# SECTION 1: Confluent Rewriting System (CI analog)
# ============================================================

class ConfluentRewritingSystem:
    """
    A simple confluent string rewriting system.

    Rules: a set of (pattern, replacement) pairs that are confluent.
    We use a terminating confluent system (guarantees unique normal form).

    This models CI: regardless of rule application order, the final
    state (causal graph) is the same.
    """

    def __init__(self, rules, alphabet_size=3):
        """
        rules: list of (pattern, replacement) where pattern and replacement
               are tuples of symbols (integers).
        alphabet_size: number of distinct symbols
        """
        self.rules = rules
        self.alphabet_size = alphabet_size

    def find_applicable_rules(self, state):
        """Find all positions where rules can be applied."""
        applicable = []
        for rule_idx, (pattern, replacement) in enumerate(self.rules):
            plen = len(pattern)
            for pos in range(len(state) - plen + 1):
                if tuple(state[pos:pos+plen]) == pattern:
                    applicable.append((rule_idx, pos))
        return applicable

    def apply_rule(self, state, rule_idx, pos):
        """Apply a specific rule at a specific position."""
        pattern, replacement = self.rules[rule_idx]
        new_state = list(state[:pos]) + list(replacement) + list(state[pos+len(pattern):])
        return tuple(new_state)

    def reduce_to_normal_form(self, state, order='random'):
        """
        Reduce state to normal form by applying rules until no more apply.

        order: 'random' (random rule/position), 'left' (leftmost first),
               'right' (rightmost first)

        For a confluent system, all orders give the same normal form.
        """
        state = tuple(state)
        steps = 0
        history = [state]
        max_steps = 1000

        while steps < max_steps:
            applicable = self.find_applicable_rules(state)
            if not applicable:
                break

            if order == 'random':
                idx = np.random.randint(len(applicable))
            elif order == 'left':
                idx = 0  # leftmost rule application
            elif order == 'right':
                idx = len(applicable) - 1  # rightmost
            else:
                idx = 0

            rule_idx, pos = applicable[idx]
            state = self.apply_rule(state, rule_idx, pos)
            history.append(state)
            steps += 1

        return state, history


class NonConfluentRewritingSystem(ConfluentRewritingSystem):
    """
    A non-confluent rewriting system for comparison.
    Different rule orders produce DIFFERENT normal forms.
    """

    def __init__(self, rules, alphabet_size=3):
        super().__init__(rules, alphabet_size)


def make_confluent_system():
    """
    Create a confluent (CI) rewriting system.

    Rules (all reduce symbol values, guaranteeing termination):
    - (2, 2) -> (1, 0)     [two 2s become 1,0]
    - (2, 1) -> (0, 1)     [2,1 becomes 0,1]
    - (1, 2) -> (1, 0)     [1,2 becomes 1,0]
    - (2, 0) -> (0, 0)     [2,0 becomes 0,0]
    - (0, 2) -> (0, 0)     [0,2 becomes 0,0]

    These rules are confluent: all critical pairs resolve.
    Check: (2,2,1): apply rule 1 first -> (1,0,1), or rule 2 at pos 1 -> (2,0,1)
    -> (0,0,1). But (1,0,1) is normal, (0,0,1) is also normal.
    NOT confluent as stated. Let me design a properly confluent system.

    Properly confluent system: simple reduction rules.
    """
    # Use a system where all rules reduce a "weight" so it terminates,
    # and critical pairs all resolve.
    # Simplest confluent system: reduce any 2 to 1 (no overlaps possible)
    rules = [
        ((2,), (1,)),      # any 2 becomes 1
        ((1, 1), (0, 1)),  # two 1s: first becomes 0
    ]
    # Check confluence: the only critical pair is (2, 1, 1):
    # Path A: reduce 2 first -> (1, 1, 1) -> (0, 1, 1) -> (0, 0, 1)
    # Path B: reduce (1,1) at pos 1 first -> (2, 0, 1) -> (1, 0, 1)
    # These give different results! Not confluent.

    # Let me use an even simpler system: just single-symbol reductions
    # that are trivially confluent (no overlapping patterns).
    rules = [
        ((2, 0), (0, 0)),  # 2 next to 0 -> both 0
        ((0, 2), (0, 0)),  # 0 next to 2 -> both 0
        ((2, 1), (1, 1)),  # 2 next to 1 -> both 1
        ((1, 2), (1, 1)),  # 1 next to 2 -> both 1
    ]
    # These rules: 2 is "assimilated" by its neighbors.
    # Critical pair: (2, 1, 2):
    # Path A: apply at pos 0 -> (1, 1, 2) -> (1, 1, 1)
    # Path B: apply at pos 1 -> (2, 1, 1) -> (1, 1, 1)
    # Both give (1,1,1). Confluent!
    # Critical pair: (0, 2, 1):
    # Path A: apply at pos 0 -> (0, 0, 1)
    # Path B: apply at pos 1 -> (0, 1, 1)
    # Different! NOT confluent.

    # Actually designing a confluent system requires care.
    # Let me use the simplest approach: a system with no overlapping patterns.

    # Non-overlapping confluent system:
    # Rules operate on isolated symbols, so no critical pairs exist.
    rules = [
        ((2,), (0,)),  # Replace any 2 with 0
    ]
    # Trivially confluent (single-symbol rules can't overlap)
    # but too simple to be interesting.

    # Better: use a Markov chain on pairs with guaranteed confluence
    # by making all rules strictly decrease a well-ordering.

    # Let's use the "bubble sort" rules: swap (b, a) -> (a, b) if b > a
    # This is the classic confluent string rewriting system.
    rules = [
        ((2, 0), (0, 2)),  # swap 2,0 -> 0,2
        ((2, 1), (1, 2)),  # swap 2,1 -> 1,2
        ((1, 0), (0, 1)),  # swap 1,0 -> 0,1
    ]
    # This IS confluent (well-known result). Normal form = sorted string.
    # Termination: each swap reduces the number of inversions.
    # Confluence: follows from the fact that any two swaps on disjoint
    # positions commute, and overlapping critical pairs resolve.
    # (1,0,2): Path A: swap at 0 -> (0,1,2). Path B: no other rule applies.
    # (2,1,0): Path A: swap at 0 -> (1,2,0) -> (1,0,2) -> (0,1,2).
    #          Path B: swap at 1 -> (2,0,1) -> (0,2,1) -> (0,1,2). Same!

    return ConfluentRewritingSystem(rules, alphabet_size=3)


def make_non_confluent_system():
    """
    Create a non-confluent system for comparison.
    Different rule orders produce different results.
    """
    rules = [
        ((2, 1), (0, 0)),  # 2,1 -> 0,0
        ((1, 0), (2, 2)),  # 1,0 -> 2,2
    ]
    # (2, 1, 0):
    # Path A: apply rule 1 at pos 0 -> (0, 0, 0) [normal form]
    # Path B: apply rule 2 at pos 1 -> (2, 2, 2) [then no rule applies -> normal]
    # Different normal forms! Not confluent.
    return NonConfluentRewritingSystem(rules, alphabet_size=3)


# ============================================================
# SECTION 2: Observer and Statistics Collection
# ============================================================

class Observer:
    """
    An observer watching a sub-region of the rewriting system.

    The observer sees a window of the lattice and collects statistics
    about the symbol configurations in that window.
    """

    def __init__(self, window_start, window_size):
        self.window_start = window_start
        self.window_size = window_size

    def observe(self, state):
        """Extract the observer's view of the state."""
        end = min(self.window_start + self.window_size, len(state))
        return tuple(state[self.window_start:end])

    def compute_statistics(self, observation):
        """
        Compute sufficient statistics of the observation.

        For an Ising-like model on the observer's sub-region:
        T_1 = sum of symbols (magnetization-like)
        T_2 = sum of neighbor products (correlation-like)
        """
        obs = np.array(observation)
        n = len(obs)

        if n == 0:
            return np.array([0.0, 0.0])

        # T1: mean value (magnetization analog)
        t1 = np.mean(obs)

        # T2: nearest-neighbor correlation (Ising coupling analog)
        if n > 1:
            t2 = np.mean(obs[:-1] * obs[1:])
        else:
            t2 = 0.0

        return np.array([t1, t2])


# ============================================================
# SECTION 3: Statistical Testing
# ============================================================

def fit_exponential_family(observations, k=2):
    """
    Fit a canonical exponential family to observed configurations.

    For binary/ternary configurations of length L:
    p(x | theta) = exp(theta . T(x) - A(theta)) * h(x)

    where T(x) = sufficient statistics, A = log partition function.

    Returns: theta (parameters), log_likelihood, AIC
    """
    # Compute sufficient statistics for each observation
    obs_array = np.array(observations)
    n_obs, L = obs_array.shape

    # Sufficient statistics: [mean, neighbor_correlation]
    T_all = np.zeros((n_obs, k))
    for i in range(n_obs):
        T_all[i, 0] = np.mean(obs_array[i])
        if L > 1:
            T_all[i, 1] = np.mean(obs_array[i, :-1] * obs_array[i, 1:])

    # Empirical means of sufficient statistics
    T_mean = np.mean(T_all, axis=0)

    # For a discrete exponential family, we need to enumerate all possible states
    # and fit theta via maximum likelihood.
    # For small L, enumerate all states.
    alphabet_size = int(obs_array.max()) + 1

    if L <= 6:  # Enumerable
        all_states = _enumerate_states(L, alphabet_size)

        def neg_log_likelihood(theta):
            # Compute log-partition function
            log_probs = []
            for state in all_states:
                s = np.array(state)
                t = np.array([np.mean(s), np.mean(s[:-1]*s[1:]) if L > 1 else 0.0])
                log_probs.append(np.dot(theta, t))
            A = logsumexp(log_probs)

            # Log-likelihood
            ll = 0.0
            for i in range(n_obs):
                ll += np.dot(theta, T_all[i]) - A
            return -ll / n_obs

        # Optimize
        result = minimize(neg_log_likelihood, np.zeros(k), method='L-BFGS-B')
        theta_opt = result.x
        nll = result.fun * n_obs

        # AIC = 2k - 2*log_likelihood
        aic = 2 * k + 2 * nll
        bic = k * np.log(n_obs) + 2 * nll

        return theta_opt, -nll, aic, bic
    else:
        # For larger L, use moment matching (approximate)
        # This is the MLE for exponential families
        T_mean = np.mean(T_all, axis=0)
        return T_mean, 0.0, np.inf, np.inf  # Placeholder


def fit_mixture_model(observations, n_components=2):
    """
    Fit a mixture model (non-exponential family) to observed configurations.

    p(x | pi, params) = sum_k pi_k * p_k(x | params_k)

    Uses EM algorithm.
    Returns: params, log_likelihood, AIC
    """
    obs_array = np.array(observations)
    n_obs, L = obs_array.shape
    alphabet_size = int(obs_array.max()) + 1

    if L > 6:
        return None, -np.inf, np.inf, np.inf

    all_states = _enumerate_states(L, alphabet_size)
    n_states = len(all_states)

    # Initialize mixture components with random probabilities
    # Each component is a categorical distribution over states
    np.random.seed(42)
    component_probs = np.random.dirichlet(np.ones(n_states), size=n_components)
    mixing_weights = np.ones(n_components) / n_components

    # Map observations to state indices
    state_to_idx = {tuple(s): i for i, s in enumerate(all_states)}
    obs_indices = [state_to_idx.get(tuple(o), 0) for o in obs_array]

    # EM iterations
    for _ in range(50):
        # E-step: compute responsibilities
        responsibilities = np.zeros((n_obs, n_components))
        for i, idx in enumerate(obs_indices):
            for k in range(n_components):
                responsibilities[i, k] = mixing_weights[k] * component_probs[k, idx]
            total = responsibilities[i].sum()
            if total > 0:
                responsibilities[i] /= total
            else:
                responsibilities[i] = 1.0 / n_components

        # M-step: update parameters
        N_k = responsibilities.sum(axis=0) + 1e-10
        mixing_weights = N_k / n_obs

        for k in range(n_components):
            counts = np.zeros(n_states)
            for i, idx in enumerate(obs_indices):
                counts[idx] += responsibilities[i, k]
            component_probs[k] = (counts + 1e-10) / (N_k[k] + n_states * 1e-10)

    # Compute log-likelihood
    ll = 0.0
    for i, idx in enumerate(obs_indices):
        p = sum(mixing_weights[k] * component_probs[k, idx] for k in range(n_components))
        ll += np.log(max(p, 1e-300))

    n_params = n_components * n_states + n_components - 1  # All component probs + mixing weights
    aic = 2 * n_params - 2 * ll
    bic = n_params * np.log(n_obs) - 2 * ll

    return (mixing_weights, component_probs), ll, aic, bic


def _enumerate_states(L, alphabet_size):
    """Enumerate all possible states of length L with given alphabet."""
    if L == 0:
        return [()]
    states = []
    for i in range(alphabet_size**L):
        state = []
        val = i
        for _ in range(L):
            state.append(val % alphabet_size)
            val //= alphabet_size
        states.append(tuple(state))
    return states


def compute_maxent_distance(observations, k=2):
    """
    Compute the KL divergence from the empirical distribution to the
    MaxEnt distribution with the same expected sufficient statistics.

    Small KL divergence = observer is close to MaxEnt = exponential family.
    """
    obs_array = np.array(observations)
    n_obs, L = obs_array.shape
    alphabet_size = int(obs_array.max()) + 1

    if L > 6:
        return np.inf

    all_states = _enumerate_states(L, alphabet_size)
    n_states = len(all_states)

    # Compute empirical distribution
    state_to_idx = {tuple(s): i for i, s in enumerate(all_states)}
    empirical = np.zeros(n_states)
    for o in obs_array:
        idx = state_to_idx.get(tuple(o), 0)
        empirical[idx] += 1
    empirical /= empirical.sum()
    empirical = np.maximum(empirical, 1e-300)  # Avoid log(0)

    # Fit exponential family (MaxEnt with same moments)
    theta_opt, _, _, _ = fit_exponential_family(observations, k)

    # Compute MaxEnt distribution
    maxent = np.zeros(n_states)
    for i, state in enumerate(all_states):
        s = np.array(state)
        t = np.array([np.mean(s), np.mean(s[:-1]*s[1:]) if L > 1 else 0.0])
        maxent[i] = np.dot(theta_opt, t)
    maxent -= logsumexp(maxent)
    maxent = np.exp(maxent)
    maxent = np.maximum(maxent, 1e-300)

    # KL divergence D_KL(empirical || maxent)
    kl = np.sum(empirical * np.log(empirical / maxent))

    return kl


def test_sufficient_statistic_dimension(observations, max_dim=5):
    """
    Test whether the empirical distribution has fixed-dimensional
    sufficient statistics (KPD-inspired test).

    Method: fit exponential families of dimension 1, 2, ..., max_dim
    and check where the log-likelihood saturates.

    If it saturates at dimension k, the data is consistent with a
    k-dimensional exponential family.
    """
    obs_array = np.array(observations)
    n_obs, L = obs_array.shape
    alphabet_size = int(obs_array.max()) + 1

    if L > 5:
        return {'saturating_dim': None, 'log_likelihoods': [], 'message': 'L too large'}

    all_states = _enumerate_states(L, alphabet_size)
    n_states = len(all_states)

    # Define sufficient statistics of increasing dimension
    def compute_T(state, dim):
        s = np.array(state, dtype=float)
        T = []
        if dim >= 1:
            T.append(np.mean(s))  # Mean
        if dim >= 2 and L > 1:
            T.append(np.mean(s[:-1] * s[1:]))  # Neighbor correlation
        if dim >= 3:
            T.append(np.var(s))  # Variance
        if dim >= 4 and L > 2:
            T.append(np.mean(s[:-2] * s[2:]))  # Next-nearest neighbor
        if dim >= 5:
            T.append(np.mean(s**2))  # Second moment
        return np.array(T[:dim])

    results = []
    for dim in range(1, max_dim + 1):
        actual_dim = len(compute_T(all_states[0], dim))
        if actual_dim == 0:
            continue

        # Fit exponential family of this dimension
        T_all = np.array([compute_T(state, dim) for state in all_states])

        # Map observations to indices
        state_to_idx = {tuple(s): i for i, s in enumerate(all_states)}
        obs_indices = [state_to_idx.get(tuple(o), 0) for o in obs_array]

        # Compute empirical T means
        T_obs = np.array([compute_T(tuple(obs_array[i]), dim) for i in range(n_obs)])
        T_mean = np.mean(T_obs, axis=0)

        def neg_ll(theta):
            log_probs = T_all @ theta
            A = logsumexp(log_probs)
            ll = np.mean(T_obs @ theta) - A
            return -ll

        try:
            result = minimize(neg_ll, np.zeros(actual_dim), method='L-BFGS-B')
            ll = -result.fun * n_obs
            aic = 2 * actual_dim - 2 * ll
            results.append({'dim': actual_dim, 'll': ll, 'aic': aic})
        except Exception:
            results.append({'dim': actual_dim, 'll': -np.inf, 'aic': np.inf})

    # Find saturating dimension (where adding more dims doesn't help)
    if len(results) < 2:
        return {'saturating_dim': 1, 'results': results}

    sat_dim = 1
    for i in range(1, len(results)):
        improvement = results[i]['ll'] - results[i-1]['ll']
        if improvement > 1.0:  # Significant improvement
            sat_dim = results[i]['dim']

    return {'saturating_dim': sat_dim, 'results': results}


# ============================================================
# SECTION 4: Main Experiment
# ============================================================

def run_experiment(n_initial_states=200, lattice_size=8, observer_window=4,
                   n_reduction_orders=5, verbose=True):
    """
    Main experiment: compare CI vs non-CI systems.

    For each system:
    1. Generate random initial states
    2. Reduce to normal form (for CI: multiple orders, should give same result)
    3. Observer collects statistics from the observer window
    4. Test whether statistics are exponential family
    """

    ci_system = make_confluent_system()
    non_ci_system = make_non_confluent_system()

    results = {}

    for system_name, system in [("CI (confluent)", ci_system),
                                  ("non-CI", non_ci_system)]:
        if verbose:
            print(f"\n{'='*60}")
            print(f"System: {system_name}")
            print(f"{'='*60}")

        observer = Observer(window_start=0, window_size=observer_window)
        all_observations = []
        confluence_violations = 0

        for trial in range(n_initial_states):
            # Generate random initial state
            state = tuple(np.random.randint(0, 3, size=lattice_size))

            # Reduce using multiple orders
            normal_forms = []
            for order in ['random', 'left', 'right']:
                nf, history = system.reduce_to_normal_form(state, order=order)
                normal_forms.append(nf)

            # Check confluence
            if len(set(normal_forms)) > 1:
                confluence_violations += 1

            # Observer watches the normal form
            # For CI: all orders give same observation
            # For non-CI: different orders may give different observations
            for nf in normal_forms[:1]:  # Take first for CI (all same)
                obs = observer.observe(nf)
                if len(obs) == observer_window:
                    all_observations.append(obs)

        if verbose:
            print(f"  Trials: {n_initial_states}")
            print(f"  Confluence violations: {confluence_violations}/{n_initial_states}")
            print(f"  Observations collected: {len(all_observations)}")

        if len(all_observations) < 10:
            if verbose:
                print("  Too few observations for analysis.")
            results[system_name] = {'status': 'insufficient_data'}
            continue

        observations = np.array(all_observations)

        # Test 1: Fit exponential family
        theta_ef, ll_ef, aic_ef, bic_ef = fit_exponential_family(
            observations, k=2)

        # Test 2: Fit mixture model
        params_mix, ll_mix, aic_mix, bic_mix = fit_mixture_model(
            observations, n_components=2)

        # Test 3: MaxEnt distance
        kl_maxent = compute_maxent_distance(observations, k=2)

        # Test 4: Sufficient statistic dimension
        ssd = test_sufficient_statistic_dimension(observations)

        if verbose:
            print(f"\n  --- Exponential Family Fit ---")
            print(f"  theta = {theta_ef}")
            print(f"  Log-likelihood: {ll_ef:.2f}")
            print(f"  AIC: {aic_ef:.2f}, BIC: {bic_ef:.2f}")

            print(f"\n  --- Mixture Model Fit (2 components) ---")
            print(f"  Log-likelihood: {ll_mix:.2f}")
            print(f"  AIC: {aic_mix:.2f}, BIC: {bic_mix:.2f}")

            print(f"\n  --- Model Selection ---")
            if aic_ef < aic_mix:
                print(f"  AIC prefers: EXPONENTIAL FAMILY (delta = {aic_mix - aic_ef:.2f})")
            else:
                print(f"  AIC prefers: MIXTURE MODEL (delta = {aic_ef - aic_mix:.2f})")

            if bic_ef < bic_mix:
                print(f"  BIC prefers: EXPONENTIAL FAMILY (delta = {bic_mix - bic_ef:.2f})")
            else:
                print(f"  BIC prefers: MIXTURE MODEL (delta = {bic_ef - bic_mix:.2f})")

            print(f"\n  --- MaxEnt Distance ---")
            print(f"  KL(empirical || MaxEnt) = {kl_maxent:.6f}")
            if kl_maxent < 0.01:
                print(f"  Assessment: VERY CLOSE to MaxEnt (< 0.01)")
            elif kl_maxent < 0.1:
                print(f"  Assessment: CLOSE to MaxEnt (< 0.1)")
            elif kl_maxent < 0.5:
                print(f"  Assessment: MODERATE deviation from MaxEnt")
            else:
                print(f"  Assessment: FAR from MaxEnt")

            print(f"\n  --- Sufficient Statistic Dimension ---")
            print(f"  Saturating dimension: {ssd.get('saturating_dim', 'N/A')}")
            if 'results' in ssd:
                for r in ssd['results']:
                    print(f"    dim={r['dim']}: LL={r['ll']:.2f}, AIC={r['aic']:.2f}")

        results[system_name] = {
            'n_observations': len(all_observations),
            'confluence_violations': confluence_violations,
            'exp_family': {'theta': theta_ef, 'll': ll_ef, 'aic': aic_ef, 'bic': bic_ef},
            'mixture': {'ll': ll_mix, 'aic': aic_mix, 'bic': bic_mix},
            'maxent_distance': kl_maxent,
            'suff_stat_dim': ssd
        }

    return results


def run_persistence_test(n_trials=100, lattice_size=10, verbose=True):
    """
    Test whether "persistent" patterns (those that survive rewriting)
    have statistics closer to MaxEnt than transient patterns.

    This tests the CI + persistence -> MaxEnt conjecture.
    """
    if verbose:
        print(f"\n{'='*60}")
        print("PERSISTENCE TEST: Do persistent patterns have MaxEnt statistics?")
        print(f"{'='*60}")

    ci_system = make_confluent_system()

    persistent_observations = []
    transient_observations = []

    observer_window = 3
    observer = Observer(0, observer_window)

    for trial in range(n_trials):
        state = tuple(np.random.randint(0, 3, size=lattice_size))
        nf, history = ci_system.reduce_to_normal_form(state, order='random')

        if len(history) < 2:
            continue

        # "Persistent" observation: the normal form (survived all rewriting)
        obs_persistent = observer.observe(nf)
        if len(obs_persistent) == observer_window:
            persistent_observations.append(obs_persistent)

        # "Transient" observation: an intermediate state
        mid_idx = len(history) // 2
        obs_transient = observer.observe(history[mid_idx])
        if len(obs_transient) == observer_window:
            transient_observations.append(obs_transient)

    if len(persistent_observations) < 10 or len(transient_observations) < 10:
        if verbose:
            print("  Insufficient data for persistence test.")
        return None

    # Compare MaxEnt distances
    kl_persistent = compute_maxent_distance(np.array(persistent_observations))
    kl_transient = compute_maxent_distance(np.array(transient_observations))

    if verbose:
        print(f"\n  Persistent observations: {len(persistent_observations)}")
        print(f"  Transient observations: {len(transient_observations)}")
        print(f"\n  KL(persistent || MaxEnt) = {kl_persistent:.6f}")
        print(f"  KL(transient  || MaxEnt) = {kl_transient:.6f}")

        if kl_persistent < kl_transient:
            ratio = kl_transient / max(kl_persistent, 1e-10)
            print(f"\n  RESULT: Persistent patterns are {ratio:.1f}x CLOSER to MaxEnt")
            print(f"  This SUPPORTS the CI + persistence -> MaxEnt conjecture")
        else:
            ratio = kl_persistent / max(kl_transient, 1e-10)
            print(f"\n  RESULT: Transient patterns are {ratio:.1f}x CLOSER to MaxEnt")
            print(f"  This DOES NOT SUPPORT the conjecture")

    return {
        'kl_persistent': kl_persistent,
        'kl_transient': kl_transient,
        'n_persistent': len(persistent_observations),
        'n_transient': len(transient_observations),
        'supports_conjecture': kl_persistent < kl_transient
    }


def run_typicality_test(n_trials=300, lattice_sizes=[6, 8, 10, 12],
                         observer_window=3, verbose=True):
    """
    Test the "causal typicality" conjecture (Conjecture 9.1 from
    CI-PERSISTENCE-MAXENT):

    For large CI hypergraphs, the observer's boundary statistics
    should be approximately MaxEnt, with the approximation improving
    as the system size grows.

    We test: does KL(observer || MaxEnt) decrease with lattice size N?
    """
    if verbose:
        print(f"\n{'='*60}")
        print("TYPICALITY TEST: Does MaxEnt distance decrease with system size?")
        print(f"{'='*60}")

    ci_system = make_confluent_system()
    observer = Observer(0, observer_window)

    results = []

    for N in lattice_sizes:
        observations = []
        for trial in range(n_trials):
            state = tuple(np.random.randint(0, 3, size=N))
            nf, _ = ci_system.reduce_to_normal_form(state, order='random')
            obs = observer.observe(nf)
            if len(obs) == observer_window:
                observations.append(obs)

        if len(observations) < 20:
            results.append({'N': N, 'kl': np.inf, 'n_obs': len(observations)})
            continue

        kl = compute_maxent_distance(np.array(observations))
        results.append({'N': N, 'kl': kl, 'n_obs': len(observations)})

        if verbose:
            print(f"  N={N:3d}: KL(obs || MaxEnt) = {kl:.6f} "
                  f"(n_obs={len(observations)})")

    # Check if KL decreases with N
    kl_values = [r['kl'] for r in results if r['kl'] < np.inf]
    if len(kl_values) >= 2:
        trend = np.polyfit(range(len(kl_values)), kl_values, 1)
        decreasing = trend[0] < 0

        if verbose:
            print(f"\n  Trend (linear fit slope): {trend[0]:.6f}")
            if decreasing:
                print(f"  RESULT: KL DECREASES with system size")
                print(f"  This SUPPORTS the causal typicality conjecture")
            else:
                print(f"  RESULT: KL does NOT decrease with system size")
                print(f"  This DOES NOT SUPPORT the conjecture")

    return results


# ============================================================
# SECTION 5: Entry Point
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("CI -> EXPONENTIAL FAMILY TEST")
    print("Testing whether causal invariance constrains observer statistics")
    print("toward exponential families")
    print("=" * 70)

    # Test 1: Basic CI vs non-CI comparison
    print("\n\n" + "#" * 70)
    print("TEST 1: CI vs non-CI system -- exponential family fit comparison")
    print("#" * 70)
    results = run_experiment(
        n_initial_states=500,
        lattice_size=8,
        observer_window=4,
        verbose=True
    )

    # Test 2: Persistence test
    print("\n\n" + "#" * 70)
    print("TEST 2: Do persistent patterns have MaxEnt statistics?")
    print("#" * 70)
    persistence_results = run_persistence_test(
        n_trials=500,
        lattice_size=10,
        verbose=True
    )

    # Test 3: Typicality test
    print("\n\n" + "#" * 70)
    print("TEST 3: Causal typicality -- does MaxEnt distance scale with size?")
    print("#" * 70)
    typicality_results = run_typicality_test(
        n_trials=500,
        lattice_sizes=[6, 8, 10, 12, 16],
        observer_window=3,
        verbose=True
    )

    # Summary
    print("\n\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print("\n1. CI vs non-CI:")
    for name, r in results.items():
        if 'maxent_distance' in r:
            print(f"   {name}: KL to MaxEnt = {r['maxent_distance']:.6f}")

    print("\n2. Persistence test:")
    if persistence_results:
        print(f"   Persistent KL: {persistence_results['kl_persistent']:.6f}")
        print(f"   Transient KL:  {persistence_results['kl_transient']:.6f}")
        print(f"   Supports conjecture: {persistence_results['supports_conjecture']}")

    print("\n3. Typicality test:")
    for r in typicality_results:
        print(f"   N={r['N']}: KL = {r['kl']:.6f}")

    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print("""
Key question: Does CI force exponential family statistics?

This toy model tests three aspects:
1. Whether CI systems produce observations better fit by exponential
   families than non-CI systems (basic comparison)
2. Whether persistent patterns (normal forms) are closer to MaxEnt
   than transient patterns (CI + persistence -> MaxEnt conjecture)
3. Whether MaxEnt distance decreases with system size (causal
   typicality conjecture)

IMPORTANT CAVEATS:
- This is a TOY MODEL. The confluent rewriting system (bubble sort)
  is much simpler than a Wolfram-style hypergraph system.
- The "observer" is a window function, not a true persistent
  sub-hypergraph with self-maintaining dynamics.
- The sufficient statistics used (mean, correlation) are pre-specified,
  not derived from the system dynamics.
- The results are suggestive, not definitive.

The real theoretical question requires formal proof, not just
numerical evidence. See CI-EXPONENTIAL-FAMILY-ANALYSIS-2026-02-16.md
for the rigorous analysis.
""")
