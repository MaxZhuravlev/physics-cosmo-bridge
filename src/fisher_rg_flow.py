#!/usr/bin/env python3
"""
Fisher Information RG Flow Analysis

Investigates whether renormalization group (RG) coarse-graining on observer graphs
produces a natural flow toward effective continuous geometry.

Research Question:
    Does the Fisher information matrix have a well-defined RG flow?
    If so, does the flow have fixed points where near-diagonal structure
    and Lorentzian signature selection are ENHANCED?

Method:
    1. Start with Ising model on path/2D lattice (exact Fisher matrix)
    2. Apply Kadanoff block-spin transformation (k neighboring sites → 1 effective site)
    3. Compute Fisher matrix of blocked model
    4. Track: near-diagonal ratio, Lorentzian preference W(q=1), effective coupling
    5. Iterate until system too small

Key Insight:
    This is DIFFERENT from naive continuum limit (N → ∞).
    RG progressively blocks sites, creating effective interactions at larger scales.
    At RG fixed points, continuous symmetry can EMERGE from discrete dynamics.

Attribution:
    test_id: TEST-BRIDGE-MVP1-FISHER-RG-FLOW-001
    mvp_layer: MVP-1
    dialogue_id: session-2026-02-17-rg-coarse-graining
"""

import numpy as np
import itertools
from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class RGFlowStep:
    """Single step in RG flow."""
    iteration: int
    n_sites: int
    m_edges: int
    J_eff: float  # Effective coupling at this scale
    near_diagonal_ratio: float
    W_q1: float  # Lorentzian preference
    spectral_gap: float  # (d_2 - d_1) / |d_1| if exists
    effective_dimension: float  # Participation ratio of eigenvalues


def create_path_J_matrix(n: int, J: float = 1.0) -> np.ndarray:
    """
    Create coupling matrix for 1D path (chain) of n sites.

    Args:
        n: Number of sites
        J: Nearest-neighbor coupling strength

    Returns:
        J_matrix: (n, n) symmetric coupling matrix
    """
    J_matrix = np.zeros((n, n))
    for i in range(n - 1):
        J_matrix[i, i + 1] = J
        J_matrix[i + 1, i] = J
    return J_matrix


def create_2d_grid_J_matrix(nx: int, ny: int, J: float = 1.0) -> np.ndarray:
    """
    Create coupling matrix for 2D grid (nx × ny sites).

    Args:
        nx, ny: Grid dimensions
        J: Nearest-neighbor coupling

    Returns:
        J_matrix: (nx*ny, nx*ny) coupling matrix
    """
    n = nx * ny
    J_matrix = np.zeros((n, n))

    def idx(i, j):
        """Map 2D coords to linear index."""
        return i * ny + j

    for i in range(nx):
        for j in range(ny):
            # Right neighbor
            if j < ny - 1:
                J_matrix[idx(i, j), idx(i, j + 1)] = J
                J_matrix[idx(i, j + 1), idx(i, j)] = J
            # Down neighbor
            if i < nx - 1:
                J_matrix[idx(i, j), idx(i + 1, j)] = J
                J_matrix[idx(i + 1, j), idx(i, j)] = J

    return J_matrix


def compute_exact_fisher_ising(J_matrix: np.ndarray) -> Tuple[np.ndarray, List[Tuple[int, int]]]:
    """
    Compute exact Fisher Information Matrix for Ising model.

    H(s) = - sum_{i<j} J_{ij} s_i s_j
    P(s) = exp(-H(s)) / Z  (beta=1)

    Fisher matrix F_ab = Cov(phi_a, phi_b) where phi_e = s_i * s_j for edge e=(i,j)

    Args:
        J_matrix: (N, N) symmetric coupling matrix

    Returns:
        F: (m, m) Fisher matrix (m = number of edges)
        edges: List of (i, j) edge tuples
    """
    N = J_matrix.shape[0]

    # Identify edges
    edges = []
    for i in range(N):
        for j in range(i + 1, N):
            if abs(J_matrix[i, j]) > 1e-10:
                edges.append((i, j))

    m = len(edges)
    if m == 0:
        return np.zeros((0, 0)), []

    # Generate all 2^N Ising states
    states = np.array(list(itertools.product([-1, 1], repeat=N)))

    # Compute interactions phi_e = s_i * s_j for each edge
    interactions = np.zeros((2**N, m))
    for k, (i, j) in enumerate(edges):
        interactions[:, k] = states[:, i] * states[:, j]

    # Compute energies
    J_values = np.array([J_matrix[u, v] for u, v in edges])
    energies = -interactions @ J_values

    # Probabilities (beta=1)
    min_E = np.min(energies)
    weights = np.exp(-(energies - min_E))
    Z = np.sum(weights)
    probs = weights / Z

    # Fisher matrix = Cov(phi)
    mean_phi = probs @ interactions
    centered_interactions = interactions - mean_phi
    F = (centered_interactions * probs[:, None]).T @ centered_interactions

    return F, edges


