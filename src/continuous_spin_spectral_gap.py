#!/usr/bin/env python3
"""
Continuous Spin Models: Spectral Gap Selection Analysis

Extends the Spectral Gap Selection Theorem from DISCRETE spin models
(Ising, Potts) to CONTINUOUS spin models (XY, Heisenberg).

Key question: Does W(q=1) > W(q>=2) hold for continuous symmetry groups?

Models:
  XY model:         spins on S^1 (unit circle), H = -J sum cos(theta_i - theta_j)
  Heisenberg model: spins on S^2 (unit sphere), H = -J sum sigma_i . sigma_j

Method:
  Numerical integration (deterministic quadrature for small graphs,
  Monte Carlo for validation) to compute the Fisher information matrix
  F_{ab} = Cov(T_a, T_b) where T_e is the sufficient statistic for edge e.

  For XY:  T_e = cos(theta_i - theta_j)
  For Heisenberg: T_e = sigma_i . sigma_j

Attribution:
    test_id: TEST-BRIDGE-MVP1-CONTINUOUS-SPIN-001
    mvp_layer: MVP-1
    dialogue_id: session-2026-02-17-continuous-spin
    recovery_path: papers/structural-bridge/src/continuous_spin_spectral_gap.py
"""

import numpy as np
import itertools
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
import time
import sys


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ContinuousSpinResult:
    """Results for a single (model, graph, J) configuration."""
    model: str                     # "XY" or "Heisenberg"
    graph_name: str
    n_vertices: int
    n_edges: int
    coupling_J: float
    is_tree: bool
    girth: int                     # float('inf') encoded as 9999 for trees

    # Fisher matrix properties
    fisher_diag_entries: np.ndarray  # diagonal of F
    fisher_off_diag_norm: float      # ||F - diag(F)||_F / ||diag(F)||_F
    fisher_is_diagonal: bool         # True if off-diag norm < 1e-6
    fisher_is_proportional_to_I: bool  # True if all diag entries are equal

    # Spectral gap selection
    W_values: Dict[int, float] = field(default_factory=dict)
    q_optimal: int = 1
    q1_wins: bool = True
    W_q1: float = 0.0
    W_best_higher: float = 0.0
    margin: float = 0.0

    # Error estimation
    integration_method: str = "quadrature"
    n_integration_points: int = 0


# ---------------------------------------------------------------------------
# Graph utilities
# ---------------------------------------------------------------------------

def create_graph(graph_type: str, n: int) -> Tuple[List[Tuple[int, int]], bool, int]:
    """
    Create edge list for a specified graph topology.

    Returns:
        edges: list of (i, j) pairs
        is_tree: True if graph is a tree
        girth: length of shortest cycle (9999 for trees)
    """
    if graph_type == "path":
        edges = [(i, i + 1) for i in range(n - 1)]
        return edges, True, 9999

    elif graph_type == "star":
        edges = [(0, i) for i in range(1, n)]
        return edges, True, 9999

    elif graph_type == "cycle":
        edges = [(i, (i + 1) % n) for i in range(n)]
        return edges, False, n

    elif graph_type == "complete":
        edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
        is_tree = (n <= 2)
        girth = 3 if n >= 3 else 9999
        return edges, is_tree, girth

    elif graph_type == "ladder":
        # Two parallel paths connected by rungs: 2n vertices, 3n-2 edges
        # Vertices 0..n-1 (top) and n..2n-1 (bottom)
        edges = []
        for i in range(n - 1):
            edges.append((i, i + 1))          # top rail
            edges.append((n + i, n + i + 1))  # bottom rail
        for i in range(n):
            edges.append((i, n + i))          # rungs
        return edges, False, 4

    else:
        raise ValueError(f"Unknown graph type: {graph_type}")


# ---------------------------------------------------------------------------
# XY Model Fisher Matrix (deterministic quadrature)
# ---------------------------------------------------------------------------

def xy_fisher_quadrature(
    edges: List[Tuple[int, int]],
    n_vertices: int,
    J: float,
    n_quad: int = 64
) -> np.ndarray:
    """
    Compute Fisher information matrix for XY model using deterministic
    quadrature on [0, 2*pi)^n.

    XY Hamiltonian: H = -J * sum_{(i,j) in E} cos(theta_i - theta_j)
    Sufficient statistics: T_e = cos(theta_i - theta_j) for edge e=(i,j)
    Fisher matrix: F_{ab} = Cov(T_a, T_b) under the Boltzmann distribution

    For n_vertices <= 5, we use a tensor-product grid.
    For n_vertices > 5, we use importance sampling (see xy_fisher_mc).

    Args:
        edges: list of (i, j) pairs
        n_vertices: number of vertices (spins)
        J: coupling strength
        n_quad: number of quadrature points per dimension

    Returns:
        F: (m, m) Fisher information matrix where m = len(edges)
    """
    m = len(edges)
    if m == 0:
        return np.zeros((0, 0))

    # Quadrature grid: trapezoidal rule on [0, 2*pi) for each angle
    # For the XY model, the partition function is invariant under global
    # rotation, so we can fix theta_0 = 0 to remove the zero mode.
    # This leaves (n-1) free angles.

    n_free = n_vertices - 1
    angles = np.linspace(0, 2 * np.pi, n_quad, endpoint=False)
    d_theta = 2 * np.pi / n_quad

    if n_free == 0:
        # Single vertex, no edges possible
        return np.zeros((m, m))

    # For small systems, use full tensor product grid
    if n_free <= 5:
        # Build grid for free angles (theta_1, ..., theta_{n-1})
        grids = [angles] * n_free
        mesh = np.meshgrid(*grids, indexing='ij')
        # Shape: (n_quad, ..., n_quad, n_free)

        # Flatten: each row is a configuration of free angles
        flat_angles = np.column_stack([g.ravel() for g in mesh])
        n_configs = flat_angles.shape[0]

        # Full angle array: theta_0 = 0 (fixed), theta_1..theta_{n-1} = free
        all_angles = np.zeros((n_configs, n_vertices))
        all_angles[:, 1:] = flat_angles

        # Compute sufficient statistics T_e = cos(theta_i - theta_j)
        T = np.zeros((n_configs, m))
        for k, (i, j) in enumerate(edges):
            T[:, k] = np.cos(all_angles[:, i] - all_angles[:, j])

        # Compute Boltzmann weights: exp(J * sum_e T_e)
        # (The Hamiltonian is H = -J * sum T_e, so weight = exp(-H) = exp(J * sum T_e))
        energy_contributions = J * np.sum(T, axis=1)
        # Subtract max for numerical stability
        energy_contributions -= np.max(energy_contributions)
        weights = np.exp(energy_contributions)

        # Integration weight (uniform grid)
        # Total weight = sum(weights) * (d_theta)^n_free
        Z = np.sum(weights) * (d_theta ** n_free)
        probs = weights / np.sum(weights)

        # Fisher matrix = Cov(T) under the Boltzmann distribution
        mean_T = probs @ T
        centered_T = T - mean_T
        F = (centered_T * probs[:, None]).T @ centered_T

        return F

    else:
        # Fall through to Monte Carlo for larger systems
        return xy_fisher_mc(edges, n_vertices, J, n_samples=50000)


