#!/usr/bin/env python3
"""
Non-Uniform Tree Fisher Matrix Verification

Verifies the conjecture that for Ising models on trees with non-uniform couplings,
the Fisher matrix in edge parameterization is diagonal with F_ii = sech²(J_i).

Research Question:
    Does the Tree Fisher Identity extend to non-uniform couplings?
    Conjecture: F = diag(sech²(J_1), sech²(J_2), ..., sech²(J_m))

Method:
    1. Generate trees with non-uniform couplings
    2. Compute exact Ising Fisher matrix
    3. Verify diagonal structure
    4. Verify sech²(J_e) formula for each edge

Attribution:
    test_id: TEST-BRIDGE-MVP1-NONUNIFORM-TREE-001
    mvp_layer: MVP-1
    dialogue_id: session-2026-02-16-nonuniform-tree
"""

import numpy as np
import itertools
from typing import List, Tuple, Optional
from dataclasses import dataclass
import networkx as nx


@dataclass
class NonuniformTreeResult:
    """Results for a single non-uniform tree verification."""
    graph_type: str
    n_vertices: int
    n_edges: int
    J_values: np.ndarray
    is_tree: bool
    is_diagonal: bool
    diagonal_error: float
    sech_squared_match: bool
    sech_squared_error: float
    F_matrix: np.ndarray
    edges: List[Tuple[int, int]]


def is_tree_graph(J_matrix: np.ndarray, tol: float = 1e-10) -> bool:
    """
    Check if J_matrix represents a tree graph.

    A tree has n vertices and n-1 edges, and is connected.
    """
    n = J_matrix.shape[0]

    # Count edges
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if abs(J_matrix[i, j]) > tol:
                edges.append((i, j))

    n_edges = len(edges)

    # Tree has n-1 edges
    if n_edges != n - 1:
        return False

    # Check connectivity using BFS
    visited = set()
    queue = [0]
    visited.add(0)

    while queue:
        u = queue.pop(0)
        for i in range(n):
            if i not in visited and abs(J_matrix[u, i]) > tol:
                visited.add(i)
                queue.append(i)

    return len(visited) == n


def create_tree_graph_nonuniform(
    graph_type: str,
    n: int,
    J_edges: List[float]
) -> np.ndarray:
    """
    Create J-matrix for tree with non-uniform couplings.

    Args:
        graph_type: "path", "star", "random_tree", "cycle" (for negative tests)
        n: Number of vertices
        J_edges: List of coupling values (length should match number of edges)

    Returns:
        J_matrix: Symmetric coupling matrix
    """
    J_matrix = np.zeros((n, n))

    if graph_type == "path":
        # Path: linear chain
        assert len(J_edges) == n - 1, f"Path needs {n-1} edges, got {len(J_edges)}"
        for i in range(n - 1):
            J_matrix[i, i + 1] = J_edges[i]
            J_matrix[i + 1, i] = J_edges[i]

    elif graph_type == "star":
        # Star: central node (0) connected to all others
        assert len(J_edges) == n - 1, f"Star needs {n-1} edges, got {len(J_edges)}"
        for i in range(1, n):
            J_matrix[0, i] = J_edges[i - 1]
            J_matrix[i, 0] = J_edges[i - 1]

    elif graph_type == "random_tree":
        # Random tree using Prüfer sequence
        assert len(J_edges) == n - 1, f"Tree needs {n-1} edges, got {len(J_edges)}"

        # Generate random tree using networkx (updated API)
        rng = np.random.default_rng(hash(tuple(J_edges)) % 2**32)
        G = nx.random_labeled_tree(n, seed=int(rng.integers(0, 2**31)))

        # Assign couplings to edges
        for idx, (u, v) in enumerate(G.edges()):
            if idx < len(J_edges):
                J_matrix[u, v] = J_edges[idx]
                J_matrix[v, u] = J_edges[idx]

    elif graph_type == "cycle":
        # Cycle (NOT a tree - for negative tests)
        assert len(J_edges) == n, f"Cycle needs {n} edges, got {len(J_edges)}"
        for i in range(n - 1):
            J_matrix[i, i + 1] = J_edges[i]
            J_matrix[i + 1, i] = J_edges[i]
        # Close the cycle
        J_matrix[0, n - 1] = J_edges[-1]
        J_matrix[n - 1, 0] = J_edges[-1]

    else:
        raise ValueError(f"Unknown graph_type: {graph_type}")

    return J_matrix


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


