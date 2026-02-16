#!/usr/bin/env python3
"""
Degeneracy Analysis: Why W(q=1) = W_max under H1' signed-edge construction.

RESEARCH QUESTION:
    The 240-configuration phase diagram shows W(q=1) = W(q>=2) for every
    configuration (exact tie, 0% q=1 win rate). Is this an algebraic identity
    or a numerical coincidence? What causes it? Can alternative mass tensors
    break the degeneracy?

ANALYTICAL DIAGNOSIS:
    In compute_signed_edge_spectral_gap, the code computes:
        A_H1 = F^{1/2} S F^{1/2}  (fixed, from Fiedler signs)
    Then for each q, it applies a signature matrix Sig (q entries flipped to -1):
        A_transformed = Sig * A_H1 * Sig
    and checks eigenvalues of A_transformed.

    KEY OBSERVATION: Sig is a diagonal matrix with +/-1 entries.
    Therefore Sig = Sig^T = Sig^{-1}, making Sig an orthogonal matrix.
    The transformation A -> Sig * A * Sig is a SIMILARITY transformation
    (since Sig^{-1} = Sig), which PRESERVES ALL EIGENVALUES.

    CONCLUSION: eigvalsh(Sig * A * Sig) = eigvalsh(A) for ALL Sig.
    This makes W(q) identical for all q -- an EXACT ALGEBRAIC IDENTITY,
    not a numerical coincidence.

    The degeneracy is caused by a mathematical error in the spectral gap
    computation: congruence by an orthogonal diagonal matrix is a similarity
    transform and cannot change the spectrum.

INVESTIGATION PLAN:
    1. Verify the algebraic identity numerically for small cases
    2. Show exact eigenvalue structure
    3. Test alternative mass tensor constructions that might avoid this
    4. Identify what WOULD break the degeneracy

Attribution:
    test_id: TEST-BRIDGE-MVP1-DEGENERACY-ANALYSIS-001
    dialogue_id: session-2026-02-17-degeneracy
    recovery_path: output/degeneracy_analysis_results.md
"""

import numpy as np
import itertools
import networkx as nx
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from signed_edge_phase_diagram import (
    compute_exact_fisher_ising,
    compute_fiedler_sign_assignment,
    generate_random_graph
)


# ============================================================================
# PART 1: Verify the algebraic identity (similarity invariance)
# ============================================================================

def verify_similarity_invariance(F, S_diag, verbose=True):
    """
    Verify that Sig * (F^{1/2} S F^{1/2}) * Sig has the SAME eigenvalues
    for all possible signature matrices Sig.

    This demonstrates the algebraic identity that causes the degeneracy.

    Returns:
        is_algebraic: True if degeneracy is exact (not numerical)
        max_eigenvalue_deviation: Maximum deviation across all Sig choices
    """
    m = F.shape[0]

    # Compute F^{1/2}
    vals, vecs = np.linalg.eigh(F)
    vals = np.maximum(vals, 1e-10)
    F_sqrt = vecs @ np.diag(np.sqrt(vals)) @ vecs.T

    S = np.diag(S_diag)
    A_H1 = F_sqrt @ S @ F_sqrt

    # Reference eigenvalues (no signature flip)
    eigs_ref = np.sort(np.linalg.eigvalsh(A_H1))

    max_deviation = 0.0
    all_eigs = [eigs_ref]

    # Test all possible signature matrices (2^m possibilities)
    if m <= 10:
        for bits in itertools.product([-1, 1], repeat=m):
            Sig = np.diag(np.array(bits, dtype=float))
            A_transformed = Sig @ A_H1 @ Sig
            eigs_transformed = np.sort(np.linalg.eigvalsh(A_transformed))

            deviation = np.max(np.abs(eigs_transformed - eigs_ref))
            max_deviation = max(max_deviation, deviation)
            all_eigs.append(eigs_transformed)
    else:
        # Random sampling for large m
        rng = np.random.default_rng(42)
        for _ in range(500):
            bits = rng.choice([-1.0, 1.0], size=m)
            Sig = np.diag(bits)
            A_transformed = Sig @ A_H1 @ Sig
            eigs_transformed = np.sort(np.linalg.eigvalsh(A_transformed))

            deviation = np.max(np.abs(eigs_transformed - eigs_ref))
            max_deviation = max(max_deviation, deviation)
            all_eigs.append(eigs_transformed)

    is_algebraic = max_deviation < 1e-12

    if verbose:
        print(f"  A_H1 = F^{{1/2}} S F^{{1/2}} eigenvalues: {eigs_ref}")
        print(f"  Max deviation across all Sig: {max_deviation:.2e}")
        print(f"  Degeneracy is {'EXACT (algebraic)' if is_algebraic else 'APPROXIMATE (numerical)'}")

    return is_algebraic, max_deviation, eigs_ref


def prove_similarity_algebraically(verbose=True):
    """
    Prove algebraically: for diagonal Sig with Sig^2 = I,
    the transformation A -> Sig A Sig is a similarity transform.

    Proof:
        Sig is diagonal with entries +/-1
        => Sig^T = Sig (symmetric)
        => Sig^2 = I (involution)
        => Sig^{-1} = Sig

        Therefore: Sig A Sig = Sig A Sig^{-1}
        This is a similarity transformation.

        Eigenvalues are invariant under similarity: spec(BAB^{-1}) = spec(A)

        QED: spec(Sig A Sig) = spec(A) for all diagonal Sig with +/-1 entries.
    """
    if verbose:
        print("\n" + "=" * 80)
        print("ALGEBRAIC PROOF: Sig * A * Sig preserves eigenvalues")
        print("=" * 80)
        print()
        print("  Given: Sig = diag(s_1, ..., s_m) with s_i in {+1, -1}")
        print("  Then:  Sig^T = Sig  (diagonal matrices are symmetric)")
        print("         Sig^2 = I   (s_i^2 = 1 for all i)")
        print("         Sig^{-1} = Sig")
        print()
        print("  Therefore: Sig * A * Sig = Sig * A * Sig^{-1}")
        print("  This is a SIMILARITY transformation.")
        print()
        print("  Fundamental theorem of linear algebra:")
        print("  spec(B A B^{-1}) = spec(A) for any invertible B")
        print()
        print("  CONCLUSION: spec(Sig * A * Sig) = spec(A) for ALL Sig")
        print("  => W(q) is IDENTICAL for all q")
        print("  => The degeneracy is an EXACT ALGEBRAIC IDENTITY")
        print("  => It CANNOT be broken by any choice of Sig")
        print()
        print("  ROOT CAUSE in the phase diagram code:")
        print("  Line 253: A_transformed = Sig @ A_H1 @ Sig")
        print("  This operation preserves all eigenvalues of A_H1,")
        print("  so beta_c and L_gap are q-independent.")


