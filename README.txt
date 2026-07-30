BizMatch Competitive Research — Phase 0 integrity + Phase 1 substitutes

Canonical sources are separated by research scope:
  data/competitive-research-tracker.csv
  data/substitutes-research.csv
  data/substitute-evidence.csv
  data/substitute-workflows.csv

Competitor build flow:
  CSV -> validation -> XLSX -> website/reports/cards -> validation

Substitute build flow:
  substitute entities + evidence + workflows -> validation
  -> generated matrix/workflow/evidence reports -> website -> validation

Run:
  python3 tools/build_all.py

Run the deterministic two-build check:
  python3 tools/validate_data.py --check-build

Important boundaries:
- data/competitive-research-tracker.xlsx is generated; do not edit it manually.
- The three substitute CSVs are the canonical normalized Phase 1 layer and are
  edited manually with evidence IDs kept referentially valid.
- SUBSTITUTE_MATRIX.md, SUBSTITUTE_WORKFLOWS.md,
  SUBSTITUTE_EVIDENCE_REGISTER.md, and the Alternative Workflows site page are
  generated; do not edit them manually.
- Substitute records never enter the 36-company tracker. Existing companies are
  linked through existing_competitor_slug.
- archive/data/bizmatch-competitive-research-cited.* is historical audit material.
- archive/legacy-scoring/ contains deprecated ranker code.
- Legacy score columns remain in the CSV only for audit and do not feed the site.
- relationship_score is null / Insufficient Evidence until explicit sourced inputs exist.
- The active landing page publishes evidence status, not strategic recommendations.
- Historical strategic hypotheses are isolated under the site Archive; Phase 0 did not
  re-run White Space, MVP, Mystery Shopping, launch-sequence, or Build/Buy research.
- The generator removes stale/non-canonical company-profile HTML files.
- XLSX generation normalizes both ZIP entry timestamps and Office core metadata.
- Phase 1 uses qualitative substitute strength only. It creates no numeric
  threat, opportunity, relationship, readiness, or product-priority score.
- Company Documentation and Company Claim remain visibly labeled and are not
  promoted to independent behavioral evidence.

Documentation:
- DATA_INTEGRITY.md
- RECONCILIATION_REPORT.md
- SCORING_METHODOLOGY.md
- EXCLUSION_LOG.md
- SUBSTITUTE_RESEARCH.md
- SUBSTITUTE_MATRIX.md (generated)
- SUBSTITUTE_WORKFLOWS.md (generated)
- SUBSTITUTE_EVIDENCE_REGISTER.md (generated)

Open index.html after a successful build.
