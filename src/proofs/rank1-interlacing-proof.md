# Rank-1 Interlacing Proof of Lorentzian Selection

**Author:** Max Zhuravlev (with mathematical formalization assistance)
**Date:** 2026-02-17
**Status:** THEOREM (diagonal and near-diagonal cases)
**Approach:** Unified rank-1 vs. rank-q perturbation analysis via secular equations

---

## Abstract

We provide an alternative proof of the spectral gap selection theorem using
the rank-1 structure of the Lorentzian (q=1) sign flip as the central
organizing principle. The key observation is that the signed metric kernel
A(S_q) = F^{1/2} S_q F^{1/2} can be written as F minus a rank-q positive
semi-definite correction. For q=1 this is a rank-1 update, whose eigenvalues
are governed by the secular equation and the Cauchy interlacing theorem,
producing exactly one spectrally isolated negative eigenvalue. For q>=2 the
update has rank q, producing q negative eigenvalues that cluster together
when F is near-diagonal. This rank-based dichotomy provides a unified and
more transparent proof than the three-stage approach (Theorems A, B, C) in
the original document.

The proof is complete and self-contained for diagonal F (Theorem 1), and
extends to near-diagonal F (Theorem 2) with explicit constants derived from
the secular equation. A comparison with the original three-stage proof is
provided in Section 6.

---

## Table of Contents

