#!/usr/bin/env python3
"""
Test suite for signed metric perturbation theory.

Tests the theoretical prediction that for near-diagonal Fisher matrices F,
the signed construction g = FSF + β·F can achieve Lorentzian signature
for appropriate sign patterns S.

TDD Attribution:
    test_id: TEST-BRIDGE-MVP1-SIGNED-PERTURBATION-001
    mvp_layer: MVP-1
    vector_id: Lorentzian-mechanism-validation
    recovery_path: output/SIGNED-METRIC-PERTURBATION-THEORY.md

Author: Developer Agent (TDD)
Date: 2026-02-17
"""

import numpy as np
import pytest


class TestUniformDiagonalBase:
    """Test base case: F = c·I (uniform diagonal)."""

    def test_single_negative_sign_achieves_lorentzian(self):
        """
        For F = c·I and S = diag(+1, ..., +1, -1), verify that
        g = FSF + β·F has exactly one negative eigenvalue for -c < β < c.

        Eigenvalues of g = c²S + βcI = c(cS + βI) are:
        - c(c + β) with multiplicity m-1 (from s_i = +1)
        - c(-c + β) with multiplicity 1 (from s_i = -1)

        Lorentzian regime: -c < β < c (exactly one negative eigenvalue)
        Below β = -c: all negative eigenvalues
        Above β = c: all positive eigenvalues
        """
        c = 1.0
        m = 5
        F = c * np.eye(m)

        # Sign matrix: one negative
        S = np.diag([1, 1, 1, 1, -1])

        # Test β in Lorentzian range (-c < β < c)
        beta_values = [-0.5 * c, 0.0, 0.5 * c]

        for beta in beta_values:
            g = F @ S @ F + beta * F
            eigs = np.linalg.eigvalsh(g)

            # Count negative eigenvalues
            n_negative = np.sum(eigs < -1e-10)

            assert n_negative == 1, (
                f"Expected 1 negative eigenvalue for β={beta:.2f}, "
                f"got {n_negative}. Eigenvalues: {eigs}"
            )

    def test_critical_beta_bounds(self):
        """
        For F = c·I, S = diag(..., -1), eigenvalues of g = FSF + β·F are:
        - g = c²·S + β·c·I = c·(c·S + β·I)
        - Eigenvalues: c(c + β) (m-1 times), c(-c + β) (1 time)

        Critical betas:
        - Lower: c(-c + β) = 0 → β = -c (positive eigenvalues start)
        - Upper: c(-c + β) = 0 → β = c (negative eigenvalue crosses zero)

        Lorentzian regime: -c < β < c (exactly one negative eigenvalue)
        """
        c = 1.5
        m = 4
        F = c * np.eye(m)
        S = np.diag([1, 1, 1, -1])

        # In Lorentzian regime: exactly one negative eigenvalue
        beta = 0.5 * c
        g = F @ S @ F + beta * F
        eigs = np.linalg.eigvalsh(g)
        assert np.sum(eigs < -1e-10) == 1, "Should have exactly 1 negative eigenvalue for -c < β < c"

        # Above upper critical: all eigenvalues positive
        beta = 1.1 * c
        g = F @ S @ F + beta * F
        eigs = np.linalg.eigvalsh(g)
        assert np.all(eigs > -1e-10), "Should have no negative eigenvalues for β > c"

        # At upper critical: eigenvalue crosses zero
        beta = c
        g = F @ S @ F + beta * F
        eigs = np.linalg.eigvalsh(g)
        assert np.min(np.abs(eigs)) < 1e-10, "Should have zero eigenvalue at β = c"

        # At lower critical: eigenvalue crosses from all-negative
        beta = -c
        g = F @ S @ F + beta * F
        eigs = np.linalg.eigvalsh(g)
        assert np.min(np.abs(eigs)) < 1e-10, "Should have zero eigenvalue at β = -c"

    def test_spectral_gap_weighting(self):
        """
        For Lorentzian signature, W(q=1) = β_c × L_gap where:
        - β_c = -λ_min (critical beta at crossing)
        - L_gap = (λ_2 - λ_1) / |λ_1|

        For F = c·I, S with one negative, eigenvalues of g = c(cS + βI):
        - λ_1 = c(-c + β) (from negative sign)
        - λ_2 = c(c + β) (from positive signs)

        At β slightly below β_c = c (in Lorentzian regime):
        - λ_1 = c(-c + β) < 0 (negative)
        - λ_2 = c(c + β) > 0 (positive)
        - L_gap = (λ_2 - λ_1)/|λ_1| = [c(c+β) - c(-c+β)] / |c(c-β)|
                = 2c² / (c(c-β)) = 2c / (c-β)

        For small δ = c - β:
        - W(q=1) ≈ (c·δ) × (2c/δ) = 2c²
        """
        c = 2.0
        m = 6
        F = c * np.eye(m)
        S = np.diag([1, 1, 1, 1, 1, -1])

        # Critical beta where negative eigenvalue crosses zero
        beta_c = c

        # Compute eigenvalues at β slightly below β_c (in Lorentzian regime)
        beta = 0.99 * beta_c
        g = F @ S @ F + beta * F
        eigs = np.sort(np.linalg.eigvalsh(g))

        lambda_1 = eigs[0]  # Most negative
        lambda_2 = eigs[1]  # Second eigenvalue

        # Verify formula
        assert lambda_1 < 0, "λ_1 should be negative in Lorentzian regime"

        L_gap = (lambda_2 - lambda_1) / abs(lambda_1)
        W_q1 = (-lambda_1) * L_gap

        # Theoretical prediction: W(q=1) = 2c²
        W_theory = 2 * c**2

        np.testing.assert_allclose(W_q1, W_theory, rtol=0.05)


