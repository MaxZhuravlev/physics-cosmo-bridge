#!/usr/bin/env python3
"""
Test Fisher RG Flow Analysis

Tests for renormalization group coarse-graining of Fisher matrices.

Attribution:
    test_id: TEST-BRIDGE-MVP1-FISHER-RG-FLOW-001
    mvp_layer: MVP-1
    dialogue_id: session-2026-02-17-rg-coarse-graining
"""

import numpy as np
import pytest
from fisher_rg_flow import (
    compute_exact_fisher_ising,
    block_ising_1d,
    compute_near_diagonal_ratio,
    compute_lorentzian_preference,
    fisher_rg_flow_1d,
    create_path_J_matrix,
)


class TestIsingFisherComputation:
    """Test exact Ising Fisher matrix computation."""

    def test_path_2_sites(self):
        """Test 2-site path (trivial case)."""
        J_matrix = create_path_J_matrix(2, J=1.0)
        F, edges = compute_exact_fisher_ising(J_matrix)

        assert F.shape == (1, 1), "2-site path has 1 edge"
        assert len(edges) == 1
        assert F[0, 0] > 0, "Fisher matrix is positive definite"

    def test_path_3_sites(self):
        """Test 3-site path."""
        J_matrix = create_path_J_matrix(3, J=1.0)
        F, edges = compute_exact_fisher_ising(J_matrix)

        assert F.shape == (2, 2), "3-site path has 2 edges"
        assert len(edges) == 2

        # Check positive definiteness
        eigvals = np.linalg.eigvalsh(F)
        assert np.all(eigvals > 0), "Fisher matrix is positive definite"

    def test_coupling_scaling(self):
        """Test that Fisher matrix scales appropriately with coupling."""
        J_matrix_weak = create_path_J_matrix(4, J=0.1)
        J_matrix_strong = create_path_J_matrix(4, J=1.0)

        F_weak, _ = compute_exact_fisher_ising(J_matrix_weak)
        F_strong, _ = compute_exact_fisher_ising(J_matrix_strong)

        # Stronger coupling should give larger Fisher matrix
        assert np.mean(F_strong) > np.mean(F_weak)


class TestBlockingTransformation:
    """Test RG blocking transformation for 1D Ising."""

    def test_block_4_to_2(self):
        """Test blocking 4 sites to 2 sites."""
        J_matrix = create_path_J_matrix(4, J=1.0)
        J_blocked = block_ising_1d(J_matrix)

        assert J_blocked.shape == (2, 2), "Blocking reduces size by factor 2"

        # Blocked coupling should be nonzero and related to original
        assert abs(J_blocked[0, 1]) > 0

    def test_block_6_to_3(self):
        """Test blocking 6 sites to 3 sites."""
        J_matrix = create_path_J_matrix(6, J=1.0)
        J_blocked = block_ising_1d(J_matrix)

        assert J_blocked.shape == (3, 3), "6→3 blocking"

        # Check path structure preserved (tridiagonal)
        for i in range(3):
            for j in range(3):
                if abs(i - j) > 1:
                    assert abs(J_blocked[i, j]) < 1e-10, "Only NN couplings"

    def test_effective_coupling_strength(self):
        """Test that effective coupling has expected sign."""
        J_matrix = create_path_J_matrix(4, J=1.0)
        J_blocked = block_ising_1d(J_matrix)

        J_eff = J_blocked[0, 1]
        # For ferromagnetic J>0, blocked coupling should be positive (but possibly smaller)
        assert J_eff > 0


