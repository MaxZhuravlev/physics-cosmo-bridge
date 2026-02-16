#!/usr/bin/env python3
"""
Test suite for M = F² universality investigation.

Attribution:
    test_id: TEST-BRIDGE-MVP1-MF2-UNIVERSALITY-001
    mvp_layer: MVP-1
    dialogue_id: session-2026-02-17-mf2-investigation
    recovery_path: papers/structural-bridge/src/test_mf2_universality.py
    purpose: Systematically test when and why M = F² holds
"""

import pytest
import numpy as np
from mf2_universality_investigation import (
    compute_fisher_matrix,
    compute_mass_tensor,
    test_mf2_identity,
    # Model-specific functions
    rbm_model,
    gaussian_mixture_model,
    bernoulli_mixture_model,
    truncated_exponential_model,
)


class TestMF2Identity:
    """Test M = F² across different statistical model families."""

    def test_rbm_satisfies_mf2(self):
        """RBM visible marginals should satisfy M = F² (reproduce existing result)."""
        # Small RBM: 2 visible, 1 hidden
        model = rbm_model(n_visible=2, n_hidden=1, coupling=1.0, seed=42)
        F = compute_fisher_matrix(model)
        M = compute_mass_tensor(model)

        is_equal, error = test_mf2_identity(F, M)

        assert is_equal, f"RBM should satisfy M = F² but error = {error:.2e}"
        assert error < 1e-6, f"RBM M = F² error too large: {error:.2e}"

    def test_mixture_violates_mf2(self):
        """Mixture models are NOT exponential families and should violate M = F²."""
        # Mixture of 2 Gaussians
        model = gaussian_mixture_model(n_components=2, dim=2, seed=42)
        F = compute_fisher_matrix(model)
        M = compute_mass_tensor(model)

        is_equal, error = test_mf2_identity(F, M)

        # EXPECT this to FAIL (mixture ≠ exponential family)
        assert not is_equal, "Mixture should violate M = F² but it holds!"
        assert error > 1e-3, f"Mixture should have large M-F² error but got {error:.2e}"

    def test_truncated_exponential_violates_mf2(self):
        """Truncated exponential families should violate M = F²."""
        # Truncated Gaussian (exp family with support restriction)
        model = truncated_exponential_model(family='gaussian', dim=2, seed=42)
        F = compute_fisher_matrix(model)
        M = compute_mass_tensor(model)

        is_equal, error = test_mf2_identity(F, M)

        # EXPECT violation (truncation breaks exponential family)
        assert not is_equal, "Truncated model should violate M = F² but it holds!"
        assert error > 1e-3, f"Truncated model should have large error but got {error:.2e}"

    def test_bernoulli_mixture_violates_mf2(self):
        """Bernoulli mixture should violate M = F²."""
        model = bernoulli_mixture_model(n_components=2, dim=3, seed=42)
        F = compute_fisher_matrix(model)
        M = compute_mass_tensor(model)

        is_equal, error = test_mf2_identity(F, M)

        # EXPECT violation
        assert not is_equal, "Bernoulli mixture should violate M = F²"
        assert error > 1e-3, f"Bernoulli mixture should have large error but got {error:.2e}"


class TestRBMExponentialFamilyStructure:
    """Test whether RBM visible marginals ARE exponential families."""

    def test_rbm_is_curved_exponential_family(self):
        """
        Hypothesis: RBM visible marginal p(v) = exp(a^T v + sum_j log(1 + exp(b_j + W_j^T v))) / Z
        is a CURVED exponential family in parameter a.

        This would explain M = F².
        """
        # This test checks the FORM of p(v)
        model = rbm_model(n_visible=2, n_hidden=1, coupling=1.0, seed=42)

        # Check if log p(v; theta) has the form: theta^T T(v) - A(theta)
        # For RBM: theta = a (visible biases), T(v) = v (sufficient statistic)
        # A(theta) should be log Z(theta)

        # If this is exponential family, Fisher should equal Hessian of A(theta)
        # This is a STRUCTURAL test, not just M = F²

        # TODO: Implement exponential family structure check
        pytest.skip("Needs implementation: exponential family structure test")


class TestMassDefinition:
    """Test that mass tensor M is computed correctly from loss Hessian."""

    def test_mass_equals_expected_likelihood_hessian(self):
        """
        For exponential families, M should equal:
        M_ij = E_x[∂²/∂θ_i∂θ_j (-log p(x; θ))]

        For exponential family p(x) = exp(θ^T T(x) - A(θ)):
        -log p(x) = -θ^T T(x) + A(θ)
        ∂²/∂θ_i∂θ_j (-log p(x)) = ∂²A/∂θ_i∂θ_j = F_ij

        Hence M = F for exponential families.
        But we compute M = F @ F... Need to clarify definition.
        """
        pytest.skip("Need to clarify: is M = Hessian of loss, or M = F @ F?")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
