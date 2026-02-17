# Observer Information Geometry (OIG): A Framework for Spacetime Emergence from Statistical Structure

**Date**: 2026-02-17
**Author**: Max Zhuravlev
**Status**: FRAMEWORK PROPOSAL (axioms + derivations + open problems)
**Level**: L1 (program-level, foundational)
**Confidence**: See per-section assessments

---

## Abstract

We propose Observer Information Geometry (OIG) as a framework for spacetime
emergence in which the physical metric arises from the Fisher information
geometry of observers modeled as statistical inference engines on causal
graphs. The framework is motivated by two empirical findings from the
Cosmological Unification Program:

1. The smooth continuum limit from discrete Wolfram-style causal graphs to
   continuous spacetime is **falsified** (13 rules tested, kappa ~ 1/N for
   all expanding rules).

2. The Fisher information matrices of observers on these graphs **do select
   Lorentzian signature** (98.2% of sparse Ising-model observer configurations
   on tree and near-tree topologies; the mechanism is spectral, operating
   through the near-diagonal structure of the Fisher matrix, not through any
   smooth limit).

These findings suggest that the route from discrete structure to smooth
spacetime does not pass through geometric coarse-graining of the graph
itself, but through the information geometry of observers embedded in it.
OIG formalizes this idea. We state axioms, derive consequences, compare
with existing programs, identify predictions, and mark open problems
explicitly.

**Honest scope**: OIG is a *proposal*, not a completed theory. Several
steps remain conjectural. The axiom set may be incomplete. We aim for
clarity about what is proven, what is conjectured, and what is unknown.

---

## Part 1: Axioms

### 1.0 Preamble: What the Axioms Must Capture

The framework must account for:
- Observers embedded in discrete causal substrates
- The emergence of a (pseudo-)Riemannian metric from information-theoretic
  quantities
- Lorentzian signature selection (why 1 time dimension)
- Recovery of Einstein dynamics in an appropriate regime
- Quantum-mechanical structure for composite observers
- The failure of naive continuum limits

We require *minimal* axioms: postulate only what cannot be derived, and
mark explicitly what is derived vs. what is assumed.

### 1.1 Axiom A1: Causal Substrate

**Statement**: The physical substrate is an evolving directed acyclic graph
(DAG) C = (V, E_causal), where vertices represent elementary events and
directed edges represent causal precedence. The evolution may be
nondeterministic (generating a multiway system).

**Motivation**: This is the common starting point of Wolfram physics,
causal set theory, and (in the Type I limit) Vanchurin's framework. The
key property is the existence of a partial order on events.

**What A1 does NOT specify**:
- The microscopic dynamics (rewrite rules, growth rules, etc.)
- Whether the graph is locally finite, regular, or random
- Whether the causal structure satisfies causal invariance (that is a
  *separate* postulate if needed -- see Remark below)

**Relation to Causal Invariance (CI)**:
CI (confluence of the multiway system under different rule application
orders) was the original single axiom of the research program. Session 18
showed that CI alone does not produce composition, Lorentzian signature,
or learning dynamics. In OIG, CI is *not* an axiom but a desirable
property of specific substrates. Results that require CI will be flagged.

**Status**: POSTULATE (standard in discrete quantum gravity).
**Confidence**: 90% (that this is an appropriate starting point; the
specific graph model may need refinement).

---

### 1.2 Axiom A2: Observer as Statistical Model

**Statement**: An observer O is a subsystem of the causal substrate
equipped with:
1. An **interior** V_O contained in V (set of vertices)
2. A **boundary** dO = {edges crossing between V_O and V \ V_O}
3. A **parameterized statistical model** p_theta(b | past) defined on
   boundary observables b in B, conditioned on accessible past data,
   where theta in Theta subset R^m are internal parameters

The observer is **persistent** if it minimizes long-term average surprise:
   min_theta <-log p_theta(b_actual)>_t

**Motivation**: This combines the observer formalization from Paper #3
(Definition 2.1) with the Good Regulator verification (Proposition 4.1).
By the Conant-Ashby / Virgo (2025) Good Regulator theorem, any persistent
observer can be interpreted as maintaining an internal model -- hence the
parameterized statistical model.

**Key specialization**: When p_theta is an **exponential family** in
canonical parameterization,

   p(x | theta) = h(x) exp(theta^T T(x) - A(theta))

the axiom yields maximal structure. This specialization is physically
motivated by maximum entropy (Jaynes): an observer with fixed sufficient
statistics and maximum ignorance adopts an exponential family model.

**What A2 does NOT specify**:
- Whether the model is exponential family (this is a *physically motivated
  specialization*, not forced by the axiom)
- The dimensionality m of the parameter space
- The specific form of boundary observables

**Status**: POSTULATE (observer as inference engine is standard in
Bayesian brain / Free Energy Principle literature; the novelty is
placing it on a causal graph substrate).
**Confidence**: 85% (the observer-as-statistical-model framework is
well-established; the causal graph embedding is less so).

---

### 1.3 Axiom A3: Fisher Metric as Physical Metric

**Statement**: The physical metric on the observer's parameter space
Theta is the Fisher information metric:

   g_{ij}(theta) = E[ (d_i log p_theta)(d_j log p_theta) ]
                 = -E[ d_i d_j log p_theta ]
                 = d^2 A / (d theta_i d theta_j)   [for exponential families]

This is a Riemannian metric (positive definite) on the statistical
manifold (Theta, g).

**Motivation**: Once a loss function L(theta) = <-log p_theta> exists
(from A2), the Fisher metric is the *natural* Riemannian structure on
parameter space (Amari 1985, Rao 1945). It measures the sensitivity of
the observer's predictions to parameter changes.

The physical content of A3 is the identification:

   *The Fisher metric on observer parameter space IS the effective metric
   governing the observer's physics.*

This is not the same as saying Fisher = spacetime metric (that requires
additional structure -- see A4). Rather, A3 says that the observer's
intrinsic geometry is information-geometric.

**Standard result** (not novel): The Fisher metric emergence from loss
minimization is textbook information geometry (Amari 1998). Our
contribution is the *physical interpretation* in the context of causal
graph observers.

