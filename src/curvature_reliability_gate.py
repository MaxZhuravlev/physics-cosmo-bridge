#!/usr/bin/env python3
"""Curvature reliability gate for Paper #1.

This gate enforces three properties:
1) Quantitative robustness on a fixed multi-pattern test set.
2) Heuristic 1D-like control sanity check.
3) Claim-hygiene in live project files (no known overclaim phrases).

The output is written to output/curvature_reliability_report.json.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Dict, List, Sequence, Tuple

import numpy as np

from multiple_spatial_curvature import (
    compute_ollivier_ricci_curvature,
    create_2d_triangle_mesh,
    create_hexagonal_mesh,
    create_square_grid,
    create_tetrahedral_3d,
    hypergraph_to_causal_graph,
)
from ollivier_ricci import test_ricci_on_string_systems


ROOT_DIR = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT_DIR / "output" / "curvature_reliability_report.json"

ALPHAS: Sequence[float] = (0.25, 0.50, 0.75)

PatternFactory = Callable[[int], List[Tuple[int, ...]]]
PATTERNS: Sequence[Tuple[str, PatternFactory, int]] = (
    ("Triangle Mesh 2D", create_2d_triangle_mesh, 3),
    ("Square Grid 2D", create_square_grid, 3),
    ("Hexagonal Mesh", create_hexagonal_mesh, 2),
    ("Triangle Mesh 2D (large)", create_2d_triangle_mesh, 4),
    ("Tetrahedral 3D", create_tetrahedral_3d, 2),
)

# Keep this list narrow to avoid false positives on legitimate disclaimers.
BANNED_OVERCLAIM_PATTERNS: Sequence[str] = (
    r"EMPIRICALLY\s+CONFIRMED",
    r"all\s+theorems\s+become\s+UNCONDITIONAL",
    r"Main\s+claim\s+already\s+decisive",
    r"ENTIRE\s+known\s+physics",
    r"CONTINUAL\s+LIMIT:\s+Empirically\s+supported",
)

LIVE_FILES: Sequence[Path] = (
    ROOT_DIR / "CLAUDE.md",
    ROOT_DIR / "README.md",
    ROOT_DIR / "VALUE-TRACKS.yaml",
    ROOT_DIR / "output" / "latex" / "main.tex",
    ROOT_DIR / "src" / "multiple_spatial_curvature.py",
    ROOT_DIR / "src" / "ollivier_ricci.py",
    ROOT_DIR / "src" / "SPATIAL_CRITICAL_TEST.wl",
    ROOT_DIR / "scripts" / "run_full_quality.sh",
    ROOT_DIR / "vos" / "value-transformation.md",
    ROOT_DIR / "vos" / "scope-boundaries.md",
    ROOT_DIR / "vos" / "integration-contract.md",
)

BASE_ALPHA = 0.5
MIN_SIGNIFICANT_AT_BASE_ALPHA = 3
MIN_NONWEAK_PER_ALPHA = 4
MIN_OVERALL_MEAN = 0.05
MAX_ABS_1D_CONTROL_MEAN = 0.05


@dataclass
class PatternMetric:
    name: str
    size: int
    mean_kappa: float
    std_kappa: float
    nonzero_fraction: float
    status: str


@dataclass
class AlphaSummary:
    alpha: float
    tested_patterns: int
    significant_count: int
    overall_mean_kappa: float
    overall_std_kappa: float
    patterns: List[PatternMetric]


def classify_mean_kappa(value: float) -> str:
    if value > 0.1:
        return "significant"
    if value > 0.01:
        return "moderate"
    return "weak"


def run_alpha_sweep() -> List[AlphaSummary]:
    summaries: List[AlphaSummary] = []

    for alpha in ALPHAS:
        pattern_metrics: List[PatternMetric] = []

        for name, factory, size in PATTERNS:
            hyperedges = factory(size)
            graph = hypergraph_to_causal_graph(hyperedges)
            curvatures = compute_ollivier_ricci_curvature(graph, sample_size=100, alpha=alpha)
            if not curvatures:
                continue

            mean_kappa = float(np.mean(curvatures))
            std_kappa = float(np.std(curvatures))
            nonzero_fraction = float(np.mean(np.abs(curvatures) > 1e-6))
            pattern_metrics.append(
                PatternMetric(
                    name=name,
                    size=size,
                    mean_kappa=mean_kappa,
                    std_kappa=std_kappa,
                    nonzero_fraction=nonzero_fraction,
                    status=classify_mean_kappa(mean_kappa),
                )
            )

        if not pattern_metrics:
            summaries.append(
                AlphaSummary(
                    alpha=float(alpha),
                    tested_patterns=0,
                    significant_count=0,
                    overall_mean_kappa=float("nan"),
                    overall_std_kappa=float("nan"),
                    patterns=[],
                )
            )
            continue

        means = np.array([metric.mean_kappa for metric in pattern_metrics], dtype=float)
        significant_count = sum(metric.status == "significant" for metric in pattern_metrics)
        summaries.append(
            AlphaSummary(
                alpha=float(alpha),
                tested_patterns=len(pattern_metrics),
                significant_count=significant_count,
                overall_mean_kappa=float(np.mean(means)),
                overall_std_kappa=float(np.std(means)),
                patterns=pattern_metrics,
            )
        )

    return summaries


def scan_claim_hygiene() -> List[Dict[str, object]]:
    hits: List[Dict[str, object]] = []

    for path in LIVE_FILES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()
        for pattern in BANNED_OVERCLAIM_PATTERNS:
            regex = re.compile(pattern, re.IGNORECASE)
            for idx, line in enumerate(lines, start=1):
                if regex.search(line):
                    hits.append(
                        {
                            "file": str(path.relative_to(ROOT_DIR)),
                            "line": idx,
                            "pattern": pattern,
                            "text": line.strip(),
                        }
                    )
    return hits


def evaluate_gate(alpha_summaries: Sequence[AlphaSummary], control_stats: Dict[str, float], claim_hits: Sequence[Dict[str, object]]) -> Tuple[bool, List[str]]:
    failures: List[str] = []

    if claim_hits:
        failures.append(f"claim_hygiene failed: {len(claim_hits)} banned phrase hit(s)")

    for summary in alpha_summaries:
        if summary.tested_patterns < len(PATTERNS):
            failures.append(
                f"alpha={summary.alpha}: tested_patterns={summary.tested_patterns} < expected={len(PATTERNS)}"
            )
            continue
        nonweak_count = sum(metric.status != "weak" for metric in summary.patterns)
        if nonweak_count < MIN_NONWEAK_PER_ALPHA:
            failures.append(
                f"alpha={summary.alpha}: nonweak_count={nonweak_count} < {MIN_NONWEAK_PER_ALPHA}"
            )
        if summary.overall_mean_kappa < MIN_OVERALL_MEAN:
            failures.append(
                f"alpha={summary.alpha}: overall_mean_kappa={summary.overall_mean_kappa:.4f} < {MIN_OVERALL_MEAN:.2f}"
            )
        if abs(summary.alpha - BASE_ALPHA) < 1e-12 and summary.significant_count < MIN_SIGNIFICANT_AT_BASE_ALPHA:
            failures.append(
                f"alpha={summary.alpha}: significant_count={summary.significant_count} < {MIN_SIGNIFICANT_AT_BASE_ALPHA} at base alpha"
            )

    control_mean = float(control_stats.get("mean", float("nan")))
    if np.isnan(control_mean):
        failures.append("1D-control: mean is NaN")
    elif abs(control_mean) > MAX_ABS_1D_CONTROL_MEAN:
        failures.append(
            f"1D-control: |mean|={abs(control_mean):.4f} > {MAX_ABS_1D_CONTROL_MEAN:.2f}"
        )

    return len(failures) == 0, failures


def main() -> int:
    alpha_summaries = run_alpha_sweep()
    control_stats = test_ricci_on_string_systems()
    control_summary = {
        key: value for key, value in control_stats.items() if key != "values"
    }
    claim_hits = scan_claim_hygiene()
    ok, failures = evaluate_gate(alpha_summaries, control_summary, claim_hits)

    report = {
        "gate": "curvature_reliability",
        "status": "pass" if ok else "fail",
        "thresholds": {
            "alphas": list(ALPHAS),
            "expected_patterns": len(PATTERNS),
            "base_alpha": BASE_ALPHA,
            "min_significant_at_base_alpha": MIN_SIGNIFICANT_AT_BASE_ALPHA,
            "min_nonweak_per_alpha": MIN_NONWEAK_PER_ALPHA,
            "min_overall_mean_kappa": MIN_OVERALL_MEAN,
            "max_abs_1d_control_mean": MAX_ABS_1D_CONTROL_MEAN,
        },
        "alpha_summaries": [
            {
                **asdict(summary),
                "patterns": [asdict(metric) for metric in summary.patterns],
            }
            for summary in alpha_summaries
        ],
        "control_1d": control_summary,
        "claim_hygiene": {
            "banned_patterns": list(BANNED_OVERCLAIM_PATTERNS),
            "hits": list(claim_hits),
        },
        "failures": failures,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print("[reliability] report:", REPORT_PATH)
    print("[reliability] status:", report["status"])
    if failures:
        for item in failures:
            print("[reliability] failure:", item)
        return 1

    print("[reliability] all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