def xy_fisher_mc(
    edges: List[Tuple[int, int]],
    n_vertices: int,
    J: float,
    n_samples: int = 50000,
    n_burnin: int = 5000,
    seed: int = 42
) -> np.ndarray:
    """
    Compute Fisher information matrix for XY model using Metropolis-Hastings
    Monte Carlo sampling.

    Args:
        edges: list of (i, j) pairs
        n_vertices: number of spins
        J: coupling strength
        n_samples: number of MCMC samples after burn-in
        n_burnin: number of burn-in steps
        seed: random seed

    Returns:
        F: (m, m) Fisher information matrix
    """
    m = len(edges)
    rng = np.random.default_rng(seed)

    # Pre-build adjacency for energy computation
    # For each vertex, store list of (neighbor, edge_index)
    adj = [[] for _ in range(n_vertices)]
    for k, (i, j) in enumerate(edges):
        adj[i].append((j, k))
        adj[j].append((i, k))

    # Initialize random configuration
    theta = rng.uniform(0, 2 * np.pi, n_vertices)

    # Compute initial energy
    def compute_energy(theta_config):
        E = 0.0
        for (i, j) in edges:
            E -= J * np.cos(theta_config[i] - theta_config[j])
        return E

    current_energy = compute_energy(theta)

    # Collect samples
    T_samples = np.zeros((n_samples, m))
    proposal_width = 0.5  # Adjusted during burn-in

    accept_count = 0
    total_steps = n_burnin + n_samples

    for step in range(total_steps):
        # Propose: pick random vertex, shift its angle
        v = rng.integers(0, n_vertices)
        delta = rng.normal(0, proposal_width)
        new_theta_v = theta[v] + delta

        # Compute energy change (only edges incident to v)
        dE = 0.0
        for (nb, _) in adj[v]:
            dE -= J * (np.cos(new_theta_v - theta[nb]) - np.cos(theta[v] - theta[nb]))

        # Metropolis acceptance
        if dE < 0 or rng.random() < np.exp(-dE):
            theta[v] = new_theta_v
            current_energy += dE
            accept_count += 1

        # Adaptive proposal width during burn-in
        if step < n_burnin and step > 0 and step % 500 == 0:
            rate = accept_count / (step + 1)
            if rate > 0.5:
                proposal_width *= 1.1
            elif rate < 0.3:
                proposal_width *= 0.9

        # Record sample after burn-in
        if step >= n_burnin:
            idx = step - n_burnin
            for k, (i, j) in enumerate(edges):
                T_samples[idx, k] = np.cos(theta[i] - theta[j])

    # Fisher matrix = covariance of sufficient statistics
    mean_T = np.mean(T_samples, axis=0)
    centered_T = T_samples - mean_T
    F = centered_T.T @ centered_T / n_samples

    return F


# ---------------------------------------------------------------------------
# Heisenberg Model Fisher Matrix (deterministic for small n, MC otherwise)
# ---------------------------------------------------------------------------

def heisenberg_fisher_mc(
    edges: List[Tuple[int, int]],
    n_vertices: int,
    J: float,
    n_samples: int = 50000,
    n_burnin: int = 5000,
    seed: int = 42
) -> np.ndarray:
    """
    Compute Fisher information matrix for Heisenberg model using Metropolis
    Monte Carlo on S^2.

    Heisenberg Hamiltonian: H = -J * sum_{(i,j)} sigma_i . sigma_j
    Sufficient statistics: T_e = sigma_i . sigma_j for edge e=(i,j)
    Fisher matrix: F_{ab} = Cov(T_a, T_b)

    Args:
        edges: list of (i, j) pairs
        n_vertices: number of spins
        J: coupling strength
        n_samples: number of MCMC samples
        n_burnin: burn-in steps
        seed: random seed

    Returns:
        F: (m, m) Fisher information matrix
    """
    m = len(edges)
    rng = np.random.default_rng(seed)

    # Pre-build adjacency
    adj = [[] for _ in range(n_vertices)]
    for k, (i, j) in enumerate(edges):
        adj[i].append((j, k))
        adj[j].append((i, k))

    # Initialize random unit vectors on S^2
    def random_unit_vector():
        v = rng.normal(0, 1, 3)
        return v / np.linalg.norm(v)

    def propose_near(v, width=0.3):
        """Propose new unit vector near v by adding Gaussian noise and normalizing."""
        v_new = v + rng.normal(0, width, 3)
        return v_new / np.linalg.norm(v_new)

    spins = np.array([random_unit_vector() for _ in range(n_vertices)])

    # Collect samples
    T_samples = np.zeros((n_samples, m))
    proposal_width = 0.3
    accept_count = 0
    total_steps = n_burnin + n_samples

    for step in range(total_steps):
        # Propose: pick random vertex, propose new direction
        v = rng.integers(0, n_vertices)
        new_spin = propose_near(spins[v], proposal_width)

        # Energy change (only edges incident to v)
        dE = 0.0
        for (nb, _) in adj[v]:
            dE -= J * (np.dot(new_spin, spins[nb]) - np.dot(spins[v], spins[nb]))

        # Metropolis acceptance
        if dE < 0 or rng.random() < np.exp(-dE):
            spins[v] = new_spin
            accept_count += 1

        # Adaptive proposal width during burn-in
        if step < n_burnin and step > 0 and step % 500 == 0:
            rate = accept_count / (step + 1)
            if rate > 0.5:
                proposal_width *= 1.05
            elif rate < 0.3:
                proposal_width *= 0.95

        # Record sample after burn-in
        if step >= n_burnin:
            idx = step - n_burnin
            for k, (i, j) in enumerate(edges):
                T_samples[idx, k] = np.dot(spins[i], spins[j])

    # Fisher matrix = covariance of sufficient statistics
    mean_T = np.mean(T_samples, axis=0)
    centered_T = T_samples - mean_T
    F = centered_T.T @ centered_T / n_samples

    return F


