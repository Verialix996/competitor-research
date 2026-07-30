Generated site. Do not hand-edit generated HTML or data files.

Source:
  ../../data/competitive-research-tracker.csv
  ../../data/substitutes-research.csv
  ../../data/substitute-evidence.csv
  ../../data/substitute-workflows.csv
  ../../data/market-research.json
  ../../data/findings-and-implications.json

Build:
  python3 tools/build_all.py

Numeric rankings are disabled until explicit sourced relationship-score inputs exist.
Legacy ranker code is retained only under ../../archive/legacy-scoring/.
The company-profile directory is a generated exact manifest: stale aliases are
removed on build. Historical strategic recommendations are available only
through Archive and are not presented on the active Evidence Status page.
The top-level /market-research/ route is generated from aggregate,
non-identifying content and remains separate from competitor and substitute
research.
The top-level /findings-conclusions/ route and
../../FINDINGS_AND_STRATEGIC_IMPLICATIONS.md are generated from the structured
active-conclusions source. They preserve evidence links and publish conditional
implications only.
