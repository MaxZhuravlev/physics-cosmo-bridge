# CRITICAL PEER REVIEW - Skeptical Assessment

**Reviewer**: Acting as theoretical physics PhD (foundations/quantum gravity)
**Manuscript**: "From Causal Invariance to Quantum Theory"
**Recommendation**: MAJOR REVISIONS REQUIRED

---

## OVERALL ASSESSMENT

**Summary**: The manuscript attempts to connect Wolfram's hypergraph physics with Vanchurin's neural network cosmology via uniqueness theorems. While the empirical work is solid (κ=0.67 validation notable), the theoretical claims are significantly overstated, and several critical gaps undermine the central thesis.

**Major concerns**:
1. Lovelock chain has unjustified step (discrete→diffeomorphisms)
2. "LD emergent" claim not rigorously proven
3. Over-reliance on numerical experiments to substitute for proofs
4. Novelty overstated (~10-15% genuinely new, not 35%)
5. Missing engagement with obvious counterarguments

**Recommendation**: Major revisions. The paper contains useful observations but needs significant modesty in claims.

---

## DETAILED CRITIQUE

### THEOREM 1: Lovelock Chain (CI → Einstein)

#### Claimed Proof Structure

1. CI → Discrete Covariance (Gorard) ✓
2. Continual Limit (κ=0.67 empirical)
3. Discrete Covariance → Diffeomorphisms
4. Lovelock Theorem (1971) ✓
5. Fixes Onsager Tensor

#### CRITICAL PROBLEM: Step 2→3 is NOT PROVEN

**Authors claim**: "Continual limit" validated by κ=0.67

**Reality**:
- κ=0.67 shows *curvature exists* on small graphs (N=9 states!)
- Does NOT prove discrete covariance → diffeomorphism invariance
- Gorard's discrete covariance ≠ smooth diffeomorphisms (different symmetries!)

**Missing**:
- Formal proof that discrete symmetry → continuous symmetry in limit
- Gorard shows Ollivier-Ricci → Ricci (partial), not full diffeomorphism group
- N=9 is TINY - where is N→∞ limit actually tested?

**Counterargument not addressed**:
- Discrete symmetries can BREAK in continuum limit (standard in lattice field theory)
- Authors test κ≠0 (geometry exists) but not diffeomorphism invariance (full symmetry group)
- These are DIFFERENT things!

**Verdict**: Step 3 is ASSUMED, not proven. The empirical test (κ=0.67) does not validate this step.

**Impact**: Entire Lovelock chain rests on unjustified assumption.

---

### THEOREM 2: Amari Chain (Persistence → NG)

#### Claimed Proof

1. Persistence → Modeling (Conant-Ashby)
2. Modeling → Loss
3. Loss → Fisher metric
4. Fisher → Riemannian
5. Amari: Unique NG
6. This is Vanchurin Eq.3.4

#### PROBLEMS

**Problem 1**: Conant-Ashby theorem has SPECIFIC conditions

- Applies to *control systems* with *disturbances*
- Does NOT generally apply to arbitrary "persistent observers"
- Authors do NOT verify hypergraph observers satisfy theorem conditions
- **Missing**: Formal verification that multiway systems ∈ Conant-Ashby domain

**Problem 2**: Step 2 is a LEAP

"Modeling → Loss function emerges"

- This is NOT obvious or proven
- Many models don't minimize loss (e.g., Bayesian posteriors)
- Why GRADIENT descent? Why not other learning rules?
- **Missing**: Proof that modeling NECESSARILY implies loss minimization

**Problem 3**: Two independent inputs (CI + persistence)

- Authors claim "from one axiom" but need TWO
- CI alone doesn't give persistence
- Persistence is ADDITIONAL assumption
- **Misleading**: "From one axiom" (actually needs two)

**Verdict**: Chain has multiple unjustified leaps. NOT rigorous.

---

### THEOREM 3: LD Emergent (Most Problematic)

#### Claimed Proof

"LD emerges from {Purification + Perfect Dist. + Operational Composition}"

#### CRITICAL ISSUES

**Issue 1**: "Operational Composition → Tensor Product" is DEFINITIONAL

- In Chiribella framework, tensor product is HOW you define composition
- NOT a theorem - it's a framework choice
- Authors claim "naturally acquire" - but this is definitional, not derived

**Issue 2**: "Tensor Product → LD" is TAUTOLOGICAL

- LD (local distinguishability) MEANS local marginals determine joint
- This is literally DEFINITION of tensor product (separability)
- Authors "prove" A → A (trivial!)