# ============================================================================
# PART 2: Detailed eigenvalue analysis for small cases
# ============================================================================

def analyze_eigenstructure(m, J, graph_type, seed=42, verbose=True):
    """
    For a given configuration, compute the full eigenvalue structure of
    F^{-1/2} M^{H1'} F^{-1/2} for various mass tensor constructions.

    Returns dict with eigenvalue data.
    """
    G = generate_random_graph(m, graph_type, seed)
    n_actual = G.number_of_nodes()
    m_actual = G.number_of_edges()

    if n_actual > 14 or m_actual < 3:
        if verbose:
            print(f"  Skipping: N={n_actual}, m={m_actual} (too large or too small)")
        return None

    F = compute_exact_fisher_ising(G, J)
    S_diag = compute_fiedler_sign_assignment(G)

    # Compute matrix powers
    vals, vecs = np.linalg.eigh(F)
    vals = np.maximum(vals, 1e-10)
    F_sqrt = vecs @ np.diag(np.sqrt(vals)) @ vecs.T
    F_inv_sqrt = vecs @ np.diag(1.0 / np.sqrt(vals)) @ vecs.T

    S = np.diag(S_diag)

    if verbose:
        print(f"\n  Configuration: m={m}, J={J}, {graph_type}, seed={seed}")
        print(f"  Graph: N={n_actual}, m={m_actual}")
        print(f"  Fiedler signs: {S_diag}")
        print(f"  F eigenvalues: {np.sort(vals)}")
        print(f"  Number of negative signs: {int(np.sum(S_diag < 0))}")

    # ---- A_H1 = F^{1/2} S F^{1/2} ----
    A_H1 = F_sqrt @ S @ F_sqrt
    eigs_A_H1 = np.sort(np.linalg.eigvalsh(A_H1))
    eigvals_A_H1, eigvecs_A_H1 = np.linalg.eigh(A_H1)
    sort_idx = eigvals_A_H1.argsort()
    eigvals_A_H1 = eigvals_A_H1[sort_idx]
    eigvecs_A_H1 = eigvecs_A_H1[:, sort_idx]

    if verbose:
        print(f"\n  A_H1 = F^{{1/2}} S F^{{1/2}}:")
        print(f"    Eigenvalues: {eigs_A_H1}")
        print(f"    Negative eigenvalues: {eigs_A_H1[eigs_A_H1 < -1e-10]}")
        print(f"    Positive eigenvalues: {eigs_A_H1[eigs_A_H1 > 1e-10]}")
        if len(eigs_A_H1) > 1:
            gap = eigs_A_H1[1] - eigs_A_H1[0]
            print(f"    Spectral gap (d2 - d1): {gap:.6f}")

    # ---- M_H1 = S F^2 S ----
    M_baseline = F @ F
    M_H1 = S @ M_baseline @ S

    # ---- F^{-1/2} M^{H1'} F^{-1/2} ----
    B_H1 = F_inv_sqrt @ M_H1 @ F_inv_sqrt
    eigs_B_H1 = np.sort(np.linalg.eigvalsh(B_H1))

    if verbose:
        print(f"\n  B = F^{{-1/2}} (S F^2 S) F^{{-1/2}}:")
        print(f"    Eigenvalues: {eigs_B_H1}")
        # Verify: this should equal (F^{-1/2} S F^{1/2})(F^{1/2} S F^{-1/2}) * F
        # Let's compute directly
        T = F_inv_sqrt @ S @ F_sqrt
        B_check = T @ T.T @ F  # Not quite right, let me think...
        # Actually: F^{-1/2} S F^2 S F^{-1/2} = (F^{-1/2} S F)(F S F^{-1/2})
        # = (F^{-1/2} S F)(F^{-1/2} S F)^T  [since (F^{-1/2} S F)^T = F S F^{-1/2}]
        C = F_inv_sqrt @ S @ F
        B_check2 = C @ C.T
        eigs_B_check2 = np.sort(np.linalg.eigvalsh(B_check2))
        print(f"    Check (should match): {eigs_B_check2}")
        print(f"    B = (F^{{-1/2}} S F)(F^{{-1/2}} S F)^T -- this is ALWAYS PSD!")
        print(f"    => F^{{-1/2}} (S F^2 S) F^{{-1/2}} is PSD regardless of S")

    return {
        'config': (m, J, graph_type, seed),
        'F_eigs': np.sort(vals),
        'S_diag': S_diag,
        'A_H1_eigs': eigs_A_H1,
        'B_H1_eigs': eigs_B_H1,
        'A_H1_eigvecs': eigvecs_A_H1,
        'A_H1': A_H1,
        'F': F,
        'S': S,
        'n_negative_signs': int(np.sum(S_diag < 0)),
        'has_negative_A_eig': bool(np.any(eigs_A_H1 < -1e-10)),
    }


def compute_W_for_all_q(F, S_diag, verbose=True):
    """
    Compute W(q) for all q values using the CORRECT construction from the
    phase diagram code, and show that they are all identical.

    This replicates the logic from compute_signed_edge_spectral_gap but
    with explicit tracking of why W(q) = W(q') for all q, q'.
    """
    m = F.shape[0]

    vals, vecs = np.linalg.eigh(F)
    vals = np.maximum(vals, 1e-10)
    F_sqrt = vecs @ np.diag(np.sqrt(vals)) @ vecs.T

    S = np.diag(S_diag)
    A_H1 = F_sqrt @ S @ F_sqrt

    eigs_A = np.sort(np.linalg.eigvalsh(A_H1))

    if verbose:
        print(f"\n  A_H1 eigenvalues (q-independent): {eigs_A}")

    results = {}
    for q in range(0, min(m + 1, 7)):
        best_beta_c = -1.0
        best_L_gap = 0.0

        # All signature assignments for this q
        if m <= 10:
            sign_assignments = list(itertools.combinations(range(m), q)) if q > 0 else [()]
        else:
            rng = np.random.default_rng(42 + q)
            sign_assignments = []
            for _ in range(min(500, 2**m)):
                perm = rng.permutation(m)
                sign_assignments.append(tuple(perm[:q]))

        for neg_indices in sign_assignments:
            Sig_diag = np.ones(m)
            if len(neg_indices) > 0:
                Sig_diag[list(neg_indices)] = -1.0
            Sig = np.diag(Sig_diag)

            A_transformed = Sig @ A_H1 @ Sig
            eigs = np.linalg.eigvalsh(A_transformed)
            min_eig = eigs[0]
            second_eig = eigs[1] if len(eigs) > 1 else min_eig

            if min_eig < 0:
                beta_c = -min_eig
                L_gap = (second_eig - min_eig) / abs(min_eig) if min_eig != 0 else 0.0

                if beta_c > best_beta_c:
                    best_beta_c = beta_c
                    best_L_gap = L_gap

        W = best_beta_c * best_L_gap if best_beta_c > 0 else 0.0
        results[q] = {'W': W, 'beta_c': best_beta_c, 'L_gap': best_L_gap}

        if verbose:
            print(f"  q={q}: W={W:.6f}, beta_c={best_beta_c:.6f}, L_gap={best_L_gap:.6f}")

    return results


