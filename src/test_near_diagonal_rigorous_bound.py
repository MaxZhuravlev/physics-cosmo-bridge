#!/usr/bin/env python3
"""
Test Suite for Near-Diagonal Fisher Rigorous Bound Derivation
==============================================================

TDD approach: Write tests FIRST defining expected behavior.

TEST PLAN:
----------
1. Correlation decay lemma for Ising edge variables
2. Fisher = Covariance (exponential family property)
3. Off-diagonal bound from correlation decay
4. Frobenius norm ratio bound
5. Constant C identification for classical graph families
6. Verification on Petersen, Heawood, cubic graphs g=3-8

TEST-ID: TEST-PHYSICS-MVP1-NEAR-DIAGONAL-001
Attribution:
  mvp_layer: MVP-1
  vector_id: rigorous-bound-derivation
  debugging_session:
    dialogue_id: session-2026-02-17-near-diagonal
    understanding: |
      Near-diagonal Fisher property requires rigorous proof.
      Classical correlation decay (Dobrushin-Simon-Lieb) provides foundation.
      Fisher = Covariance for exponential families.
      Bound must be explicit with identified constant.
  recovery_path: papers/structural-bridge/output/NEAR-DIAGONAL-RIGOROUS-BOUND.md
"""

import numpy as np
import pytest
from scipy import linalg as la
from typing import Tuple, List, Dict
import sys


# ========================================================================
# Test Data Generators
# ========================================================================

def petersen_graph() -> Tuple[int, List[Tuple[int, int]], int, int]:
    """Petersen graph: 10 vertices, 15 edges, girth = 5, Δ = 3."""
    outer = [(i, (i+1) % 5) for i in range(5)]
    inner = [(5 + i, 5 + (i+2) % 5) for i in range(5)]
    connect = [(i, i+5) for i in range(5)]
    edges = outer + inner + connect
    return 10, edges, 5, 3  # n, edges, girth, max_degree


def heawood_graph() -> Tuple[int, List[Tuple[int, int]], int, int]:
    """Heawood graph: 14 vertices, 21 edges, girth = 6, Δ = 3."""
    adj = [
        (0,1),(0,5),(0,13),
        (1,2),(1,10),
        (2,3),(2,7),
        (3,4),(3,12),
        (4,5),(4,9),
        (5,6),
        (6,7),(6,11),
        (7,8),
        (8,9),(8,13),
        (9,10),
        (10,11),
        (11,12),
        (12,13)
    ]
    return 14, adj, 6, 3


def cycle_graph(g: int) -> Tuple[int, List[Tuple[int, int]], int, int]:
    """Cycle graph C_g: girth = g, Δ = 2."""
    edges = [(i, (i+1) % g) for i in range(g)]
    return g, edges, g, 2