def verify_diagonal_structure(F: np.ndarray, tol: float = 1e-9) -> bool:
    """
    Check if Fisher matrix is diagonal to within tolerance.

    Returns True if max |F_ij| for i≠j is less than tol.
    """
    m = F.shape[0]
    if m == 0:
        return True

    # Extract off-diagonal elements
    off_diag = F - np.diag(np.diag(F))
    max_off_diag = np.max(np.abs(off_diag))

    return max_off_diag < tol


def verify_sech_squared_formula(
    F: np.ndarray,
    J_values: np.ndarray,
    tol: float = 1e-9
) -> bool:
    """
    Verify that F_ii = sech²(J_i) for all i.

    Returns True if max |F_ii - sech²(J_i)| < tol.
    """
    if len(F) == 0:
        return True

    # Compute expected values: sech²(J_i) = 1/cosh²(J_i)
    expected_diag = 1.0 / np.cosh(J_values)**2

    # Extract diagonal
    actual_diag = np.diag(F)

    # Compare
    max_error = np.max(np.abs(actual_diag - expected_diag))

    return max_error < tol


def get_diagonal_error(F: np.ndarray) -> float:
    """Return max |F_ij| for i≠j."""
    if F.shape[0] == 0:
        return 0.0
    off_diag = F - np.diag(np.diag(F))
    return np.max(np.abs(off_diag))


def get_sech_squared_error(F: np.ndarray, J_values: np.ndarray) -> float:
    """Return max |F_ii - sech²(J_i)|."""
    if len(F) == 0:
        return 0.0
    expected_diag = 1.0 / np.cosh(J_values)**2
    actual_diag = np.diag(F)
    return np.max(np.abs(actual_diag - expected_diag))


def verify_tree_configuration(
    graph_type: str,
    n: int,
    J_edges: np.ndarray,
    tol: float = 1e-9
) -> NonuniformTreeResult:
    """
    Verify the Tree Fisher Identity for a single non-uniform tree configuration.

    Returns detailed results including pass/fail for both checks.
    """
    # Create graph
    J_matrix = create_tree_graph_nonuniform(graph_type, n, list(J_edges))

    # Check if it's a tree
    is_tree = is_tree_graph(J_matrix)

    # Compute Fisher matrix
    F, edges = compute_exact_fisher_ising(J_matrix)

    if len(F) == 0:
        return NonuniformTreeResult(
            graph_type=graph_type,
            n_vertices=n,
            n_edges=0,
            J_values=J_edges,
            is_tree=is_tree,
            is_diagonal=True,
            diagonal_error=0.0,
            sech_squared_match=True,
            sech_squared_error=0.0,
            F_matrix=F,
            edges=edges
        )

    # Get J values in edge order
    J_values_ordered = np.array([J_matrix[u, v] for u, v in edges])

    # Verify diagonal structure
    is_diagonal = verify_diagonal_structure(F, tol)
    diag_error = get_diagonal_error(F)

    # Verify sech² formula
    sech_match = verify_sech_squared_formula(F, J_values_ordered, tol)
    sech_error = get_sech_squared_error(F, J_values_ordered)

    return NonuniformTreeResult(
        graph_type=graph_type,
        n_vertices=n,
        n_edges=len(edges),
        J_values=J_values_ordered,
        is_tree=is_tree,
        is_diagonal=is_diagonal,
        diagonal_error=diag_error,
        sech_squared_match=sech_match,
        sech_squared_error=sech_error,
        F_matrix=F,
        edges=edges
    )