# ============================================================================
# PART 3: Alternative mass tensor constructions
# ============================================================================

def test_alternative_constructions(m, J, graph_type, seed=42, verbose=True):
    """
    Test mass tensor constructions that might break the W(q) degeneracy.

    The degeneracy occurs because:
        W(q) depends on eigenvalues of Sig * A * Sig
        and Sig * A * Sig is similar to A (same eigenvalues).

    To break the degeneracy, we need W(q) to depend on q through
    a mechanism that is NOT a similarity transformation.

    Alternative approach: define the spectral gap directly from the
    eigenvalues of Sig * A (not Sig * A * Sig). Then Sig * A is NOT
    similar to A in general.
    """
    G = generate_random_graph(m, graph_type, seed)
    n_actual = G.number_of_nodes()
    m_actual = G.number_of_edges()

    if n_actual > 14 or m_actual < 3:
        if verbose:
            print(f"  Skipping: N={n_actual}, m={m_actual}")
        return None

    F = compute_exact_fisher_ising(G, J)
    S_diag = compute_fiedler_sign_assignment(G)

    vals, vecs = np.linalg.eigh(F)
    vals = np.maximum(vals, 1e-10)
    F_sqrt = vecs @ np.diag(np.sqrt(vals)) @ vecs.T
    F_inv_sqrt = vecs @ np.diag(1.0 / np.sqrt(vals)) @ vecs.T

    S = np.diag(S_diag)

    results = {}

    if verbose:
        print(f"\n  Config: m_target={m}, m_actual={m_actual}, J={J}, {graph_type}")
        print(f"  F eigenvalues: {np.sort(vals)}")
        print(f"  Fiedler signs: {S_diag}")
        print(f"  Number of negative signs: {int(np.sum(S_diag < 0))}")

    # ---- Construction A: M = S * F * S (linear, not quadratic) ----
    M_A = S @ F @ S
    # F^{-1/2} M F^{-1/2} = F^{-1/2} S F S F^{-1/2}
    B_A = F_inv_sqrt @ M_A @ F_inv_sqrt
    eigs_B_A = np.sort(np.linalg.eigvalsh(B_A))
    # Also: B_A = (F^{-1/2} S F^{1/2})(F^{1/2} S F^{-1/2})
    # But F^{1/2} S F^{-1/2} != (F^{-1/2} S F^{1/2})^T in general
    # So B_A is NOT guaranteed PSD

    # Test W(q) for this construction
    W_A = _compute_W_all_q(B_A, m_actual)

    results['M=SFS'] = {
        'description': 'M = S*F*S (linear)',
        'eigs': eigs_B_A,
        'has_negative': bool(np.any(eigs_B_A < -1e-10)),
        'W_by_q': W_A,
        'degeneracy_broken': _check_degeneracy_broken(W_A),
    }

    if verbose:
        print(f"\n  [A] M = S*F*S:")
        print(f"    F^{{-1/2}} M F^{{-1/2}} eigenvalues: {eigs_B_A}")
        print(f"    Has negative eig: {results['M=SFS']['has_negative']}")
        print(f"    W by q: { {q: f'{v:.6f}' for q, v in W_A.items()} }")
        print(f"    Degeneracy broken: {results['M=SFS']['degeneracy_broken']}")

    # ---- Construction B: M = S * (F + eps*I)^2 * S (regularized) ----
    for eps in [0.01, 0.1, 0.5]:
        F_reg = F + eps * np.eye(m_actual)
        M_B = S @ F_reg @ F_reg @ S
        B_B = F_inv_sqrt @ M_B @ F_inv_sqrt
        eigs_B_B = np.sort(np.linalg.eigvalsh(B_B))
        W_B = _compute_W_all_q(B_B, m_actual)

        key = f'M=S(F+{eps}I)^2S'
        results[key] = {
            'description': f'M = S*(F+{eps}I)^2*S',
            'eigs': eigs_B_B,
            'has_negative': bool(np.any(eigs_B_B < -1e-10)),
            'W_by_q': W_B,
            'degeneracy_broken': _check_degeneracy_broken(W_B),
        }

        if verbose:
            print(f"\n  [B] M = S*(F+{eps}I)^2*S:")
            print(f"    F^{{-1/2}} M F^{{-1/2}} eigenvalues: {eigs_B_B}")
            print(f"    Degeneracy broken: {results[key]['degeneracy_broken']}")

    # ---- Construction C: M = S * F^alpha * S for various alpha ----
    for alpha in [0.5, 1.0, 1.5, 3.0]:
        F_alpha = vecs @ np.diag(vals ** alpha) @ vecs.T
        M_C = S @ F_alpha @ S
        B_C = F_inv_sqrt @ M_C @ F_inv_sqrt
        eigs_B_C = np.sort(np.linalg.eigvalsh(B_C))
        W_C = _compute_W_all_q(B_C, m_actual)

        key = f'M=SF^{alpha}S'
        results[key] = {
            'description': f'M = S*F^{alpha}*S',
            'eigs': eigs_B_C,
            'has_negative': bool(np.any(eigs_B_C < -1e-10)),
            'W_by_q': W_C,
            'degeneracy_broken': _check_degeneracy_broken(W_C),
        }

        if verbose:
            print(f"\n  [C] M = S*F^{alpha}*S:")
            print(f"    F^{{-1/2}} M F^{{-1/2}} eigenvalues: {eigs_B_C}")
            print(f"    Has negative eig: {results[key]['has_negative']}")
            print(f"    Degeneracy broken: {results[key]['degeneracy_broken']}")

    # ---- Construction D: M = F * S * F (different factorization order) ----
    M_D = F @ S @ F
    B_D = F_inv_sqrt @ M_D @ F_inv_sqrt
    eigs_B_D = np.sort(np.linalg.eigvalsh(B_D))
    W_D = _compute_W_all_q(B_D, m_actual)

    results['M=FSF'] = {
        'description': 'M = F*S*F',
        'eigs': eigs_B_D,
        'has_negative': bool(np.any(eigs_B_D < -1e-10)),
        'W_by_q': W_D,
        'degeneracy_broken': _check_degeneracy_broken(W_D),
    }

    if verbose:
        print(f"\n  [D] M = F*S*F:")
        print(f"    F^{{-1/2}} M F^{{-1/2}} eigenvalues: {eigs_B_D}")
        print(f"    Note: F^{{-1/2}} (FSF) F^{{-1/2}} = F^{{1/2}} S F^{{1/2}} = A_H1 (same as original!)")
        print(f"    Has negative eig: {results['M=FSF']['has_negative']}")
        print(f"    Degeneracy broken: {results['M=FSF']['degeneracy_broken']}")

    # ---- Construction E: Use Sig*A (not Sig*A*Sig) for spectral analysis ----
    # This is NOT a similarity transform, so eigenvalues DO depend on Sig
    A_H1 = F_sqrt @ S @ F_sqrt
    W_E = {}
    for q in range(0, min(m_actual + 1, 7)):
        best_gap_ratio = 0.0
        if m_actual <= 10:
            sign_assignments = list(itertools.combinations(range(m_actual), q)) if q > 0 else [()]
        else:
            sign_assignments = [()]

        for neg_indices in sign_assignments:
            Sig_diag = np.ones(m_actual)
            if len(neg_indices) > 0:
                Sig_diag[list(neg_indices)] = -1.0
            Sig = np.diag(Sig_diag)

            # Use Sig * A (not Sig * A * Sig)
            A_mod = Sig @ A_H1
            eigs = np.sort(np.linalg.eigvalsh(A_mod))
            min_eig = eigs[0]
            if min_eig < -1e-10 and len(eigs) > 1:
                gap_ratio = (eigs[1] - eigs[0]) / abs(eigs[0])
                best_gap_ratio = max(best_gap_ratio, gap_ratio)

        W_E[q] = best_gap_ratio

    results['Sig*A_not_symmetric'] = {
        'description': 'Use Sig*A (asymmetric, eigenvalues q-dependent)',
        'W_by_q': W_E,
        'degeneracy_broken': _check_degeneracy_broken(W_E),
    }

    if verbose:
        print(f"\n  [E] Sig*A (asymmetric product):")
        print(f"    W by q: { {q: f'{v:.6f}' for q, v in W_E.items()} }")
        print(f"    Degeneracy broken: {results['Sig*A_not_symmetric']['degeneracy_broken']}")

    # ---- Construction F: Direct Lorentzian metric (q-dependent M) ----
    # Instead of applying Sig to the spectral operator, build M that
    # explicitly depends on q: M_q = sum_i sig_i * f_i * e_i e_i^T
    # where sig_i is the signature. This makes M itself q-dependent.
    eig_F, evec_F = np.linalg.eigh(F)
    W_F = {}
    for q in range(0, min(m_actual + 1, 7)):
        best_sep = 0.0
        if m_actual <= 10:
            sign_assignments = list(itertools.combinations(range(m_actual), q)) if q > 0 else [()]
        else:
            sign_assignments = [()]

        for neg_indices in sign_assignments:
            sig = np.ones(m_actual)
            if len(neg_indices) > 0:
                sig[list(neg_indices)] = -1.0

            # Construct q-dependent mass tensor in F-eigenbasis
            # M_q = sum sig_i * f_i^2 * |e_i><e_i|
            M_q = evec_F @ np.diag(sig * eig_F**2) @ evec_F.T
            # Then F^{-1/2} M_q F^{-1/2} = sum sig_i * f_i * |e_i><e_i|
            B_q = F_inv_sqrt @ M_q @ F_inv_sqrt
            eigs_Bq = np.sort(np.linalg.eigvalsh(B_q))

            if eigs_Bq[0] < -1e-10 and len(eigs_Bq) > 1:
                sep = (eigs_Bq[1] - eigs_Bq[0]) / abs(eigs_Bq[0])
                best_sep = max(best_sep, sep)

        W_F[q] = best_sep

    results['q_dependent_M'] = {
        'description': 'M_q with signature in F-eigenbasis (q-dependent M)',
        'W_by_q': W_F,
        'degeneracy_broken': _check_degeneracy_broken(W_F),
    }

    if verbose:
        print(f"\n  [F] q-dependent M in F-eigenbasis:")
        print(f"    W by q: { {q: f'{v:.6f}' for q, v in W_F.items()} }")
        print(f"    Degeneracy broken: {results['q_dependent_M']['degeneracy_broken']}")

    return results


