#!/usr/bin/env python3
"""
Spectral Gap Analysis for Ising Fisher Matrices

Tests whether Ising Fisher matrices exhibit spectral gap weighting W(q) that favors q=1
(Lorentzian signature) over higher q values.

Research Question:
    Do ISING FISHER MATRICES (not generic random PD matrices) form a special class
    where W(q=1) = beta_c(q=1) * L_gap(q=1) dominates over W(q>=2)?

Method:
    1. Compute exact Ising Fisher matrices for various graph topologies
    2. For each q from 1 to m-1, compute:
       - beta_c(q) = max over sign assignments with q negative of [-min_eig(F^{1/2}SF^{1/2})]
       - L_gap(q) = (d_2 - d_1)/|d_1| at the optimal sign assignment
       - W(q) = beta_c(q) * L_gap(q)
    3. Determine if W(q=1) > max W(q>=2)

Attribution:
    test_id: TEST-BRIDGE-MVP1-SPECTRAL-GAP-ISING-001
    mvp_layer: MVP-1
    dialogue_id: session-2026-02-16-spectral-gap-ising
"""

import numpy as np
import itertools
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import time
import networkx as nx


@dataclass
class SpectralGapResult:
    """Results for a single (graph, J, q) configuration."""
    graph_name: str
    n_vertices: int
    n_edges: int
    coupling_J: float
    q: int
    beta_c: float
    L_gap: float
    W: float
    optimal_sign_assignment: np.ndarray
    min_eig: float
    second_eig: float


@dataclass
class GraphAnalysisResult:
    """Aggregated results for a single (graph, J) pair."""
    graph_name: str
    n_vertices: int
    n_edges: int
    coupling_J: float
    q_results: Dict[int, SpectralGapResult]
    q1_wins: bool  # True if W(q=1) > max W(q>=2)

    def get_winner_q(self) -> int:
        """Return q with maximum W."""
        if not self.q_results:
            return -1
        return max(self.q_results.keys(), key=lambda q: self.q_results[q].W)

    def get_W_q1(self) -> float:
        """Get W(q=1)."""
        return self.q_results.get(1, SpectralGapResult(
            graph_name=self.graph_name, n_vertices=self.n_vertices,
            n_edges=self.n_edges, coupling_J=self.coupling_J, q=1,
            beta_c=0, L_gap=0, W=0, optimal_sign_assignment=np.array([]),
            min_eig=0, second_eig=0
        )).W

    def get_max_W_higher(self) -> float:
        """Get max W(q>=2)."""
        higher_q = {q: res for q, res in self.q_results.items() if q >= 2}
        if not higher_q:
            return 0.0
        return max(res.W for res in higher_q.values())


