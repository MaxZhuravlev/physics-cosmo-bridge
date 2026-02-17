#!/usr/bin/env python3
"""
Numerical Verification: Explicit Constants for Theorem B
=========================================================

Verifies the explicit bounds derived in explicit-constants-proposition-B.md
against exact Ising Fisher matrix computations.

Tests:
1. Gamma(kappa) controls the signed kernel perturbation
2. W(q=1) lower bound is conservative (does not exceed actual)
3. W(q>=2) upper bound holds
4. Margin bound holds for all tested configurations
5. Threshold epsilon_0 is correct (margin positive when eps < eps_0)

Author: Max Zhuravlev
Date: 2026-02-17
"""

import numpy as np
from scipy import linalg as la
from itertools import product, combinations
from typing import List, Tuple, Dict


# ========================================================================
# Section 1: Exact Ising computation
# ========================================================================

def compute_exact_fisher(n_vertices: int, edges: List[Tuple[int, int]],
                         J: float) -> np.ndarray:
    """Compute exact Fisher information matrix for Ising model."""
    m = len(edges)
    states = np.array(list(product([-1, 1], repeat=n_vertices)))
    phi = np.zeros((len(states), m))
    for idx, (i, j) in enumerate(edges):
        phi[:, idx] = states[:, i] * states[:, j]
    energy = -J * phi.sum(axis=1)
    energy -= energy.max()
    weights = np.exp(-energy)
    probs = weights / weights.sum()
    mean_phi = probs @ phi
    F = np.zeros((m, m))
    for a in range(m):
        for b in range(m):
            F[a, b] = np.sum(probs * phi[:, a] * phi[:, b]) - mean_phi[a] * mean_phi[b]
    return F


def compute_W(F: np.ndarray, q: int) -> float:
    """Compute optimal W(q) = max over q-sign assignments of mu_2 - mu_1."""
    m = F.shape[0]
    if q == 0 or q == m:
        return 0.0
    best_W = -np.inf
    F_sqrt = la.sqrtm(F).real
    for neg_indices in combinations(range(m), q):
        signs = np.ones(m)
        for idx in neg_indices:
            signs[idx] = -1
        S = np.diag(signs)
        A = F_sqrt @ S @ F_sqrt
        eigs = np.sort(la.eigvalsh(A))
        mu1, mu2 = eigs[0], eigs[1]
        if mu1 >= 0:
            continue
        W = mu2 - mu1
        best_W = max(best_W, W)
    return best_W if best_W > -np.inf else 0.0


# ========================================================================
# Section 2: Explicit constants from Theorem B
# ========================================================================

def Gamma(kappa: float) -> float:
    """Kernel perturbation constant Gamma(kappa) = sqrt(2*kappa) + 1/4."""
    return np.sqrt(2 * kappa) + 0.25


def epsilon_0(f_min: float, f_max: float) -> float:
    """Explicit threshold epsilon_0 = f_min / (2 * Gamma(kappa))."""
    kappa = f_max / f_min
    return f_min / (2 * Gamma(kappa))


def predicted_margin_lower_bound(f_min: float, f_max: float, eps: float) -> float:
    """Predicted lower bound on W(q=1) - max_{q>=2} W(q)."""
    kappa = f_max / f_min
    G = Gamma(kappa)
    return 2 * f_min - 4 * eps * G


def predicted_W1_lower(f_min: float, f_max: float, eps: float) -> float:
    """Predicted lower bound on W(q=1)."""
    kappa = f_max / f_min
    G = Gamma(kappa)
    return f_min + f_max - 2 * eps * G


def predicted_W2_upper(f_min: float, f_max: float, eps: float) -> float:
    """Predicted upper bound on max_{q>=2} W(q)."""
    kappa = f_max / f_min
    G = Gamma(kappa)
    return (f_max - f_min) + 2 * eps * G


# ========================================================================
# Section 3: Graph generators
# ========================================================================

