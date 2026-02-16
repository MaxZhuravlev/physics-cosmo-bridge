#!/usr/bin/env python3
"""
Tests for non-uniform coupling tree Fisher matrix verification.

Attribution:
    test_id: TEST-BRIDGE-MVP1-NONUNIFORM-TREE-001
    mvp_layer: MVP-1
    dialogue_id: session-2026-02-16-nonuniform-tree
"""

import numpy as np
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nonuniform_tree_verification import (
    create_tree_graph_nonuniform,
    compute_exact_fisher_ising,
    verify_diagonal_structure,
    verify_sech_squared_formula,
    is_tree_graph
)


class TestNonuniformTreeFisher:
    """Test suite for non-uniform tree Fisher matrix verification."""

    def test_path_graph_nonuniform_is_diagonal(self):
        """Path graph with non-uniform couplings should produce diagonal Fisher."""
        n = 5
        J_edges = [0.5, 1.0, 1.5, 2.0]  # 4 edges for 5-vertex path

        J_matrix = create_tree_graph_nonuniform("path", n, J_edges)
        F, edges = compute_exact_fisher_ising(J_matrix)

        # F should be diagonal
        assert verify_diagonal_structure(F), "Fisher matrix should be diagonal for tree"

    def test_star_graph_nonuniform_is_diagonal(self):
        """Star graph with non-uniform couplings should produce diagonal Fisher."""
        n = 6  # 1 center + 5 leaves
        J_edges = [0.3, 0.6, 0.9, 1.2, 1.5]  # 5 edges

        J_matrix = create_tree_graph_nonuniform("star", n, J_edges)
        F, edges = compute_exact_fisher_ising(J_matrix)

        assert verify_diagonal_structure(F), "Fisher matrix should be diagonal for tree"

    def test_random_tree_nonuniform_is_diagonal(self):
        """Random tree with non-uniform couplings should produce diagonal Fisher."""
        n = 8
        J_edges = [0.2 * (i + 1) for i in range(n - 1)]  # n-1 edges for tree

        J_matrix = create_tree_graph_nonuniform("random_tree", n, J_edges)

        # Verify it's actually a tree
        assert is_tree_graph(J_matrix), "Should generate a valid tree"

        F, edges = compute_exact_fisher_ising(J_matrix)
        assert verify_diagonal_structure(F), "Fisher matrix should be diagonal for tree"

    def test_diagonal_values_match_sech_squared(self):
        """Diagonal values should be sech²(J_e) for each edge e."""
        n = 4
        J_edges = [0.5, 1.0, 1.5]  # 3 edges

        J_matrix = create_tree_graph_nonuniform("path", n, J_edges)
        F, edges = compute_exact_fisher_ising(J_matrix)

        # Get J values in edge order
        J_values = np.array([J_matrix[u, v] for u, v in edges])

        # Verify F_ii = sech²(J_i)
        assert verify_sech_squared_formula(F, J_values), \
            "Diagonal entries should equal sech²(J_e)"

    def test_large_random_tree_batch(self):
        """Test multiple random trees with random non-uniform couplings."""
        n_tests = 10
        rng = np.random.default_rng(42)

        for _ in range(n_tests):
            n = rng.integers(5, 10)
            # Random couplings in [0.1, 2.0]
            J_edges = rng.uniform(0.1, 2.0, size=n - 1)

            J_matrix = create_tree_graph_nonuniform("random_tree", n, J_edges)

            if not is_tree_graph(J_matrix):
                continue  # Skip if not a tree

            F, edges = compute_exact_fisher_ising(J_matrix)
            J_values = np.array([J_matrix[u, v] for u, v in edges])

            assert verify_diagonal_structure(F), \
                f"Tree {_} should have diagonal Fisher"
            assert verify_sech_squared_formula(F, J_values), \
                f"Tree {_} should satisfy sech² formula"

    def test_log_normal_coupling_distribution(self):
        """Test with couplings from log-normal distribution."""
        n = 7
        rng = np.random.default_rng(123)
        J_edges = rng.lognormal(mean=0.0, sigma=0.5, size=n - 1)

        J_matrix = create_tree_graph_nonuniform("path", n, J_edges)
        F, edges = compute_exact_fisher_ising(J_matrix)
        J_values = np.array([J_matrix[u, v] for u, v in edges])

        assert verify_diagonal_structure(F)
        assert verify_sech_squared_formula(F, J_values)

    def test_extreme_coupling_values(self):
        """Test with very weak and very strong couplings."""
        n = 5
        J_edges = [0.01, 0.05, 10.0, 20.0]  # Mix of weak and strong

        J_matrix = create_tree_graph_nonuniform("path", n, J_edges)
        F, edges = compute_exact_fisher_ising(J_matrix)
        J_values = np.array([J_matrix[u, v] for u, v in edges])

        assert verify_diagonal_structure(F)
        assert verify_sech_squared_formula(F, J_values)

    def test_non_tree_fails_diagonal_check(self):
        """Cycle graph (non-tree) should NOT have diagonal Fisher."""
        n = 5
        J_edges = [1.0] * n  # n edges (creates cycle)

        J_matrix = create_tree_graph_nonuniform("cycle", n, J_edges)

        # Verify it's NOT a tree
        assert not is_tree_graph(J_matrix), "Cycle should not be a tree"

        F, edges = compute_exact_fisher_ising(J_matrix)

        # Fisher should NOT be diagonal
        assert not verify_diagonal_structure(F, tol=1e-8), \
            "Cycle graph should have non-diagonal Fisher"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
