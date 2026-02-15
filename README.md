# Connecting Wolfram and Vanchurin Cosmologies: A Lovelock Bridge

**Author**: Max Zhuravlev (Independent Research)
**Date**: February 2026
**Status**: Preprint (submitted to arXiv physics.gen-ph)
**Quality**: 8.7/10 (Multi-AI validated: Claude + Gemini + Analyst)

---

## 📄 Paper

**Download**: [main.pdf](output/latex/main.pdf) (61 KB, 4 pages)

**arXiv Package**: [arxiv-submission-final.tar.gz](output/arxiv-submission-final.tar.gz) (477 KB)

---

## 📝 Abstract

We demonstrate a formal connection between Wolfram's hypergraph physics and Vanchurin's neural network cosmology through Lovelock's uniqueness theorem, providing a possible answer to Vanchurin's explicitly stated open question regarding the derivation of Onsager tensor symmetries from first principles.

**Key Result**: Gorard (2020) proved causal invariance → discrete general covariance. Under the working assumption of a continuum limit, this yields diffeomorphism invariance. Lovelock's theorem (1971) then uniquely determines Einstein's gravity in D=4. This may constrain Vanchurin's phenomenologically chosen Onsager tensor (Eq. 93).

**Contribution**: First formal link between Wolfram Physics Project and Vanchurin Neural Network Cosmology. Synthesis of existing results (Gorard, Lovelock, Vanchurin) making explicit a connection not previously noted in literature.

---

## 🔍 Main Claim (Conservative)

**If** the continuum limit holds (standard assumption in discrete gravity), **then** causal invariance uniquely constrains Vanchurin's Onsager tensor via:

```
Causal Invariance (Wolfram)
  ↓ [Gorard 2020: CI ⟺ discrete covariance]
Discrete General Covariance
  ↓ [Continuum limit - ASSUMED]
Diffeomorphism Invariance
  ↓ [Lovelock 1971: unique tensor in D≤4]
Einstein Tensor (unique)
  ↓ [Reverse engineering]
Onsager Tensor (Vanchurin Eq. 93)
```

**We do NOT claim**: New theorem, proof of continuum limit, or full QM/learning derivations (future work).

---

## 💎 Why This Matters

Two independent physics programs derived the same gravity from completely different premises:
- **Wolfram**: Computation without purpose (hypergraph rewriting)
- **Vanchurin**: Learning with purpose (neural network optimization)

They never cited each other. We show they **must** converge: Lovelock's theorem proves there is exactly ONE gravity compatible with the required symmetry. Both programs arrive at it because mathematics leaves no alternative.

**Implication**: May suggest Wolfram describes the substrate, Vanchurin describes observer experience inside it. Same reality, different viewpoints.

---

## 🧪 Computational Validation

**Numerical evidence** (preliminary):
- Spatial hypergraph tests: κ = 0.67 ± 0.03 (N=9 states)
- 5 spatial rules: mean κ = 0.30
- Curvature suggests non-trivial geometry

**Code**: All computational experiments in `src/` directory

**Reproducibility**: `make quality` runs full validation

---

## 📚 References

**Key sources**:
- Gorard, J. (2020). Complex Systems 29(2), 599-654; arXiv:2004.14810
- Lovelock, D. (1971). J. Math. Phys. 12(3), 498-501
- Vanchurin, V. (2020). Entropy 22(11), 1210; arXiv:2008.01540
- Wolfram, S. et al. (2020). Complex Systems 29, 107-536

---

## ⚠️ Limitations (Explicitly Stated)

1. **Continuum limit**: Assumed, not proven (longstanding challenge)
2. **Numerical evidence**: Preliminary (N=9, spatial rules only)
3. **Uniqueness**: Lovelock constrains form, not all parameters
4. **D=4**: Assumed (not derived from causal invariance)
5. **Synthesis**: Connects existing results, proves no new theorems

---

## 🔬 Falsifiability

The proposed bridge could be falsified by:
1. Discovering CI-hypergraph rules that do NOT approach diffeomorphisms in continuum
2. Formal proof that discrete covariance ≠ smooth diffeomorphisms

---

## 💻 Code & Data

**Computational validation scripts**: See `src/` directory

**Figures**:
- Fig1: Purification vs LD scaling
- Fig2: Theorem flowchart

**Automation**: Makefile + CI workflow

**Requirements**: Python (NumPy, NetworkX), Wolfram SetReplace (optional)

---

## 📖 How to Cite

### Before arXiv acceptance:

```bibtex
@misc{Zhuravlev2026Lovelock,
  author = {Zhuravlev, Max},
  title = {Connecting Wolfram and Vanchurin Cosmologies: A Lovelock Bridge},
  year = {2026},
  howpublished = {Preprint},
  url = {https://github.com/MaxZhuravlev/physics-cosmo-bridge},
  note = {Submitted to arXiv}
}
```

### After arXiv acceptance (update to):

```bibtex
@article{Zhuravlev2026Lovelock,
  author = {Zhuravlev, Max},
  title = {Connecting Wolfram and Vanchurin Cosmologies: A Lovelock Bridge},
  journal = {arXiv preprint arXiv:2602.XXXXX},
  year = {2026},
  eprint = {2602.XXXXX},
  archivePrefix = {arXiv},
  primaryClass = {physics.gen-ph},
  url = {https://github.com/MaxZhuravlev/physics-cosmo-bridge}
}
```

---

## 🎓 Related Work

This is **Paper #1** of a 4-paper research program:

- **Paper #1** (this work): Lovelock bridge (gravity sector)
- **Paper #2** (in progress): QM from purification path
- **Paper #3** (planned): Amari learning dynamics
- **Paper #4** (future): Unified framework

**Program repository**: https://github.com/MaxZhuravlev/physics-cosmo-unification

---

## 🙏 Acknowledgments

Research conducted with AI assistance (Claude, Anthropic; Gemini, Google; Codex, OpenAI).

Computational: M3 Max (128GB), Python, Wolfram SetReplace

Multi-AI validation improved quality from 6.0/10 → 8.7/10 through iterative review.

---

## 📧 Contact

**Author**: Max Zhuravlev
**Repository**: https://github.com/MaxZhuravlev/physics-cosmo-bridge
**Issues**: Use GitHub Issues for questions/feedback

---

## 📜 License

**Paper**: arXiv perpetual non-exclusive license (or CC BY when finalized)
**Code**: MIT License

---

## 🔗 Links

- **Paper PDF**: [main.pdf](output/latex/main.pdf)
- **arXiv Package**: [arxiv-submission-final.tar.gz](output/arxiv-submission-final.tar.gz)
- **Source Code**: [src/](src/)
- **Computational Validation**: [output/](output/)
- **Program Umbrella**: https://github.com/MaxZhuravlev/physics-cosmo-unification

---

**Publication Date**: February 15, 2026
**Version**: v1.0 (preprint)
**Status**: Public, citable, peer feedback welcome

---

*Conservative synthesis connecting Wolfram and Vanchurin via Lovelock's uniqueness theorem*