**Issue 3**: Empirical "confirmation" is BACKWARDS

Authors say:
> "LD emerges at small N (0%), breaks at large N (78%)"

**But**:
- Small N perfect → sampling artifact (only 1134 systems tested!)
- Large N failure → LD does NOT hold generally
- This CONTRADICTS "LD emergent" - if emergent, should STRENGTHEN with scale!

**Authors confused**:
- LD failing at scale ≠ "LD emergent"
- If LD were consequence of purification, should work at ALL scales
- Failure at scale suggests LD is NOT consequence but independent requirement

**Verdict**: Claim is LOGICALLY BACKWARDS. LD failure contradicts "emergent" interpretation.

---

### OBSERVATION 1: Fisher=Riemann (Vanchurin 2017)

**Authors correctly** cite Vanchurin 2017 (after correction).

**But**:
- This is NOT "observation" - it's Vanchurin's result
- Why include in "our" paper at all?
- Adds nothing new

**Should**: Either remove entirely or acknowledge as "recalling Vanchurin 2017"

---

### OBSERVATION 2: Arrow of Time

**Claimed**: dL/dt ≤ 0 + acyclic → deterministic arrow

**Problem**: This is TRIVIAL

- dL/dt ≤ 0: Standard gradient descent (known for centuries)
- Acyclic graphs: Definition of "causal" graph
- "Combination" adds nothing

**Missing**:
- Why is THIS arrow same as THERMODYNAMIC arrow?
- Connection to entropy increase not shown
- Just naming gradient descent "arrow of time" doesn't make it so

**Verdict**: Trivial observation, misleadingly labeled.

---

## EMPIRICAL WORK

### Strengths (Acknowledged)

- κ=0.67 measurement is solid work
- N=20,006 scale impressive for Python
- 6 spatial patterns show robustness
- Code appears reproducible

### Critical Weaknesses

**1. N=9 for "continual limit"**

- Wolfram test: Only 9 states!
- "Continual limit" means N→∞
- Testing at N=9 and claiming "limit confirmed" is ABSURD
- Need N>10,000 minimum for any continuum claim

**2. Purification "100%" misleading**

- Authors test: "Does extended state exist?"
- Of course it does - multiway ALWAYS branches!
- This is testing definition, not axiom
- **Not surprising** that multiway has purification structure

**3. LD "emergence" backwards**

- Perfect at N<200: Sampling artifact (authors admit!)
- Failing at N>5000: LD does NOT generally hold
- **Conclusion should be**: LD fails, not "LD emergent"

---

## MATHEMATICAL RIGOR

### Missing Proofs

**1. Discrete → Continuous** (Step 3 of Lovelock)

- Authors cite κ=0.67 as "proof"
- But κ measures curvature, not symmetry group
- **Missing**: Proof that discrete symmetry group → Diff(M)
- This is CENTRAL claim - cannot be substituted by numerical test!

**2. LD = Consequence**

- Authors claim tensor product → LD
- But tensor product ASSUMES separability = LD
- **Circular**: Assume what you're proving

**3. "Uniqueness" claims**

- Lovelock: Requires diffeomorphisms (not proven from CI)
- Amari: Requires Riemannian manifold (inherited from unproven Step 3)
- **All uniqueness rests on unjustified continual limit**

---

## NOVELTY ASSESSMENT

### Authors Claim: "~35% genuinely new"

### Reviewer Assessment: ~10-15%

**Genuinely new**:
- LD emergence interpretation (~5%, but wrong!)
- Numerical continual limit test (~10%)

**NOT new**:
- Gorard 2020: Already connects CI to GR
- Lovelock 1971: Classical
- Vanchurin 2020: Already has all components
- Amari 1998: Well known
- Chiribella 2011: Complete QM derivation already exists

**"First formal link"**: MISLEADING

- Gorard IS Wolfram team - already connected!
- Vanchurin cites information geometry
- "Link" is just citing both papers together
- Not a mathematical contribution

**"Answering Vanchurin's question"**: WEAK

- Vanchurin asks "can Onsager be derived?"
- Authors answer: "Gorard + Lovelock"
- But Gorard doesn't prove diffeomorphisms (gap!)
- So answer is INCOMPLETE

---

## SPECIFIC TECHNICAL ERRORS

### Error 1: Confusing curvature with symmetry

**Line 117**: "κ=0.67...confirming intrinsic geometry emergence"

**Problem**:
- Curvature (κ) ≠ Symmetry (Diff group)
- Flat space (κ=0) can have diffeomorphism invariance!
- Non-zero κ doesn't prove Diff invariance