def run_comprehensive_verification(n_tests: int = 50) -> List[NonuniformTreeResult]:
    """
    Run comprehensive verification across multiple tree topologies and coupling distributions.

    Tests:
        - Path graphs with various coupling distributions
        - Star graphs with various coupling distributions
        - Random trees with various coupling distributions
        - Different coupling distributions: uniform, log-normal, exponential

    Returns:
        List of verification results
    """
    results = []
    rng = np.random.default_rng(42)

    print("=" * 80)
    print("NON-UNIFORM TREE FISHER MATRIX VERIFICATION")
    print("=" * 80)
    print()
    print(f"Running {n_tests} verification tests...")
    print()

    # Counter for test types
    test_counts = {
        "path_uniform": 0,
        "path_lognormal": 0,
        "star_uniform": 0,
        "star_lognormal": 0,
        "random_uniform": 0,
        "random_lognormal": 0,
        "random_exponential": 0,
    }

    target_per_type = n_tests // 7

    for test_type in test_counts.keys():
        for _ in range(target_per_type):
            n = rng.integers(5, 12)

            # Generate couplings based on test type
            if "uniform" in test_type:
                J_edges = rng.uniform(0.1, 2.0, size=n - 1)
            elif "lognormal" in test_type:
                J_edges = rng.lognormal(mean=0.0, sigma=0.5, size=n - 1)
            elif "exponential" in test_type:
                J_edges = rng.exponential(scale=1.0, size=n - 1)
            else:
                J_edges = rng.uniform(0.1, 2.0, size=n - 1)

            # Determine graph type
            if test_type.startswith("path"):
                graph_type = "path"
            elif test_type.startswith("star"):
                graph_type = "star"
            else:
                graph_type = "random_tree"

            result = verify_tree_configuration(graph_type, n, J_edges)
            results.append(result)

            test_counts[test_type] += 1

    return results