def compute_exact_fisher_ising(J_matrix: np.ndarray) -> Tuple[np.ndarray, List[Tuple[int, int]]]:
    """
    Compute exact Fisher Information Matrix for Ising model.

    H(s) = - sum_{i<j} J_{ij} s_i s_j
    P(s) = exp(-H(s)) / Z

    Returns:
        F: (m, m) Fisher matrix
        edges: List of (i, j) pairs corresponding to F rows/cols
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

    # Generate all 2^N states
    states = np.array(list(itertools.product([-1, 1], repeat=N)))

    # Compute interactions (spin products for each edge)
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

    # Fisher matrix (covariance of phi_e = s_i * s_j)
    mean_phi = probs @ interactions
    centered_interactions = interactions - mean_phi
    F = (centered_interactions * probs[:, None]).T @ centered_interactions

    return F, edges


def compute_spectral_gap_for_q(
    F: np.ndarray,
    q: int,
    exhaustive_threshold: int = 12
) -> Tuple[float, float, float, np.ndarray, float, float]:
    """
    Compute beta_c(q), L_gap(q), W(q) for given q.

    For q negative signs, find the sign assignment that maximizes beta_c.

    Returns:
        beta_c: Maximum beta_c for this q
        L_gap: Spectral gap (d_2 - d_1)/|d_1| at optimal assignment
        W: Weighting W(q) = beta_c * L_gap
        optimal_S: Diagonal of optimal sign matrix
        min_eig: d_1 at optimal assignment
        second_eig: d_2 at optimal assignment
    """
    m = F.shape[0]

    if q < 0 or q > m:
        raise ValueError(f"q must be in [0, m], got q={q}, m={m}")

    # Stabilize F
    F_stab = F + 1e-9 * np.eye(m)
    vals, vecs = np.linalg.eigh(F_stab)
    F_sqrt = vecs @ np.diag(np.sqrt(np.maximum(vals, 0))) @ vecs.T

    best_beta_c = -1.0
    best_L_gap = 0.0
    best_S = np.ones(m)
    best_min_eig = 0.0
    best_second_eig = 0.0

    # Generate sign assignments
    if m <= exhaustive_threshold:
        # Exhaustive enumeration
        sign_assignments = itertools.combinations(range(m), q)
    else:
        # Random sampling (1000 samples)
        n_samples = 1000
        rng = np.random.default_rng(42)
        indices_list = []
        for _ in range(n_samples):
            perm = rng.permutation(m)
            indices_list.append(tuple(perm[:q]))
        sign_assignments = indices_list

    for neg_indices in sign_assignments:
        S_diag = np.ones(m)
        if len(neg_indices) > 0:
            S_diag[list(neg_indices)] = -1.0

        S_mat = np.diag(S_diag)
        A = F_sqrt @ S_mat @ F_sqrt

        eigs = np.linalg.eigvalsh(A)
        min_eig = eigs[0]
        second_eig = eigs[1] if len(eigs) > 1 else min_eig

        if min_eig < 0:
            beta_c = -min_eig
            L_gap = (second_eig - min_eig) / abs(min_eig) if min_eig != 0 else 0

            if beta_c > best_beta_c:
                best_beta_c = beta_c
                best_L_gap = L_gap
                best_S = S_diag
                best_min_eig = min_eig
                best_second_eig = second_eig

    W = best_beta_c * best_L_gap if best_beta_c > 0 else 0.0

    return best_beta_c, best_L_gap, W, best_S, best_min_eig, best_second_eig


def create_graph_J_matrix(graph_type: str, n: int, J: float = 1.0) -> np.ndarray:
    """
    Create J-matrix for specified graph topology.

    Supported graphs:
        - "complete_K{n}": Complete graph
        - "path_P{n}": Path graph
        - "star_S{n}": Star graph (n-1 edges from center)
        - "cycle_C{n}": Cycle graph
        - "random_ER{n}_{p}": Erdos-Renyi with edge probability p
    """
    J_matrix = np.zeros((n, n))

    if graph_type.startswith("complete"):
        # Complete graph: all pairs connected
        for i in range(n):
            for j in range(i + 1, n):
                J_matrix[i, j] = J
                J_matrix[j, i] = J

    elif graph_type.startswith("path"):
        # Path graph: chain
        for i in range(n - 1):
            J_matrix[i, i + 1] = J
            J_matrix[i + 1, i] = J

    elif graph_type.startswith("star"):
        # Star graph: central node (0) connected to all others
        for i in range(1, n):
            J_matrix[0, i] = J
            J_matrix[i, 0] = J

    elif graph_type.startswith("cycle"):
        # Cycle graph: path + wrap-around edge
        for i in range(n - 1):
            J_matrix[i, i + 1] = J
            J_matrix[i + 1, i] = J
        J_matrix[0, n - 1] = J
        J_matrix[n - 1, 0] = J

    elif graph_type.startswith("random"):
        # Erdos-Renyi random graph
        # Extract probability from graph_type string
        parts = graph_type.split("_")
        p = float(parts[2]) if len(parts) > 2 else 0.5
        rng = np.random.default_rng(42)
        for i in range(n):
            for j in range(i + 1, n):
                if rng.random() < p:
                    J_matrix[i, j] = J
                    J_matrix[j, i] = J

    return J_matrix


def analyze_graph(
    graph_name: str,
    n_vertices: int,
    coupling_J: float,
    exhaustive_threshold: int = 12
) -> Optional[GraphAnalysisResult]:
    """
    Analyze a single (graph, J) configuration.

    Computes W(q) for all q from 1 to m-1 and determines if q=1 wins.
    """
    # Create graph
    J_matrix = create_graph_J_matrix(graph_name, n_vertices, coupling_J)

    # Compute Fisher matrix
    F, edges = compute_exact_fisher_ising(J_matrix)
    m = len(edges)

    if m < 3:
        # Too small for meaningful analysis
        return None

    # Analyze all q
    q_results = {}
    for q in range(1, m):
        try:
            beta_c, L_gap, W, S, min_eig, second_eig = compute_spectral_gap_for_q(
                F, q, exhaustive_threshold
            )

            q_results[q] = SpectralGapResult(
                graph_name=graph_name,
                n_vertices=n_vertices,
                n_edges=m,
                coupling_J=coupling_J,
                q=q,
                beta_c=beta_c,
                L_gap=L_gap,
                W=W,
                optimal_sign_assignment=S,
                min_eig=min_eig,
                second_eig=second_eig
            )
        except Exception as e:
            print(f"Error computing q={q} for {graph_name}: {e}")
            continue

    if not q_results:
        return None

    # Check if q=1 wins
    W_q1 = q_results[1].W if 1 in q_results else 0.0
    W_higher = max((res.W for q, res in q_results.items() if q >= 2), default=0.0)
    q1_wins = W_q1 > W_higher

    return GraphAnalysisResult(
        graph_name=graph_name,
        n_vertices=n_vertices,
        n_edges=m,
        coupling_J=coupling_J,
        q_results=q_results,
        q1_wins=q1_wins
    )


def main():
    """Run comprehensive Ising Fisher spectral gap analysis."""

    print("=" * 80)
    print("SPECTRAL GAP ANALYSIS: ISING FISHER MATRICES")
    print("=" * 80)
    print()
    print("Research Question:")
    print("  Do Ising Fisher matrices favor W(q=1) over W(q>=2)?")
    print()
    print("Method:")
    print("  - Compute exact Ising Fisher for various graph topologies")
    print("  - For each q: compute beta_c(q), L_gap(q), W(q) = beta_c * L_gap")
    print("  - Check if W(q=1) > max W(q>=2)")
    print()
    print("=" * 80)
    print()

    # Test suite
    test_cases = []

    # Complete graphs (K3, K4, K5)
    for n in [3, 4, 5]:
        test_cases.append((f"complete_K{n}", n))

    # Path graphs (P4, P5, P6)
    for n in [4, 5, 6]:
        test_cases.append((f"path_P{n}", n))

    # Star graphs (S4, S5, S6)
    for n in [4, 5, 6]:
        test_cases.append((f"star_S{n}", n))

    # Cycle graphs (C4, C5, C6)
    for n in [4, 5, 6]:
        test_cases.append((f"cycle_C{n}", n))

    # Random graphs
    for n in [4, 5, 6]:
        test_cases.append((f"random_ER{n}_0.5", n))

    # Coupling strengths
    J_values = [0.1, 0.3, 0.5, 0.8, 1.0]

    results = []

    print(f"{'Graph':<20} {'N':<4} {'m':<4} {'J':<6} {'q_win':<6} {'W(q=1)':<12} {'W_max(q>=2)':<12} {'q=1 wins?'}")
    print("-" * 90)

    for graph_name, n in test_cases:
        for J in J_values:
            try:
                result = analyze_graph(graph_name, n, J, exhaustive_threshold=12)
                if result is None:
                    continue

                results.append(result)

                q_win = result.get_winner_q()
                W_q1 = result.get_W_q1()
                W_max_higher = result.get_max_W_higher()
                wins = "YES" if result.q1_wins else "NO"

                print(f"{graph_name:<20} {n:<4} {result.n_edges:<4} {J:<6.2f} {q_win:<6} "
                      f"{W_q1:<12.4f} {W_max_higher:<12.4f} {wins}")

            except Exception as e:
                print(f"Error on {graph_name} (N={n}, J={J}): {e}")
                continue

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    if results:
        total = len(results)
        q1_wins_count = sum(1 for r in results if r.q1_wins)
        percentage = 100 * q1_wins_count / total

        print(f"Total cases analyzed: {total}")
        print(f"Cases where W(q=1) > max W(q>=2): {q1_wins_count}/{total} ({percentage:.1f}%)")
        print()

        # Pattern analysis
        print("PATTERN ANALYSIS:")
        print()

        # By graph type
        graph_types = {}
        for r in results:
            base_type = r.graph_name.split("_")[0]
            if base_type not in graph_types:
                graph_types[base_type] = {"total": 0, "q1_wins": 0}
            graph_types[base_type]["total"] += 1
            if r.q1_wins:
                graph_types[base_type]["q1_wins"] += 1

        print("By graph topology:")
        for gtype, counts in sorted(graph_types.items()):
            pct = 100 * counts["q1_wins"] / counts["total"]
            print(f"  {gtype:12s}: {counts['q1_wins']:2d}/{counts['total']:2d} ({pct:5.1f}%)")

        # By coupling strength
        print()
        print("By coupling strength:")
        J_bins = {}
        for r in results:
            J_rounded = round(r.coupling_J, 1)
            if J_rounded not in J_bins:
                J_bins[J_rounded] = {"total": 0, "q1_wins": 0}
            J_bins[J_rounded]["total"] += 1
            if r.q1_wins:
                J_bins[J_rounded]["q1_wins"] += 1

        for J_val, counts in sorted(J_bins.items()):
            pct = 100 * counts["q1_wins"] / counts["total"]
            print(f"  J={J_val:3.1f}: {counts['q1_wins']:2d}/{counts['total']:2d} ({pct:5.1f}%)")

        # Write detailed results
        write_detailed_results(results)

    else:
        print("No valid results obtained.")

    print()
    print("=" * 80)
    print(f"Detailed results written to: experience/insights/SPECTRAL-GAP-ISING-SPECIFIC-2026-02-16.md")
    print("=" * 80)


def write_detailed_results(results: List[GraphAnalysisResult]):
    """Write comprehensive results to markdown file."""

    output_path = "/Users/Max_1/Projects/PhysicsResearch/cosmological-unification/papers/structural-bridge/experience/insights/SPECTRAL-GAP-ISING-SPECIFIC-2026-02-16.md"

    with open(output_path, "w") as f:
        f.write("# Spectral Gap Analysis: Ising Fisher Matrices\n\n")
        f.write("**Date:** 2026-02-16\n")
        f.write("**Attribution:** TEST-BRIDGE-MVP1-SPECTRAL-GAP-ISING-001\n\n")

        f.write("## Research Question\n\n")
        f.write("Do ISING FISHER MATRICES exhibit spectral gap weighting W(q) = beta_c(q) * L_gap(q) ")
        f.write("that favors q=1 (Lorentzian signature) over higher q values?\n\n")

        f.write("## Method\n\n")
        f.write("1. Compute exact Ising Fisher matrices for various graph topologies\n")
        f.write("2. For each q from 1 to m-1:\n")
        f.write("   - beta_c(q) = max over sign assignments with q negative of [-min_eig(F^{1/2}SF^{1/2})]\n")
        f.write("   - L_gap(q) = (d_2 - d_1)/|d_1| at optimal sign assignment\n")
        f.write("   - W(q) = beta_c(q) * L_gap(q)\n")
        f.write("3. Check if W(q=1) > max W(q>=2)\n\n")

        f.write("## Summary\n\n")
        total = len(results)
        q1_wins_count = sum(1 for r in results if r.q1_wins)
        percentage = 100 * q1_wins_count / total

        f.write(f"**Total cases:** {total}\n")
        f.write(f"**Cases where q=1 wins:** {q1_wins_count} ({percentage:.1f}%)\n\n")

        if percentage < 50:
            f.write("**CONCLUSION:** Ising Fisher matrices do NOT preferentially favor q=1. ")
            f.write("This is a NEGATIVE RESULT for the Lorentzian selection hypothesis.\n\n")
        else:
            f.write("**CONCLUSION:** Ising Fisher matrices DO favor q=1 in most cases.\n\n")

        f.write("## Detailed Results\n\n")
        f.write("| Graph | N | m | J | q_win | W(q=1) | max W(q>=2) | q=1 wins? |\n")
        f.write("|-------|---|---|---|-------|--------|-------------|----------|\n")

        for r in results:
            q_win = r.get_winner_q()
            W_q1 = r.get_W_q1()
            W_max_higher = r.get_max_W_higher()
            wins = "YES" if r.q1_wins else "NO"

            f.write(f"| {r.graph_name} | {r.n_vertices} | {r.n_edges} | {r.coupling_J:.2f} | "
                   f"{q_win} | {W_q1:.4f} | {W_max_higher:.4f} | {wins} |\n")

        f.write("\n## Pattern Analysis\n\n")

        # By graph type
        graph_types = {}
        for r in results:
            base_type = r.graph_name.split("_")[0]
            if base_type not in graph_types:
                graph_types[base_type] = {"total": 0, "q1_wins": 0}
            graph_types[base_type]["total"] += 1
            if r.q1_wins:
                graph_types[base_type]["q1_wins"] += 1

        f.write("### By Graph Topology\n\n")
        f.write("| Topology | q=1 wins | Total | Percentage |\n")
        f.write("|----------|----------|-------|------------|\n")
        for gtype, counts in sorted(graph_types.items()):
            pct = 100 * counts["q1_wins"] / counts["total"]
            f.write(f"| {gtype} | {counts['q1_wins']} | {counts['total']} | {pct:.1f}% |\n")

        # By coupling
        f.write("\n### By Coupling Strength\n\n")
        f.write("| J | q=1 wins | Total | Percentage |\n")
        f.write("|---|----------|-------|------------|\n")
        J_bins = {}
        for r in results:
            J_rounded = round(r.coupling_J, 1)
            if J_rounded not in J_bins:
                J_bins[J_rounded] = {"total": 0, "q1_wins": 0}
            J_bins[J_rounded]["total"] += 1
            if r.q1_wins:
                J_bins[J_rounded]["q1_wins"] += 1

        for J_val, counts in sorted(J_bins.items()):
            pct = 100 * counts["q1_wins"] / counts["total"]
            f.write(f"| {J_val:.1f} | {counts['q1_wins']} | {counts['total']} | {pct:.1f}% |\n")

        f.write("\n## Interpretation\n\n")

        if percentage < 30:
            f.write("The Ising Fisher matrices show STRONG EVIDENCE AGAINST the Lorentzian selection ")
            f.write("hypothesis. The spectral gap weighting W(q) does NOT favor q=1.\n\n")
            f.write("**Implication:** The PSD obstruction (standard metric tensors cannot produce ")
            f.write("Lorentzian signatures) applies to Ising models just as it does to generic ")
            f.write("positive definite matrices. No special structure saves the Lorentzian hypothesis ")
            f.write("in the Ising case.\n\n")
        elif percentage < 60:
            f.write("The results are MIXED. Ising Fisher matrices favor q=1 in roughly half of cases.\n\n")
            f.write("**Implication:** Some graph topologies or coupling regimes may favor q=1, ")
            f.write("but this is not a universal feature of Ising Fisher matrices.\n\n")
        else:
            f.write("The Ising Fisher matrices show MODERATE EVIDENCE FOR the Lorentzian selection ")
            f.write("hypothesis in most (but not all) cases.\n\n")
            f.write("**Implication:** The specific structure of Ising Fisher matrices (covariance ")
            f.write("of spin products) may provide some bias toward q=1, though exceptions exist.\n\n")

        f.write("## Next Steps\n\n")
        f.write("- Investigate which graph properties correlate with q=1 winning\n")
        f.write("- Test larger graphs (N > 6) with sampling\n")
        f.write("- Compare to other physics models (XY model, Heisenberg model)\n")
        f.write("- Theoretical analysis: can we prove conditions under which W(q=1) dominates?\n\n")

        f.write("---\n\n")
        f.write("*Generated by spectral_gap_ising_analysis.py*\n")


if __name__ == "__main__":
    main()
