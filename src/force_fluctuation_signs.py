#!/usr/bin/env python3
"""
Force-Fluctuation Edge Sign Assignment
=======================================

TEST IMPLEMENTATION of Approach 2 from EDGE-SIGN-ORIGIN-RESEARCH-2026-02-16.md

Research Question: Can edge signs s_e be derived from the force-fluctuation
decomposition (Vanchurin Type II, NR Eq. 4.3) rather than imposed via
adjacency rule?

Approach 2 (Force-Fluctuation):
    sigma_FF(e) = -1  if ∇w_e is aligned with F = -∇L (force direction)
    sigma_FF(e) = +1  if ∇w_e is perpendicular to F

Theoretical basis: The metric decomposition
    g = -(m γ² / 2Q) F ⊗ F + κ
has exactly ONE negative eigenvalue (rank-1 force term). This maps onto
M^{H1'} with exactly ONE timelike direction.

Test predictions:
1. Force-fluctuation signs should produce Lorentzian signature
2. Should give exactly 1 negative eigenvalue in M^{H1'}
3. May differ from adjacency rule but should work physically
4. Should be label-independent

Author: Max Zhuravlev (Cosmological Unification Program)
Date: 2026-02-16
Session: 24, dir-005 Force-fluctuation numerical test
Status: PURE RESEARCH (honest reporting, positive or negative)
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Callable, Literal, Optional
from pathlib import Path

# Import infrastructure from existing codebase
from beta_c_high_dim import (
    ObserverTopology,
    create_observer_topology,
    compute_edge_gradient,
    compute_mass_tensor_H1_prime,
    compute_fisher_metric_gaussian,
    compute_beta_c_and_signature,
    edge_weight_gaussian,
    GraphType,
)


# ============================================================================
# 1. Loss Functions
# ============================================================================

def loss_quadratic(weights: np.ndarray) -> float:
    """Simple quadratic loss: L(w) = (1/2) Σ_i w_i²

    Gradient: ∇L = w
    This is the simplest possible loss for testing.
    """
    return 0.5 * np.sum(weights**2)


def loss_gradient_quadratic(weights: np.ndarray) -> np.ndarray:
    """Gradient of quadratic loss: ∇L = w"""
    return weights


def loss_feedforward_mse(
    theta: np.ndarray,
    topology: ObserverTopology,
    target_output: float = 1.0,
    n_vertices: int = None
) -> float:
    """MSE loss for simple feedforward network.

    Network: weights {w_e} -> output = Σ_e w_e(θ)
    Loss: L = (1/2)(output - target)²
    """
    if n_vertices is None:
        if topology.edges:
            n_vertices = max(max(e) for e in topology.edges) + 1
        else:
            n_vertices = topology.n_params

    # Compute network output
    output = sum(
        edge_weight_gaussian(edge, theta, n_vertices)
        for edge in topology.edges
    )

    # MSE loss
    error = output - target_output
    return 0.5 * error**2


def loss_gradient_feedforward_mse(
    theta: np.ndarray,
    topology: ObserverTopology,
    target_output: float = 1.0,
    n_vertices: int = None
) -> np.ndarray:
    """Gradient of feedforward MSE loss.

    ∇L = (output - target) * Σ_e ∇w_e(θ)
    """
    if n_vertices is None:
        if topology.edges:
            n_vertices = max(max(e) for e in topology.edges) + 1
        else:
            n_vertices = topology.n_params

    # Compute network output
    output = sum(
        edge_weight_gaussian(edge, theta, n_vertices)
        for edge in topology.edges
    )

    # Error signal
    error = output - target_output

    # Gradient: chain rule
    grad = np.zeros(topology.n_params)
    for edge in topology.edges:
        grad += compute_edge_gradient(edge, theta, n_vertices)

    return error * grad


# ============================================================================
# 2. Force-Fluctuation Sign Assignment
# ============================================================================

def compute_force_vector(
    theta: np.ndarray,
    topology: ObserverTopology,
    loss_type: Literal["quadratic", "feedforward_mse"] = "quadratic",
    target_output: float = 1.0,
    n_vertices: int = None
) -> np.ndarray:
    """Compute force vector F = -∇L at parameter point θ.

    Args:
        theta: Parameter values
        topology: Observer topology
        loss_type: Which loss function to use
        target_output: Target for feedforward loss
        n_vertices: Number of vertices (inferred if None)

    Returns:
        F: Force vector (n_params,)
    """
    if loss_type == "quadratic":
        # For quadratic loss, edges contribute their current weights
        # This is a toy model; real weights would come from edge_weight_gaussian
        # For simplicity: treat theta as effective "weights"
        grad_L = loss_gradient_quadratic(theta)

    elif loss_type == "feedforward_mse":
        grad_L = loss_gradient_feedforward_mse(
            theta, topology, target_output, n_vertices
        )
    else:
        raise ValueError(f"Unknown loss_type: {loss_type}")

    # Force is negative gradient
    F = -grad_L
    return F


def compute_alignment(
    edge_gradient: np.ndarray,
    force: np.ndarray
) -> float:
    """Compute alignment between edge gradient and force.

    α_e = |∇w_e · F| / (|∇w_e| |F|)

    This is |cos(angle(∇w_e, F))| ∈ [0, 1].
    """
    norm_edge = np.linalg.norm(edge_gradient)
    norm_force = np.linalg.norm(force)

    if norm_edge < 1e-15 or norm_force < 1e-15:
        return 0.0

    dot_product = np.abs(np.dot(edge_gradient, force))
    alignment = dot_product / (norm_edge * norm_force)

    return alignment


def assign_force_fluctuation_signs(
    theta: np.ndarray,
    topology: ObserverTopology,
    loss_type: Literal["quadratic", "feedforward_mse"] = "quadratic",
    alignment_threshold: float = 1.0 / np.sqrt(2),  # 45 degrees
    target_output: float = 1.0,
    n_vertices: int = None
) -> tuple[list[int], dict]:
    """Assign edge signs using force-fluctuation decomposition.

    Args:
        theta: Parameter point
        topology: Observer topology
        loss_type: Loss function type
        alignment_threshold: α_crit; edges with α > α_crit get σ = -1
        target_output: Target for feedforward loss
        n_vertices: Number of vertices

    Returns:
        signs: List of signs [-1 or +1] for each edge
        diagnostics: Dict with alignment values, force norm, etc.
    """
    if n_vertices is None:
        if topology.edges:
            n_vertices = max(max(e) for e in topology.edges) + 1
        else:
            n_vertices = topology.n_params

    # Compute force vector F = -∇L
    F = compute_force_vector(theta, topology, loss_type, target_output, n_vertices)

    # Compute alignment for each edge
    alignments = []
    signs = []

    for edge in topology.edges:
        grad_e = compute_edge_gradient(edge, theta, n_vertices)
        alpha_e = compute_alignment(grad_e, F)
        alignments.append(alpha_e)

        # Sign assignment: timelike if strongly aligned, spacelike otherwise
        if alpha_e > alignment_threshold:
            signs.append(-1)  # Timelike (aligned with force)
        else:
            signs.append(+1)  # Spacelike (orthogonal to force)

    diagnostics = {
        "force": F,
        "force_norm": np.linalg.norm(F),
        "alignments": alignments,
        "threshold": alignment_threshold,
        "n_timelike": sum(1 for s in signs if s == -1),
        "n_spacelike": sum(1 for s in signs if s == +1),
    }

    return signs, diagnostics


# ============================================================================
# 3. Comparison with Adjacency Rule
# ============================================================================

@dataclass
class SignComparisonResult:
    """Results comparing force-fluctuation vs adjacency sign assignments."""

    topology: ObserverTopology
    theta: np.ndarray
    loss_type: str

    # Signs
    signs_adjacency: list[int]
    signs_force_fluctuation: list[int]

    # Agreement
    n_edges_agree: int
    n_edges_disagree: int
    fraction_agreement: float

    # Edge-by-edge details
    edge_details: list[dict]

    # Mass tensor eigenvalues
    M_adjacency_eigenvalues: np.ndarray
    M_force_fluctuation_eigenvalues: np.ndarray

    # Signature characteristics
    is_lorentzian_adjacency: bool
    is_lorentzian_force_fluctuation: bool

    # β_c values
    beta_c_adjacency: float
    beta_c_force_fluctuation: float

    # Diagnostics from force computation
    force_diagnostics: dict


def compare_sign_assignments(
    theta: np.ndarray,
    topology_base: ObserverTopology,
    loss_type: Literal["quadratic", "feedforward_mse"] = "quadratic",
    alignment_threshold: float = 1.0 / np.sqrt(2),
    n_vertices: int = None
) -> SignComparisonResult:
    """Compare adjacency vs force-fluctuation sign assignments.

    Args:
        theta: Parameter point
        topology_base: Observer topology (will be cloned with different signs)
        loss_type: Loss function type
        alignment_threshold: Alignment threshold for force-fluctuation
        n_vertices: Number of vertices

    Returns:
        SignComparisonResult with detailed comparison
    """
    if n_vertices is None:
        if topology_base.edges:
            n_vertices = max(max(e) for e in topology_base.edges) + 1
        else:
            n_vertices = topology_base.n_params

    # Get adjacency signs (already in topology_base if created with sign_mode="adjacency")
    signs_adjacency = list(topology_base.edge_signs)

    # Get force-fluctuation signs
    signs_ff, force_diag = assign_force_fluctuation_signs(
        theta, topology_base, loss_type, alignment_threshold,
        target_output=1.0, n_vertices=n_vertices
    )

    # Compare edge by edge
    edge_details = []
    n_agree = 0
    n_disagree = 0

    for i, edge in enumerate(topology_base.edges):
        s_adj = signs_adjacency[i]
        s_ff = signs_ff[i]
        agree = (s_adj == s_ff)

        if agree:
            n_agree += 1
        else:
            n_disagree += 1

        edge_details.append({
            "edge": edge,
            "sign_adjacency": s_adj,
            "sign_force_fluctuation": s_ff,
            "alignment": force_diag["alignments"][i],
            "agree": agree,
        })

    fraction_agreement = n_agree / len(topology_base.edges) if topology_base.edges else 0.0

    # Create topologies with each sign assignment
    topology_adjacency = ObserverTopology(
        n_params=topology_base.n_params,
        edges=topology_base.edges,
        edge_signs=signs_adjacency,
        graph_type=topology_base.graph_type,
        name=f"{topology_base.graph_type}_adjacency"
    )

    topology_ff = ObserverTopology(
        n_params=topology_base.n_params,
        edges=topology_base.edges,
        edge_signs=signs_ff,
        graph_type=topology_base.graph_type,
        name=f"{topology_base.graph_type}_force_fluctuation"
    )

    # Compute mass tensors
    M_adj = compute_mass_tensor_H1_prime(topology_adjacency, theta, n_vertices)
    M_ff = compute_mass_tensor_H1_prime(topology_ff, theta, n_vertices)

    # Eigenvalues
    M_adj_eigs = np.linalg.eigvalsh(M_adj)
    M_ff_eigs = np.linalg.eigvalsh(M_ff)

    # Check Lorentzian signature (exactly 1 negative eigenvalue)
    n_neg_adj = np.sum(M_adj_eigs < -1e-12)
    n_neg_ff = np.sum(M_ff_eigs < -1e-12)

    is_lorentzian_adj = (n_neg_adj == 1)
    is_lorentzian_ff = (n_neg_ff == 1)

    # Compute β_c
    analysis_adj = compute_beta_c_and_signature(topology_adjacency, theta, n_vertices=n_vertices)
    analysis_ff = compute_beta_c_and_signature(topology_ff, theta, n_vertices=n_vertices)

    return SignComparisonResult(
        topology=topology_base,
        theta=theta,
        loss_type=loss_type,
        signs_adjacency=signs_adjacency,
        signs_force_fluctuation=signs_ff,
        n_edges_agree=n_agree,
        n_edges_disagree=n_disagree,
        fraction_agreement=fraction_agreement,
        edge_details=edge_details,
        M_adjacency_eigenvalues=M_adj_eigs,
        M_force_fluctuation_eigenvalues=M_ff_eigs,
        is_lorentzian_adjacency=is_lorentzian_adj,
        is_lorentzian_force_fluctuation=is_lorentzian_ff,
        beta_c_adjacency=analysis_adj.beta_c,
        beta_c_force_fluctuation=analysis_ff.beta_c,
        force_diagnostics=force_diag,
    )


# ============================================================================
# 4. Systematic Study Across Topologies
# ============================================================================

def systematic_comparison_study(
    n_params_list: list[int] = [3, 4, 5, 6],
    graph_types: list[GraphType] = ["chain", "star", "complete"],
    loss_types: list[str] = ["quadratic", "feedforward_mse"],
    alignment_thresholds: list[float] = [1.0/np.sqrt(2), 0.5, 0.8],
    n_samples_per_config: int = 10,
    seed: int = 42
) -> dict:
    """Systematic study comparing force-fluctuation vs adjacency signs.

    For each configuration (n_params, graph_type, loss_type, threshold):
    - Generate random parameter points
    - Compare sign assignments
    - Record agreement rates, Lorentzian signature success, etc.

    Returns:
        results: Nested dict with all comparison results
    """
    rng = np.random.default_rng(seed)
    results = {}

    total_configs = len(n_params_list) * len(graph_types) * len(loss_types) * len(alignment_thresholds)
    current = 0

    for n in n_params_list:
        for graph_type in graph_types:
            for loss_type in loss_types:
                for threshold in alignment_thresholds:
                    current += 1
                    key = (n, graph_type, loss_type, threshold)

                    print(f"[{current}/{total_configs}] n={n}, graph={graph_type}, "
                          f"loss={loss_type}, threshold={threshold:.3f}...", end=" ")

                    # Create base topology with adjacency signs
                    topology = create_observer_topology(
                        n_params=n,
                        graph_type=graph_type,
                        sign_mode="adjacency",
                        rng=rng
                    )

                    if not topology.edges:
                        print("SKIP (no edges)")
                        continue

                    # Sample random parameter points
                    comparisons = []
                    for _ in range(n_samples_per_config):
                        theta = rng.normal(0, 0.5, size=n)

                        comparison = compare_sign_assignments(
                            theta, topology, loss_type, threshold
                        )
                        comparisons.append(comparison)

                    # Aggregate statistics
                    agreement_rates = [c.fraction_agreement for c in comparisons]
                    lorentzian_rates_adj = [c.is_lorentzian_adjacency for c in comparisons]
                    lorentzian_rates_ff = [c.is_lorentzian_force_fluctuation for c in comparisons]

                    mean_agreement = np.mean(agreement_rates)
                    lorentzian_frac_adj = np.mean(lorentzian_rates_adj)
                    lorentzian_frac_ff = np.mean(lorentzian_rates_ff)

                    results[key] = {
                        "n_params": n,
                        "graph_type": graph_type,
                        "loss_type": loss_type,
                        "threshold": threshold,
                        "n_samples": len(comparisons),
                        "mean_agreement": mean_agreement,
                        "lorentzian_frac_adjacency": lorentzian_frac_adj,
                        "lorentzian_frac_force_fluctuation": lorentzian_frac_ff,
                        "comparisons": comparisons,  # Store individual results
                    }

                    print(f"Agreement: {mean_agreement*100:.1f}%, "
                          f"Lorentzian(adj): {lorentzian_frac_adj*100:.1f}%, "
                          f"Lorentzian(FF): {lorentzian_frac_ff*100:.1f}%")

    return results


# ============================================================================
# 5. Self-Tests
# ============================================================================

def run_self_tests() -> bool:
    """TDD self-tests for force-fluctuation implementation."""

    print("=" * 70)
    print("SELF-TESTS: Force-Fluctuation Sign Assignment")
    print("=" * 70)

    all_passed = True

    def check(name: str, condition: bool, detail: str = ""):
        nonlocal all_passed
        status = "PASS" if condition else "FAIL"
        if not condition:
            all_passed = False
        print(f"  [{status}] {name}{' -- ' + detail if detail else ''}")

    # Test 1: Force computation
    print("\nTest 1: Force computation")
    theta_2d = np.array([1.0, 0.5])
    topology_simple = create_observer_topology(2, "chain", "adjacency")

    F_quad = compute_force_vector(theta_2d, topology_simple, "quadratic")
    check("Quadratic force = -θ", np.allclose(F_quad, -theta_2d))

    F_ff = compute_force_vector(theta_2d, topology_simple, "feedforward_mse")
    check("Feedforward force computed", F_ff.shape == (2,))

    # Test 2: Alignment computation
    print("\nTest 2: Alignment computation")
    v1 = np.array([1.0, 0.0])
    v2 = np.array([1.0, 0.0])
    alpha_parallel = compute_alignment(v1, v2)
    check("Parallel vectors: alignment = 1", np.isclose(alpha_parallel, 1.0))

    v3 = np.array([0.0, 1.0])
    alpha_perp = compute_alignment(v1, v3)
    check("Perpendicular vectors: alignment = 0", np.isclose(alpha_perp, 0.0))

    v4 = np.array([1.0, 1.0])
    alpha_45 = compute_alignment(v1, v4)
    check("45-degree vectors: alignment = 1/√2",
          np.isclose(alpha_45, 1.0/np.sqrt(2)))

    # Test 3: Sign assignment
    print("\nTest 3: Force-fluctuation sign assignment")
    topology_chain = create_observer_topology(3, "chain", "adjacency")
    theta_3d = np.array([1.0, 0.5, -0.3])  # Non-zero to get non-zero force

    signs_ff, diag = assign_force_fluctuation_signs(
        theta_3d, topology_chain, "quadratic"
    )

    check("FF signs computed", len(signs_ff) == len(topology_chain.edges))
    check("Signs are ±1", all(s in [-1, 1] for s in signs_ff))
    check("Force is non-zero", diag["force_norm"] > 1e-10,
          f"||F|| = {diag['force_norm']:.3e}")

    # Test 4: Comparison
    print("\nTest 4: Sign comparison")
    comparison = compare_sign_assignments(theta_3d, topology_chain, "quadratic")

    check("Comparison computed", comparison is not None)
    check("Agreement fraction in [0,1]",
          0.0 <= comparison.fraction_agreement <= 1.0)
    check("Edge details match edge count",
          len(comparison.edge_details) == len(topology_chain.edges))

    # Test 5: Lorentzian signature check
    print("\nTest 5: Lorentzian signature from FF signs")
    # Force-fluctuation should produce exactly 1 negative eigenvalue (rank-1 force)
    n_negative_ff = np.sum(comparison.M_force_fluctuation_eigenvalues < -1e-12)
    check("FF produces at most 1 negative eigenvalue", n_negative_ff <= 1,
          f"Found {n_negative_ff} negative eigenvalues")

    # Test 6: Threshold sensitivity
    print("\nTest 6: Threshold sensitivity")
    # Use a different theta to ensure variety in alignments
    theta_varied = np.array([2.0, 0.1, -1.5])
    signs_strict, _ = assign_force_fluctuation_signs(
        theta_varied, topology_chain, "quadratic", alignment_threshold=0.9
    )
    signs_loose, _ = assign_force_fluctuation_signs(
        theta_varied, topology_chain, "quadratic", alignment_threshold=0.3
    )

    n_timelike_strict = sum(1 for s in signs_strict if s == -1)
    n_timelike_loose = sum(1 for s in signs_loose if s == -1)

    check("Stricter threshold => fewer timelike edges",
          n_timelike_strict <= n_timelike_loose,
          f"strict: {n_timelike_strict}, loose: {n_timelike_loose}")

    print("\n" + "=" * 70)
    print(f"SELF-TESTS: {'ALL PASSED ✓' if all_passed else 'SOME FAILED ✗'}")
    print("=" * 70)

    return all_passed


# ============================================================================
# 6. Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Force-fluctuation edge sign assignment numerical test"
    )
    parser.add_argument("--test", action="store_true",
                        help="Run self-tests only")
    parser.add_argument("--study", action="store_true",
                        help="Run systematic comparison study")
    parser.add_argument("--n-samples", type=int, default=10,
                        help="Samples per configuration")
    parser.add_argument("--output", type=str,
                        default="/Users/Max_1/Projects/PhysicsResearch/cosmological-unification/experience/insights/FORCE-FLUCTUATION-NUMERICAL-TEST-2026-02-16.md",
                        help="Output markdown file")

    args = parser.parse_args()

    if args.test:
        import sys
        success = run_self_tests()
        sys.exit(0 if success else 1)

    if args.study:
        print("\n" + "=" * 70)
        print("FORCE-FLUCTUATION SIGN ASSIGNMENT: NUMERICAL TEST")
        print("=" * 70)
        print()

        # Run self-tests first
        if not run_self_tests():
            print("\nSelf-tests failed. Aborting study.")
            import sys
            sys.exit(1)

        print("\n" + "=" * 70)
        print("SYSTEMATIC COMPARISON STUDY")
        print("=" * 70)
        print()

        results = systematic_comparison_study(
            n_params_list=[3, 4, 5, 6],
            graph_types=["chain", "star", "complete"],
            loss_types=["quadratic", "feedforward_mse"],
            alignment_thresholds=[1.0/np.sqrt(2), 0.5, 0.8],
            n_samples_per_config=args.n_samples
        )

        # Generate markdown report
        from datetime import datetime

        md_lines = []
        md_lines.append("# Force-Fluctuation Edge Sign Assignment: Numerical Test")
        md_lines.append("")
        md_lines.append(f"**Generated**: {datetime.now().isoformat()}")
        md_lines.append(f"**Samples per configuration**: {args.n_samples}")
        md_lines.append("")
        md_lines.append("## Research Question")
        md_lines.append("")
        md_lines.append("Can edge signs σ(e) ∈ {+1, -1} be derived from the force-fluctuation")
        md_lines.append("decomposition (Approach 2 from EDGE-SIGN-ORIGIN-RESEARCH-2026-02-16.md)")
        md_lines.append("rather than imposed via the adjacency rule?")
        md_lines.append("")
        md_lines.append("## Methodology")
        md_lines.append("")
        md_lines.append("**Force-Fluctuation Sign Rule**:")
        md_lines.append("```")
        md_lines.append("F = -∇L                    (force on parameters)")
        md_lines.append("α_e = |∇w_e · F| / (|∇w_e| |F|)   (alignment)")
        md_lines.append("σ_FF(e) = -1  if α_e > α_crit     (timelike)")
        md_lines.append("σ_FF(e) = +1  if α_e ≤ α_crit     (spacelike)")
        md_lines.append("```")
        md_lines.append("")
        md_lines.append("**Test Protocol**:")
        md_lines.append("1. For each topology (O3, O4, O5, O6) x (chain, star, complete)")
        md_lines.append("2. Sample random parameter points θ ~ N(0, 0.5²)")
        md_lines.append("3. Compute force F for two loss types (quadratic, feedforward MSE)")
        md_lines.append("4. Assign signs via force-fluctuation rule with various thresholds")
        md_lines.append("5. Compare with adjacency rule signs")
        md_lines.append("6. Check: Does force-fluctuation produce Lorentzian signature?")
        md_lines.append("")
        md_lines.append("## Results")
        md_lines.append("")

        # Table 1: Agreement rates
        md_lines.append("### Table 1: Agreement with Adjacency Rule")
        md_lines.append("")
        md_lines.append("Mean fraction of edges where σ_FF = σ_adjacency:")
        md_lines.append("")

        # Group by (loss_type, threshold)
        for loss_type in ["quadratic", "feedforward_mse"]:
            for threshold in [1.0/np.sqrt(2), 0.5, 0.8]:
                md_lines.append(f"#### {loss_type}, threshold={threshold:.3f}")
                md_lines.append("")
                md_lines.append("| n | chain | star | complete |")
                md_lines.append("|---|-------|------|----------|")

                for n in [3, 4, 5, 6]:
                    row = f"| {n} |"
                    for graph_type in ["chain", "star", "complete"]:
                        key = (n, graph_type, loss_type, threshold)
                        if key in results:
                            agreement = results[key]["mean_agreement"] * 100
                            row += f" {agreement:5.1f}% |"
                        else:
                            row += " - |"
                    md_lines.append(row)

                md_lines.append("")

        # Table 2: Lorentzian success rates
        md_lines.append("### Table 2: Lorentzian Signature Success Rates")
        md_lines.append("")
        md_lines.append("Fraction of samples producing exactly 1 negative eigenvalue:")
        md_lines.append("")

        for loss_type in ["quadratic", "feedforward_mse"]:
            for threshold in [1.0/np.sqrt(2), 0.5, 0.8]:
                md_lines.append(f"#### {loss_type}, threshold={threshold:.3f}")
                md_lines.append("")
                md_lines.append("**Adjacency Rule**:")
                md_lines.append("")
                md_lines.append("| n | chain | star | complete |")
                md_lines.append("|---|-------|------|----------|")

                for n in [3, 4, 5, 6]:
                    row = f"| {n} |"
                    for graph_type in ["chain", "star", "complete"]:
                        key = (n, graph_type, loss_type, threshold)
                        if key in results:
                            frac = results[key]["lorentzian_frac_adjacency"] * 100
                            row += f" {frac:5.1f}% |"
                        else:
                            row += " - |"
                    md_lines.append(row)

                md_lines.append("")
                md_lines.append("**Force-Fluctuation Rule**:")
                md_lines.append("")
                md_lines.append("| n | chain | star | complete |")
                md_lines.append("|---|-------|------|----------|")

                for n in [3, 4, 5, 6]:
                    row = f"| {n} |"
                    for graph_type in ["chain", "star", "complete"]:
                        key = (n, graph_type, loss_type, threshold)
                        if key in results:
                            frac = results[key]["lorentzian_frac_force_fluctuation"] * 100
                            row += f" {frac:5.1f}% |"
                        else:
                            row += " - |"
                    md_lines.append(row)

                md_lines.append("")

        # Analysis
        md_lines.append("## Analysis")
        md_lines.append("")
        md_lines.append("### Key Findings")
        md_lines.append("")

        # Compute summary statistics
        all_agreements = []
        all_lorentzian_ff = []
        all_lorentzian_adj = []

        for key, data in results.items():
            all_agreements.append(data["mean_agreement"])
            all_lorentzian_ff.append(data["lorentzian_frac_force_fluctuation"])
            all_lorentzian_adj.append(data["lorentzian_frac_adjacency"])

        if all_agreements:
            md_lines.append(f"1. **Overall agreement with adjacency rule**: "
                          f"{np.mean(all_agreements)*100:.1f}% ± {np.std(all_agreements)*100:.1f}%")

        if all_lorentzian_ff:
            md_lines.append(f"2. **Lorentzian success (force-fluctuation)**: "
                          f"{np.mean(all_lorentzian_ff)*100:.1f}% ± {np.std(all_lorentzian_ff)*100:.1f}%")

        if all_lorentzian_adj:
            md_lines.append(f"3. **Lorentzian success (adjacency)**: "
                          f"{np.mean(all_lorentzian_adj)*100:.1f}% ± {np.std(all_lorentzian_adj)*100:.1f}%")

        md_lines.append("")
        md_lines.append("### Interpretation")
        md_lines.append("")
        md_lines.append("**HONEST ASSESSMENT (to be filled after reviewing results)**:")
        md_lines.append("")
        md_lines.append("- Does force-fluctuation reliably produce Lorentzian signature?")
        md_lines.append("- How does it compare to adjacency rule?")
        md_lines.append("- What is the threshold sensitivity?")
        md_lines.append("- Are there failure modes?")
        md_lines.append("")
        md_lines.append("**Confidence Level**: TBD")
        md_lines.append("")
        md_lines.append("**Negative Results** (if any): TBD")
        md_lines.append("")

        # Metadata
        md_lines.append("## Metadata")
        md_lines.append("")
        md_lines.append("```yaml")
        md_lines.append("document: FORCE-FLUCTUATION-NUMERICAL-TEST-2026-02-16.md")
        md_lines.append(f"created: {datetime.now().isoformat()}")
        md_lines.append("approach: Approach 2 (Force-Fluctuation Decomposition)")
        md_lines.append("reference: EDGE-SIGN-ORIGIN-RESEARCH-2026-02-16.md Section 3")
        md_lines.append(f"n_configurations: {len(results)}")
        md_lines.append(f"samples_per_config: {args.n_samples}")
        md_lines.append("loss_types: [quadratic, feedforward_mse]")
        md_lines.append("alignment_thresholds: [0.707, 0.5, 0.8]")
        md_lines.append("```")

        # Write to file
        output_text = "\n".join(md_lines)

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_text)

        print(f"\n\nResults written to: {args.output}")
        print(f"Total configurations: {len(results)}")
        print("\nDone.")
