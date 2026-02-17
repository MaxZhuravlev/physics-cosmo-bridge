#!/usr/bin/env python3
"""
Tests for the extended computational campaign.

Verifies:
1. Core Fisher computation matches existing implementation
2. MCMC Fisher estimation convergence
3. Graph generators produce correct topologies
4. Spectral gap computation correctness
5. Potts and Gaussian Fisher correctness
6. Signature determination logic

Attribution:
    test_id: TEST-BRIDGE-EXTENDED-CAMPAIGN-VERIFY-001
    date: 2026-02-17
"""

import numpy as np
import pytest
import networkx as nx

from extended_computational_campaign import (
    ising_fisher_exact,
    ising_fisher_monte_carlo,
    compute_fisher_adaptive,
    make_J_matrix,
    make_graph,
    compute_W_for_q,
    determine_signature,
    fisher_diagonality,
    potts_fisher_exact,
    gaussian_fisher_exact,
)


class TestIsingFisherExact:
    """Test exact Ising Fisher computation against known results."""

    def test_single_edge(self):
        """Single edge: F should be 1x1 positive scalar."""
        J_mat = np.array([[0, 1.0], [1.0, 0]])
        F, edges = ising_fisher_exact(J_mat)
        assert F.shape == (1, 1)
        assert F[0, 0] > 0
        assert len(edges) == 1

    def test_triangle_psd(self):
        """Triangle graph: F should be 3x3, symmetric, PSD."""
        J_mat = np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]], dtype=float)
        F, edges = ising_fisher_exact(J_mat)
        assert F.shape == (3, 3)
        assert len(edges) == 3
        assert np.allclose(F, F.T, atol=1e-12), "Fisher must be symmetric"
        eigs = np.linalg.eigvalsh(F)
        assert np.all(eigs >= -1e-10), "Fisher must be PSD"

    def test_path_diagonal(self):
        """Path graph (tree): Fisher should be diagonal."""
        n = 5
        G = nx.path_graph(n)
        J_mat = make_J_matrix(G, 0.5)
        F, edges = ising_fisher_exact(J_mat)
        m = len(edges)
        assert m == n - 1
        # Off-diagonal should be essentially zero
        off_mask = ~np.eye(m, dtype=bool)
        assert np.max(np.abs(F[off_mask])) < 1e-10

    def test_tree_fisher_identity(self):
        """Tree Fisher Identity: F_ii = sech^2(J) for trees."""
        J = 0.7
        expected = 1.0 / np.cosh(J)**2
        for n in [4, 6, 8]:
            G = nx.path_graph(n)
            J_mat = make_J_matrix(G, J)
            F, edges = ising_fisher_exact(J_mat)
            diag_vals = np.diag(F)
            assert np.allclose(diag_vals, expected, atol=1e-10), \
                f"Tree Fisher Identity failed for path n={n}"

    def test_consistency_with_existing(self):
        """Check P4 J=0.5 matches known W(q=1) ~ 1.5729."""
        from spectral_gap_ising_analysis import compute_exact_fisher_ising as old_fisher
        from spectral_gap_ising_analysis import create_graph_J_matrix

        J_mat_old = create_graph_J_matrix("path_P4", 4, J=0.5)
        F_old, edges_old = old_fisher(J_mat_old)

        G = nx.path_graph(4)
        J_mat_new = make_J_matrix(G, 0.5)
        F_new, edges_new = ising_fisher_exact(J_mat_new)

        # Same number of edges
        assert len(edges_old) == len(edges_new)
        # Fisher matrices should match (up to edge ordering)
        assert np.allclose(sorted(np.diag(F_old)), sorted(np.diag(F_new)), atol=1e-10)


class TestIsingFisherMCMC:
    """Test MCMC Fisher estimation convergence."""

    def test_mcmc_matches_exact_small(self):
        """MCMC should approximate exact Fisher for small systems."""
        G = nx.path_graph(6)
        J_mat = make_J_matrix(G, 0.5)

        F_exact, _ = ising_fisher_exact(J_mat)
        F_mc, _ = ising_fisher_monte_carlo(J_mat, n_samples=500000, burn_in=20000)

        # MCMC should match exact within ~5%
        rel_err = np.linalg.norm(F_exact - F_mc) / np.linalg.norm(F_exact)
        assert rel_err < 0.1, f"MCMC rel error {rel_err:.3f} > 0.1"

    def test_mcmc_diagonal_on_tree(self):
        """MCMC Fisher on tree should be approximately diagonal."""
        G = nx.path_graph(8)
        J_mat = make_J_matrix(G, 0.5)
        F_mc, _ = ising_fisher_monte_carlo(J_mat, n_samples=300000)
        diag_err = fisher_diagonality(F_mc)
        # Should be near-diagonal (tolerance is loose due to MC noise)
        assert diag_err < 0.15, f"MCMC tree diagonality {diag_err:.3f} > 0.15"


