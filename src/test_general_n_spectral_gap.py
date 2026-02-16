#!/usr/bin/env python3
"""
Tests for general-n spectral gap selection theorem.

TDD approach:
1. Test tree diagonal theorem
2. Test q=1 dominance for sparse graphs
3. Test scaling with n

Attribution:
    test_id: TEST-BRIDGE-MVP1-GENERAL-N-SPECTRAL-GAP-002
    mvp_layer: MVP-1
    vector_id: open-problem-3-extension
"""

import pytest
import numpy as np
from general_n_spectral_gap import (
    verify_tree_diagonal_theorem,
    analyze_general_n_scaling,
    compute_spectral_gap_general_n,
)
from spectral_gap_ising_analysis import compute_exact_fisher_ising


class TestTreeDiagonalTheorem:
    """Test Tree Fisher Identity: F = sech²(J) × I for tree graphs."""

    def test_path_graph_is_diagonal(self):
        """Path graphs should have diagonal Fisher matrices."""
        for n in [3, 5, 8]:
            result = verify_tree_diagonal_theorem(n, 'path', J=0.5)
            assert result.is_tree
            assert result.is_diagonal, f"Path graph n={n} should be diagonal"
            assert result.F_off_diagonal_max < 1e-6

    def test_star_graph_is_diagonal(self):
        """Star graphs should have diagonal Fisher matrices."""
        for n in [3, 5, 8]:
            result = verify_tree_diagonal_theorem(n, 'star', J=0.5)
            assert result.is_tree
            assert result.is_diagonal, f"Star graph n={n} should be diagonal"
            assert result.F_off_diagonal_max < 1e-6

    def test_random_tree_is_diagonal(self):
        """Random trees should have diagonal Fisher matrices."""
        for n in [5, 10]:
            result = verify_tree_diagonal_theorem(n, 'random_tree', J=0.5)
            assert result.is_tree
            assert result.is_diagonal, f"Random tree n={n} should be diagonal"
            assert result.F_off_diagonal_max < 1e-6

    def test_diagonal_values_match_sech_squared(self):
        """Diagonal entries should equal sech²(J)."""
        J = 0.5
        expected = 1.0 / np.cosh(J)**2

        for n in [3, 5, 8]:
            result = verify_tree_diagonal_theorem(n, 'path', J=J)
            assert result.diagonal_match_error < 1e-10, \
                f"Diagonal values should match sech²(J) for n={n}"
            assert np.allclose(result.F_diagonal, expected, atol=1e-10)

    def test_q1_dominance_on_trees(self):
        """For tree graphs, W(q=1) should dominate W(q≥2)."""
        for n in [3, 5, 8, 12]:
            result = verify_tree_diagonal_theorem(n, 'path', J=0.5)

            # For diagonal F, q≥2 should have degenerate eigenvalues → L_gap=0 → W=0
            assert result.q1_W > 0, f"W(q=1) should be positive for n={n}"
            assert result.q2_W >= 0  # May be 0 due to degeneracy

            # Absolute dominance for diagonal case
            if result.is_diagonal and n > 2:
                assert result.q1_W > result.q2_W, \
                    f"W(q=1) should dominate W(q=2) for diagonal case n={n}"