def block_ising_1d(J_matrix: np.ndarray, block_size: int = 2) -> np.ndarray:
    """
    Kadanoff block-spin RG transformation for 1D Ising model.

    Procedure:
        1. Group sites into blocks of size k (block_size)
        2. Sum spins within each block: S_I = sum_{i in block I} s_i
        3. Compute effective Hamiltonian for block spins
        4. Use second-order cumulant expansion to get J_eff

    For 1D Ising with NN coupling J:
        J_eff ≈ k * J  (to leading order)

    More accurate (decimation RG for k=2):
        Integrate out every other spin analytically.

    Args:
        J_matrix: (n, n) coupling matrix for original system
        block_size: Number of sites per block (default=2)

    Returns:
        J_blocked: (n/block_size, n/block_size) effective coupling matrix
    """
    n = J_matrix.shape[0]
    if n % block_size != 0:
        # Truncate to multiple of block_size
        n = (n // block_size) * block_size

    n_blocks = n // block_size

    # For 1D path, use decimation RG (exact for k=2)
    if block_size == 2:
        # Decimation: integrate out odd sites, keep even sites
        # For path: J_eff[i, i+1] = J^2 / (2 * tanh^{-1}(tanh(J)))
        # Simplified: J_eff ≈ J * (1 - small corrections)

        J = J_matrix[0, 1]  # Assume uniform coupling
        if abs(J) < 1e-10:
            return np.zeros((n_blocks, n_blocks))

        # Exact RG formula for 1D Ising decimation
        # Keep even sites (0, 2, 4, ...), integrate odd sites (1, 3, 5, ...)
        # J_new / J_old = tanh(J_old)^2 / tanh(J_old) = tanh(J_old)
        J_eff = np.arctanh(np.tanh(J)**2)

        J_blocked = create_path_J_matrix(n_blocks, J=J_eff)
        return J_blocked

    else:
        # Simple majority-rule blocking (approximate)
        J = J_matrix[0, 1]
        # Heuristic: J_eff ~ J * (block_size / 2)
        J_eff = J * (block_size / 2.0)
        J_blocked = create_path_J_matrix(n_blocks, J=J_eff)
        return J_blocked


def block_ising_2d(J_matrix: np.ndarray, nx: int, ny: int, block_size: int = 2) -> Tuple[np.ndarray, int, int]:
    """
    Kadanoff block-spin RG for 2D Ising on square lattice.

    Procedure:
        1. Group (block_size × block_size) sites into one block spin
        2. Use Kadanoff approximation: majority rule or Migdal-Kadanoff
        3. Compute effective coupling

    Args:
        J_matrix: (nx*ny, nx*ny) coupling matrix
        nx, ny: Original grid dimensions
        block_size: Block dimension (2 → 2×2 blocks)

    Returns:
        J_blocked: Effective coupling for blocked system
        nx_new, ny_new: New grid dimensions
    """
    # For simplicity, use Migdal-Kadanoff approximation
    # J_eff ≈ (1/4) * ln(cosh(4*J))

    J = J_matrix[0, 1] if J_matrix.shape[0] > 1 else 1.0

    # Migdal-Kadanoff RG (approximate)
    if abs(J) > 1e-10:
        J_eff = 0.25 * np.log(np.cosh(4.0 * J))
    else:
        J_eff = 0.0

    nx_new = nx // block_size
    ny_new = ny // block_size

    if nx_new < 1 or ny_new < 1:
        return np.zeros((0, 0)), 0, 0

    J_blocked = create_2d_grid_J_matrix(nx_new, ny_new, J=J_eff)
    return J_blocked, nx_new, ny_new


def compute_near_diagonal_ratio(F: np.ndarray) -> float:
    """
    Compute near-diagonal ratio: ||F_off|| / ||F_diag||

    Measures deviation from diagonal structure.

    Args:
        F: Fisher matrix

    Returns:
        ratio: ||F - diag(F)|| / ||diag(F)||
    """
    if F.size == 0:
        return 0.0

    F_diag = np.diag(np.diag(F))
    F_off = F - F_diag

    norm_diag = np.linalg.norm(F_diag, 'fro')
    norm_off = np.linalg.norm(F_off, 'fro')

    if norm_diag < 1e-10:
        return 0.0

    return norm_off / norm_diag


def compute_lorentzian_preference(F: np.ndarray, exhaustive_threshold: int = 12) -> float:
    """
    Compute Lorentzian preference W(q=1) = beta_c(q=1) * L_gap(q=1).

    For signed metric M = F^{1/2} S F^{1/2} with S = diag(1, ..., 1, -1),
    compute:
        - beta_c(q=1) = -min_eig(M) if min_eig < 0, else 0
        - L_gap(q=1) = (d_2 - d_1) / |d_1|
        - W(q=1) = beta_c * L_gap

    Args:
        F: Fisher matrix
        exhaustive_threshold: If m > threshold, use random sampling

    Returns:
        W_q1: Lorentzian preference weighting
    """
    m = F.shape[0]
    if m < 2:
        return 0.0

    # Stabilize F
    F_stab = F + 1e-9 * np.eye(m)
    vals, vecs = np.linalg.eigh(F_stab)
    F_sqrt = vecs @ np.diag(np.sqrt(np.maximum(vals, 0))) @ vecs.T

    best_beta_c = 0.0
    best_L_gap = 0.0

    # Search over all possible single-negative sign assignments
    if m <= exhaustive_threshold:
        sign_choices = range(m)
    else:
        # Random sample
        rng = np.random.default_rng(42)
        sign_choices = rng.choice(m, size=min(1000, m), replace=False)

    for neg_idx in sign_choices:
        S_diag = np.ones(m)
        S_diag[neg_idx] = -1.0

        S_mat = np.diag(S_diag)
        M = F_sqrt @ S_mat @ F_sqrt

        eigs = np.linalg.eigvalsh(M)
        min_eig = eigs[0]
        second_eig = eigs[1] if len(eigs) > 1 else min_eig

        if min_eig < 0:
            beta_c = -min_eig
            L_gap = (second_eig - min_eig) / abs(min_eig) if min_eig != 0 else 0

            if beta_c > best_beta_c:
                best_beta_c = beta_c
                best_L_gap = L_gap

    W_q1 = best_beta_c * best_L_gap
    return W_q1


def compute_effective_dimension(F: np.ndarray) -> float:
    """
    Compute effective dimension via participation ratio of eigenvalues.

    D_eff = (sum lambda_i)^2 / sum lambda_i^2

    Args:
        F: Fisher matrix

    Returns:
        D_eff: Effective dimension (1 to m)
    """
    if F.size == 0:
        return 0.0

    eigvals = np.linalg.eigvalsh(F)
    eigvals = np.maximum(eigvals, 0)  # Ensure positive

    sum_eigs = np.sum(eigvals)
    sum_sq_eigs = np.sum(eigvals**2)

    if sum_sq_eigs < 1e-10:
        return 0.0

    D_eff = sum_eigs**2 / sum_sq_eigs
    return D_eff


def compute_spectral_gap(F: np.ndarray) -> float:
    """
    Compute spectral gap (d_2 - d_1) / |d_1| for F.

    If F is all positive, return normalized gap.

    Args:
        F: Fisher matrix

    Returns:
        gap: Spectral gap ratio
    """
    if F.shape[0] < 2:
        return 0.0

    eigvals = np.linalg.eigvalsh(F)
    d_1 = eigvals[0]
    d_2 = eigvals[1]

    if abs(d_1) < 1e-10:
        return 0.0

    gap = (d_2 - d_1) / abs(d_1)
    return gap


def fisher_rg_flow_1d(
    J_init: np.ndarray,
    max_iterations: int = 10,
    block_size: int = 2
) -> List[RGFlowStep]:
    """
    Compute RG flow for 1D Ising Fisher matrices.

    Procedure:
        1. Start with J_init
        2. Compute Fisher matrix
        3. Measure: near-diagonal ratio, W(q=1), spectral gap, effective dimension
        4. Apply blocking transformation J → J_blocked
        5. Repeat until system too small

    Args:
        J_init: Initial (n, n) coupling matrix
        max_iterations: Maximum RG steps
        block_size: Sites per block (default=2)

    Returns:
        flow: List of RGFlowStep data
    """
    flow = []
    J_current = J_init.copy()

    for it in range(max_iterations):
        n_sites = J_current.shape[0]

        # Compute Fisher matrix
        F, edges = compute_exact_fisher_ising(J_current)
        m_edges = len(edges)

        if m_edges < 2:
            # System too small
            break

        # Extract effective coupling (assume uniform for path)
        J_eff = J_current[0, 1] if n_sites > 1 else 0.0

        # Compute geometric measures
        near_diag = compute_near_diagonal_ratio(F)
        W_q1 = compute_lorentzian_preference(F)
        gap = compute_spectral_gap(F)
        D_eff = compute_effective_dimension(F)

        step = RGFlowStep(
            iteration=it,
            n_sites=n_sites,
            m_edges=m_edges,
            J_eff=J_eff,
            near_diagonal_ratio=near_diag,
            W_q1=W_q1,
            spectral_gap=gap,
            effective_dimension=D_eff
        )
        flow.append(step)

        # Apply blocking
        J_blocked = block_ising_1d(J_current, block_size=block_size)

        if J_blocked.shape[0] < 2:
            # Cannot block further
            break

        J_current = J_blocked

    return flow


def fisher_rg_flow_2d(
    J_init: np.ndarray,
    nx_init: int,
    ny_init: int,
    max_iterations: int = 10,
    block_size: int = 2
) -> List[RGFlowStep]:
    """
    Compute RG flow for 2D Ising Fisher matrices.

    Args:
        J_init: Initial coupling matrix
        nx_init, ny_init: Initial grid dimensions
        max_iterations: Maximum RG steps
        block_size: Block dimension (2 → 2×2 blocks)

    Returns:
        flow: List of RGFlowStep data
    """
    flow = []
    J_current = J_init.copy()
    nx, ny = nx_init, ny_init

    for it in range(max_iterations):
        n_sites = nx * ny

        # Compute Fisher matrix
        F, edges = compute_exact_fisher_ising(J_current)
        m_edges = len(edges)

        if m_edges < 2 or n_sites < 4:
            break

        # Extract effective coupling
        J_eff = J_current[0, 1] if J_current.shape[0] > 1 else 0.0

        # Compute measures
        near_diag = compute_near_diagonal_ratio(F)
        W_q1 = compute_lorentzian_preference(F)
        gap = compute_spectral_gap(F)
        D_eff = compute_effective_dimension(F)

        step = RGFlowStep(
            iteration=it,
            n_sites=n_sites,
            m_edges=m_edges,
            J_eff=J_eff,
            near_diagonal_ratio=near_diag,
            W_q1=W_q1,
            spectral_gap=gap,
            effective_dimension=D_eff
        )
        flow.append(step)

        # Apply 2D blocking
        J_blocked, nx_new, ny_new = block_ising_2d(J_current, nx, ny, block_size=block_size)

        if nx_new < 1 or ny_new < 1:
            break

        J_current = J_blocked
        nx, ny = nx_new, ny_new

    return flow


def main():
    """Run Fisher RG flow analysis and write results."""
    import json

    print("=" * 80)
    print("FISHER INFORMATION RG FLOW ANALYSIS")
    print("=" * 80)
    print()
    print("Research Question:")
    print("  Does RG coarse-graining improve geometric structure of Fisher matrices?")
    print()
    print("Method:")
    print("  - Start with 1D/2D Ising model")
    print("  - Apply Kadanoff block-spin RG")
    print("  - Track: near-diagonal ratio, W(q=1), spectral gap, effective dimension")
    print("  - Check if near-diagonal ratio DECREASES (geometry improves)")
    print()
    print("=" * 80)
    print()

    results = {
        "1d_flows": [],
        "2d_flows": []
    }

    # 1D RG flows
    print("1D RG FLOWS")
    print("-" * 80)

    sizes_1d = [8, 16, 32, 64]
    couplings = [0.3, 0.5, 1.0]

    for n in sizes_1d:
        for J in couplings:
            print(f"\n1D Path: n={n}, J={J:.2f}")
            J_init = create_path_J_matrix(n, J=J)
            flow = fisher_rg_flow_1d(J_init, max_iterations=6)

            print(f"{'Iter':<6} {'N':<6} {'m':<6} {'J_eff':<10} {'near_diag':<12} {'W(q=1)':<12} {'gap':<10}")
            print("-" * 70)

            flow_data = []
            for step in flow:
                print(f"{step.iteration:<6} {step.n_sites:<6} {step.m_edges:<6} "
                      f"{step.J_eff:<10.4f} {step.near_diagonal_ratio:<12.4f} "
                      f"{step.W_q1:<12.4f} {step.spectral_gap:<10.4f}")

                flow_data.append({
                    "iteration": step.iteration,
                    "n_sites": step.n_sites,
                    "m_edges": step.m_edges,
                    "J_eff": step.J_eff,
                    "near_diagonal_ratio": step.near_diagonal_ratio,
                    "W_q1": step.W_q1,
                    "spectral_gap": step.spectral_gap,
                    "effective_dimension": step.effective_dimension
                })

            # Check trend
            if len(flow) >= 2:
                initial_ratio = flow[0].near_diagonal_ratio
                final_ratio = flow[-1].near_diagonal_ratio
                improves = final_ratio < initial_ratio
                print(f"  → Near-diagonal improves: {improves} ({initial_ratio:.4f} → {final_ratio:.4f})")

            results["1d_flows"].append({
                "n_init": n,
                "J_init": J,
                "flow": flow_data
            })

    # 2D RG flows (smaller due to computational cost)
    print("\n\n2D RG FLOWS")
    print("-" * 80)

    grid_sizes = [(4, 4), (6, 6)]
    couplings_2d = [0.5, 1.0]

    for (nx, ny) in grid_sizes:
        for J in couplings_2d:
            print(f"\n2D Grid: {nx}×{ny}, J={J:.2f}")
            J_init = create_2d_grid_J_matrix(nx, ny, J=J)
            flow = fisher_rg_flow_2d(J_init, nx, ny, max_iterations=4)

            print(f"{'Iter':<6} {'N':<6} {'m':<6} {'J_eff':<10} {'near_diag':<12} {'W(q=1)':<12}")
            print("-" * 70)

            flow_data = []
            for step in flow:
                print(f"{step.iteration:<6} {step.n_sites:<6} {step.m_edges:<6} "
                      f"{step.J_eff:<10.4f} {step.near_diagonal_ratio:<12.4f} "
                      f"{step.W_q1:<12.4f}")

                flow_data.append({
                    "iteration": step.iteration,
                    "n_sites": step.n_sites,
                    "m_edges": step.m_edges,
                    "J_eff": step.J_eff,
                    "near_diagonal_ratio": step.near_diagonal_ratio,
                    "W_q1": step.W_q1,
                    "spectral_gap": step.spectral_gap,
                    "effective_dimension": step.effective_dimension
                })

            if len(flow) >= 2:
                initial_ratio = flow[0].near_diagonal_ratio
                final_ratio = flow[-1].near_diagonal_ratio
                improves = final_ratio < initial_ratio
                print(f"  → Near-diagonal improves: {improves} ({initial_ratio:.4f} → {final_ratio:.4f})")

            results["2d_flows"].append({
                "nx_init": nx,
                "ny_init": ny,
                "J_init": J,
                "flow": flow_data
            })

    # Write JSON results
    output_json = "/Users/Max_1/Projects/PhysicsResearch/cosmological-unification/papers/structural-bridge/output/FISHER-RG-FLOW-RESULTS.json"
    with open(output_json, "w") as f:
        json.dump(results, f, indent=2)

    print()
    print("=" * 80)
    print(f"Results written to: {output_json}")
    print("Writing markdown summary...")

    # Write markdown summary
    write_markdown_summary(results)

    print("=" * 80)


def write_markdown_summary(results: dict):
    """Write comprehensive markdown summary of RG flow results."""

    output_path = "/Users/Max_1/Projects/PhysicsResearch/cosmological-unification/papers/structural-bridge/output/FISHER-RG-FLOW-RESULTS.md"

    with open(output_path, "w") as f:
        f.write("# Fisher Information RG Flow Analysis\n\n")
        f.write("**Date:** 2026-02-17\n")
        f.write("**Attribution:** TEST-BRIDGE-MVP1-FISHER-RG-FLOW-001\n\n")

        f.write("## Research Question\n\n")
        f.write("Does renormalization group (RG) coarse-graining on observer graphs ")
        f.write("produce a natural flow toward effective continuous geometry?\n\n")

        f.write("**Key Insight:** This is DIFFERENT from naive continuum limit (N → ∞). ")
        f.write("RG progressively blocks sites, creating effective interactions at larger scales. ")
        f.write("At RG fixed points, continuous symmetry can EMERGE from discrete dynamics.\n\n")

        f.write("## Method\n\n")
        f.write("1. Start with Ising model on path/2D lattice (exact Fisher matrix)\n")
        f.write("2. Apply Kadanoff block-spin transformation (k neighboring sites → 1 effective site)\n")
        f.write("3. Compute Fisher matrix of blocked model\n")
        f.write("4. Track:\n")
        f.write("   - **Near-diagonal ratio**: ||F_off|| / ||F_diag|| (lower = more geometric)\n")
        f.write("   - **W(q=1)**: Lorentzian preference = beta_c(q=1) * L_gap(q=1)\n")
        f.write("   - **Spectral gap**: (d_2 - d_1) / |d_1|\n")
        f.write("   - **Effective dimension**: Participation ratio of eigenvalues\n")
        f.write("   - **J_eff**: Effective coupling at blocked scale\n")
        f.write("5. Iterate until system too small\n\n")

        f.write("## Expected Outcomes\n\n")
        f.write("- **Near-diagonal ratio DECREASES**: Coarse-graining improves Lorentzian signature (positive)\n")
        f.write("- **RG fixed points with exact diagonal F**: These are the \"continuum limit\" (breakthrough)\n")
        f.write("- **RG flow chaotic/divergent**: This approach fails (negative, but informative)\n\n")

        f.write("---\n\n")

        # 1D Results
        f.write("## 1D RG Flow Results\n\n")

        trend_summary_1d = {"improves": 0, "worsens": 0, "neutral": 0}

        for flow_result in results["1d_flows"]:
            n = flow_result["n_init"]
            J = flow_result["J_init"]
            flow = flow_result["flow"]

            f.write(f"### 1D Path: n={n}, J={J:.2f}\n\n")

            if len(flow) > 0:
                f.write("| Iter | N | m | J_eff | near_diag | W(q=1) | gap |\n")
                f.write("|------|---|---|-------|-----------|--------|-----|\n")

                for step in flow:
                    f.write(f"| {step['iteration']} | {step['n_sites']} | {step['m_edges']} | "
                           f"{step['J_eff']:.4f} | {step['near_diagonal_ratio']:.4f} | "
                           f"{step['W_q1']:.4f} | {step['spectral_gap']:.4f} |\n")

                # Trend analysis
                if len(flow) >= 2:
                    initial = flow[0]["near_diagonal_ratio"]
                    final = flow[-1]["near_diagonal_ratio"]
                    rel_change = (final - initial) / initial if initial > 0 else 0

                    if final < initial * 0.95:
                        trend = "IMPROVES"
                        trend_summary_1d["improves"] += 1
                    elif final > initial * 1.05:
                        trend = "WORSENS"
                        trend_summary_1d["worsens"] += 1
                    else:
                        trend = "NEUTRAL"
                        trend_summary_1d["neutral"] += 1

                    f.write(f"\n**Trend:** Near-diagonal ratio {trend} ({initial:.4f} → {final:.4f}, {rel_change*100:.1f}%)\n\n")

        f.write("### 1D Summary\n\n")
        total_1d = sum(trend_summary_1d.values())
        if total_1d > 0:
            f.write(f"- **Improves:** {trend_summary_1d['improves']}/{total_1d} ({100*trend_summary_1d['improves']/total_1d:.1f}%)\n")
            f.write(f"- **Worsens:** {trend_summary_1d['worsens']}/{total_1d} ({100*trend_summary_1d['worsens']/total_1d:.1f}%)\n")
            f.write(f"- **Neutral:** {trend_summary_1d['neutral']}/{total_1d} ({100*trend_summary_1d['neutral']/total_1d:.1f}%)\n\n")

        # 2D Results
        f.write("---\n\n")
        f.write("## 2D RG Flow Results\n\n")

        trend_summary_2d = {"improves": 0, "worsens": 0, "neutral": 0}

        for flow_result in results["2d_flows"]:
            nx = flow_result["nx_init"]
            ny = flow_result["ny_init"]
            J = flow_result["J_init"]
            flow = flow_result["flow"]

            f.write(f"### 2D Grid: {nx}×{ny}, J={J:.2f}\n\n")

            if len(flow) > 0:
                f.write("| Iter | N | m | J_eff | near_diag | W(q=1) |\n")
                f.write("|------|---|---|-------|-----------|--------|\n")

                for step in flow:
                    f.write(f"| {step['iteration']} | {step['n_sites']} | {step['m_edges']} | "
                           f"{step['J_eff']:.4f} | {step['near_diagonal_ratio']:.4f} | "
                           f"{step['W_q1']:.4f} |\n")

                if len(flow) >= 2:
                    initial = flow[0]["near_diagonal_ratio"]
                    final = flow[-1]["near_diagonal_ratio"]
                    rel_change = (final - initial) / initial if initial > 0 else 0

                    if final < initial * 0.95:
                        trend = "IMPROVES"
                        trend_summary_2d["improves"] += 1
                    elif final > initial * 1.05:
                        trend = "WORSENS"
                        trend_summary_2d["worsens"] += 1
                    else:
                        trend = "NEUTRAL"
                        trend_summary_2d["neutral"] += 1

                    f.write(f"\n**Trend:** Near-diagonal ratio {trend} ({initial:.4f} → {final:.4f}, {rel_change*100:.1f}%)\n\n")

        f.write("### 2D Summary\n\n")
        total_2d = sum(trend_summary_2d.values())
        if total_2d > 0:
            f.write(f"- **Improves:** {trend_summary_2d['improves']}/{total_2d} ({100*trend_summary_2d['improves']/total_2d:.1f}%)\n")
            f.write(f"- **Worsens:** {trend_summary_2d['worsens']}/{total_2d} ({100*trend_summary_2d['worsens']/total_2d:.1f}%)\n")
            f.write(f"- **Neutral:** {trend_summary_2d['neutral']}/{total_2d} ({100*trend_summary_2d['neutral']/total_2d:.1f}%)\n\n")

        # Overall conclusion
        f.write("---\n\n")
        f.write("## Conclusion\n\n")

        total_improves = trend_summary_1d["improves"] + trend_summary_2d["improves"]
        total_all = total_1d + total_2d

        if total_all > 0:
            improve_pct = 100 * total_improves / total_all

            if improve_pct > 60:
                f.write(f"**POSITIVE RESULT ({improve_pct:.1f}%)**: RG coarse-graining IMPROVES near-diagonal structure in most cases.\n\n")
                f.write("**Interpretation:** The discrete → continuous flow works via RG, not naive N → ∞. ")
                f.write("At large scales, Fisher matrices become more diagonal, improving geometric interpretation.\n\n")
                f.write("**Next steps:**\n")
                f.write("- Test RG flow on multiway hypergraph systems\n")
                f.write("- Identify RG fixed points (if J_eff converges)\n")
                f.write("- Analytic calculation of RG flow for Fisher matrices\n\n")

            elif improve_pct > 30:
                f.write(f"**MIXED RESULT ({improve_pct:.1f}%)**: RG shows improvement in some cases but not universally.\n\n")
                f.write("**Interpretation:** RG may improve geometry for specific parameter regimes ")
                f.write("(low coupling, large initial size) but not generically.\n\n")
                f.write("**Next steps:**\n")
                f.write("- Identify which parameters correlate with improvement\n")
                f.write("- Test critical regime (near phase transition)\n\n")

            else:
                f.write(f"**NEGATIVE RESULT ({improve_pct:.1f}%)**: RG coarse-graining does NOT improve near-diagonal structure.\n\n")
                f.write("**Interpretation:** The continuum limit problem remains. RG blocking does not ")
                f.write("resolve the discrete-to-continuous gap for Fisher matrices.\n\n")
                f.write("**Implication:** The naive continuum limit failure (κ → 0) is NOT fixed by RG. ")
                f.write("A different mechanism is needed.\n\n")

        f.write("---\n\n")
        f.write("*Generated by fisher_rg_flow.py*\n")

    print(f"Markdown summary written to: {output_path}")


if __name__ == "__main__":
    main()