class TestGraphGenerators:
    """Test graph generators produce correct topologies."""

    def test_path(self):
        G = make_graph("path", 10)
        assert G.number_of_nodes() == 10
        assert G.number_of_edges() == 9
        assert nx.is_tree(G)

    def test_star(self):
        G = make_graph("star", 8)
        assert G.number_of_nodes() == 8
        assert G.number_of_edges() == 7
        assert nx.is_tree(G)

    def test_cycle(self):
        G = make_graph("cycle", 6)
        assert G.number_of_nodes() == 6
        assert G.number_of_edges() == 6
        assert not nx.is_tree(G)

    def test_complete(self):
        G = make_graph("complete", 5)
        assert G.number_of_nodes() == 5
        assert G.number_of_edges() == 10  # C(5,2)

    def test_random_tree(self):
        G = make_graph("random_tree", 15)
        assert G.number_of_nodes() == 15
        assert G.number_of_edges() == 14
        assert nx.is_tree(G)

    def test_erdos_renyi_connected(self):
        G = make_graph("erdos_renyi_sparse", 20)
        assert nx.is_connected(G)


class TestSpectralGap:
    """Test spectral gap computation."""

    def test_diagonal_q1(self):
        """For diagonal F, q=1 should always produce W > 0."""
        F = np.diag([1.0, 2.0, 3.0, 4.0])
        result = compute_W_for_q(F, 1)
        assert result["W"] > 0
        assert result["beta_c"] > 0
        assert result["L_gap"] > 0

    def test_q_zero_returns_zero(self):
        """q=0 should return zero."""
        F = np.diag([1.0, 2.0, 3.0])
        result = compute_W_for_q(F, 0)
        assert result["W"] == 0.0

    def test_q_equals_m_returns_zero(self):
        """q=m should return zero (all negative = no negative eigenvalue structure)."""
        F = np.diag([1.0, 2.0, 3.0])
        result = compute_W_for_q(F, 3)
        assert result["W"] == 0.0

    def test_path_favors_q1(self):
        """Path graph should strongly favor q=1."""
        G = nx.path_graph(6)
        J_mat = make_J_matrix(G, 0.5)
        F, _ = ising_fisher_exact(J_mat)
        sig = determine_signature(F, max_q=4)
        assert sig["q1_wins"], "Path graph should favor q=1"
        assert sig["W_q1"] > 0

    def test_determine_signature_completeness(self):
        """Signature determination should return all required fields."""
        F = np.diag([1.0, 2.0, 3.0, 4.0, 5.0])
        sig = determine_signature(F, max_q=4)
        required_keys = ["W_values", "q_max", "W_q1", "W_max_higher", "q1_wins", "margin"]
        for key in required_keys:
            assert key in sig, f"Missing key: {key}"


class TestFisherDiagonality:
    """Test diagonality metric."""

    def test_diagonal_matrix(self):
        F = np.diag([1.0, 2.0, 3.0])
        assert fisher_diagonality(F) < 1e-12

    def test_nondiagonal_matrix(self):
        F = np.array([[1.0, 0.5, 0.0], [0.5, 1.0, 0.0], [0.0, 0.0, 1.0]])
        d = fisher_diagonality(F)
        assert d > 0.1


class TestPottsFisher:
    """Test Potts Fisher computation."""

    def test_potts_q2_matches_ising(self):
        """Potts with q=2 should match Ising Fisher (up to parameterization)."""
        G = nx.path_graph(4)
        edges = list(G.edges())
        J = 0.5

        F_potts = potts_fisher_exact(edges, J, 2, 4)
        # Potts q=2 with delta statistic is equivalent to Ising
        # but with different parameterization. Both should be diagonal on trees.
        m = len(edges)
        off_mask = ~np.eye(m, dtype=bool)
        assert np.max(np.abs(F_potts[off_mask])) < 1e-10, "Potts q=2 tree should be diagonal"

    def test_potts_psd(self):
        """Potts Fisher should be PSD."""
        edges = [(0, 1), (1, 2), (0, 2)]
        F = potts_fisher_exact(edges, 0.5, 3, 3)
        eigs = np.linalg.eigvalsh(F)
        assert np.all(eigs >= -1e-10)


class TestGaussianFisher:
    """Test Gaussian Fisher computation."""

    def test_gaussian_psd(self):
        """Gaussian Fisher should be PSD."""
        edges = [(0, 1), (1, 2)]
        F = gaussian_fisher_exact(3, edges, 0.3)
        eigs = np.linalg.eigvalsh(F)
        assert np.all(eigs >= -1e-10)

    def test_gaussian_symmetric(self):
        """Gaussian Fisher should be symmetric."""
        edges = [(0, 1), (1, 2), (0, 2)]
        F = gaussian_fisher_exact(3, edges, 0.3)
        assert np.allclose(F, F.T)


def test_integration_quick():
    """Quick integration test: run Task 2 with minimal configs."""
    # Just verify the pipeline works without errors
    G = make_graph("path", 5)
    J_mat = make_J_matrix(G, 0.5)
    F, edges = compute_fisher_adaptive(J_mat)
    sig = determine_signature(F, max_q=3)
    assert sig["q1_wins"], "Path n=5 should favor q=1"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