class TestPerturbedDiagonal:
    """Test perturbation: F = D + ε·O where D diagonal, O off-diagonal."""

    def test_perturbation_preserves_lorentzian(self):
        """
        For F = D + ε·O with D = diag(c₁, ..., c_m) and small ε,
        Lorentzian signature should persist up to critical ε.

        For D = c·I, Lorentzian regime is -c < β < c.
        We test β = 0 (middle of regime).
        """
        m = 4
        c = 1.0
        D = c * np.eye(m)

        # Off-diagonal perturbation (symmetric)
        O = np.array([
            [0, 1, 0, 0],
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 0]
        ]) * 0.1  # Path-graph coupling structure

        S = np.diag([1, 1, 1, -1])
        beta = 0.0  # Middle of Lorentzian regime for D = c·I

        # Test increasing perturbation strength
        epsilon_values = np.linspace(0, 0.5, 11)
        results = []

        for eps in epsilon_values:
            F = D + eps * O
            g = F @ S @ F + beta * F
            eigs = np.linalg.eigvalsh(g)
            n_neg = np.sum(eigs < -1e-10)
            results.append(n_neg)

        # At ε=0, should have exactly 1 negative eigenvalue
        assert results[0] == 1, "Base case should be Lorentzian"

        # For small ε, should remain Lorentzian (persistence)
        assert np.all(np.array(results[:5]) == 1), (
            "Small perturbations should preserve Lorentzian signature"
        )

    def test_critical_epsilon_scaling(self):
        """
        As ε increases, Lorentzian signature is lost when the perturbation
        disrupts the sign pattern. Critical ε should scale with diagonal strength.
        """
        m = 5

        for c in [0.5, 1.0, 2.0]:
            D = c * np.eye(m)

            # Random symmetric off-diagonal
            rng = np.random.RandomState(42)
            O = rng.randn(m, m)
            O = (O + O.T) / 2  # Symmetrize
            np.fill_diagonal(O, 0)
            O = O / np.linalg.norm(O, ord=2)  # Normalize

            S = np.diag([1, 1, 1, 1, -1])
            beta = 0.5 * c

            # Find critical epsilon via binary search
            eps_low, eps_high = 0.0, 2 * c

            for _ in range(20):
                eps_mid = (eps_low + eps_high) / 2
                F = D + eps_mid * O
                g = F @ S @ F + beta * F
                eigs = np.linalg.eigvalsh(g)
                n_neg = np.sum(eigs < -1e-10)

                if n_neg == 1:
                    eps_low = eps_mid
                else:
                    eps_high = eps_mid

            eps_critical = eps_low

            # Critical ε should be O(c) for normalized O
            assert 0.1 * c < eps_critical < 5 * c, (
                f"Critical ε={eps_critical:.3f} should scale with c={c}"
            )


