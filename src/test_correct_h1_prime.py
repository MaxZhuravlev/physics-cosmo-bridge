#!/usr/bin/env python3
"""
Test CORRECT H1' construction based on theorem statement:
"W(q=1) > 0 whenever F^{1/2} S F^{1/2} has a negative eigenvalue"

This means we should test eigenvalues of F^{1/2} * S * F^{1/2}, not F^{-1/2} * M * F^{-1/2}.
"""

import numpy as np
import networkx as nx
from signed_edge_phase_diagram import (
    compute_exact_fisher_ising,
    compute_fiedler_sign_assignment,
    generate_random_graph
)


def test_correct_h1_construction(m: int, J: float, graph_type: str, seed: int = 42):
    """Test correct H1' construction: eigenvalues of F^{1/2} S F^{1/2}."""

    print(f"\n{'='*80}")
    print(f"Testing m={m}, J={J}, {graph_type}, seed={seed}")
    print(f"{'='*80}\n")

    # Generate graph
    G = generate_random_graph(m, graph_type, seed)
    print(f"Graph: N={G.number_of_nodes()}, m={G.number_of_edges()}")

    # Compute Fisher
    F = compute_exact_fisher_ising(G, J)

    # Get Fiedler sign assignment
    S_diag = compute_fiedler_sign_assignment(G)
    S = np.diag(S_diag)
    print(f"Fiedler signs: {S_diag}")

    # Compute F^{1/2}
    vals, vecs = np.linalg.eigh(F)
    vals = np.maximum(vals, 1e-10)
    F_sqrt = vecs @ np.diag(np.sqrt(vals)) @ vecs.T

    # CORRECT H1' quantity: F^{1/2} * S * F^{1/2}
    A_H1 = F_sqrt @ S @ F_sqrt

    eigs_H1 = np.linalg.eigvalsh(A_H1)
    print(f"Eigenvalues of F^{{1/2}} S F^{{1/2}}: {eigs_H1}")

    has_negative = np.any(eigs_H1 < -1e-10)
    print(f"Has negative eigenvalue: {has_negative}")

    if has_negative:
        min_eig = eigs_H1[0]
        beta_c = -min_eig
        print(f"SUCCESS! min_eig = {min_eig:.6f}, beta_c = {beta_c:.6f}")
    else:
        print(f"No negative eigenvalue. Min = {eigs_H1[0]:.6f}")

    return has_negative


def main():
    """Test several cases."""

    test_cases = [
        (3, 0.5, 'tree'),
        (4, 1.0, 'sparse'),
        (5, 0.5, 'dense'),
        (6, 1.0, 'tree'),
        (8, 0.5, 'dense'),
    ]

    successes = 0
    for m, J, graph_type in test_cases:
        if test_correct_h1_construction(m, J, graph_type):
            successes += 1

    print(f"\n{'='*80}")
    print(f"Summary: {successes}/{len(test_cases)} cases produced negative eigenvalues")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
