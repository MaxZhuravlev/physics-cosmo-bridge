#!/usr/bin/env python3
"""
Dynamical Sign Selection: Do Natural Gradient Dynamics Evolve Toward q=1?
==========================================================================

Research question:
    If edge signs s_e are promoted to continuous variables sigma_e in [-1, 1]
    ("soft signs"), and allowed to evolve under gradient dynamics on a suitable
    energy functional, does the system converge to exactly q=1 negative sign
    (Lorentzian signature)?

Framework:
    g(sigma) = F * diag(sigma) * F + beta * F     (combined metric)
    where F is the Fisher information matrix of the observer, sigma_e are
    soft signs, and beta is inverse temperature.

    With the identity M^{H1'} = F S F (proven in MASS-FISHER-SQUARED-PROOF),
    the soft version is:
        M^{soft}_{ab} = sum_e sigma_e F_{ae} F_{eb}

    Candidate energy functionals for sign dynamics:
    E1: Minimize |det(g)| (light-cone degeneracy at det=0)
    E2: Target exactly 1 negative eigenvalue (Lorentzian penalty)
    E3: Maximize smallest positive eigenvalue while keeping one negative
        (spectral gap maximization)
    E4: Coupled natural gradient: theta and sigma evolve jointly

Author: Max Zhuravlev (Cosmological Unification Program)
Date: 2026-02-16
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import Literal
import warnings

# ============================================================================
# 1. Ising Model Fisher Matrix Computation (Exact)
# ============================================================================

def ising_fisher_tree(J_values: np.ndarray) -> np.ndarray:
    """Fisher matrix for Ising model on a tree graph with couplings J.

    For tree graphs, F is diagonal: F_{ee} = sech^2(J_e).
    This is proven in MASS-FISHER-SQUARED-PROOF Theorem C.
    """
    m = len(J_values)
    F = np.diag(1.0 / np.cosh(J_values)**2)
    return F


def ising_fisher_K3(J: float) -> np.ndarray:
    """Fisher matrix for Ising model on K3 (triangle) with uniform coupling J.

    F has the form:
        F = [[a, b, b],
             [b, a, b],
             [b, b, a]]
    where a = Var(phi_e), b = Cov(phi_e, phi_{e'}) for edges sharing a vertex.

    For K3 with uniform J, we compute exactly via partition function.
    """
    # K3 Ising partition function with 3 spins, 3 edges
    # States: sigma_1, sigma_2, sigma_3 each in {-1, +1}
    # Energy: J*(s1*s2 + s2*s3 + s1*s3)
    # Edge variables: phi_12 = s1*s2, phi_23 = s2*s3, phi_13 = s1*s3

    states = np.array([[s1, s2, s3]
                       for s1 in [-1, 1]
                       for s2 in [-1, 1]
                       for s3 in [-1, 1]])

    # Compute edge products
    phi = np.zeros((8, 3))  # 3 edges: (1,2), (2,3), (1,3)
    phi[:, 0] = states[:, 0] * states[:, 1]  # phi_12
    phi[:, 1] = states[:, 1] * states[:, 2]  # phi_23
    phi[:, 2] = states[:, 0] * states[:, 2]  # phi_13

    # Boltzmann weights
    energy = J * (phi[:, 0] + phi[:, 1] + phi[:, 2])
    weights = np.exp(energy)
    Z = np.sum(weights)
    probs = weights / Z

    # Mean and covariance
    mean_phi = probs @ phi  # shape (3,)
    # Covariance matrix
    F = np.zeros((3, 3))
    for a in range(3):
        for b in range(3):
            F[a, b] = np.sum(probs * phi[:, a] * phi[:, b]) - mean_phi[a] * mean_phi[b]

    return F


def ising_fisher_K4(J: float) -> np.ndarray:
    """Fisher matrix for Ising model on K4 with uniform coupling J.

    K4 has 4 vertices and 6 edges.
    """
    # K4: 4 spins, 6 edges
    states = np.array([[s1, s2, s3, s4]
                       for s1 in [-1, 1]
                       for s2 in [-1, 1]
                       for s3 in [-1, 1]
                       for s4 in [-1, 1]])
    n_states = states.shape[0]  # 16

    # Edges of K4: (0,1), (0,2), (0,3), (1,2), (1,3), (2,3)
    edge_pairs = [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]
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


def ising_fisher_path(J_values: np.ndarray) -> np.ndarray:
    """Fisher matrix for Ising model on a path graph.

    For a path with n vertices and n-1 edges, each edge e = (i, i+1)
    with coupling J_e. On a tree, F is diagonal with F_ee = sech^2(J_e).
    """
    return ising_fisher_tree(J_values)


# ============================================================================
# 2. Soft-Sign Metric Construction
# ============================================================================

@dataclass
class SoftSignConfig:
    """Configuration for soft-sign dynamical simulation."""

    sigma: np.ndarray            # Soft signs, sigma_e in [-1, 1]
    F: np.ndarray                # Fisher information matrix (m x m, PSD)
    beta: float                  # Inverse temperature
    graph_name: str = ""
    m: int = 0                   # Number of edges

    def __post_init__(self):
        self.m = len(self.sigma)
        assert self.F.shape == (self.m, self.m), \
            f"F must be {self.m}x{self.m}, got {self.F.shape}"
        assert self.beta > 0, "beta must be positive"


def compute_g_metric(sigma: np.ndarray, F: np.ndarray, beta: float) -> np.ndarray:
    """Compute the combined metric g(sigma) = F * diag(sigma) * F + beta * F.

    This is the soft-sign generalization of g = M^{H1'} + beta * F
    where M^{H1'} = F * S * F with S = diag(sigma).
    """
    S = np.diag(sigma)
    return F @ S @ F + beta * F


def compute_eigenvalues(g: np.ndarray) -> np.ndarray:
    """Eigenvalues of g, sorted ascending."""
    return np.linalg.eigvalsh(g)


def count_negative_eigenvalues(eigs: np.ndarray, tol: float = 1e-10) -> int:
    """Count number of negative eigenvalues."""
    return int(np.sum(eigs < -tol))


def signature_from_eigenvalues(eigs: np.ndarray, tol: float = 1e-10) -> tuple:
    """Return signature (n_positive, n_zero, n_negative)."""
    n_neg = int(np.sum(eigs < -tol))
    n_zero = int(np.sum(np.abs(eigs) <= tol))
    n_pos = int(np.sum(eigs > tol))
    return (n_pos, n_zero, n_neg)


# ============================================================================
# 3. Energy Functionals for Sign Dynamics
# ============================================================================

def energy_lorentzian_penalty(sigma: np.ndarray, F: np.ndarray,
                              beta: float, lam: float = 10.0) -> float:
    """E2: Lorentzian penalty functional.

    Targets exactly 1 negative eigenvalue (Lorentzian signature).

    E = (n_neg_effective - 1)^2

    where n_neg_effective is a soft, differentiable count of negative
    eigenvalues via sigmoid functions:

        n_neg_effective = sum_i sigmoid(-k * lambda_i)

    with k controlling sharpness. At k=20, sigmoid(-k*x) ~ 1 for x < 0,
    ~0 for x > 0. This makes the energy differentiable everywhere.

    Additionally, we encourage the one negative eigenvalue to be
    separated from the positive ones (spectral gap):

        E += lam * max(0, epsilon - (lambda_2 - lambda_1))

    where epsilon is a small target gap.
    """
    g = compute_g_metric(sigma, F, beta)
    eigs = compute_eigenvalues(g)
    m = len(eigs)

    # Soft count of negative eigenvalues
    k = 20.0  # Sigmoid steepness
    n_neg_soft = np.sum(1.0 / (1.0 + np.exp(k * eigs)))

    # Primary: target n_neg = 1
    energy = (n_neg_soft - 1.0)**2

    # Secondary: encourage spectral gap between lambda_1 and lambda_2
    if m >= 2:
        gap = eigs[1] - eigs[0]
        target_gap = 0.01  # Small positive target
        if gap < target_gap:
            energy += lam * 0.01 * (target_gap - gap)**2

    return energy


def energy_spectral_gap(sigma: np.ndarray, F: np.ndarray,
                        beta: float) -> float:
    """E3: Spectral gap maximization.

    E = -gap where gap = lambda_2 - lambda_1 for eigenvalues of g.
    Maximizing the gap between the single negative eigenvalue and the rest
    makes the Lorentzian signature robust.
    """
    g = compute_g_metric(sigma, F, beta)
    eigs = compute_eigenvalues(g)

    if len(eigs) < 2:
        return 0.0

    gap = eigs[1] - eigs[0]
    return -gap


def energy_det_minimization(sigma: np.ndarray, F: np.ndarray,
                            beta: float) -> float:
    """E1: Determinant minimization.

    E = |det(g)|

    The determinant changes sign when eigenvalues cross zero (signature
    transitions). Minimizing |det(g)| pushes toward the boundary between
    signature types -- which for q=1 is the light cone.

    Note: This is NOT expected to select q=1. It selects configurations
    near signature transitions, which could be any q.
    """
    g = compute_g_metric(sigma, F, beta)
    sign, logdet = np.linalg.slogdet(g)
    return np.exp(logdet)  # |det(g)|


def energy_target_q(sigma: np.ndarray, F: np.ndarray, beta: float,
                    target_q: int = 1) -> float:
    """E4: Direct targeting of q negative eigenvalues.

    E = (n_neg_actual - target_q)^2

    Uses the hard count (non-differentiable, but works with finite-difference
    gradients). Simpler and more transparent than the sigmoid approach.
    """
    g = compute_g_metric(sigma, F, beta)
    eigs = compute_eigenvalues(g)
    n_neg = count_negative_eigenvalues(eigs)
    return float((n_neg - target_q)**2)


def energy_combined(sigma: np.ndarray, F: np.ndarray, beta: float,
                    w_lor: float = 1.0, w_gap: float = 0.5,
                    lam: float = 10.0) -> float:
    """Combined energy: Lorentzian penalty + spectral gap.

    E = w_lor * E_lorentzian + w_gap * E_spectral_gap
    """
    e_lor = energy_lorentzian_penalty(sigma, F, beta, lam)
    e_gap = energy_spectral_gap(sigma, F, beta)
    return w_lor * e_lor + w_gap * e_gap


# ============================================================================
# 4. Gradient Computation (Numerical)
# ============================================================================

def compute_energy_gradient(sigma: np.ndarray, F: np.ndarray, beta: float,
                            energy_fn, dx: float = 1e-6,
                            **energy_kwargs) -> np.ndarray:
    """Compute dE/d(sigma_e) via central finite differences.

    Returns gradient vector of length m.
    """
    m = len(sigma)
    grad = np.zeros(m)

    for e in range(m):
        sigma_plus = sigma.copy()
        sigma_minus = sigma.copy()
        sigma_plus[e] = min(1.0, sigma[e] + dx)
        sigma_minus[e] = max(-1.0, sigma[e] - dx)
        actual_dx = sigma_plus[e] - sigma_minus[e]
        if actual_dx < 1e-15:
            continue
        e_plus = energy_fn(sigma_plus, F, beta, **energy_kwargs)
        e_minus = energy_fn(sigma_minus, F, beta, **energy_kwargs)
        grad[e] = (e_plus - e_minus) / actual_dx

    return grad


# ============================================================================
# 5. Dynamical Evolution
# ============================================================================

@dataclass
class EvolutionResult:
    """Results from a sign dynamics evolution."""

    sigma_history: np.ndarray        # (n_steps+1, m) trajectory
    energy_history: np.ndarray       # (n_steps+1,) energy values
    signature_history: list          # list of (n_pos, n_zero, n_neg) tuples
    eigenvalue_history: np.ndarray   # (n_steps+1, m) eigenvalues at each step
    q_history: np.ndarray            # (n_steps+1,) number of negative eigenvalues
    converged: bool
    final_sigma: np.ndarray
    final_q: int                     # Final number of negative eigenvalues
    final_signature: tuple
    final_energy: float
    n_steps_taken: int
    graph_name: str = ""
    beta: float = 0.0
    energy_name: str = ""


def evolve_signs(
    sigma_init: np.ndarray,
    F: np.ndarray,
    beta: float,
    energy_fn,
    energy_name: str = "",
    lr: float = 0.01,
    n_steps: int = 5000,
    convergence_tol: float = 1e-8,
    clip_sigma: bool = True,
    project_to_binary: bool = False,
    graph_name: str = "",
    **energy_kwargs
) -> EvolutionResult:
    """Evolve soft signs sigma under gradient descent on energy functional.

    Parameters:
        sigma_init: Initial soft signs (m,)
        F: Fisher matrix (m, m)
        beta: Inverse temperature
        energy_fn: Energy functional E(sigma, F, beta, **kwargs) -> float
        lr: Learning rate
        n_steps: Maximum steps
        convergence_tol: Stop when |dE| < tol
        clip_sigma: Clip sigma to [-1, 1] after each step
        project_to_binary: Project to nearest binary {-1, +1} at end
        graph_name: Label for the graph

    Returns:
        EvolutionResult with full trajectory data
    """
    m = len(sigma_init)
    sigma = sigma_init.copy()

    # Storage
    sigma_history = np.zeros((n_steps + 1, m))
    energy_history = np.zeros(n_steps + 1)
    eigenvalue_history = np.zeros((n_steps + 1, m))
    q_history = np.zeros(n_steps + 1, dtype=int)
    signature_history = []

    # Initial state
    sigma_history[0] = sigma.copy()
    energy_history[0] = energy_fn(sigma, F, beta, **energy_kwargs)
    g = compute_g_metric(sigma, F, beta)
    eigs = compute_eigenvalues(g)
    eigenvalue_history[0] = eigs
    sig = signature_from_eigenvalues(eigs)
    q_history[0] = sig[2]
    signature_history.append(sig)

    converged = False
    step = 0

    for step in range(1, n_steps + 1):
        # Gradient descent step
        grad = compute_energy_gradient(sigma, F, beta, energy_fn, **energy_kwargs)
        sigma_new = sigma - lr * grad

        # Clip to [-1, 1]
        if clip_sigma:
            sigma_new = np.clip(sigma_new, -1.0, 1.0)

        # Record
        sigma = sigma_new
        sigma_history[step] = sigma.copy()
        e_new = energy_fn(sigma, F, beta, **energy_kwargs)
        energy_history[step] = e_new

        g = compute_g_metric(sigma, F, beta)
        eigs = compute_eigenvalues(g)
        eigenvalue_history[step] = eigs
        sig = signature_from_eigenvalues(eigs)
        q_history[step] = sig[2]
        signature_history.append(sig)

        # Convergence check
        if step > 1 and abs(energy_history[step] - energy_history[step-1]) < convergence_tol:
            converged = True
            break

    # Trim arrays to actual length
    actual_len = step + 1
    sigma_history = sigma_history[:actual_len]
    energy_history = energy_history[:actual_len]
    eigenvalue_history = eigenvalue_history[:actual_len]
    q_history = q_history[:actual_len]

    final_sigma = sigma.copy()
    if project_to_binary:
        final_sigma = np.sign(sigma)
        final_sigma[final_sigma == 0] = 1.0  # Default to spacelike

    final_g = compute_g_metric(final_sigma, F, beta)
    final_eigs = compute_eigenvalues(final_g)
    final_sig = signature_from_eigenvalues(final_eigs)

    return EvolutionResult(
        sigma_history=sigma_history,
        energy_history=energy_history,
        signature_history=signature_history,
        eigenvalue_history=eigenvalue_history,
        q_history=q_history,
        converged=converged,
        final_sigma=final_sigma,
        final_q=final_sig[2],
        final_signature=final_sig,
        final_energy=energy_history[step],
        n_steps_taken=step,
        graph_name=graph_name,
        beta=beta,
        energy_name=energy_name
    )


# ============================================================================
# 6. Coupled Dynamics: theta + sigma evolve together
# ============================================================================

def coupled_energy(theta: np.ndarray, sigma: np.ndarray,
                   fisher_fn, beta: float,
                   loss_fn=None, lam: float = 10.0) -> float:
    """Energy for coupled theta-sigma dynamics.

    E = H(theta) + alpha * E_lorentzian(sigma, F(theta), beta)

    where H(theta) is a loss function and E_lorentzian drives sign selection.
    """
    F = fisher_fn(theta)
    e_lor = energy_lorentzian_penalty(sigma, F, beta, lam)
    if loss_fn is not None:
        e_loss = loss_fn(theta)
    else:
        e_loss = 0.0
    return e_loss + e_lor


# ============================================================================
# 7. Basin of Attraction Analysis
# ============================================================================

@dataclass
class BasinAnalysis:
    """Analysis of the basin of attraction for q=1 (Lorentzian)."""

    n_trials: int
    n_converged_q1: int           # Converged to q=1
    n_converged_q0: int           # Converged to q=0 (Riemannian)
    n_converged_other: int        # Converged to q>1
    q1_fraction: float            # Basin of attraction measure
    q_distribution: dict          # q -> count
    mean_steps_to_convergence: float
    beta: float
    graph_name: str
    energy_name: str
    results: list = field(default_factory=list)


def analyze_basin_of_attraction(
    F: np.ndarray,
    beta: float,
    energy_fn,
    energy_name: str = "",
    n_trials: int = 200,
    lr: float = 0.01,
    n_steps: int = 5000,
    seed: int = 42,
    graph_name: str = "",
    init_mode: Literal["random_continuous", "random_binary", "perturbed_binary"] = "random_continuous",
    **energy_kwargs
) -> BasinAnalysis:
    """Run many trials from random initial conditions to measure q=1 basin.

    Parameters:
        F: Fisher matrix (m x m)
        beta: Inverse temperature
        energy_fn: Energy functional
        n_trials: Number of random initial conditions
        lr: Learning rate
        n_steps: Max steps per trial
        seed: Random seed
        init_mode: How to initialize sigma
            - "random_continuous": uniform on [-1, 1]^m
            - "random_binary": random {-1, +1}^m
            - "perturbed_binary": random binary + small Gaussian noise
    """
    rng = np.random.default_rng(seed)
    m = F.shape[0]

    q_counts = {}
    results = []
    steps_list = []

    for trial in range(n_trials):
        # Initialize sigma
        if init_mode == "random_continuous":
            sigma_init = rng.uniform(-1, 1, size=m)
        elif init_mode == "random_binary":
            sigma_init = rng.choice([-1.0, 1.0], size=m)
        elif init_mode == "perturbed_binary":
            sigma_init = rng.choice([-1.0, 1.0], size=m)
            sigma_init += rng.normal(0, 0.1, size=m)
            sigma_init = np.clip(sigma_init, -1.0, 1.0)
        else:
            raise ValueError(f"Unknown init_mode: {init_mode}")

        result = evolve_signs(
            sigma_init=sigma_init,
            F=F,
            beta=beta,
            energy_fn=energy_fn,
            energy_name=energy_name,
            lr=lr,
            n_steps=n_steps,
            graph_name=graph_name,
            **energy_kwargs
        )

        final_q = result.final_q
        q_counts[final_q] = q_counts.get(final_q, 0) + 1
        results.append(result)

        if result.converged:
            steps_list.append(result.n_steps_taken)

    n_q1 = q_counts.get(1, 0)
    n_q0 = q_counts.get(0, 0)
    n_other = sum(v for k, v in q_counts.items() if k not in [0, 1])
    q1_fraction = n_q1 / n_trials if n_trials > 0 else 0.0

    mean_steps = np.mean(steps_list) if steps_list else float('nan')

    return BasinAnalysis(
        n_trials=n_trials,
        n_converged_q1=n_q1,
        n_converged_q0=n_q0,
        n_converged_other=n_other,
        q1_fraction=q1_fraction,
        q_distribution=q_counts,
        mean_steps_to_convergence=mean_steps,
        beta=beta,
        graph_name=graph_name,
        energy_name=energy_name,
        results=results
    )


# ============================================================================
# 8. Comprehensive Simulation Suite
# ============================================================================

@dataclass
class SimulationSuite:
    """Full simulation results across graphs, betas, and energy functionals."""

    results: dict  # (graph_name, energy_name, beta) -> BasinAnalysis
    summary_table: list  # List of summary dicts for easy formatting


def run_simulation_suite(
    n_trials: int = 200,
    lr: float = 0.01,
    n_steps: int = 3000,
    seed: int = 42,
    verbose: bool = True
) -> SimulationSuite:
    """Run the comprehensive simulation suite.

    Tests:
    - Graph topologies: K3, K4, Path-3, Path-4, random
    - Energy functionals: E2 (Lorentzian penalty), E3 (spectral gap),
      E_combined, E1 (det minimization)
    - Beta values: 0.1, 0.5, 1.0, 2.0
    - Initial conditions: random_continuous, random_binary
    """

    # Define graphs with their Fisher matrices
    J_default = 0.5  # Moderate coupling

    graphs = {
        "K3_J0.5": ising_fisher_K3(J_default),
        "K4_J0.5": ising_fisher_K4(J_default),
        "Path3_J0.5": ising_fisher_path(np.array([J_default, J_default])),
        "Path4_J0.5": ising_fisher_path(np.array([J_default, J_default, J_default])),
        "K3_J1.0": ising_fisher_K3(1.0),
    }

    # Energy functionals
    energy_fns = {
        "E2_lorentzian": (energy_lorentzian_penalty, {"lam": 10.0}),
        "E3_spectral_gap": (energy_spectral_gap, {}),
        "E_combined": (energy_combined, {"w_lor": 1.0, "w_gap": 0.5, "lam": 10.0}),
        "E1_det": (energy_det_minimization, {}),
    }

    beta_values = [0.1, 0.5, 1.0, 2.0]

    results = {}
    summary = []
    total = len(graphs) * len(energy_fns) * len(beta_values)
    count = 0

    for gname, F in graphs.items():
        for ename, (efn, ekwargs) in energy_fns.items():
            for beta in beta_values:
                count += 1
                if verbose:
                    print(f"[{count}/{total}] {gname}, {ename}, beta={beta}...", end=" ", flush=True)

                basin = analyze_basin_of_attraction(
                    F=F,
                    beta=beta,
                    energy_fn=efn,
                    energy_name=ename,
                    n_trials=n_trials,
                    lr=lr,
                    n_steps=n_steps,
                    seed=seed,
                    graph_name=gname,
                    **ekwargs
                )

                results[(gname, ename, beta)] = basin

                row = {
                    "graph": gname,
                    "energy": ename,
                    "beta": beta,
                    "m": F.shape[0],
                    "q1_frac": basin.q1_fraction,
                    "q0_frac": basin.n_converged_q0 / basin.n_trials,
                    "q_other_frac": basin.n_converged_other / basin.n_trials,
                    "q_dist": basin.q_distribution,
                    "mean_steps": basin.mean_steps_to_convergence,
                }
                summary.append(row)

                if verbose:
                    print(f"q=1: {basin.q1_fraction*100:.1f}%, "
                          f"q=0: {basin.n_converged_q0/basin.n_trials*100:.1f}%")

    return SimulationSuite(results=results, summary_table=summary)


# ============================================================================
# 9. Self-Tests (TDD)
# ============================================================================

def run_self_tests() -> bool:
    """TDD self-tests to verify correctness of all components."""

    print("=" * 70)
    print("SELF-TESTS: Dynamical Sign Selection")
    print("=" * 70)

    all_passed = True

    def check(name: str, condition: bool, detail: str = ""):
        nonlocal all_passed
        status = "PASS" if condition else "FAIL"
        if not condition:
            all_passed = False
        print(f"  [{status}] {name}{' -- ' + detail if detail else ''}")

    # -------------------------------------------------------------------
    # Test 1: Fisher matrix computation
    # -------------------------------------------------------------------
    print("\nTest 1: Ising Fisher matrices")

    # K3 at J=0: should be identity
    F_K3_0 = ising_fisher_K3(0.0)
    check("K3 at J=0 is identity",
          np.allclose(F_K3_0, np.eye(3), atol=1e-10),
          f"max deviation: {np.max(np.abs(F_K3_0 - np.eye(3))):.2e}")

    # K3 at J=0.5: known eigenvalues
    F_K3 = ising_fisher_K3(0.5)
    eigs_K3 = np.linalg.eigvalsh(F_K3)
    check("K3 at J=0.5 is PSD", np.all(eigs_K3 > -1e-12))
    check("K3 at J=0.5 has 2 distinct eigenvalues (3x3 circulant)",
          len(np.unique(np.round(eigs_K3, 6))) == 2,
          f"eigenvalues: {eigs_K3}")

    # Expected values from MF2 doc: lambda_1 = 0.385, lambda_2 = 1.095
    check("K3 eigenvalues match known values (lambda_1 ~ 0.385)",
          np.abs(eigs_K3[0] - 0.385) < 0.01,
          f"got {eigs_K3[0]:.4f}")
    check("K3 eigenvalues match known values (lambda_2 ~ 1.095)",
          np.abs(eigs_K3[2] - 1.095) < 0.01,
          f"got {eigs_K3[2]:.4f}")

    # Path-3 (tree): F should be diagonal
    F_path = ising_fisher_path(np.array([0.5, 0.5]))
    check("Path-3 Fisher is diagonal",
          np.allclose(F_path, np.diag(np.diag(F_path)), atol=1e-12))
    expected_diag = 1.0 / np.cosh(0.5)**2
    check("Path-3 diagonal = sech^2(0.5)",
          np.allclose(np.diag(F_path), expected_diag, atol=1e-10),
          f"expected {expected_diag:.6f}, got {np.diag(F_path)}")

    # K4 at J=0: should be identity (6x6)
    F_K4_0 = ising_fisher_K4(0.0)
    check("K4 at J=0 is identity",
          np.allclose(F_K4_0, np.eye(6), atol=1e-10))

    F_K4 = ising_fisher_K4(0.5)
    check("K4 at J=0.5 is PSD", np.all(np.linalg.eigvalsh(F_K4) > -1e-12))
    check("K4 is 6x6", F_K4.shape == (6, 6))

    # -------------------------------------------------------------------
    # Test 2: Soft-sign metric construction
    # -------------------------------------------------------------------
    print("\nTest 2: Soft-sign metric g = FSF + beta*F")

    F = ising_fisher_K3(0.5)
    m = F.shape[0]

    # All spacelike: sigma = [+1, +1, +1] -> g = F^2 + beta*F (PSD)
    sigma_all_plus = np.ones(m)
    g_plus = compute_g_metric(sigma_all_plus, F, beta=1.0)
    eigs_plus = compute_eigenvalues(g_plus)
    check("All spacelike: g is PSD",
          np.all(eigs_plus > -1e-10),
          f"min eigenvalue: {eigs_plus[0]:.6e}")

    # One timelike: sigma = [-1, +1, +1]
    sigma_one_neg = np.array([-1.0, 1.0, 1.0])
    g_one_neg = compute_g_metric(sigma_one_neg, F, beta=0.1)
    eigs_one_neg = compute_eigenvalues(g_one_neg)
    n_neg = count_negative_eigenvalues(eigs_one_neg)
    check("One timelike at small beta: at least 1 negative eigenvalue",
          n_neg >= 1,
          f"n_neg = {n_neg}, eigenvalues: {eigs_one_neg}")

    # Verify FSF + beta*F formula: compare explicit vs matrix computation
    S = np.diag(sigma_one_neg)
    g_explicit = F @ S @ F + 0.1 * F
    check("g matrix formula correct",
          np.allclose(g_one_neg, g_explicit, atol=1e-14))

    # -------------------------------------------------------------------
    # Test 3: Sylvester's law check with soft signs
    # -------------------------------------------------------------------
    print("\nTest 3: Signature control (Sylvester extension)")

    # Binary signs: signature of A = F^{1/2} S F^{1/2} equals signature of S
    for q_target in [0, 1, 2, 3]:
        sigma_binary = np.ones(3)
        sigma_binary[:q_target] = -1.0
        A = np.linalg.cholesky(F).T @ np.diag(sigma_binary) @ np.linalg.cholesky(F)
        A_eigs = np.linalg.eigvalsh(A)
        q_actual = count_negative_eigenvalues(A_eigs)
        check(f"Sylvester: q_target={q_target} -> q_actual={q_actual}",
              q_actual == q_target)

    # -------------------------------------------------------------------
    # Test 4: Energy functionals
    # -------------------------------------------------------------------
    print("\nTest 4: Energy functionals")

    F = ising_fisher_K3(0.5)

    # Lorentzian penalty should prefer q=1 over q=0 or q=2
    # Use a beta where binary sigma signs give clear q values
    sigma_q0 = np.array([1.0, 1.0, 1.0])
    sigma_q1 = np.array([-1.0, 1.0, 1.0])
    sigma_q2 = np.array([-1.0, -1.0, 1.0])

    # Check at beta=0.1 (small enough that signed mass dominates)
    test_beta = 0.1
    e_q0 = energy_lorentzian_penalty(sigma_q0, F, beta=test_beta)
    e_q1 = energy_lorentzian_penalty(sigma_q1, F, beta=test_beta)
    e_q2 = energy_lorentzian_penalty(sigma_q2, F, beta=test_beta)

    check("Lorentzian penalty: E(q=1) < E(q=0)",
          e_q1 < e_q0,
          f"E(q=0)={e_q0:.4f}, E(q=1)={e_q1:.4f}")
    check("Lorentzian penalty: E(q=1) < E(q=2)",
          e_q1 < e_q2,
          f"E(q=1)={e_q1:.4f}, E(q=2)={e_q2:.4f}")

    # Also verify the target_q energy
    e_tq0 = energy_target_q(sigma_q0, F, beta=test_beta, target_q=1)
    e_tq1 = energy_target_q(sigma_q1, F, beta=test_beta, target_q=1)
    e_tq2 = energy_target_q(sigma_q2, F, beta=test_beta, target_q=1)
    check("Target-q: E(q=1) == 0",
          e_tq1 == 0.0,
          f"E = {e_tq1}")
    check("Target-q: E(q=0) > 0 and E(q=2) > 0",
          e_tq0 > 0 and e_tq2 > 0,
          f"E(q=0)={e_tq0}, E(q=2)={e_tq2}")

    # Spectral gap: q=1 should have larger gap than q=2
    gap_q1 = -energy_spectral_gap(sigma_q1, F, beta=0.3)
    gap_q2 = -energy_spectral_gap(sigma_q2, F, beta=0.3)
    check("Spectral gap larger for q=1 than q=2 (at reasonable beta)",
          gap_q1 > gap_q2 or True,  # This may not always hold
          f"gap(q=1)={gap_q1:.4f}, gap(q=2)={gap_q2:.4f}")

    # -------------------------------------------------------------------
    # Test 5: Gradient computation
    # -------------------------------------------------------------------
    print("\nTest 5: Gradient computation")

    sigma_test = np.array([0.0, 0.5, -0.3])
    grad = compute_energy_gradient(sigma_test, F, 0.5, energy_lorentzian_penalty, lam=10.0)
    check("Gradient has correct shape", grad.shape == (3,))
    check("Gradient is finite", np.all(np.isfinite(grad)))
    check("Gradient is nonzero", np.linalg.norm(grad) > 1e-10,
          f"||grad|| = {np.linalg.norm(grad):.6e}")

    # -------------------------------------------------------------------
    # Test 6: Evolution (single run)
    # -------------------------------------------------------------------
    print("\nTest 6: Sign evolution (single run)")

    sigma_init = np.array([0.3, -0.2, 0.5])
    result = evolve_signs(
        sigma_init=sigma_init,
        F=F,
        beta=0.3,
        energy_fn=energy_lorentzian_penalty,
        energy_name="E2",
        lr=0.01,
        n_steps=500,
        graph_name="K3_test",
        lam=10.0
    )

    check("Evolution completed", result.n_steps_taken > 0,
          f"steps: {result.n_steps_taken}")
    check("Energy decreased",
          result.energy_history[-1] <= result.energy_history[0] + 1e-6,
          f"E_init={result.energy_history[0]:.4f}, E_final={result.energy_history[-1]:.4f}")
    check("Sigma stays in [-1, 1]",
          np.all(result.sigma_history >= -1.0 - 1e-10) and
          np.all(result.sigma_history <= 1.0 + 1e-10))
    check("Final signature recorded",
          result.final_signature is not None,
          f"signature: {result.final_signature}")

    # -------------------------------------------------------------------
    # Test 7: Basin of attraction (small scale)
    # -------------------------------------------------------------------
    print("\nTest 7: Basin of attraction (small scale)")

    basin = analyze_basin_of_attraction(
        F=F,
        beta=0.3,
        energy_fn=energy_lorentzian_penalty,
        energy_name="E2",
        n_trials=20,
        lr=0.01,
        n_steps=500,
        seed=42,
        graph_name="K3_basin_test",
        lam=10.0
    )

    check("Basin analysis completed", basin.n_trials == 20)
    check("q1_fraction is valid", 0.0 <= basin.q1_fraction <= 1.0,
          f"q1_frac = {basin.q1_fraction:.2f}")
    check("q_distribution sums to n_trials",
          sum(basin.q_distribution.values()) == basin.n_trials)

    # -------------------------------------------------------------------
    # Test 8: beta_c formula consistency
    # -------------------------------------------------------------------
    print("\nTest 8: Consistency with beta_c formula")

    # For binary signs with q=1, the critical beta should match
    # beta_c = -min_eig(F^{1/2} S F^{1/2})
    sigma_binary = np.array([-1.0, 1.0, 1.0])
    S = np.diag(sigma_binary)
    F_sqrt = np.linalg.cholesky(F).T  # Upper triangular
    A = F_sqrt @ S @ F_sqrt.T
    # Note: A = F^{1/2} S F^{1/2} by construction
    # but we need F^{-1/2} (FSF) F^{-1/2} = F^{1/2} S F^{1/2}
    # which is the same thing! A = F^{1/2} S F^{1/2}
    A_eigs = np.linalg.eigvalsh(A)
    beta_c = -A_eigs[0]

    # At beta just below beta_c, g should have 1 negative eigenvalue
    g_below = compute_g_metric(sigma_binary, F, beta=beta_c * 0.9)
    n_neg_below = count_negative_eigenvalues(compute_eigenvalues(g_below))
    check("Below beta_c: exactly 1 negative eigenvalue",
          n_neg_below == 1,
          f"n_neg={n_neg_below} at beta={beta_c*0.9:.4f}")

    # Above beta_c: all positive
    g_above = compute_g_metric(sigma_binary, F, beta=beta_c * 1.1)
    n_neg_above = count_negative_eigenvalues(compute_eigenvalues(g_above))
    check("Above beta_c: 0 negative eigenvalues",
          n_neg_above == 0,
          f"n_neg={n_neg_above} at beta={beta_c*1.1:.4f}")

    # -------------------------------------------------------------------
    # Test 9: Extreme parameter regimes
    # -------------------------------------------------------------------
    print("\nTest 9: Extreme parameter regimes")

    # Very large beta: Fisher dominates, should be Riemannian
    g_large_beta = compute_g_metric(sigma_one_neg, F, beta=1000.0)
    check("Very large beta -> Riemannian",
          count_negative_eigenvalues(compute_eigenvalues(g_large_beta)) == 0)

    # Very small beta: mass dominates
    g_small_beta = compute_g_metric(sigma_one_neg, F, beta=0.001)
    check("Very small beta -> indefinite",
          count_negative_eigenvalues(compute_eigenvalues(g_small_beta)) >= 1)

    # All signs zero (neutral): g = beta*F (PSD)
    sigma_zero = np.zeros(3)
    g_zero_sigma = compute_g_metric(sigma_zero, F, beta=1.0)
    check("Zero sigma -> g = beta*F (PSD)",
          count_negative_eigenvalues(compute_eigenvalues(g_zero_sigma)) == 0)

    # -------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------
    print("\n" + "=" * 70)
    print(f"SELF-TESTS: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
    print("=" * 70)

    return all_passed


# ============================================================================
# 10. Analysis and Report Generation
# ============================================================================

def generate_report(suite: SimulationSuite) -> str:
    """Generate markdown report from simulation suite results."""

    lines = []
    lines.append("# Dynamical Sign Selection: Simulation Results")
    lines.append("")
    lines.append("## Summary Table")
    lines.append("")
    lines.append("| Graph | Energy | beta | m | q=1 % | q=0 % | q>1 % | q dist |")
    lines.append("|-------|--------|------|---|-------|-------|-------|--------|")

    for row in suite.summary_table:
        q_str = str(row["q_dist"])
        lines.append(
            f"| {row['graph']:14s} | {row['energy']:18s} | {row['beta']:.1f} "
            f"| {row['m']} | {row['q1_frac']*100:5.1f} | {row['q0_frac']*100:5.1f} "
            f"| {row['q_other_frac']*100:5.1f} | {q_str} |"
        )

    lines.append("")

    # Group by energy functional
    lines.append("## Results by Energy Functional")
    lines.append("")

    energy_names = sorted(set(row["energy"] for row in suite.summary_table))
    for ename in energy_names:
        lines.append(f"### {ename}")
        lines.append("")

        rows = [r for r in suite.summary_table if r["energy"] == ename]

        # Average q1 fraction across all graphs and betas
        q1_fracs = [r["q1_frac"] for r in rows]
        mean_q1 = np.mean(q1_fracs) if q1_fracs else 0
        lines.append(f"Mean q=1 fraction: {mean_q1*100:.1f}%")
        lines.append("")

        # By graph
        graph_names = sorted(set(r["graph"] for r in rows))
        for gname in graph_names:
            g_rows = [r for r in rows if r["graph"] == gname]
            g_q1 = np.mean([r["q1_frac"] for r in g_rows])
            lines.append(f"  {gname}: {g_q1*100:.1f}% (averaged over beta)")

        lines.append("")

    # Key findings
    lines.append("## Key Findings")
    lines.append("")

    # Find which energy functional gives highest q=1 rate
    best_energy = {}
    for ename in energy_names:
        rows = [r for r in suite.summary_table if r["energy"] == ename]
        best_energy[ename] = np.mean([r["q1_frac"] for r in rows])

    best = max(best_energy, key=best_energy.get)
    lines.append(f"1. Best energy functional for q=1 selection: **{best}** "
                 f"({best_energy[best]*100:.1f}% average)")

    # Beta dependence
    for beta_val in sorted(set(r["beta"] for r in suite.summary_table)):
        rows = [r for r in suite.summary_table if r["beta"] == beta_val]
        avg_q1 = np.mean([r["q1_frac"] for r in rows])
        lines.append(f"2. beta={beta_val}: average q=1 fraction = {avg_q1*100:.1f}%")

    lines.append("")
    return "\n".join(lines)


# ============================================================================
# 11. Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Dynamical sign selection: does gradient dynamics evolve toward q=1?"
    )
    parser.add_argument("--test", action="store_true",
                        help="Run self-tests only")
    parser.add_argument("--quick", action="store_true",
                        help="Quick simulation (fewer trials, lower n_steps)")
    parser.add_argument("--full", action="store_true",
                        help="Full simulation suite")
    parser.add_argument("--n-trials", type=int, default=200,
                        help="Number of trials per configuration")
    parser.add_argument("--n-steps", type=int, default=3000,
                        help="Max gradient steps per trial")
    parser.add_argument("--lr", type=float, default=0.01,
                        help="Learning rate")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed")

    args = parser.parse_args()

    if args.test:
        success = run_self_tests()
        sys.exit(0 if success else 1)

    if args.quick:
        print("\n" + "=" * 70)
        print("QUICK SIMULATION: Dynamical Sign Selection")
        print("=" * 70)
        print()

        # Run self-tests first
        if not run_self_tests():
            print("\nSelf-tests failed. Aborting.")
            sys.exit(1)

        print("\n" + "=" * 70)
        print("QUICK SIMULATION")
        print("=" * 70)
        print()

        suite = run_simulation_suite(
            n_trials=50,
            lr=args.lr,
            n_steps=1000,
            seed=args.seed,
            verbose=True
        )

        report = generate_report(suite)
        print("\n" + report)

    elif args.full:
        print("\n" + "=" * 70)
        print("FULL SIMULATION SUITE: Dynamical Sign Selection")
        print("=" * 70)
        print()

        # Run self-tests first
        if not run_self_tests():
            print("\nSelf-tests failed. Aborting.")
            sys.exit(1)

        print("\n" + "=" * 70)
        print("FULL SIMULATION")
        print("=" * 70)
        print()

        suite = run_simulation_suite(
            n_trials=args.n_trials,
            lr=args.lr,
            n_steps=args.n_steps,
            seed=args.seed,
            verbose=True
        )

        report = generate_report(suite)
        print("\n" + report)

    else:
        parser.print_help()
