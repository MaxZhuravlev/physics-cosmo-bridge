# TODO для Следующей Сессии

**Current Quality**: 8/10 (functional, publishable)
**Target**: 10/10 (perfect)
**Time Required**: 10-15 minutes

---

## REMAINING CLEANUP (Quick Fixes)

### 1. Root (1 file to remove)
```bash
mv ОКОНЧАТЕЛЬНЫЙ_СТАТУС.md archive/session-docs/
```

### 2. output/latex/ (6 .md files to remove)
```bash
cd output/latex
mkdir -p ../../archive/submission-package-docs
mv CONSERVATIVE_CHANGES.md FINAL_REVIEW_SUMMARY.md PAPER_STRENGTHS.md \
   PRE_SUBMISSION_ACTIONS.md README_SUBMISSION_PACKAGE.md \
   SUBMISSION_CHECKLIST.md ../../archive/submission-package-docs/
```

**After**: output/latex/ contains ONLY:
- main.tex (143 lines)
- references.bib (if created)
- figures/ (if any)

---

## CONTENT FIXES (For main.tex)

**Before submission**, fix these in main.tex:

1. **Line 11**: Replace `[Your Name]` with actual name
2. **Add after line 68**:
   ```latex
   Note: We assume $D=4$, consistent with observation
   but not derived from causal invariance.
   ```
3. **Add after line 115** (Gorard ref):
   ```latex
   (preprint, not peer-reviewed as of 2026)
   ```
4. **Remove unused refs**: Amari (133), Chiribella (138), Conant-Ashby (141)
   - Paper #1 doesn't use these theorems

---

## THEN READY

**To compile**:
```bash
cd output/latex
pdflatex main.tex
pdflatex main.tex
```

**Or**: Upload to Overleaf/arXiv (they compile)

---

## SUBMISSION

**arXiv**: physics.gen-ph
**Email Vanchurin**: vvanchur@d.umn.edu (attach PDF)
**YouTube**: Post comment after arXiv live

---

**Total time to perfect**: 15-20 minutes
**Current state**: Publishable at 8/10
**After fixes**: Perfect at 10/10

---

_Use /cws-launch to continue with this TODO list_