1. [Setup and Notation](#1-setup-and-notation)
2. [The Rank Structure of Sign Flips](#2-the-rank-structure-of-sign-flips)
3. [Theorem 1: Diagonal Case via Secular Equation](#3-theorem-1-diagonal-case-via-secular-equation)
4. [Theorem 2: Near-Diagonal Case via Rank-1 Perturbation Theory](#4-theorem-2-near-diagonal-case-via-rank-1-perturbation-theory)
5. [Failed Directions and Counterexamples](#5-failed-directions-and-counterexamples)
6. [Comparison with Three-Stage Proof](#6-comparison-with-three-stage-proof)
7. [LaTeX-Ready Theorem Statements](#7-latex-ready-theorem-statements)

---

## 1. Setup and Notation

We adopt the definitions from the spectral gap selection theorem document.
Let F be an m x m positive definite matrix (m >= 3). For a sign assignment
S_q = diag(s_1, ..., s_m) with exactly q entries equal to -1, define:

    A(S_q) = F^{1/2} S_q F^{1/2}                                    (1.1)

with eigenvalues d_1 <= d_2 <= ... <= d_m. The spectral gap weighting is:

    W(S_q) = beta_c * L_gap                                          (1.2)

where beta_c = -d_1 and L_gap = (d_2 - d_1)/|d_1|, so that:

    W(S_q) = d_2 - d_1                                               (1.3)

**Observation:** W(S_q) = d_2(A) - d_1(A), the gap between the two smallest
eigenvalues of A(S_q). This simplification (which follows from expanding
beta_c * L_gap = |d_1| * (d_2 - d_1)/|d_1| = d_2 - d_1) will be central.

The signature weighting is W(q) = max_{S : |{e : s_e = -1}| = q} W(S_q).

---

## 2. The Rank Structure of Sign Flips

### 2.1 Decomposition

Write S_q = I_m - 2 P_q where P_q = sum_{j in J_q} e_j e_j^T is the
orthogonal projector onto the flipped coordinates, with J_q the index set
of flipped signs (|J_q| = q). Then:

    A(S_q) = F^{1/2} (I - 2 P_q) F^{1/2}
           = F - 2 F^{1/2} P_q F^{1/2}                              (2.1)

Define the correction matrix:

    Delta_q := 2 F^{1/2} P_q F^{1/2}                                (2.2)

Then A(S_q) = F - Delta_q. The matrix Delta_q is positive semi-definite
(since P_q is PSD and F^{1/2} is invertible) with rank exactly q (since
P_q has rank q and F^{1/2} is full rank).

### 2.2 The q=1 Case: Rank-1 Update

For q = 1 with the single flipped index k:

    P_1 = e_k e_k^T

    Delta_1 = 2 F^{1/2} e_k e_k^T F^{1/2} = 2 f_k f_k^T           (2.3)

where f_k = F^{1/2} e_k is the k-th column of F^{1/2}. This is a rank-1
PSD matrix with the single nonzero eigenvalue 2 ||f_k||^2 = 2 (F)_{kk}
= 2 F_{kk}.

Therefore A(S_1) = F - 2 f_k f_k^T is a rank-1 perturbation of F.

### 2.3 The q >= 2 Case: Rank-q Update

For q >= 2 with flipped indices J_q = {j_1, ..., j_q}:

    P_q = sum_{j in J_q} e_j e_j^T

    Delta_q = 2 sum_{j in J_q} f_j f_j^T                            (2.4)

This is a rank-q PSD matrix (rank exactly q when the vectors {f_j}_{j in J_q}
are linearly independent, which holds when F is positive definite since
F^{1/2} is invertible).

### 2.4 Key Structural Difference

The rank of Delta_q determines how many eigenvalues of F can be "pushed
below zero" by the subtraction A = F - Delta_q:

- **Rank 1 (q=1):** By the Cauchy interlacing theorem (Lemma 2.1 below),
  at most ONE eigenvalue of A can fall below lambda_min(F). Since F is
  positive definite (all eigenvalues > 0), A has at most one non-positive
  eigenvalue. Combined with the existence proof (Section 3), A has
  EXACTLY one negative eigenvalue, and it is ISOLATED from the rest.

- **Rank q (q>=2):** By Weyl's inequality, up to q eigenvalues can be
  pushed below lambda_min(F). When F is near-diagonal, these q negative
  eigenvalues cluster together, producing a small spectral gap.

This is the fundamental dichotomy that drives Lorentzian selection.

**Lemma 2.1** (Cauchy Interlacing for Rank-1 Perturbations; Bhatia 1997,
Theorem III.1.5). Let B be symmetric with eigenvalues lambda_1 <= ... <= lambda_m.
Let A = B - alpha v v^T for alpha > 0 and unit vector v. Let mu_1 <= ... <= mu_m
be the eigenvalues of A. Then:

    mu_1 <= lambda_1 <= mu_2 <= lambda_2 <= ... <= lambda_{m-1} <= mu_m

In particular, mu_2 >= lambda_1.

**Lemma 2.2** (Weyl's Inequality; Horn & Johnson 2012, Theorem 4.3.1).
Let B, C be m x m symmetric matrices. Then for each i:

    lambda_i(B) + lambda_1(C) <= lambda_i(B + C) <= lambda_i(B) + lambda_m(C)

In particular, if C has rank r, then lambda_i(B + C) = lambda_i(B) for
all i such that the eigenvalue is "unaffected" by the rank-r subspace.
More precisely: lambda_i(B + C) can differ from lambda_i(B) by at most
||C||_op, and at most r eigenvalues can shift significantly.

---

## 3. Theorem 1: Diagonal Case via Secular Equation

### 3.1 Statement

**Theorem 1** (Rank-1 Isolation implies Lorentzian Selection -- Diagonal Case).
Let F = D = diag(d_1, ..., d_m) with d_1 >= d_2 >= ... >= d_m > 0 and m >= 3.
Then:

(a) W(1) = d_1 + d_m (achieved by flipping the index of d_1).

(b) W(q) = d_1 - d_m for q = 2, and W(q) <= d_1 - d_m for all q >= 2.

(c) W(1) - W(q) >= 2 d_m for all q >= 2.

(d) When D = d * I_m: W(1) = 2d and W(q) = 0 for all q >= 2.

### 3.2 Proof via Secular Equation

We prove this by analyzing the secular equation for rank-1 and rank-q
perturbations of diagonal matrices.

**Proof of (a): The q=1 secular equation.**

For diagonal F = D, f_k = D^{1/2} e_k = sqrt(d_k) e_k. The rank-1
update is:

    A = D - 2 d_k e_k e_k^T = diag(d_1, ..., d_{k-1}, -d_k, d_{k+1}, ..., d_m)

This is diagonal, so the eigenvalues are explicit:
{d_1, ..., d_{k-1}, -d_k, d_{k+1}, ..., d_m}.

There is exactly one negative eigenvalue: -d_k. The second-smallest
eigenvalue is d_2(A) = min_{j != k} d_j.

Therefore:

    W(k) = d_2(A) - d_1(A) = min_{j != k} d_j - (-d_k) = min_{j != k} d_j + d_k

To maximize over k, note:

    W(k) = d_k + min_{j != k} d_j

- For k such that d_k = d_1 (the maximum): min_{j != k} d_j = d_m (since
  removing the maximum preserves the minimum when m >= 3). So W = d_1 + d_m.

- For k such that d_k < d_1: W(k) = d_k + min_{j != k} d_j <= d_k + d_m
  < d_1 + d_m. (If k is the index of d_m, then min_{j != k} d_j = d_{m-1}
  >= d_m, so W(k) = d_m + d_{m-1} <= d_m + d_1.)

Therefore W(1) = d_1 + d_m, achieved at k = argmax_i d_i.

**Alternative derivation via secular equation (for non-diagonal case
preparation).** Even though the diagonal case is trivial, we set up the
secular equation framework. For a rank-1 update A = B - sigma u u^T with
B symmetric having eigenvalues lambda_1 >= ... >= lambda_m and u = sum c_i v_i
(expansion in eigenvectors of B), the eigenvalues mu of A satisfy the
secular equation:

    1 = sigma * sum_{i=1}^{m} c_i^2 / (lambda_i - mu)               (3.1)

For B = D, sigma = 2d_k, u = e_k: the expansion coefficients are c_i = delta_{ik}
(since eigenvectors of D are the standard basis vectors). The secular equation
becomes:

    1 = 2d_k / (d_k - mu)

    d_k - mu = 2d_k

    mu = -d_k

This confirms the negative eigenvalue is exactly -d_k. The other eigenvalues
remain at d_j for j != k (they satisfy the secular equation trivially since
c_j = 0 for j != k).

**Proof of (b): The q >= 2 case.**

For q >= 2 with flipped indices J_q = {j_1, ..., j_q} where we label
d_{j_1} >= d_{j_2} >= ... >= d_{j_q}:

    A = D - 2 sum_{j in J_q} d_j e_j e_j^T

Since D is diagonal and the perturbation is also diagonal:

    A = diag(s_1 d_1, ..., s_m d_m)

The eigenvalues are {s_i d_i}. The q negative eigenvalues are
{-d_{j_1}, -d_{j_2}, ..., -d_{j_q}}, ordered as:

    d_1(A) = -d_{j_1},  d_2(A) = -d_{j_2}

(since d_{j_1} >= d_{j_2}, so -d_{j_1} <= -d_{j_2}).

The spectral gap is:

    W = d_2(A) - d_1(A) = -d_{j_2} - (-d_{j_1}) = d_{j_1} - d_{j_2}

To maximize over all choices of q indices from {1, ..., m}:

We want to maximize d_{j_1} - d_{j_2} where d_{j_1} >= d_{j_2} are the
two largest values among the chosen q indices.

**For q = 2:** Choose j_1, j_2. The gap is d_{j_1} - d_{j_2}. To maximize,
take d_{j_1} = d_1 (global max) and d_{j_2} = d_m (global min). Then
W(2) = d_1 - d_m.

**For q = 3:** Choose j_1, j_2, j_3. The two largest are d_{j_1} >= d_{j_2}.
To maximize d_{j_1} - d_{j_2}, take d_{j_1} = d_1 and then minimize d_{j_2}.
Since d_{j_2} is the second-largest of the three chosen values, to minimize
it we should make the other two chosen values as small as possible. So
choose {d_1, d_{m-1}, d_m}. Then d_{j_1} = d_1 and d_{j_2} = d_{m-1}.
Thus W(3) = d_1 - d_{m-1} <= d_1 - d_m = W(2).

**For general q >= 2:** By the same argument, the optimal choice always
includes d_1 (to maximize d_{j_1}) and the q-1 smallest values
{d_{m-q+2}, ..., d_m} (to minimize d_{j_2}). Then d_{j_2} = d_{m-q+2} >= d_m,
so:

    W(q) = d_1 - d_{m-q+2} <= d_1 - d_m = W(2)

Therefore W(q) is maximized at q = 2 with W(2) = d_1 - d_m, and W(q) is
non-increasing in q for q >= 2.

**Proof of (c):**

    W(1) - max_{q >= 2} W(q) = (d_1 + d_m) - (d_1 - d_m) = 2 d_m > 0

since d_m > 0 (F is positive definite). QED.

**Proof of (d):**

When D = d * I_m: d_1 = d_m = d. Then W(1) = d + d = 2d and W(2) = d - d = 0.
For all q >= 2: W(q) = 0 (all q flipped eigenvalues are identical at -d, so
the gap between d_1(A) and d_2(A) is zero). QED.

### 3.3 The Rank-1 Isolation Mechanism (Conceptual Summary)

Why does q=1 win? The answer has a clean algebraic explanation:

**For q=1:** The eigenvalue spectrum of A has the form
{d_1, ..., d_{k-1}, -d_k, d_{k+1}, ..., d_m}. The negative eigenvalue -d_k
is separated from the positive bulk {d_j : j != k} by a gap of at least
d_m + d_k. This gap grows with d_k (which we choose to be maximal).

The spectral gap W = d_m + d_1 measures the "distance" from the isolated
negative eigenvalue to the nearest positive eigenvalue. It equals the
SUM of the extreme eigenvalues.

**For q >= 2:** The eigenvalue spectrum of A has q negative values. The
gap between the two most negative eigenvalues is d_{j_1} - d_{j_2},
which measures the SPREAD of the flipped eigenvalues. At best this
equals d_1 - d_m, the DIFFERENCE of the extreme eigenvalues.

The inequality W(1) > W(q >= 2) reduces to:

    d_1 + d_m > d_1 - d_m    iff    2 d_m > 0

which holds whenever F is positive definite (d_m > 0). This is the
deepest algebraic reason: a sum of positive quantities always exceeds
their difference.

---

## 4. Theorem 2: Near-Diagonal Case via Rank-1 Perturbation Theory

### 4.1 Statement

**Theorem 2** (Rank-1 Isolation for Near-Diagonal Matrices). Let
F = D + epsilon * E be an m x m positive definite matrix where:
- D = diag(d_1, ..., d_m) with d_1 >= d_2 >= ... >= d_m > 0
- E is symmetric with ||E||_op <= 1
- 0 <= epsilon < d_m / 2 (ensuring positive definiteness)
- kappa := d_1 / d_m is the condition number of D

Define the perturbation constant C_pert := 5 kappa / 2 = 5 d_1 / (2 d_m).

Then:

(a) For q = 1 (Lorentzian), with the sign flip at index 1 (the index of d_1):

    W(1) >= d_1 + d_m - 2 C_pert * epsilon
          = d_1 + d_m - 5 kappa * epsilon                           (4.1)

(b) For q >= 2 (higher signatures), for ANY choice of q flipped indices:

    W(q) <= d_1 - d_m + 2 C_pert * epsilon
          = d_1 - d_m + 5 kappa * epsilon                           (4.2)

(c) Therefore W(1) > W(q) for all q >= 2 whenever:

    epsilon < epsilon* := d_m / (2 C_pert) = d_m^2 / (5 d_1)        (4.3)

with margin:

    W(1) - max_{q >= 2} W(q) >= 2 d_m - 4 C_pert * epsilon
                               = 2 d_m - 10 kappa * epsilon         (4.4)

(d) For the physically important case D = d * I_m (kappa = 1, C_pert = 5/2):

    W(1) > W(q)   whenever   epsilon < d / 5                        (4.5)

    Margin >= 2d - 10 epsilon                                        (4.6)

    In terms of the off-diagonal ratio rho := epsilon / d:

    W(1) > W(q)   whenever   rho < 1/5                              (4.7)

### 4.2 Key Lemma: Eigenvalue Perturbation Bound

**Lemma 4.1** (Eigenvalue Perturbation for the Signed Kernel). Let
F = D + epsilon * E with the conditions of Theorem 2. Let A_0(S) = D^{1/2} S D^{1/2}
be the unperturbed signed kernel and A(S) = F^{1/2} S F^{1/2} be the perturbed
signed kernel. Then for each i:

    |d_i(A(S)) - d_i(A_0(S))| <= C_pert * epsilon                   (4.8)

where C_pert = (5/2) kappa = (5/2) d_1 / d_m.

For the case kappa = 1 (D proportional to identity): C_pert = 5/2.

**Proof of Lemma 4.1.**

We bound ||A(S) - A_0(S)||_op and then apply Weyl's inequality.

**Step 1: Factorization of F^{1/2}.**

Write F = D^{1/2}(I + G) D^{1/2} where G := epsilon D^{-1/2} E D^{-1/2}.
Then:

    ||G||_op <= epsilon ||D^{-1/2}||_op^2 ||E||_op = epsilon / d_m < 1/2

since epsilon < d_m / 2. The matrix I + G is positive definite, and:

    F^{1/2} = D^{1/2} (I + G)^{1/2}

Define H := (I + G)^{1/2} - I. By the power series expansion
(I + G)^{1/2} = I + G/2 - G^2/8 + ..., which converges for ||G||_op < 1,
we obtain the bound:

    ||H||_op <= ||G||_op / (1 - ||G||_op)

For ||G||_op <= epsilon/d_m < 1/2, this gives:

    ||H||_op <= (epsilon/d_m) / (1 - epsilon/d_m) <= 2 epsilon / d_m

(using 1/(1 - x) <= 2 for x <= 1/2). A tighter bound follows from the
fact that the coefficients of the power series of (1+x)^{1/2} - 1 satisfy
|c_1| + |c_2| + ... = 1 (they sum to (1+x)^{1/2} - 1 at x = 1, which
equals sqrt(2) - 1 < 1). So actually ||H||_op <= ||G||_op for ||G|| < 1/2.

We use the conservative bound:

    ||H||_op <= epsilon / d_m                                        (4.9)

**Step 2: Bound on ||A(S) - A_0(S)||_op.**

Expanding A(S) = D^{1/2}(I+H) S (I+H) D^{1/2}:

    A(S) = D^{1/2} S D^{1/2} + D^{1/2}(HS + SH + HSH) D^{1/2}
         = A_0(S) + D^{1/2}(HS + SH + HSH) D^{1/2}

Since ||S||_op = 1 (S is a signature matrix):

    ||HS + SH + HSH||_op <= 2||H||_op * ||S||_op + ||H||_op^2 * ||S||_op
                         = 2||H||_op + ||H||_op^2

Substituting (4.9) and using epsilon < d_m/2 so epsilon^2/d_m^2 < epsilon/(2 d_m):

    2||H||_op + ||H||_op^2 <= 2 epsilon/d_m + epsilon^2/d_m^2
                            <= 2 epsilon/d_m + epsilon/(2 d_m)
                            = (5/2) epsilon / d_m

Therefore:

    ||A(S) - A_0(S)||_op <= ||D^{1/2}||_op^2 * (5/2) epsilon / d_m
                         = d_1 * (5/2) epsilon / d_m
                         = (5/2) kappa * epsilon                     (4.10)

**Step 3: Apply Weyl's inequality.**

By Weyl's inequality (Lemma 2.2):

    |d_i(A(S)) - d_i(A_0(S))| <= ||A(S) - A_0(S)||_op <= (5/2) kappa * epsilon

This gives C_pert = (5/2) kappa = (5/2) d_1/d_m.  []

**Remark on the condition number dependence.** The bound involves
kappa = d_1/d_m. For the physical case D = d * I_m (Ising on trees with
uniform coupling), kappa = 1 and C_pert = 5/2. For general diagonal D with
large condition number, the perturbation bound degrades, which is expected:
a poorly conditioned diagonal matrix amplifies off-diagonal perturbations.
The threshold epsilon* = d_m/(2 C_pert) = d_m^2/(5 d_1) decreases with
kappa, reflecting this sensitivity.

### 4.3 Proof of Theorem 2

**Proof of (a):** For q = 1 with the sign flip at index 1:

The unperturbed signed kernel has eigenvalues
{-d_1, d_2, ..., d_m}. So d_1(A_0) = -d_1 and d_2(A_0) = d_m (the
minimum among {d_2, ..., d_m}).

The unperturbed spectral gap is:

    W_0(1) = d_2(A_0) - d_1(A_0) = d_m - (-d_1) = d_m + d_1

By Lemma 4.1, each eigenvalue of A(S) differs from the corresponding
eigenvalue of A_0(S) by at most C_pert * epsilon. The Weyl bound is
two-sided: for each i,

    d_i(A_0) - C_pert epsilon <= d_i(A) <= d_i(A_0) + C_pert epsilon

The worst case for the gap W = d_2 - d_1 occurs when d_2 decreases and
d_1 increases simultaneously:

    W(1) = d_2(A) - d_1(A)
         >= (d_2(A_0) - C_pert epsilon) - (d_1(A_0) + C_pert epsilon)
         = W_0(1) - 2 C_pert epsilon
         = (d_1 + d_m) - 2 C_pert epsilon                           (4.11)

**Proof of (b):** For q >= 2 with any sign assignment, the two most negative
eigenvalues of A_0(S) are -d_{j_1} and -d_{j_2} (where d_{j_1} >= d_{j_2}
are the two largest flipped diagonal entries). The unperturbed gap is:

    W_0(q) = d_{j_1} - d_{j_2}

The worst case for W(q) is when d_2(A) increases and d_1(A) decreases:

    W(q) = d_2(A) - d_1(A)
         <= (d_2(A_0) + C_pert epsilon) - (d_1(A_0) - C_pert epsilon)
         = W_0(q) + 2 C_pert epsilon

The maximum over sign assignments gives:

    max_{S} W_0(q) = d_1 - d_m   (from Theorem 1(b))

Therefore:

    W(q) <= (d_1 - d_m) + 2 C_pert epsilon                          (4.12)

**Proof of (c):** Combining (4.11) and (4.12):

    W(1) - max_{q >= 2} W(q) >= [(d_1 + d_m) - 2 C_pert epsilon]
                                - [(d_1 - d_m) + 2 C_pert epsilon]
                               = 2 d_m - 4 C_pert epsilon           (4.13)

This is positive whenever:

    epsilon < epsilon* := d_m / (2 C_pert) = d_m / (5 kappa)
                        = d_m^2 / (5 d_1)                            (4.14)

**Proof of (d):** For D = d * I_m (kappa = 1, C_pert = 5/2):

    epsilon* = d / 5                                                  (4.18)

    Margin >= 2d - 10 epsilon     (for epsilon < d/5)                (4.19)

In terms of the off-diagonal ratio rho = epsilon/d:

    W(1) > W(q)   whenever   rho < 1/5                              (4.20)

**QED.**

### 4.4 Comparison with Interlacing-Based Bound

We can obtain a sharper bound for the q=1 case by using the interlacing
theorem directly, without the Weyl perturbation bound.

**Proposition 4.2** (Sharp q=1 Bound via Interlacing). Under the conditions
of Theorem 2, for q = 1 with the sign flip at index k:

(i) A(S_1) has exactly one negative eigenvalue.

(ii) d_2(A(S_1)) >= lambda_min(F) >= d_m - epsilon.

(iii) W(1) >= lambda_min(F) + |d_1(A)|.

**Proof.** Part (i): By Lemma 2.1 (Cauchy interlacing), applied to
A(S_1) = F - 2 f_k f_k^T where f_k = F^{1/2} e_k: the second eigenvalue
of A satisfies d_2(A) >= lambda_1(F) = lambda_min(F) > 0. Since A is
obtained from F by subtracting a rank-1 PSD matrix, A has at most one
eigenvalue below lambda_min(F). The vector f_k/||f_k|| gives
(f_k/||f_k||)^T A (f_k/||f_k||) = ||f_k||^2 - 2||f_k||^2 = -||f_k||^2 < 0,
so A has at least one negative eigenvalue. Therefore exactly one. []

Part (ii): By interlacing, d_2(A) >= lambda_min(F). By Weyl's inequality
applied to F = D + epsilon E: lambda_min(F) >= d_m - epsilon. []

Part (iii): W(1) = d_2(A) - d_1(A) = d_2(A) + |d_1(A)| >= lambda_min(F) + |d_1(A)|.

Since |d_1(A)| > 0 and lambda_min(F) >= d_m - epsilon > 0:

    W(1) >= d_m - epsilon + |d_1(A)| > d_m - epsilon               (4.21)

To get a tighter lower bound on |d_1(A)|, we use the trace:

    tr(A) = tr(F^{1/2} S F^{1/2}) = tr(S F) = sum_j s_j F_{jj}

For q = 1 with s_k = -1:

    tr(A) = sum_{j != k} F_{jj} - F_{kk} = tr(F) - 2 F_{kk}

The sum of eigenvalues equals the trace:

    d_1(A) + sum_{i=2}^{m} d_i(A) = tr(F) - 2 F_{kk}

Since d_i(A) <= lambda_max(F) <= d_1 + epsilon for i >= 2:

    d_1(A) >= tr(F) - 2 F_{kk} - (m-1)(d_1 + epsilon)

This gives a lower bound on d_1(A) (which is negative), hence an upper bound
on |d_1(A)|. For the purpose of a lower bound on W, the interlacing result
(ii) already provides the key improvement: the d_2(A) >= lambda_min(F)
bound is EXACT from interlacing, not approximate. []

**Remark.** The interlacing theorem provides a "one-sided" improvement: it
sharpens the lower bound on d_2(A) for q=1 (using the structural fact that
only one eigenvalue can drop below lambda_min(F)), but does not help bound
the q >= 2 case. The full Theorem 2 still requires Weyl for the upper bound
on W(q >= 2).

### 4.5 The Physical Case: D = sech^2(J) * I_m

For the Ising model on a tree with uniform coupling J, F_tree = sech^2(J) * I_m.
For a sparse graph with girth g, F = F_tree + epsilon E where
epsilon = O(tanh^{g-2}(J)) by correlation decay (Dobrushin-Shlosman).

In this case d_1 = d_m = d = sech^2(J), so kappa = 1 and:

    C_pert = 5/2

    epsilon* = d/5 = sech^2(J)/5                                    (4.22)

The condition for Lorentzian selection is:

    epsilon < sech^2(J)/5

which, using epsilon = C(Delta, J) * tanh^{g-2}(J) * sech^2(J), becomes:

    C(Delta, J) * tanh^{g-2}(J) < 1/5                               (4.23)

This is the explicit version of the implicit threshold in the Main Theorem
of the original proof, with the constant 1/5 replacing the uncomputed c_4.

For weak coupling (J << 1): tanh(J) approx J and C(Delta, J) approx K * Delta * J.
The condition becomes K * Delta * J^{g-1} < 1/5, which is satisfied for all
J < (5 K Delta)^{-1/(g-1)}. For g >= 5 and moderate Delta, this allows J
up to O(1).

For strong coupling (J >> 1): tanh(J) -> 1 and C(Delta, J) grows as
K * Delta * e^{2J}/4. The condition K * Delta * e^{2J}/4 < 1/5 gives
J < (1/2) log(4/(5 K Delta)), which is negative for K * Delta > 4/5.
Therefore the perturbative regime is limited to moderate J for dense graphs.

---

## 5. Failed Directions and Counterexamples

### 5.1 The General Conjecture as Originally Stated

The original conjecture proposed a gap bound:

    gap(q=1) >= 2 f_min / kappa(F)

for GENERAL positive definite F (not necessarily near-diagonal). This
fails.

**Counterexample 5.1.** Let m = 3, F = [[4, 3, 0], [3, 4, 0], [0, 0, 1]].
F is positive definite with eigenvalues {7, 1, 1}. The condition number
is kappa(F) = 7.

We use the similarity A(S) = F^{1/2} S F^{1/2} ~ S F (since
F^{1/2} S F^{1/2} = F^{1/2} (S F) F^{-1/2}), which allows us to
compute eigenvalues of A(S) by finding eigenvalues of S F.

**For q = 1**, flipping index 1 (largest diagonal entry d_1 = 4):

    S_1 F = diag(-1,1,1) * [[4,3,0],[3,4,0],[0,0,1]]
          = [[-4,-3,0],[3,4,0],[0,0,1]]

    det(S_1 F - lambda I) = (-4-lambda)(4-lambda)(1-lambda) + 9(1-lambda)
    = (1-lambda)[(-4-lambda)(4-lambda) + 9]
    = (1-lambda)[lambda^2 - 16 + 9]
    = (1-lambda)(lambda^2 - 7) = 0

    eigenvalues: {-sqrt(7), 1, sqrt(7)} = {-2.646, 1, 2.646}

    W(q=1) = d_2 - d_1 = 1 - (-sqrt(7)) = 1 + sqrt(7) = 3.646

**For q = 2**, flipping indices 1 and 2:

    S_2 F = diag(-1,-1,1) * [[4,3,0],[3,4,0],[0,0,1]]
          = [[-4,-3,0],[-3,-4,0],[0,0,1]]

    det(S_2 F - lambda I) = [(-4-lambda)(-4-lambda) - 9](1-lambda)
    = [(lambda+4)^2 - 9](1-lambda)
    = (lambda+1)(lambda+7)(1-lambda) = 0

    eigenvalues: {-7, -1, 1}

    W(q=2) = d_2 - d_1 = -1 - (-7) = 6

Therefore W(q=1) = 3.646 < 6 = W(q=2). **Lorentzian selection FAILS.**

This counterexample shows that for GENERAL positive definite F (with
significant off-diagonal structure), the rank-1 argument does not guarantee
Lorentzian selection. The off-diagonal entries (F_{12} = 3) create strong
eigenvalue mixing that disrupts the isolation mechanism.

**Root cause:** The matrix F in this example has eigenvalues {7, 1, 1}.
The large ratio lambda_max/lambda_min = 7 combined with the specific
eigenvector structure means that the rank-1 sign flip at the "wrong"
index produces a large negative eigenvalue but the gap is not maximized
because the eigenvector of the negative eigenvalue overlaps strongly with
multiple coordinate directions.

More fundamentally: the counterexample has ||F - diag(F)||_op/||diag(F)||_op = 3/4
= 0.75, which is well above the threshold epsilon* = d_m/5 = 1/5 from
Theorem 2. So the counterexample is outside the perturbative regime, as
expected.

### 5.2 What Additional Conditions Are Needed

The counterexample in Section 5.1 shows that the conjecture fails for
general PD matrices. The failure mode is:

1. **Large off-diagonal entries** create strong eigenvector mixing.
2. For q >= 2, the signed kernel S_q F can align the negative eigenspace
   with a high-eigenvalue direction of F, producing a LARGE negative
   eigenvalue with a LARGE gap to the next.
3. For q = 1, the rank-1 constraint limits the negative eigenvalue to
   interact with only one direction, which may not capture the full
   eigenvalue range of F.

The precise condition needed is **near-diagonality**: ||F - diag(F)|| must
be small relative to the diagonal spread. Theorem 2 quantifies this as
epsilon < d_m^2 / (5 d_1).

### 5.3 Attempted Strengthening: Condition Number Bound

One might hope that the condition could be relaxed to a condition on
kappa(F) alone (without requiring near-diagonality). This also fails.

**Counterexample 5.2.** Take F = [[2, 1], [1, 2]] with m = 2. Eigenvalues
{3, 1}, kappa = 3. But m = 2 makes the comparison vacuous (q can only be 1
or 2, and q = m is trivial). For m >= 3, the counterexample in 5.1 with
kappa(F) = 7 shows that even moderate condition numbers allow failure.

The key insight is that the condition number of F is necessary but not
sufficient: the ALIGNMENT of F's eigenvectors with the coordinate axes
(which determines how close F is to diagonal) is the crucial factor.

---

## 6. Comparison with Three-Stage Proof

### 6.1 Architecture Comparison

| Aspect | Three-Stage (A, B, C) | Rank-1 Approach |
|--------|----------------------|-----------------|
| **Number of theorems** | 3 + 5 lemmas | 2 + 2 lemmas |
| **Central idea** | Case-by-case analysis | Rank-1 vs rank-q dichotomy |
| **Diagonal case** | Theorem A (direct) | Theorem 1 (via secular eq.) |
| **Near-diagonal** | Proposition B (sketch) | Theorem 2 (explicit bound) |
| **Graph theory** | Theorem C (separate) | Not included (same input) |
| **Constants** | Implicit (c_1 -- c_4) | Explicit (C_pert = 5/2 kappa) |
| **Threshold** | Implicit (epsilon*) | Explicit (d_m^2 / (5 d_1)) |
| **Conceptual unity** | Moderate (three stages) | High (one principle) |

### 6.2 Strengths of the Rank-1 Approach

1. **Conceptual clarity.** The entire argument reduces to a single
   structural observation: a rank-1 perturbation creates one isolated
   eigenvalue (by interlacing), while a rank-q perturbation creates q
   clustered eigenvalues. The competition between isolation (large gap)
   and clustering (small gap) is the ENTIRE content of the theorem.

2. **Explicit constants.** The perturbation bound C_pert = (5/2) kappa
   and the threshold epsilon* = d_m^2/(5 d_1) are explicitly computed,
   unlike the implicit c_1 -- c_4 in Proposition B.

3. **The "sum vs difference" insight.** The deepest algebraic reason for
   Lorentzian selection is exposed: W(1) = d_1 + d_m (sum) vs
   W(q >= 2) <= d_1 - d_m (difference), and a sum of positive numbers
   always exceeds their difference. This makes the result feel inevitable
   rather than accidental.

4. **Natural connection to spiked covariance models.** The rank-1
   perturbation framework connects directly to the Baik-Ben Arous-Peche
   phase transition in random matrix theory, where a rank-1 signal
   creates an outlier eigenvalue. Our result is the deterministic analog:
   a rank-1 sign flip creates an outlier NEGATIVE eigenvalue.

### 6.3 Weaknesses of the Rank-1 Approach

1. **Same perturbative limitation.** The rank-1 approach still requires
   near-diagonality for the non-tree case. It does not extend to general
   PD matrices (counterexample in Section 5.1).

2. **Kappa dependence.** The explicit threshold epsilon* = d_m^2/(5 d_1)
   degrades with the condition number of D. For D proportional to
   identity (kappa = 1), this gives epsilon* = d/5, which is reasonable.
   For large kappa, the threshold is restrictive.

3. **Does not replace Theorem C.** The graph-theoretic content (connecting
   girth and sparsity to near-diagonality) is not addressed by the rank-1
   approach. Theorem C (or an equivalent) is still needed to close the
   chain from graph structure to near-diagonality.

### 6.4 Assessment: Complementary, Not Replacement

The rank-1 approach is **stronger** than the three-stage proof in the
following sense:

- It provides a conceptually unified proof of the diagonal + near-diagonal
  results (replacing Theorem A + Proposition B with a single framework).
- It gives explicit constants where the original had implicit ones.
- It identifies the "sum vs difference" algebraic mechanism.

It is **weaker** in the following sense:

- It does not address the graph-theoretic connection (Theorem C).
- The counterexample shows the approach cannot be extended to general
  positive definite matrices without near-diagonality.

**Recommendation:** Use the rank-1 approach as the PRIMARY proof for the
algebraic selection result (Theorems 1 and 2), and retain Theorem C as
the bridge from graph theory to the near-diagonality condition. This
replaces the three-stage (A, B, C) architecture with a two-stage
(Rank-1 + Graph Theory) architecture:

```
Graph structure (Delta, g)
    |
    | [Theorem C: correlation decay (unchanged)]
    v
Near-diagonal Fisher: ||F - D||/||D|| <= C(Delta,J) * tanh^{g-2}(J)
    |
    | [Theorem 2: rank-1 vs rank-q perturbation (NEW, explicit constants)]
    v
Lorentzian selection: W(1) > W(q >= 2)
    |
    | [Theorem 1: algebraic identity d_1+d_m > d_1-d_m (CLEANER)]
    v
Mechanism: sum > difference when d_m > 0
```

---

## 7. LaTeX-Ready Theorem Statements

### 7.1 Theorem 1 (Diagonal Case)

```latex
\begin{theorem}[Rank-1 Isolation Implies Lorentzian Selection -- Diagonal Case]
\label{thm:rank1-diagonal}
Let $F = D = \operatorname{diag}(d_1, \ldots, d_m)$ be a positive definite
diagonal matrix with $d_1 \geq d_2 \geq \cdots \geq d_m > 0$ and $m \geq 3$.
For a sign assignment $S_q$ with exactly $q$ entries equal to $-1$, define
the signed metric kernel $A(S_q) = D^{1/2} S_q D^{1/2}$ and the spectral
gap weighting $W(S_q) = d_2(A) - d_1(A)$ where $d_1(A) \leq d_2(A) \leq
\cdots \leq d_m(A)$ are the ordered eigenvalues of $A$.

Then:
\begin{enumerate}[(a)]
\item $W(1) = d_1 + d_m$, achieved by flipping the index of $d_1$.
\item $W(q) \leq d_1 - d_m$ for all $q \geq 2$, with equality at $q = 2$.
\item $W(1) - \max_{q \geq 2} W(q) \geq 2\,d_m > 0$.
\item When $D = d \cdot I_m$: $W(1) = 2d$ and $W(q) = 0$ for all $q \geq 2$.
\end{enumerate}

The mechanism is the rank-1 isolation principle: for $q = 1$, the signed
kernel $A(S_1) = D - 2\,d_k\, e_k e_k^\top$ is a rank-1 perturbation of $D$,
producing exactly one negative eigenvalue $-d_k$ isolated from the positive
bulk by a gap of $d_m + d_k$ (a \emph{sum}). For $q \geq 2$, the $q$
negative eigenvalues cluster, giving a gap of at most $d_1 - d_m$
(a \emph{difference}).
\end{theorem}
```

### 7.2 Theorem 2 (Near-Diagonal Case)

```latex
\begin{theorem}[Rank-1 Isolation for Near-Diagonal Matrices]
\label{thm:rank1-neardiag}
Let $F = D + \varepsilon E$ be an $m \times m$ positive definite matrix where
$D = \operatorname{diag}(d_1, \ldots, d_m)$ with $d_1 \geq \cdots \geq d_m > 0$,
$\|E\|_{\mathrm{op}} \leq 1$, and $0 \leq \varepsilon < d_m / 2$. Let
$\kappa = d_1 / d_m$ be the condition number of $D$.

Then:
\begin{enumerate}[(a)]
\item $W(1) \geq (d_1 + d_m) - 5\kappa\,\varepsilon$.
\item $W(q) \leq (d_1 - d_m) + 5\kappa\,\varepsilon$ for all $q \geq 2$.
\item $W(1) > W(q)$ for all $q \geq 2$ whenever
      $\varepsilon < \varepsilon^* := d_m^2 / (5\,d_1)$.
\item The margin satisfies
      $W(1) - \max_{q \geq 2} W(q) \geq 2\,d_m - 10\kappa\,\varepsilon$.
\end{enumerate}

For the Ising model on a sparse graph with girth $g$ and maximum degree
$\Delta$, the perturbation $\varepsilon = C(\Delta, J) \cdot
\tanh^{g-2}(J) \cdot \operatorname{sech}^2(J)$ from correlation decay.
In the physical case $D = \operatorname{sech}^2(J) \cdot I_m$ ($\kappa = 1$),
the threshold becomes $C(\Delta, J) \cdot \tanh^{g-2}(J) < 1/5$.
\end{theorem}
```

### 7.3 Corollary (Application to Trees)

```latex
\begin{corollary}[Tree Observer Selection]
\label{cor:tree-selection}
For the Ising model on any tree graph with uniform coupling $J > 0$,
the Fisher matrix $F = \operatorname{sech}^2(J) \cdot I_m$ (Tree Fisher
Identity). By Theorem~\ref{thm:rank1-diagonal}(d):
\[
  W(1) = 2\,\operatorname{sech}^2(J) > 0 = W(q)
  \quad \text{for all } q \geq 2.
\]
Lorentzian signature is selected with infinite margin ($W(1)/W(q) = \infty$).
The mechanism is rank-1 isolation: the single sign flip produces a
spectrally isolated negative eigenvalue, while multiple sign flips produce
degenerate (zero-gap) negative eigenvalues.
\end{corollary}
```

---

## Appendix A: Summary of Named Theorems Used

| Theorem | Reference | Where Used |
|---------|-----------|------------|
| Cauchy Interlacing | Bhatia (1997), Thm III.1.5 | Lemma 2.1 |
| Weyl's Inequality | Horn & Johnson (2012), Thm 4.3.1 | Lemma 2.2, Theorem 2 |
| Courant-Fischer Minimax | Horn & Johnson (2012), Thm 4.2.11 | Proof of Lemma 2.1 |
| Correlation Decay | Dobrushin & Shlosman (1985) | Section 4.5 (cited) |
| Tree Fisher Identity | Lemma 6.1 of spectral-gap-selection-theorem.md | Corollary |

## Appendix B: The "Sum vs. Difference" Principle

The core algebraic content of the entire theorem is captured by the
following elementary inequality:

**For any a >= b > 0:**

    a + b > a - b    iff    2b > 0

This is the "sum vs difference" principle. In the context of Lorentzian
selection:

- a = d_1 (largest diagonal entry of F)
- b = d_m (smallest diagonal entry of F)
- a + b = W(q=1) (spectral gap for rank-1 sign flip)
- a - b = W(q=2) (spectral gap for rank-2 sign flip)

The positive definiteness of F guarantees b > 0, which is the ONLY
condition needed for Lorentzian selection in the diagonal case.

In the near-diagonal case, the perturbation smears this inequality by
O(epsilon), and the theorem quantifies how much smearing is tolerable
before the inequality reverses.

---

*Rank-1 Interlacing Proof of Lorentzian Selection. The rank-1 sign flip
creates a spectrally isolated negative eigenvalue (by Cauchy interlacing);
multiple sign flips create clustered negative eigenvalues (by Weyl
perturbation). The resulting spectral gap inequality W(1) = d_1 + d_m >
d_1 - d_m >= W(q >= 2) holds for all positive definite diagonal matrices
and persists under near-diagonal perturbations with epsilon < d_m^2/(5 d_1).
The algebraic mechanism is the elementary inequality: a sum of positive
numbers exceeds their difference.*
