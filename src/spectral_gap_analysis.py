import numpy as np
import itertools
from beta_c_high_dim_corrected import compute_exact_fisher_ising

def analyze_spectral_gap(n_vertices: int, graph_type: str = "random", connectivity: float = 0.5):
    """
    Analyze the spectral gap (d2 - d1) of the operator A = F^{1/2} S F^{1/2}
    for different sign assignments S to check if Lorentzian (q=1) is 'spectrally isolated'.
    """
    # 1. Generate Graph
    rng = np.random.default_rng()
    mask = rng.random((n_vertices, n_vertices)) < connectivity
    mask = np.triu(mask, 1)
    couplings = rng.normal(0, 1.0, size=(n_vertices, n_vertices))
    J = couplings * mask
    J = J + J.T # Symmetric
    
    # Check for meaningful graph
    if np.sum(np.abs(J)) < 1e-10: return None

    try:
        F, edges = compute_exact_fisher_ising(J)
    except ValueError:
        return None
        
    m = len(edges)
    m = len(edges)
    if m < 3: return None

    # Precompute F^{1/2}
    try:
        F_stab = F + 1e-9 * np.eye(m)
        vals, vecs = np.linalg.eigh(F_stab)
        F_sqrt = vecs @ np.diag(np.sqrt(np.maximum(vals, 0))) @ vecs.T
    except np.linalg.LinAlgError:
        return None

    # Compare q=1 vs q=m (Lorentzian vs Euclidean)
    
    # Lorentzian (q=1): Sample many
    gaps_q1 = []
    n_samples = 50
    indices = [rng.permutation(m)[:1] for _ in range(n_samples)] # q=1 samples
    
    for neg_idx in indices:
        S = np.ones(m)
        S[neg_idx] = -1.0
        A = F_sqrt @ np.diag(S) @ F_sqrt
        eigs = np.linalg.eigvalsh(A) # sorted ascending
        # d1 is most negative (or smallest)
        # gap = d2 - d1
        gaps_q1.append(eigs[1] - eigs[0])

    # Euclidean (q=0 or q=m):
    # q=0 (all +): A = F. eigs >= 0. d1 is min positive. d2-d1 is spectral gap of F.
    # q=m (all -): A = -F. eigs = -lambda_F. sorted: -lam_max, -lam_max-1...
    # d1 = -lam_max. d2 = -lam_max-1. Gap = (-lam_max-1) - (-lam_max) = lam_max - lam_max-1.
    
    eigs_F = np.linalg.eigvalsh(F_stab)
    gap_euclidean = eigs_F[-1] - eigs_F[-2] # Gap at the top end of F spectrum
    
    avg_gap_q1 = np.mean(gaps_q1)
    
    return {
        "n": n_vertices,
        "m": m,
        "avg_gap_q1": avg_gap_q1,
        "gap_euclidean": gap_euclidean,
        "ratio": avg_gap_q1 / gap_euclidean
    }

def main():
    print("SPECTRAL GAP ANALYSIS")
    print("=====================")
    print(f"{'N':<4} {'M':<4} {'Gap(Lor)':<10} {'Gap(Euc)':<10} {'Ratio (Lor/Euc)'}")
    
    for n in [3, 4, 5, 6, 7]:
        for _ in range(3):
            res = analyze_spectral_gap(n, connectivity=0.7)
            if res:
                print(f"{res['n']:<4} {res['m']:<4} {res['avg_gap_q1']:<10.4f} {res['gap_euclidean']:<10.4f} {res['ratio']:.2f}")

if __name__ == "__main__":
    main()