def print_verification_summary(results: List[NonuniformTreeResult]):
    """Print summary of verification results."""
    print()
    print("=" * 80)
    print("VERIFICATION RESULTS")
    print("=" * 80)
    print()

    # Filter to trees only
    tree_results = [r for r in results if r.is_tree]

    if not tree_results:
        print("No tree configurations tested.")
        return

    # Success metrics
    diagonal_pass = sum(1 for r in tree_results if r.is_diagonal)
    sech_pass = sum(1 for r in tree_results if r.sech_squared_match)
    both_pass = sum(1 for r in tree_results if r.is_diagonal and r.sech_squared_match)

    total = len(tree_results)

    print(f"Total tree configurations tested: {total}")
    print()
    print(f"Diagonal structure verified: {diagonal_pass}/{total} ({100*diagonal_pass/total:.1f}%)")
    print(f"Sech² formula verified: {sech_pass}/{total} ({100*sech_pass/total:.1f}%)")
    print(f"Both conditions verified: {both_pass}/{total} ({100*both_pass/total:.1f}%)")
    print()

    # Max errors
    max_diag_error = max(r.diagonal_error for r in tree_results)
    max_sech_error = max(r.sech_squared_error for r in tree_results)

    print(f"Maximum diagonal error: {max_diag_error:.2e}")
    print(f"Maximum sech² error: {max_sech_error:.2e}")
    print()

    # By graph type
    print("By graph topology:")
    for gtype in ["path", "star", "random_tree"]:
        type_results = [r for r in tree_results if r.graph_type == gtype]
        if type_results:
            type_pass = sum(1 for r in type_results if r.is_diagonal and r.sech_squared_match)
            print(f"  {gtype:15s}: {type_pass}/{len(type_results)} ({100*type_pass/len(type_results):.1f}%)")

    # Overall conclusion
    print()
    print("=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print()

    if both_pass == total:
        print("✓ CONJECTURE VERIFIED: All tree configurations satisfy:")
        print("  - F is diagonal (max off-diagonal < 1e-9)")
        print("  - F_ii = sech²(J_i) for all edges i")
        print()
        print("The Tree Fisher Identity extends to non-uniform couplings.")
    else:
        print(f"✗ CONJECTURE FAILED: {total - both_pass}/{total} configurations failed.")
        print()
        print("Counter-examples found. Investigation needed.")

    print()
    print("=" * 80)


def main():
    """Run comprehensive non-uniform tree verification."""
    results = run_comprehensive_verification(n_tests=50)

    print_verification_summary(results)

    # Write detailed results
    write_detailed_results(results)

    print()
    print(f"Detailed results written to:")
    print(f"  /Users/Max_1/Projects/PhysicsResearch/cosmological-unification/")
    print(f"  experience/insights/NONUNIFORM-TREE-VERIFICATION-2026-02-16.md")
    print()


def write_detailed_results(results: List[NonuniformTreeResult]):
    """Write detailed verification results to markdown file."""
    output_path = "/Users/Max_1/Projects/PhysicsResearch/cosmological-unification/experience/insights/NONUNIFORM-TREE-VERIFICATION-2026-02-16.md"

    tree_results = [r for r in results if r.is_tree]

    with open(output_path, "w") as f:
        f.write("# Non-Uniform Tree Fisher Matrix Verification\n\n")
        f.write("**Date:** 2026-02-16\n")
        f.write("**Attribution:** TEST-BRIDGE-MVP1-NONUNIFORM-TREE-001\n\n")

        f.write("## Conjecture\n\n")
        f.write("For an Ising model on a tree with non-uniform couplings {J_e : e ∈ E}, ")
        f.write("the Fisher matrix in edge parameterization should be:\n\n")
        f.write("```\n")
        f.write("F = diag(sech²(J_1), sech²(J_2), ..., sech²(J_m))\n")
        f.write("```\n\n")

        f.write("## Reasoning\n\n")
        f.write("On a tree, the Hamiltonian H = -Σ_e J_e σ_e decomposes into independent ")
        f.write("terms in the edge variables σ_e (no cycle constraints). Therefore each σ_e ")
        f.write("should be an independent Bernoulli with parameter depending only on J_e.\n\n")

        f.write("## Method\n\n")
        f.write("1. Generate tree graphs (paths, stars, random trees)\n")
        f.write("2. Assign non-uniform couplings from various distributions\n")
        f.write("3. Compute exact Ising Fisher matrix\n")
        f.write("4. Verify F is diagonal (max |F_ij| < 1e-9 for i≠j)\n")
        f.write("5. Verify F_ii = sech²(J_i) (max error < 1e-9)\n\n")

        f.write("## Results\n\n")

        total = len(tree_results)
        both_pass = sum(1 for r in tree_results if r.is_diagonal and r.sech_squared_match)
        max_diag_error = max(r.diagonal_error for r in tree_results) if tree_results else 0
        max_sech_error = max(r.sech_squared_error for r in tree_results) if tree_results else 0

        f.write(f"**Total configurations tested:** {total}\n")
        f.write(f"**Configurations passing both checks:** {both_pass}/{total} ({100*both_pass/total:.1f}%)\n")
        f.write(f"**Maximum diagonal error:** {max_diag_error:.2e}\n")
        f.write(f"**Maximum sech² error:** {max_sech_error:.2e}\n\n")

        # Detailed table
        f.write("### Detailed Results\n\n")
        f.write("| Graph Type | N | m | Diagonal? | Sech²? | Diag Error | Sech Error |\n")
        f.write("|------------|---|---|-----------|--------|------------|------------|\n")

        for r in tree_results:
            diag_mark = "✓" if r.is_diagonal else "✗"
            sech_mark = "✓" if r.sech_squared_match else "✗"
            f.write(f"| {r.graph_type:10s} | {r.n_vertices:2d} | {r.n_edges:2d} | "
                   f"{diag_mark:9s} | {sech_mark:6s} | {r.diagonal_error:.2e} | {r.sech_squared_error:.2e} |\n")

        # Conclusion
        f.write("\n## Conclusion\n\n")

        if both_pass == total and total > 0:
            f.write("**CONJECTURE VERIFIED** ✓\n\n")
            f.write("All tested tree configurations satisfy:\n")
            f.write("1. Fisher matrix is diagonal to machine precision\n")
            f.write("2. Diagonal entries match sech²(J_e) to machine precision\n\n")
            f.write("**Implication:** The Tree Fisher Identity (uniform case) extends ")
            f.write("naturally to non-uniform couplings. Each edge variable σ_e is ")
            f.write("independent with variance sech²(J_e), regardless of the coupling ")
            f.write("values on other edges.\n\n")
            f.write("**Next steps:**\n")
            f.write("- Formal proof of the extension\n")
            f.write("- Integration into spectral gap analysis\n")
            f.write("- Test weighted spectral gap W(q) for non-uniform case\n")
        else:
            f.write("**CONJECTURE FAILED** ✗\n\n")
            f.write(f"Found {total - both_pass} counter-examples among {total} tests.\n\n")
            f.write("Investigation needed to understand failure modes.\n")

        f.write("\n---\n\n")
        f.write("*Generated by nonuniform_tree_verification.py*\n")


if __name__ == "__main__":
    main()