def _compute_W_all_q(B, m):
    """
    Compute W(q) for all q for a given matrix B = F^{-1/2} M F^{-1/2}.
    Uses the same Sig*B*Sig formulation as the phase diagram code.
    """
    W_values = {}
    for q in range(0, min(m + 1, 7)):
        best_beta_c = -1.0
        best_L_gap = 0.0

        if m <= 10:
            sign_assignments = list(itertools.combinations(range(m), q)) if q > 0 else [()]
        else:
            rng = np.random.default_rng(42 + q)
            sign_assignments = []
            for _ in range(min(500, 2**m)):
                perm = rng.permutation(m)
                sign_assignments.append(tuple(perm[:q]))

        for neg_indices in sign_assignments:
            Sig_diag = np.ones(m)
            if len(neg_indices) > 0:
                Sig_diag[list(neg_indices)] = -1.0
            Sig = np.diag(Sig_diag)

            B_transformed = Sig @ B @ Sig
            eigs = np.linalg.eigvalsh(B_transformed)
            min_eig = eigs[0]
            second_eig = eigs[1] if len(eigs) > 1 else min_eig

            if min_eig < 0:
                beta_c = -min_eig
                L_gap = (second_eig - min_eig) / abs(min_eig) if min_eig != 0 else 0.0

                if beta_c > best_beta_c:
                    best_beta_c = beta_c
                    best_L_gap = L_gap

        W = best_beta_c * best_L_gap if best_beta_c > 0 else 0.0
        W_values[q] = W

    return W_values


def _check_degeneracy_broken(W_by_q):
    """Check if W(q=1) != W(q) for some q >= 2."""
    if 1 not in W_by_q:
        return False
    W1 = W_by_q[1]
    for q, W in W_by_q.items():
        if q >= 2 and abs(W - W1) > 1e-10:
            return True
    return False


# ============================================================================
# PART 4: The REAL degeneracy-breaking analysis
# ============================================================================