class TestGeneralSignPatterns:
    """Test different sign patterns and their Lorentzian viability."""

    def test_k_negative_signs(self):
        """
        For F = c·I and k negative signs in S, the metric has signature (m-k, k).
        Only k=1 gives Lorentzian signature.
        """
        c = 1.0
        m = 6
        F = c * np.eye(m)
        beta = 0.5 * c

        for k in range(1, m):
            # Create sign pattern with k negative signs
            signs = np.ones(m)
            signs[:k] = -1
            S = np.diag(signs)

            g = F @ S @ F + beta * F
            eigs = np.linalg.eigvalsh(g)
            n_neg = np.sum(eigs < -1e-10)

            if k == 1:
                assert n_neg == 1, f"k=1 should give Lorentzian (q=1)"
            else:
                assert n_neg != 1, f"k={k} should NOT give Lorentzian"

    def test_optimal_sign_placement_for_perturbation(self):
        """
        For F = D + ε·O, placing the negative sign on the largest diagonal
        entry D_ii should maximize robustness to perturbation.
        """
        m = 4
        D = np.diag([1.0, 1.5, 2.0, 1.2])

        # Small off-diagonal coupling
        O = np.array([
            [0, 0.1, 0, 0],
            [0.1, 0, 0.1, 0],
            [0, 0.1, 0, 0.1],
            [0, 0, 0.1, 0]
        ])

        eps = 0.3
        F = D + eps * O
        beta = 1.0

        # Test all possible single-negative sign placements
        W_values = []

        for neg_idx in range(m):
            signs = np.ones(m)
            signs[neg_idx] = -1
            S = np.diag(signs)

            g = F @ S @ F + beta * F
            eigs = np.sort(np.linalg.eigvalsh(g))

            if eigs[0] < -1e-10:  # Lorentzian regime
                lambda_1, lambda_2 = eigs[0], eigs[1]
                beta_c = -lambda_1
                L_gap = (lambda_2 - lambda_1) / abs(lambda_1)
                W = beta_c * L_gap
            else:
                W = 0.0

            W_values.append(W)

        # Verify that largest diagonal entry gives largest W
        best_idx = np.argmax(W_values)
        largest_diag_idx = np.argmax(np.diag(D))

        assert best_idx == largest_diag_idx, (
            f"Expected largest diagonal entry (idx={largest_diag_idx}) to give "
            f"best W, but got idx={best_idx}"
        )


class TestTheoremStatement:
    """Test the main theorem: conditions for Lorentzian signature."""

    def test_theorem_near_diagonal(self):
        """
        THEOREM (Empirical):
        For F near-diagonal with F ≈ diag(f_1, ..., f_m),
        and S with exactly one negative sign on index i,
        the metric g = FSF + β·F has Lorentzian signature for
        β in interval approximately (-f_i, f_i).

        For diagonal F = diag(f_1, ..., f_m):
        - Eigenvalues: f_j² + β·f_j (j ≠ i), -f_i² + β·f_i (for j = i)
        - Critical β where -f_i² + β·f_i = 0: β = f_i
        - Lorentzian regime: -f_i < β < f_i

        For near-diagonal F: β_critical ≈ f_i with O(δ) corrections
        """
        # Test case: near-diagonal Fisher
        m = 5
        D = np.diag([1.2, 1.5, 1.8, 1.1, 1.4])

        # Small off-diagonal
        rng = np.random.RandomState(123)
        O = rng.randn(m, m)
        O = (O + O.T) / 2
        np.fill_diagonal(O, 0)

        # Scale to δ = 0.2
        delta = 0.2
        F = D + delta * np.linalg.norm(D, ord=2) * O / np.linalg.norm(O, ord=2)

        # Verify near-diagonality
        delta_actual = np.linalg.norm(F - np.diag(np.diag(F)), ord=2) / np.linalg.norm(np.diag(np.diag(F)), ord=2)
        assert delta_actual < 0.3, f"Should be near-diagonal, got δ={delta_actual:.3f}"

        # Place negative sign on largest diagonal entry
        largest_idx = np.argmax(np.diag(F))
        signs = np.ones(m)
        signs[largest_idx] = -1
        S = np.diag(signs)

        # Find β range that gives Lorentzian signature
        beta_candidates = np.linspace(-3, 3, 61)
        lorentzian_betas = []

        for beta in beta_candidates:
            g = F @ S @ F + beta * F
            eigs = np.linalg.eigvalsh(g)
            n_neg = np.sum(eigs < -1e-10)

            if n_neg == 1:
                lorentzian_betas.append(beta)

        # Check that Lorentzian regime exists and is non-empty
        assert len(lorentzian_betas) > 0, "Should have Lorentzian regime for near-diagonal F"

        beta_lower_actual = min(lorentzian_betas)
        beta_upper_actual = max(lorentzian_betas)

        # Theoretical prediction: For diagonal F = diag(..., f_i, ...),
        # critical β ≈ f_i (upper bound)
        # Lower bound is more complex for non-uniform diagonal
        f_i = D[largest_idx, largest_idx]  # Diagonal entry with negative sign
        beta_upper_theory = f_i

        # Check that upper bound matches (within 50% tolerance for perturbations)
        np.testing.assert_allclose(beta_upper_actual, beta_upper_theory, rtol=0.5)

        # Check that Lorentzian regime width is O(f_i)
        regime_width = beta_upper_actual - beta_lower_actual
        assert 0.5 * f_i < regime_width < 3 * f_i, (
            f"Regime width {regime_width:.3f} should be O(f_i)={f_i:.3f}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