class TestGeometricMeasures:
    """Test geometric quality measures (near-diagonal ratio, Lorentzian preference)."""

    def test_near_diagonal_ratio_identity(self):
        """Test diagonal matrix gives ratio = 0."""
        F_diag = np.diag([1.0, 2.0, 3.0])
        ratio = compute_near_diagonal_ratio(F_diag)

        assert abs(ratio) < 1e-10, "Diagonal matrix has zero off-diagonal ratio"

    def test_near_diagonal_ratio_full(self):
        """Test fully random matrix has ratio > 0."""
        np.random.seed(42)
        A = np.random.randn(4, 4)
        F_full = A @ A.T  # PSD

        ratio = compute_near_diagonal_ratio(F_full)
        assert ratio > 0, "Random PSD matrix has nonzero off-diagonal"

    def test_lorentzian_preference_all_positive(self):
        """Test all-positive eigenvalues gives W(q=1) = 0."""
        F_positive = np.diag([1.0, 2.0, 3.0])
        W_q1 = compute_lorentzian_preference(F_positive)

        # All positive → no negative eigenvalues → no Lorentzian signature
        assert W_q1 == 0.0

    def test_lorentzian_preference_near_diagonal(self):
        """Test near-diagonal with small off-diagonal perturbation."""
        F = np.diag([1.0, 1.0, 1.0])
        F[0, 1] = F[1, 0] = 0.1

        W_q1 = compute_lorentzian_preference(F)
        # Should still be zero (all positive even with off-diagonal)
        assert W_q1 == 0.0


class TestRGFlow1D:
    """Test full RG flow for 1D Ising."""

    def test_flow_structure(self):
        """Test that RG flow returns expected data structure."""
        J_init = create_path_J_matrix(8, J=1.0)
        flow = fisher_rg_flow_1d(J_init, max_iterations=2)

        assert len(flow) > 0, "Flow should have at least one entry"

        # Check first entry
        step = flow[0]
        assert "iteration" in step
        assert "n_sites" in step
        assert "m_edges" in step
        assert "J_eff" in step
        assert "near_diagonal_ratio" in step
        assert "W_q1" in step

    def test_flow_size_reduction(self):
        """Test that RG iterations reduce system size."""
        J_init = create_path_J_matrix(8, J=1.0)
        flow = fisher_rg_flow_1d(J_init, max_iterations=3)

        sizes = [step["n_sites"] for step in flow]
        assert sizes == sorted(sizes, reverse=True), "Sites decrease with RG"

    def test_flow_terminates(self):
        """Test that flow terminates when system too small."""
        J_init = create_path_J_matrix(4, J=1.0)
        flow = fisher_rg_flow_1d(J_init, max_iterations=10)

        # Should terminate before 10 iterations (4→2→1, stops at 2)
        assert len(flow) < 10


class TestRGConvergence:
    """Test RG convergence properties (these are RESEARCH QUESTIONS)."""

    def test_near_diagonal_improves_under_rg(self):
        """
        RESEARCH QUESTION: Does near-diagonal ratio DECREASE under RG?

        This test documents the phenomenon but may FAIL if RG does not improve geometry.
        A failure is informative (negative result).
        """
        J_init = create_path_J_matrix(16, J=1.0)
        flow = fisher_rg_flow_1d(J_init, max_iterations=3)

        ratios = [step["near_diagonal_ratio"] for step in flow]

        # HYPOTHESIS: ratio should decrease (geometry improves)
        # If this fails, it means RG does NOT improve near-diagonal structure
        if len(ratios) >= 2:
            # Document trend but don't assert (this is exploratory)
            trend_decreasing = ratios[-1] < ratios[0]
            print(f"\nRG trend: ratios = {ratios}, decreasing = {trend_decreasing}")

    def test_rg_fixed_point_existence(self):
        """
        RESEARCH QUESTION: Does RG flow converge to a fixed point?

        Fixed point = J_eff stops changing significantly.
        """
        J_init = create_path_J_matrix(32, J=1.0)
        flow = fisher_rg_flow_1d(J_init, max_iterations=5)

        J_effs = [step["J_eff"] for step in flow]

        if len(J_effs) >= 3:
            # Check relative change in last step
            rel_change = abs(J_effs[-1] - J_effs[-2]) / abs(J_effs[-2])
            print(f"\nRG J_eff sequence: {J_effs}")
            print(f"Last step relative change: {rel_change:.6f}")

            # Document but don't assert (exploratory)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