def analyze_correct_spectral_selection(m, J, graph_type, seed=42, verbose=True):
    """
    The CORRECT approach to spectral selection should not use Sig*A*Sig
    (which is trivially similar to A). Instead, the q-dependence should
    come from a DIFFERENT mechanism.

    This function analyzes what the correct mechanism should be.

    Physical picture:
        - The observer has m parameters (edge couplings)
        - A Lorentzian spacetime has signature (1, m-1) or (q, m-q)
        - The question: which q makes the observer's model best fit spacetime?

    Correct formulation (from Vanchurin Type II):
        - The metric on parameter space is g_mu_nu
        - For Lorentzian signature, we need g to have q negative eigenvalues
        - The spectral gap measures how "clean" the signature is
        - For M = F^2 (standard): g = F (always PSD, q=0 wins trivially)
        - For M != F^2: g can have mixed signature
        - The q that best matches the actual signature of g should win

    Key insight: the signature is a property of g = F^{-1/2} M F^{-1/2},
    not of Sig * g * Sig. The number of negative eigenvalues of g IS q.
    There is no optimization over Sig needed -- q is DETERMINED by g.
    """
    G = generate_random_graph(m, graph_type, seed)
    n_actual = G.number_of_nodes()
    m_actual = G.number_of_edges()

    if n_actual > 14 or m_actual < 3:
        return None

    F = compute_exact_fisher_ising(G, J)
    S_diag = compute_fiedler_sign_assignment(G)

    vals, vecs = np.linalg.eigh(F)
    vals = np.maximum(vals, 1e-10)
    F_sqrt = vecs @ np.diag(np.sqrt(vals)) @ vecs.T
    F_inv_sqrt = vecs @ np.diag(1.0 / np.sqrt(vals)) @ vecs.T

    S = np.diag(S_diag)

    # For different mass tensor constructions, the signature of
    # g = F^{-1/2} M F^{-1/2} directly gives q.

    constructions = {}

    # Standard: M = F^2
    M_std = F @ F
    g_std = F_inv_sqrt @ M_std @ F_inv_sqrt  # = F
    eigs_std = np.sort(np.linalg.eigvalsh(g_std))
    q_std = int(np.sum(eigs_std < -1e-10))

    constructions['M=F^2'] = {
        'eigs': eigs_std,
        'q_determined': q_std,
        'spectral_gap': eigs_std[1] - eigs_std[0] if len(eigs_std) > 1 else 0,
    }

    # H1': M = S F^2 S
    M_H1 = S @ M_std @ S
    g_H1 = F_inv_sqrt @ M_H1 @ F_inv_sqrt
    eigs_H1 = np.sort(np.linalg.eigvalsh(g_H1))
    q_H1 = int(np.sum(eigs_H1 < -1e-10))

    constructions['M=SF^2S'] = {
        'eigs': eigs_H1,
        'q_determined': q_H1,
        'spectral_gap': eigs_H1[1] - eigs_H1[0] if len(eigs_H1) > 1 else 0,
    }

    # H1' via F^{1/2} S F^{1/2}
    A_H1 = F_sqrt @ S @ F_sqrt
    eigs_A_H1 = np.sort(np.linalg.eigvalsh(A_H1))
    q_A_H1 = int(np.sum(eigs_A_H1 < -1e-10))

    constructions['A=F^{1/2}SF^{1/2}'] = {
        'eigs': eigs_A_H1,
        'q_determined': q_A_H1,
        'spectral_gap': eigs_A_H1[1] - eigs_A_H1[0] if len(eigs_A_H1) > 1 else 0,
    }

    # Linear: M = S F S
    M_lin = S @ F @ S
    g_lin = F_inv_sqrt @ M_lin @ F_inv_sqrt
    eigs_lin = np.sort(np.linalg.eigvalsh(g_lin))
    q_lin = int(np.sum(eigs_lin < -1e-10))

    constructions['M=SFS'] = {
        'eigs': eigs_lin,
        'q_determined': q_lin,
        'spectral_gap': eigs_lin[1] - eigs_lin[0] if len(eigs_lin) > 1 else 0,
    }

    # F S F
    M_FSF = F @ S @ F
    g_FSF = F_inv_sqrt @ M_FSF @ F_inv_sqrt  # = F^{1/2} S F^{1/2}
    eigs_FSF = np.sort(np.linalg.eigvalsh(g_FSF))
    q_FSF = int(np.sum(eigs_FSF < -1e-10))

    constructions['M=FSF'] = {
        'eigs': eigs_FSF,
        'q_determined': q_FSF,
        'spectral_gap': eigs_FSF[1] - eigs_FSF[0] if len(eigs_FSF) > 1 else 0,
    }

    if verbose:
        print(f"\n  Correct spectral selection (q determined by signature of g):")
        print(f"  Config: m={m_actual}, J={J}, {graph_type}")
        for name, data in constructions.items():
            print(f"    {name}: q_determined={data['q_determined']}, "
                  f"eigs={data['eigs']}, gap={data['spectral_gap']:.6f}")

    return constructions


# ============================================================================
# PART 5: The PSD obstruction for S*F^2*S
# ============================================================================

def prove_psd_obstruction(verbose=True):
    """
    Prove that F^{-1/2} (S F^2 S) F^{-1/2} is ALWAYS PSD,
    regardless of the sign matrix S.

    Proof:
        F^{-1/2} (S F^2 S) F^{-1/2}
        = F^{-1/2} S F F F^{-1/2}   ... wait, S may not commute with F

        Let's be more careful. S is diagonal, F is symmetric PD.

        F^{-1/2} S F^2 S F^{-1/2}

        Let C = F^{-1/2} S F = (product of matrices)
        Then F^{-1/2} S F^2 S F^{-1/2} = F^{-1/2} S F * F * S F^{-1/2}
                                          = C * F * S * F^{-1/2}
        Hmm, this doesn't simplify cleanly.

        Better: F^{-1/2} S F^2 S F^{-1/2} = (F^{-1/2} S F)(F S F^{-1/2})
        Note: (F S F^{-1/2})^T = F^{-1/2} S^T F^T = F^{-1/2} S F  [since S^T=S, F^T=F]
        So: F^{-1/2} S F^2 S F^{-1/2} = C C^T where C = F^{-1/2} S F

        C C^T is ALWAYS PSD (it's a Gram matrix).

        QED: F^{-1/2} (S F^2 S) F^{-1/2} >= 0 for ALL diagonal S.

        CONSEQUENCE: M = S F^2 S can NEVER produce Lorentzian signature
        through the F^{-1/2} M F^{-1/2} spectral test.
        The number of negative eigenvalues q = 0 ALWAYS.
    """
    if verbose:
        print("\n" + "=" * 80)
        print("PSD OBSTRUCTION for M = S*F^2*S")
        print("=" * 80)
        print()
        print("  Claim: F^{-1/2} (S F^2 S) F^{-1/2} is PSD for ALL diagonal S.")
        print()
        print("  Proof:")
        print("    Let C = F^{-1/2} S F")
        print("    Note: (F S F^{-1/2})^T = F^{-1/2} S F = C  [since S, F symmetric]")
        print("    Therefore:")
        print("      F^{-1/2} S F^2 S F^{-1/2}")
        print("      = (F^{-1/2} S F)(F S F^{-1/2})")
        print("      = C * C^T")
        print("    C*C^T is a Gram matrix => always PSD.")
        print()
        print("  CONSEQUENCE:")
        print("    M = S*F^2*S produces q = 0 (all positive eigenvalues)")
        print("    for ANY sign matrix S, regardless of Fiedler or other strategy.")
        print("    The H1' construction with M = S*F^2*S CANNOT produce")
        print("    Lorentzian signature through the standard spectral test.")
        print()
        print("  IMPORTANT DISTINCTION:")
        print("    The matrix A = F^{1/2} S F^{1/2} CAN have negative eigenvalues")
        print("    (this is NOT the same as F^{-1/2} M F^{-1/2}).")
        print("    The phase diagram code actually tests A = F^{1/2} S F^{1/2},")
        print("    which is the correct object. But then it applies Sig*A*Sig")
        print("    which is a similarity transform and cannot change the spectrum.")