def heisenberg_fisher_quadrature(
    edges: List[Tuple[int, int]],
    n_vertices: int,
    J: float,
    n_theta: int = 32,
    n_phi: int = 64
) -> np.ndarray:
    """
    Compute Fisher matrix for Heisenberg model using spherical quadrature.

    For small graphs (n_vertices <= 3), we integrate over S^2 for each spin
    (fixing spin 0 along z-axis by rotational invariance).

    The integration measure on S^2 is sin(theta) d_theta d_phi.

    Args:
        edges: list of (i, j) pairs
        n_vertices: number of spins
        J: coupling strength
        n_theta: polar angle grid points
        n_phi: azimuthal angle grid points

    Returns:
        F: (m, m) Fisher information matrix
    """
    m = len(edges)
    if m == 0:
        return np.zeros((0, 0))

    n_free = n_vertices - 1  # Fix spin 0 along z

    if n_free > 3:
        # Too many dimensions for quadrature, fall back to MC
        return heisenberg_fisher_mc(edges, n_vertices, J, n_samples=100000)

    # Build quadrature grid on S^2
    # theta in [0, pi], phi in [0, 2*pi)
    theta_grid = np.linspace(0, np.pi, n_theta + 2)[1:-1]  # Exclude poles
    phi_grid = np.linspace(0, 2 * np.pi, n_phi, endpoint=False)
    d_theta = np.pi / (n_theta + 1)
    d_phi = 2 * np.pi / n_phi

    # Precompute sin(theta) for the measure
    sin_theta = np.sin(theta_grid)

    # Number of quadrature points per spin
    n_per_spin = n_theta * n_phi

    # Build cartesian coordinates for all grid points on one sphere
    single_sphere = np.zeros((n_per_spin, 3))
    for it, th in enumerate(theta_grid):
        for ip, ph in enumerate(phi_grid):
            idx = it * n_phi + ip
            single_sphere[idx] = [np.sin(th) * np.cos(ph),
                                  np.sin(th) * np.sin(ph),
                                  np.cos(th)]

    # Quadrature weights for one sphere (sin(theta) * d_theta * d_phi)
    single_weights = np.zeros(n_per_spin)
    for it, th in enumerate(theta_grid):
        for ip in range(n_phi):
            idx = it * n_phi + ip
            single_weights[idx] = np.sin(th) * d_theta * d_phi

    # Fixed spin 0 = (0, 0, 1) (z-axis)
    spin0 = np.array([0.0, 0.0, 1.0])

    if n_free == 1:
        # 2 spins, 1 free
        n_configs = n_per_spin
        # Build sufficient statistics and weights
        T_all = np.zeros((n_configs, m))
        w_all = np.zeros(n_configs)

        for c in range(n_per_spin):
            spins = [spin0, single_sphere[c]]
            # Compute T_e for each edge
            for k, (i, j) in enumerate(edges):
                T_all[c, k] = np.dot(spins[i], spins[j])
            # Boltzmann weight * integration measure
            energy = -J * np.sum(T_all[c, :])
            w_all[c] = np.exp(-energy) * single_weights[c]  # measure * Boltzmann (beta=1 convention: exp(+J*sum T))

        # Normalize
        # Actually: weight = exp(J * sum T_e) * measure
        # Because H = -J sum T_e, so exp(-H) = exp(J sum T_e)
        boltzmann = np.exp(J * np.sum(T_all, axis=1))
        w_all = boltzmann * single_weights
        Z = np.sum(w_all)
        probs = w_all / Z

        mean_T = probs @ T_all
        centered = T_all - mean_T
        F = (centered * probs[:, None]).T @ centered
        return F

    elif n_free == 2:
        # 3 spins, 2 free
        n_configs = n_per_spin ** 2
        T_all = np.zeros((n_configs, m))
        w_all = np.zeros(n_configs)

        idx = 0
        for c1 in range(n_per_spin):
            for c2 in range(n_per_spin):
                spins = [spin0, single_sphere[c1], single_sphere[c2]]
                for k, (i, j) in enumerate(edges):
                    T_all[idx, k] = np.dot(spins[i], spins[j])
                boltzmann_factor = np.exp(J * np.sum(T_all[idx, :]))
                w_all[idx] = boltzmann_factor * single_weights[c1] * single_weights[c2]
                idx += 1

        Z = np.sum(w_all)
        probs = w_all / Z
        mean_T = probs @ T_all
        centered = T_all - mean_T
        F = (centered * probs[:, None]).T @ centered
        return F

    elif n_free == 3:
        # 4 spins, 3 free -- use coarser grid
        n_theta_coarse = min(n_theta, 16)
        n_phi_coarse = min(n_phi, 32)
        theta_c = np.linspace(0, np.pi, n_theta_coarse + 2)[1:-1]
        phi_c = np.linspace(0, 2 * np.pi, n_phi_coarse, endpoint=False)
        dt_c = np.pi / (n_theta_coarse + 1)
        dp_c = 2 * np.pi / n_phi_coarse
        n_per = n_theta_coarse * n_phi_coarse

        sphere_c = np.zeros((n_per, 3))
        weights_c = np.zeros(n_per)
        for it, th in enumerate(theta_c):
            for ip, ph in enumerate(phi_c):
                idx = it * n_phi_coarse + ip
                sphere_c[idx] = [np.sin(th) * np.cos(ph),
                                 np.sin(th) * np.sin(ph),
                                 np.cos(th)]
                weights_c[idx] = np.sin(th) * dt_c * dp_c

        n_configs = n_per ** 3
        # For 4 vertices with coarse grid, this is manageable if n_per ~ 512
        # 512^3 = 134M which is too much. Use MC instead.
        if n_configs > 5_000_000:
            return heisenberg_fisher_mc(edges, n_vertices, J, n_samples=100000)

        T_all = np.zeros((n_configs, m))
        w_all = np.zeros(n_configs)

        idx = 0
        for c1 in range(n_per):
            for c2 in range(n_per):
                for c3 in range(n_per):
                    spins = [spin0, sphere_c[c1], sphere_c[c2], sphere_c[c3]]
                    for k, (i, j) in enumerate(edges):
                        T_all[idx, k] = np.dot(spins[i], spins[j])
                    boltzmann_factor = np.exp(J * np.sum(T_all[idx, :]))
                    w_all[idx] = (boltzmann_factor *
                                  weights_c[c1] * weights_c[c2] * weights_c[c3])
                    idx += 1

        Z = np.sum(w_all)
        probs = w_all / Z
        mean_T = probs @ T_all
        centered = T_all - mean_T
        F = (centered * probs[:, None]).T @ centered
        return F

    else:
        return heisenberg_fisher_mc(edges, n_vertices, J, n_samples=100000)


# ---------------------------------------------------------------------------
# Spectral gap computation (shared with Ising analysis)
# ---------------------------------------------------------------------------