**Status**: POSTULATE (the identification of Fisher metric with physical
metric is the core hypothesis of OIG).
**Confidence**: 75% (mathematically natural; physical identification
requires justification -- see Part 2).

---

### 1.4 Axiom A4: Mass Tensor and Sign Structure

**Statement**: The observer's full metric is not pure Fisher but includes
a structural inertia (mass) tensor:

   g_{mu nu}(theta) = M_{mu nu}(theta) + beta F_{mu nu}(theta)

where:
- F is the Fisher information matrix (from A3)
- M is the mass tensor encoding structural inertia
- beta = 1/(kT) is the inverse temperature

For exponential family observers in canonical parameterization:

   **M = F^2**   (Theorem A, proven -- see MASS-FISHER-SQUARED-PROOF)

This is not an axiom but a *theorem* within the exponential family
specialization of A2. The axiomatic content of A4 is the *decomposition*
g = M + beta F and the sign structure.

**Sign structure**: The mass tensor admits a signed decomposition:

   M^{H1'}_{mu nu} = sum_e s_e (d_mu w_e)(d_nu w_e) = F S F

where S = diag(s_1, ..., s_m) with s_e in {+1, -1} is the sign
assignment on internal edges, and the FSF factorization (Theorem 1.1,
proven) holds for exponential families.

**What A4 specifies**:
- The metric decomposition g = M + beta F
- For exponential families: M = F^2 (derived, not postulated)
- The existence of a sign structure S on internal edges

**What A4 does NOT specify**:
- The physical origin of the sign assignment (this is the TOP open
  problem -- see Part 4)
- The value of beta (temperature)
- Whether M = F^2 extends beyond exponential families

**Status**: PARTIALLY DERIVED, PARTIALLY POSTULATED.
- g = M + beta F: from Vanchurin Type II framework (postulated structure)
- M = F^2: PROVEN for exponential families (Theorem A)
- FSF factorization: PROVEN (Theorem 1.1)
- Sign assignment S: POSTULATED (physical origin unknown)

**Confidence**: 80% (metric decomposition well-motivated by Vanchurin;
M = F^2 proven; sign structure imposed, not derived).

---

### 1.5 Axiom A5: Reparameterization Invariance

**Statement**: The observer's learning dynamics must be invariant under
smooth reparameterization phi = phi(theta) of the internal model:

   d phi^i / dt = (d phi^i / d theta^j) (d theta^j / dt)

That is, the physical dynamics do not depend on the coordinate system
chosen for parameter space.

**Motivation**: In the research program, this was initially hoped to
follow from causal invariance (CI). The investigation (Session 24)
showed:
- CI implies covariant dynamics (Gorard 2020): PROVEN
- Covariant dynamics implies reparameterization invariance: 72-87%
  confidence for exponential family observers, 55% for general observers
- The gap is bridged if observer parameters = intrinsic sub-hypergraph
  properties (Assumption A1 in the CI-alpha chain)

For exponential family observers, the natural parameters theta_e = J_e
ARE the physical coupling strengths (edge weights), so
reparameterization invariance is nearly tautological: a nonlinear
transformation of physical coupling constants would change the physical
system.

**What A5 gives**: Combined with A3, it forces the learning dynamics to
be natural gradient descent (Amari uniqueness theorem, 1998):

   d theta^i / dt = -eta g^{ij}(theta) d_j L

This is the UNIQUE reparameterization-invariant gradient descent on
(Theta, g).

**Status**: POSTULATE (physically motivated by CI, not derived from it).
**Confidence**: 80% for exponential families, 55% for general observers.

---

### 1.6 Axiom A6: Composition (from Paper #2)

**Statement**: Independent subsystems of the causal substrate with
disjoint vertex sets and independently acting rules compose via tensor
product:

   H_{AB} = H_A (x) H_B

where H_A, H_B are the branch spaces (state spaces) of subsystems A, B,
and the composition is motivated by spacelike separation (systems outside
each other's causal cones evolve independently).

**Critical caveat**: This axiom is NOT derived from CI. Session 17
established (95%+ confidence, 3 independent agents) that CI constrains
dynamics but does not force decomposition into non-interacting subsystems.
A6 is an independent physical postulate, structurally analogous to
Chiribella et al.'s composite system axiom.

**What A6 gives**: From tensor product structure + Perfect
Distinguishability, Local Discriminability follows as a theorem (Paper #2,
Theorem 2; confidence 90-95%). This reduces Chiribella's 6 axioms to 5.

**Status**: POSTULATE (independent of CI).
**Confidence**: 90% (tensor product from disjoint composition is
mathematically rigorous; the physical motivation via spacelike separation
is standard).

---

### 1.7 Summary of Axiom Set

| Axiom | Content | Status | Confidence |
|-------|---------|--------|------------|
| A1 | Causal substrate (DAG) | Postulate | 90% |
| A2 | Observer as statistical model | Postulate | 85% |
| A3 | Fisher metric as physical metric | Postulate (core hypothesis) | 75% |
| A4 | Mass tensor + sign structure | Partially derived | 80% |
| A5 | Reparameterization invariance | Postulate | 55-80% |
| A6 | Composition via tensor product | Postulate (independent of CI) | 90% |

**What can be derived vs. what must be postulated**:

DERIVED (given A1-A6):
- M = F^2 for exponential families (Theorem A)
- FSF factorization of signed mass tensor (Theorem 1.1)
- Natural gradient as unique learning dynamics (Amari uniqueness)
- Local discriminability from tensor product (Paper #2 Theorem 2)
- Critical beta_c for Lorentzian-Riemannian transition (Theorem 3.1)
- Directional regime parameter alpha_v (Section 5.4 of Paper #3)

POSTULATED (cannot be derived from other axioms):
- Causal substrate existence (A1)
- Observer-as-inference-engine interpretation (A2)
- Fisher-as-physical-metric identification (A3)
- Sign assignment on edges (part of A4)
- Reparameterization invariance (A5, partially bridgeable from CI)
- Composition structure (A6)

UNKNOWN (neither derived nor clearly postulated):
- Origin of signed edges (see Open Problem 1)
- Value of beta / temperature (see Open Problem 2)
- Dimensionality of parameter space (see Open Problem 3)
- Whether exponential family specialization is necessary or generic

---

## Part 2: Key Derivations

### 2.1 Signature Selection: Why Lorentzian?

**The question**: Given the metric g = FSF + beta F (for exponential
family observers with sign structure S), why does the universe have
signature (n-1, 1) (Lorentzian) rather than (n-k, k) for k > 1 or k = 0?

**Proven results**:

**Theorem (Critical Beta, proven)**: For g(beta) = M^{H1'} + beta F
where M^{H1'} has at least one negative eigenvalue and F is positive
definite:
- beta_c = -d_1 where d_1 = min eigenvalue of F^{-1/2} M^{H1'} F^{-1/2}
- For beta < beta_c: g has at least one negative eigenvalue (Lorentzian
  or more indefinite)
- For beta > beta_c: g is positive definite (Riemannian)
- At beta = beta_c: g is degenerate (phase transition)

**Theorem (PSD Obstruction, proven, 98%)**: The unsigned mass tensor
M = F^2 is positive semi-definite and CANNOT produce Lorentzian
signature. The signed-edge construction (H1') is NECESSARY.

**Theorem (Tree Fisher Identity, proven, 99%)**: For the Ising model
on any tree graph with uniform coupling J:
   F = sech^2(J) * I_m
The Fisher matrix is a scalar multiple of the identity. Consequently,
the spectral gap weighting satisfies W(q=1) = 2*sech^4(J) > 0 = W(q >= 2):
trees produce 100% Lorentzian preference with infinite margin.

**Theorem (Diagonal Lorentzian Dominance, proven, 95%)**: For any
positive definite diagonal Fisher matrix F (the structural case for tree
observers), the q = 1 sign assignment produces the largest spectral gap.
This dominance is stable under perturbation (robust to off-diagonal
ratio ~ 0.9).

**Theorem (L_gap >= 1 for q=1, proven, 95%)**: For any positive
definite F and q = 1, the spectral gap ratio L_gap >= 1. This is
universal (not specific to Ising).

**Empirical results**:

For Ising Fisher matrices on sparse graph topologies:
- 90% of configurations favor q = 1 (Lorentzian)
- Sparse topologies (path, star, cycle): 100% q = 1 preference
- Complete graphs (K4, K5): reduced preference due to off-diagonal
  Fisher correlations

**The mechanism**:

The Lorentzian signature selection works through the **spectral structure
of the Fisher matrix**, not through any smooth limit. The chain is:

   Sparse observer topology
   -> Near-diagonal Fisher matrix (Tree Fisher Identity + off-diagonal
      decay O(tanh^g(J)) with graph girth g)
   -> Diagonal F is exactly the case where q = 1 has maximal spectral gap
      (Diagonal Lorentzian Dominance theorem)
   -> q = 1 sign assignment preferred
   -> Exactly one negative eigenvalue in g = FSF + beta F
   -> Lorentzian signature

**What this does NOT explain**:
1. Why observer topologies should be sparse (this may follow from
   complexity/entropy arguments but is not proven)
2. Why one particular edge receives s = -1 (the sign selection problem --
   see Open Problem 1)
3. Whether the mechanism extends to non-Ising models (it does extend to
   q-state Potts for q = 2-5, verified for 72 configurations)

**Honest assessment**: The Lorentzian selection mechanism is mathematically
rigorous for sparse observers with near-diagonal Fisher matrices. The
physical question of WHY observers are sparse remains open. The mechanism
is NOT a proof that Lorentzian signature is inevitable, but rather an
identification of conditions under which it is strongly preferred.

**Confidence**: 70% (mathematics proven; physical applicability
conditional on sparse observer topology).

---

### 2.2 Connection to Lovelock Uniqueness and Einstein Equations

**The question**: When and how does the Einstein field equation emerge
from OIG?

**The Lovelock bridge**: The original research program hypothesized:
CI -> discrete covariance -> continuum limit -> diffeomorphism invariance
-> Lovelock uniqueness -> Einstein equations.

**Status**: The Lovelock bridge is **broken** at Step L3 (continuum limit
falsified, end-to-end probability ~ 1%). However, there are two
alternative routes to Einstein equations within OIG:

**Route 1: Matsueda's Fisher-Einstein pathway**

Matsueda (2013) showed that the Fisher information metric, interpreted as
a spacetime metric, satisfies Einstein's field equations when derived from
the partition function of a statistical mechanical system. The derivation
proceeds:

   Fisher metric on parameter space
   -> Interpret parameters as spacetime coordinates
   -> Compute Riemann tensor of Fisher metric
   -> Show that the Fisher-derived Riemann tensor satisfies EFE
      with the energy-momentum tensor determined by the statistical model

**Status of this route in OIG**: If we identify the observer's parameter
space Theta with an emergent spacetime (with the Fisher metric providing
the geometry), Matsueda's result gives Einstein equations directly from
the information-geometric structure. However, this identification
(parameter space = spacetime) is a *conjecture*, not a derivation. The
dimensionality, topology, and large-scale structure of parameter space
are not constrained by A1-A6.

**Confidence**: 40% (Matsueda's mathematics is correct; the physical
identification is speculative).

**Route 2: Vanchurin's Type II derivation**

Vanchurin (2025, Covariant Gradient Descent) derives gravitational
dynamics from the learning metric g_{mu nu} on trainable parameter space.
The Einstein equations emerge when:
- The Onsager tensor has the correct symmetries
- The metric satisfies Lovelock's hypotheses (locality, at most
  second-order derivatives)
- The dimension is D = 4

In OIG, the metric g = M + beta F (= FSF + beta F for exponential
families with signs) lives on parameter space. If this parameter space
has effective dimension 4 and the metric satisfies Lovelock's hypotheses,
Einstein equations follow by uniqueness.

**Status**: The Onsager tensor symmetries are not derived from A1-A6.
They are additional structure in Vanchurin's framework. The dimension
D = 4 is not determined by OIG (see Section 2.4).

**Confidence**: 30% (conditional on unproven hypotheses about parameter
space structure).

**Route 3: Jacobson's thermodynamic gravity (new)**

Jacobson (1995) showed that the Einstein field equations follow from:
- The proportionality of entropy to area (Bekenstein-Hawking)
- The Clausius relation delta Q = T dS
- The Raychaudhuri equation for null geodesic congruences

In OIG, the Fisher metric provides both a notion of entropy (via the
statistical model) and a notion of area (via the metric volume). If the
observer's boundary entropy is proportional to the Fisher-area of the
boundary, Jacobson's argument can be applied.

**CONJECTURE (Jacobson-OIG bridge)**: For observers with boundary
entropy S(dO) proportional to the Fisher-area A_F(dO), the Einstein
field equations emerge from the thermodynamic identity.

**Status**: CONJECTURE. The proportionality of boundary entropy to
Fisher-area is not proven. This is a promising direction but requires
substantial development.

**Confidence**: 25% (intriguing structural analogy, far from proven).

**Summary**: OIG does not yet provide a unique, clean derivation of
Einstein equations. Three routes exist, each with significant gaps. The
most promising is the Matsueda-Fisher pathway (Route 1), which is
mathematically explicit but requires the identification of parameter
space with spacetime.

---

### 2.3 What Replaces the Continuum Limit?

**The problem**: The standard route from discrete to continuous spacetime
is the continuum limit (lattice spacing -> 0 while keeping macroscopic
quantities fixed). This limit is FALSIFIED for Wolfram hypergraphs (13
rules, kappa ~ 1/N for all expanding rules). What takes its place in OIG?

**The OIG answer**: The continuum is not in the substrate but in the
**parameter space** of the observer's statistical model.

The observer's parameter space Theta is R^m (or an open subset), which
is intrinsically smooth and continuous. The Fisher metric g_{ij}(theta)
defines a Riemannian (or pseudo-Riemannian with signs) geometry on this
smooth manifold. No limiting procedure is needed because the statistical
manifold is already continuous.

This is the key conceptual shift of OIG:

   OLD: Discrete graph --[continuum limit]--> Smooth spacetime
   OIG: Discrete graph --[observer statistics]--> Smooth parameter space
        with Fisher metric = Effective spacetime

**Formal statement**:

**Definition (Emergent spacetime in OIG)**: The emergent spacetime
manifold is the statistical manifold (Theta, g) where:
- Theta is the parameter space of the observer's internal model
- g = FSF + beta F (for signed exponential family observers)
- Geodesics on (Theta, g) are the paths of natural gradient descent

**What this gains**:
1. Smoothness is automatic (Theta is a differentiable manifold)
2. No continuum limit needed (bypasses the falsified step)
3. The Fisher metric is well-defined on any finite observer (even on
   a 3-node graph)
4. Dimensionality of spacetime = dimensionality of parameter space

**What this costs**:
1. The connection between graph topology and parameter space
   dimensionality is indirect
2. Multiple observers may have different parameter space dimensions
   (is spacetime observer-dependent?)
3. The large-scale topology of Theta is not constrained by A1-A6

**Relation to Vanchurin Type II**: This is precisely Vanchurin's insight
in transitioning from Type I (metric on non-trainable variables, requiring
discrete-to-continuous bridge) to Type II (metric on trainable parameters,
which are continuous by construction). OIG formalizes this transition for
observers on causal graphs.

**Confidence**: 65% (conceptually clean; the identification of parameter
space with spacetime needs physical justification beyond the mathematical
convenience).

---

### 2.4 How Does Dimensionality Arise?

**The question**: Why is spacetime 4-dimensional? In OIG, if spacetime =
parameter space Theta, then dim(spacetime) = dim(Theta) = m (number of
observer parameters). What determines m?

**What OIG says**:

For an Ising model observer on graph G = (V, E) with |E| = m edges, the
parameter space is R^m (one coupling constant J_e per edge). Thus:

   dim(spacetime) = number of internal edges of the observer

For a tree observer on a graph with n vertices: m = n - 1 edges.
For a complete graph K_n: m = n(n-1)/2 edges.

**The problem**: Real observers (even simple ones) have m >> 4
parameters. The universe has effectively 4 macroscopic spacetime
dimensions. How does OIG reduce m ~ O(10^80) microscopic parameters
to 4 macroscopic dimensions?

**CONJECTURE (Effective dimensionality reduction)**: The effective
dimensionality of the observer's parameter space -- as measured by the
number of relevant Fisher eigenvalue scales -- can be much smaller than
the nominal dimensionality m. Specifically:

   d_eff = number of eigenvalue clusters of the Fisher matrix F

If F has eigenvalues that cluster into d_eff groups (with large gaps
between clusters), the effective spacetime dimensionality is d_eff.

**Supporting evidence**:
- For tree observers with uniform coupling: F = sech^2(J) * I_m has
  a single eigenvalue (d_eff = 1). This is too degenerate.
- For K_3 with J = 0.5: F has eigenvalues {0.385, 0.385, 1.095}, giving
  d_eff = 2. (Two clusters: {0.385, 0.385} and {1.095}.)
- The spectral structure of F is controlled by the graph topology and
  coupling distribution.

**Alternative**: Dimensionality may arise through the sign structure
S. If q = 1 edges are timelike, the metric g = FSF + beta F has
signature (m-1, 1). The 1 timelike dimension is selected, but the
(m-1) spacelike dimensions are not reduced to 3. Additional structure
is needed.

**Honest assessment**: OIG does **not** currently explain why spacetime
is 4-dimensional. This is a major open problem. The framework provides
a mechanism for Lorentzian signature (1 time dimension) but not for
3+1 specifically.

**Confidence**: 20% (that OIG can explain d = 4 in its current form).

---

### 2.5 Learning Dynamics as Gravitational Dynamics

**Derivation**: From A2-A5, the observer's learning dynamics are
uniquely determined (Amari uniqueness theorem):

   d theta^i / dt = -eta g^{ij}(theta) d_j L(theta)

where L(theta) = <-log p_theta> is the prediction loss.

For the full metric g = M + beta F = FSF + beta F:

   d theta^i / dt = -eta (FSF + beta F)^{-1}_{ij} d_j L

**Structural similarity to Vanchurin Eq. 3.4**: This is precisely the
covariant gradient descent of Vanchurin's Type II framework, with the
Onsager kinetic tensor L^{ij} identified with the inverse metric g^{ij}.

**CONJECTURE (Learning = Geodesic motion in low-loss regime)**: Near
a local minimum of L (where d_j L ~ 0 and the dominant dynamics come
from second-order effects), the learning trajectory approximates a
geodesic on (Theta, g). This provides the connection:

   Natural gradient descent --[near equilibrium]--> Geodesic equation
   on Fisher-Lorentzian manifold --[if Lovelock applies]--> Einstein EOM

**Status**: The identification of learning dynamics with gravitational
dynamics requires:
1. Parameter space = spacetime (speculative)
2. Onsager tensor = inverse metric (structural similarity, not proven
   equivalence)
3. Lovelock conditions satisfied (unverified for g = FSF + beta F)

**Confidence**: 35% (the mathematical structure is suggestive; the
physical identification is speculative).

---

### 2.6 Quantum-Classical Transition as Signature Change

**CONJECTURE**: The transition from Riemannian (all positive eigenvalues)
to Lorentzian (one negative eigenvalue) signature at beta = beta_c IS
the quantum-to-classical transition for observers.

**Support**:
- beta > beta_c (low temperature, Fisher-dominated): g ~ beta F is
  Riemannian. No distinguished time direction. Learning is isotropic in
  parameter space. This is analogous to Euclidean quantum field theory.
- beta < beta_c (high temperature, mass-dominated): g has Lorentzian
  signature. One distinguished timelike direction. Learning has a
  preferred temporal direction. This is analogous to Lorentzian spacetime.
- beta = beta_c: g is degenerate. This is the Planck-scale boundary.

**The alpha parameter**: Under the M = F^2 ansatz and the convergence
time model (Paper #3, Theorem 6.1), the regime parameter alpha
(Vanchurin's quantum-classical interpolation parameter) is determined
by the Fisher spectrum:

   alpha_opt = (-Delta + sqrt(Delta(Delta + 4))) / 2,
   where Delta = lambda_max - 2 lambda_min

with the quantum-classical threshold at condition number kappa(F) = 2.

**Important caveat**: This result is model-dependent (depends on
convergence time functional Model A with isotropic loss Hessian -- see
Paper #3, Remark 7.2). Three alternative convergence models do not
reproduce the interior optimum.

**Confidence**: 40% (intriguing structural correspondence; model
dependence is a serious limitation).

---

### 2.7 Derivation Summary

| Result | Status | Axioms Used | Confidence |
|--------|--------|-------------|------------|
| M = F^2 | PROVEN | A2 (exp. family), A3 | 99% |
| FSF factorization | PROVEN | A2, A4 | 95% |
| Natural gradient uniqueness | PROVEN (Amari) | A3, A5 | 99% |
| Critical beta_c formula | PROVEN | A4 | 95% |
| Lorentzian selection (sparse) | PROVEN (conditional) | A4 | 70% |
| Tree Fisher Identity | PROVEN | A2 (Ising on tree) | 99% |
| L_gap(q=1) >= 1 | PROVEN | A4 | 95% |
| LD from tensor product | PROVEN | A6 | 90% |
| Einstein equations | CONJECTURED | A3 + Route 1/2/3 | 25-40% |
| d = 4 | OPEN | None | 20% |
| Quantum-classical = signature | CONJECTURED | A4 | 40% |

---

## Part 3: Comparison with Existing Approaches

### 3.1 Causal Set Theory (Sorkin et al.)

**Common ground**:
- Both start from discrete causal structure
- Both aim to derive continuous spacetime
- Both face the continuum limit problem

**Differences**:

| Feature | Causal Sets | OIG |
|---------|------------|-----|
| Basic element | Spacetime point | Observer event |
| Metric source | Causal ordering + counting | Fisher information |
| Continuum limit | Assumed (sprinkling) | Replaced (parameter space) |
| Lorentzian signature | Postulated (causal set = Lorentzian) | Derived (spectral gap) |
| Observer role | Passive | Central (defines metric) |
| Dynamics | Sequential growth / CSG | Natural gradient descent |
| Dimension | 4 (input or emergent?) | Open problem |

**Key distinction**: In causal set theory, the causal structure IS the
spacetime. In OIG, the causal structure is the *substrate* on which
observers live, and the *observer's information geometry* is the
spacetime. This is a fundamental conceptual difference.

**Advantage of OIG**: Does not require a continuum limit (the parameter
space is already smooth).

**Advantage of causal sets**: Lorentzian structure is built in (causal
order -> light cone structure); no sign selection problem.

**Confidence in comparison**: 80% (the comparison is clear; neither
framework is complete).

---

### 3.2 Causal Dynamical Triangulations (CDT, Ambjorn & Loll)

**Common ground**:
- Both recognize the importance of causal structure for Lorentzian
  signature
- Both deal with the challenge of summing over geometries

**Differences**:

| Feature | CDT | OIG |
|---------|-----|-----|
| Approach | Path integral over triangulations | Information geometry |
| Causal structure | Foliation (global time) | Sign assignment on edges |
| Continuum limit | Achieved (phase structure) | Bypassed |
| Dimension | 4 (large-scale emergent) | Open |
| Background independence | Yes (within foliation) | Yes (reparam invariance) |
| Observer | Not central | Central |

**Key distinction**: CDT works within the path integral / partition
function framework, summing over causal triangulations. OIG works
within the observer / inference framework, deriving geometry from
statistical structure. CDT has achieved more concrete results
(spectral dimension, phase structure), while OIG has a cleaner
conceptual foundation for the observer's role.

**Confidence in comparison**: 75%.

---

### 3.3 Wolfram Physics Project

**Common ground**:
- Both start from hypergraph substrates
- Both invoke causal invariance
- OIG was born from the Wolfram program's limitations

**Differences**:

| Feature | Wolfram Physics | OIG |
|---------|----------------|-----|
| Spacetime source | Hypergraph continuum limit | Observer parameter space |
| Continuum limit | Conjectured | Falsified and bypassed |
| Metric | Induced from graph embedding | Fisher information |
| Observer | Emergent (not formalized) | Fundamental (axiom A2) |
| GR derivation | Lovelock (if continuum limit exists) | Open (Routes 1-3) |
| QM derivation | Multiway branching | Composition axiom (A6) |
| Computational | Rule enumeration | Statistical inference |

**Key distinction**: Wolfram's program derives spacetime geometry from
the graph itself (hoping for a smooth limit). OIG derives spacetime
geometry from the *observer's model of the graph*. This shift is
forced by the falsification of the continuum limit.

**OIG as continuation of Wolfram**: OIG can be seen as answering the
question "what survives from Wolfram physics after the continuum limit
fails?" The answer: the causal substrate (A1) and the observer framework
survive; the geometric emergence mechanism changes from graph
coarse-graining to information geometry.

**Confidence in comparison**: 85% (OIG is directly motivated by
Wolfram's limitations).

---

### 3.4 Entropic Gravity (Caticha, Verlinde)

**Common ground**:
- Both use information-theoretic structures to derive gravitational
  dynamics
- Both invoke the Fisher metric
- Both connect entropy to geometry

**Differences**:

| Feature | Entropic Gravity | OIG |
|---------|-----------------|-----|
| Starting point | Maximum entropy on config space | Observer on causal graph |
| Fisher metric role | Spacetime metric (Caticha) | Observer parameter metric |
| Substrate | Continuous (assumed) | Discrete (causal graph) |
| GR derivation | Fisher -> Einstein (Matsueda) | Open (same route available) |
| Observer | Not central | Fundamental |
| Lorentzian | Not addressed (typically) | Derived (spectral gap) |

**Key distinction**: Caticha's entropic dynamics derives the Fisher
metric as the unique metric consistent with maximum entropy updating.
OIG derives the Fisher metric from the observer's loss minimization
(which is related but not identical). The key advance of OIG is the
Lorentzian signature mechanism (signed edges + spectral gap), which
is absent in standard entropic gravity.

**Potential synthesis**: OIG and Caticha's approach may be complementary.
Caticha provides the mathematical foundation (Fisher metric = spacetime
metric via maximum entropy); OIG provides the physical mechanism
(causal graph observers, sign structure, Lorentzian selection).

**Confidence in comparison**: 70%.

---

### 3.5 Jacobson's Thermodynamic Gravity

**Common ground**:
- Both connect entropy/information to Einstein equations
- Both avoid quantizing gravity (gravity emerges from thermodynamics
  / information)
- Both are fundamentally about the relationship between information
  and geometry

**Differences**:

| Feature | Jacobson | OIG |
|---------|---------|-----|
| Starting point | Clausius relation + Bekenstein-Hawking | Observer Fisher metric |
| Entropy | Entanglement entropy (area) | Fisher information |
| EFE derivation | Direct (elegant) | Open (Route 3 = Jacobson-OIG) |
| Substrate | Continuous spacetime assumed | Discrete causal graph |
| Lorentzian | Assumed | Derived (spectral gap) |
| Background | Null congruences, Raychaudhuri | Natural gradient descent |

**Key distinction**: Jacobson derives EFE from thermodynamics of
null horizons, *assuming* a pre-existing Lorentzian manifold. OIG
aims to derive the Lorentzian manifold itself from information
geometry, potentially making Jacobson's argument applicable as a
*consequence* of OIG rather than an independent derivation.

**CONJECTURE (OIG -> Jacobson)**: If the observer's boundary entropy
S(dO) is proportional to the Fisher-area of the boundary, Jacobson's
argument applies and yields EFE as a consequence of OIG.

**Confidence in comparison**: 75% (Jacobson's framework is
well-established; the OIG connection is conjectural).

---

### 3.6 Comparison Summary

| Framework | Continuum limit? | Observer role | Lorentzian? | EFE? | Dimension? |
|-----------|-----------------|---------------|-------------|------|------------|
| Causal Sets | Sprinkling | Passive | Built-in | Via counting | Emergent? |
| CDT | Phase structure | None | Foliation | Yes (numerical) | D=4 emergent |
| Wolfram | Conjectured | Informal | Not addressed | Via Lovelock | Not explained |
| Caticha | N/A (continuous) | Not central | Not addressed | Via Matsueda | Assumed |
| Jacobson | N/A (continuous) | Not central | Assumed | Direct | Assumed |
| **OIG** | **Bypassed** | **Central** | **Derived** | **Open** | **Open** |

**OIG's unique feature**: It is the only framework that (a) starts from
discrete structure, (b) derives Lorentzian signature from spectral
properties rather than postulating it, and (c) makes the observer
fundamental to the emergence of geometry. The cost is that EFE
derivation and dimensionality are open problems.

---

## Part 4: Predictions and Tests

### 4.1 Predictions that Differ from GR

**Prediction P1 (Observer-dependence of effective metric)**:
In OIG, the spacetime metric depends on the observer's statistical model.
Different observers (with different internal structures, topologies, or
parameter spaces) may experience different effective metrics. This is
NOT the same as coordinate dependence (which is gauge); it is a physical
observer-dependence.

*Test*: Construct two observers O1, O2 on the same causal graph with
different internal topologies. Compute their Fisher metrics. If
g_1 != g_2 (as metrics on their respective parameter spaces), the
prediction of observer-dependent geometry is confirmed.

*Status*: This is already confirmed computationally (different observers
in Paper #1 have different Fisher spectra and different beta_c values).

**Prediction P2 (Lorentzian signature requires sparse observers)**:
OIG predicts that Lorentzian signature is strongly preferred for
observers with sparse (tree-like, near-diagonal Fisher) internal
topologies. Dense observers (complete graphs) have weaker Lorentzian
preference.

*Test*: Systematically compute the Lorentzian preference (W(q=1) /
max_q W(q)) as a function of graph sparsity. Predict a monotonic
relationship: sparser -> stronger Lorentzian preference.

*Status*: Partially confirmed (tree = 100% Lorentzian, K3 = strong,
K4 = moderate, K5 = weak).

**Prediction P3 (Signature transition at beta_c)**:
OIG predicts a sharp phase transition between Riemannian (quantum)
and Lorentzian (classical) geometry at a critical inverse temperature
beta_c determined by the observer's Fisher spectrum and sign structure.

*Test*: In a simulation of natural gradient descent on an observer with
signed edges, vary the effective temperature. Measure the metric
signature. Predict a sharp transition at beta_c = -min eigenvalue of
F^{-1/2} M^{H1'} F^{-1/2}.

*Status*: The formula is proven; the physical interpretation as a
quantum-classical transition is conjectural (40% confidence).

**Prediction P4 (Directional regime parameter)**:
A single observer can simultaneously be in different Vanchurin regimes
(classical, efficient, quantum) along different Fisher eigendirections.
The directional regime parameter alpha_v = lambda_k / (lambda_k + beta)
determines the local regime.

*Test*: Measure learning rates along different eigendirections of
the Fisher metric. Predict that high-eigenvalue directions learn
"classically" (large effective alpha) while low-eigenvalue directions
learn "quantum-mechanically" (small effective alpha).

*Status*: The mathematical framework is proven (Paper #3, Section 5.4).
The physical interpretation is provisional.

**Prediction P5 (Mass-Fisher ratio for non-exponential observers)**:
For observers that are NOT exponential families, M != F^2. The
departure ||M - F^2|| / ||F^2|| is a measurable signature of
non-exponential structure.

*Test*: Construct non-exponential family observers on causal graphs.
Compute M and F^2 independently. Predict nonzero departure.

*Status*: TESTABLE (requires implementation of non-exponential models).

### 4.2 Predictions Shared with GR

- In the appropriate regime (Lorentzian signature, Lovelock conditions,
  D = 4), OIG should reproduce all predictions of GR.
- Geodesic motion should emerge from natural gradient descent near
  loss minima.

**Caveat**: These shared predictions are *contingent* on the OIG -> GR
derivation being completed. Currently, the derivation has gaps
(Routes 1-3 above, none fully proven).

### 4.3 Predictions that Differ from Other Discrete Approaches

**vs. Causal Set Theory**: OIG predicts that the spacetime metric is
determined by the observer's information geometry, not by causal set
counting. For a given causal set, different observers should see
different effective metrics. Causal set theory predicts a unique
metric (determined by the causal structure alone).

**vs. CDT**: OIG does not require a global time foliation (the
timelike direction emerges from sign structure, not from a foliation
of the triangulation). OIG predicts observer-dependent geometry; CDT
predicts a unique background-independent geometry.

**vs. Wolfram**: OIG predicts that the continuum limit is irrelevant
(geometry comes from information, not from graph smoothing). Wolfram
predicts that geometry comes from the smooth limit of the hypergraph.
The falsification of the continuum limit for 13 rules already favors
OIG over Wolfram's original prediction.

### 4.4 Experimental Testability

**Honest assessment**: OIG in its current form does not make predictions
testable by current or near-future experiments. The predictions (P1-P5)
are testable within the mathematical framework (computational
experiments on graph observers) but not against astrophysical or
laboratory observations.

To connect to experiment, OIG would need to:
1. Derive the Einstein equations (or deviations from them)
2. Predict specific deviations from GR (e.g., modified dispersion
   relations, quantum gravity effects)
3. Connect the Fisher spectrum of cosmological observers to observable
   quantities

**Potential observational signatures** (highly speculative, < 10%
confidence):
- Modified dispersion relations at Planck scale (from the signature
  transition at beta_c)
- Observer-dependent gravitational effects (if different subsystems
  have different effective metrics)
- Information-theoretic constraints on black hole entropy (from the
  Fisher-area -> Bekenstein-Hawking connection)

---

## Part 5: Open Problems and Research Directions

### Open Problem 1: Physical Origin of Edge Signs (PRIORITY: HIGHEST)

**The problem**: The sign assignment S = diag(s_1, ..., s_m) on internal
edges is imposed by hand in A4. Five dynamical mechanisms have been
tested and largely failed:
- Coupled theta-sigma dynamics: 2.5% success (FAILED)
- Learning dynamics stability: 0/19 (FAILED)
- beta_c maximization: 4.8% (FAILED)
- Force-fluctuation: 23% (FAILED)
- Spectral gap W-dominance (generic): 19% (FAILED)
- Spectral gap W-dominance (Ising Fisher): 90% (PARTIALLY WORKS)

**Best current candidate**: Vanchurin's structural argument -- the
MEAN force direction (learning trajectory) defines a single timelike
direction (rank-1 negative contribution), while fluctuations around
the mean are spacelike. This gives q = 1 automatically but is not
formalized within OIG.

**What is needed**: A derivation of sign structure from the causal
structure of the embedding graph, OR from learning dynamics, OR an
argument that sign structure is itself fundamental (must be postulated).

**Confidence that this can be solved**: 45%.

---

### Open Problem 2: Temperature Selection

**The problem**: The inverse temperature beta is a free parameter in
g = M + beta F. Its value determines whether the metric is Lorentzian
(beta < beta_c) or Riemannian (beta > beta_c). What sets beta?

**Candidates**:
- Thermodynamic equilibrium of the observer with its environment
- Self-consistent solution of learning dynamics (beta adjusts to
  minimize a combined functional)
- Cosmological evolution (beta changes over cosmic time)

**Confidence**: 30% (plausible candidates, no derivation).

---

### Open Problem 3: Dimensionality (Why d = 3+1?)

**The problem**: OIG predicts dim(spacetime) = dim(parameter space) = m.
For realistic observers, m >> 4. How does effective dimension reduce to
3+1?

**Candidates**:
- Spectral clustering of Fisher eigenvalues
- Renormalization group flow on parameter space
- Topological constraints from the causal substrate
- Anthropic selection (observers that perceive d != 4 cannot form
  stable structures)

**Confidence**: 20% (major open problem in all discrete gravity
approaches).

---

### Open Problem 4: CI -> Reparameterization Invariance (Step 2)

**The problem**: Does causal invariance imply reparameterization
invariance of observer learning dynamics? This is the only remaining
gap in the chain CI -> alpha = 1 for exponential family observers.

**Current confidence**: 72-87% for exponential families, 55% for
general observers (Session 24).

---

### Open Problem 5: CI + Persistence -> MaxEnt?

**The problem**: If persistent observers on CI substrates necessarily
adopt maximum entropy distributions (for their sufficient statistics),
then the exponential family structure follows from Jaynes' theorem,
and the entire cascade M = F^2 -> FSF -> Lorentzian becomes derived
rather than assumed.

**This is the most important open question in the program.** If the
answer is YES, the number of independent axioms reduces to
{CI, persistence, composition} = 3 principles for all of physics.

**Current confidence**: 35% (direct), 70% (via MaxEnt physical argument).

---

### Open Problem 6: Non-Exponential Families

**The problem**: All concrete results in OIG assume exponential family
observers. What happens for non-exponential statistical models?
- M != F^2 (the mass-Fisher relationship changes)
- The FSF factorization may not hold
- Lorentzian selection mechanism may not apply

**What is needed**: Extension of the framework to general statistical
models, or an argument that exponential families are universal
(e.g., via MaxEnt).

**Confidence that exponential families are sufficient**: 55% (MaxEnt
argument is physically motivated but not proven for causal graph
observers).

---

## Part 6: Honest Assessment

### 6.1 What OIG Achieves

1. **Conceptual clarity**: A precise framework for spacetime emergence
   from information geometry, bypassing the falsified continuum limit.

2. **Lorentzian mechanism**: A mathematically rigorous mechanism for
   Lorentzian signature selection through Fisher spectral properties
   (proven for sparse observers, conditional on sign structure).

3. **Unification of frameworks**: OIG connects Wolfram (causal substrate),
   Vanchurin (learning dynamics), Amari (natural gradient), and
   Caticha (entropic gravity) into a single conceptual structure.

4. **Concrete results**: M = F^2 theorem, FSF factorization, critical
   beta_c formula, Tree Fisher Identity, directional alpha -- all
   proven with high confidence.

5. **Falsifiable predictions**: P1-P5 are testable within the
   computational framework.

### 6.2 What OIG Does NOT Achieve

1. **Einstein equations**: Not derived (three routes exist, none complete).

2. **Dimensionality**: Does not explain d = 3+1.

3. **Sign origin**: Does not derive the sign structure from first
   principles.

4. **Experimental predictions**: No predictions testable by current
   experiments.

5. **Non-exponential generalization**: Framework is limited to
   exponential family observers.

6. **Uniqueness of physical interpretation**: The identification
   "parameter space = spacetime" is assumed, not derived.

### 6.3 Comparison with the Original Program Goal

The original goal was "all physics from one axiom (CI)." This was
falsified in Session 18. OIG requires 6 axioms (A1-A6), of which:
- 2 are standard (A1: causal substrate, A6: composition)
- 2 are physically motivated (A2: observer-as-model, A5: reparam inv)
- 1 is the core hypothesis (A3: Fisher = physical metric)
- 1 is partially derived (A4: mass tensor, with sign structure imposed)

This is more axioms than "one," but fewer than most competing frameworks.
The honest conclusion: OIG is a multi-axiom framework with a strong
central hypothesis (Fisher metric as physical metric) and a specific
mechanism for Lorentzian signature that is absent from competitors.

### 6.4 Confidence Map

```
Axioms A1-A6 (well-motivated)                    [75-90%]
    |
    v
Exponential family specialization (MaxEnt)        [55-70%]
    |
    v
M = F^2, FSF, beta_c formulas (PROVEN)           [95-99%]
    |
    v
Lorentzian selection (sparse observers)           [70%]
    |            |
    v            v [25-40%]
Learning dynamics      Einstein equations
(PROVEN: Amari)        (CONJECTURED: Routes 1-3)
    [99%]                    |
                             v [20%]
                        Dimensionality d = 3+1
                        (OPEN PROBLEM)
```

---

## Meta

```yaml
document: observer-information-geometry.md
created: 2026-02-17
type: framework-proposal
level: L1 (program-level, foundational)

axioms: 6 (A1-A6)
proven_theorems: 8 (M=F^2, FSF, beta_c, PSD obstruction, Tree Fisher,
  Diagonal Lorentzian, L_gap, natural gradient uniqueness)
conjectures: 5 (Jacobson-OIG, learning=geodesic, effective dimensionality,
  quantum-classical=signature, CI->MaxEnt)
open_problems: 6

comparison_frameworks: 5 (causal sets, CDT, Wolfram, Caticha, Jacobson)
predictions: 5 (P1-P5)
testable_by_experiment: 0 (computational tests only)

key_strengths:
  - Bypasses falsified continuum limit
  - Derives Lorentzian signature (conditional on sparse topology)
  - Connects multiple existing frameworks
  - Mathematically rigorous core results

key_weaknesses:
  - Does not derive Einstein equations
  - Does not explain dimensionality
  - Sign structure imposed, not derived
  - Limited to exponential family observers
  - No experimental predictions

depends_on:
  - MASS-FISHER-SQUARED-PROOF-2026-02-16.md (Theorem A)
  - LORENTZIAN-MECHANISM-FORMAL-ANALYSIS-2026-02-16.md (beta_c, signs)
  - CROSS-PAPER-SYNTHESIS-SESSION24-2026-02-16.md (exponential family thread)
  - SESSION-24-FINAL-SYNTHESIS-2026-02-16.md (program status)
  - Paper #1 manuscript (negative results)
  - Paper #2 manuscript (composition axiom)
  - Paper #3 manuscript (Amari chain)

confidence: 55% overall
  proven_core: 90% (mathematical results)
  physical_interpretation: 50% (Fisher = spacetime metric)
  completeness: 30% (many open problems)
```

---

*Observer Information Geometry: A framework for spacetime emergence from
the Fisher information geometry of observers on causal graphs. Bypasses
the falsified continuum limit by placing geometry in the observer's
parameter space rather than in the graph itself. Derives Lorentzian
signature through the spectral gap mechanism for sparse observers with
signed edges. Does not yet derive Einstein equations, dimensionality, or
the physical origin of edge signs. Requires 6 axioms; core results are
mathematically proven; physical interpretation is provisional.*