def verify_psd_numerically(n_tests=100, verbose=True):
    """Verify PSD obstruction numerically across many random cases."""
    if verbose:
        print("\n  Numerical verification of PSD obstruction:")

    min_eig_found = float('inf')
    n_checked = 0

    for seed in range(n_tests):
        rng = np.random.default_rng(seed)
        m = rng.integers(3, 8)

        # Random PD matrix F
        A = rng.normal(size=(m, m))
        F = A @ A.T + 0.1 * np.eye(m)

        # Random sign matrix
        S_diag = rng.choice([-1.0, 1.0], size=m)
        S = np.diag(S_diag)

        # Compute F^{-1/2} S F^2 S F^{-1/2}
        vals, vecs = np.linalg.eigh(F)
        F_inv_sqrt = vecs @ np.diag(1.0 / np.sqrt(vals)) @ vecs.T
        M = S @ F @ F @ S
        B = F_inv_sqrt @ M @ F_inv_sqrt
        eigs = np.linalg.eigvalsh(B)
        min_eig = eigs[0]
        min_eig_found = min(min_eig_found, min_eig)
        n_checked += 1

    if verbose:
        print(f"    Tested {n_checked} random (F, S) pairs")
        print(f"    Minimum eigenvalue found: {min_eig_found:.2e}")
        print(f"    PSD verified: {min_eig_found > -1e-10}")

    return min_eig_found > -1e-10


# ============================================================================
# MAIN: Run all analyses and write results
# ============================================================================

def main():
    print("\n" + "=" * 80)
    print("DEGENERACY ANALYSIS: W(q=1) = W_max under H1' construction")
    print("=" * 80)

    # ========== Part 0: Algebraic proof ==========
    prove_similarity_algebraically()
    prove_psd_obstruction()

    # ========== Part 1: Verify similarity invariance numerically ==========
    print("\n" + "=" * 80)
    print("PART 1: Numerical verification of similarity invariance")
    print("=" * 80)

    test_configs = [
        (3, 0.5, 'tree', 42),
        (4, 1.0, 'sparse', 42),
        (4, 0.3, 'dense', 42),
        (5, 0.5, 'tree', 42),
        (5, 1.0, 'dense', 42),
    ]

    similarity_results = []
    for m, J, gt, seed in test_configs:
        print(f"\n  Testing m={m}, J={J}, {gt}:")
        G = generate_random_graph(m, gt, seed)
        n_actual = G.number_of_nodes()
        m_actual = G.number_of_edges()
        if n_actual > 14 or m_actual < 3:
            print(f"  Skipped (N={n_actual})")
            continue

        F = compute_exact_fisher_ising(G, J)
        S_diag = compute_fiedler_sign_assignment(G)
        is_alg, max_dev, eigs = verify_similarity_invariance(F, S_diag)
        similarity_results.append({
            'config': (m, J, gt),
            'is_algebraic': is_alg,
            'max_deviation': max_dev,
            'eigs': eigs,
        })

    # ========== Part 1b: Verify PSD numerically ==========
    print("\n" + "=" * 80)
    print("PART 1b: Numerical verification of PSD obstruction")
    print("=" * 80)
    psd_verified = verify_psd_numerically(n_tests=200)

    # ========== Part 2: Detailed eigenvalue structure ==========
    print("\n" + "=" * 80)
    print("PART 2: Detailed eigenvalue structure for small cases")
    print("=" * 80)

    eigenstructure_results = []
    for m, J, gt, seed in test_configs:
        result = analyze_eigenstructure(m, J, gt, seed)
        if result is not None:
            eigenstructure_results.append(result)

    # ========== Part 2b: W(q) for all q ==========
    print("\n" + "=" * 80)
    print("PART 2b: W(q) values for all q (showing q-independence)")
    print("=" * 80)

    W_results = []
    for m, J, gt, seed in test_configs:
        G = generate_random_graph(m, gt, seed)
        n_actual = G.number_of_nodes()
        m_actual = G.number_of_edges()
        if n_actual > 14 or m_actual < 3:
            continue
        F = compute_exact_fisher_ising(G, J)
        S_diag = compute_fiedler_sign_assignment(G)

        print(f"\n  Config: m={m}, J={J}, {gt}:")
        W_q = compute_W_for_all_q(F, S_diag)
        W_results.append({'config': (m, J, gt), 'W_by_q': W_q})

    # ========== Part 3: Alternative constructions ==========
    print("\n" + "=" * 80)
    print("PART 3: Alternative mass tensor constructions")
    print("=" * 80)

    alt_results = []
    for m, J, gt, seed in test_configs:
        result = test_alternative_constructions(m, J, gt, seed)
        if result is not None:
            alt_results.append({'config': (m, J, gt), 'constructions': result})

    # ========== Part 4: Correct spectral selection ==========
    print("\n" + "=" * 80)
    print("PART 4: Correct spectral selection (q from signature, not optimization)")
    print("=" * 80)

    spectral_results = []
    for m, J, gt, seed in test_configs:
        result = analyze_correct_spectral_selection(m, J, gt, seed)
        if result is not None:
            spectral_results.append({'config': (m, J, gt), 'constructions': result})

    # ========== Write results ==========
    print("\n" + "=" * 80)
    print("Writing results...")
    print("=" * 80)

    output_path = "/Users/Max_1/Projects/PhysicsResearch/cosmological-unification/papers/structural-bridge/output/degeneracy_analysis_results.md"
    write_results(output_path, similarity_results, psd_verified,
                  eigenstructure_results, W_results, alt_results, spectral_results)
    print(f"Results written to: {output_path}")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("1. DEGENERACY IS EXACT (algebraic identity, not numerical):")
    print("   Sig * A * Sig is a similarity transform => same eigenvalues for all q")
    print()
    print("2. ADDITIONAL OBSTRUCTION: M = S*F^2*S gives F^{-1/2}MF^{-1/2} = CC^T (PSD)")
    print("   So M = S*F^2*S NEVER produces Lorentzian regardless of S")
    print()
    print("3. F^{1/2} S F^{1/2} CAN have negative eigenvalues (Lorentzian directions)")
    print("   but the W(q) computation via Sig*A*Sig is q-independent")
    print()
    print("4. ALTERNATIVE CONSTRUCTIONS:")
    for alt in alt_results[:1]:  # Just first config
        for name, data in alt['constructions'].items():
            broken = data.get('degeneracy_broken', False)
            if broken:
                print(f"   {name}: DEGENERACY BROKEN")
            else:
                print(f"   {name}: degeneracy persists")
    print()
    print("5. CORRECT APPROACH: q is DETERMINED by the signature of g = F^{-1/2}MF^{-1/2},")
    print("   not optimized over. The Sig*A*Sig construction is fundamentally flawed.")