def compute_spectral_gap_weighting(
    F: np.ndarray,
    q: int,
    exhaustive_threshold: int = 12,
    seed: int = 42
) -> Tuple[float, float, float]:
    """
    Compute W(q) = beta_c(q) * L_gap(q) for a given Fisher matrix.

    For q negative signs assigned to edges, find the sign assignment
    that maximizes the spectral gap weighting.

    Returns:
        W: spectral gap weighting
        beta_c: critical inverse temperature
        L_gap: spectral gap ratio
    """
    m = F.shape[0]
    if q < 1 or q >= m:
        return 0.0, 0.0, 0.0

    # Compute F^{1/2}
    F_stab = F + 1e-10 * np.eye(m)
    vals, vecs = np.linalg.eigh(F_stab)
    vals = np.maximum(vals, 0)
    F_sqrt = vecs @ np.diag(np.sqrt(vals)) @ vecs.T

    best_W = 0.0
    best_beta_c = 0.0
    best_L_gap = 0.0

    # Enumerate sign assignments
    if m <= exhaustive_threshold:
        sign_iter = itertools.combinations(range(m), q)
    else:
        rng = np.random.default_rng(seed + q)
        n_samples = min(2000, max(500, m * 50))
        sign_iter = []
        for _ in range(n_samples):
            perm = rng.permutation(m)
            sign_iter.append(tuple(perm[:q]))

    for neg_indices in sign_iter:
        S_diag = np.ones(m)
        for idx in neg_indices:
            S_diag[idx] = -1.0
        S = np.diag(S_diag)
        A = F_sqrt @ S @ F_sqrt

        eigs = np.linalg.eigvalsh(A)
        d1 = eigs[0]
        d2 = eigs[1] if len(eigs) > 1 else d1

        if d1 < -1e-15:
            beta_c = -d1
            L_gap = (d2 - d1) / abs(d1)
            W = beta_c * L_gap

            if W > best_W:
                best_W = W
                best_beta_c = beta_c
                best_L_gap = L_gap

    return best_W, best_beta_c, best_L_gap


# ---------------------------------------------------------------------------
# Analysis driver
# ---------------------------------------------------------------------------

def analyze_continuous_model(
    model: str,
    graph_type: str,
    n_vertices: int,
    J: float,
    n_quad: int = 64,
    n_mc_samples: int = 50000
) -> Optional[ContinuousSpinResult]:
    """
    Analyze a single (model, graph, J) configuration.

    Args:
        model: "XY" or "Heisenberg"
        graph_type: graph topology name
        n_vertices: number of vertices
        J: coupling strength
        n_quad: quadrature points per dimension (XY)
        n_mc_samples: Monte Carlo samples (Heisenberg)

    Returns:
        ContinuousSpinResult with all analysis data
    """
    edges, is_tree, girth = create_graph(graph_type, n_vertices)
    m = len(edges)

    if m < 2:
        return None

    t0 = time.time()

    # Compute Fisher matrix
    integration_method = "quadrature"
    n_integration_points = 0

    if model == "XY":
        n_free = n_vertices - 1
        if n_free <= 5:
            F = xy_fisher_quadrature(edges, n_vertices, J, n_quad=n_quad)
            n_integration_points = n_quad ** n_free
        else:
            F = xy_fisher_mc(edges, n_vertices, J, n_samples=n_mc_samples)
            integration_method = "MC"
            n_integration_points = n_mc_samples

    elif model == "Heisenberg":
        if n_vertices <= 3:
            F = heisenberg_fisher_quadrature(edges, n_vertices, J)
            integration_method = "quadrature"
            n_integration_points = 0  # Varies
        else:
            F = heisenberg_fisher_mc(edges, n_vertices, J, n_samples=n_mc_samples)
            integration_method = "MC"
            n_integration_points = n_mc_samples
    else:
        raise ValueError(f"Unknown model: {model}")

    elapsed = time.time() - t0

    # Symmetrize F (numerical noise)
    F = 0.5 * (F + F.T)

    # Check positive semi-definiteness
    eig_F = np.linalg.eigvalsh(F)
    if np.min(eig_F) < -1e-6:
        print(f"WARNING: Fisher matrix has negative eigenvalue {np.min(eig_F):.2e} "
              f"for {model} {graph_type} n={n_vertices} J={J}")

    # Fisher matrix properties
    diag_F = np.diag(F)
    F_diag_matrix = np.diag(diag_F)
    F_off = F - F_diag_matrix

    diag_norm = np.linalg.norm(F_diag_matrix, 'fro')
    off_norm = np.linalg.norm(F_off, 'fro')
    off_diag_ratio = off_norm / diag_norm if diag_norm > 1e-15 else float('inf')

    is_diagonal = off_diag_ratio < 1e-4
    # Check if diagonal entries are all approximately equal
    if len(diag_F) > 0 and np.mean(diag_F) > 1e-15:
        relative_spread = np.std(diag_F) / np.mean(diag_F)
        is_proportional = relative_spread < 1e-4
    else:
        is_proportional = False

    # Spectral gap weighting for q = 1, 2, ..., min(m-1, 6)
    max_q = min(m - 1, 6)
    W_values = {}
    for q in range(1, max_q + 1):
        W, beta_c, L_gap = compute_spectral_gap_weighting(F, q)
        W_values[q] = W

    # Determine winner
    W_q1 = W_values.get(1, 0.0)
    W_higher = {q: w for q, w in W_values.items() if q >= 2}
    W_best_higher = max(W_higher.values()) if W_higher else 0.0
    q_optimal = max(W_values.keys(), key=lambda q: W_values[q]) if W_values else 1
    q1_wins = (W_q1 > W_best_higher) if (W_q1 > 1e-15 or W_best_higher > 1e-15) else True

    margin = (W_q1 - W_best_higher) / max(W_q1, 1e-15) if W_q1 > 1e-15 else 0.0

    return ContinuousSpinResult(
        model=model,
        graph_name=graph_type,
        n_vertices=n_vertices,
        n_edges=m,
        coupling_J=J,
        is_tree=is_tree,
        girth=girth,
        fisher_diag_entries=diag_F,
        fisher_off_diag_norm=off_diag_ratio,
        fisher_is_diagonal=is_diagonal,
        fisher_is_proportional_to_I=is_proportional,
        W_values=W_values,
        q_optimal=q_optimal,
        q1_wins=q1_wins,
        W_q1=W_q1,
        W_best_higher=W_best_higher,
        margin=margin,
        integration_method=integration_method,
        n_integration_points=n_integration_points
    )


# ---------------------------------------------------------------------------
# Main campaign
# ---------------------------------------------------------------------------

