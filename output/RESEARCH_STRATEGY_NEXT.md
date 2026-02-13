# Research Strategy After MacBook Tests
**Date**: 2026-02-13
**Status**: Core bridge proven, QM sector needs alternative approach

---

## Current Situation

### SOLID (Mathematical theorems, independent of simulations)
- ✅ Lovelock chain: CI → unique gravity
- ✅ Amari chain: persistence → unique learning dynamics
- ✅ Fisher = Riemann (consequence of Lovelock)
- ✅ Arrow of time (dL/dt ≤ 0)
- ✅ Cross-program prediction (Shannon, ρ=0.47)

### PROBLEM (Empirical contradiction)
- ⚠️ **LD fails at scale** (null_dim=339-390 for N>500)
  - Was 0 for N<200 (1134/1134, 20/20)
  - **Sampling artifact** discovered
  - **Undermines Chiribella QM derivation**

### UNRESOLVED
- ⚠️ Dirac orientation (all attempts → α=0)
- ⏳ Continual limit (κ≠0 partial, 2/5 systems)

---

## Three Research Directions

### PRIORITY 1: Alternative QM Path (★★★★★)
**Problem**: Chiribella requires LD (Axiom 4), which fails at scale.

**Solution paths**:

**A. Purification without LD**
- Chiribella Axiom 5 (purification) may work independently
- Compact structure of multiway (branching + confluence)
- **Test**: Formal check if purification holds without full LD

**B. Coarse-grained unitarity**
- Global confluence ≠ unitary (proven, 0.67-1.0 deviation)
- But maybe unitary on **subspaces**?
- SVD showed top modes → projector structure
- **Test**: Effective unitarity after coarse-graining

**C. Category theory**
- Dagger-compact categories (Coecke/Abramsky)
- Purification = compact object condition
- Approximate dagger verified (34-92%)
- **Test**: Does approximate structure suffice?

**Recommended**: Start with **A (purification)** - most direct.

---

### PRIORITY 2: LD Mechanism Investigation (★★★★☆)
**Question**: WHY does rank collapse at depth 4→5?

**Hypothesis**: States at large depth have overlapping children distributions.
Not enough local diversity to distinguish globally.

**Tests**:
1. **Cumulative LD**: Test null_dim for depths ≤d (inductive)
2. **Spatial graphs**: Does LD work for 2D/3D embedded hypergraphs?
3. **Information-theoretic bound**: Maximum distinguishability vs graph properties

**Key**: If LD works for spatial but not abstract graphs → dimension matters.

---

### PRIORITY 3: Dirac Physics Orientation (★★★★)
**Problem**: All tested orientations degenerate (α=0)
- Descendants: all E- (monot decreasing)
- Lex: trivial M⁺M⁻=0

**Physics-motivated orientation**:
Hyperedge vertex order = NATURAL orientation
- {{1,2,3}} → {{4,5,6}}: (1→4, 2→5, 3→6) mapping
- Preserves structure of vertex roles
- Intrinsic to hypergraph, not ad hoc

**Test**: Implement on rules with explicit vertex correspondence.

---

## Actionable Next Steps

### Immediate (This Session)
1. ✅ MacBook tests completed
2. ⏭️ **Investigate purification path** (QM without LD)
3. ⏭️ **Test cumulative LD** (inductive proof)
4. ⏭️ **Try hyperedge vertex orientation** for Dirac

### This Week
5. Update note to Vanchurin with honest findings
6. Formalize purification argument
7. If purification works → QM sector closes via alternative path

### Long-term
8. SetReplace tests on spatial hypergraphs (if Wolfram Engine accessible)
9. Submit preprint (conservative: Lovelock+Amari, honest: QM open)
10. Contact Vanchurin/Gorard with findings

---

## Strategic Assessment

**What we have**:
- Solid bridge: gravity + dynamics (theorems, unconditional except continual limit)
- Partial QM: 4/5 Chiribella axioms (LD problematic)
- New prediction: Dirac from orientation (if right definition found)

**What we need**:
- Alternative QM path (purification most promising)
- OR honest limitation: "QM mechanism open, requires spatial graphs"

**Publication readiness**:
- **NOW**: Lovelock+Amari bridge (solid, publishable)
- **After purification test**: Full QM claim (if works)
- **After spatial tests**: Continual limit claim (if κ≠0 stable)

---

## Code Assets Created

- `hypergraph_engine.py` - multiway evolution ✓
- `ollivier_ricci.py` - curvature calculation ✓
- `run_critical_tests.py` - full test suite ✓
- `deep_analysis.py` - investigation tools ✓
- `corrected_tests.py` - improved protocols ✓

All ready for further tests.

---

## Recommended Immediate Actions

### Test 1: Purification Path (30 min)
```python
# Formal check: Does purification axiom hold for multiway systems?
# Purification: For any mixed state ρ, exists pure |ψ⟩ in larger space
#               such that Tr_bath(|ψ⟩⟨ψ|) = ρ
#
# Multiway analog: branch structure provides purification space
```

### Test 2: Cumulative LD (30 min)
```python
# Inductive proof: If null_dim(d)=0 and dynamics connects all states,
#                  then null_dim(d+1)=0
#
# Test on wolfram up to depth where it breaks (d=4)
```

### Test 3: Hyperedge Vertex Orientation (45 min)
```python
# For rule {{1,2,3},{2,4,5}} → {{5,6,1},{6,4,2},{4,5,3}}
# Track vertex mapping: 1→5→..., 2→6→..., 3→1→...
# Define E+ preserves mapping, E- reverses
```

---

*Focus: Close QM via alternative path OR clearly demarcate limitation*