def write_results(output_path, similarity_results, psd_verified,
                  eigenstructure_results, W_results, alt_results, spectral_results):
    """Write comprehensive results to markdown."""

    with open(output_path, 'w') as f:
        f.write("# Degeneracy Analysis: W(q=1) = W_max under H1' Construction\n\n")
        f.write("**Generated:** 2026-02-17\n")
        f.write("**Attribution:** TEST-BRIDGE-MVP1-DEGENERACY-ANALYSIS-001\n\n")

        # ============ Executive Summary ============
        f.write("## Executive Summary\n\n")
        f.write("The 240-configuration phase diagram showed W(q=1) = W(q>=2) for every\n")
        f.write("configuration (exact tie, 0% q=1 win rate). This investigation identifies\n")
        f.write("**two independent algebraic obstructions** that explain the degeneracy.\n\n")

        f.write("### Finding 1: Similarity Invariance (W(q) is q-independent)\n\n")
        f.write("The spectral gap computation applies a signature matrix Sig to the operator:\n")
        f.write("```\n")
        f.write("A_transformed = Sig * A_H1 * Sig\n")
        f.write("```\n")
        f.write("Since Sig is diagonal with +/-1 entries, Sig^{-1} = Sig. Therefore\n")
        f.write("`Sig * A * Sig = Sig * A * Sig^{-1}` is a **similarity transformation**,\n")
        f.write("which preserves ALL eigenvalues. This makes W(q) **identical** for all q.\n\n")
        f.write("This is an **exact algebraic identity**, not a numerical coincidence.\n\n")

        f.write("### Finding 2: PSD Obstruction (M = S*F^2*S cannot produce Lorentzian)\n\n")
        f.write("For the mass tensor M = S*F^2*S:\n")
        f.write("```\n")
        f.write("F^{-1/2} (S F^2 S) F^{-1/2} = (F^{-1/2} S F)(F^{-1/2} S F)^T = C * C^T\n")
        f.write("```\n")
        f.write("This is a Gram matrix, which is **always PSD** regardless of S.\n")
        f.write(f"Numerically verified across 200 random cases: {'CONFIRMED' if psd_verified else 'FAILED'}.\n\n")

        f.write("### Finding 3: Correct Approach\n\n")
        f.write("The signature q should be **determined** by the eigenvalue structure of\n")
        f.write("g = F^{-1/2} M F^{-1/2}, not optimized over using Sig*A*Sig. The number\n")
        f.write("of negative eigenvalues of g directly gives q. No optimization needed.\n\n")

        # ============ Algebraic Proof ============
        f.write("## Algebraic Proof: Similarity Invariance\n\n")
        f.write("**Theorem.** For any symmetric matrix A and any diagonal matrix\n")
        f.write("Sig = diag(s_1, ..., s_m) with s_i in {+1, -1}:\n")
        f.write("```\n")
        f.write("spec(Sig * A * Sig) = spec(A)\n")
        f.write("```\n\n")
        f.write("**Proof.**\n")
        f.write("1. Sig is diagonal with +/-1 entries => Sig^T = Sig\n")
        f.write("2. s_i^2 = 1 for all i => Sig^2 = I\n")
        f.write("3. Therefore Sig^{-1} = Sig\n")
        f.write("4. So Sig * A * Sig = Sig * A * Sig^{-1} (similarity transform)\n")
        f.write("5. Eigenvalues are invariant under similarity: spec(BAB^{-1}) = spec(A)\n")
        f.write("6. QED\n\n")

        f.write("**Consequence for the phase diagram code:**\n")
        f.write("Line 253 of `signed_edge_phase_diagram.py`:\n")
        f.write("```python\n")
        f.write("A_transformed = Sig @ A_H1 @ Sig\n")
        f.write("```\n")
        f.write("This operation preserves eigenvalues of A_H1 for all Sig, making\n")
        f.write("beta_c and L_gap (and therefore W) q-independent.\n\n")

        # ============ PSD Obstruction ============
        f.write("## PSD Obstruction for M = S*F^2*S\n\n")
        f.write("**Theorem.** F^{-1/2} (S F^2 S) F^{-1/2} is PSD for all diagonal S.\n\n")
        f.write("**Proof.**\n")
        f.write("```\n")
        f.write("Let C = F^{-1/2} S F\n")
        f.write("Note: (F S F^{-1/2})^T = F^{-1/2} S^T F^T = F^{-1/2} S F = C\n")
        f.write("Therefore:\n")
        f.write("  F^{-1/2} S F^2 S F^{-1/2}\n")
        f.write("  = (F^{-1/2} S F)(F S F^{-1/2})\n")
        f.write("  = C * C^T\n")
        f.write("```\n")
        f.write("C*C^T is a Gram matrix and always PSD. QED.\n\n")
        f.write("**Consequence:** The construction M = S*F^2*S gives q = 0 (Riemannian)\n")
        f.write("for ALL sign matrices S. To get Lorentzian (q > 0), one must use a\n")
        f.write("different mass tensor construction.\n\n")
        f.write("**Important distinction:** F^{1/2} S F^{1/2} CAN have negative eigenvalues.\n")
        f.write("This is the correct object for testing Lorentzian signature. However,\n")
        f.write("it is NOT the same as F^{-1/2} M^{H1'} F^{-1/2}.\n\n")

        # ============ Numerical Verification ============
        f.write("## Numerical Verification\n\n")

        f.write("### Similarity Invariance\n\n")
        f.write("| m | J | Graph | Max Eigenvalue Deviation | Algebraic? |\n")
        f.write("|---|---|-------|------------------------|------------|\n")
        for r in similarity_results:
            m, J, gt = r['config']
            f.write(f"| {m} | {J} | {gt} | {r['max_deviation']:.2e} | "
                   f"{'YES' if r['is_algebraic'] else 'NO'} |\n")
        f.write("\n")

        f.write("### Eigenvalue Structure (A = F^{1/2} S F^{1/2})\n\n")
        f.write("| m | J | Graph | n_neg_signs | A eigenvalues | Has neg eig? |\n")
        f.write("|---|---|-------|------------|---------------|-------------|\n")
        for r in eigenstructure_results:
            m, J, gt, _ = r['config']
            eigs_str = ', '.join(f'{e:.4f}' for e in r['A_H1_eigs'])
            f.write(f"| {m} | {J} | {gt} | {r['n_negative_signs']} | "
                   f"[{eigs_str}] | {'YES' if r['has_negative_A_eig'] else 'NO'} |\n")
        f.write("\n")

        f.write("### W(q) Values (showing q-independence)\n\n")
        for wr in W_results:
            m, J, gt = wr['config']
            f.write(f"**Config: m={m}, J={J}, {gt}:**\n\n")
            f.write("| q | W(q) | beta_c | L_gap |\n")
            f.write("|---|------|--------|-------|\n")
            for q, data in sorted(wr['W_by_q'].items()):
                f.write(f"| {q} | {data['W']:.6f} | {data['beta_c']:.6f} | {data['L_gap']:.6f} |\n")
            f.write("\n")

        # ============ Alternative Constructions ============
        f.write("## Alternative Mass Tensor Constructions\n\n")
        f.write("Testing whether alternative constructions break the W(q) degeneracy.\n\n")

        f.write("### Summary Table\n\n")
        f.write("| Construction | Degeneracy Broken? | Has Negative Eigs? | Notes |\n")
        f.write("|-------------|-------------------|-------------------|-------|\n")

        if alt_results:
            # Use first config as representative
            for name, data in alt_results[0]['constructions'].items():
                broken = data.get('degeneracy_broken', False)
                has_neg = data.get('has_negative', 'N/A')
                desc = data.get('description', name)
                f.write(f"| {desc} | {'YES' if broken else 'NO'} | "
                       f"{has_neg} | |\n")

        f.write("\n")

        # Detailed alternative results
        for alt in alt_results:
            m, J, gt = alt['config']
            f.write(f"### Config: m={m}, J={J}, {gt}\n\n")
            for name, data in alt['constructions'].items():
                f.write(f"**{data.get('description', name)}:**\n")
                if 'eigs' in data:
                    eigs_str = ', '.join(f'{e:.6f}' for e in data['eigs'])
                    f.write(f"- Eigenvalues: [{eigs_str}]\n")
                if 'W_by_q' in data:
                    W_str = ', '.join(f'q={q}:{v:.6f}' for q, v in sorted(data['W_by_q'].items()))
                    f.write(f"- W(q): {W_str}\n")
                f.write(f"- Degeneracy broken: {data.get('degeneracy_broken', 'N/A')}\n\n")

        # ============ Correct Spectral Selection ============
        f.write("## Correct Spectral Selection\n\n")
        f.write("Instead of optimizing over Sig (which is trivially similarity-invariant),\n")
        f.write("the correct approach is to determine q from the signature of g = F^{-1/2} M F^{-1/2}.\n\n")

        f.write("| Construction | q (from eigenvalue signature) | Eigenvalues |\n")
        f.write("|-------------|------------------------------|-------------|\n")
        if spectral_results:
            for name, data in spectral_results[0]['constructions'].items():
                eigs_str = ', '.join(f'{e:.4f}' for e in data['eigs'])
                f.write(f"| {name} | {data['q_determined']} | [{eigs_str}] |\n")
        f.write("\n")

        # ============ Physical Interpretation ============
        f.write("## Physical Interpretation and Implications for Paper #1\n\n")

        f.write("### Root Cause of the Degeneracy\n\n")
        f.write("The degeneracy has **two independent causes**:\n\n")
        f.write("1. **Similarity invariance**: The Sig*A*Sig construction used to vary q\n")
        f.write("   is a similarity transformation and cannot change eigenvalues. This means\n")
        f.write("   the W(q) metric as currently defined is q-independent for ANY matrix A.\n")
        f.write("   This is a bug in the spectral gap computation, not a feature of the\n")
        f.write("   H1' construction specifically.\n\n")
        f.write("2. **PSD obstruction for S*F^2*S**: Even if the W(q) computation were fixed,\n")
        f.write("   the mass tensor M = S*F^2*S gives F^{-1/2}MF^{-1/2} = CC^T which is\n")
        f.write("   always PSD. So this specific mass tensor cannot produce Lorentzian\n")
        f.write("   signature regardless of S.\n\n")

        f.write("### What DOES Work\n\n")
        f.write("1. **F^{1/2} S F^{1/2}** (the A_H1 matrix): This CAN have negative eigenvalues\n")
        f.write("   when S has appropriate signs. The number of negative eigenvalues directly\n")
        f.write("   determines the signature. For Lorentzian, we need exactly 1 negative eigenvalue.\n\n")
        f.write("2. **M = S*F*S** (linear construction): F^{-1/2}(SFS)F^{-1/2} is NOT guaranteed\n")
        f.write("   PSD, so this construction can in principle produce Lorentzian signature.\n\n")
        f.write("3. **M = F*S*F**: F^{-1/2}(FSF)F^{-1/2} = F^{1/2} S F^{1/2}, which is the\n")
        f.write("   same as A_H1. This is the natural construction where M = F*S*F and\n")
        f.write("   the spectral test gives the correct Lorentzian signature.\n\n")

        f.write("### Implications for Paper #1\n\n")
        f.write("1. **The W(q) computation needs a different mechanism for q-dependence.**\n")
        f.write("   The Sig*A*Sig construction is fundamentally flawed because it's a similarity\n")
        f.write("   transform. The correct approach: q is determined by how many eigenvalues of\n")
        f.write("   A = F^{1/2} S F^{1/2} are negative.\n\n")
        f.write("2. **The PSD obstruction for M = S*F^2*S is a genuine negative result.**\n")
        f.write("   This should be stated clearly: the quadratic construction cannot produce\n")
        f.write("   Lorentzian signature. Only the linear constructions (M = SFS or M = FSF)\n")
        f.write("   or the direct A = F^{1/2} S F^{1/2} formulation can.\n\n")
        f.write("3. **The phrase 'beta_c > 0 but W(q=1) = W_max' is misleading.**\n")
        f.write("   It should be 'the signature of A_H1 determines q; the Sig*A*Sig\n")
        f.write("   construction adds no information because it preserves eigenvalues.'\n\n")
        f.write("4. **The Fiedler sign method result (beta_c > 0) remains valid.**\n")
        f.write("   A = F^{1/2} S F^{1/2} does have negative eigenvalues when S has\n")
        f.write("   Fiedler-based signs. The issue is only with how W(q) is defined.\n\n")

        f.write("---\n\n")
        f.write("*Generated by degeneracy_analysis.py*\n")


if __name__ == "__main__":
    main()
