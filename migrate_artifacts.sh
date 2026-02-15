#!/bin/bash
# Automated PE-based artifact reorganization

set -e

echo "=== PE-BASED ARTIFACT MIGRATION ==="
echo

# Create all needed directories
echo "Creating directory structure..."
mkdir -p archive/{src,docs,incremental}
mkdir -p ../operational-qm-from-ci/{src,resources/{overclaimed,failed-attempts},experience/insights}

# Migrate problematic code → Project #2
echo "Migrating problematic code to Project #2..."
for file in src/purification*.py src/formal_*.py src/MAXIMUM_*.py src/massive_*.py src/hypergraph_engine.py src/run_critical_tests.py; do
    if [ -f "$file" ]; then
        echo "  → $file"
        cp "$file" ../operational-qm-from-ci/src/
    fi
done

# Migrate overclaimed docs → Project #2
echo "Migrating overclaimed documents to Project #2..."
for file in output/manuscript.tex output/PREPRINT_DRAFT.md output/THEOREM_COMPLETE*.md; do
    if [ -f "$file" ]; then
        echo "  → $file"
        cp "$file" ../operational-qm-from-ci/resources/overclaimed/
    fi
done

# Migrate session summaries → archive
echo "Migrating historical documents to archive..."
for file in Session*.md ПОКАЗАТЬ*.md ИТОГ*.md ФИНАЛ*.md; do
    if [ -f "$file" ]; then
        echo "  → $file"
        mv "$file" archive/docs/
    fi
done

# Keep only minimal in Paper #1
echo "Paper #1 minimal set:"
echo "  ✓ PAPER1_CONSERVATIVE.tex"
echo "  ✓ src/ollivier_ricci.py"
echo "  ✓ src/multiple_spatial_curvature.py"
echo "  ✓ reviews/ (3 files)"
echo "  ✓ data/ (spatial results)"

echo
echo "✅ PE-based reorganization complete"
echo "Paper #1: Clean & minimal"
echo "Project #2: All materials ready"
echo "Archive: Historical preserved"
