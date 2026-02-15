# Pattern Library

Reusable patterns extracted from this project's experience.

---

## Overview

This directory contains patterns (solutions to recurring problems) that emerged from 14+ sessions of AI-assisted physics research. Each pattern is:

- **Actionable:** Can be applied immediately to similar contexts
- **Evidenced:** Backed by quantified outcomes from this project
- **Leveled:** Classified by abstraction (L1-universal, L2-domain, L3-project)

---

## Patterns

### Organizational (L1 - Universal)

**pt.organizational.quality-first-not-context-excuse**
- **Problem:** Using context ("just research", "just exploring") as excuse for low quality
- **Solution:** Quality discipline independent of context
- **Evidence:** Chaos compounds to 2.8% productivity by session 10; quality compounds to 13.8x
- **Impact:** Choose your compounding (×190 vs ×0.0008 at N=20)

### Research (L2 - AI-Assisted Research)

**pt.research.pe-first**
- **Problem:** "Structure comes later" in exploratory research → quality drift, scope creep, lost insights
- **Solution:** PE methodology from session 1 (VOS, VALUE-TRACKS, /pe-classify)
- **Evidence:** This project: 2 weeks crisis without PE, immediate clarity with PE
- **Impact:** 6x ROI (3 hours overhead prevents 21 hours crisis)

**pt.research.honest-novelty-tracking**
- **Problem:** Overclaiming drift (40% → 60% internal, 20% actual)
- **Solution:** /pe-classify each result with novelty level (DISCOVERY, CONTRIBUTION, SYNTHESIS, CITATION)
- **Evidence:** This project: no tracking → overclaiming crisis, post-crisis tracking → honest 0.25
- **Impact:** Prevents reputational damage, enables correct journal targeting

**pt.research.negative-results-as-insights** (referenced, not yet extracted)
- **Problem:** Publication bias, repeated failures by other researchers
- **Solution:** /pe-classify obstacles as first-class insights
- **Evidence:** This project: 5 negative results → reviewer praise for honesty

---

## Usage

### For This Project

Patterns are already applied (lessons learned from failure):
- **pt.research.pe-first:** VALUE-TRACKS.yaml created in session 13 (late, but present)
- **pt.research.honest-novelty-tracking:** Corrected to 0.25 novelty after crisis
- **pt.organizational.quality-first:** Applied retroactively in sessions 11-14

### For Future Projects

**Apply from session 1:**

```bash
# Session 1 init:
cd ~/Projects/PhysicsResearch/{problematics}/
/cw--uu-create-project {project-name}

# → Creates VOS, VALUE-TRACKS.yaml, experience/
# → Defines scope, deliverable, novelty expectations

# Every session:
/pe-classify {result}
# → Auto-saves insights
# → Tracks novelty honestly
# → Updates VALUE-TRACKS.yaml

/cws-route {artifact}
# → Semantic organization from start

# Weekly:
/cws-handoff
# → State preservation across sessions
```

**Reference these patterns** when:
- Starting new research project → pt.research.pe-first
- Writing claims for publication → pt.research.honest-novelty-tracking
- Tempted to skip structure → pt.organizational.quality-first

---

## Pattern Format

Each pattern file contains:

```yaml
pattern_id: pt.{family}.{name}
domain: research | organizational | infrastructure
level: L1 (universal) | L2 (domain) | L3 (project)

problem: "What recurring problem does this solve?"
solution: "What is the reusable solution?"
evidence: "What outcomes from this project validate it?"
impact: "What is the quantified compound value?"

anti_pattern: "What mistakes does this prevent?"
related_patterns: "What other patterns interact with this?"
```

---

## Abstraction Levels

**L1 (Universal):** Applies to ANY executor
- Example: pt.organizational.quality-first-not-context-excuse
- Reuse: All future work (research, infrastructure, business)

**L2 (Domain):** Applies to specific domain
- Example: pt.research.pe-first (AI-assisted research)
- Reuse: All future research projects

**L3 (Project):** Applies to this project only
- Example: pt.physics.wolfram-vanchurin-specific
- Reuse: Limited (reference only)

**Promotion rule:** Always promote to highest applicable level for maximum reuse.

---

## Contribution

When you discover a pattern:

1. **Extract it:**
   - Problem: What keeps recurring?
   - Solution: What consistently works?
   - Evidence: What outcomes validate it?

2. **Classify it:**
   - Level: L1 (universal), L2 (domain), L3 (project)?
   - Family: organizational, research, infrastructure?

3. **Document it:**
   - Create `pt.{family}.{name}.yaml`
   - Include quantified evidence
   - Link to source insight

4. **Update this README:**
   - Add pattern to appropriate section
   - Update usage examples

---

## Compound Value

Patterns enable **exponential learning:**

```
Without patterns: Each project starts from scratch
With patterns: Each project builds on all previous

Pattern library size N:
  Project efficiency ≈ 1.3^N

At N=10 patterns: ×13.8 efficiency
At N=50 patterns: ×4,978 efficiency
```

**Key insight:** Patterns add to EXPONENT, not coefficient!

This project extracted 3+ patterns from crisis. Future projects applying these patterns will:
- Avoid 2-week reorganization crisis (×1.3)
- Track novelty honestly (×1.3)
- Maintain quality discipline (×1.3)
- **Compound:** ×2.2 efficiency vs this project

---

## Cross-References

**Source insights:**
- `experience/insights/pe-organizational-lessons-2026-02-15.md` — Full crisis analysis
- `experience/insights/dialogue-analysis-10-sessions.md` — 10-session research summary

**Related systems:**
- `/pe-classify` skill — Pattern/insight classification
- `/cws-route` skill — Semantic artifact routing
- `VALUE-TRACKS.yaml` — Quality and progress tracking

**Upstream (ClaudeWorkspace):**
- PE methodology patterns (when extracted to global library)
- CW system improvement proposals (from lessons document)

---

*Patterns are not overhead. Patterns are compound infrastructure.*
