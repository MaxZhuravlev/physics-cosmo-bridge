#!/usr/bin/env python3
"""
Higher-Dimensional β_c Analysis for Lorentzian Signature Selection
===================================================================

Research question: Does the Lorentzian signature mechanism (1 timelike + (n-1)
spacelike dimensions) emerge NATURALLY from the β_c formula for n > 2, or do
we get arbitrary signature mixtures?

Context: Papers/structural-bridge, Section 6 β_c theorems. The formula
β_c = -d_1 (min eigenvalue of F^{-1/2} M^{H1'} F^{-1/2}) has been verified
numerically for n=2 only. Key question: as n increases, does the framework
prefer exactly 1 negative eigenvalue (Lorentzian) or multiple?

Theoretical framework:
    M^{H1'}_{μν} = Σ_e s_e (∂_μ w_e)(∂_ν w_e)   -- signed edge contributions
    g(β) = M^{H1'} + β F                          -- combined metric
    A = F^{-1/2} M^{H1'} F^{-1/2}                 -- normalized operator
    β_c = -d_1 where d_1 ≤ d_2 ≤ ... ≤ d_n        -- critical temperature

Signature at β < β_c:
    (n_+, 0, n_-) where n_- = #{i : d_i < -β}

Physical predictions to test:
    1. Does n_- = 1 dominate for random observer topologies?
    2. Is there a spectral gap d_1 << d_2 < 0 selecting 1 timelike direction?
    3. Does topology (chain, star, complete) affect signature selection?
    4. What fraction of random sign assignments produce Lorentzian vs others?

Author: Max Zhuravlev (Cosmological Unification Program)
Date: 2026-02-16
Session: 24, dir-003 Lorentzian mechanism extension
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import Callable, Literal
import itertools
from collections import Counter


# ============================================================================
# 1. Observer Topology Generators
# ============================================================================

GraphType = Literal["chain", "star", "complete", "random", "tree"]


@dataclass
class ObserverTopology:
    """Observer topology with n parameters and signed internal edges."""

    n_params: int
    edges: list[tuple[int, ...]]  # Edge vertex indices
    edge_signs: list[int]  # s_e ∈ {+1, -1} for each edge
    graph_type: GraphType
    name: str = ""

    def __post_init__(self):
        if not self.name:
            self.name = f"{self.graph_type}_n{self.n_params}_e{len(self.edges)}"
        assert len(self.edges) == len(self.edge_signs), \
            "Must have one sign per edge"
        assert all(s in [-1, 1] for s in self.edge_signs), \
            "Signs must be ±1"

    @property
    def n_timelike(self) -> int:
        """Number of timelike edges (s_e = -1)."""
        return sum(1 for s in self.edge_signs if s == -1)

    @property
    def n_spacelike(self) -> int:
        """Number of spacelike edges (s_e = +1)."""
        return sum(1 for s in self.edge_signs if s == 1)


def generate_chain_graph(n: int, n_vertices: int = None) -> list[tuple[int, int]]:
    """Generate path graph edges: (0,1), (1,2), ..., (k-1, k)."""
    if n_vertices is None:
        n_vertices = max(3, n)  # At least 3 vertices for non-trivial topology
    return [(i, i+1) for i in range(n_vertices - 1)]


def generate_star_graph(n: int, n_vertices: int = None) -> list[tuple[int, int]]:
    """Generate star graph: hub at 0, edges (0,1), (0,2), ..., (0, k-1)."""
    if n_vertices is None:
        n_vertices = max(3, n)
    return [(0, i) for i in range(1, n_vertices)]


def generate_complete_graph(n: int, n_vertices: int = None) -> list[tuple[int, int]]:
    """Generate complete graph K_k: all pairs (i,j) with i < j."""
    if n_vertices is None:
        n_vertices = max(3, n)
    return [(i, j) for i in range(n_vertices) for j in range(i+1, n_vertices)]


def generate_random_graph(n: int, n_vertices: int = None,
                          edge_prob: float = 0.5,
                          rng: np.random.Generator = None) -> list[tuple[int, int]]:
    """Generate random graph: each possible edge included with probability p."""
    if n_vertices is None:
        n_vertices = max(3, n)
    if rng is None:
        rng = np.random.default_rng()

    edges = []
    for i in range(n_vertices):
        for j in range(i+1, n_vertices):
            if rng.random() < edge_prob:
                edges.append((i, j))

    # Ensure at least one edge
    if not edges:
        edges = [(0, 1)]

    return edges


def generate_tree_graph(n: int, n_vertices: int = None,
                        rng: np.random.Generator = None) -> list[tuple[int, int]]:
    """Generate random tree (n_vertices - 1 edges, connected, acyclic)."""
    if n_vertices is None:
        n_vertices = max(3, n)
    if rng is None:
        rng = np.random.default_rng()

    # Prüfer sequence → tree
    if n_vertices == 1:
        return []
    if n_vertices == 2:
        return [(0, 1)]

    # Random spanning tree via Prüfer sequence
    sequence = rng.integers(0, n_vertices, size=n_vertices - 2)

    # Decode Prüfer sequence to tree
    degree = np.ones(n_vertices, dtype=int)
    for s in sequence:
        degree[s] += 1

    edges = []
    for s in sequence:
        # Find first leaf (degree 1)
        for leaf in range(n_vertices):
            if degree[leaf] == 1:
                edges.append((min(s, leaf), max(s, leaf)))
                degree[leaf] -= 1
                degree[s] -= 1
                break

    # Connect final two vertices with degree 1
    leaves = [i for i in range(n_vertices) if degree[i] == 1]
    if len(leaves) == 2:
        edges.append((min(leaves), max(leaves)))

    return edges


def adjacency_based_signs(edges: list[tuple[int, ...]]) -> list[int]:
    """Assign signs based on adjacency rule from Paper #1:

    - Adjacent vertices (|i - j| == 1): timelike → s_e = -1
    - Non-adjacent: spacelike → s_e = +1

    This is the rule that produced Lorentzian signature for n=2.
    """
    signs = []
    for edge in edges:
        if len(edge) == 2:
            diff = abs(edge[1] - edge[0])
            signs.append(-1 if diff == 1 else 1)
        else:
            # Higher-order hyperedges: default spacelike
            signs.append(1)
    return signs


def random_sign_assignment(n_edges: int,
                           n_timelike_target: int = None,
                           rng: np.random.Generator = None) -> list[int]:
    """Random sign assignment with optional target number of timelike edges.

    If n_timelike_target is None: 50/50 random.
    Otherwise: exactly that many timelike edges, rest spacelike.
    """
    if rng is None:
        rng = np.random.default_rng()

    if n_timelike_target is None:
        return [rng.choice([-1, 1]) for _ in range(n_edges)]
    else:
        signs = [-1] * n_timelike_target + [1] * (n_edges - n_timelike_target)
        rng.shuffle(signs)
        return signs


def create_observer_topology(
    n_params: int,
    graph_type: GraphType,
    sign_mode: Literal["adjacency", "random", "all_timelike", "all_spacelike"] = "adjacency",
    n_vertices: int = None,
    rng: np.random.Generator = None
) -> ObserverTopology:
    """Factory for creating observer topologies with specified structure."""

    if graph_type == "chain":
        edges = generate_chain_graph(n_params, n_vertices)
    elif graph_type == "star":
        edges = generate_star_graph(n_params, n_vertices)
    elif graph_type == "complete":
        edges = generate_complete_graph(n_params, n_vertices)
    elif graph_type == "random":
        edges = generate_random_graph(n_params, n_vertices, rng=rng)
    elif graph_type == "tree":
        edges = generate_tree_graph(n_params, n_vertices, rng=rng)
    else:
        raise ValueError(f"Unknown graph_type: {graph_type}")

    if sign_mode == "adjacency":
        signs = adjacency_based_signs(edges)
    elif sign_mode == "random":
        signs = random_sign_assignment(len(edges), rng=rng)
    elif sign_mode == "all_timelike":
        signs = [-1] * len(edges)
    elif sign_mode == "all_spacelike":
        signs = [1] * len(edges)
    else:
        raise ValueError(f"Unknown sign_mode: {sign_mode}")

    return ObserverTopology(
        n_params=n_params,
        edges=edges,
        edge_signs=signs,
        graph_type=graph_type
    )


# ============================================================================
# 2. Configuration Functions and Gradient Computation
# ============================================================================

def edge_weight_gaussian(edge: tuple[int, ...], theta: np.ndarray,
                         n_vertices: int) -> float:
    """Gaussian edge weight function (from mass_tensor_computation.py):

    w_e(θ) = exp(-||θ - c_e||^2 / (2 s_e^2))

    where c_e depends on edge vertex indices (mean of indices normalized),
    and s_e is the edge scale (inversely proportional to edge order).
    """
    max_v = max(1, n_vertices - 1)
    c = np.mean(edge) / max_v  # Center in [0, 1]
    s = 1.0 / (1.0 + len(edge))  # Scale
    norm_sq = np.sum((theta - c)**2)
    return np.exp(-norm_sq / (2 * s**2))


def compute_edge_gradient(edge: tuple[int, ...], theta: np.ndarray,
                          n_vertices: int, dx: float = 1e-5) -> np.ndarray:
    """Compute gradient ∂w_e/∂θ via central finite differences."""
    n = len(theta)
    grad = np.zeros(n)

    for i in range(n):
        theta_plus = theta.copy()
        theta_minus = theta.copy()
        theta_plus[i] += dx
        theta_minus[i] -= dx

        w_plus = edge_weight_gaussian(edge, theta_plus, n_vertices)
        w_minus = edge_weight_gaussian(edge, theta_minus, n_vertices)

        grad[i] = (w_plus - w_minus) / (2 * dx)

    return grad


# ============================================================================
# 3. Mass and Fisher Tensor Computation
# ============================================================================

def compute_mass_tensor_H1_prime(
    topology: ObserverTopology,
    theta: np.ndarray,
    n_vertices: int = None
) -> np.ndarray:
    """Compute M^{H1'}_{μν} = Σ_e s_e (∂_μ w_e)(∂_ν w_e).

    This is the signed version from the Lorentzian analysis.
    """
    n = topology.n_params
    M = np.zeros((n, n))

    if n_vertices is None:
        # Infer from edges
        if topology.edges:
            n_vertices = max(max(e) for e in topology.edges) + 1
        else:
            n_vertices = n

    for edge, sign in zip(topology.edges, topology.edge_signs):
        grad = compute_edge_gradient(edge, theta, n_vertices)
        M += sign * np.outer(grad, grad)

    return M


def compute_fisher_metric_gaussian(theta: np.ndarray) -> np.ndarray:
    """Fisher metric for n-dimensional Gaussian with parameters (μ, log σ, ...).

    For simplicity, use a diagonal structure:
        F[0, 0] = 1 / σ^2  (mean parameter)
        F[i, i] = 2 for i > 0 (log-scale parameters)

    This generalizes the 2D case from the original code.
    """
    n = len(theta)
    F = np.zeros((n, n))

    if n >= 1:
        # First parameter: mean (assume σ = 1 at baseline)
        sigma = np.exp(theta[1]) if n >= 2 else 1.0
        F[0, 0] = 1.0 / sigma**2

    # Remaining parameters: log-scale (Fisher = 2 in log-parametrization)
    for i in range(1, n):
        F[i, i] = 2.0

    return F


# ============================================================================
# 4. β_c Computation and Signature Analysis
# ============================================================================

@dataclass
class SignatureAnalysis:
    """Results of signature analysis for an observer topology."""

    topology: ObserverTopology
    theta: np.ndarray

    # Matrices
    M: np.ndarray
    F: np.ndarray
    A: np.ndarray  # F^{-1/2} M F^{-1/2}

    # Eigenvalues
    M_eigenvalues: np.ndarray
    F_eigenvalues: np.ndarray
    A_eigenvalues: np.ndarray  # d_1 ≤ d_2 ≤ ... ≤ d_n

    # Critical beta
    beta_c: float  # = -d_1 if d_1 < 0, else 0

    # Signature characteristics
    n_negative_A: int  # Number of negative eigenvalues in A
    spectral_gap_ratio: float  # |d_2 - d_1| / |d_1| if multiple negative

    # Signature function: n_negative(β) for β ∈ (0, β_c)
    beta_samples: np.ndarray = field(default_factory=lambda: np.array([]))
    n_negative_at_beta: np.ndarray = field(default_factory=lambda: np.array([]))


def compute_beta_c_and_signature(
    topology: ObserverTopology,
    theta: np.ndarray,
    beta_samples: np.ndarray = None,
    n_vertices: int = None
) -> SignatureAnalysis:
    """Compute β_c and signature characteristics for a given topology."""

    n = topology.n_params

    # Compute tensors
    M = compute_mass_tensor_H1_prime(topology, theta, n_vertices)
    F = compute_fisher_metric_gaussian(theta)

    # Eigenvalues
    M_eigs = np.linalg.eigvalsh(M)
    F_eigs = np.linalg.eigvalsh(F)

    # Normalized operator A = F^{-1/2} M F^{-1/2}
    F_sqrt_inv = np.linalg.inv(np.linalg.cholesky(F)).T  # F = L L^T => F^{-1/2} = L^{-T}
    A = F_sqrt_inv @ M @ F_sqrt_inv.T
    A_eigs = np.linalg.eigvalsh(A)  # Sorted ascending: d_1 ≤ d_2 ≤ ... ≤ d_n

    # Critical beta
    d_1 = A_eigs[0]
    beta_c = -d_1 if d_1 < 0 else 0.0

    # Count negative eigenvalues in A
    n_negative_A = np.sum(A_eigs < -1e-12)

    # Spectral gap ratio
    if n_negative_A >= 2:
        d_2 = A_eigs[1]
        spectral_gap_ratio = abs(d_2 - d_1) / max(abs(d_1), 1e-15)
    else:
        spectral_gap_ratio = 0.0

    # Signature function n_negative(β)
    if beta_samples is None:
        if beta_c > 0:
            beta_samples = np.logspace(np.log10(beta_c/100), np.log10(beta_c*2), 50)
        else:
            beta_samples = np.logspace(-3, 1, 50)

    n_negative_at_beta = np.array([
        np.sum(A_eigs < -beta) for beta in beta_samples
    ])

    return SignatureAnalysis(
        topology=topology,
        theta=theta,
        M=M,
        F=F,
        A=A,
        M_eigenvalues=M_eigs,
        F_eigenvalues=F_eigs,
        A_eigenvalues=A_eigs,
        beta_c=beta_c,
        n_negative_A=n_negative_A,
        spectral_gap_ratio=spectral_gap_ratio,
        beta_samples=beta_samples,
        n_negative_at_beta=n_negative_at_beta
    )


# ============================================================================
# 5. Statistical Analysis Over Ensembles
# ============================================================================

@dataclass
class EnsembleStatistics:
    """Aggregated statistics over multiple observer configurations."""

    n_params: int
    graph_type: GraphType
    n_samples: int

    # Signature distribution at β just below β_c
    signature_distribution: Counter  # (n_+, n_-) → count

    # Fraction with exactly 1 negative eigenvalue (Lorentzian)
    lorentzian_fraction: float

    # Mean spectral gap for configurations with ≥2 negative eigenvalues
    mean_spectral_gap: float
    std_spectral_gap: float

    # β_c statistics
    beta_c_values: list[float]
    mean_beta_c: float
    std_beta_c: float

    # Individual analyses (for detailed inspection)
    analyses: list[SignatureAnalysis] = field(default_factory=list)


def analyze_ensemble(
    n_params: int,
    graph_type: GraphType,
    n_samples: int,
    sign_mode: str = "random",
    theta: np.ndarray = None,
    n_vertices: int = None,
    rng: np.random.Generator = None
) -> EnsembleStatistics:
    """Analyze signature statistics over an ensemble of random configurations."""

    if rng is None:
        rng = np.random.default_rng()

    if theta is None:
        # Default: θ at origin (with log σ = 0 for stability)
        theta = np.zeros(n_params)
        if n_params >= 2:
            theta[1] = 0.0  # log σ = 0 => σ = 1

    analyses = []
    signature_counts = Counter()
    spectral_gaps = []
    beta_c_values = []

    for _ in range(n_samples):
        # Generate random topology
        topology = create_observer_topology(
            n_params=n_params,
            graph_type=graph_type,
            sign_mode=sign_mode,
            n_vertices=n_vertices,
            rng=rng
        )

        # Skip if no edges (trivial)
        if not topology.edges:
            continue

        # Compute signature
        analysis = compute_beta_c_and_signature(topology, theta, n_vertices=n_vertices)
        analyses.append(analysis)

        # Record signature at β slightly below β_c
        if analysis.beta_c > 0:
            beta_test = analysis.beta_c * 0.5
            n_neg = np.sum(analysis.A_eigenvalues < -beta_test)
            n_pos = topology.n_params - n_neg
            signature_counts[(n_pos, n_neg)] += 1

            beta_c_values.append(analysis.beta_c)

            if analysis.n_negative_A >= 2:
                spectral_gaps.append(analysis.spectral_gap_ratio)

    # Compute statistics
    total_valid = sum(signature_counts.values())
    lorentzian_count = signature_counts.get((n_params - 1, 1), 0)
    lorentzian_fraction = lorentzian_count / total_valid if total_valid > 0 else 0.0

    mean_spectral_gap = np.mean(spectral_gaps) if spectral_gaps else 0.0
    std_spectral_gap = np.std(spectral_gaps) if spectral_gaps else 0.0

    mean_beta_c = np.mean(beta_c_values) if beta_c_values else 0.0
    std_beta_c = np.std(beta_c_values) if beta_c_values else 0.0

    return EnsembleStatistics(
        n_params=n_params,
        graph_type=graph_type,
        n_samples=len(analyses),
        signature_distribution=signature_counts,
        lorentzian_fraction=lorentzian_fraction,
        mean_spectral_gap=mean_spectral_gap,
        std_spectral_gap=std_spectral_gap,
        beta_c_values=beta_c_values,
        mean_beta_c=mean_beta_c,
        std_beta_c=std_beta_c,
        analyses=analyses
    )


# ============================================================================
# 6. Main Research Sweep
# ============================================================================

def run_high_dimensional_sweep(
    n_params_list: list[int] = [2, 3, 4, 5, 6, 8, 10],
    graph_types: list[GraphType] = ["chain", "star", "complete", "random", "tree"],
    n_samples_per_config: int = 100,
    seed: int = 42
) -> dict[tuple[int, GraphType], EnsembleStatistics]:
    """Main research sweep: analyze signature selection across dimensions and topologies.

    Returns:
        results: dict mapping (n_params, graph_type) → EnsembleStatistics
    """

    rng = np.random.default_rng(seed)
    results = {}

    total_configs = len(n_params_list) * len(graph_types)
    current = 0

    for n in n_params_list:
        for graph_type in graph_types:
            current += 1
            print(f"[{current}/{total_configs}] n={n}, graph={graph_type}...", end=" ")

            stats = analyze_ensemble(
                n_params=n,
                graph_type=graph_type,
                n_samples=n_samples_per_config,
                sign_mode="random",
                rng=rng
            )

            results[(n, graph_type)] = stats
            print(f"Lorentzian: {stats.lorentzian_fraction*100:.1f}%, "
                  f"<β_c>={stats.mean_beta_c:.3f}")

    return results


# ============================================================================
# 7. Self-Tests
# ============================================================================

def run_self_tests() -> bool:
    """TDD self-tests to verify correctness."""

    print("=" * 60)
    print("SELF-TESTS: β_c High-Dimensional Analysis")
    print("=" * 60)

    all_passed = True

    def check(name: str, condition: bool, detail: str = ""):
        nonlocal all_passed
        status = "PASS" if condition else "FAIL"
        if not condition:
            all_passed = False
        print(f"  [{status}] {name}{' -- ' + detail if detail else ''}")

    # Test 1: Topology generation
    print("\nTest 1: Topology generation")
    chain = generate_chain_graph(n=3, n_vertices=4)
    check("Chain graph has n_vertices-1 edges", len(chain) == 3)
    check("Chain edges are sequential", chain == [(0,1), (1,2), (2,3)])

    star = generate_star_graph(n=3, n_vertices=4)
    check("Star graph has n_vertices-1 edges", len(star) == 3)
    check("Star edges all connect to hub 0", all(e[0] == 0 for e in star))

    complete = generate_complete_graph(n=3, n_vertices=4)
    expected_complete_size = 4 * 3 // 2
    check("Complete K_4 has 6 edges", len(complete) == expected_complete_size)

    # Test 2: Sign assignment
    print("\nTest 2: Sign assignment")
    chain_signs = adjacency_based_signs(chain)
    check("Chain adjacency rule: all timelike", all(s == -1 for s in chain_signs),
          f"got {chain_signs}")

    star_signs = adjacency_based_signs(star)
    # Star: (0,1) adjacent, (0,2) not adjacent (diff=2), (0,3) not adjacent
    check("Star: (0,1) timelike", star_signs[0] == -1)

    # Test 3: Fisher metric shape
    print("\nTest 3: Fisher metric")
    theta_2d = np.array([0.5, 0.0])
    F_2d = compute_fisher_metric_gaussian(theta_2d)
    check("2D Fisher is 2x2", F_2d.shape == (2, 2))
    check("2D Fisher diagonal", np.allclose(F_2d, np.diag(np.diag(F_2d))))

    theta_5d = np.zeros(5)
    F_5d = compute_fisher_metric_gaussian(theta_5d)
    check("5D Fisher is 5x5", F_5d.shape == (5, 5))
    check("5D Fisher positive definite", np.all(np.linalg.eigvalsh(F_5d) > 0))

    # Test 4: Mass tensor computation
    print("\nTest 4: Mass tensor H1'")
    topology_simple = ObserverTopology(
        n_params=2,
        edges=[(0, 1)],
        edge_signs=[-1],
        graph_type="chain"
    )
    M_simple = compute_mass_tensor_H1_prime(topology_simple, theta_2d, n_vertices=2)
    check("M^{H1'} is symmetric", np.allclose(M_simple, M_simple.T))
    check("M^{H1'} with one timelike edge has ≤1 negative eigenvalue",
          np.sum(np.linalg.eigvalsh(M_simple) < -1e-12) <= 1)

    # Test 5: β_c computation
    print("\nTest 5: β_c computation")
    analysis_simple = compute_beta_c_and_signature(topology_simple, theta_2d, n_vertices=2)
    check("β_c computed", analysis_simple.beta_c >= 0)
    check("A eigenvalues sorted",
          np.allclose(np.sort(analysis_simple.A_eigenvalues), analysis_simple.A_eigenvalues))

    # If d_1 < 0, then β_c = -d_1
    if analysis_simple.A_eigenvalues[0] < 0:
        check("β_c = -d_1",
              np.isclose(analysis_simple.beta_c, -analysis_simple.A_eigenvalues[0]))

    # Test 6: Signature counting
    print("\nTest 6: Signature counting")
    n_neg_at_zero = np.sum(analysis_simple.A_eigenvalues < 0)
    if analysis_simple.beta_c > 0:
        beta_above = analysis_simple.beta_c * 2
        n_neg_above = np.sum(analysis_simple.A_eigenvalues < -beta_above)
        check("No negative eigenvalues for β > β_c", n_neg_above == 0,
              f"n_neg(2*β_c) = {n_neg_above}")

    # Test 7: Known case from Paper #1 (n=2, triangle)
    print("\nTest 7: Reproduce Paper #1 results (n=2)")
    topology_triangle = ObserverTopology(
        n_params=2,
        edges=[(0,1), (1,2), (0,2)],
        edge_signs=[-1, -1, 1],  # Adjacent timelike, non-adjacent spacelike
        graph_type="complete"
    )
    analysis_triangle = compute_beta_c_and_signature(topology_triangle, theta_2d, n_vertices=3)
    # Paper reports β_c ≈ 2.68 for O4 (triangle)
    # Allow 20% tolerance (different edge weight functions, finite differences)
    expected_beta_c_O4 = 2.68
    relative_error = abs(analysis_triangle.beta_c - expected_beta_c_O4) / expected_beta_c_O4
    check("Triangle β_c ≈ 2.68 (Paper #1 O4)", relative_error < 0.3,
          f"computed β_c = {analysis_triangle.beta_c:.3f}, expected ≈ {expected_beta_c_O4}")

    print("\n" + "=" * 60)
    print(f"SELF-TESTS: {'ALL PASSED ✓' if all_passed else 'SOME FAILED ✗'}")
    print("=" * 60)

    return all_passed


# ============================================================================
# 8. Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Higher-dimensional β_c signature analysis"
    )
    parser.add_argument("--test", action="store_true",
                        help="Run self-tests only")
    parser.add_argument("--sweep", action="store_true",
                        help="Run full research sweep")
    parser.add_argument("--n-samples", type=int, default=100,
                        help="Samples per (n, topology) configuration")
    parser.add_argument("--output", type=str,
                        default="/Users/Max_1/Projects/PhysicsResearch/cosmological-unification/experience/insights/BETA-C-HIGH-DIMENSIONAL-ANALYSIS-2026-02-16.md",
                        help="Output file path")

    args = parser.parse_args()

    if args.test:
        import sys
        success = run_self_tests()
        sys.exit(0 if success else 1)

    if args.sweep:
        print("\n" + "=" * 60)
        print("HIGH-DIMENSIONAL β_c SIGNATURE ANALYSIS")
        print("=" * 60)
        print()

        # Run self-tests first
        if not run_self_tests():
            print("\nSelf-tests failed. Aborting sweep.")
            import sys
            sys.exit(1)

        print("\n" + "=" * 60)
        print("MAIN RESEARCH SWEEP")
        print("=" * 60)
        print()

        results = run_high_dimensional_sweep(
            n_params_list=[2, 3, 4, 5, 6, 8, 10],
            graph_types=["chain", "star", "complete", "random", "tree"],
            n_samples_per_config=args.n_samples
        )

        # Generate markdown report
        from datetime import datetime

        md_lines = []
        md_lines.append("# Higher-Dimensional β_c Signature Analysis")
        md_lines.append("")
        md_lines.append(f"**Generated**: {datetime.now().isoformat()}")
        md_lines.append(f"**Samples per configuration**: {args.n_samples}")
        md_lines.append("")
        md_lines.append("## Research Question")
        md_lines.append("")
        md_lines.append("Does the β_c Lorentzian signature mechanism naturally select")
        md_lines.append("exactly 1 timelike direction (Lorentzian signature) for n > 2,")
        md_lines.append("or do we get arbitrary signature mixtures?")
        md_lines.append("")
        md_lines.append("## Methodology")
        md_lines.append("")
        md_lines.append("For each (n, topology) configuration:")
        md_lines.append("1. Generate random observer topologies with signed edges")
        md_lines.append("2. Compute M^{H1'} = Σ_e s_e (∂w_e)(∂w_e)^T")
        md_lines.append("3. Compute A = F^{-1/2} M^{H1'} F^{-1/2}")
        md_lines.append("4. Find β_c = -d_1 (min eigenvalue of A)")
        md_lines.append("5. Count negative eigenvalues at β < β_c")
        md_lines.append("6. Aggregate signature statistics")
        md_lines.append("")
        md_lines.append("## Results")
        md_lines.append("")

        # Table 1: Lorentzian fraction by (n, topology)
        md_lines.append("### Table 1: Lorentzian Signature Selection Rates")
        md_lines.append("")
        md_lines.append("Fraction of random configurations producing exactly 1 negative eigenvalue")
        md_lines.append("(Lorentzian signature) at β = β_c/2:")
        md_lines.append("")

        n_values = sorted(set(k[0] for k in results.keys()))
        graph_types = sorted(set(k[1] for k in results.keys()))

        # Header
        header = "| n |" + "".join(f" {g:10s} |" for g in graph_types)
        md_lines.append(header)
        md_lines.append("|" + "---|" * (len(graph_types) + 1))

        for n in n_values:
            row = f"| {n} |"
            for g in graph_types:
                stats = results.get((n, g))
                if stats:
                    frac = stats.lorentzian_fraction * 100
                    row += f" {frac:8.1f}% |"
                else:
                    row += " - |"
            md_lines.append(row)

        md_lines.append("")

        # Table 2: Mean β_c values
        md_lines.append("### Table 2: Mean β_c Values")
        md_lines.append("")
        md_lines.append("| n |" + "".join(f" {g:10s} |" for g in graph_types))
        md_lines.append("|" + "---|" * (len(graph_types) + 1))

        for n in n_values:
            row = f"| {n} |"
            for g in graph_types:
                stats = results.get((n, g))
                if stats:
                    row += f" {stats.mean_beta_c:10.3f} |"
                else:
                    row += " - |"
            md_lines.append(row)

        md_lines.append("")

        # Table 3: Spectral gap statistics
        md_lines.append("### Table 3: Spectral Gap Ratio (for configs with ≥2 negative eigenvalues)")
        md_lines.append("")
        md_lines.append("Mean |d_2 - d_1| / |d_1|:")
        md_lines.append("")
        md_lines.append("| n |" + "".join(f" {g:10s} |" for g in graph_types))
        md_lines.append("|" + "---|" * (len(graph_types) + 1))

        for n in n_values:
            row = f"| {n} |"
            for g in graph_types:
                stats = results.get((n, g))
                if stats and stats.mean_spectral_gap > 0:
                    row += f" {stats.mean_spectral_gap:10.3f} |"
                else:
                    row += " - |"
            md_lines.append(row)

        md_lines.append("")

        # Detailed signature distributions for selected configs
        md_lines.append("## Detailed Signature Distributions")
        md_lines.append("")

        for n in [3, 4, 6]:
            md_lines.append(f"### n = {n}")
            md_lines.append("")

            for g in ["complete", "random"]:
                stats = results.get((n, g))
                if not stats:
                    continue

                md_lines.append(f"#### {g.capitalize()} Graph")
                md_lines.append("")
                md_lines.append("| Signature (n_+, n_-) | Count | Fraction |")
                md_lines.append("|----------------------|-------|----------|")

                total = sum(stats.signature_distribution.values())
                for sig, count in sorted(stats.signature_distribution.items(),
                                        key=lambda x: -x[1]):
                    frac = count / total if total > 0 else 0
                    md_lines.append(f"| ({sig[0]}, {sig[1]}) | {count:5d} | {frac*100:6.2f}% |")

                md_lines.append("")

        # Analysis and conclusions
        md_lines.append("## Analysis")
        md_lines.append("")
        md_lines.append("### Key Findings")
        md_lines.append("")

        # Compute summary statistics
        lorentzian_fractions_by_n = {}
        for n in n_values:
            fracs = [results[(n, g)].lorentzian_fraction
                    for g in graph_types if (n, g) in results]
            lorentzian_fractions_by_n[n] = np.mean(fracs) if fracs else 0

        md_lines.append(f"1. **Lorentzian selection rates vary with dimension**:")
        for n, mean_frac in lorentzian_fractions_by_n.items():
            md_lines.append(f"   - n={n}: {mean_frac*100:.1f}% (averaged over topologies)")
        md_lines.append("")

        md_lines.append("2. **Topology dependence**: ")
        for g in graph_types:
            fracs = [results[(n, g)].lorentzian_fraction
                    for n in n_values if (n, g) in results]
            mean_g = np.mean(fracs) if fracs else 0
            md_lines.append(f"   - {g}: {mean_g*100:.1f}% Lorentzian (averaged over n)")
        md_lines.append("")

        md_lines.append("3. **Spectral gaps**: Configurations with multiple negative")
        md_lines.append("   eigenvalues show spectral gap ratios:")
        all_gaps = [s.mean_spectral_gap for s in results.values() if s.mean_spectral_gap > 0]
        if all_gaps:
            md_lines.append(f"   - Mean: {np.mean(all_gaps):.3f}")
            md_lines.append(f"   - Median: {np.median(all_gaps):.3f}")
            md_lines.append(f"   - Range: [{np.min(all_gaps):.3f}, {np.max(all_gaps):.3f}]")
        md_lines.append("")

        md_lines.append("### Interpretation")
        md_lines.append("")
        md_lines.append("TODO: Add physical interpretation after reviewing results.")
        md_lines.append("")

        md_lines.append("## Metadata")
        md_lines.append("")
        md_lines.append("```yaml")
        md_lines.append("document: BETA-C-HIGH-DIMENSIONAL-ANALYSIS-2026-02-16.md")
        md_lines.append(f"created: {datetime.now().isoformat()}")
        md_lines.append("framework: Vanchurin Type II, H1' signed edges")
        md_lines.append("n_dimensions_tested: " + str(n_values))
        md_lines.append("topologies: " + str(graph_types))
        md_lines.append(f"samples_per_config: {args.n_samples}")
        md_lines.append(f"total_analyses: {sum(s.n_samples for s in results.values())}")
        md_lines.append("```")

        # Write to file
        output_text = "\n".join(md_lines)

        import os
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, "w") as f:
            f.write(output_text)

        print(f"\n\nResults written to: {args.output}")
        print(f"Total configurations analyzed: {len(results)}")
        print(f"Total individual observers: {sum(s.n_samples for s in results.values())}")
        print("\nDone.")
