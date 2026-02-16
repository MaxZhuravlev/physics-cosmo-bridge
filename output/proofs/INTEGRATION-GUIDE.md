# Integration Guide: Tree Fisher Identity Proof

**For:** Paper #1 (structural-bridge)
**Created:** 2026-02-17

---

## Quick Integration (Recommended)

### Step 1: Add Footnote to Theorem 5.7

In `output/latex/main.tex` around line 1265, modify:

```latex
\begin{theorem}[Tree Fisher identity]
\label{thm:tree-fisher}
For an Ising model on a tree graph~$G$ (connected, acyclic) with
uniform coupling~$J$, the Fisher information matrix in the edge
parameterization is
\begin{equation}
\label{eq:tree-fisher}
F = \operatorname{sech}^2(J)\, I_m\,,
\end{equation}
where $I_m$ is the $m \times m$ identity matrix.%
\footnote{A complete rigorous proof with extensions to non-uniform
couplings, Potts models, and analysis of cycle failure is provided
in the supplementary material (Ancillary File 1).}
\end{theorem}
```

### Step 2: Add to arXiv Ancillary Files

When preparing arXiv submission:

```bash
# In arxiv-submission/ directory:
mkdir -p anc/
cp output/proofs/tree-fisher-identity-proof.pdf anc/
```

arXiv will list as "Ancillary File 1" with description: "Rigorous proof of Tree Fisher Identity with extensions"

### Step 3: Mention in Abstract (Optional)

Current abstract (line 59) says:
```
Additionally, we prove the \emph{Tree Fisher Identity}: the Ising Fisher
matrix on tree graphs equals $\operatorname{sech}^2(J)$ times the identity,
```

Could expand to:
```
Additionally, we prove the \emph{Tree Fisher Identity}: the Ising Fisher
matrix on tree graphs equals $\operatorname{sech}^2(J)$ times the identity
(with rigorous proof in supplementary material extending to non-uniform
couplings and showing the result is model-specific to discrete spins),
```

But current version is fine (brevity).

---

## Extended Integration (If Main Proof Needs Expansion)

### Option: Expand In-Text Proof to ~1 Page

Replace lines 1277-1294 with:

```latex
\begin{proof}
On a tree with $n$ vertices and $m = n - 1$ edges, fix a root vertex
$v_0$ (arbitrary).

\textbf{Step 1: Edge variable independence.}
For any configuration of edge variables
$\boldsymbol{\sigma} = (\sigma_{e_1}, \ldots, \sigma_{e_m})$ where
$\sigma_e = s_i s_j$ for edge $e = (i,j)$, we count the number of
spin configurations $\mathbf{s}$ consistent with this.

Given $\boldsymbol{\sigma}$, the tree structure implies:
\begin{itemize}
\item Once we fix $s_{v_0} \in \{-1, +1\}$, all other spins are
uniquely determined by tree traversal: for each vertex~$v \neq v_0$,
follow the unique path $v_0 \to v$ and propagate spins via
$s_{u_{i+1}} = \sigma_{e_i'}\, s_{u_i}$ where $e_i'$ is the edge
$(u_i, u_{i+1})$ along the path.

\item There are exactly 2 spin configurations: $\mathbf{s}$ and
$-\mathbf{s}$ (global flip).

\item \emph{Key:} No cycles means no constraints on
$\boldsymbol{\sigma}$. All $2^m$ edge configurations are realizable.
(For comparison, on a cycle, $\prod_{e \in \text{cycle}} \sigma_e = +1$
is a constraint reducing realizable configurations.)
\end{itemize}

The Boltzmann distribution therefore factorizes in edge variables:
\begin{equation}
P(\boldsymbol{\sigma})
= \frac{2}{Z} \exp\Biggl(\sum_{e \in E} J_e \sigma_e\Biggr)
= \prod_{e \in E} \frac{\exp(J_e \sigma_e)}{2\cosh(J_e)}
=: \prod_{e \in E} P(\sigma_e)\,,
\end{equation}
where $Z = 2 \prod_e 2\cosh(J_e)$ and the marginal is
$P(\sigma_e = +1) = (1 + \tanh J_e)/2$.

\textbf{Step 2: Covariance calculation.}
Independence implies
$\operatorname{Cov}(\sigma_e, \sigma_f) = 0$ for $e \neq f$.
For $e = f$, $\operatorname{Cov}(\sigma_e, \sigma_e)
= \operatorname{Var}(\sigma_e) = 1 - \tanh^2(J_e)
= \operatorname{sech}^2(J_e)$ (using $\sigma_e^2 = 1$).

Therefore $F_{ab} = \delta_{ab}\, \operatorname{sech}^2(J_a)$,
giving equation~\eqref{eq:tree-fisher} for uniform~$J$.

A complete rigorous proof with non-uniform couplings, Potts model
extensions, and analysis of cycle failure is in Ancillary File~1.
\end{proof}
```

This adds ~30 lines, giving more detail while staying under 1 page.

---

## What the Standalone Proof Adds

The in-text proof (brief or expanded) covers the core result. The standalone proof adds:

1. **Counting argument details:** Why exactly 2 spin configs, tree traversal mechanics

2. **Cycle failure mechanism:** Explicit constraint ∏ σ_e = +1 on cycles, why it breaks independence

