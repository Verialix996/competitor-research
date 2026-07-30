BizMatch Competitive Research — Phase 0

Canonical source of truth:
  data/competitive-research-tracker.csv

Canonical build flow:
  CSV -> validation -> XLSX -> website/reports/cards -> validation

Run:
  python3 tools/build_all.py

Run the deterministic two-build check:
  python3 tools/validate_data.py --check-build

Important boundaries:
- data/competitive-research-tracker.xlsx is generated; do not edit it manually.
- archive/data/bizmatch-competitive-research-cited.* is historical audit material.
- archive/legacy-scoring/ contains deprecated ranker code.
- Legacy score columns remain in the CSV only for audit and do not feed the site.
- relationship_score is null / Insufficient Evidence until explicit sourced inputs exist.
- The active landing page publishes evidence status, not strategic recommendations.
- Historical strategic hypotheses are isolated under the site Archive; Phase 0 did not
  re-run White Space, MVP, Mystery Shopping, launch-sequence, or Build/Buy research.
- The generator removes stale/non-canonical company-profile HTML files.
- XLSX generation normalizes both ZIP entry timestamps and Office core metadata.

Documentation:
- DATA_INTEGRITY.md
- RECONCILIATION_REPORT.md
- SCORING_METHODOLOGY.md
- EXCLUSION_LOG.md

Open index.html after a successful build.
