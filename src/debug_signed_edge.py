#!/usr/bin/env python3
"""
Debug signed-edge H1' construction.
Investigate why Fiedler method gives 0% Lorentzian rate.
"""

import numpy as np
import networkx as nx
from signed_edge_phase_diagram import (
    compute_exact_fisher_ising,
    compute_fiedler_sign_assignment,
    generate_random_graph
)


def debug_single_case(m: int, J: float, graph_type: str, seed: int = 42):
    """Debug single configuration."""

    print(f"\n{'='*80}")
    print(f"DEBUGGING: m={m}, J={J}, graph_type={graph_type}, seed={seed}")
    print(f"{'='*80}\n")

    # Generate graph
    G = generate_random_graph(m, graph_type, seed)
    print(f"Graph: N={G.number_of_nodes()}, m={G.number_of_edges()}")
    print(f"Edges: {list(G.edges())}\n")

    # Compute Fisher
    F = compute_exact_fisher_ising(G, J)
    print(f"Fisher matrix F:")
    print(F)
    print(f"F eigenvalues: {np.linalg.eigvalsh(F)}\n")

    # Get Fiedler sign assignment
    S_diag = compute_fiedler_sign_assignment(G)
    print(f"Fiedler sign assignment S_diag: {S_diag}")

    # Compute Laplacian and Fiedler vector for inspection
    L = nx.laplacian_matrix(G).toarray()
    eigenvalues, eigenvectors = np.linalg.eigh(L)
    idx = eigenvalues.argsort()
    fiedler_vec = eigenvectors[:, idx[1]]
    print(f"Fiedler vector: {fiedler_vec}")
    print(f"Laplacian eigenvalues: {eigenvalues[idx][:5]}\n")

    # Construct M = S * F^2 * S (original interpretation)
    S = np.diag(S_diag)
    M_baseline = F @ F
    M_H1_v1 = S @ M_baseline @ S

    print(f"M (baseline F^2):")
    print(M_baseline)
    print(f"M baseline eigenvalues: {np.linalg.eigvalsh(M_baseline)}\n")

    print(f"M^{{H1'}} = S * F^2 * S (version 1):")
    print(M_H1_v1)
    print(f"M^{{H1'}} eigenvalues: {np.linalg.eigvalsh(M_H1_v1)}\n")

    # Alternative: M = (S*F)^2
    SF = S @ F
    M_H1_v2 = SF @ SF.T
    print(f"M^{{H1'}} = (S*F)^2 (version 2):")
    print(M_H1_v2)
    print(f"M^{{H1'}} v2 eigenvalues: {np.linalg.eigvalsh(M_H1_v2)}\n")

    # Use v2 for rest of analysis
    M_H1 = M_H1_v2

    # Compute F^{-1/2} M F^{-1/2}
    vals, vecs = np.linalg.eigh(F)
    vals = np.maximum(vals, 1e-10)
    F_inv_sqrt = vecs @ np.diag(1.0 / np.sqrt(vals)) @ vecs.T

    A_baseline = F_inv_sqrt @ M_baseline @ F_inv_sqrt
    A_H1 = F_inv_sqrt @ M_H1 @ F_inv_sqrt

    print(f"A = F^{{-1/2}} M F^{{-1/2}} (baseline):")
    print(A_baseline)
    print(f"A eigenvalues: {np.linalg.eigvalsh(A_baseline)}\n")

    print(f"A' = F^{{-1/2}} M^{{H1'}} F^{{-1/2}}:")
    print(A_H1)
    print(f"A' eigenvalues: {np.linalg.eigvalsh(A_H1)}\n")

    # Check for negative eigenvalues
    eigs_baseline = np.linalg.eigvalsh(A_baseline)
    eigs_H1 = np.linalg.eigvalsh(A_H1)

    print(f"Baseline has negative eigenvalues: {np.any(eigs_baseline < 0)}")
    print(f"H1' has negative eigenvalues: {np.any(eigs_H1 < 0)}")

    if np.any(eigs_H1 < 0):
        print(f"SUCCESS: H1' produces negative eigenvalue {eigs_H1[0]:.6f}")
    else:
        print(f"FAILURE: H1' still PSD, min eigenvalue = {eigs_H1[0]:.6f}")

    # Try alternative: what if we use S on the signature operator instead?
    print(f"\n{'='*80}")
    print("Alternative approach: apply S to signature operator")
    print(f"{'='*80}\n")

    # For q=1, try all single-sign-flip options
    print("Testing q=1 with all single sign flips:")
    for flip_idx in range(len(S_diag)):
        Sig_diag = np.ones(len(S_diag))
        Sig_diag[flip_idx] = -1.0
        Sig = np.diag(Sig_diag)

        A_test = F_inv_sqrt @ Sig @ M_H1 @ Sig @ F_inv_sqrt
        eigs_test = np.linalg.eigvalsh(A_test)

        if eigs_test[0] < 0:
            beta_c = -eigs_test[0]
            print(f"  flip_idx={flip_idx}: min_eig={eigs_test[0]:.6f}, beta_c={beta_c:.6f} ✓")
        else:
            print(f"  flip_idx={flip_idx}: min_eig={eigs_test[0]:.6f} (still PSD)")


def main():
    """Run debug on representative cases."""

    # Test cases
    test_cases = [
        (3, 0.5, 'tree'),
        (4, 1.0, 'sparse'),
        (5, 0.5, 'dense'),
        (6, 1.0, 'tree'),
    ]

    for m, J, graph_type in test_cases:
        debug_single_case(m, J, graph_type)


if __name__ == "__main__":
    main()