3. **Adjacent edge covariance formula:** Cov(σ_e₁, σ_e₂) = sech²(J)·tanh^(g-2)(J) on cycles

4. **Potts extension:** Proof for q-state models (q ≥ 2)

5. **Gaussian non-extension:** Why Tree Fisher Identity fails for GGMs (precision matrix parameterization)

6. **Boundary conditions:** Open vs fixed boundary handling

7. **Physical interpretation:** Information geometry, learning dynamics, spectral gap selection

8. **Numerical verification:** Comprehensive (133 configs, Ising/Potts/Gaussian)

9. **References:** Baxter (transfer matrix), Amari (info geometry), Lauritzen (graphical models)

---

## Reviewer Anticipated Questions

### Q1: "Why is this diagonal? Seems non-obvious."

**Brief answer (in-text):** Trees have no cycles, so edge variables are independent.

**Full answer (supplementary):** Section 4 proves independence via counting (2 spin configs per edge config with no cycle constraints), leading to factorization P(σ) = ∏ P(σ_e).

### Q2: "Does this extend to non-uniform couplings?"

**Brief answer:** Yes, Corollary 5.6 (main.tex line 1296).

**Full answer:** Theorem 1 (supplementary) handles non-uniform {J_e} fully. Verified 49 non-uniform configs numerically.

### Q3: "What about graphs with cycles?"

**Brief answer:** Fails due to constraint ∏ σ_e = +1 around cycles.

**Full answer:** Section 8 (supplementary) derives exact formula Cov ~ tanh^(g-2)(J) for adjacent edges, verified on cycle graphs g = 3 to 12.

### Q4: "Is this universal to exponential families?"

**Brief answer:** No, model-specific to discrete spins.

**Full answer:** Section 12 (supplementary) shows Gaussian graphical models have non-diagonal F even on trees (precision matrix coupling).

---

## arXiv Submission Checklist

When submitting to arXiv:

- [ ] Compile standalone proof: `pdflatex tree-fisher-identity-proof.tex` (×2)
- [ ] Create `anc/` directory in submission package
- [ ] Copy `tree-fisher-identity-proof.pdf` to `anc/`
- [ ] Update `00README.XXX` to mention ancillary file:
  ```
  Ancillary File 1 (tree-fisher-identity-proof.pdf):
  Rigorous proof of Tree Fisher Identity (Theorem 5.7) with extensions
  to non-uniform couplings, Potts models, and analysis of cycle failure.
  ```
- [ ] Test arXiv build with ancillary files
- [ ] Add footnote to Theorem 5.7 citing ancillary file

---

## Cross-Paper References

### Paper #3 (amari-chain)

Paper #3 uses the Tree Fisher Identity when discussing pure Fisher metric (M_μν = F_μν case).

**Add citation in Paper #3:** "For tree observer topologies, F is exactly diagonal (Tree Fisher Identity; see Paper #1 Theorem 5.7 and ancillary proof for details)."

### Paper #2 (operational-qm)

Paper #2 doesn't directly use Tree Fisher Identity, but the principle of "topology determines metric structure" is related.

**Possible mention:** "Graph topology constrains information geometry (cf. Tree Fisher Identity in [Paper #1])."

---

## File Locations

```
papers/structural-bridge/
└── output/
    ├── latex/
    │   └── main.tex                    # Lines 1265-1294 (brief proof)
    └── proofs/
        ├── tree-fisher-identity-proof.tex          # 20 pages (standalone)
        ├── TREE-FISHER-PROOF-SUMMARY.md           # This summary
        └── INTEGRATION-GUIDE.md                   # This file
```

After compilation:
```
└── proofs/
    ├── tree-fisher-identity-proof.pdf  # → Copy to arxiv-submission/anc/
    └── ...
```

---

## Compilation Commands

```bash
# Navigate to proofs directory
cd papers/structural-bridge/output/proofs/

# Compile (two passes for references)
pdflatex tree-fisher-identity-proof.tex
pdflatex tree-fisher-identity-proof.tex

# Check output
ls -lh tree-fisher-identity-proof.pdf
open tree-fisher-identity-proof.pdf  # macOS
```

Expected output: ~20 page PDF with theorem environments, equations, proofs.

---

## Validation Checklist

Before submission:

- [ ] All equations compile correctly
- [ ] All theorem/lemma/proof environments balanced
- [ ] References cite correctly (Baxter, Amari, etc.)
- [ ] Figures/tables (none in this proof) compile
- [ ] Cross-references (\\cref, \\ref) resolve correctly
- [ ] Abstract accurately summarizes content
- [ ] No orphaned sections or incomplete proofs
- [ ] Consistent notation throughout
- [ ] Physical interpretation section connects to Paper #1 results

---

## Meta

```yaml
created: 2026-02-17
purpose: Integration guide for rigorous Tree Fisher Identity proof
target: Paper #1 (structural-bridge-via-uniqueness-theorems)
integration_effort: ~5 minutes (add footnote + include ancillary file)
alternative_effort: ~30 minutes (expand in-text proof to 1 page)
recommendation: "Quick integration with ancillary file (preserves main text flow)"
```

---

*Integration guide for Tree Fisher Identity proof: Minimal friction, maximum rigor.*