**This is undergraduate mistake**

### Error 2: N=9 as "continuum"

**Line 243**: "9 states, causal graph 40 vertices"

**Then Line 117**: "decisively supporting discrete→continuous transition"

**Problem**: 9 states is NOT continuum! This is ridiculous.

### Error 3: Sampling artifact as "emergence"

**Line 275**: "N<200: 0% null (Perfect artifact)"

**Then Line 203**: "LD emerges at small N"

**Problem**: Authors ADMIT it's artifact, then claim it "emerges"!

**Contradiction**: Can't be both artifact AND emergence.

---

## LOGICAL GAPS

### Gap 1: Why these programs converge AT ALL?

**Authors argue**: Uniqueness theorems force convergence

**But**:
- Wolfram: Discrete, no smooth manifold (yet)
- Vanchurin: Continuous, has manifold (from start)
- **Different starting points, different structures**
- Why should discrete CI → continuous Diff be valid?

**Missing**: Argument for why these DIFFERENT frameworks map to each other

### Gap 2: Observer role unclear

**Sometimes**: Observer is part of substrate (embedded)
**Sometimes**: Observer is external (measuring)
**Sometimes**: Observer parameter space IS spacetime

**Inconsistent**: Which is it? These are different things!

### Gap 3: What about non-spatial rules?

**Authors test**: Spatial hypergraphs (triangle, square, etc.)

**But**:
- Wolfram model is ABSTRACT hypergraph (not necessarily spatial)
- Most rules in "Registry of Notable Universes" are NOT spatial
- **Selection bias**: Testing only rules that give desired result?

**Missing**: Test on abstract (non-spatial) rules. Prediction: κ≈0 (as authors found earlier on string rewriting)

---

## FATAL FLAW: Circular Reasoning

### The Circle

1. Authors claim: CI → diffeomorphisms (via continual limit)
2. Test: κ=0.67 on spatial graphs
3. Conclude: Continual limit confirmed
4. Therefore: CI → diffeomorphisms

**But**:
- Spatial graphs are CHOSEN to have geometry (triangles, squares)
- Of course they have curvature!
- This doesn't prove ARBITRARY CI-system → diffeomorphisms
- **Circular**: Test confirms assumption only for pre-selected geometric cases

### What They Should Test

**Falsification**: Take NON-spatial CI-system, measure κ

**Prediction**: If CI → geometry is general, ALL CI-systems should have κ≠0