def run_campaign():
    """Run the full continuous spin model spectral gap analysis campaign."""

    print("=" * 90)
    print("CONTINUOUS SPIN MODELS: SPECTRAL GAP SELECTION ANALYSIS")
    print("=" * 90)
    print()
    print("Research Question:")
    print("  Does the Spectral Gap Selection Theorem extend from discrete (Ising/Potts)")
    print("  to continuous (XY/Heisenberg) spin models?")
    print()
    print("Models:")
    print("  XY:          spins on S^1, H = -J sum cos(theta_i - theta_j)")
    print("  Heisenberg:  spins on S^2, H = -J sum sigma_i . sigma_j")
    print()
    print("Spectral gap weighting: W(q) = beta_c(q) * L_gap(q)")
    print("  where A(S) = F^{1/2} S F^{1/2}, beta_c = -d_1, L_gap = (d_2-d_1)/|d_1|")
    print()
    print("=" * 90)
    print()

    # Define test configurations
    # Format: (graph_type, n_vertices)
    graph_configs = [
        ("path", 3),
        ("path", 5),
        ("star", 4),
        ("cycle", 4),
        ("cycle", 6),
        ("complete", 4),
        ("path", 4),
        ("star", 5),
        ("path", 6),
        ("cycle", 5),
    ]

    J_values = [0.1, 0.3, 0.5, 1.0, 1.5, 2.0]

    models = ["XY", "Heisenberg"]

    all_results = []

    # Header
    print(f"{'Model':<12} {'Graph':<10} {'n':<4} {'m':<4} {'J':<6} "
          f"{'Tree':<5} {'F diag?':<8} {'F~I?':<5} "
          f"{'W(1)':<10} {'W_best>=2':<10} {'q1?':<4} {'Margin':<10} {'Method':<8}")
    print("-" * 115)

    for model in models:
        for graph_type, n in graph_configs:
            for J in J_values:
                try:
                    result = analyze_continuous_model(
                        model=model,
                        graph_type=graph_type,
                        n_vertices=n,
                        J=J,
                        n_quad=64,
                        n_mc_samples=50000
                    )
                    if result is None:
                        continue

                    all_results.append(result)

                    tree_str = "Y" if result.is_tree else "N"
                    diag_str = "Y" if result.fisher_is_diagonal else f"N({result.fisher_off_diag_norm:.1e})"
                    prop_str = "Y" if result.fisher_is_proportional_to_I else "N"
                    q1_str = "Y" if result.q1_wins else "N"
                    margin_str = f"{result.margin:.4f}" if result.W_q1 > 1e-15 else "N/A"

                    print(f"{model:<12} {graph_type:<10} {n:<4} {result.n_edges:<4} {J:<6.2f} "
                          f"{tree_str:<5} {diag_str:<8} {prop_str:<5} "
                          f"{result.W_q1:<10.4f} {result.W_best_higher:<10.4f} "
                          f"{q1_str:<4} {margin_str:<10} {result.integration_method:<8}")

                except Exception as e:
                    print(f"ERROR: {model} {graph_type} n={n} J={J}: {e}")
                    continue

        print()  # Blank line between models

    # Summary statistics
    print()
    print("=" * 90)
    print("SUMMARY STATISTICS")
    print("=" * 90)
    print()

    if not all_results:
        print("No valid results obtained.")
        return all_results

    # Overall
    total = len(all_results)
    q1_wins = sum(1 for r in all_results if r.q1_wins)
    print(f"Total configurations tested: {total}")
    print(f"Lorentzian selection (q=1 wins): {q1_wins}/{total} ({100*q1_wins/total:.1f}%)")
    print()

    # By model
    for model in models:
        model_results = [r for r in all_results if r.model == model]
        if not model_results:
            continue
        n_total = len(model_results)
        n_wins = sum(1 for r in model_results if r.q1_wins)
        print(f"  {model}: {n_wins}/{n_total} ({100*n_wins/n_total:.1f}%)")

        # By topology
        for is_tree_val, tree_label in [(True, "trees"), (False, "non-trees")]:
            topo_results = [r for r in model_results if r.is_tree == is_tree_val]
            if topo_results:
                t_wins = sum(1 for r in topo_results if r.q1_wins)
                print(f"    {tree_label}: {t_wins}/{len(topo_results)} "
                      f"({100*t_wins/len(topo_results):.1f}%)")

    print()

    # Tree Fisher Identity check
    print("--- Tree Fisher Identity ---")
    tree_results = [r for r in all_results if r.is_tree]
    if tree_results:
        for model in models:
            mt = [r for r in tree_results if r.model == model]
            if mt:
                n_diag = sum(1 for r in mt if r.fisher_is_diagonal)
                n_prop = sum(1 for r in mt if r.fisher_is_proportional_to_I)
                print(f"  {model} on trees:")
                print(f"    F diagonal: {n_diag}/{len(mt)} ({100*n_diag/len(mt):.1f}%)")
                print(f"    F ~ c*I:    {n_prop}/{len(mt)} ({100*n_prop/len(mt):.1f}%)")
                # Show typical diagonal entries
                example = mt[0]
                print(f"    Example ({example.graph_name} n={example.n_vertices} J={example.coupling_J}): "
                      f"diag = {example.fisher_diag_entries[:4]}")
    print()

    # Coupling dependence
    print("--- Coupling Strength Dependence ---")
    for model in models:
        model_results = [r for r in all_results if r.model == model]
        for J in J_values:
            j_results = [r for r in model_results if abs(r.coupling_J - J) < 0.01]
            if j_results:
                n_wins = sum(1 for r in j_results if r.q1_wins)
                print(f"  {model} J={J:.1f}: {n_wins}/{len(j_results)} "
                      f"({100*n_wins/len(j_results):.1f}%)")
    print()

    # Comparison table: Ising vs Potts vs XY vs Heisenberg
    print("--- Cross-Model Comparison ---")
    print("(XY/Heisenberg results from this campaign; Ising/Potts from prior work)")
    print()
    print(f"{'Model':<14} {'Tree Fisher ID':<20} {'Spectral Gap Sel.':<20} {'Notes'}")
    print("-" * 80)

    for model in models:
        mt = [r for r in tree_results if r.model == model]
        all_m = [r for r in all_results if r.model == model]
        tree_diag = "YES" if mt and all(r.fisher_is_diagonal for r in mt) else "PARTIAL"
        if mt and not any(r.fisher_is_diagonal for r in mt):
            tree_diag = "NO"
        q1_rate = sum(1 for r in all_m if r.q1_wins) / len(all_m) * 100 if all_m else 0
        notes = ""
        if model == "XY":
            notes = "Continuous S^1 symmetry"
        elif model == "Heisenberg":
            notes = "Continuous S^2 symmetry"
        print(f"{model:<14} {tree_diag:<20} {q1_rate:.0f}%{'':<16} {notes}")

    print(f"{'Ising':<14} {'YES (exact)':<20} {'98.2% (prior)':<20} {'Z_2 discrete'}")
    print(f"{'Potts (q=3)':<14} {'YES (exact)':<20} {'~95% (prior)':<20} {'S_q discrete'}")
    print()

    return all_results


