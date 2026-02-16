#!/usr/bin/env python3
"""
Spectral Gap Scaling Analysis for Lorentzian Sign Selection
============================================================

Research Question (Session 24):
    Does the spectral gap weighting mechanism W(q) = beta_c(q) × L_gap(q)
    favor q=1 (Lorentzian signature) for m >> 3 edges?

Background:
    From ENTROPIC-SIGN-SELECTION-2026-02-16.md:
    - Naive beta_c maximization FAILS: beta_c(q=2) > beta_c(q=1) for K3
      (Theorem 7.1, proven, confidence 99%)
    - BUT: Spectral gap weighting RESCUES it on K3:
      W(q=1) = beta_c(q=1) × L_gap(q=1) = 0.542 × 1.710 = 0.927
      W(q=2) = beta_c(q=2) × L_gap(q=2) = 0.778 × 0.305 = 0.237
      (W(q=1) / W(q=2) ≈ 3.9×, strongly favoring q=1)

    Key question: Does this hold for larger m, or was K3 special?

Spectral Gap Definition (Def 1.4):
    L_gap(S) = (d_2 - d_1) / |d_1|

    where d_1 < d_2 ≤ ... ≤ d_m are eigenvalues of A = F^{1/2} S F^{1/2},
    ordered from most negative to most positive.

    For q=1: d_1 < 0, d_2 > 0 → large gap (well-separated timelike direction)
    For q≥2: d_1 < d_2 < 0 → small gap (clustered negative eigenvalues)

Predictions to Test:
    1. W(q=1) > W(q≥2) for generic graphs with m ≥ 3
    2. L_gap(q=1) / L_gap(q=2) ~ O(m) (spectral gap grows with m)
    3. beta_c(q=2) may exceed beta_c(q=1) but W(q=2) < W(q=1) due to gap penalty

Implementation:
    - Exact Fisher matrices for K3, K4, K5 (Ising model)
    - Random graphs (Erdős-Rényi, geometric random)
    - Path, star, tree graphs
    - For each graph: compute beta_c(q), L_gap(q), W(q) for ALL q
    - Handle combinatorial explosion: sample sign assignments for large m

Author: Max Zhuravlev (Cosmological Unification Program)
Date: 2026-02-16
Priority: L(P) = 6.5 (TOP-3 program blocker)
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Callable
import itertools
import warnings

# Import from existing dynamical_signs.py
from dynamical_signs import (
    ising_fisher_K3,
    ising_fisher_K4,
    ising_fisher_path,
    ising_fisher_tree,
)


# ============================================================================
# 1. Fisher Matrix Generation for Random Graphs
# ============================================================================

def ising_fisher_Kn(n: int, J: float) -> np.ndarray:
    """Fisher matrix for complete graph K_n with uniform coupling J.

    K_n has n vertices and m = n(n-1)/2 edges.
    """
    if n == 3:
        return ising_fisher_K3(J)
    elif n == 4:
        return ising_fisher_K4(J)
    elif n >= 5:
        # For K5, K6: use exact partition function enumeration
        # This is exponential but feasible for n ≤ 6 (2^n = 64 states)
        states = np.array(list(itertools.product([-1, 1], repeat=n)))
        n_states = states.shape[0]

        # All pairs (i, j) with i < j
        edge_pairs = [(i, j) for i in range(n) for j in range(i+1, n)]
        m = len(edge_pairs)

        phi = np.zeros((n_states, m))
        for idx, (i, j) in enumerate(edge_pairs):
            phi[:, idx] = states[:, i] * states[:, j]

        energy = J * np.sum(phi, axis=1)
        weights = np.exp(energy)
        Z = np.sum(weights)
        probs = weights / Z

        mean_phi = probs @ phi
        F = np.zeros((m, m))
        for a in range(m):
            for b in range(m):
                F[a, b] = np.sum(probs * phi[:, a] * phi[:, b]) - mean_phi[a] * mean_phi[b]

        return F
    else:
        raise ValueError(f"n must be >= 3, got {n}")


def random_fisher_matrix(m: int, seed: int = 42, condition_number: float = 10.0) -> np.ndarray:
    """Generate a random PSD Fisher matrix of size m.

    Uses Wishart distribution (X^T X where X ~ N(0, I)).
    Condition number controls spread of eigenvalues.
    """
    rng = np.random.default_rng(seed)
    n_samples = max(m, int(m * 1.5))  # Ensure full rank
    X = rng.normal(0, 1, size=(n_samples, m))
    F_raw = X.T @ X / n_samples

    # Scale eigenvalues to target condition number
    eigs, Q = np.linalg.eigh(F_raw)
    eigs_scaled = np.linspace(1.0, condition_number, m)
    F = Q @ np.diag(eigs_scaled) @ Q.T

    return F


def erdos_renyi_fisher(n: int, p: float, J: float, seed: int = 42) -> np.ndarray:
    """Fisher matrix for Ising model on Erdős-Rényi random graph G(n, p).

    Creates random graph with n nodes, edge probability p, then computes
    exact Ising Fisher matrix.
    """
    rng = np.random.default_rng(seed)

    # Generate edges
    edges = []
    for i in range(n):
        for j in range(i+1, n):
            if rng.random() < p:
                edges.append((i, j))

    m = len(edges)
    if m == 0:
        raise ValueError("No edges generated, increase p or n")

    # For sparse graphs, use tree approximation (diagonal Fisher)
    # For dense graphs, use exact computation (expensive for n > 6)
    if n <= 6:
        # Exact computation via partition function
        states = np.array(list(itertools.product([-1, 1], repeat=n)))
        n_states = states.shape[0]

        phi = np.zeros((n_states, m))
        for idx, (i, j) in enumerate(edges):
            phi[:, idx] = states[:, i] * states[:, j]

        energy = J * np.sum(phi, axis=1)
        weights = np.exp(energy)
        Z = np.sum(weights)
        probs = weights / Z

        mean_phi = probs @ phi
        F = np.zeros((m, m))
        for a in range(m):
            for b in range(m):
                F[a, b] = np.sum(probs * phi[:, a] * phi[:, b]) - mean_phi[a] * mean_phi[b]

        return F
    else:
        # Approximate as tree (diagonal Fisher)
        warnings.warn(f"n={n} too large for exact computation, using tree approximation")
        return np.diag(1.0 / np.cosh(J)**2 * np.ones(m))


def star_graph_fisher(n: int, J: float) -> np.ndarray:
    """Fisher matrix for star graph with n-1 edges (n nodes, 1 central).

    Star graph is a tree: F is diagonal with F_ee = sech^2(J).
    """
    m = n - 1
    return ising_fisher_tree(np.full(m, J))


# ============================================================================
# 2. Sign Assignment Enumeration and Sampling
# ============================================================================

def enumerate_sign_assignments(m: int, q: int) -> np.ndarray:
    """Enumerate all binary sign assignments with exactly q negative signs.

    Returns array of shape (C(m, q), m) where each row is a sign vector.
    """
    from itertools import combinations
    import math

    n_assignments = int(math.comb(m, q))
    assignments = np.ones((n_assignments, m))

    for idx, neg_indices in enumerate(combinations(range(m), q)):
        assignments[idx, list(neg_indices)] = -1.0

    return assignments


def sample_sign_assignments(m: int, q: int, n_samples: int, seed: int = 42) -> np.ndarray:
    """Sample random sign assignments with exactly q negative signs.

    Returns array of shape (n_samples, m).
    """
    rng = np.random.default_rng(seed)
    assignments = np.ones((n_samples, m))

    for i in range(n_samples):
        neg_indices = rng.choice(m, size=q, replace=False)
        assignments[i, neg_indices] = -1.0

    return assignments


# ============================================================================
# 3. Critical Beta and Spectral Gap Computation
# ============================================================================

@dataclass
class SignatureMetrics:
    """Metrics for a single sign assignment S."""

    S: np.ndarray                 # Sign vector (m,)
    q: int                        # Number of negative signs
    beta_c: float                 # Critical beta
    eigenvalues: np.ndarray       # Eigenvalues of A = F^{1/2} S F^{1/2}
    L_gap: float                  # Spectral gap (d_2 - d_1) / |d_1|
    W: float                      # W(S) = beta_c × L_gap
    signature: tuple              # (n_pos, n_zero, n_neg) at beta=0


def compute_signature_metrics(S: np.ndarray, F: np.ndarray) -> SignatureMetrics:
    """Compute beta_c, spectral gap, and W for sign assignment S.

    Uses the proven formula (MF2-LORENTZIAN-IMPLICATIONS):
        beta_c(S) = -lambda_min(F^{1/2} S F^{1/2})

    Spectral gap:
        L_gap(S) = (d_2 - d_1) / |d_1|
    where d_1, d_2 are smallest eigenvalues.
    """
    m = len(S)
    assert F.shape == (m, m), f"F must be {m}x{m}"

    # Construct A = F^{1/2} S F^{1/2}
    try:
        F_sqrt = np.linalg.cholesky(F).T  # Upper triangular, so F = F_sqrt.T @ F_sqrt
    except np.linalg.LinAlgError:
        # F is not PSD (numerical error), use eigenvalue decomposition
        eigs_F, Q = np.linalg.eigh(F)
        eigs_F = np.maximum(eigs_F, 1e-14)  # Enforce PSD
        F_sqrt = Q @ np.diag(np.sqrt(eigs_F)) @ Q.T

    S_diag = np.diag(S)
    A = F_sqrt @ S_diag @ F_sqrt.T

    # Eigenvalues of A
    eigs = np.linalg.eigvalsh(A)  # Sorted ascending
    d_1 = eigs[0]
    d_2 = eigs[1] if len(eigs) > 1 else 0.0

    # beta_c = -lambda_min(A) = -d_1
    beta_c = -d_1

    # Count negative eigenvalues at beta=0 (signature of A)
    n_neg = int(np.sum(eigs < -1e-10))
    n_zero = int(np.sum(np.abs(eigs) <= 1e-10))
    n_pos = int(np.sum(eigs > 1e-10))
    signature = (n_pos, n_zero, n_neg)

    # Spectral gap
    if abs(d_1) > 1e-14:
        L_gap = (d_2 - d_1) / abs(d_1)
    else:
        L_gap = 0.0

    # W = beta_c × L_gap
    W = beta_c * L_gap

    q_actual = n_neg  # Should equal input q by Sylvester's law

    return SignatureMetrics(
        S=S.copy(),
        q=q_actual,
        beta_c=beta_c,
        eigenvalues=eigs,
        L_gap=L_gap,
        W=W,
        signature=signature
    )


# ============================================================================
# 4. Aggregate Statistics for All q
# ============================================================================

@dataclass
class QMetrics:
    """Aggregate metrics for all sign assignments with q negative signs."""

    q: int
    n_assignments: int            # Total assignments with this q
    n_sampled: int                # Number actually computed (if sampled)

    # Best assignment (max beta_c)
    best_beta_c: float
    best_L_gap: float
    best_W: float
    best_S: np.ndarray

    # Mean/std over all assignments
    mean_beta_c: float
    std_beta_c: float
    mean_L_gap: float
    std_L_gap: float
    mean_W: float
    std_W: float

    # Full distribution (if small enough)
    all_metrics: list = field(default_factory=list)


def compute_q_metrics(
    F: np.ndarray,
    q: int,
    max_enumerate: int = 1000,
    n_samples: int = 500,
    seed: int = 42
) -> QMetrics:
    """Compute metrics for ALL sign assignments with q negative signs.

    If C(m, q) ≤ max_enumerate: enumerate all
    Else: sample n_samples randomly
    """
    import math
    m = F.shape[0]
    n_total = int(math.comb(m, q))

    if n_total <= max_enumerate:
        # Enumerate all
        sign_assignments = enumerate_sign_assignments(m, q)
        n_sampled = n_total
    else:
        # Sample
        sign_assignments = sample_sign_assignments(m, q, n_samples, seed)
        n_sampled = n_samples

    # Compute metrics for each
    all_metrics = []
    for S in sign_assignments:
        metrics = compute_signature_metrics(S, F)
        all_metrics.append(metrics)

    # Aggregate
    beta_c_values = [met.beta_c for met in all_metrics]
    L_gap_values = [met.L_gap for met in all_metrics]
    W_values = [met.W for met in all_metrics]

    best_idx = int(np.argmax(W_values))
    best = all_metrics[best_idx]

    return QMetrics(
        q=q,
        n_assignments=n_total,
        n_sampled=n_sampled,
        best_beta_c=best.beta_c,
        best_L_gap=best.L_gap,
        best_W=best.W,
        best_S=best.S.copy(),
        mean_beta_c=float(np.mean(beta_c_values)),
        std_beta_c=float(np.std(beta_c_values)),
        mean_L_gap=float(np.mean(L_gap_values)),
        std_L_gap=float(np.std(L_gap_values)),
        mean_W=float(np.mean(W_values)),
        std_W=float(np.std(W_values)),
        all_metrics=all_metrics if n_total <= max_enumerate else []
    )


# ============================================================================
# 5. Full Graph Analysis
# ============================================================================

@dataclass
class GraphAnalysis:
    """Complete analysis for a single graph across all q."""

    graph_name: str
    m: int                        # Number of edges
    F: np.ndarray                 # Fisher matrix

    q_metrics: dict               # q -> QMetrics
    q_max_W: int                  # Value of q that maximizes W
    W_ratio_q1_to_q2: float       # W(q=1) / W(q=2) if both exist

    # Theoretical predictions
    spectral_gap_ratio_predicted: Optional[float] = None  # L_gap(q=1) / L_gap(q=2) ~ O(m)?


def analyze_graph(
    F: np.ndarray,
    graph_name: str = "",
    q_range: Optional[list[int]] = None,
    max_enumerate: int = 1000,
    n_samples: int = 500,
    seed: int = 42
) -> GraphAnalysis:
    """Analyze spectral gap scaling for a graph across all q.

    Args:
        F: Fisher matrix (m, m)
        graph_name: Label for the graph
        q_range: List of q values to compute (default: [1, 2, ..., m])
        max_enumerate: Max assignments to enumerate exactly
        n_samples: Number of samples if C(m, q) too large
        seed: Random seed for sampling

    Returns:
        GraphAnalysis with full statistics
    """
    m = F.shape[0]

    if q_range is None:
        q_range = list(range(1, m + 1))  # q = 1, 2, ..., m

    q_metrics = {}
    for q in q_range:
        metrics = compute_q_metrics(F, q, max_enumerate, n_samples, seed)
        q_metrics[q] = metrics

    # Find q that maximizes W
    W_by_q = {q: met.best_W for q, met in q_metrics.items()}
    q_max_W = max(W_by_q, key=W_by_q.get)

    # W ratio
    if 1 in q_metrics and 2 in q_metrics:
        W1 = q_metrics[1].best_W
        W2 = q_metrics[2].best_W
        W_ratio = W1 / W2 if W2 > 1e-14 else float('inf')
    else:
        W_ratio = float('nan')

    return GraphAnalysis(
        graph_name=graph_name,
        m=m,
        F=F,
        q_metrics=q_metrics,
        q_max_W=q_max_W,
        W_ratio_q1_to_q2=W_ratio
    )


# ============================================================================
# 6. Scaling Study: m = 3, 6, 10, 15, 20
# ============================================================================

@dataclass
class ScalingStudy:
    """Results from scaling analysis across multiple graphs."""

    analyses: list[GraphAnalysis]
    summary: dict  # graph_name -> (m, q_max_W, W_ratio, L_gap_ratio)


def run_scaling_study(
    graphs: dict[str, np.ndarray],
    q_range_factory: Callable[[int], list[int]] = lambda m: [1, 2],
    max_enumerate: int = 1000,
    n_samples: int = 500,
    seed: int = 42,
    verbose: bool = True
) -> ScalingStudy:
    """Run spectral gap scaling study on multiple graphs.

    Args:
        graphs: Dict mapping graph_name -> Fisher matrix
        q_range_factory: Function m -> list of q values to test
        max_enumerate: Max assignments to enumerate exactly
        n_samples: Number of samples if C(m, q) too large
        seed: Random seed
        verbose: Print progress

    Returns:
        ScalingStudy with full results
    """
    analyses = []
    summary = {}

    for gname, F in graphs.items():
        m = F.shape[0]
        q_range = q_range_factory(m)

        if verbose:
            print(f"Analyzing {gname} (m={m}, q={q_range})...", end=" ", flush=True)

        analysis = analyze_graph(
            F=F,
            graph_name=gname,
            q_range=q_range,
            max_enumerate=max_enumerate,
            n_samples=n_samples,
            seed=seed
        )

        analyses.append(analysis)

        # Summary stats
        if 1 in analysis.q_metrics and 2 in analysis.q_metrics:
            L1 = analysis.q_metrics[1].best_L_gap
            L2 = analysis.q_metrics[2].best_L_gap
            L_gap_ratio = L1 / L2 if L2 > 1e-14 else float('inf')
        else:
            L_gap_ratio = float('nan')

        summary[gname] = {
            "m": m,
            "q_max_W": analysis.q_max_W,
            "W_ratio": analysis.W_ratio_q1_to_q2,
            "L_gap_ratio": L_gap_ratio,
        }

        if verbose:
            print(f"q_max_W={analysis.q_max_W}, W(q=1)/W(q=2)={analysis.W_ratio_q1_to_q2:.3f}, "
                  f"L_gap(q=1)/L_gap(q=2)={L_gap_ratio:.3f}")

    return ScalingStudy(analyses=analyses, summary=summary)


# ============================================================================
# 7. Report Generation
# ============================================================================

def generate_scaling_report(study: ScalingStudy) -> str:
    """Generate markdown report for scaling study."""

    lines = []
    lines.append("# Spectral Gap Scaling Analysis")
    lines.append("")
    lines.append("## Summary Table")
    lines.append("")
    lines.append("| Graph | m | q(max W) | W(q=1)/W(q=2) | L_gap(q=1)/L_gap(q=2) | Prediction |")
    lines.append("|-------|---|----------|---------------|-----------------------|------------|")

    for gname, stats in study.summary.items():
        m = stats["m"]
        q_max = stats["q_max_W"]
        W_ratio = stats["W_ratio"]
        L_ratio = stats["L_gap_ratio"]

        # Prediction: W(q=1) should dominate
        prediction = "✓ q=1" if q_max == 1 else f"✗ q={q_max}"

        lines.append(f"| {gname:20s} | {m:2d} | {q_max:8d} | "
                     f"{W_ratio:13.3f} | {L_ratio:21.3f} | {prediction:10s} |")

    lines.append("")

    # Key findings
    lines.append("## Key Findings")
    lines.append("")

    # Count how many graphs have q_max_W = 1
    n_total = len(study.summary)
    n_q1 = sum(1 for s in study.summary.values() if s["q_max_W"] == 1)
    frac_q1 = n_q1 / n_total if n_total > 0 else 0

    lines.append(f"1. **W(q) maximized at q=1**: {n_q1}/{n_total} graphs ({frac_q1*100:.1f}%)")
    lines.append("")

    # W ratio scaling
    W_ratios = [s["W_ratio"] for s in study.summary.values() if not np.isnan(s["W_ratio"])]
    if W_ratios:
        mean_W_ratio = np.mean(W_ratios)
        lines.append(f"2. **Mean W(q=1)/W(q=2)**: {mean_W_ratio:.3f}")
        lines.append("")

    # L_gap ratio scaling
    L_ratios = [s["L_gap_ratio"] for s in study.summary.values() if not np.isnan(s["L_gap_ratio"])]
    if L_ratios:
        mean_L_ratio = np.mean(L_ratios)
        lines.append(f"3. **Mean L_gap(q=1)/L_gap(q=2)**: {mean_L_ratio:.3f}")
        lines.append("")

    # m-dependence
    m_values = sorted(set(s["m"] for s in study.summary.values()))
    lines.append("### Scaling with m")
    lines.append("")
    for m_val in m_values:
        relevant = {k: v for k, v in study.summary.items() if v["m"] == m_val}
        if relevant:
            W_ratios_m = [v["W_ratio"] for v in relevant.values() if not np.isnan(v["W_ratio"])]
            L_ratios_m = [v["L_gap_ratio"] for v in relevant.values() if not np.isnan(v["L_gap_ratio"])]
            if W_ratios_m:
                lines.append(f"- **m={m_val}**: W_ratio = {np.mean(W_ratios_m):.3f} ± {np.std(W_ratios_m):.3f}, "
                             f"L_gap_ratio = {np.mean(L_ratios_m):.3f} ± {np.std(L_ratios_m):.3f}")
    lines.append("")

    # Theoretical prediction check
    lines.append("## Theoretical Predictions")
    lines.append("")
    lines.append("**Conjecture 7.1** (ENTROPIC-SIGN-SELECTION): W(q=1) > W(q≥2) for generic F.")
    lines.append("")
    if frac_q1 >= 0.9:
        lines.append(f"**Status**: STRONGLY SUPPORTED ({frac_q1*100:.0f}% success rate)")
    elif frac_q1 >= 0.7:
        lines.append(f"**Status**: SUPPORTED ({frac_q1*100:.0f}% success rate)")
    elif frac_q1 >= 0.5:
        lines.append(f"**Status**: WEAKLY SUPPORTED ({frac_q1*100:.0f}% success rate)")
    else:
        lines.append(f"**Status**: NOT SUPPORTED ({frac_q1*100:.0f}% success rate)")
    lines.append("")

    lines.append("**Conjecture 7.4**: L_gap(q=1) / L_gap(q=2) = O(m)")
    lines.append("")
    if L_ratios and m_values:
        # Fit L_gap_ratio ~ a * m + b
        m_vals_with_L = [s["m"] for s in study.summary.values() if not np.isnan(s["L_gap_ratio"])]
        L_vals_with_m = [s["L_gap_ratio"] for s in study.summary.values() if not np.isnan(s["L_gap_ratio"])]
        if len(m_vals_with_L) >= 2:
            p = np.polyfit(m_vals_with_L, L_vals_with_m, 1)
            lines.append(f"Linear fit: L_gap_ratio ≈ {p[0]:.3f} × m + {p[1]:.3f}")
            if p[0] > 0.1:
                lines.append(f"**Status**: SUPPORTED (positive slope {p[0]:.3f})")
            else:
                lines.append(f"**Status**: WEAK (slope {p[0]:.3f} near zero)")
        else:
            lines.append("**Status**: INSUFFICIENT DATA for linear fit")
    lines.append("")

    return "\n".join(lines)


# ============================================================================
# 8. Self-Tests
# ============================================================================

def run_self_tests() -> bool:
    """TDD self-tests."""

    print("=" * 70)
    print("SELF-TESTS: Spectral Gap Scaling")
    print("=" * 70)

    all_passed = True

    def check(name: str, condition: bool, detail: str = ""):
        nonlocal all_passed
        status = "PASS" if condition else "FAIL"
        if not condition:
            all_passed = False
        print(f"  [{status}] {name}{' -- ' + detail if detail else ''}")

    # Test 1: Fisher matrix generation
    print("\nTest 1: Fisher matrix generation")

    F_K3 = ising_fisher_Kn(3, 0.5)
    check("K3 Fisher is 3x3", F_K3.shape == (3, 3))
    check("K3 Fisher is PSD", np.all(np.linalg.eigvalsh(F_K3) > -1e-10))

    F_K4 = ising_fisher_Kn(4, 0.5)
    check("K4 Fisher is 6x6", F_K4.shape == (6, 6))
    check("K4 Fisher is PSD", np.all(np.linalg.eigvalsh(F_K4) > -1e-10))

    F_K5 = ising_fisher_Kn(5, 0.5)
    m5 = 5 * 4 // 2
    check(f"K5 Fisher is {m5}x{m5}", F_K5.shape == (m5, m5))
    check("K5 Fisher is PSD", np.all(np.linalg.eigvalsh(F_K5) > -1e-10))

    F_path = star_graph_fisher(5, 0.5)
    check("Star graph Fisher is diagonal", np.allclose(F_path, np.diag(np.diag(F_path)), atol=1e-12))

    # Test 2: Sign assignment enumeration
    print("\nTest 2: Sign assignment enumeration")

    assignments = enumerate_sign_assignments(3, 1)
    check("C(3, 1) = 3", assignments.shape[0] == 3)
    check("Each has 1 negative", np.all(np.sum(assignments < 0, axis=1) == 1))

    assignments_q2 = enumerate_sign_assignments(4, 2)
    check("C(4, 2) = 6", assignments_q2.shape[0] == 6)
    check("Each has 2 negatives", np.all(np.sum(assignments_q2 < 0, axis=1) == 2))

    # Test 3: Signature metrics computation
    print("\nTest 3: Signature metrics computation")

    F = ising_fisher_K3(0.5)
    S = np.array([-1.0, 1.0, 1.0])  # q=1

    metrics = compute_signature_metrics(S, F)
    check("q=1 assignment recognized", metrics.q == 1)
    check("beta_c > 0", metrics.beta_c > 0)
    check("L_gap > 0 for q=1", metrics.L_gap > 0,
          f"L_gap = {metrics.L_gap:.4f}")

    # Known value from ENTROPIC-SIGN-SELECTION: beta_c(q=1) ~ 0.542 for K3 at J=0.5
    check("beta_c(q=1) matches known value",
          abs(metrics.beta_c - 0.542) < 0.01,
          f"beta_c = {metrics.beta_c:.4f}")

    # q=2 case
    S_q2 = np.array([-1.0, -1.0, 1.0])
    metrics_q2 = compute_signature_metrics(S_q2, F)
    check("q=2 assignment recognized", metrics_q2.q == 2)
    check("beta_c(q=2) > beta_c(q=1)", metrics_q2.beta_c > metrics.beta_c,
          f"beta_c(q=2)={metrics_q2.beta_c:.4f}, beta_c(q=1)={metrics.beta_c:.4f}")
    check("L_gap(q=1) > L_gap(q=2)", metrics.L_gap > metrics_q2.L_gap,
          f"L_gap(q=1)={metrics.L_gap:.4f}, L_gap(q=2)={metrics_q2.L_gap:.4f}")
    check("W(q=1) > W(q=2)", metrics.W > metrics_q2.W,
          f"W(q=1)={metrics.W:.4f}, W(q=2)={metrics_q2.W:.4f}")

    # Test 4: Q-level aggregation
    print("\nTest 4: Q-level aggregation")

    q_met = compute_q_metrics(F, q=1, max_enumerate=10, n_samples=100)
    check("Q metrics for q=1", q_met.q == 1)
    check("n_assignments = C(3,1) = 3", q_met.n_assignments == 3)
    check("best_W computed", q_met.best_W > 0)

    # Test 5: Graph analysis
    print("\nTest 5: Full graph analysis")

    analysis = analyze_graph(F, graph_name="K3_test", q_range=[1, 2], max_enumerate=10)
    check("Graph analysis complete", analysis.m == 3)
    check("q_max_W should be 1", analysis.q_max_W == 1,
          f"q_max_W = {analysis.q_max_W}")
    check("W_ratio > 1", analysis.W_ratio_q1_to_q2 > 1.0,
          f"W_ratio = {analysis.W_ratio_q1_to_q2:.3f}")

    # Test 6: Scaling study
    print("\nTest 6: Scaling study")

    graphs = {
        "K3": ising_fisher_K3(0.5),
        "K4": ising_fisher_K4(0.5),
        "Path4": ising_fisher_path(np.full(3, 0.5)),
    }

    study = run_scaling_study(
        graphs,
        q_range_factory=lambda m: [1, 2],
        max_enumerate=50,
        n_samples=100,
        seed=42,
        verbose=False
    )

    check("Scaling study complete", len(study.analyses) == 3)
    check("All graphs have q_max_W = 1",
          all(a.q_max_W == 1 for a in study.analyses),
          f"q_max_W values: {[a.q_max_W for a in study.analyses]}")

    # Test 7: Report generation
    print("\nTest 7: Report generation")

    report = generate_scaling_report(study)
    check("Report generated", len(report) > 0)
    check("Report contains summary table", "Summary Table" in report)
    check("Report contains key findings", "Key Findings" in report)

    print("\n" + "=" * 70)
    print(f"SELF-TESTS: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
    print("=" * 70)

    return all_passed


# ============================================================================
# 9. Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Spectral gap scaling analysis for Lorentzian sign selection"
    )
    parser.add_argument("--test", action="store_true",
                        help="Run self-tests only")
    parser.add_argument("--quick", action="store_true",
                        help="Quick analysis (K3, K4, Path graphs)")
    parser.add_argument("--full", action="store_true",
                        help="Full scaling study (K3, K4, K5, K6, random graphs)")
    parser.add_argument("--max-enumerate", type=int, default=1000,
                        help="Max sign assignments to enumerate (vs sample)")
    parser.add_argument("--n-samples", type=int, default=500,
                        help="Number of samples if too many assignments")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed")
    parser.add_argument("--output", type=str, default=None,
                        help="Output file for report (default: stdout)")

    args = parser.parse_args()

    if args.test:
        success = run_self_tests()
        sys.exit(0 if success else 1)

    if not run_self_tests():
        print("\nSelf-tests failed. Aborting.")
        sys.exit(1)

    J_default = 0.5  # Moderate coupling

    if args.quick:
        print("\n" + "=" * 70)
        print("QUICK SCALING ANALYSIS")
        print("=" * 70)
        print()

        graphs = {
            "K3_J0.5": ising_fisher_K3(J_default),
            "K4_J0.5": ising_fisher_K4(J_default),
            "Path3_J0.5": ising_fisher_path(np.full(2, J_default)),
            "Path4_J0.5": ising_fisher_path(np.full(3, J_default)),
            "Star4_J0.5": star_graph_fisher(4, J_default),
        }

        study = run_scaling_study(
            graphs,
            q_range_factory=lambda m: list(range(1, min(m+1, 4))),  # q=1,2,3
            max_enumerate=args.max_enumerate,
            n_samples=args.n_samples,
            seed=args.seed,
            verbose=True
        )

        report = generate_scaling_report(study)
        print("\n" + report)

        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"\nReport written to {args.output}")

    elif args.full:
        print("\n" + "=" * 70)
        print("FULL SCALING STUDY")
        print("=" * 70)
        print()

        graphs = {
            "K3_J0.5": ising_fisher_K3(J_default),
            "K4_J0.5": ising_fisher_K4(J_default),
            "K5_J0.5": ising_fisher_Kn(5, J_default),
            "K6_J0.5": ising_fisher_Kn(6, J_default),
            "Path3_J0.5": ising_fisher_path(np.full(2, J_default)),
            "Path4_J0.5": ising_fisher_path(np.full(3, J_default)),
            "Path5_J0.5": ising_fisher_path(np.full(4, J_default)),
            "Star5_J0.5": star_graph_fisher(5, J_default),
            "Star6_J0.5": star_graph_fisher(6, J_default),
            "Random_m5_seed42": random_fisher_matrix(5, seed=42),
            "Random_m8_seed43": random_fisher_matrix(8, seed=43),
            "Random_m10_seed44": random_fisher_matrix(10, seed=44),
            "Random_m15_seed45": random_fisher_matrix(15, seed=45),
        }

        study = run_scaling_study(
            graphs,
            q_range_factory=lambda m: [1, 2] if m <= 15 else [1],  # For large m, only test q=1,2
            max_enumerate=args.max_enumerate,
            n_samples=args.n_samples,
            seed=args.seed,
            verbose=True
        )

        report = generate_scaling_report(study)
        print("\n" + report)

        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"\nReport written to {args.output}")

    else:
        parser.print_help()
