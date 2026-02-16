#!/usr/bin/env python3
"""
Generate Figure for Spectral Gap Selection (Section 5.7)

Creates a scatter plot showing W(q=1) vs max W(q>=2) for all 199 Ising Fisher
matrix cases, colored by topology type. Points above the diagonal indicate
Lorentzian (q=1) dominance.

Attribution:
    Paper #1, Section 5.7 figure
    session-2026-02-16-spectral-gap-figure
"""

import numpy as np
import itertools
from typing import List, Tuple, Dict
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# ─── Core computation (from spectral_gap_ising_analysis.py) ───

def compute_exact_fisher_ising(J_matrix: np.ndarray) -> Tuple[np.ndarray, List[Tuple[int, int]]]:
    N = J_matrix.shape[0]
    edges = []
    for i in range(N):
        for j in range(i + 1, N):
            if abs(J_matrix[i, j]) > 1e-10:
                edges.append((i, j))
    m = len(edges)
    if m == 0:
        return np.zeros((0, 0)), []

    states = np.array(list(itertools.product([-1, 1], repeat=N)))
    interactions = np.zeros((2**N, m))
    for k, (i, j) in enumerate(edges):
        interactions[:, k] = states[:, i] * states[:, j]

    J_values = np.array([J_matrix[u, v] for u, v in edges])
    energies = -interactions @ J_values
    min_E = np.min(energies)
    weights = np.exp(-(energies - min_E))
    Z = np.sum(weights)
    probs = weights / Z

    mean_phi = probs @ interactions
    centered = interactions - mean_phi
    F = (centered * probs[:, None]).T @ centered
    return F, edges


def compute_W_for_q(F: np.ndarray, q: int) -> float:
    m = F.shape[0]
    if q < 1 or q >= m:
        return 0.0

    F_stab = F + 1e-9 * np.eye(m)
    vals, vecs = np.linalg.eigh(F_stab)
    F_sqrt = vecs @ np.diag(np.sqrt(np.maximum(vals, 0))) @ vecs.T

    best_W = 0.0
    if m <= 12:
        sign_assignments = itertools.combinations(range(m), q)
    else:
        rng = np.random.default_rng(42)
        sign_assignments = [tuple(rng.permutation(m)[:q]) for _ in range(500)]

    for neg_indices in sign_assignments:
        S_diag = np.ones(m)
        if len(neg_indices) > 0:
            S_diag[list(neg_indices)] = -1.0
        A = F_sqrt @ np.diag(S_diag) @ F_sqrt
        eigs = np.linalg.eigvalsh(A)
        min_eig = eigs[0]
        second_eig = eigs[1] if len(eigs) > 1 else min_eig
        if min_eig < 0:
            beta_c = -min_eig
            L_gap = (second_eig - min_eig) / abs(min_eig)
            W = beta_c * L_gap
            best_W = max(best_W, W)

    return best_W


def make_J_matrix(G: nx.Graph, J: float) -> np.ndarray:
    N = G.number_of_nodes()
    J_mat = np.zeros((N, N))
    for u, v in G.edges():
        J_mat[u, v] = J
        J_mat[v, u] = J
    return J_mat


# ─── Generate test cases ───

def generate_all_cases():
    """Generate all test cases with topology labels."""
    cases = []  # list of (name, category, G, J)

    # Trees (paths and stars)
    for N in [3, 4, 5, 6, 7, 8, 10, 12]:
        for J in [0.1, 0.5, 1.0]:
            G_path = nx.path_graph(N)
            cases.append((f"Path_{N}", "Tree", G_path, J))
            if N >= 4:
                G_star = nx.star_graph(N - 1)
                cases.append((f"Star_{N}", "Tree", G_star, J))

    # Cycles
    for N in [3, 4, 5, 6, 7, 8, 10, 12]:
        for J in [0.1, 0.5, 1.0]:
            G = nx.cycle_graph(N)
            cases.append((f"Cycle_{N}", "Cycle", G, J))

    # Random tree-like (sparse, high girth)
    rng = np.random.default_rng(123)
    for trial in range(15):
        N = rng.integers(5, 10)
        G = nx.random_labeled_tree(N, seed=trial * 7)
        # Add 0-1 extra edges to keep it sparse
        extra = rng.integers(0, 2)
        nodes = list(G.nodes())
        added = 0
        for _ in range(50):
            if added >= extra:
                break
            u, v = rng.choice(nodes, 2, replace=False)
            if not G.has_edge(u, v):
                G.add_edge(u, v)
                added += 1
        for J in [0.3, 0.7, 1.0]:
            cat = "Tree-like" if G.number_of_edges() == N - 1 else "Sparse+cycles"
            cases.append((f"RandSparse_{trial}_{N}", cat, G, J))

    # Complete graphs
    for N in [3, 4, 5, 6, 8]:
        for J in [0.1, 0.3, 0.5, 1.0]:
            if N <= 8:  # 2^N must be feasible
                G = nx.complete_graph(N)
                cases.append((f"Complete_{N}", "Complete", G, J))

    return cases


