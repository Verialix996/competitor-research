BizMatch Research — Phase 0 integrity + Phase 1 substitutes + active conclusions

Canonical sources are separated by research scope:
  data/competitive-research-tracker.csv
  data/substitutes-research.csv
  data/substitute-evidence.csv
  data/substitute-workflows.csv
  data/market-research.json
  data/findings-and-implications.json

Competitor build flow:
  CSV -> validation -> XLSX -> website/reports/cards -> validation

Substitute build flow:
  substitute entities + evidence + workflows -> validation
  -> generated matrix/workflow/evidence reports -> website -> validation

Market-research build flow:
  aggregate, non-identifying market-research content -> validation
  -> /market-research/ -> validation

Active-conclusions build flow:
  evidence-linked findings and conditional implications -> validation
  -> FINDINGS_AND_STRATEGIC_IMPLICATIONS.md
  -> /, /findings-conclusions/, and /presentation/ -> validation

Presentation architecture:
  Overview -> Findings -> Market Research -> Competitive Landscape
  -> How Users Solve It Today -> Evidence -> Methodology -> Presentation -> Archive

The overview and executive brief do not maintain separate research claims.
`tools/presentation_views.py` resolves human-readable competitor, substitute,
Job, and evidence labels from the canonical sources at generation time. Missing
references fail validation instead of falling back to raw IDs or slugs.

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
- data/findings-and-implications.json is the manually maintained active
  conclusions source. Every material item must resolve to evidence IDs,
  aggregate market-research paths, or an explicit Insufficient Evidence status.
- FINDINGS_AND_STRATEGIC_IMPLICATIONS.md and
  findings-conclusions/index.html are generated; do not edit them manually.
- index.html, presentation/index.html, the workflow explorer, competitive
  landscape, evidence library, and company profiles are generated presentation
  views; do not edit them manually.
- sites/full-report-site/site-ui.js contains only filtering, presentation
  navigation, and URL-state behavior. It contains no research dataset.
- Substitute records never enter the 36-company tracker. Existing companies are
  linked through existing_competitor_slug.
- archive/data/bizmatch-competitive-research-cited.* is historical audit material.
- archive/legacy-scoring/ contains deprecated ranker code.
- Legacy score columns remain in the CSV only for audit and do not feed the site.
- relationship_score is null / Insufficient Evidence until explicit sourced inputs exist.
- Active conclusions are evidence-linked and conditional. The site publishes
  no final product, market, MVP, Build/Buy, White Space, or PMF recommendation.
- Historical strategic hypotheses are isolated under the site Archive; Phase 0 did not
  re-run White Space, MVP, Mystery Shopping, launch-sequence, or Build/Buy research.
- The generator removes stale/non-canonical company-profile HTML files.
- XLSX generation normalizes both ZIP entry timestamps and Office core metadata.
- Phase 1 uses qualitative substitute strength only. It creates no numeric
  threat, opportunity, relationship, readiness, or product-priority score.
- Company Documentation and Company Claim remain visibly labeled and are not
  promoted to independent behavioral evidence.
- data/market-research.json is the single public content source for the
  generated Market Research route. It contains aggregate findings only; private
  recordings, transcripts, names, contact details, and raw interview files must
  never be copied into the public build.
- market-research/index.html is generated; do not edit it manually.

Documentation:
- DATA_INTEGRITY.md
- RECONCILIATION_REPORT.md
- SCORING_METHODOLOGY.md
- EXCLUSION_LOG.md
- SUBSTITUTE_RESEARCH.md
- SUBSTITUTE_MATRIX.md (generated)
- SUBSTITUTE_WORKFLOWS.md (generated)
- SUBSTITUTE_EVIDENCE_REGISTER.md (generated)
- FINDINGS_AND_STRATEGIC_IMPLICATIONS.md (generated)

Open index.html after a successful build.