**Reality**: Abstract string rewriting gave κ≈0 (authors' earlier tests!)

**Conclusion**: κ≠0 is property of SPATIAL rules, not CI in general

**This breaks entire Lovelock chain**.

---

## SPECIFIC RECOMMENDATIONS

### Major Revisions Required

**1. Retract "Theorem" claims**

Replace:
- ❌ "Theorem 1: CI → Einstein"
- ✓ "Conjecture 1: CI → Einstein (if continual limit holds)"

Acknowledge: Step 3 unproven

**2. Fix LD interpretation**

Current: "LD emerges"
Problem: LD FAILS at scale (opposite of emergence)
Correct: "LD holds for finite QM, breaks in thermodynamic limit"

**3. Admit selection bias**

- Tested only spatial rules (pre-selected for geometry)
- Abstract rules gave κ≈0 (negative result!)
- Cannot claim "CI → geometry" generally

**4. Drastically reduce novelty claims**

- ~10% genuinely new (numerical tests)
- ~90% synthesis
- "First formal link": Misleading (Gorard IS Wolfram team!)

**5. Clarify observer role**

- Embedded? External? Parameter space?
- Pick ONE interpretation and stick to it

---

## MISSING REFERENCES

**Critical omissions**:

1. **Discrete→continuous limits**: Vast literature!
   - Lattice gauge theory
   - Renormalization group
   - Asymptotic safety
   - **Why not cite standard results?**

2. **Operational QM**: Earlier work!
   - Hardy 2001 (5 axioms, different from Chiribella)
   - Dakić & Brukner 2009
   - Masanes & Müller 2011
   - **Authors ignore alternative derivations**

3. **Information geometry**: Established field!
   - Amari 1980s work (earlier than 1998)
   - Connection to physics (many papers)
   - **Not novel to connect Fisher to physics**

---

## QUESTIONS FOR AUTHORS

**Q1**: Why does κ=0.67 at N=9 validate continuum limit?

Standard: Need N→∞. You test N=9. Explain.

**Q2**: Abstract string rules gave κ≈0. Why?

If CI → geometry, why do non-spatial CI-systems fail?

**Q3**: Conant-Ashby conditions

Prove hypergraph observers satisfy theorem hypothesis. Currently assumed.

**Q4**: LD fails at large N. How is this "emergence"?

Emergence means property APPEARS with scale. LD DISAPPEARS. Contradiction?

**Q5**: What's genuinely new?

Gorard 2020 already connects CI to GR (you cite him).
Vanchurin 2020 already has Fisher→Riemann (his 2017 paper).
Chiribella 2011 already derives QM from axioms.

What do YOU add beyond "reading all three papers"?

---

## TECHNICAL ERRORS

### Error 1: Dimensions

**Line 125**: "In D≤4 dimensions"

**Lovelock theorem**: Different in D=2,3,4
- D=2: Topological (no propagating GR)
- D=3: No GR at all!
- D=4: Einstein (correct)

**Authors use D≤4** (wrong!) - Lovelock varies by dimension.

Should: D=4 specifically (our universe)

### Error 2: "Empirically confirmed continual limit"

**Throughout manuscript**: κ=0.67 "confirms" continual limit

**Problem**:
- Continual limit is mathematical (N→∞)
- Cannot be "empirically confirmed" at finite N
- Can only be "empirically supported" or "numerically consistent with"

**Language**: Overconfident. No finite test proves limit.

### Error 3: "Purification postulate" in axiom list

**Line 185**: Lists {1,2,3,5}

**Chiribella 2011**:
- 5 axioms: {1,2,3,4,5}
- Purification: Separate postulate (6)

**Authors conflate**: Axiom 5 (pure conditioning) ≠ Purification postulate

**This was noted in corrections** but language still confusing.

---

## COMPARISON WITH EXISTING WORK

### vs Gorard (2020)

**Gorard already**:
- Derives Einstein from CI
- Shows discrete→continuous (partial)
- Connects Wolfram to GR

**Authors add**: Link to Vanchurin (synthesis)

**Novelty**: ~5% (connection is obvious for anyone reading both)

### vs Vanchurin (2020, 2017)

**Vanchurin already**:
- Derives Einstein from neural network
- Has Fisher→Riemann connection (2017)
- Has learning dynamics

**Authors add**: Claim his choice is "forced" (via Gorard)

**Problem**: Forcing argument rests on unproven continual limit

**Novelty**: ~5% (and questionable)

### vs Chiribella (2011)

**Chiribella already**: Complete QM from 6 principles

**Authors claim**: Can do with 4 (LD emergent)

**Problem**:
- LD "emerges" only at small N (artifact!)
- LD fails at large N (contradicts quantum theory for macroscopic!)
- **Authors found LD doesn't generally hold** - this CONTRADICTS Chiribella, not extends!

**Novelty**: ~0% (actually contradicts existing work)

---

## WHAT WOULD STRENGTHEN

### Minimum Viable Paper

**Keep**:
1. κ=0.67 spatial tests (solid numerical work)
2. N=20,006 purification tests (good computation)
3. Observation: Gorard + Vanchurin programs share structure

**Remove**:
4. "Theorem" claims (unjustified)
5. "From one axiom" (need two: CI + persistence)
6. "LD emergent" (backwards - it fails!)
7. Continual limit "confirmed" (only supported)

**Reframe as**:
"Numerical investigations of connections between Wolfram and Vanchurin cosmologies"

**Honest contribution**:
- First to numerically test continual limit (κ=0.67)
- First to systematically compare programs
- Useful synthesis

**No overclaiming**.

---

## MISSING CRITICAL DISCUSSION

### Not Addressed

**1. Universality**

Do ALL CI-systems → geometry?
Authors test only spatial rules.
String rewriting gave κ≈0 (negative!)
**Selection bias not discussed**.

**2. Alternative explanations**

Could programs converge for OTHER reasons?
- Both fit data (not surprising)
- Many theories fit same phenomena
- Convergence ≠ identity

**3. Counterexamples**

Are there CI-systems WITHOUT diffeomorphisms?
Authors don't look for counterexamples.
**Not scientific** - must try to falsify!

**4. Quantum gravity**

If CI → QM and CI → GR, why not CI → quantum gravity?
Authors derive both separately but don't unify.
**Obvious next step** not mentioned.

---

## LANGUAGE ISSUES

### Overclaiming (Throughout)

❌ "We prove" → Should: "We argue"
❌ "Uniquely determined" → Should: "Constrained by"
❌ "Empirically confirmed" → Should: "Numerically consistent with"
❌ "Unconditional theorems" → Should: "Conditional on continual limit"

### Vague Terms

- "Forced to converge" (emotionally loaded)
- "Mathematics left no alternative" (too strong)
- "Decisively" (overused: 8 times!)

**More appropriate**: Scientific modesty

---

## COMPARISON TO STANDARDS

### What Top-Tier Paper Would Have

**Rigor**:
- Every step proven or clearly assumed
- Alternative explanations considered
- Counterexamples sought
- All gaps acknowledged

**This paper**:
- Key step (discrete→diffeomorphisms) unproven
- Alternative explanations not considered
- Counterexamples ignored (string rewriting!)
- Gaps minimized

### What Good Synthesis Would Have

**Synthesis**:
- Clear what's new vs known
- Proper credit to original authors
- Modest claims
- Useful organization

**This paper**:
- Overclaims novelty (35% → actually 10%)
- Takes credit for others' results ("Theorem 4")
- Overly strong claims
- Organization OK

---

## VERDICT BY SECTION

| Section | Quality | Issues |
|---------|---------|--------|
| Abstract | ⚠️ Overclaims | "Prove", "unconditional" too strong |
| Intro | ✓ OK | Clear setup |
| Theorem 1 | ✗ Flawed | Step 3 unproven, N=9 insufficient |
| Theorem 2 | ⚠️ Weak | Multiple leaps, 2 axioms not 1 |
| Theorem 3 | ✗ Wrong | LD failure ≠ emergence, circular |
| Methods | ✓ Good | Solid experimental work |
| Results | ✓ Solid | Data appears sound |
| Discussion | ⚠️ Overstated | Doesn't address obvious issues |
| Conclusions | ⚠️ Too strong | Restate claims modestly |

---

## FINAL RECOMMENDATION

### MAJOR REVISIONS REQUIRED

**Must fix**:
1. Retract "proof" claims → "arguments" or "conjectures"
2. Acknowledge Step 3 (discrete→diffeomorphisms) unproven
3. Fix LD interpretation (fails at scale, not emergent)
4. Drastically reduce novelty claims (~10%)
5. Add critical discussion section
6. Test non-spatial rules (expect κ≈0)
7. Address circular reasoning (spatial selection)

**After revisions**:
- Could be acceptable as "numerical investigations" paper
- NOT as "proof" paper
- Suitable for specialized journal (not PRL/Nature)

### IF AUTHORS REFUSE REVISIONS

**Reject**.

Core claims rest on unjustified Step 3. Cannot publish as "theorem" without proof.

---

## CONSTRUCTIVE SUGGESTIONS

### How to Fix

**Option A**: Prove Step 3 (discrete→diffeomorphisms)

- Rigorous mathematical proof
- Or cite existing proof (if exists)
- Then Lovelock chain valid

**Option B**: Acknowledge limitation

- "Theorem 1 (conditional on continual limit)"
- "Step 3 remains open mathematical question"
- Honest about what's proven vs conjectured

**Option C**: Reframe entirely

- "Numerical evidence for connection"
- "Synthesis of Gorard, Vanchurin, Chiribella"
- Modest, honest contribution

**I recommend Option C**: Honest synthesis paper with good numerical work.

---

## POSITIVE ASPECTS (Acknowledge)

**Good**:
- κ=0.67 measurement (solid)
- 6 spatial patterns (robustness)
- N=20,006 scale (impressive computation)
- Code apparently reproducible
- Honest about some limitations (10 failures documented)

**These are VALUABLE** - just don't overclaim!

---

## RATING

**Scientific Soundness**: 4/10 (empirical OK, theory flawed)
**Novelty**: 3/10 (~10% new, overclaimed as 35%)
**Clarity**: 6/10 (clear writing, but misleading claims)
**Rigor**: 3/10 (key steps unproven)
**Impact**: 5/10 (if revised: useful synthesis)

**Overall**: 4/10 - MAJOR REVISIONS

---

## REVIEWER CONFIDENCE

**High confidence** in this assessment.

I have expertise in:
- Foundations of QM (operational approaches)
- Quantum gravity (discrete→continuous)
- Information geometry

The errors identified are fundamental, not nitpicks.

---

**RECOMMENDATION**: Major revisions or reject.

Core theoretical claims unsupported. Empirical work alone insufficient for "proof" paper.

Reframe as synthesis/numerical investigation → potentially acceptable.

As currently written → not publishable in serious journal.

---

_Reviewed 2026-02-14_
_Critical peer review complete_
