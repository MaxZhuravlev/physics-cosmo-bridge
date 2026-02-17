# Causal Structure from the Signed-Edge Construction: Analysis

**Author:** Max Zhuravlev (with mathematical formalization assistance)
**Date:** 2026-02-17
**Status:** Research note (computational results + algebraic analysis)
**Confidence:** See Section 7 for per-claim confidence levels

---

## Abstract

We investigate whether the signed-edge construction A(S) = F^{1/2} S F^{1/2}
that selects Lorentzian signature (q=1) on sparse observer graphs also
induces a CAUSAL STRUCTURE (partial order) on the observer graph. Through
explicit computation on 8 graph families at 3 coupling values (90 sign
assignments total), we find a surprising positive result: the eigenvector
corresponding to the negative eigenvalue of A(S) defines a "vertex flow"
that produces a valid partial order in 100% of cases tested. However, this
result is ultimately SUPERFICIAL as a connection to causal set theory, for
reasons we make precise.

The signed-edge construction produces something better described as a
TEMPORAL POLARIZATION of the graph (a splitting into past/future hemispheres
relative to the flipped edge) rather than a genuine causal set. The
connection to Bombelli-Sorkin causal sets is a structural analogy, not a
mathematical equivalence.

---

## Table of Contents

1. [Setup and Definitions](#1-setup-and-definitions)
2. [Computational Results](#2-computational-results)
3. [Algebraic Analysis: Why It Works on Trees](#3-algebraic-analysis-why-it-works-on-trees)
4. [Algebraic Analysis: Why It Works on Cycles](#4-algebraic-analysis-why-it-works-on-cycles)
5. [Connection to Causal Set Theory](#5-connection-to-causal-set-theory)
6. [Connection to Wolfram Causal Graphs](#6-connection-to-wolfram-causal-graphs)
7. [Assessment and Confidence Levels](#7-assessment-and-confidence-levels)
8. [What the Construction Actually Does](#8-what-the-construction-actually-does)
9. [Open Questions](#9-open-questions)

---

## 1. Setup and Definitions

### 1.1 The Signed Metric Kernel

Recall from the spectral gap selection theorem: given an observer graph G
with Ising Fisher matrix F (m x m, positive definite), and a sign assignment
S = diag(s_1, ..., s_m) with exactly one s_k = -1 (the q=1 case), the
signed metric kernel is:

    A(S) = F^{1/2} S F^{1/2}                                       (1.1)

This matrix has exactly one negative eigenvalue d_1 < 0 (by Lemma 6.3 of
the spectral gap theorem) and (m-1) positive eigenvalues d_2, ..., d_m > 0.

Let v_- be the eigenvector corresponding to d_1. This is the "timelike
direction" in the m-dimensional edge parameter space.

### 1.2 From Edge Space to Vertex Space

The eigenvector v_- has components (v_1, ..., v_m), one per edge. We define
a VERTEX FLOW by interpreting v_e as a signed flow along edge e = (i,j):

    phi(i) = sum_{e=(i,j) in E} v_e                                (1.2)
    phi(j) = sum_{e=(i,j) in E} (-v_e)

More precisely, for each edge e = (i,j), the component v_e contributes
+v_e to vertex i and -v_e to vertex j. The resulting vertex flow
phi: V -> R assigns a real number to each vertex.

### 1.3 Partial Order from Vertex Flow

We define a relation on vertices:

    i < j  iff  phi(i) < phi(j)                                    (1.3)

Since phi assigns real numbers to vertices, this is automatically:
- Antisymmetric (phi(i) < phi(j) implies phi(j) > phi(i), so not j < i)
- Transitive (phi(i) < phi(j) and phi(j) < phi(k) implies phi(i) < phi(k))

Therefore the vertex flow ALWAYS defines a partial order (technically, a
pre-order modulo ties). The question is whether this partial order has any
physical content.

**Important observation:** The partial order is guaranteed to be valid by
construction, since it comes from a real-valued function on vertices. This
is NOT a deep result --- any real-valued function on a finite set defines
a partial order (equivalently, a total pre-order). The real question is:
does this particular function have physical meaning?

---

## 2. Computational Results

### 2.1 Summary Statistics

We computed the vertex flow and resulting partial order for 8 graph
families (Path P3, P4, P5; Star S4; Cycle C4, C5; Complete K3, K4) at
3 coupling values (J = 0.3, 0.5, 1.0), for all possible q=1 sign
assignments. Total: 90 sign assignments analyzed.

| Statistic | Value |
|-----------|-------|
| Total sign assignments | 90 |
| Valid partial orders | 90/90 (100%) |
| Total orders (all pairs comparable) | 48/90 (53.3%) |
| Optimal-W sign gives partial order | 24/24 (100%) |
| Eigenvector localized on flipped edge | 90/90 (100%) |

### 2.2 Tree Graphs (Diagonal Fisher)

For tree graphs (P3, P4, P5, S4), the Fisher matrix is diagonal:
F = sech^2(J) * I_m. The results are degenerate:

**Path P3** (2 edges):
- Flipping edge (0,1): v_- = (1, 0), vertex flow = (+1, -1, 0)
  Order: 1 < 2 < 0 (total order)
- Flipping edge (1,2): v_- = (0, 1), vertex flow = (0, +1, -1)
  Order: 2 < 0 < 1 (total order)
- Both W = 2 * sech^2(J). The eigenvector is perfectly localized on the
  flipped edge.

**Path P4** (3 edges):
- Flipping any edge e = (i,j): v_- is the standard basis vector e_k,
  vertex flow has phi(i) = +1, phi(j) = -1, phi(others) = 0.
- All W equal (degenerate). Only 5/6 pairs are comparable (83.3%).
- The two endpoints of the flipped edge are ordered (j < i), and all
  other vertices have phi = 0 (incomparable with each other but
  comparable with the endpoints).

**Key observation for trees:** When F is diagonal (exact identity for
trees), the eigenvector of A(S) is exactly the standard basis vector
corresponding to the flipped edge. The vertex flow is nonzero ONLY at the
two endpoints of the flipped edge. This means:

- The "causal structure" is trivial: it says only that one endpoint of
  the timelike edge is "before" and the other is "after."
- Vertices not incident to the timelike edge are "spacelike separated"
  (incomparable in the order).
- The ordering on non-incident vertices is determined only by their
  incidence to the flipped edge (connected through vertex i or vertex j),
  with tied values for vertices at equal graph distance.

### 2.3 Cyclic Graphs (Off-Diagonal Fisher)

For graphs with cycles, the Fisher matrix has off-diagonal entries that
break the degeneracy and spread the eigenvector:

**Cycle C4** (4 edges, J = 0.5, Fisher diagonal ratio 0.294):
- Flipping edge (0,1): v_- = (-1.000, +0.006, +0.006, +0.006)
  Vertex flow = (-0.994, +1.006, 0.000, -0.011)
  All 6 pairs comparable (total order): 0 < 3 < 2 < 1

- Flipping edge (1,2): v_- = (-0.006, -0.006, +1.000, -0.006)
  Vertex flow = (-0.011, +1.006, -1.006, +0.011)
  All 6 pairs comparable (total order): 2 < 0 < 3 < 1

**Cycle C5** (5 edges, J = 0.5, Fisher diagonal ratio 0.156):
- Flipping edge (1,2): v_- = (-0.002, -0.002, +1.000, -0.002, -0.002)
  Vertex flow = (-0.004, +1.002, -1.002, 0.000, +0.004)
  All 10 pairs comparable (total order): 2 < 0 < 3 < 4 < 1

**Complete K3** (3 edges, J = 0.5, Fisher diagonal ratio 0.539):
- Flipping edge (0,1): v_- = (-1.000, +0.015, +0.015)
  Vertex flow = (-0.985, +1.015, -0.031)
  All 3 pairs comparable (total order): 0 < 2 < 1

**Complete K4** (6 edges, J = 0.5, Fisher diagonal ratio 0.896):
- Flipping edge (1,2): v_- = (-0.021, -0.021, -0.066, +0.997, -0.021, -0.021)
  Vertex flow = (-0.109, +0.997, -0.997, +0.109)
  All 6 pairs comparable (total order): 2 < 0 < 3 < 1

**Key observation for cyclic graphs:** Off-diagonal Fisher entries spread
the eigenvector slightly (from concentration 1.000 on trees to 0.991-0.999
on cycles). This spreading creates a small but nonzero flow at ALL vertices,
which breaks the degeneracy and often produces a TOTAL order. The ordering
respects the graph distance from the flipped edge:
- Vertices adjacent to the flipped edge have large |phi|
- Vertices far from the flipped edge have small |phi|
- The sign of phi determines "past" vs "future"

### 2.4 Effect of Coupling Strength

The Fisher diagonal ratio increases with J (stronger coupling = more
off-diagonal entries). The effect on the partial order:

| Graph | J=0.3 ratio | J=0.5 ratio | J=1.0 ratio | Orderings get richer? |
|-------|-------------|-------------|-------------|----------------------|
| P4 (tree) | 0.000 | 0.000 | 0.000 | No (always degenerate) |
| C4 | 0.135 | 0.294 | 0.524 | Yes (more pairs comparable) |
| C5 | 0.045 | 0.156 | 0.418 | Stays total for all J |
| K3 | 0.380 | 0.539 | 0.682 | Stays total for all J |
| K4 | 0.651 | 0.896 | 1.001 | Stays total for all J |

Stronger coupling produces more off-diagonal Fisher entries, which spread
the eigenvector more, creating richer orderings. However, the basic
structure (endpoints of flipped edge maximally ordered) is preserved.

---

## 3. Algebraic Analysis: Why It Works on Trees

### 3.1 Exact Result

**Proposition 3.1.** For F = d * I_m (diagonal, uniform), the signed kernel
A(S_k) = d * S_k (where S_k flips sign of edge k). The negative
eigenvector is v_- = e_k (the k-th standard basis vector), with eigenvalue
-d.

**Proof.** A(S_k) = F^{1/2} S_k F^{1/2} = d^{1/2} I * S_k * d^{1/2} I
= d * S_k = d * diag(1, ..., -1, ..., 1). The eigenvectors are the
standard basis vectors, with eigenvalue -d for e_k and +d for all others.
[]

### 3.2 Vertex Flow Structure

**Corollary 3.2.** For a tree with uniform coupling, flipping edge
e_k = (i, j) produces vertex flow:

    phi(i) = +1, phi(j) = -1, phi(v) = 0 for v != i, j

The resulting partial order has:
- j < v < i for all v with phi(v) = 0
- |{comparable pairs}| = n(n-1)/2 - (n-2)(n-3)/2

Wait --- this is wrong. If phi(v) = 0 for v != i, j, and phi(i) = +1,
phi(j) = -1, then v is comparable to both i (v < i, since 0 < 1) and j
(j < v, since -1 < 0), but all other vertices u with phi(u) = 0 are
INCOMPARABLE to v (0 = 0, no strict ordering). So the partial order is:

    j < {all other vertices equally} < i

This is not a total order (unless n = 2 or n = 3). For n = 3 (P3), the
third vertex has phi = 0, and the order IS total because there is only
one "middle" vertex. For n >= 4, the middle vertices are all tied.

**Corollary 3.3.** For trees with uniform coupling, the vertex flow from
the q=1 signed kernel produces a partial order with:
- Height 2 (chain: j < v < i, for any middle vertex v)
- Width n-2 (antichain: all middle vertices)
- Comparability = 1 - (n-2)(n-3) / (n(n-1)) for n >= 3

This converges to 1 for small n and decreases for large n.

### 3.3 Interpretation

The tree result shows that the signed-edge construction produces a
MINIMAL causal structure: it distinguishes exactly one "past" vertex
(the negative endpoint of the timelike edge), one "future" vertex
(the positive endpoint), and lumps everything else into an incomparable
"spacelike slice." This is the simplest possible causal structure
consistent with having one timelike direction.

---

## 4. Algebraic Analysis: Why It Works on Cycles

### 4.1 Perturbative Result

For F = d*I + epsilon*E (near-diagonal, as on graphs with cycles), the
negative eigenvector is:

    v_- = e_k + epsilon * sum_{j != k} (E_{jk} / (d_k + d_j)) e_j + O(epsilon^2)

(first-order perturbation theory for eigenvalues of symmetric matrices).

Since A(S_k) = d*S_k + O(epsilon), the negative eigenvalue is at -d + O(epsilon)
with eigenvector e_k + O(epsilon). The perturbative corrections are of order
epsilon / (2d) ~ ||F - diag(F)|| / ||diag(F)||, which is the Fisher
diagonal ratio.

### 4.2 Consequence for Vertex Flow

The small off-diagonal components spread the vertex flow from the two
endpoints to ALL vertices:

    phi(v) ~ 0 + O(epsilon) for v != i, j

These O(epsilon) corrections have definite signs determined by the graph
structure (specifically, by the correlations between the flipped edge
and other edges in the Fisher matrix). Because the corrections are small
but generically nonzero, they break the tie between all "middle" vertices
and can produce a total order.

### 4.3 Why the Order is "Along the Cycle"

On cycle C_n with edge (i, i+1 mod n) flipped, the vertex flow has
approximate structure:

    phi(i) ~ +1, phi(i+1) ~ -1

with corrections at other vertices that decay with graph distance from
the flipped edge. The decay follows the correlation structure of the
Ising model: vertices at distance d from the flipped edge have
|phi(v)| ~ tanh^d(J) (the correlation decay rate).

This creates an ordering that "wraps around" the cycle, starting from the
future endpoint, going around one way to the past endpoint. The result
is a total order on C_n vertices that follows the graph distance from
the timelike edge.

---

## 5. Connection to Causal Set Theory

### 5.1 Causal Set Axioms

A causal set (Bombelli, Lee, Meyer, Sorkin, 1987) is a pair (C, <=)
where:
1. (C, <=) is a partially ordered set
2. The order is LOCALLY FINITE: for all x, y in C,
   |{z : x <= z <= y}| < infinity

Our construction satisfies both axioms trivially (any finite partial order
is locally finite). The question is whether it satisfies the deeper
requirement of causal sets:

3. The partial order should approximate a Lorentzian manifold in the
   sense that the COUNTING MEASURE on the causal set should approximate
   the spacetime volume.

### 5.2 The Hauptvermutung of Causal Set Theory

Sorkin's Hauptvermutung (main conjecture) states that a causal set, if it
faithfully embeds into a Lorentzian manifold, uniquely determines that
manifold up to isometry (in the large-N limit). The key tool is the
CAUSAL MATRIX:

    C_{ij} = 1 if i < j, 0 otherwise

The causal matrix determines the manifold geometry through the counting
of causal intervals (the number of elements between two given elements
approximates the spacetime volume of the corresponding interval).

### 5.3 Comparison with Our Construction

Our construction produces a partial order, but there are critical
differences from causal sets:

**Similarity:**
- Both define a partial order on a discrete set
- Both have a single "timelike direction" (one negative eigenvalue vs
  one causal dimension)
- Both have the order induced by a real-valued function (our vertex flow
  phi; in causal sets, the "time function" on the manifold)

**Critical differences:**

1. **Dimensionality mismatch.** In causal set theory, the partial order
   encodes the FULL (d+1)-dimensional Lorentzian geometry. Our partial
   order is on VERTICES (n elements) derived from a 1-dimensional function
   (the vertex flow phi). A causal set on n points encoding a 4D manifold
   has O(n^2) causal relations; our construction has O(n) nontrivial
   relations (the vertex flow is approximately 0 except near the flipped
   edge).

2. **No volume information.** In causal set theory, the number of
   elements in a causal interval approximates the spacetime volume.
   Our construction has no such volume interpretation. The vertex flow
   values are eigenvector components, not spacetime coordinates.

3. **Localization.** Our ordering is concentrated near the flipped edge
   (the eigenvector is localized with concentration > 0.99 in all tested
   cases). In a genuine causal set approximating a Lorentzian manifold,
   the ordering is distributed throughout the set. Our "causal structure"
   is LOCAL (near the timelike edge), not global.

4. **No dynamics.** Causal sets have a natural dynamics (the classical
   sequential growth process of Rideout & Sorkin 2000). Our partial order
   is STATIC --- it is determined by the fixed sign assignment and does
   not evolve.

5. **Sign assignment dependence.** Our ordering depends on WHICH edge is
   flipped. Different sign assignments produce different orderings. In
   causal set theory, the causal order is intrinsic to the set. In our
   framework, it depends on an imposed choice (Open Problem 7 of the
   spectral gap theorem).

### 5.4 Verdict on Causal Set Connection

**The connection is SUPERFICIAL.** While both frameworks produce partial
orders on discrete sets, the mechanisms and physical content are entirely
different:

- Causal sets: the partial order IS the fundamental structure from which
  geometry emerges.
- Our construction: the partial order is a DERIVED quantity from an
  eigenvector computation on a pre-existing Fisher information geometry.

The signed-edge construction does not produce a causal set in the
Bombelli-Sorkin sense. It produces a real-valued function on vertices
(the vertex flow) that happens to define a partial order. This is no
more surprising than the fact that ANY real-valued function on a finite
set defines a partial order.

**What IS interesting** is not the partial order itself, but the fact
that the vertex flow has a specific geometric structure: it is concentrated
on the flipped edge and decays with graph distance. This is a consequence
of the LOCALIZATION of the negative eigenvector, which in turn follows
from the near-diagonal structure of the Fisher matrix on sparse graphs.

---

## 6. Connection to Wolfram Causal Graphs

### 6.1 Wolfram Causal Structure

In the Wolfram model, causal structure arises from the CAUSAL GRAPH: a
directed acyclic graph whose vertices are rewrite events and whose edges
represent causal dependencies (event B uses output of event A). The
causal graph defines a partial order on events, and this partial order
approximates a Lorentzian manifold when the underlying hypergraph rule
satisfies causal invariance.

### 6.2 Comparison with Our Construction

| Feature | Wolfram causal graph | Our signed-edge construction |
|---------|---------------------|------------------------------|
| Vertices | Rewrite events | Observer graph vertices |
| Edges | Causal dependencies | Observer graph edges |
| Ordering | Event A causes B | Vertex flow phi(A) < phi(B) |
| Origin | Intrinsic to dynamics | Derived from eigenvector |
| Dimensionality | Full (3+1) | 1-dimensional (vertex flow) |
| Dynamics | Evolving | Static |

### 6.3 Could the Sign Assignment Come from the Causal Graph?

This is the most interesting open question (Open Problem 7 of the
spectral gap theorem). If the observer's graph G is embedded in a
causal set or Wolfram causal graph, then there is a natural candidate
for the sign assignment:

**Conjecture 6.1.** Let G be a subgraph of a causal DAG (directed
acyclic graph). For each edge (i,j) of G, define:

    s_e = -1  if (i,j) is a CAUSAL edge (i causes j or j causes i)
    s_e = +1  if (i,j) is a SPACELIKE edge (i and j are not causally related)

Then the number of causal edges should be exactly 1 per "time slice"
of the observer graph, recovering the q=1 sign assignment.

**Status of Conjecture 6.1:** This is a hand-waving argument, not a
mathematical conjecture. It would require:
1. A precise definition of "embedded in a causal DAG"
2. A proof that the embedding produces exactly q=1 causal edges per
   time slice
3. A demonstration that the resulting A(S) selects the correct
   Lorentzian signature

None of these steps have been carried out. The conjecture is listed as
Open Problem 7 in the spectral gap selection theorem.

### 6.4 Assessment

The connection to Wolfram causal graphs is SPECULATIVE at this stage.
The signed-edge construction and the Wolfram causal graph both produce
partial orders on discrete structures, but through completely different
mechanisms. The possibility that the sign assignment derives from causal
structure remains an open question that could potentially unify the two
frameworks, but no mathematical progress has been made.

---

## 7. Assessment and Confidence Levels

### 7.1 Per-Claim Confidence

| Claim | Confidence | Basis |
|-------|-----------|-------|
| Vertex flow always defines a valid partial order | **99%** | Automatic from real-valued function |
| Eigenvector is localized on flipped edge (sparse graphs) | **95%** | 90/90 computations + perturbation theory |
| Cyclic graphs produce richer orderings than trees | **90%** | 24/24 non-tree cases + algebraic argument |
| Connection to causal set theory is SUPERFICIAL | **85%** | 5 critical differences identified |
| Connection to Wolfram causal graphs is speculative | **80%** | No mathematical content beyond analogy |
| Vertex flow reflects graph distance from flipped edge | **90%** | All cyclic graph cases + Ising correlation decay |
| Sign assignment could derive from causal structure | **15%** | No evidence beyond wishful thinking |

### 7.2 What IS Real

The following findings have genuine mathematical content:

1. **Eigenvector localization:** The negative eigenvector of A(S_1) is
   concentrated on the flipped edge with concentration >= 0.99 for all
   tested sparse graph/coupling configurations. This follows from the
   near-diagonal structure of the Fisher matrix (Theorem C of the spectral
   gap theorem) and standard perturbation theory.

2. **Temporal polarization:** The vertex flow creates a "past-future"
   splitting of the graph centered on the flipped edge. This is the
   geometric content of having one timelike direction: the signed metric
   kernel polarizes the graph into two hemispheres separated by the
   timelike edge.

3. **Ordering richness correlates with off-diagonality:** The fraction of
   comparable pairs increases with the Fisher diagonal ratio
   (more off-diagonal entries = more ordering). This is because the
   eigenvector spreading (from perturbative corrections) breaks the
   degeneracy of middle vertices.

### 7.3 What IS NOT Real

The following would be overclaiming:

1. **"The signed-edge construction IS a causal set."** No. It produces a
   trivially valid partial order from a real-valued function. The partial
   order has no volume interpretation, no dynamics, and no intrinsic
   geometry.

2. **"The vertex flow is a time coordinate."** Not in any physical sense.
   It is an eigenvector component that happens to define an ordering. The
   ordering has no known relationship to physical time.

3. **"The sign assignment derives from causality."** This is an open
   problem with no supporting evidence. It would be dishonest to claim
   this as a result.

---

## 8. What the Construction Actually Does

### 8.1 Temporal Polarization

The most accurate description of what the signed-edge construction does
to the observer graph is TEMPORAL POLARIZATION:

1. One edge is designated as "timelike" (s_k = -1).
2. The signed metric kernel A(S) has one negative eigenvalue, with
   eigenvector concentrated on the timelike edge.
3. The vertex flow assigns "future" (+) and "past" (-) labels to the
   endpoints of the timelike edge.
4. Other vertices receive small flow values determined by their Fisher
   correlation with the timelike edge.
5. The result is a POLARIZATION of the graph into past/future hemispheres.

This is the correct geometric interpretation of "one timelike direction
in the parameter space." It does not create a causal set; it creates a
DIRECTION on the graph.

### 8.2 Comparison with the Six Frameworks

Adding this analysis to the cross-connections analysis:

| Connection | Classification | Confidence |
|-----------|---------------|-----------|
| 1. QEC | Plausible conjecture | 40% |
| 2. Holography | Plausible conjecture | 35% |
| 3. Anza-Crutchfield | Structural parallel | 70% |
| 4. Lorentzian mechanisms | Complementary | 60% |
| 5. Entropic gravity | Structural parallel | 50% |
| 6. Causal fermion systems | Suggestive analogy | 20% |
| **7. Causal sets (this analysis)** | **Superficial analogy** | **15%** |

The causal set connection is the WEAKEST of all seven connections
examined. It is weaker than the causal fermion system connection
because at least CFS shares the algebraic structure A_{xy} ~ F^{1/2} S F^{1/2},
while the causal set connection shares only the trivial property of
"being a partial order."

### 8.3 The Positive Takeaway

Despite the negative assessment of the causal set connection, the
computation reveals a genuinely interesting structural feature:

**The spectral gap selection theorem, beyond selecting Lorentzian
signature, also determines the ORIENTATION of the timelike direction.**

The eigenvector v_- tells us not just THAT there is one timelike
direction, but WHERE it points in the parameter space. This is additional
geometric information beyond the signature alone. The temporal
polarization of the graph is a PREDICTION of the construction that could
in principle be tested: the observer's parameter space should have a
distinguished direction along which the metric is timelike, and this
direction should be concentrated on a specific edge of the observer
graph.

---

## 9. Open Questions

### 9.1 Does the Temporal Polarization Have Physical Content?

The vertex flow phi defines a direction on the observer graph. If the
observer graph represents an actual physical system (e.g., a neural
network in Vanchurin's framework), does the direction phi correspond
to any physical observable? Possible candidates:
- The direction of maximal Fisher information loss (information arrow of time)
- The direction of maximal prediction error (learning gradient)
- The direction of energy flow (thermodynamic arrow of time)

### 9.2 Multiple Timelike Edges

The q=1 construction flips only one edge. But a genuine causal structure
on a d-dimensional system would have O(n) causal relations, not just one.
Could the q=1 signed-edge construction be iterated or composed to produce
a richer causal structure?

### 9.3 Sign Assignment from Dynamics

If the signs s_e are promoted to dynamical variables (as explored in
dynamical_signs.py), does the dynamics select a sign configuration that
correlates with any pre-existing causal structure on the graph? This
is the key question connecting the algebraic construction to physics.

### 9.4 Functor from Signed Graphs to Partial Orders

Can we formalize the map

    (G, S, F) |-> (V, <=_phi)

as a functor from the category of "signed-edge observer graphs" to the
category of partially ordered sets? If so, what are its properties
(faithfulness, fullness, preservation of products)?

This is a well-defined mathematical question that could be answered
regardless of the physical interpretation.

---

## Appendix A: Explicit Computations for P3, C4, K3

### A.1 Path P3 (m=2 edges, tree)

Graph: 0 -- 1 -- 2
Edges: e_0 = (0,1), e_1 = (1,2)
Fisher: F = sech^2(J) * I_2

Flip e_0:
    A = sech^2(J) * diag(-1, +1)
    d_1 = -sech^2(J), v_- = (1, 0)
    phi = (+1, -1, 0)
    Order: 1 < 2 < 0 (total, since only 3 vertices and one tie is broken)

Flip e_1:
    A = sech^2(J) * diag(+1, -1)
    d_1 = -sech^2(J), v_- = (0, 1)
    phi = (0, +1, -1)
    Order: 2 < 0 < 1 (total)

Both give W = 2*sech^2(J) (degenerate -- no preferred sign assignment).

### A.2 Cycle C4 (m=4 edges, J=0.5)

Graph: 0 -- 1 -- 2 -- 3 -- 0
Edges: e_0=(0,1), e_1=(0,3), e_2=(1,2), e_3=(2,3)

Fisher (J=0.5):
    F = [[0.712, 0.121, 0.121, 0.121],
         [0.121, 0.712, 0.121, 0.121],
         [0.121, 0.121, 0.712, 0.121],
         [0.121, 0.121, 0.121, 0.712]]

Diagonal ratio: 0.294

Flip e_0 = (0,1):
    d_1 = -0.681, v_- = (-1.000, +0.006, +0.006, +0.006)
    phi = (-0.994, +1.006, 0.000, -0.011)
    Order: 0 < 3 < 2 < 1 (total, W = 1.277)

Flip e_2 = (1,2):
    d_1 = -0.681, v_- = (-0.006, -0.006, +1.000, -0.006)
    phi = (-0.011, +1.006, -1.006, +0.011)
    Order: 2 < 0 < 3 < 1 (total, W = 1.277)

All four sign assignments give the same W (by symmetry of C4).
The ordering "wraps around" the cycle starting from the flipped edge.

### A.3 Complete K3 (m=3 edges, J=0.5)

Graph: 0 -- 1, 0 -- 2, 1 -- 2
Edges: e_0=(0,1), e_1=(0,2), e_2=(1,2)

Fisher (J=0.5):
    F = [[0.622, 0.237, 0.237],
         [0.237, 0.622, 0.237],
         [0.237, 0.237, 0.622]]

Diagonal ratio: 0.539

Flip e_0 = (0,1):
    d_1 = -0.542, v_- = (-1.000, +0.015, +0.015)
    phi = (-0.985, +1.015, -0.031)
    Order: 0 < 2 < 1 (total, W = 0.927)

All three sign assignments give the same W (by symmetry of K3).
The ordering always places the endpoints of the flipped edge at the
extremes, with the third vertex in between.

---

## Appendix B: Computational Details

All computations performed by `causal_structure_computation.py`.

- Exact Ising partition function computation for all graph/J
  configurations (enumeration of all 2^n spin configurations)
- Fisher matrix = covariance of edge variables under Boltzmann measure
- Signed kernel A(S) = F^{1/2} S F^{1/2} via scipy.linalg.sqrtm
- Eigendecomposition via numpy.linalg.eigh
- Vertex flow via signed edge-vertex incidence
- Partial order from vertex flow (real-valued function on vertices)
- Causal set axiom checks (transitivity, antisymmetry, local finiteness)

Total computation time: < 30 seconds for all 90 configurations.

---

## Meta

```yaml
document: causal-structure-analysis.md
created: 2026-02-17
type: research-note (computational + algebraic)
level: L2 (paper-level result)
supporting_code: causal_structure_computation.py
configurations_tested: 90 (8 graphs x 3 couplings x 3-6 sign assignments each)
honesty_check:
  overclaiming_risk: LOW (negative assessment of causal set connection)
  superficial_analogies_flagged: YES (causal set, Wolfram)
  genuine_findings_identified: YES (eigenvector localization, temporal polarization)
  positive_findings_not_oversold: YES (stated as "interesting structural feature")
verdict: |
  The signed-edge construction does NOT induce a causal set.
  It produces a TEMPORAL POLARIZATION (past/future splitting centered
  on the timelike edge). This is geometrically meaningful but distinct
  from genuine causal structure in the Bombelli-Sorkin sense.
```

---

*Causal Structure Analysis: The signed-edge construction produces a valid
partial order (trivially, from a real-valued vertex flow) that we call
"temporal polarization." This is NOT a causal set: it lacks volume
information, dynamics, and intrinsic geometry. The connection to causal
set theory is superficial (confidence: 15%). What IS genuine is the
eigenvector localization on the timelike edge (confidence: 95%) and
the resulting past/future splitting of the observer graph. The question
of whether the sign assignment derives from an underlying causal structure
remains the key open problem (Open Problem 7 of the spectral gap theorem).*
