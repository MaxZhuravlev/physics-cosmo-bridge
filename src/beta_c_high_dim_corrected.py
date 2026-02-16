import numpy as np
import itertools
from dataclasses import dataclass
from typing import List, Tuple, Dict
import time

@dataclass
class SimulationResult:
    n_vertices: int
    n_edges: int
    graph_type: str
    optimal_q: int
    optimal_beta_c: float
    lorentzian_beta_c: float
    euclidean_beta_c: float
    is_lorentzian_optimal: bool

def compute_exact_fisher_ising(J_matrix: np.ndarray) -> np.ndarray:
    """
    Compute the exact Fisher Information Matrix for an Ising model defined by J_matrix.
    H(s) = - sum_{i<j} J_{ij} s_i s_j
    Probability P(s) = exp(-H(s)) / Z
    
    Parameters:
        J_matrix: (N, N) symmetric matrix of couplings.
    
    Returns:
        F: (m, m) Fisher matrix, where m is the number of non-zero entries in upper triangle of J.
        The rows/cols are indexed by the edges (i,j) in lexicographical order.
    """
    N = J_matrix.shape[0]
    
    # Identify edges
    edges = []
    for i in range(N):
        for j in range(i + 1, N):
            if abs(J_matrix[i, j]) > 1e-10: # Non-zero coupling
                edges.append((i, j))
    
    m = len(edges)
    if m == 0:
        return np.zeros((0, 0))

    # Generate all 2^N states
    states = np.array(list(itertools.product([-1, 1], repeat=N))) # (2^N, N)
    
    # Compute Energies
    # E_s = - sum J_ij s_i s_j
    # Vectorized:
    # interactions[:, k] = s_i * s_j for k-th edge
    interactions = np.zeros((2**N, m))
    for k, (i, j) in enumerate(edges):
        interactions[:, k] = states[:, i] * states[:, j]
    
    # Energy = - sum_k J_{edge_k} * interaction_k
    # We need the J values corresponding to the edges list
    J_values = np.array([J_matrix[u, v] for u, v in edges])
    energies = - interactions @ J_values 
    
    # Probabilities
    # Shift energies for numerical stability
    min_E = np.min(energies)
    weights = np.exp(-(energies - min_E)) # Boltzmann weights, beta=1 implicitly for the reference state
    Z = np.sum(weights)
    probs = weights / Z
    
    # Compute Edge Expectations <phi_e>
    # phi_e = s_i s_j
    # E[phi] = probs . interactions
    mean_phi = probs @ interactions # (m,)
    
    # Compute Covariance Matrix (Fisher Matrix)
    # F_{ab} = E[phi_a phi_b] - E[phi_a]E[phi_b]
    # E[phi_a phi_b]
    
    # We can do this efficiently:
    # weighted_interactions = interactions * sqrt(probs)[:, None]
    # second_moment = weighted_interactions.T @ weighted_interactions
    
    # Or:
    # Covariance = E[(phi - mu)(phi - mu)^T]
    centered_interactions = interactions - mean_phi
    # We need to weight each row by prob
    # Cov = sum_s P(s) (phi(s) - mu)(phi(s) - mu)^T
    #     = (centered_interactions * probs[:, None]).T @ centered_interactions
    
    F = (centered_interactions * probs[:, None]).T @ centered_interactions
    
    return F, edges