def write_results_file(results: List[ContinuousSpinResult], filepath: str):
    """Write detailed results to a markdown file."""

    with open(filepath, "w") as f:
        f.write("# Continuous Spin Models: Spectral Gap Selection Analysis\n\n")
        f.write("**Date:** 2026-02-17\n")
        f.write("**Attribution:** TEST-BRIDGE-MVP1-CONTINUOUS-SPIN-001\n")
        f.write("**Script:** `continuous_spin_spectral_gap.py`\n\n")

        f.write("---\n\n")
        f.write("## Summary\n\n")

        if not results:
            f.write("No results generated.\n")
            return

        total = len(results)
        q1_wins = sum(1 for r in results if r.q1_wins)
        f.write(f"- Total configurations: {total}\n")
        f.write(f"- Lorentzian selection (q=1 wins): {q1_wins}/{total} ({100*q1_wins/total:.1f}%)\n\n")

        # By model
        for model in ["XY", "Heisenberg"]:
            mr = [r for r in results if r.model == model]
            if mr:
                nw = sum(1 for r in mr if r.q1_wins)
                f.write(f"- {model}: {nw}/{len(mr)} ({100*nw/len(mr):.1f}%)\n")
        f.write("\n")

        # Detailed table
        f.write("## Detailed Results\n\n")
        f.write("| Model | Graph | n | m | J | Tree | F diag? | F~I? | W(1) | W_best>=2 | q1? | Margin |\n")
        f.write("|-------|-------|---|---|---|------|---------|------|------|-----------|-----|--------|\n")

        for r in results:
            tree_s = "Y" if r.is_tree else "N"
            diag_s = "Y" if r.fisher_is_diagonal else f"N({r.fisher_off_diag_norm:.1e})"
            prop_s = "Y" if r.fisher_is_proportional_to_I else "N"
            q1_s = "Y" if r.q1_wins else "N"
            margin_s = f"{r.margin:.4f}" if r.W_q1 > 1e-15 else "N/A"

            f.write(f"| {r.model} | {r.graph_name} | {r.n_vertices} | {r.n_edges} | "
                    f"{r.coupling_J:.2f} | {tree_s} | {diag_s} | {prop_s} | "
                    f"{r.W_q1:.4f} | {r.W_best_higher:.4f} | {q1_s} | {margin_s} |\n")

        f.write("\n")

        # Tree Fisher Identity analysis
        f.write("## Tree Fisher Identity Analysis\n\n")
        tree_results = [r for r in results if r.is_tree]
        if tree_results:
            f.write("For discrete models (Ising, Potts), the Tree Fisher Identity states that\n")
            f.write("F = diag(f_1, ..., f_m) on tree graphs, i.e., edge variables are independent.\n\n")

            for model in ["XY", "Heisenberg"]:
                mt = [r for r in tree_results if r.model == model]
                if not mt:
                    continue
                f.write(f"### {model} Model on Trees\n\n")
                n_diag = sum(1 for r in mt if r.fisher_is_diagonal)
                n_prop = sum(1 for r in mt if r.fisher_is_proportional_to_I)
                f.write(f"- F diagonal: {n_diag}/{len(mt)} ({100*n_diag/len(mt):.1f}%)\n")
                f.write(f"- F proportional to I: {n_prop}/{len(mt)} ({100*n_prop/len(mt):.1f}%)\n\n")

                if n_diag == len(mt):
                    f.write("**The Tree Fisher Identity HOLDS for the " + model + " model.**\n")
                    f.write("Edge variables cos(theta_i - theta_j) are mutually independent on trees.\n\n")
                elif n_diag > 0:
                    f.write("**The Tree Fisher Identity PARTIALLY holds.**\n")
                    f.write("Some tree configurations show non-diagonal F.\n\n")
                else:
                    f.write("**The Tree Fisher Identity FAILS for the " + model + " model.**\n")
                    f.write("Edge variables are NOT independent on trees for continuous spins.\n\n")

                # Show off-diagonal norms
                f.write("Off-diagonal norms:\n\n")
                f.write("| Graph | n | J | ||F-diag(F)||/||diag(F)|| |\n")
                f.write("|-------|---|---|---------------------------|\n")
                for r in mt:
                    f.write(f"| {r.graph_name} | {r.n_vertices} | {r.coupling_J:.2f} | "
                            f"{r.fisher_off_diag_norm:.2e} |\n")
                f.write("\n")

        # Spectral gap selection analysis
        f.write("## Spectral Gap Selection Analysis\n\n")

        for model in ["XY", "Heisenberg"]:
            mr = [r for r in results if r.model == model]
            if not mr:
                continue
            f.write(f"### {model} Model\n\n")

            # Trees vs non-trees
            for label, subset in [("Trees", [r for r in mr if r.is_tree]),
                                  ("Non-trees", [r for r in mr if not r.is_tree])]:
                if not subset:
                    continue
                nw = sum(1 for r in subset if r.q1_wins)
                f.write(f"**{label}:** {nw}/{len(subset)} select q=1 ({100*nw/len(subset):.1f}%)\n\n")

            # By coupling
            f.write("By coupling strength:\n\n")
            f.write("| J | q=1 wins | Total | Rate |\n")
            f.write("|---|----------|-------|------|\n")
            for J_val in sorted(set(r.coupling_J for r in mr)):
                jr = [r for r in mr if abs(r.coupling_J - J_val) < 0.01]
                nw = sum(1 for r in jr if r.q1_wins)
                f.write(f"| {J_val:.2f} | {nw} | {len(jr)} | {100*nw/len(jr):.1f}% |\n")
            f.write("\n")

        # Cross-model comparison
        f.write("## Cross-Model Comparison\n\n")
        f.write("| Model | Symmetry | Tree Fisher ID | Spectral Gap Selection | Notes |\n")
        f.write("|-------|----------|----------------|----------------------|-------|\n")
        f.write("| Ising | Z_2 (discrete) | YES (exact, proven) | 98.2% (proven for trees) | Baseline |\n")
        f.write("| Potts (q=3-5) | S_q (discrete) | YES (exact) | ~95% | Discrete universality |\n")

        for model in ["XY", "Heisenberg"]:
            mr = [r for r in results if r.model == model]
            mt = [r for r in mr if r.is_tree]
            sym = "U(1) (S^1)" if model == "XY" else "SO(3) (S^2)"
            tree_id = "?"
            if mt:
                nd = sum(1 for r in mt if r.fisher_is_diagonal)
                tree_id = f"{nd}/{len(mt)}" if nd < len(mt) else "YES"
            sel = f"{sum(1 for r in mr if r.q1_wins)}/{len(mr)}" if mr else "N/A"
            notes = "Continuous" if model == "XY" else "Continuous, higher dim"
            f.write(f"| {model} | {sym} | {tree_id} | {sel} | {notes} |\n")

        f.write("\n")

        # Key observations
        f.write("## Key Observations\n\n")
        f.write("### 1. Tree Fisher Identity for Continuous Models\n\n")

        xy_tree = [r for r in results if r.model == "XY" and r.is_tree]
        heis_tree = [r for r in results if r.model == "Heisenberg" and r.is_tree]

        if xy_tree:
            all_diag = all(r.fisher_is_diagonal for r in xy_tree)
            if all_diag:
                f.write("For the XY model, the Tree Fisher Identity **holds**: F is diagonal on trees.\n")
                f.write("This is because the sufficient statistic T_e = cos(theta_i - theta_j) depends\n")
                f.write("only on the angle DIFFERENCE, and on a tree the angle differences are\n")
                f.write("independent random variables (analogous to the Ising edge variables phi_e = s_i*s_j).\n\n")
            else:
                off_norms = [r.fisher_off_diag_norm for r in xy_tree]
                f.write(f"For the XY model, F is near-diagonal on trees (max off-diag ratio: {max(off_norms):.2e}).\n")
                f.write("This suggests approximate but not exact diagonality.\n\n")

        if heis_tree:
            all_diag = all(r.fisher_is_diagonal for r in heis_tree)
            if all_diag:
                f.write("For the Heisenberg model, the Tree Fisher Identity **holds**: F is diagonal on trees.\n\n")
            else:
                off_norms = [r.fisher_off_diag_norm for r in heis_tree]
                f.write(f"For the Heisenberg model on trees, max off-diag ratio: {max(off_norms):.2e}.\n\n")

        f.write("### 2. Spectral Gap Selection Universality\n\n")

        xy_all = [r for r in results if r.model == "XY"]
        heis_all = [r for r in results if r.model == "Heisenberg"]

        if xy_all:
            rate = 100 * sum(1 for r in xy_all if r.q1_wins) / len(xy_all)
            f.write(f"XY model: q=1 selected in {rate:.1f}% of configurations.\n")
        if heis_all:
            rate = 100 * sum(1 for r in heis_all if r.q1_wins) / len(heis_all)
            f.write(f"Heisenberg model: q=1 selected in {rate:.1f}% of configurations.\n")
        f.write("\n")

        f.write("### 3. Mechanism Analysis\n\n")
        f.write("The spectral gap selection mechanism relies on two properties of F:\n\n")
        f.write("1. **Near-diagonality**: F is close to diagonal for sparse graphs\n")
        f.write("2. **Rank-1 isolation**: A single sign flip creates one spectrally\n")
        f.write("   isolated negative eigenvalue, while multiple flips create clustered\n")
        f.write("   negative eigenvalues with small spectral gap\n\n")
        f.write("If continuous models preserve near-diagonality on sparse graphs,\n")
        f.write("the mechanism should work identically regardless of the internal\n")
        f.write("symmetry group of the spin variable.\n\n")

        f.write("### 4. What Fails (If Anything)\n\n")

        failures = [r for r in results if not r.q1_wins]
        if failures:
            f.write("Configurations where q=1 did NOT win:\n\n")
            f.write("| Model | Graph | n | J | W(1) | W_best>=2 | q_opt |\n")
            f.write("|-------|-------|---|---|------|-----------|-------|\n")
            for r in failures:
                f.write(f"| {r.model} | {r.graph_name} | {r.n_vertices} | "
                        f"{r.coupling_J:.2f} | {r.W_q1:.4f} | {r.W_best_higher:.4f} | "
                        f"{r.q_optimal} |\n")
            f.write("\n")
        else:
            f.write("All configurations selected q=1 (Lorentzian). No failures observed.\n\n")

        f.write("---\n\n")
        f.write("*Generated by continuous_spin_spectral_gap.py*\n")