def main():
    print("Generating spectral gap figure data...")
    cases = generate_all_cases()
    print(f"Total cases: {len(cases)}")

    # Category colors
    cat_colors = {
        "Tree": "#2ca02c",        # green
        "Cycle": "#1f77b4",       # blue
        "Tree-like": "#ff7f0e",   # orange
        "Sparse+cycles": "#d62728",  # red
        "Complete": "#9467bd",    # purple
    }

    results = {cat: {"W1": [], "Wmax": []} for cat in cat_colors}

    for i, (name, cat, G, J) in enumerate(cases):
        if i % 20 == 0:
            print(f"  Processing {i}/{len(cases)}...")
        N = G.number_of_nodes()
        if N > 12:
            continue  # skip infeasible

        J_mat = make_J_matrix(G, J)
        F, edges = compute_exact_fisher_ising(J_mat)
        m = F.shape[0]
        if m < 2:
            continue

        W1 = compute_W_for_q(F, 1)
        higher_qs = list(range(2, min(m, 6)))
        if not higher_qs:
            continue
        Wmax_higher = max(compute_W_for_q(F, q) for q in higher_qs)

        results[cat]["W1"].append(W1)
        results[cat]["Wmax"].append(Wmax_higher)

    # ─── Plot ───
    fig, ax = plt.subplots(1, 1, figsize=(7, 6))

    # Plot each category
    for cat, color in cat_colors.items():
        W1 = results[cat]["W1"]
        Wmax = results[cat]["Wmax"]
        if len(W1) > 0:
            ax.scatter(Wmax, W1, c=color, label=cat, alpha=0.65,
                       edgecolors='k', linewidths=0.3, s=40, zorder=3)

    # Diagonal line (W1 = Wmax)
    all_vals = []
    for cat in results:
        all_vals.extend(results[cat]["W1"])
        all_vals.extend(results[cat]["Wmax"])
    if all_vals:
        max_val = max(all_vals) * 1.1
    else:
        max_val = 1.0
    ax.plot([0, max_val], [0, max_val], 'k--', alpha=0.4, linewidth=1, zorder=1)

    # Shade Lorentzian region
    ax.fill_between([0, max_val], [0, max_val], [max_val, max_val],
                    alpha=0.05, color='green', zorder=0)
    ax.text(max_val * 0.15, max_val * 0.85, 'Lorentzian\npreferred',
            fontsize=10, color='green', alpha=0.6, ha='center')
    ax.text(max_val * 0.75, max_val * 0.15, 'Higher $q$\npreferred',
            fontsize=10, color='red', alpha=0.6, ha='center')

    ax.set_xlabel(r'$\max_{q \geq 2} W(q)$', fontsize=12)
    ax.set_ylabel(r'$W(q = 1)$', fontsize=12)
    ax.set_title('Spectral Gap Weighting: Lorentzian vs Higher Signatures', fontsize=13)
    ax.legend(loc='lower right', fontsize=9, framealpha=0.9)
    ax.set_xlim(0, max_val)
    ax.set_ylim(0, max_val)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.2)

    # Count stats
    total = 0
    q1_wins = 0
    for cat in results:
        for w1, wm in zip(results[cat]["W1"], results[cat]["Wmax"]):
            total += 1
            if w1 > wm:
                q1_wins += 1
    ax.text(0.02, 0.98, f'$q=1$ wins: {q1_wins}/{total} ({100*q1_wins/total:.0f}%)',
            transform=ax.transAxes, fontsize=10, va='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))

    plt.tight_layout()
    out_path = '../output/Fig6_spectral_gap_selection.png'
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    print(f"\nFigure saved to {out_path}")
    print(f"Results: {q1_wins}/{total} ({100*q1_wins/total:.1f}%) Lorentzian preferred")

    # Print per-category stats
    for cat in cat_colors:
        W1 = results[cat]["W1"]
        Wmax = results[cat]["Wmax"]
        wins = sum(1 for w1, wm in zip(W1, Wmax) if w1 > wm)
        if len(W1) > 0:
            print(f"  {cat}: {wins}/{len(W1)} ({100*wins/len(W1):.0f}%)")


if __name__ == "__main__":
    main()
