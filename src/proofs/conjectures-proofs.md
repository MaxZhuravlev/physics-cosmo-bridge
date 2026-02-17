# Proofs and Analysis of Conjectures 1, 2, and 5 from Paper #5

**Author:** Max Zhuravlev (with mathematical formalization assistance)
**Date:** 2026-02-17
**Status:** Conjecture 2 PROVEN; Conjecture 5 PARTIALLY PROVEN; Conjecture 1 PARTIALLY PROVEN
**Depends on:** spectral-gap-selection-theorem.md (Theorems A, B, C)

---

## Table of Contents

1. [Conjecture 2: Tree Absolute Selection (PROVEN)](#conjecture-2-tree-absolute-selection)
2. [Conjecture 5: Girth-Coupling Duality (PARTIALLY PROVEN)](#conjecture-5-girth-coupling-duality)
3. [Conjecture 1: Sparse Universality (PARTIALLY PROVEN)](#conjecture-1-sparse-universality)
4. [Summary and LaTeX-Ready Statements](#summary-and-latex-ready-statements)

---

## Conjecture 2: Tree Absolute Selection

### Statement

**Conjecture 2** (Tree Absolute Selection). On any tree graph,
$W(1)/W(q \geq 2) = \infty$ (infinite margin) for all $J$.

### Status: PROVEN (upgraded to Theorem)

This follows immediately from existing results. The proof is short and
complete.

### Proof

**Theorem 2' (Tree Absolute Selection).** Let $G = (V, E)$ be any tree
graph with $|E| = m \geq 2$ edges and arbitrary coupling parameters
$\mathbf{J} = (J_{e_1}, \ldots, J_{e_m})$ with $|J_e| < \infty$ for all
$e$. Then:

(a) **Uniform coupling** ($J_e = J$ for all $e$):

$$W(q \geq 2) = 0 \quad \text{and} \quad W(1) = 2\operatorname{sech}^2(J) > 0$$

so $W(1)/W(q \geq 2) = \infty$.

(b) **Non-uniform coupling** ($J_e$ varying):

$$W(1) = d_{\min} + d_{\max} > d_{\max} - d_{\min} = W(q \geq 2) \geq 0$$

where $d_{\min} = \operatorname{sech}^2(\max_e |J_e|)$ and
$d_{\max} = \operatorname{sech}^2(\min_e |J_e|)$. The ratio $W(1)/W(q \geq 2)
= \infty$ if and only if all $|J_e|$ are equal.

**Proof.** The argument proceeds in three steps.

**Step 1: Tree Fisher Identity (Lemma 6.1 of the main proof).**

On any tree $G$, the Fisher information matrix is exactly diagonal:

$$F = \operatorname{diag}(\operatorname{sech}^2(J_{e_1}), \ldots, \operatorname{sech}^2(J_{e_m}))$$

This is proven in Lemma 6.1 of spectral-gap-selection-theorem.md. The key
mechanism is that on a tree, the edge observables $\phi_e = \sigma_i \sigma_j$
are mutually independent under the Boltzmann distribution, because the
Hamiltonian $H = -\sum_e J_e \phi_e$ factorizes in the edge variable
representation (there are no cycles to create dependencies).

**Step 2: For any diagonal PD matrix, $W(q \geq 2) = 0$ when $q \geq 2$ negative
eigenvalues exist with two equal.**

For $F = D = \operatorname{diag}(d_1, \ldots, d_m)$ with all $d_i > 0$,
consider any sign assignment $S$ with exactly $q \geq 2$ negative entries at
positions $j_1, \ldots, j_q$. The signed metric kernel is:

$$A(S) = D^{1/2} S D^{1/2} = S D = \operatorname{diag}(s_1 d_1, \ldots, s_m d_m)$$

since $D^{1/2}$ is diagonal and commutes with $S$. The eigenvalues of $A(S)$
include the $q$ negative values $\{-d_{j_1}, \ldots, -d_{j_q}\}$ and the
$(m - q)$ positive values $\{d_i : s_i = +1\}$.

The two most negative eigenvalues are:
- $d_1(A) = -\max(d_{j_1}, \ldots, d_{j_q})$
- $d_2(A) = -\operatorname{second\text{-}max}(d_{j_1}, \ldots, d_{j_q})$

The spectral gap ratio is:

$$L_{\mathrm{gap}} = \frac{d_2(A) - d_1(A)}{|d_1(A)|}$$

Now compute:

$$W(S) = \beta_c \cdot L_{\mathrm{gap}} = |d_1(A)| \cdot \frac{d_2(A) - d_1(A)}{|d_1(A)|} = d_2(A) - d_1(A)$$

Substituting:

$$W(S) = \max_k d_{j_k} - \operatorname{second\text{-}max}_k d_{j_k}$$

This is the difference between the two largest diagonal entries among the
flipped indices. To compute $W(q) = \max_S W(S)$ over all choices of $q$
indices:

For **uniform coupling** $J_e = J$ for all $e$: all diagonal entries are
equal, $d_i = \operatorname{sech}^2(J)$ for all $i$. Therefore:

$$\max_k d_{j_k} = \operatorname{second\text{-}max}_k d_{j_k} = \operatorname{sech}^2(J)$$

and $W(S) = 0$ for **every** sign assignment with $q \geq 2$.

For **non-uniform coupling**: the diagonal entries $d_i = \operatorname{sech}^2(J_{e_i})$
may differ. The maximum $W(q)$ over all sign assignments with $q \geq 2$ is:

- For $q = 2$: choose the indices $j_1, j_2$ to maximize
  $|d_{j_1} - d_{j_2}|$. This gives $W(2) = d_{\max} - d_{\min}$ where
  $d_{\max} = \max_i d_i$ and $d_{\min} = \min_i d_i$.

- For $q \geq 3$: choose the $q$ indices to maximize the gap between the
  two largest. The optimal choice includes $d_{\max}$ and then $q - 1$
  values as small as possible. The second-largest among the chosen set is
  maximized at $d_{(2)}$ (the second-smallest diagonal entry overall, in
  ascending ordering) when $q = 3$, giving $W(3) \leq d_{\max} - d_{(2)}
  \leq d_{\max} - d_{\min}$.

Therefore $W(q) \leq d_{\max} - d_{\min}$ for all $q \geq 2$, with equality
at $q = 2$.

**Key observation for trees:** Even in the non-uniform case, $W(q \geq 2)$
is FINITE (equals $d_{\max} - d_{\min}$), while $W(1)$ is also finite
(equals $d_{\min} + d_{\max}$). The ratio $W(1)/W(q \geq 2) =
(d_{\min} + d_{\max})/(d_{\max} - d_{\min})$, which is finite but greater
than 1. The infinite ratio claim specifically holds when all couplings are
equal (uniform $J$).

**Correction to the conjecture statement:** The conjecture as stated --
"$W(1)/W(q \geq 2) = \infty$ for all $J$" -- is TRUE when $J$ denotes a
uniform coupling (scalar), since all diagonal entries of $F$ are equal
($\operatorname{sech}^2(J)$), giving $W(q \geq 2) = 0$.

For non-uniform couplings $\mathbf{J} = (J_1, \ldots, J_m)$ with
$J_i \neq J_j$ for some $i, j$, the ratio is finite but always greater than
1 (by Theorem A).

**Step 3: $W(1) > 0$ for all trees.**

By Theorem A(a) (or Corollary A.2 for non-uniform coupling):

$$W(1) = d_{\min} + d_{\max}$$

where $d_{\min} = \min_e \operatorname{sech}^2(J_e) > 0$ (since
$\operatorname{sech}^2(J) > 0$ for all finite $J$) and $d_{\max} > 0$.
Therefore $W(1) \geq 2 d_{\min} > 0$.

**Conclusion.** For trees with uniform coupling:

$$W(1) = 2\operatorname{sech}^2(J) > 0 = W(q \geq 2) \quad \Rightarrow \quad W(1)/W(q \geq 2) = \infty$$

For trees with non-uniform coupling:

$$W(1) = d_{\min} + d_{\max} > d_{\max} - d_{\min} = W(q \geq 2) \geq 0$$

with strict inequality $W(1) > W(q \geq 2)$ always, and
$W(1)/W(q \geq 2) = \infty$ if and only if all couplings are equal.

$\blacksquare$

### Remark on Interpretation

The physical significance is that on trees, Lorentzian signature ($q = 1$)
is selected with **zero competition** from higher signatures when couplings
are uniform. The mechanism is transparent: the Fisher matrix is exactly
proportional to the identity, so flipping one sign creates a single isolated
negative eigenvalue (spectral gap = 2d), while flipping two or more creates
degenerate negative eigenvalues (spectral gap = 0).

For non-uniform couplings on trees, the infinite margin degrades to a finite
margin, but the selection $W(1) > W(q \geq 2)$ is still unconditional --
no constraint on $J$ is needed.

---

## Conjecture 5: Girth-Coupling Duality

### Statement

**Conjecture 5** (Girth-Coupling Duality). The critical coupling
$J_{\mathrm{crit}}(g)$ for graphs with girth $g$ and fixed degree $\Delta$
satisfies $J_{\mathrm{crit}}(g) \sim c \cdot g^\alpha$ for universal
exponents $c, \alpha > 0$.

### Status: PARTIALLY PROVEN

We derive the functional form of $J_{\mathrm{crit}}(g)$ from the
near-diagonal condition (Theorem C + Proposition B). The result is that
$J_{\mathrm{crit}}(g)$ grows with $g$, but the growth is NOT a power law
$c \cdot g^\alpha$ as conjectured. Instead, $J_{\mathrm{crit}}(g)$ grows
faster than any polynomial for large $g$. The conjecture is PARTIALLY
REFUTED in its specific claim about power-law scaling, but the underlying
phenomenon (larger girth permits stronger coupling) is confirmed and given
an exact asymptotic.

### Analysis

**Step 1: The implicit equation for $J_{\mathrm{crit}}$.**

From Theorem C (near-diagonal Fisher) and Proposition B (perturbation
stability), Lorentzian selection holds when:

$$C(\Delta, J) \cdot \tanh^{g-2}(J) < \varepsilon^*(\Delta, m) \tag{5.1}$$

where $C(\Delta, J) = K \Delta \sinh(J)\cosh(J)$ and $\varepsilon^*$ is the
near-diagonal threshold from Proposition B (implicit, involving constants
$c_1$--$c_4$).

The critical coupling $J_{\mathrm{crit}}(g)$ is the solution to:

$$K \Delta \sinh(J)\cosh(J) \cdot \tanh^{g-2}(J) = \varepsilon^* \tag{5.2}$$

**Step 2: Rewrite in terms of elementary functions.**

Using $\sinh(J)\cosh(J) = \frac{1}{2}\sinh(2J)$ and
$\tanh(J) = 1 - 2/(e^{2J} + 1)$, the equation becomes complicated for
finite $J$. We analyze the asymptotic regimes.

**Step 3: Small $J$ asymptotic (perturbative regime).**

For $J \ll 1$: $\tanh(J) \approx J$, $\sinh(J)\cosh(J) \approx J$. The
condition (5.2) becomes:

$$K \Delta \cdot J \cdot J^{g-2} = K \Delta \cdot J^{g-1} = \varepsilon^*$$

Solving: $J_{\mathrm{crit}} = (\varepsilon^* / (K\Delta))^{1/(g-1)}$.

For large $g$: $J_{\mathrm{crit}} \to 1$ from below (the $(g-1)$-th root
of a constant approaches 1). But this is the wrong regime -- we want the
large-$J$ behavior, since increasing girth should INCREASE $J_{\mathrm{crit}}$.

**Step 4: Large $J$ asymptotic (strong coupling regime).**

For $J \gg 1$: $\tanh(J) \to 1 - 2e^{-2J}$, $\sinh(J)\cosh(J) \sim
\frac{1}{4}e^{2J}$. The condition (5.2) becomes:

$$K\Delta \cdot \frac{1}{4}e^{2J} \cdot (1 - 2e^{-2J})^{g-2} \approx
K\Delta \cdot \frac{1}{4}e^{2J} \cdot e^{-2(g-2)e^{-2J}} = \varepsilon^*$$

Using $(1 - x)^n \approx e^{-nx}$ for small $x$:

$$\frac{K\Delta}{4} \cdot e^{2J} \cdot e^{-2(g-2)e^{-2J}} = \varepsilon^*$$

Taking logarithms:

$$2J - 2(g-2)e^{-2J} = \ln\frac{4\varepsilon^*}{K\Delta}$$

For large $g$ with $J = J_{\mathrm{crit}}$, both terms must balance. Setting
$u = e^{-2J}$ (so $J = -\frac{1}{2}\ln u$):

$$-\ln u - 2(g-2)u = \ln\frac{4\varepsilon^*}{K\Delta}$$

For large $g$, $u$ must be small (i.e., $J$ is large). The dominant
balance is $2(g-2)u \sim -\ln u$, giving:

$$u \sim \frac{\ln(g)}{2g} \quad \Rightarrow \quad
J_{\mathrm{crit}} \sim \frac{1}{2}\ln\frac{2g}{\ln g}
\sim \frac{1}{2}\ln g \quad \text{(leading order for large } g\text{)}$$

**Step 5: Intermediate $J$ regime (the physically relevant case).**

For moderate $J$ (the regime where most computational data lies), we can
use the intermediate approximation $\tanh(J) \approx 1 - 2e^{-2J}$ but
keep $\sinh(J)\cosh(J)$ exact. The equation (5.2) can be written as:

$$f(J, g) := K\Delta \cdot \sinh(J)\cosh(J) \cdot \tanh^{g-2}(J) = \varepsilon^* \tag{5.3}$$

For fixed $g$, $f(J, g)$ is a product of an increasing factor
($\sinh(J)\cosh(J)$) and a factor that increases toward 1 ($\tanh^{g-2}(J)$).
For small $J$, $f \approx K\Delta J^{g-1} \to 0$. For large $J$, $f \sim
K\Delta \frac{1}{4}e^{2J} \to \infty$. So $f$ is increasing and crosses
$\varepsilon^*$ exactly once, confirming that $J_{\mathrm{crit}}(g)$ is
well-defined.

**Step 6: Asymptotic form of $J_{\mathrm{crit}}(g)$.**

The dominant behavior for large $g$ is:

$$\boxed{J_{\mathrm{crit}}(g) \sim \frac{1}{2}\ln g + O(\ln\ln g)}
\tag{5.4}$$

This is a **logarithmic** growth, not a power law $c \cdot g^\alpha$.
The conjectured form $J_{\mathrm{crit}} \sim c \cdot g^\alpha$ is therefore
**incorrect** as a large-$g$ asymptotic.

**Step 7: Why the power-law conjecture may have appeared correct numerically.**

For moderate values of $g$ (say $g = 4$ to $g = 20$, the range of
computational data), $\frac{1}{2}\ln g$ is approximately:

| $g$ | $\frac{1}{2}\ln g$ |
|-----|-------------------|
| 4 | 0.693 |
| 6 | 0.896 |
| 10 | 1.151 |
| 20 | 1.498 |

Over this range, $\frac{1}{2}\ln g$ can be well-approximated by a power law
$c \cdot g^\alpha$ with small $\alpha$. A least-squares fit to
$\ln(J_{\mathrm{crit}})$ vs $\ln(g)$ over $g \in [4, 20]$ would yield an
effective exponent $\alpha_{\mathrm{eff}} \approx 0.47$, which could be
mistaken for a universal exponent. However, this is an artifact of the
limited range: $\ln g$ is not a power of $g$ in the large-$g$ limit.

### Theorem (Girth-Coupling Duality -- Corrected Form)

**Theorem 5'.** Let $G$ be a connected graph with girth $g \geq 3$, maximum
degree $\Delta$, and uniform Ising coupling $J$. Let $J_{\mathrm{crit}}(g,
\Delta)$ be the solution to $C(\Delta, J) \cdot \tanh^{g-2}(J) =
\varepsilon^*(\Delta)$ from Theorem C + Proposition B. Then:

(a) $J_{\mathrm{crit}}(g, \Delta)$ is well-defined for all $g \geq 3$
and is strictly increasing in $g$.

(b) For large $g$:

$$J_{\mathrm{crit}}(g, \Delta) = \frac{1}{2}\ln g + O(\ln\ln g)$$

(c) $J_{\mathrm{crit}}(g, \Delta) \to \infty$ as $g \to \infty$, recovering
the tree result (trees have $g = \infty$, no coupling restriction).

(d) The conjectured power-law form $J_{\mathrm{crit}} \sim c \cdot g^\alpha$
does NOT hold asymptotically. The true growth is logarithmic.

**Proof.** Parts (a)--(c) follow from Steps 4--6 above. For part (d):
suppose $J_{\mathrm{crit}} = c \cdot g^\alpha$ for some $c, \alpha > 0$.
Then $J_{\mathrm{crit}}/\ln g = c \cdot g^\alpha / \ln g \to \infty$ for
any $\alpha > 0$. But from (b), $J_{\mathrm{crit}}/\ln g \to 1/2$ as
$g \to \infty$. Contradiction.  $\blacksquare$

### Status Summary for Conjecture 5

| Aspect | Status |
|--------|--------|
| "Larger girth permits stronger coupling" | PROVEN (monotonicity, part (a)) |
| "$J_{\mathrm{crit}} \to \infty$ as $g \to \infty$" | PROVEN (recovers tree case, part (c)) |
| "Power-law form $c \cdot g^\alpha$" | REFUTED (logarithmic, not power-law, part (d)) |
| "Universal exponents $c, \alpha$" | REFUTED (no power-law, so no universal exponents) |
| Quantitative threshold $\varepsilon^*$ | REMAINS IMPLICIT (depends on uncomputed constants $c_1$--$c_4$) |

**Corrected conjecture:** Replace "satisfies $J_{\mathrm{crit}}(g)
\sim c \cdot g^\alpha$" with "satisfies $J_{\mathrm{crit}}(g) \sim
\frac{1}{2}\ln g$ for large $g$."

---

## Conjecture 1: Sparse Universality

### Statement

**Conjecture 1** (Sparse Universality). For any graph with maximum degree
$\Delta \leq 4$ and any Ising coupling $J$, $W(1) > W(q)$ for all
$q \geq 2$.

### Status: PARTIALLY PROVEN

We prove a conditional version for $J$ below a threshold depending on
$\Delta$ and the girth $g$. The unconditional version (for ALL $J$) remains
open. The 5 numerical failures on $C_3$ at $J > 5$ are consistent with
the limitation of our approach.

### What Existing Results Give

**Step 1: Tree subcase (immediate).**

For any tree with $\Delta \leq 4$ (or any $\Delta$): $W(1) > W(q)$ for all
$q \geq 2$ and ALL $J$. This is Theorem A + Lemma 6.1, proven unconditionally.

**Step 2: Graphs with cycles, perturbative regime.**

For graphs with $\Delta \leq 4$ and girth $g \geq 3$, Theorem C gives:

$$\frac{||F - \operatorname{diag}(F)||_{\mathrm{op}}}{||\operatorname{diag}(F)||_{\mathrm{op}}} \leq C(4, J) \cdot \tanh^{g-2}(J) \tag{1.1}$$

where $C(4, J) = 4K\sinh(J)\cosh(J)$.

Proposition B then gives $W(1) > W(q \geq 2)$ when this ratio is below the
threshold $\varepsilon^*$. This proves the conjecture for $J < J_{\mathrm{crit}}(g, 4)$.

**Step 3: The problem -- $C_3$ (triangle) with $\Delta = 2$, girth $g = 3$.**

The triangle $C_3$ has $\Delta = 2 \leq 4$ and girth $g = 3$. The
near-diagonality bound gives:

$$\text{ratio} \leq C(2, J) \cdot \tanh^1(J) = 2K\sinh(J)\cosh(J)\tanh(J)$$

For $J > 5$: $\tanh(J) \approx 1$ and $\sinh(J)\cosh(J) \approx
\frac{1}{4}e^{2J} \approx 5.5 \times 10^4$. So ratio $\approx 2K \times
5.5 \times 10^4 \gg 1$. The perturbative approach gives NO information in
this regime.

The 5 numerical failures (on $C_3$ at $J > 5$) occur precisely where the
perturbative bound is vacuous. This is a genuine failure of the proof
strategy, not a numerical artifact.

### Attempt at a Non-Perturbative Proof for Specific Graphs

**Approach 1: Exact computation on $C_3$.**

The triangle $C_3$ has $m = 3$ edges and the Fisher matrix is a $3 \times 3$
matrix. In principle, $F$ can be computed exactly:

$$F_{ee} = \operatorname{sech}^2(J) \quad \text{(diagonal entries)}$$

$$F_{ab} = \langle\sigma_i\sigma_j\sigma_k\sigma_l\rangle - \langle\sigma_i\sigma_j\rangle\langle\sigma_k\sigma_l\rangle \quad \text{(off-diagonal)}$$

For $C_3$ with uniform coupling $J$, by symmetry $F$ has the form:

$$F = \begin{pmatrix} d & c & c \\ c & d & c \\ c & c & d \end{pmatrix}$$

where $d = \operatorname{sech}^2(J)$ and $c = F_{12}$ (covariance between
adjacent edge variables on $C_3$).

The eigenvalues of this circulant matrix are:
- $\lambda_1 = d + 2c$ (eigenvector $(1,1,1)/\sqrt{3}$)
- $\lambda_{2,3} = d - c$ (degenerate, eigenvectors orthogonal to $(1,1,1)$)

For the conjecture to hold ($W(1) > W(q \geq 2)$), we would need to analyze
$A(S) = F^{1/2} S F^{1/2}$ for $q = 1$ and $q = 2$ sign assignments.

**Computing $c$ on $C_3$:**

Label vertices $1, 2, 3$ and edges $e_1 = (1,2), e_2 = (2,3), e_3 = (1,3)$.
For adjacent edges $e_1 = (1,2)$ and $e_2 = (2,3)$:

$$F_{12} = \langle\sigma_1\sigma_2 \cdot \sigma_2\sigma_3\rangle - \langle\sigma_1\sigma_2\rangle\langle\sigma_2\sigma_3\rangle$$
$$= \langle\sigma_1\sigma_3\rangle - \langle\sigma_1\sigma_2\rangle\langle\sigma_2\sigma_3\rangle$$

On $C_3$: $\langle\sigma_1\sigma_3\rangle = \langle\sigma_1\sigma_2\rangle$
by symmetry, and both equal $\tanh(J) \cdot (1 + R)/(1 + R')$ for some
corrections depending on the cycle. Exact computation using the partition
function:

$$Z = \sum_{\sigma} e^{J(\sigma_1\sigma_2 + \sigma_2\sigma_3 + \sigma_1\sigma_3)}$$
$$= 2(e^{3J} + 3e^{-J}) = 2e^{-J}(e^{4J} + 3)$$

(summing over $2^3 = 8$ configurations: the all-same configurations give
$e^{3J}$ each (2 of them), and the remaining 6 configurations each have
exactly one negative edge, giving $e^{-J}$ each, but actually: configurations
with 2 aligned + 1 anti-aligned give $e^{3J - 2J} = e^J$... let me compute
carefully.)

For $C_3$ with spins $\sigma_1, \sigma_2, \sigma_3 \in \{-1, +1\}$:

| $\sigma_1$ | $\sigma_2$ | $\sigma_3$ | $\sigma_1\sigma_2 + \sigma_2\sigma_3 + \sigma_1\sigma_3$ | Weight |
|:-:|:-:|:-:|:-:|:-:|
| + | + | + | 3 | $e^{3J}$ |
| + | + | - | -1 | $e^{-J}$ |
| + | - | + | -1 | $e^{-J}$ |
| + | - | - | -1 | $e^{-J}$ |
| - | + | + | -1 | $e^{-J}$ |
| - | + | - | -1 | $e^{-J}$ |
| - | - | + | -1 | $e^{-J}$ |
| - | - | - | 3 | $e^{3J}$ |

So $Z = 2e^{3J} + 6e^{-J}$.

$\langle\sigma_1\sigma_2\rangle = \frac{1}{Z}\sum_\sigma \sigma_1\sigma_2 \cdot e^{J(\sigma_1\sigma_2 + \sigma_2\sigma_3 + \sigma_1\sigma_3)}$

For $\sigma_1\sigma_2 = +1$: configs $(+,+,+), (+,+,-), (-,-,+), (-,-,-)$.
- $(+,+,+)$: weight $e^{3J}$, $\sigma_1\sigma_2 = +1$
- $(+,+,-)$: $\sigma_1\sigma_2 = +1$, $\sigma_2\sigma_3 = -1$, $\sigma_1\sigma_3 = -1$; sum = $1 - 1 - 1 = -1$; weight $e^{-J}$
- $(-,-,+)$: $\sigma_1\sigma_2 = +1$, $\sigma_2\sigma_3 = -1$, $\sigma_1\sigma_3 = -1$; sum = $-1$; weight $e^{-J}$
- $(-,-,-)$: weight $e^{3J}$

Contribution with $\sigma_1\sigma_2 = +1$: $2e^{3J} + 2e^{-J}$

For $\sigma_1\sigma_2 = -1$: remaining 4 configs.
- $(+,-,+)$: sum = $-1 - 1 + 1 = -1$; weight $e^{-J}$
- $(+,-,-)$: sum = $-1 + 1 - 1 = -1$; weight $e^{-J}$
- $(-,+,+)$: sum = $-1 + 1 - 1 = -1$; weight $e^{-J}$
- $(-,+,-)$: sum = $-1 - 1 + 1 = -1$; weight $e^{-J}$

Contribution with $\sigma_1\sigma_2 = -1$: $-4e^{-J}$

Therefore:
$$\langle\sigma_1\sigma_2\rangle = \frac{2e^{3J} + 2e^{-J} - 4e^{-J}}{2e^{3J} + 6e^{-J}} = \frac{2e^{3J} - 2e^{-J}}{2e^{3J} + 6e^{-J}} = \frac{e^{3J} - e^{-J}}{e^{3J} + 3e^{-J}}$$

Dividing by $e^{-J}$:

$$\langle\sigma_1\sigma_2\rangle = \frac{e^{4J} - 1}{e^{4J} + 3} \tag{1.2}$$

For the two-point function $\langle\sigma_1\sigma_3\rangle$: by symmetry
of $C_3$, this equals $\langle\sigma_1\sigma_2\rangle$.

Now:
$$\langle\sigma_1\sigma_2 \cdot \sigma_2\sigma_3\rangle = \langle\sigma_1\sigma_3\rangle = \frac{e^{4J} - 1}{e^{4J} + 3}$$

$$\langle\sigma_1\sigma_2\rangle \cdot \langle\sigma_2\sigma_3\rangle = \left(\frac{e^{4J} - 1}{e^{4J} + 3}\right)^2$$

Therefore:
$$c = F_{12} = \frac{e^{4J} - 1}{e^{4J} + 3} - \left(\frac{e^{4J} - 1}{e^{4J} + 3}\right)^2 = \frac{e^{4J} - 1}{e^{4J} + 3}\left(1 - \frac{e^{4J} - 1}{e^{4J} + 3}\right)$$
$$= \frac{e^{4J} - 1}{e^{4J} + 3} \cdot \frac{4}{e^{4J} + 3} = \frac{4(e^{4J} - 1)}{(e^{4J} + 3)^2} \tag{1.3}$$

And the diagonal entry:
$$d = F_{11} = \operatorname{Var}(\sigma_1\sigma_2) = 1 - \langle\sigma_1\sigma_2\rangle^2 = 1 - \left(\frac{e^{4J} - 1}{e^{4J} + 3}\right)^2$$

Setting $t = e^{4J}$:
$$d = 1 - \frac{(t-1)^2}{(t+3)^2} = \frac{(t+3)^2 - (t-1)^2}{(t+3)^2} = \frac{8t + 8}{(t+3)^2} = \frac{8(t+1)}{(t+3)^2}$$

And $c = \frac{4(t-1)}{(t+3)^2}$.

**Eigenvalues of $F$:**
- $\lambda_1 = d + 2c = \frac{8(t+1) + 8(t-1)}{(t+3)^2} = \frac{16t}{(t+3)^2}$
- $\lambda_2 = \lambda_3 = d - c = \frac{8(t+1) - 4(t-1)}{(t+3)^2} = \frac{4t + 12}{(t+3)^2} = \frac{4(t+3)}{(t+3)^2} = \frac{4}{t+3}$

Check at $J = 0$ ($t = 1$): $\lambda_1 = 16/16 = 1$, $\lambda_2 = 4/4 = 1$. Correct ($F = I$ at $J = 0$).

As $J \to \infty$ ($t \to \infty$): $\lambda_1 \to 16t/t^2 = 16/t \to 0$, $\lambda_2 \to 4/t \to 0$. Both go to zero (Fisher information vanishes at strong coupling, as expected).

The ratio $\lambda_1/\lambda_2 = \frac{16t/(t+3)^2}{4/(t+3)} = \frac{4t}{t+3}$.

As $J \to \infty$: $\lambda_1/\lambda_2 \to 4$. So the Fisher matrix is not
proportional to the identity at strong coupling; it has eigenvalue ratio 4:1.

**Analysis of $W(q)$ on $C_3$ for all $J$:**

The matrix $F$ has eigenvalues $\lambda_1 = 16t/(t+3)^2$ (simple) and
$\lambda_2 = 4/(t+3)$ (double), where $t = e^{4J}$.

Since $F$ is a $3 \times 3$ PD matrix, we need to analyze $A(S) = F^{1/2} S F^{1/2}$
for $q = 1$ and $q = 2$ sign assignments. Because $F$ is a circulant,
the analysis requires computing the full spectral decomposition.

However, the key qualitative observation is: as $J \to \infty$, the eigenvalue
ratio $\lambda_1/\lambda_2 \to 4$, meaning $F$ is NOT close to diagonal
(ratio is bounded away from 1). The perturbative approach fails.

**Numerical evidence for $C_3$ failure:** The conjecture predicts $W(1) > W(2)$
for all $J$. The 5 numerical failures at $J > 5$ suggest $W(2) > W(1)$ at
strong coupling on $C_3$.

The mechanism: at strong coupling on $C_3$, the Fisher matrix has eigenvalue
ratio 4:1. The two degenerate eigenvalues ($\lambda_2 = \lambda_3$) mean
that flipping two signs in the degenerate eigenspace can create a spectral
gap, while flipping one sign of the simple eigenvalue produces a smaller
relative gap. This is a genuine non-perturbative phenomenon that our
proof strategy cannot capture.

### What Can Be Proven

**Theorem 1' (Conditional Sparse Universality).** For any graph $G$ with
maximum degree $\Delta \leq 4$, girth $g \geq 3$, and uniform Ising
coupling $J$:

(a) If $G$ is a tree ($g = \infty$): $W(1) > W(q)$ for all $q \geq 2$ and
ALL $J > 0$.

(b) If $G$ has finite girth $g \geq 3$: $W(1) > W(q)$ for all $q \geq 2$
whenever $J < J_{\mathrm{crit}}(g, 4)$, where $J_{\mathrm{crit}}$ is
the solution to $C(4, J) \cdot \tanh^{g-2}(J) = \varepsilon^*$.

(c) $J_{\mathrm{crit}}(g, 4) \to \infty$ as $g \to \infty$.

**Proof.** Part (a): Theorem A + Lemma 6.1. Part (b): Theorem C (with
$\Delta = 4$) + Proposition B. Part (c): By Theorem 5' above, $J_{\mathrm{crit}}
\sim \frac{1}{2}\ln g \to \infty$.  $\blacksquare$

### Why the Full Conjecture Remains Open

The full conjecture ("for ANY $J$") requires a non-perturbative argument
that works at strong coupling. Our proof strategy (near-diagonal Fisher
$\to$ perturbation stability) fundamentally breaks down when:

1. The girth is small (especially $g = 3$, the triangle).
2. The coupling is strong ($J \gg 1$), making $C(\Delta, J) \cdot
   \tanh^{g-2}(J) \gg \varepsilon^*$.

The 5 numerical failures on $C_3$ at $J > 5$ suggest that the conjecture
as stated may be **false**: the triangle at strong coupling may genuinely
fail to select $q = 1$. If confirmed, the conjecture should be amended to
either:

(a) Exclude $g = 3$ (i.e., require girth $g \geq 4$ with $\Delta \leq 4$), or
(b) Add a coupling bound $J \leq J_{\max}(\Delta, g)$.

**Possible non-perturbative approaches (not attempted):**

1. **Transfer matrix method** for cycle graphs $C_n$: the $2 \times 2$
   transfer matrix of the Ising model gives exact formulas for all
   correlations. This could settle the conjecture for cycles at all $J$,
   but the spectral gap weighting $W(q)$ involves the eigenvalues of
   $F^{1/2} S F^{1/2}$ (not just of $F$), which requires a non-trivial
   analysis even with exact $F$.

2. **Belief propagation / cavity method** for tree-like graphs: on locally
   tree-like graphs (large girth), the cavity method gives asymptotically
   exact correlations. This could extend the tree result to large-girth
   graphs at ALL coupling strengths, but requires controlling the
   convergence of the cavity iteration.

3. **Computer-assisted proof** for small $m$: for $m \leq 6$ (which
   covers $C_3, C_4, C_5, C_6$ and small sparse graphs), the Fisher matrix
   can be computed exactly as a function of $J$, and $W(q)$ analyzed
   symbolically. This is feasible but tedious.

### Status Summary for Conjecture 1

| Aspect | Status |
|--------|--------|
| Trees with $\Delta \leq 4$ | PROVEN (all $J$, Theorem A + Lemma 6.1) |
| Graphs with $\Delta \leq 4$, $g \geq 4$, weak coupling | PROVEN (perturbative, Theorem C + Prop B) |
| Full conjecture (all $J$, all $\Delta \leq 4$ graphs) | OPEN |
| $C_3$ at strong coupling ($J > 5$) | LIKELY FALSE (5 numerical failures) |
| Amended conjecture (exclude $g = 3$ or add $J$ bound) | PLAUSIBLE but unproven non-perturbatively |

---

## Summary and LaTeX-Ready Statements

### Conjecture 2: PROVEN (Theorem)

```latex
\begin{theorem}[Tree Absolute Selection]
\label{thm:tree-absolute}
Let $G = (V, E)$ be any tree graph with $|E| = m \geq 2$ and uniform
Ising coupling~$J > 0$. Then $W(q \geq 2) = 0$ and $W(1) = 2\operatorname{sech}^2(J) > 0$,
so $W(1)/W(q \geq 2) = \infty$.

More generally, for non-uniform couplings $\mathbf{J} = (J_1, \ldots, J_m)$,
$W(1) = \operatorname{sech}^2(J_{\mathrm{strongest}}) + \operatorname{sech}^2(J_{\mathrm{weakest}}) > 0$
and $W(q \geq 2) = \operatorname{sech}^2(J_{\mathrm{weakest}}) - \operatorname{sech}^2(J_{\mathrm{strongest}}) \geq 0$,
where $J_{\mathrm{strongest}} = \max_e |J_e|$ and $J_{\mathrm{weakest}} = \min_e |J_e|$.
In particular, $W(1) > W(q \geq 2)$ unconditionally, with infinite ratio
if and only if all couplings are equal.
\end{theorem}

\begin{proof}
By the Tree Fisher Identity (\cref{lem:tree-fisher}), $F = \operatorname{diag}
(\operatorname{sech}^2(J_1), \ldots, \operatorname{sech}^2(J_m))$.
For uniform coupling: $F = \operatorname{sech}^2(J) \cdot I_m$.
By \cref{thm:diagonal}(d), $W(q \geq 2) = 0$ and $W(1) = 2\operatorname{sech}^2(J)$.
For non-uniform coupling: apply \cref{thm:diagonal}(a)--(c) with
$d_{(1)} = \min_e \operatorname{sech}^2(J_e) = \operatorname{sech}^2(\max_e |J_e|)$
and $d_{(m)} = \max_e \operatorname{sech}^2(J_e) = \operatorname{sech}^2(\min_e |J_e|)$.
\end{proof}
```

### Conjecture 5: PARTIALLY PROVEN (Corrected Asymptotic)

```latex
\begin{theorem}[Girth-Coupling Duality -- Corrected Form]
\label{thm:girth-coupling}
Let $J_{\mathrm{crit}}(g, \Delta)$ be the critical coupling from the
perturbative regime (\cref{thm:near-diagonal} + \cref{thm:perturbation}).
Then:
\begin{enumerate}
  \item[(a)] $J_{\mathrm{crit}}(g, \Delta)$ is strictly increasing in~$g$.
  \item[(b)] $J_{\mathrm{crit}}(g, \Delta) = \frac{1}{2}\ln g + O(\ln\ln g)$
    as $g \to \infty$.
  \item[(c)] $J_{\mathrm{crit}}(g, \Delta) \to \infty$ as $g \to \infty$,
    recovering the unconditional tree result.
  \item[(d)] The conjectured power-law form $J_{\mathrm{crit}} \sim c \cdot g^\alpha$
    does not hold; the growth is logarithmic, not polynomial.
\end{enumerate}
\end{theorem}
```

### Conjecture 1: PARTIALLY PROVEN (Conditional)

```latex
\begin{theorem}[Conditional Sparse Universality]
\label{thm:sparse-conditional}
For any graph~$G$ with maximum degree $\Delta \leq 4$ and uniform
coupling~$J$:
\begin{enumerate}
  \item[(a)] If $G$ is a tree: $W(1) > W(q)$ for all $q \geq 2$ and
    all $J > 0$ (unconditional).
  \item[(b)] If $G$ has girth $g \geq 3$: $W(1) > W(q)$ for all $q \geq 2$
    whenever $J < J_{\mathrm{crit}}(g, 4)$.
  \item[(c)] $J_{\mathrm{crit}}(g, 4) \sim \frac{1}{2}\ln g \to \infty$
    as $g \to \infty$.
\end{enumerate}
The full conjecture (all $J$, no girth restriction) remains open; numerical
evidence suggests failure on $C_3$ at $J > 5$.
\end{theorem}
```

---

## Appendix: Confidence Assessment

| Result | Confidence | Basis |
|--------|-----------|-------|
| Theorem 2' (Tree Absolute Selection) | **99%** | Direct corollary of Theorem A + Lemma 6.1 |
| Theorem 5' part (a) (monotonicity) | **95%** | Follows from properties of $f(J,g)$ |
| Theorem 5' part (b) (logarithmic growth) | **90%** | Asymptotic analysis, assuming $C(\Delta, J)$ form |
| Theorem 5' part (d) (power-law refutation) | **95%** | Direct contradiction argument |
| Theorem 1' part (a) (tree subcase) | **99%** | Theorem A + Lemma 6.1 |
| Theorem 1' part (b) (perturbative regime) | **85%** | Depends on Proposition B (implicit constants) |
| $C_3$ exact Fisher computation | **99%** | Direct calculation from partition function |
| Conjecture 1 full (all $J$) | **30%** | Likely false for $C_3$ at $J > 5$ |

---

## Changelog

- 2026-02-17: Initial creation. Conjecture 2 upgraded to theorem.
  Conjecture 5 partially proven with corrected asymptotic (logarithmic,
  not power-law). Conjecture 1 partially proven (conditional on coupling
  bound). Exact Fisher matrix for $C_3$ computed.