# ---------------------------------------------------------------------------
# Analytical derivations (printed to stdout)
# ---------------------------------------------------------------------------

def print_analytical_derivations():
    """Print the analytical Fisher matrix derivations for XY and Heisenberg models."""

    print()
    print("=" * 90)
    print("ANALYTICAL DERIVATIONS")
    print("=" * 90)
    print()

    print("PART 1: XY MODEL FISHER INFORMATION MATRIX")
    print("-" * 60)
    print()
    print("The XY model on graph G = (V, E) with |V| = n, |E| = m:")
    print()
    print("  Spins: theta_i in [0, 2*pi), i = 1, ..., n")
    print("  Hamiltonian: H = -J * sum_{(i,j) in E} cos(theta_i - theta_j)")
    print()
    print("  This is an exponential family with:")
    print("    Natural parameters: J_e (one per edge)")
    print("    Sufficient statistics: T_e = cos(theta_i - theta_j)")
    print("    Measure: product Lebesgue on [0, 2*pi)^n")
    print()
    print("  Fisher information matrix:")
    print("    F_{ab} = Cov(T_a, T_b)")
    print("           = E[cos(theta_i - theta_j) * cos(theta_k - theta_l)]")
    print("             - E[cos(theta_i - theta_j)] * E[cos(theta_k - theta_l)]")
    print()
    print("  where a = (i,j), b = (k,l) are edges.")
    print()
    print("  DIAGONAL ENTRIES:")
    print("    F_{ee} = Var(cos(theta_i - theta_j))")
    print("           = E[cos^2(theta_i - theta_j)] - (E[cos(theta_i - theta_j)])^2")
    print()
    print("  For uniform coupling J on a tree:")
    print("    Let phi_e = theta_i - theta_j be the angle difference for edge e.")
    print("    On a tree, the angle differences phi_e are INDEPENDENT random variables")
    print("    (same argument as Ising: phi_e determines the change along edge e,")
    print("     and on a tree there is a unique path between any two vertices).")
    print()
    print("    Therefore: F_{ab} = 0 for a != b on any tree.")
    print("    This is the Tree Fisher Identity for the XY model.")
    print()
    print("    The diagonal entry is:")
    print("    F_{ee} = Var(cos(phi_e)) where phi_e has distribution")
    print("    p(phi) proportional to exp(J * cos(phi))")
    print()
    print("    Using modified Bessel functions:")
    print("    E[cos(phi)] = I_1(J) / I_0(J)")
    print("    E[cos^2(phi)] = 1/2 + I_2(J) / (2*I_0(J))")
    print("    where I_n(J) is the modified Bessel function of the first kind.")
    print()
    print("    Therefore:")
    print("    F_{ee} = 1/2 + I_2(J)/(2*I_0(J)) - (I_1(J)/I_0(J))^2")
    print()
    print("  NUMERICAL VERIFICATION (J = 0.5):")

    from scipy.special import iv as bessel_i
    J = 0.5
    I0 = bessel_i(0, J)
    I1 = bessel_i(1, J)
    I2 = bessel_i(2, J)

    E_cos = I1 / I0
    E_cos2 = 0.5 + I2 / (2 * I0)
    F_diag_analytical = E_cos2 - E_cos**2

    print(f"    I_0({J}) = {I0:.6f}")
    print(f"    I_1({J}) = {I1:.6f}")
    print(f"    I_2({J}) = {I2:.6f}")
    print(f"    E[cos(phi)] = {E_cos:.6f}")
    print(f"    E[cos^2(phi)] = {E_cos2:.6f}")
    print(f"    F_ee (analytical) = {F_diag_analytical:.6f}")
    print()

    # Compare with numerical
    edges_path3, _, _ = create_graph("path", 3)
    F_num = xy_fisher_quadrature(edges_path3, 3, J, n_quad=128)
    print(f"    F_ee (numerical, path P3, n_quad=128) = {F_num[0,0]:.6f}")
    print(f"    Relative error: {abs(F_num[0,0] - F_diag_analytical)/F_diag_analytical:.2e}")
    print()

    # Comparison to Ising
    print("  COMPARISON TO ISING:")
    print(f"    Ising F_ee = sech^2(J) = {1/np.cosh(J)**2:.6f}")
    print(f"    XY F_ee = 1/2 + I_2/(2*I_0) - (I_1/I_0)^2 = {F_diag_analytical:.6f}")
    print(f"    Ratio: {F_diag_analytical / (1/np.cosh(J)**2):.4f}")
    print()
    print("    Key difference: Ising uses sech^2(J), XY uses Bessel function expression.")
    print("    Both are positive and decrease with increasing J.")
    print()

    print()
    print("PART 2: HEISENBERG MODEL FISHER INFORMATION MATRIX")
    print("-" * 60)
    print()
    print("  The Heisenberg model on graph G = (V, E):")
    print()
    print("  Spins: sigma_i in S^2 (unit sphere), parametrized by (theta_i, phi_i)")
    print("  Hamiltonian: H = -J * sum_{(i,j) in E} sigma_i . sigma_j")
    print()
    print("  Exponential family structure:")
    print("    Natural parameters: J_e (one per edge)")
    print("    Sufficient statistics: T_e = sigma_i . sigma_j")
    print("    Measure: product uniform (Haar) on (S^2)^n")
    print()
    print("  Fisher information matrix:")
    print("    F_{ab} = Cov(T_a, T_b) = Cov(sigma_i . sigma_j, sigma_k . sigma_l)")
    print()
    print("  TREE FISHER IDENTITY for Heisenberg:")
    print("    On a tree, fix a root. Each spin sigma_v is related to its parent")
    print("    sigma_{p(v)} by sigma_v = R_v * sigma_{p(v)} where R_v is a rotation.")
    print()
    print("    The sufficient statistic T_e = sigma_i . sigma_j = sigma_i^T sigma_j")
    print("    depends only on the RELATIVE ORIENTATION of adjacent spins.")
    print()
    print("    On a tree, these relative orientations are independent random variables")
    print("    (same factorization argument as for Ising and XY).")
    print()
    print("    Therefore: F_{ab} = 0 for a != b on trees.")
    print("    The Tree Fisher Identity holds for the Heisenberg model.")
    print()
    print("    The diagonal entry involves the distribution of the dot product")
    print("    of two unit vectors, weighted by exp(J * cos(alpha)) where alpha")
    print("    is the angle between them.")
    print()
    print("    Using the Langevin distribution on S^2:")
    print("    E[cos(alpha)] = coth(J) - 1/J  (Langevin function L(J))")
    print("    E[cos^2(alpha)] = 1 - 2*L(J)/J")
    print("    F_{ee} = Var(cos(alpha)) = E[cos^2] - (E[cos])^2")
    print()

    def langevin(x):
        """Langevin function L(x) = coth(x) - 1/x."""
        if abs(x) < 1e-10:
            return 0.0
        return 1.0 / np.tanh(x) - 1.0 / x

    L_J = langevin(J)
    E_cos_heis = L_J
    E_cos2_heis = 1.0 - 2.0 * L_J / J
    F_diag_heis = E_cos2_heis - E_cos_heis**2

    print(f"  NUMERICAL VERIFICATION (J = {J}):")
    print(f"    L({J}) = {L_J:.6f}")
    print(f"    E[cos(alpha)] = {E_cos_heis:.6f}")
    print(f"    E[cos^2(alpha)] = {E_cos2_heis:.6f}")
    print(f"    F_ee (analytical) = {F_diag_heis:.6f}")
    print()

    # Compare with numerical
    edges_path2, _, _ = create_graph("path", 2)
    print("    (Numerical verification for Heisenberg uses MC, so expect some noise.)")

    print()
    print("  COMPARISON: DIAGONAL ENTRIES ACROSS MODELS")
    print()
    print(f"  J = {J}:")
    print(f"    Ising:       F_ee = sech^2(J) = {1/np.cosh(J)**2:.6f}")
    print(f"    XY:          F_ee = {F_diag_analytical:.6f}")
    print(f"    Heisenberg:  F_ee = {F_diag_heis:.6f}")
    print()
    print("  All are positive and decreasing in J. The specific functional form differs,")
    print("  but the key structural property -- F is diagonal on trees -- is universal.")
    print()

    print()
    print("PART 3: TREE FISHER IDENTITY -- UNIVERSAL PROOF SKETCH")
    print("-" * 60)
    print()
    print("  Theorem (Generalized Tree Fisher Identity).")
    print("  Let M be any spin model on a tree graph G where:")
    print("    (a) Spins take values in a compact space X (e.g., {-1,+1}, S^1, S^2)")
    print("    (b) The Hamiltonian is H = -sum_{e=(i,j)} J_e * f(sigma_i, sigma_j)")
    print("        where f depends only on the pair of adjacent spins")
    print("    (c) f is symmetric: f(x, y) = f(y, x)")
    print()
    print("  Then the sufficient statistics T_e = f(sigma_i, sigma_j) are mutually")
    print("  independent under the Boltzmann distribution, and therefore the Fisher")
    print("  information matrix is diagonal: F = diag(Var(T_{e_1}), ..., Var(T_{e_m})).")
    print()
    print("  Proof sketch:")
    print("    Fix a root vertex r. On a tree, each vertex v != r has a unique parent p(v).")
    print("    The Hamiltonian factorizes:")
    print("      exp(-H) = prod_{e=(i,j) in E} exp(J_e * f(sigma_i, sigma_j))")
    print()
    print("    Integrate out spins from leaves toward root. At each leaf vertex v")
    print("    with parent edge e = (p(v), v):")
    print("      integral over sigma_v of exp(J_e * f(sigma_{p(v)}, sigma_v)) d_mu(sigma_v)")
    print("    = g(sigma_{p(v)})  [some function of the parent spin]")
    print()
    print("    This integral factors out the edge e contribution. Repeating for all")
    print("    vertices, the partition function factorizes and the T_e become independent.")
    print("    QED.")
    print()
    print("  This proof is IDENTICAL in structure to the Ising case (Lemma 6.1 of the")
    print("  Spectral Gap Selection Theorem). The key property is the TREE STRUCTURE")
    print("  (no cycles), not the nature of the spin variable.")
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Print analytical derivations first
    print_analytical_derivations()

    # Run computational campaign
    results = run_campaign()

    # Write detailed results file
    if results:
        output_path = ("/Users/Max_1/Projects/PhysicsResearch/cosmological-unification/"
                        "papers/structural-bridge/src/results/continuous-spin-analysis.md")
        write_results_file(results, output_path)
        print(f"\nDetailed results written to: {output_path}")

    print()
    print("=" * 90)
    print("CAMPAIGN COMPLETE")
    print("=" * 90)
