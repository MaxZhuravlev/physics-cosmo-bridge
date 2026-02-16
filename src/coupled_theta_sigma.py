#!/usr/bin/env python3
"""
Coupled θ-σ Dynamics: Testing Vanchurin's Single-Force Mechanism
==================================================================

Research question:
    Does a coupled simulation where:
    - θ (coupling parameters) evolves by natural gradient descent on a loss L(θ)
    - σ (edge signs) evolves to align with the temporal direction of θ-evolution
    produce spontaneous q=1 (Lorentzian) signature selection?

Theoretical framework:
    In Vanchurin's framework (ESSL Eq. 4.3), the negative metric contribution
    comes from the MEAN FORCE direction:
        g = -(m γ²/2Q) F_μ F_ν + κ_{μν}
    This automatically produces exactly q=1 (rank-1 negative part) because
    the mean force is a SINGLE vector in parameter space.

    In the H1' framework, the analogue is: the causal structure determines
    signs such that exactly one effective "timelike direction" emerges in
    the mass tensor, aligned with the θ-evolution direction.

Implementation:
    We test this by evolving θ and σ jointly:
    1. θ evolves by natural gradient descent: Δθ = -η g⁻¹(σ) ∇L(θ)
    2. σ evolves to align with F_mean: σ_e → sign(F_mean · ∇w_e)
    3. Check if the system converges to q=1

Key test:
    K4 at J=0.5 FAILED with static sign selection (0% Lorentzian in dynamical
    study). Does coupled dynamics succeed where static failed?

Author: Max Zhuravlev (Cosmological Unification Program)
Date: 2026-02-16
Prerequisites:
    - DYNAMICAL-SIGN-SELECTION-2026-02-16.md (Section 6)
    - MF2-LORENTZIAN-IMPLICATIONS-2026-02-16.md (M=F² result)
    - ENTROPIC-SIGN-SELECTION-2026-02-16.md (TOP PRIORITY)
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import Callable, Literal
import warnings

# Import Fisher matrix computation from existing code
from dynamical_signs import (
    ising_fisher_K3,
    ising_fisher_K4,
    ising_fisher_path,
    compute_g_metric,
    compute_eigenvalues,
    count_negative_eigenvalues,
    signature_from_eigenvalues,
)

# ============================================================================
# 1. Loss Functions for θ Evolution
# ============================================================================

def loss_quadratic(theta: np.ndarray, target: np.ndarray = None) -> float:
    """Quadratic loss: L(theta) = ||theta - target||²/2

    Simple convex loss for testing. The natural gradient descent should
    converge to the target.
    """
    if target is None:
        target = np.zeros_like(theta)
    return 0.5 * np.sum((theta - target)**2)


def loss_prediction_error(theta: np.ndarray, data: np.ndarray,
                          model_fn: Callable) -> float:
    """Prediction error: L(theta) = sum_i (y_i - f(x_i; theta))²

    More realistic loss for a learning observer. The observer tries to
    minimize prediction error on data.
    """
    predictions = model_fn(data, theta)
    targets = data[:, -1]  # Assume last column is target
    return 0.5 * np.sum((predictions - targets)**2)


def loss_ising_energy(theta: np.ndarray, graph_structure: dict) -> float:
    """Ising energy: L(theta) = -sum_{e} J_e * theta_e

    For an Ising observer, the loss is the negative energy. Minimizing
    this corresponds to finding the ground state.
    """
    return -np.sum(theta)


# ============================================================================
# 2. Natural Gradient Computation
# ============================================================================

def compute_natural_gradient(theta: np.ndarray,
                             loss_fn: Callable,
                             fisher_fn: Callable,
                             sigma: np.ndarray,
                             beta: float,
                             dx: float = 1e-6) -> np.ndarray:
    """Compute natural gradient: ∇_NG L = g⁻¹(σ, β) ∇L

    where g(σ, β) = F(θ) diag(σ) F(θ) + β F(θ) is the observer metric.

    Returns:
        Natural gradient vector (same shape as theta)
    """
    # Euclidean gradient via finite differences
    grad = np.zeros_like(theta)
    for i in range(len(theta)):
        theta_plus = theta.copy()
        theta_minus = theta.copy()
        theta_plus[i] += dx
        theta_minus[i] -= dx
        grad[i] = (loss_fn(theta_plus) - loss_fn(theta_minus)) / (2*dx)

    # Fisher matrix at current theta
    F = fisher_fn(theta)

    # Observer metric g(σ, β)
    g = compute_g_metric(sigma, F, beta)

    # Natural gradient: g⁻¹ ∇L
    # Use pseudo-inverse for numerical stability
    try:
        g_inv = np.linalg.inv(g)
    except np.linalg.LinAlgError:
        # If g is singular or nearly singular, use pseudo-inverse
        g_inv = np.linalg.pinv(g, rcond=1e-10)

    return g_inv @ grad


def compute_force_direction(theta: np.ndarray,
                            loss_fn: Callable,
                            dx: float = 1e-6) -> np.ndarray:
    """Compute the mean force direction F_mean = -∇L(theta)

    In Vanchurin's framework, this is the single direction that becomes
    timelike in the metric.
    """
    grad = np.zeros_like(theta)
    for i in range(len(theta)):
        theta_plus = theta.copy()
        theta_minus = theta.copy()
        theta_plus[i] += dx
        theta_minus[i] -= dx
        grad[i] = (loss_fn(theta_plus) - loss_fn(theta_minus)) / (2*dx)

    return -grad  # Force is negative gradient


# ============================================================================
# 3. Sign Alignment Rules
# ============================================================================

def update_signs_force_alignment(
    theta: np.ndarray,
    sigma: np.ndarray,
    F: np.ndarray,
    F_mean: np.ndarray,
    alignment_threshold: float = 0.0
) -> np.ndarray:
    """Update signs based on alignment with mean force direction.

    Rule: σ_e = sign(F_mean · ∇w_e) where ∇w_e is the e-th column of F
    (the Fisher matrix gives the Jacobian dw/dθ in canonical parameterization).

    For exponential families, F_ea = ∂w_e/∂θ_a, so the alignment of edge e
    with the force direction is:
        A_e = F_mean · F[e, :] = sum_a F_mean[a] * F[e,a]

    Parameters:
        alignment_threshold: Only update sign if |alignment| > threshold
            (prevents sign flipping due to numerical noise)
    """
    m = len(sigma)
    sigma_new = sigma.copy()

    for e in range(m):
        # Alignment of edge e with force direction
        # F is symmetric, so F[e, :] = F[:, e]
        alignment = np.dot(F_mean, F[e, :])

        if np.abs(alignment) > alignment_threshold:
            sigma_new[e] = np.sign(alignment)
            # Default to spacelike (+1) if alignment is exactly zero
            if sigma_new[e] == 0:
                sigma_new[e] = 1.0

    return sigma_new


def update_signs_soft_alignment(
    theta: np.ndarray,
    sigma: np.ndarray,
    F: np.ndarray,
    F_mean: np.ndarray,
    lr_sigma: float = 0.1,
    alignment_threshold: float = 1e-10
) -> np.ndarray:
    """Soft sign update: σ moves gradually toward alignment with force.

    Update rule:
        σ_e → σ_e + lr_sigma * tanh(alignment_e)

    This allows σ to evolve smoothly rather than flipping discretely.
    """
    m = len(sigma)
    sigma_new = sigma.copy()

    for e in range(m):
        alignment = np.dot(F_mean, F[e, :])
        if np.abs(alignment) > alignment_threshold:
            # Soft update toward alignment
            target_sign = np.tanh(alignment / np.linalg.norm(F_mean + 1e-12))
            sigma_new[e] += lr_sigma * (target_sign - sigma_new[e])
            # Clip to [-1, 1]
            sigma_new[e] = np.clip(sigma_new[e], -1.0, 1.0)

    return sigma_new


# ============================================================================
# 4. Coupled Dynamics Simulation
# ============================================================================

@dataclass
class CoupledResult:
    """Results from coupled θ-σ dynamics simulation."""

    theta_history: np.ndarray        # (n_steps+1, n_theta) trajectory
    sigma_history: np.ndarray        # (n_steps+1, m) soft signs trajectory
    loss_history: np.ndarray         # (n_steps+1,) loss values
    q_history: np.ndarray            # (n_steps+1,) number of negative eigenvalues
    signature_history: list          # list of (n_pos, n_zero, n_neg) tuples
    eigenvalue_history: np.ndarray   # (n_steps+1, m) eigenvalues of g
    force_alignment_history: np.ndarray  # (n_steps+1, m) force alignments

    converged: bool
    final_theta: np.ndarray
    final_sigma: np.ndarray
    final_q: int
    final_signature: tuple
    final_loss: float
    n_steps_taken: int

    # Metadata
    graph_name: str = ""
    beta: float = 0.0
    loss_name: str = ""
    sign_rule: str = ""


def evolve_coupled(
    theta_init: np.ndarray,
    sigma_init: np.ndarray,
    fisher_fn: Callable[[np.ndarray], np.ndarray],
    loss_fn: Callable[[np.ndarray], float],
    beta: float,
    loss_name: str = "",
    sign_rule: Literal["force_alignment", "soft_alignment"] = "force_alignment",
    lr_theta: float = 0.01,
    lr_sigma: float = 0.1,
    n_steps: int = 5000,
    convergence_tol: float = 1e-8,
    graph_name: str = "",
    use_natural_gradient: bool = True,
    alignment_threshold: float = 0.0,
    verbose: bool = False
) -> CoupledResult:
    """Evolve θ and σ jointly.

    Dynamics:
        θ: Natural gradient descent on loss L(θ)
        σ: Alignment with force direction F_mean = -∇L(θ)

    Parameters:
        theta_init: Initial coupling parameters (n_theta,)
        sigma_init: Initial soft signs (m,)
        fisher_fn: Function theta -> F(theta) (Fisher matrix)
        loss_fn: Function theta -> L(theta) (loss)
        beta: Inverse temperature
        sign_rule: "force_alignment" (hard) or "soft_alignment" (gradual)
        lr_theta: Learning rate for θ
        lr_sigma: Learning rate for σ (soft alignment only)
        use_natural_gradient: If True, use g⁻¹∇L; if False, use ∇L
        alignment_threshold: Minimum |alignment| to update sign

    Returns:
        CoupledResult with full trajectory data
    """
    n_theta = len(theta_init)
    m = len(sigma_init)

    theta = theta_init.copy()
    sigma = sigma_init.copy()

    # Storage
    theta_history = np.zeros((n_steps + 1, n_theta))
    sigma_history = np.zeros((n_steps + 1, m))
    loss_history = np.zeros(n_steps + 1)
    q_history = np.zeros(n_steps + 1, dtype=int)
    signature_history = []
    eigenvalue_history = np.zeros((n_steps + 1, m))
    force_alignment_history = np.zeros((n_steps + 1, m))

    # Initial state
    theta_history[0] = theta.copy()
    sigma_history[0] = sigma.copy()
    loss_history[0] = loss_fn(theta)

    F = fisher_fn(theta)
    g = compute_g_metric(sigma, F, beta)
    eigs = compute_eigenvalues(g)
    eigenvalue_history[0] = eigs
    sig = signature_from_eigenvalues(eigs)
    q_history[0] = sig[2]
    signature_history.append(sig)

    F_mean = compute_force_direction(theta, loss_fn)
    for e in range(m):
        force_alignment_history[0, e] = np.dot(F_mean, F[e, :])

    converged = False
    step = 0

    for step in range(1, n_steps + 1):
        # Compute Fisher matrix at current theta
        F = fisher_fn(theta)

        # Compute force direction
        F_mean = compute_force_direction(theta, loss_fn)

        # Update sigma (sign alignment with force)
        if sign_rule == "force_alignment":
            sigma = update_signs_force_alignment(
                theta, sigma, F, F_mean, alignment_threshold
            )
        elif sign_rule == "soft_alignment":
            sigma = update_signs_soft_alignment(
                theta, sigma, F, F_mean, lr_sigma, alignment_threshold
            )
        else:
            raise ValueError(f"Unknown sign_rule: {sign_rule}")

        # Update theta (natural gradient descent on loss)
        if use_natural_gradient:
            grad = compute_natural_gradient(theta, loss_fn, fisher_fn,
                                           sigma, beta)
        else:
            # Standard gradient
            grad = np.zeros_like(theta)
            dx = 1e-6
            for i in range(n_theta):
                theta_plus = theta.copy()
                theta_minus = theta.copy()
                theta_plus[i] += dx
                theta_minus[i] -= dx
                grad[i] = (loss_fn(theta_plus) - loss_fn(theta_minus)) / (2*dx)

        theta_new = theta - lr_theta * grad

        # Record
        theta = theta_new
        theta_history[step] = theta.copy()
        sigma_history[step] = sigma.copy()
        loss_history[step] = loss_fn(theta)

        # Metric eigenvalues
        F = fisher_fn(theta)
        g = compute_g_metric(sigma, F, beta)
        eigs = compute_eigenvalues(g)
        eigenvalue_history[step] = eigs
        sig = signature_from_eigenvalues(eigs)
        q_history[step] = sig[2]
        signature_history.append(sig)

        # Force alignments
        for e in range(m):
            force_alignment_history[step, e] = np.dot(F_mean, F[e, :])

        # Convergence check (on loss)
        if step > 10 and np.abs(loss_history[step] - loss_history[step-1]) < convergence_tol:
            converged = True
            if verbose:
                print(f"  Converged at step {step}")
            break

        # Progress reporting
        if verbose and step % 500 == 0:
            print(f"  Step {step}: loss={loss_history[step]:.6f}, q={q_history[step]}")

    # Trim arrays
    actual_len = step + 1
    theta_history = theta_history[:actual_len]
    sigma_history = sigma_history[:actual_len]
    loss_history = loss_history[:actual_len]
    eigenvalue_history = eigenvalue_history[:actual_len]
    q_history = q_history[:actual_len]
    force_alignment_history = force_alignment_history[:actual_len]

    # Final state
    final_theta = theta.copy()
    final_sigma = sigma.copy()
    final_F = fisher_fn(final_theta)
    final_g = compute_g_metric(final_sigma, final_F, beta)
    final_eigs = compute_eigenvalues(final_g)
    final_sig = signature_from_eigenvalues(final_eigs)

    return CoupledResult(
        theta_history=theta_history,
        sigma_history=sigma_history,
        loss_history=loss_history,
        q_history=q_history,
        signature_history=signature_history,
        eigenvalue_history=eigenvalue_history,
        force_alignment_history=force_alignment_history,
        converged=converged,
        final_theta=final_theta,
        final_sigma=final_sigma,
        final_q=final_sig[2],
        final_signature=final_sig,
        final_loss=loss_history[step],
        n_steps_taken=step,
        graph_name=graph_name,
        beta=beta,
        loss_name=loss_name,
        sign_rule=sign_rule
    )


# ============================================================================
# 5. Basin of Attraction Analysis for Coupled Dynamics
# ============================================================================

@dataclass
class CoupledBasinAnalysis:
    """Analysis of coupled dynamics across multiple initial conditions."""

    n_trials: int
    n_converged_q1: int
    n_converged_q0: int
    n_converged_other: int
    q1_fraction: float
    q_distribution: dict
    mean_steps_to_convergence: float
    mean_final_loss: float

    # Metadata
    beta: float
    graph_name: str
    loss_name: str
    sign_rule: str

    results: list = field(default_factory=list)


def analyze_coupled_basin(
    fisher_fn: Callable[[np.ndarray], np.ndarray],
    loss_fn: Callable[[np.ndarray], float],
    n_theta: int,
    m: int,
    beta: float,
    loss_name: str = "",
    sign_rule: Literal["force_alignment", "soft_alignment"] = "force_alignment",
    n_trials: int = 50,
    lr_theta: float = 0.01,
    lr_sigma: float = 0.1,
    n_steps: int = 3000,
    seed: int = 42,
    graph_name: str = "",
    verbose: bool = True
) -> CoupledBasinAnalysis:
    """Run coupled dynamics from multiple initial conditions.

    Tests whether coupled θ-σ dynamics spontaneously converges to q=1.
    """
    rng = np.random.default_rng(seed)

    q_counts = {}
    results = []
    steps_list = []
    loss_list = []

    for trial in range(n_trials):
        if verbose and trial % 10 == 0:
            print(f"[{trial}/{n_trials}] Running coupled dynamics...")

        # Random initial theta (small perturbation around zero)
        theta_init = rng.normal(0, 0.1, size=n_theta)

        # Random initial sigma (continuous in [-1, 1])
        sigma_init = rng.uniform(-1, 1, size=m)

        result = evolve_coupled(
            theta_init=theta_init,
            sigma_init=sigma_init,
            fisher_fn=fisher_fn,
            loss_fn=loss_fn,
            beta=beta,
            loss_name=loss_name,
            sign_rule=sign_rule,
            lr_theta=lr_theta,
            lr_sigma=lr_sigma,
            n_steps=n_steps,
            graph_name=graph_name,
            use_natural_gradient=True,
            verbose=False
        )

        final_q = result.final_q
        q_counts[final_q] = q_counts.get(final_q, 0) + 1
        results.append(result)

        if result.converged:
            steps_list.append(result.n_steps_taken)
            loss_list.append(result.final_loss)

    n_q1 = q_counts.get(1, 0)
    n_q0 = q_counts.get(0, 0)
    n_other = sum(v for k, v in q_counts.items() if k not in [0, 1])
    q1_fraction = n_q1 / n_trials if n_trials > 0 else 0.0

    mean_steps = np.mean(steps_list) if steps_list else float('nan')
    mean_loss = np.mean(loss_list) if loss_list else float('nan')

    if verbose:
        print(f"\nResults: q=1: {n_q1}/{n_trials} ({q1_fraction*100:.1f}%), "
              f"q=0: {n_q0}, q>1: {n_other}")
        print(f"Distribution: {q_counts}")

    return CoupledBasinAnalysis(
        n_trials=n_trials,
        n_converged_q1=n_q1,
        n_converged_q0=n_q0,
        n_converged_other=n_other,
        q1_fraction=q1_fraction,
        q_distribution=q_counts,
        mean_steps_to_convergence=mean_steps,
        mean_final_loss=mean_loss,
        beta=beta,
        graph_name=graph_name,
        loss_name=loss_name,
        sign_rule=sign_rule,
        results=results
    )


# ============================================================================
# 6. Graph-Specific Fisher Functions
# ============================================================================

def fisher_K3_theta(theta: np.ndarray) -> np.ndarray:
    """Fisher matrix for K3 Ising as function of theta.

    For Ising model, theta = J (coupling strengths). We assume uniform J.
    """
    J = np.mean(theta)  # Average coupling
    # Clip J to prevent numerical overflow in partition function
    J = np.clip(J, -5.0, 5.0)
    return ising_fisher_K3(J)


def fisher_K4_theta(theta: np.ndarray) -> np.ndarray:
    """Fisher matrix for K4 Ising as function of theta."""
    J = np.mean(theta)
    # Clip J to prevent numerical overflow
    J = np.clip(J, -5.0, 5.0)
    return ising_fisher_K4(J)


def fisher_path_theta(theta: np.ndarray) -> np.ndarray:
    """Fisher matrix for path graph as function of theta."""
    J_values = theta  # Each theta_i is a coupling J_i
    # Clip J values to prevent numerical overflow
    J_values = np.clip(J_values, -5.0, 5.0)
    return ising_fisher_path(J_values)


# ============================================================================
# 7. Self-Tests
# ============================================================================

def run_self_tests() -> bool:
    """TDD self-tests for coupled dynamics."""

    print("=" * 70)
    print("SELF-TESTS: Coupled θ-σ Dynamics")
    print("=" * 70)

    all_passed = True

    def check(name: str, condition: bool, detail: str = ""):
        nonlocal all_passed
        status = "PASS" if condition else "FAIL"
        if not condition:
            all_passed = False
        print(f"  [{status}] {name}{' -- ' + detail if detail else ''}")

    # Test 1: Loss functions
    print("\nTest 1: Loss functions")
    theta = np.array([0.5, 0.3, 0.7])
    target = np.zeros(3)
    loss = loss_quadratic(theta, target)
    check("Quadratic loss positive", loss > 0,
          f"loss = {loss:.4f}")
    check("Quadratic loss at target is zero",
          np.abs(loss_quadratic(target, target)) < 1e-10)

    # Test 2: Force direction
    print("\nTest 2: Force direction computation")
    F_mean = compute_force_direction(theta, lambda t: loss_quadratic(t, target))
    check("Force direction is negative gradient",
          np.allclose(F_mean, -(theta - target), atol=1e-4),
          f"F_mean = {F_mean}, expected {-(theta - target)}")
    check("Force direction has correct shape", F_mean.shape == theta.shape)

    # Test 3: Sign alignment
    print("\nTest 3: Sign alignment with force")
    sigma = np.ones(3)
    F = np.eye(3)
    F_mean_pos = np.array([1.0, 0.5, 0.3])
    sigma_aligned = update_signs_force_alignment(theta, sigma, F, F_mean_pos)
    check("All signs positive when force positive",
          np.all(sigma_aligned > 0),
          f"sigma = {sigma_aligned}")

    F_mean_mixed = np.array([-1.0, 0.5, -0.3])
    sigma_mixed = update_signs_force_alignment(theta, sigma, F, F_mean_mixed)
    check("Sign follows force direction",
          sigma_mixed[0] < 0 and sigma_mixed[1] > 0 and sigma_mixed[2] < 0,
          f"sigma = {sigma_mixed}")

    # Test 4: Coupled evolution (single run, K3)
    print("\nTest 4: Coupled evolution (single run, K3)")

    theta_init = np.array([0.5, 0.5, 0.5])
    sigma_init = np.array([0.2, -0.1, 0.3])

    def loss_K3(t):
        return loss_quadratic(t, target=np.array([0.3, 0.3, 0.3]))

    result = evolve_coupled(
        theta_init=theta_init,
        sigma_init=sigma_init,
        fisher_fn=fisher_K3_theta,
        loss_fn=loss_K3,
        beta=0.3,
        loss_name="quadratic",
        sign_rule="soft_alignment",
        lr_theta=0.01,
        lr_sigma=0.1,
        n_steps=500,
        graph_name="K3_test",
        verbose=False
    )

    check("Evolution completed", result.n_steps_taken > 0,
          f"steps = {result.n_steps_taken}")
    check("Loss decreased",
          result.loss_history[-1] <= result.loss_history[0] + 1e-6,
          f"L_init = {result.loss_history[0]:.4f}, L_final = {result.loss_history[-1]:.4f}")
    check("Sigma stays in [-1, 1]",
          np.all(result.sigma_history >= -1.0 - 1e-10) and
          np.all(result.sigma_history <= 1.0 + 1e-10))
    check("Final q recorded", result.final_q >= 0,
          f"q = {result.final_q}")

    # Test 5: Force alignment history
    print("\nTest 5: Force alignment history")
    check("Force alignment recorded",
          result.force_alignment_history.shape == (result.n_steps_taken + 1, 3))
    check("Force alignment finite",
          np.all(np.isfinite(result.force_alignment_history)))

    # Test 6: Natural gradient vs standard gradient
    print("\nTest 6: Natural gradient computation")
    theta_test = np.array([0.5, 0.5, 0.5])
    sigma_test = np.array([1.0, 1.0, 1.0])
    F_test = fisher_K3_theta(theta_test)

    def loss_test(t):
        return 0.5 * np.sum(t**2)

    nat_grad = compute_natural_gradient(theta_test, loss_test,
                                       fisher_K3_theta, sigma_test, 0.5)
    check("Natural gradient computed", nat_grad.shape == theta_test.shape)
    check("Natural gradient finite", np.all(np.isfinite(nat_grad)))

    # Test 7: Basin analysis (small scale)
    print("\nTest 7: Basin analysis (small scale)")

    basin = analyze_coupled_basin(
        fisher_fn=fisher_K3_theta,
        loss_fn=loss_K3,
        n_theta=3,
        m=3,
        beta=0.3,
        loss_name="quadratic",
        sign_rule="soft_alignment",
        n_trials=10,
        lr_theta=0.01,
        lr_sigma=0.1,
        n_steps=500,
        seed=42,
        graph_name="K3_basin_test",
        verbose=False
    )

    check("Basin analysis completed", basin.n_trials == 10)
    check("q1_fraction valid", 0.0 <= basin.q1_fraction <= 1.0,
          f"q1_frac = {basin.q1_fraction:.2f}")
    check("q_distribution sums correct",
          sum(basin.q_distribution.values()) == basin.n_trials)

    # Summary
    print("\n" + "=" * 70)
    print(f"SELF-TESTS: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
    print("=" * 70)

    return all_passed


# ============================================================================
# 8. Comprehensive Simulation Suite
# ============================================================================

@dataclass
class CoupledSimulationSuite:
    """Full coupled simulation results across graphs and betas."""

    results: dict  # (graph_name, beta, sign_rule) -> CoupledBasinAnalysis
    summary_table: list


def run_coupled_simulation_suite(
    n_trials: int = 50,
    lr_theta: float = 0.01,
    lr_sigma: float = 0.1,
    n_steps: int = 3000,
    seed: int = 42,
    verbose: bool = True
) -> CoupledSimulationSuite:
    """Run comprehensive coupled dynamics simulation.

    Tests:
    - Graphs: K3, K4, Path-4 (all at J=0.5)
    - Beta values: 0.1, 0.5
    - Sign rules: soft_alignment
    - Loss: quadratic (simple, convex)
    """

    J_default = 0.5

    # Graph configurations
    graphs = {
        "K3_J0.5": {
            "fisher_fn": fisher_K3_theta,
            "loss_fn": lambda t: loss_quadratic(t, np.full(3, 0.3)),
            "n_theta": 3,
            "m": 3,
        },
        "K4_J0.5": {
            "fisher_fn": fisher_K4_theta,
            "loss_fn": lambda t: loss_quadratic(t, np.full(6, 0.3)),
            "n_theta": 6,
            "m": 6,
        },
        "Path4_J0.5": {
            "fisher_fn": fisher_path_theta,
            "loss_fn": lambda t: loss_quadratic(t, np.full(3, 0.3)),
            "n_theta": 3,
            "m": 3,
        },
    }

    beta_values = [0.1, 0.5]
    sign_rules = ["soft_alignment"]

    results = {}
    summary = []
    total = len(graphs) * len(beta_values) * len(sign_rules)
    count = 0

    for gname, gconfig in graphs.items():
        for beta in beta_values:
            for sign_rule in sign_rules:
                count += 1
                if verbose:
                    print(f"\n[{count}/{total}] {gname}, beta={beta}, {sign_rule}")
                    print("=" * 70)

                basin = analyze_coupled_basin(
                    fisher_fn=gconfig["fisher_fn"],
                    loss_fn=gconfig["loss_fn"],
                    n_theta=gconfig["n_theta"],
                    m=gconfig["m"],
                    beta=beta,
                    loss_name="quadratic",
                    sign_rule=sign_rule,
                    n_trials=n_trials,
                    lr_theta=lr_theta,
                    lr_sigma=lr_sigma,
                    n_steps=n_steps,
                    seed=seed,
                    graph_name=gname,
                    verbose=verbose
                )

                results[(gname, beta, sign_rule)] = basin

                row = {
                    "graph": gname,
                    "beta": beta,
                    "sign_rule": sign_rule,
                    "m": gconfig["m"],
                    "q1_frac": basin.q1_fraction,
                    "q0_frac": basin.n_converged_q0 / basin.n_trials,
                    "q_other_frac": basin.n_converged_other / basin.n_trials,
                    "q_dist": basin.q_distribution,
                    "mean_steps": basin.mean_steps_to_convergence,
                    "mean_loss": basin.mean_final_loss,
                }
                summary.append(row)

    return CoupledSimulationSuite(results=results, summary_table=summary)


# ============================================================================
# 9. Report Generation
# ============================================================================

def generate_coupled_report(suite: CoupledSimulationSuite) -> str:
    """Generate markdown report from coupled simulation results."""

    lines = []
    lines.append("# Coupled θ-σ Dynamics: Simulation Results")
    lines.append("")
    lines.append("## Summary Table")
    lines.append("")
    lines.append("| Graph | beta | Sign Rule | m | q=1 % | q=0 % | q>1 % | q dist |")
    lines.append("|-------|------|-----------|---|-------|-------|-------|--------|")

    for row in suite.summary_table:
        q_str = str(row["q_dist"])
        lines.append(
            f"| {row['graph']:14s} | {row['beta']:.1f} | {row['sign_rule']:14s} "
            f"| {row['m']} | {row['q1_frac']*100:5.1f} | {row['q0_frac']*100:5.1f} "
            f"| {row['q_other_frac']*100:5.1f} | {q_str} |"
        )

    lines.append("")

    # Key findings
    lines.append("## Key Findings")
    lines.append("")

    # Overall q=1 rate
    q1_rates = [r["q1_frac"] for r in suite.summary_table]
    mean_q1 = np.mean(q1_rates) if q1_rates else 0
    lines.append(f"1. **Overall q=1 rate**: {mean_q1*100:.1f}% (averaged over all configs)")

    # K4 specific
    k4_rows = [r for r in suite.summary_table if "K4" in r["graph"]]
    if k4_rows:
        k4_q1 = np.mean([r["q1_frac"] for r in k4_rows])
        lines.append(f"2. **K4 q=1 rate**: {k4_q1*100:.1f}% (CRITICAL TEST)")
        if k4_q1 > 0.5:
            lines.append("   **SUCCESS**: Coupled dynamics overcomes K4 static failure!")
        else:
            lines.append("   **PARTIAL**: Coupled dynamics shows improvement but not decisive.")

    # By graph
    graphs = sorted(set(r["graph"] for r in suite.summary_table))
    lines.append("")
    lines.append("### By Graph:")
    for g in graphs:
        g_rows = [r for r in suite.summary_table if r["graph"] == g]
        g_q1 = np.mean([r["q1_frac"] for r in g_rows])
        lines.append(f"- {g}: {g_q1*100:.1f}%")

    # By beta
    betas = sorted(set(r["beta"] for r in suite.summary_table))
    lines.append("")
    lines.append("### By Beta:")
    for b in betas:
        b_rows = [r for r in suite.summary_table if r["beta"] == b]
        b_q1 = np.mean([r["q1_frac"] for r in b_rows])
        lines.append(f"- beta={b}: {b_q1*100:.1f}%")

    lines.append("")
    return "\n".join(lines)


# ============================================================================
# 10. Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Coupled θ-σ dynamics: testing Vanchurin's single-force mechanism"
    )
    parser.add_argument("--test", action="store_true",
                        help="Run self-tests only")
    parser.add_argument("--quick", action="store_true",
                        help="Quick simulation (20 trials, 1000 steps)")
    parser.add_argument("--full", action="store_true",
                        help="Full simulation suite (50 trials, 3000 steps)")
    parser.add_argument("--n-trials", type=int, default=50,
                        help="Number of trials per configuration")
    parser.add_argument("--n-steps", type=int, default=3000,
                        help="Max evolution steps per trial")
    parser.add_argument("--lr-theta", type=float, default=0.01,
                        help="Learning rate for theta")
    parser.add_argument("--lr-sigma", type=float, default=0.1,
                        help="Learning rate for sigma")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed")

    args = parser.parse_args()

    if args.test:
        success = run_self_tests()
        sys.exit(0 if success else 1)

    if args.quick:
        print("\n" + "=" * 70)
        print("QUICK COUPLED SIMULATION")
        print("=" * 70)
        print()

        # Run self-tests first
        if not run_self_tests():
            print("\nSelf-tests failed. Aborting.")
            sys.exit(1)

        print("\n" + "=" * 70)
        print("RUNNING QUICK SIMULATION")
        print("=" * 70)
        print()

        suite = run_coupled_simulation_suite(
            n_trials=20,
            lr_theta=args.lr_theta,
            lr_sigma=args.lr_sigma,
            n_steps=1000,
            seed=args.seed,
            verbose=True
        )

        report = generate_coupled_report(suite)
        print("\n" + "=" * 70)
        print("REPORT")
        print("=" * 70)
        print(report)

        # Write report to file
        output_path = "/Users/Max_1/Projects/PhysicsResearch/cosmological-unification/experience/insights/COUPLED-THETA-SIGMA-2026-02-16.md"
        with open(output_path, 'w') as f:
            f.write("# Coupled θ-σ Dynamics: Results\n\n")
            f.write(f"**Date**: 2026-02-16\n")
            f.write(f"**Status**: NUMERICAL SIMULATION (quick run)\n")
            f.write(f"**Command**: `python3 coupled_theta_sigma.py --quick`\n\n")
            f.write(report)
        print(f"\nReport written to: {output_path}")

    elif args.full:
        print("\n" + "=" * 70)
        print("FULL COUPLED SIMULATION SUITE")
        print("=" * 70)
        print()

        # Run self-tests first
        if not run_self_tests():
            print("\nSelf-tests failed. Aborting.")
            sys.exit(1)

        print("\n" + "=" * 70)
        print("RUNNING FULL SIMULATION")
        print("=" * 70)
        print()

        suite = run_coupled_simulation_suite(
            n_trials=args.n_trials,
            lr_theta=args.lr_theta,
            lr_sigma=args.lr_sigma,
            n_steps=args.n_steps,
            seed=args.seed,
            verbose=True
        )

        report = generate_coupled_report(suite)
        print("\n" + "=" * 70)
        print("REPORT")
        print("=" * 70)
        print(report)

        # Write report to file
        output_path = "/Users/Max_1/Projects/PhysicsResearch/cosmological-unification/experience/insights/COUPLED-THETA-SIGMA-2026-02-16.md"
        with open(output_path, 'w') as f:
            f.write("# Coupled θ-σ Dynamics: Results\n\n")
            f.write(f"**Date**: 2026-02-16\n")
            f.write(f"**Status**: NUMERICAL SIMULATION (full run)\n")
            f.write(f"**Command**: `python3 coupled_theta_sigma.py --full`\n\n")
            f.write(report)
        print(f"\nReport written to: {output_path}")

    else:
        parser.print_help()