def cycle_graph(g: int) -> Tuple[int, List[Tuple[int, int]]]:
    return g, [(i, (i + 1) % g) for i in range(g)]


def path_graph(n: int) -> Tuple[int, List[Tuple[int, int]]]:
    return n, [(i, i + 1) for i in range(n - 1)]


def star_graph(n: int) -> Tuple[int, List[Tuple[int, int]]]:
    return n, [(0, i) for i in range(1, n)]


def petersen_graph() -> Tuple[int, List[Tuple[int, int]]]:
    outer = [(i, (i + 1) % 5) for i in range(5)]
    inner = [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
    connect = [(i, i + 5) for i in range(5)]
    return 10, outer + inner + connect


def complete_graph(n: int) -> Tuple[int, List[Tuple[int, int]]]:
    return n, [(i, j) for i in range(n) for j in range(i + 1, n)]


# ========================================================================
# Section 4: Verification tests
# ========================================================================

def test_single_configuration(name: str, n: int,
                              edges: List[Tuple[int, int]],
                              J: float) -> Dict:
    """Test all bounds for a single graph configuration."""
    m = len(edges)
    F = compute_exact_fisher(n, edges, J)

    # Decompose: D = diag(F), eps*E = off-diagonal
    D = np.diag(np.diag(F))
    off_diag = F - D
    eps = la.norm(off_diag, ord=2) if la.norm(off_diag, ord=2) > 1e-15 else 0.0

    f_min_val = np.min(np.diag(F))
    f_max_val = np.max(np.diag(F))
    kappa_val = f_max_val / f_min_val if f_min_val > 0 else np.inf

    # Check hypothesis H1
    h1_satisfied = eps < f_min_val / 2

    # Compute threshold
    eps0 = epsilon_0(f_min_val, f_max_val) if f_min_val > 0 else 0.0
    within_threshold = eps < eps0

    # Compute actual W values
    W1_actual = compute_W(F, 1)
    q_range = list(range(2, min(m, 6)))
    W2_max_actual = max((compute_W(F, q) for q in q_range), default=0.0)

    actual_margin = W1_actual - W2_max_actual

    # Compute predicted bounds
    W1_lower = predicted_W1_lower(f_min_val, f_max_val, eps)
    W2_upper = predicted_W2_upper(f_min_val, f_max_val, eps)
    margin_lower = predicted_margin_lower_bound(f_min_val, f_max_val, eps)

    # Check bound validity
    W1_bound_holds = W1_actual >= W1_lower - 1e-10  # small tolerance
    W2_bound_holds = W2_max_actual <= W2_upper + 1e-10
    margin_bound_holds = actual_margin >= margin_lower - 1e-10

    # If within threshold, margin should be positive
    if within_threshold:
        margin_positive = actual_margin > 0
    else:
        margin_positive = None  # not guaranteed

    return {
        'name': name,
        'n': n,
        'm': m,
        'J': J,
        'f_min': f_min_val,
        'f_max': f_max_val,
        'kappa': kappa_val,
        'epsilon': eps,
        'epsilon_0': eps0,
        'Gamma': Gamma(kappa_val),
        'h1_satisfied': h1_satisfied,
        'within_threshold': within_threshold,
        'W1_actual': W1_actual,
        'W1_lower_bound': W1_lower,
        'W1_bound_holds': W1_bound_holds,
        'W2_max_actual': W2_max_actual,
        'W2_upper_bound': W2_upper,
        'W2_bound_holds': W2_bound_holds,
        'actual_margin': actual_margin,
        'margin_lower_bound': margin_lower,
        'margin_bound_holds': margin_bound_holds,
        'margin_positive': margin_positive,
    }


def run_all_tests():
    """Run verification on all graph configurations."""
    print("=" * 90)
    print("NUMERICAL VERIFICATION: EXPLICIT CONSTANTS FOR THEOREM B")
    print("=" * 90)
    print()

    # Define test configurations
    configs = []

    # Trees (epsilon = 0)
    for n in [3, 5, 8]:
        configs.append(("Path P%d" % n, *path_graph(n)))
    for n in [5, 8]:
        configs.append(("Star S%d" % n, *star_graph(n)))

    # Cycles (small epsilon)
    for g in [4, 5, 6, 7, 8, 10, 12]:
        if 2**g <= 2**14:
            configs.append(("Cycle C%d" % g, *cycle_graph(g)))

    # Dense graphs (large epsilon)
    for n in [4, 5]:
        configs.append(("Complete K%d" % n, *complete_graph(n)))

    # Petersen
    configs.append(("Petersen", *petersen_graph()))

    J_values = [0.3, 0.5, 1.0]

    # Run tests
    all_results = []
    total = 0
    passed_W1 = 0
    passed_W2 = 0
    passed_margin = 0
    passed_positive = 0
    total_threshold = 0

    for name, n, edges in configs:
        for J in J_values:
            if 2**n > 2**14:
                continue
            total += 1
            result = test_single_configuration(name, n, edges, J)
            all_results.append(result)

            if result['W1_bound_holds']:
                passed_W1 += 1
            if result['W2_bound_holds']:
                passed_W2 += 1
            if result['margin_bound_holds']:
                passed_margin += 1
            if result['within_threshold']:
                total_threshold += 1
                if result['margin_positive']:
                    passed_positive += 1

    # Print results table
    print(f"{'Config':<14} {'J':>4} {'f_min':>7} {'eps':>8} {'eps_0':>8} "
          f"{'W1_act':>8} {'W1_lb':>8} {'W1ok':>5} "
          f"{'W2_act':>8} {'W2_ub':>8} {'W2ok':>5} "
          f"{'margin':>8} {'m_lb':>8} {'mok':>5}")
    print("-" * 130)

    for r in all_results:
        tag = "*" if not r['within_threshold'] else " "
        print(f"{r['name']:<14} {r['J']:>4.1f} {r['f_min']:>7.4f} "
              f"{r['epsilon']:>8.5f} {r['epsilon_0']:>8.5f} "
              f"{r['W1_actual']:>8.4f} {r['W1_lower_bound']:>8.4f} "
              f"{'Y' if r['W1_bound_holds'] else 'N':>5} "
              f"{r['W2_max_actual']:>8.4f} {r['W2_upper_bound']:>8.4f} "
              f"{'Y' if r['W2_bound_holds'] else 'N':>5} "
              f"{r['actual_margin']:>8.4f} {r['margin_lower_bound']:>8.4f} "
              f"{'Y' if r['margin_bound_holds'] else 'N':>5}{tag}")

    # Summary
    print()
    print("=" * 90)
    print("SUMMARY")
    print("=" * 90)
    print(f"Total configurations tested:      {total}")
    print(f"W(q=1) lower bound holds:         {passed_W1}/{total} "
          f"({100*passed_W1/total:.1f}%)")
    print(f"W(q>=2) upper bound holds:         {passed_W2}/{total} "
          f"({100*passed_W2/total:.1f}%)")
    print(f"Margin lower bound holds:          {passed_margin}/{total} "
          f"({100*passed_margin/total:.1f}%)")
    print(f"Within threshold (eps < eps_0):    {total_threshold}/{total}")
    print(f"Margin positive when in threshold: {passed_positive}/{total_threshold} "
          f"({100*passed_positive/total_threshold:.1f}%)" if total_threshold > 0 else "N/A")
    print()

    # Detailed analysis of failures
    failures = [r for r in all_results if not r['W1_bound_holds']
                or not r['W2_bound_holds'] or not r['margin_bound_holds']]
    if failures:
        print("FAILURES (bounds violated):")
        print("-" * 60)
        for r in failures:
            issues = []
            if not r['W1_bound_holds']:
                issues.append(f"W1: actual={r['W1_actual']:.4f} < bound={r['W1_lower_bound']:.4f}")
            if not r['W2_bound_holds']:
                issues.append(f"W2: actual={r['W2_max_actual']:.4f} > bound={r['W2_upper_bound']:.4f}")
            if not r['margin_bound_holds']:
                issues.append(f"margin: actual={r['actual_margin']:.4f} < bound={r['margin_lower_bound']:.4f}")
            print(f"  {r['name']} J={r['J']}: {'; '.join(issues)}")
            print(f"    eps={r['epsilon']:.6f}, eps_0={r['epsilon_0']:.6f}, "
                  f"within_threshold={r['within_threshold']}")
    else:
        print("ALL BOUNDS HOLD -- Theorem B with explicit constants is numerically verified.")

    # Check threshold correctness: when eps >= eps_0, do we ever see q=1 lose?
    beyond_threshold = [r for r in all_results if not r['within_threshold']]
    if beyond_threshold:
        print()
        print("Configurations BEYOND threshold (eps >= eps_0):")
        q1_loses = sum(1 for r in beyond_threshold if r['actual_margin'] <= 0)
        print(f"  Total beyond threshold: {len(beyond_threshold)}")
        print(f"  q=1 actually loses:     {q1_loses}")
        print(f"  q=1 still wins:         {len(beyond_threshold) - q1_loses}")
        print("  (q=1 winning beyond threshold means our threshold is conservative, which is expected)")

    return all_results


# ========================================================================
# Section 5: Specific test -- Gamma bounds the kernel perturbation
# ========================================================================

def test_gamma_bound():
    """Verify that ||A(S) - A_0(S)||_op <= eps * Gamma(kappa) for all S."""
    print()
    print("=" * 90)
    print("TEST: Gamma(kappa) BOUNDS SIGNED KERNEL PERTURBATION")
    print("=" * 90)
    print()

    configs = [
        ("Cycle C5", *cycle_graph(5)),
        ("Cycle C6", *cycle_graph(6)),
        ("Cycle C8", *cycle_graph(8)),
        ("Petersen", *petersen_graph()),
    ]

    J_values = [0.3, 0.5, 1.0]

    total_tests = 0
    passed = 0

    for name, n, edges in configs:
        for J in J_values:
            if 2**n > 2**14:
                continue

            m = len(edges)
            F = compute_exact_fisher(n, edges, J)

            D = np.diag(np.diag(F))
            off_diag = F - D
            eps = la.norm(off_diag, ord=2)
            if eps < 1e-15:
                continue

            f_min_val = np.min(np.diag(F))
            f_max_val = np.max(np.diag(F))
            kappa_val = f_max_val / f_min_val
            G = Gamma(kappa_val)

            F_sqrt = la.sqrtm(F).real
            D_sqrt = np.diag(np.sqrt(np.diag(F)))

            # Test for several sign assignments
            for q in range(1, min(m, 4)):
                for neg_indices in combinations(range(m), q):
                    total_tests += 1
                    signs = np.ones(m)
                    for idx in neg_indices:
                        signs[idx] = -1
                    S = np.diag(signs)

                    A_perturbed = F_sqrt @ S @ F_sqrt
                    A_unperturbed = D_sqrt @ S @ D_sqrt

                    diff_norm = la.norm(A_perturbed - A_unperturbed, ord=2)
                    bound = eps * G

                    if diff_norm <= bound + 1e-12:
                        passed += 1
                    else:
                        print(f"  FAIL: {name} J={J} q={q} neg={neg_indices}: "
                              f"||A-A_0||={diff_norm:.6f} > eps*Gamma={bound:.6f}")

    print(f"Gamma bound holds: {passed}/{total_tests} "
          f"({100*passed/total_tests:.1f}%)")


# ========================================================================
# Main
# ========================================================================

if __name__ == "__main__":
    results = run_all_tests()
    test_gamma_bound()

    print()
    print("=" * 90)
    print("VERIFICATION COMPLETE")
    print("=" * 90)