def analyze_graph(n_vertices: int, graph_type: str = "random", connectivity: float = 0.5) -> SimulationResult:
    """
    Analyze a single graph:
    1. Generate topology and couplings
    2. Compute exact Fisher F
    3. Sweep all Signatures q -> Find max beta_c
    """
    # 1. Generate Graph
    J = np.zeros((n_vertices, n_vertices))
    rng = np.random.default_rng()
    
    if graph_type == "random":
        # Erdős-Rényi
        mask = rng.random((n_vertices, n_vertices)) < connectivity
        mask = np.triu(mask, 1)
        couplings = rng.normal(0, 1.0, size=(n_vertices, n_vertices))
        J = couplings * mask
        J = J + J.T # Symmetric
    elif graph_type == "complete":
        mask = np.triu(np.ones((n_vertices, n_vertices)), 1)
        couplings = rng.normal(0, 1.0, size=(n_vertices, n_vertices))
        J = couplings * mask
        J = J + J.T
        
    F, edges = compute_exact_fisher_ising(J)
    m = len(edges)
    
    if m < 3:
        # Too small to be interesting for signature
        return None

    # Precompute F^{1/2}
    try:
        # F might be singular if graph is disconnected or has symmetries?
        # Add tiny jitter for stability
        F_stab = F + 1e-9 * np.eye(m)
        vals, vecs = np.linalg.eigh(F_stab)
        F_sqrt = vecs @ np.diag(np.sqrt(np.maximum(vals, 0))) @ vecs.T
    except np.linalg.LinAlgError:
        return None

    # 3. Sweep Signatures
    # We want to find beta_c for each q
    # beta_c(S) = - min_eig( F^{1/2} S F^{1/2} )
    # If min_eig >= 0, beta_c = 0 (unstable/impossible)
    
    max_beta_c_by_q = {} # q -> max_beta_c
    
    # For small m, we can iterate ALL 2^m sign assignments?
    # m = N(N-1)/2. For N=5, m=10 -> 1024 (Easy)
    # For N=6, m=15 -> 32768 (Doable)
    # For N=7, m=21 -> 2M (Too slow for python script in loop)
    # For N=8, m=28 -> Impossible
    
    # Strategy:
    # If m <= 15: Exact sweep
    # If m > 15: Random sampling (e.g. 1000 samples per q)
    
    qs_to_check = range(m + 1)
    
    for q in qs_to_check:
        best_beta_for_q = -1.0
        
        # How many samples?
        n_samples = 100
        if m <= 12:
            # Generate all combinations of q negative signs
            # indices of negative signs
            from itertools import combinations
            idx_list = list(combinations(range(m), q))
            # If too many, subsample
            if len(idx_list) > n_samples:
                # Randomly pick
                indices = [idx_list[i] for i in rng.choice(len(idx_list), n_samples, replace=False)]
            else:
                indices = idx_list
        else:
             # Random sampling for large m
             indices = []
             for _ in range(n_samples):
                 # Random permutation
                 perm = rng.permutation(m)
                 indices.append(perm[:q])

        for neg_indices in indices:
            S_diag = np.ones(m)
            if len(neg_indices) > 0:
                S_diag[list(neg_indices)] = -1.0
            
            # Compute beta_c
            # A = F^{1/2} S F^{1/2}
            # Actually, compute eigenvalues of A is same as eigenvalues of F S?
            # No. Eigs of F S are not necessarily real.
            # But F^{1/2} S F^{1/2} is symmetric real.
            
            S_mat = np.diag(S_diag)
            A = F_sqrt @ S_mat @ F_sqrt
            
            # We want min eigenvalue
            # For random signs, A is roughly random?
            min_eig = np.linalg.eigvalsh(A)[0]
            
            if min_eig < 0:
                beta_c = -min_eig
            else:
                beta_c = 0.0
                
            if beta_c > best_beta_for_q:
                best_beta_for_q = beta_c
        
        max_beta_c_by_q[q] = best_beta_for_q

    # Identify optimal q
    optimal_q = -1
    global_max_beta = -1.0
    
    for q, beta_val in max_beta_c_by_q.items():
        if beta_val > global_max_beta:
            global_max_beta = beta_val
            optimal_q = q
            
    lorentzian_beta = max_beta_c_by_q.get(1, 0.0)
    # Euclidean is usually all positive -> q=0? Or all negative q=m?
    # q=0 means all +1. A = F (positive def). min_eig > 0 => beta_c = 0.
    # q=m means all -1. A = -F (negative def). min_eig = -lambda_max(F). beta_c = lambda_max(F).
    # So "Euclidean" in the sense of "standard metric" (+ + + +) usually implies q=0 (if we define g = M + beta F).
    # Wait, the signature of g is determined by beta relative to beta_c.
    # If we want the *observer* to have signature (p,q), we need eigenvalues of g.
    # The hypothesis "Lorentzian is preferred" means "The configuration S that gives a Lorentzian signature (1 neg eigenvalue for g) has the largest volume / beta_c range".
    # For a given S (with signature q_S on parameters), the resulting g will have some signature.
    # Wait. The signature of g is NOT necessarily the signature of S.
    # HOWEVER, for small beta, g ~ M ~ F S F. The signature of F S F is the same as the signature of S (by Sylvester's law of inertia, since F is positive definite).
    # PROOF: g = F^{1/2} ( S + beta F^{-1} ) F^{1/2}.
    # The signature of g is the signature of (S + beta F^{-1}).
    # As beta -> 0, signature(g) -> signature(S).
    # So "Lorentzian signature" implies we want S to have q=1 (or q=m-1).
    # (Assuming we want 1 time dimension).
    
    # So comparing max_beta_c for q=1 vs other q is the correct test.
    
    euclidean_beta = max_beta_c_by_q.get(m, 0.0) # All negative signs = maximum stability?
    
    return SimulationResult(
        n_vertices=n_vertices,
        n_edges=m,
        graph_type=graph_type,
        optimal_q=optimal_q,
        optimal_beta_c=global_max_beta,
        lorentzian_beta_c=lorentzian_beta,
        euclidean_beta_c=euclidean_beta,
        is_lorentzian_optimal=(optimal_q == 1)
    )