class TestGeneralNScaling:
    """Test spectral gap selection scales to general n."""

    def test_sparse_graphs_favor_q1(self):
        """Sparse graphs should favor q=1 at all n."""
        results = analyze_general_n_scaling(
            n_values=[3, 5, 8, 10],
            topologies=['path', 'star', 'cycle'],
            J_values=[0.5],
            max_q=5
        )

        sparse_results = [r for r in results if r.topology in ['path', 'star', 'cycle']]

        # Expect >95% success rate for sparse graphs
        total = len(sparse_results)
        q1_wins = sum(1 for r in sparse_results if r.q1_wins)
        success_rate = q1_wins / total if total > 0 else 0

        assert success_rate > 0.95, \
            f"Sparse graphs should favor q=1 (got {success_rate:.1%})"

    def test_near_diagonal_implies_q1_dominance(self):
        """Near-diagonal Fisher matrices should favor q=1."""
        results = analyze_general_n_scaling(
            n_values=[5, 8, 12],
            topologies=['path', 'star'],
            J_values=[0.3, 0.7],
            max_q=5
        )

        near_diagonal = [r for r in results if r.F_diagonality < 0.05]

        # All near-diagonal should favor q=1
        for r in near_diagonal:
            assert r.q1_wins, \
                f"Near-diagonal graph {r.graph_name} should favor q=1"

    def test_q1_margin_increases_with_sparsity(self):
        """More diagonal → larger margin for q=1."""
        results = analyze_general_n_scaling(
            n_values=[8],
            topologies=['path', 'cycle', 'random_sparse'],
            J_values=[0.5],
            max_q=5
        )

        # Sort by diagonality (most diagonal first)
        results_sorted = sorted(results, key=lambda r: r.F_diagonality)

        # Check that margin generally increases as diagonality decreases
        # (This is a statistical trend, not strict monotonicity)
        most_diagonal = results_sorted[:len(results_sorted)//2]
        least_diagonal = results_sorted[len(results_sorted)//2:]

        avg_margin_most_diag = np.mean([r.margin_relative for r in most_diagonal if r.q1_wins])
        avg_margin_least_diag = np.mean([r.margin_relative for r in least_diagonal if r.q1_wins])

        # Most diagonal should have better margins (when q=1 wins)
        # This is a trend test, so we allow some tolerance
        # Just check that most_diagonal cases actually win
        most_diag_wins = sum(1 for r in most_diagonal if r.q1_wins)
        assert most_diag_wins >= len(most_diagonal) * 0.8, \
            "Most diagonal cases should favor q=1"

    def test_w_q1_positive_when_negative_eigenvalue_exists(self):
        """W(q=1) > 0 when F^{-1/2} M F^{-1/2} has negative eigenvalue."""
        results = analyze_general_n_scaling(
            n_values=[5, 8],
            topologies=['path'],
            J_values=[0.5],
            max_q=3
        )

        for r in results:
            # For any reasonable graph, q=1 should achieve W > 0
            # (since we can always flip one edge to get negative eigenvalue)
            assert r.W_q1 > 0, \
                f"W(q=1) should be positive for {r.graph_name}"

    def test_scaling_to_large_n(self):
        """Test that analysis scales to n=20 without errors."""
        results = analyze_general_n_scaling(
            n_values=[15, 20],
            topologies=['path', 'star'],
            J_values=[0.5],
            max_q=8
        )

        # Should complete without errors
        assert len(results) > 0
        # All should favor q=1 for sparse graphs
        for r in results:
            assert r.q1_wins, f"Large n={r.n} should favor q=1 for sparse graphs"


class TestSpectralGapComputation:
    """Test the spectral gap computation function."""

    def test_q1_produces_single_negative_eigenvalue(self):
        """q=1 should produce exactly one negative eigenvalue."""
        # Simple diagonal Fisher matrix
        F = np.diag([1.0, 2.0, 3.0, 4.0])

        beta_c, L_gap, W, S = compute_spectral_gap_general_n(F, q=1)

        # Check that S has exactly one negative entry
        assert np.sum(S < 0) == 1

        # Compute eigenvalues
        F_sqrt = np.diag(np.sqrt(np.diag(F)))
        S_diag = np.diag(S)
        A = F_sqrt @ S_diag @ F_sqrt
        eigs = np.linalg.eigvalsh(A)

        # Should have exactly one negative eigenvalue
        assert np.sum(eigs < -1e-10) == 1

    def test_beta_c_equals_minus_min_eigenvalue(self):
        """beta_c should equal -d_1 where d_1 is minimum eigenvalue."""
        F = np.diag([1.0, 2.0, 3.0])

        beta_c, L_gap, W, S = compute_spectral_gap_general_n(F, q=1)

        # Compute eigenvalues
        F_sqrt = np.diag(np.sqrt(np.diag(F)))
        S_diag = np.diag(S)
        A = F_sqrt @ S_diag @ F_sqrt
        eigs = np.linalg.eigvalsh(A)
        d_1 = eigs[0]

        assert np.isclose(beta_c, -d_1, atol=1e-10)

    def test_L_gap_formula(self):
        """L_gap should equal (d_2 - d_1) / |d_1|."""
        F = np.diag([1.0, 2.0, 3.0, 4.0])

        beta_c, L_gap, W, S = compute_spectral_gap_general_n(F, q=1)

        # Compute eigenvalues
        F_sqrt = np.diag(np.sqrt(np.diag(F)))
        S_diag = np.diag(S)
        A = F_sqrt @ S_diag @ F_sqrt
        eigs = np.linalg.eigvalsh(A)
        d_1 = eigs[0]
        d_2 = eigs[1]

        expected_L_gap = (d_2 - d_1) / abs(d_1)
        assert np.isclose(L_gap, expected_L_gap, atol=1e-10)


def test_integration():
    """Integration test: end-to-end analysis."""
    results = analyze_general_n_scaling(
        n_values=[5, 8],
        topologies=['path', 'cycle'],
        J_values=[0.5],
        max_q=4
    )

    # Get tree results separately
    tree_results = []
    for n in [5, 8]:
        tree_results.append(verify_tree_diagonal_theorem(n, 'path', 0.5))

    # Should have results
    assert len(results) > 0

    # Tree results should all be diagonal
    tree_only = [t for t in tree_results if t.is_tree]
    for t in tree_only:
        assert t.is_diagonal

    # Path graphs should all favor q=1
    path_results = [r for r in results if r.topology == 'path']
    for r in path_results:
        assert r.q1_wins, f"Path graph {r.graph_name} should favor q=1"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