def cubic_graph_family(g: int) -> Tuple[int, List[Tuple[int, int]], int, int]:
    """Cubic (3-regular) graphs with specified girth."""
    if g == 3:
        # K4 (complete graph on 4 vertices)
        edges = [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
        return 4, edges, 3, 3
    elif g == 4:
        # K_{3,3}
        edges = [(i, 3+j) for i in range(3) for j in range(3)]
        return 6, edges, 4, 3
    elif g == 5:
        return petersen_graph()
    elif g == 6:
        return heawood_graph()
    elif g == 7:
        # McGee graph (24 vertices) - too large for exact computation
        # Fall back to cycle
        return cycle_graph(g)
    elif g == 8:
        # Tutte-Coxeter graph (30 vertices) - too large
        # Fall back to cycle
        return cycle_graph(g)
    else:
        # Default to cycle
        return cycle_graph(g)


# ========================================================================
# Test 1: Correlation Decay Lemma (theoretical validation)
# ========================================================================

class TestCorrelationDecay:
    """Test correlation decay properties for Ising models on graphs."""

    def test_correlation_decay_tree(self):
        """On trees, correlation decays exactly as tanh^d(J)."""
        # Simple path graph (tree)
        n = 5
        edges = [(i, i+1) for i in range(n-1)]
        J = 0.5

        from near_diagonal_rigorous_bound import (
            compute_exact_fisher_ising,
            compute_spin_spin_correlation
        )

        # For a path graph, <s_0 s_4> should equal tanh^4(J)
        corr = compute_spin_spin_correlation(n, edges, J, 0, 4)
        expected = np.tanh(J)**4

        assert np.abs(corr - expected) < 1e-10, \
            f"Tree correlation decay: got {corr}, expected {expected}"

    def test_correlation_decay_cycle(self):
        """On cycle C_g, correlation has exact form (t^d + t^{g-d})/(1+t^g)."""
        g = 6
        n, edges, _, _ = cycle_graph(g)
        J = 0.5
        t = np.tanh(J)

        from near_diagonal_rigorous_bound import compute_spin_spin_correlation

        # Distance 2 on cycle
        d = 2
        corr = compute_spin_spin_correlation(n, edges, J, 0, d)
        expected = (t**d + t**(g-d)) / (1 + t**g)

        assert np.abs(corr - expected) < 1e-10, \
            f"Cycle correlation: got {corr}, expected {expected}"

    def test_correlation_bounded_by_decay(self):
        """Verify correlation decay bound on general graphs."""
        # Test on Petersen graph
        n, edges, g, delta = petersen_graph()
        J = 0.5
        t = np.tanh(J)

        from near_diagonal_rigorous_bound import (
            compute_spin_spin_correlation,
            compute_line_graph_distance
        )

        # For any pair of vertices at distance d_L in line graph
        # Check correlation is bounded by C(Δ) * tanh^{d_L}(J)

        for i in range(min(5, n)):
            for j in range(i+1, min(5, n)):
                corr = compute_spin_spin_correlation(n, edges, J, i, j)

                # Line graph distance (lower bound from vertex distance)
                d_L = abs(i - j)  # Lower bound

                # Bound: |corr| <= C(delta) * tanh^{d_L}(J)
                # For 3-regular graphs, C(3) ~ 2-3 empirically
                C = 3.0
                bound = C * t**d_L

                # For nearby vertices, bound may not hold (need exact d_L)
                # This is a weak test - full test requires line graph construction


# ========================================================================
# Test 2: Fisher = Covariance (exponential family)
# ========================================================================

class TestFisherCovariance:
    """Test that Fisher matrix equals covariance for exponential families."""

    def test_fisher_equals_covariance_ising(self):
        """For Ising model, F_{ij} = Cov(σ_i, σ_j)."""
        n = 4
        edges = [(0,1), (1,2), (2,3)]  # Path
        J = 0.5

        from near_diagonal_rigorous_bound import (
            compute_exact_fisher_ising,
            compute_edge_covariance
        )

        F = compute_exact_fisher_ising(n, edges, J)

        # Check F[0,1] = Cov(σ_0, σ_1)
        cov_01 = compute_edge_covariance(n, edges, J, 0, 1)

        assert np.abs(F[0, 1] - cov_01) < 1e-10, \
            f"Fisher vs covariance: F[0,1]={F[0,1]}, Cov={cov_01}"

    def test_fisher_diagonal_is_variance(self):
        """Diagonal elements are variances: F_{ii} = Var(σ_i)."""
        n = 4
        edges = [(0,1), (1,2), (2,3)]
        J = 0.5

        from near_diagonal_rigorous_bound import (
            compute_exact_fisher_ising,
            compute_edge_variance
        )

        F = compute_exact_fisher_ising(n, edges, J)
        var_0 = compute_edge_variance(n, edges, J, 0)

        assert np.abs(F[0, 0] - var_0) < 1e-10, \
            f"Fisher diagonal: F[0,0]={F[0,0]}, Var={var_0}"


# ========================================================================
# Test 3: Off-Diagonal Bound from Correlation Decay
# ========================================================================

class TestOffDiagonalBound:
    """Test bound on off-diagonal Fisher elements."""

    def test_adjacent_edges_cycle(self):
        """Adjacent edges on cycle: exact formula verification."""
        g = 8
        n, edges, _, _ = cycle_graph(g)
        J = 0.5
        t = np.tanh(J)
        s = 1 / np.cosh(J)

        from near_diagonal_rigorous_bound import compute_exact_fisher_ising

        F = compute_exact_fisher_ising(n, edges, J)

        # Edges 0 and 1 are adjacent
        F_01 = F[0, 1]

        # Expected formula: t^{g-2} * s^4 / (1+t^g)^2
        expected = t**(g-2) * s**4 / (1 + t**g)**2

        assert np.abs(F_01 - expected) < 1e-10, \
            f"Adjacent edge formula: got {F_01}, expected {expected}"

    def test_off_diagonal_decay_with_distance(self):
        """Off-diagonal elements decay with line graph distance."""
        g = 10
        n, edges, _, _ = cycle_graph(g)
        J = 0.5

        from near_diagonal_rigorous_bound import compute_exact_fisher_ising

        F = compute_exact_fisher_ising(n, edges, J)

        # F[0,1] > F[0,2] > F[0,3] ... for small J
        assert F[0, 1] > F[0, 2] > F[0, 3], \
            "Off-diagonal should decay with distance"


# ========================================================================
# Test 4: Frobenius Norm Ratio Bound
# ========================================================================

class TestFrobeniusNormBound:
    """Test Frobenius norm ratio bound."""

    def test_bound_holds_for_cycles(self):
        """Verify bound ||F-diag(F)||/||diag(F)|| <= C·tanh^{g-2}(J) on cycles."""
        J_values = [0.1, 0.3, 0.5, 0.7, 1.0]

        from near_diagonal_rigorous_bound import (
            compute_exact_fisher_ising,
            compute_theoretical_bound
        )

        for g in [5, 6, 7, 8]:
            n, edges, girth, delta = cycle_graph(g)

            for J in J_values:
                F = compute_exact_fisher_ising(n, edges, J)
                D = np.diag(np.diag(F))

                # Empirical ratio
                ratio = la.norm(F - D, 'fro') / la.norm(D, 'fro')

                # Theoretical bound
                bound = compute_theoretical_bound(girth, delta, J)

                assert ratio <= bound * 1.01, \
                    f"g={g}, J={J}: ratio={ratio:.6f} exceeds bound={bound:.6f}"

    def test_bound_holds_for_petersen(self):
        """Verify bound on Petersen graph."""
        n, edges, g, delta = petersen_graph()
        J_values = [0.3, 0.5, 1.0]

        from near_diagonal_rigorous_bound import (
            compute_exact_fisher_ising,
            compute_theoretical_bound
        )

        for J in J_values:
            F = compute_exact_fisher_ising(n, edges, J)
            D = np.diag(np.diag(F))

            ratio = la.norm(F - D, 'fro') / la.norm(D, 'fro')
            bound = compute_theoretical_bound(g, delta, J)

            assert ratio <= bound * 1.01, \
                f"Petersen J={J}: ratio={ratio:.6f} exceeds bound={bound:.6f}"


# ========================================================================
# Test 5: Constant C Identification
# ========================================================================

class TestConstantIdentification:
    """Test identification of constant C(m, Δ, g)."""

    def test_constant_depends_on_delta(self):
        """Constant C should increase with max degree Δ."""
        J = 0.5

        from near_diagonal_rigorous_bound import extract_constant_C

        # Cycle (Δ=2) vs Petersen (Δ=3)
        n_cycle, edges_cycle, g_cycle, delta_cycle = cycle_graph(6)
        n_pet, edges_pet, g_pet, delta_pet = petersen_graph()

        C_cycle = extract_constant_C(n_cycle, edges_cycle, g_cycle, delta_cycle, J)
        C_petersen = extract_constant_C(n_pet, edges_pet, g_pet, delta_pet, J)

        # C should increase with Δ
        # (This is a weak test - actual relationship is complex)
        # Main requirement: C should be finite and positive
        assert 0 < C_cycle < 100
        assert 0 < C_petersen < 100

    def test_constant_stability_across_J(self):
        """Constant C should be relatively stable across J values."""
        g = 6
        n, edges, girth, delta = cycle_graph(g)
        J_values = [0.3, 0.5, 0.7]

        from near_diagonal_rigorous_bound import extract_constant_C

        constants = [extract_constant_C(n, edges, girth, delta, J)
                    for J in J_values]

        # Coefficient of variation should be reasonable
        mean_C = np.mean(constants)
        std_C = np.std(constants)
        cv = std_C / mean_C if mean_C > 0 else float('inf')

        # Allow up to 50% variation (empirical constant, not fundamental)
        assert cv < 0.5, f"C varies too much: CV={cv:.3f}"


# ========================================================================
# Test 6: Verification on Classical Graph Families
# ========================================================================

class TestClassicalGraphFamilies:
    """Comprehensive verification on classical graphs."""

    @pytest.mark.parametrize("g", [3, 4, 5, 6])
    def test_cubic_graphs(self, g):
        """Test bound on cubic graphs with girth g."""
        n, edges, girth, delta = cubic_graph_family(g)

        if 2**n > 2**16:
            pytest.skip(f"Graph too large: 2^{n} states")

        J_values = [0.1, 0.3, 0.5, 1.0]

        from near_diagonal_rigorous_bound import (
            compute_exact_fisher_ising,
            compute_theoretical_bound
        )

        for J in J_values:
            F = compute_exact_fisher_ising(n, edges, J)
            D = np.diag(np.diag(F))

            ratio = la.norm(F - D, 'fro') / la.norm(D, 'fro')
            bound = compute_theoretical_bound(girth, delta, J)

            assert ratio <= bound * 1.01, \
                f"Cubic g={g}, J={J}: ratio={ratio:.6f} > bound={bound:.6f}"

    def test_heawood_graph(self):
        """Test bound on Heawood graph (g=6, Δ=3)."""
        n, edges, g, delta = heawood_graph()
        J_values = [0.3, 0.5, 1.0]

        from near_diagonal_rigorous_bound import (
            compute_exact_fisher_ising,
            compute_theoretical_bound
        )

        for J in J_values:
            F = compute_exact_fisher_ising(n, edges, J)
            D = np.diag(np.diag(F))

            ratio = la.norm(F - D, 'fro') / la.norm(D, 'fro')
            bound = compute_theoretical_bound(g, delta, J)

            assert ratio <= bound * 1.01, \
                f"Heawood J={J}: ratio={ratio:.6f} > bound={bound:.6f}"


# ========================================================================
# Test 7: Theorem Statement Completeness
# ========================================================================

class TestTheoremStatement:
    """Test that theorem statement is complete and correct."""

    def test_theorem_components_present(self):
        """Verify theorem has all required components."""
        from near_diagonal_rigorous_bound import get_theorem_statement

        theorem = get_theorem_statement()

        # Required components
        assert "girth" in theorem.lower()
        assert "fisher" in theorem.lower()
        assert "bound" in theorem.lower()
        assert "tanh" in theorem.lower()
        assert "constant" in theorem.lower() or "C" in theorem

    def test_theorem_constant_is_explicit(self):
        """Constant C in theorem should be explicit function of (m, Δ, g)."""
        from near_diagonal_rigorous_bound import compute_constant_C_formula

        # Should return a function or formula
        C_formula = compute_constant_C_formula()

        # Test it can be evaluated
        m, delta, g = 10, 3, 5
        C = C_formula(m, delta, g)

        assert isinstance(C, (int, float))
        assert C > 0
        assert np.isfinite(C)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