def main():
    print(" CORRECTED HIGH-DIMENSIONAL LORENTZIAN SWEEP")
    print("=============================================")
    print("Using exact Ising Fisher Matrices (no approximations).")
    print("\nHypothesis Test:")
    print("  - Lorentzian Hypothesis: q=1 maximizes beta_c in high dimensions.")
    print("  - Null Hypothesis: q=m (all negative) or q=m/2 maximizes beta_c.\n")
    
    print(f"{'N_Vert':<6} {'M_Edge':<6} {'Type':<10} {'Opt_Q':<6} {'Lor_Beta':<10} {'Euc_Beta':<10} {'Result'}")
    print("-" * 70)
    
    vertex_counts = [4, 5, 6, 7] # 8 is getting slow for exact sum (2^8=256, but many edges)
    # N=8 -> 2^8 states = 256. F calc is fast.
    # N=10 -> 1024 states. F calc is fast.
    # The bottleneck is the number of edges m.
    # For N=7, m could be 21. 2^21 is too big for exhaustive q sweep.
    # But we implemented random q sampling.
    
    vertex_counts = [3, 4, 5, 6, 7, 8]
    
    results = []
    
    for n in vertex_counts:
        # Run multiple trials per N
        for _ in range(3): # 3 random graphs per N
            try:
                res = analyze_graph(n, "random", connectivity=0.7)
                if res is None: continue
                
                res_str = "LORENTZIAN" if res.is_lorentzian_optimal else "Euclidean/Other"
                print(f"{res.n_vertices:<6} {res.n_edges:<6} {res.graph_type:<10} {res.optimal_q:<6} {res.lorentzian_beta_c:<10.4f} {res.euclidean_beta_c:<10.4f} {res_str}")
                results.append(res)
            except Exception as e:
                print(f"Error on N={n}: {e}")

    # Summary
    print("\nSUMMARY")
    print("=" * 30)
    lorentzian_wins = sum(1 for r in results if r.is_lorentzian_optimal)
    total = len(results)
    print(f"Lorentzian Optimal (q=1): {lorentzian_wins}/{total} ({lorentzian_wins/total*100:.1f}%)")
    
    # Save detailed report
    with open("corrected_sweep_results.md", "w") as f:
        f.write("# Corrected High-Dim Lorentzian Sweep Results\n\n")
        f.write("| N | M | Optimal q | Beta_c (Lor) | Beta_c (Best) | Ratio |\n")
        f.write("|---|---|---|---|---|---|\n")
        for r in results:
            ratio = r.lorentzian_beta_c / r.optimal_beta_c if r.optimal_beta_c > 0 else 0
            f.write(f"| {r.n_vertices} | {r.n_edges} | {r.optimal_q} | {r.lorentzian_beta_c:.4f} | {r.optimal_beta_c:.4f} | {ratio:.2f} |\n")

if __name__ == "__main__":
    main()
