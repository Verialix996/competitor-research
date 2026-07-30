# Data Integrity and Canonical Build

## Source of truth

The canonical competitor source remains:

`data/competitive-research-tracker.csv`

The historical `bizmatch-competitive-research-cited.*` files are retained in
`archive/data/` for audit only. Production/build code must never read them.

Phase 1 substitute research is deliberately isolated in one normalized
canonical layer:

- `data/substitutes-research.csv` — substitute entities and representative
  evidence links.
- `data/substitute-evidence.csv` — one material claim per evidence row.
- `data/substitute-workflows.csv` — one row per Job and stage.

The first file is the entity entry point; the other two are canonical child
tables linked by `substitute_id`, `evidence_id`, and `job_id`. They are not
fallback copies of one another. No code selects among them by availability or
filename.

## Canonical flow

```text
data/competitive-research-tracker.csv
  -> tools/validate_data.py (pre-build validation)
  -> tools/build_xlsx.py
  -> data/competitive-research-tracker.xlsx
  -> tools/generate_site.py
  -> website / company cards / citation pages / archived report notices
  -> tools/validate_data.py (post-build validation)
```

```text
data/substitutes-research.csv
  + data/substitute-evidence.csv
  + data/substitute-workflows.csv
  -> tools/validate_data.py (schema, ID, URL, evidence, and reference validation)
  -> tools/build_substitute_reports.py
  -> SUBSTITUTE_MATRIX.md / SUBSTITUTE_WORKFLOWS.md /
     SUBSTITUTE_EVIDENCE_REGISTER.md
  -> tools/generate_site.py
  -> sites/full-report-site/alternative-workflows.html /
     sites/full-report-site/substitutes-data.js
  -> tools/validate_data.py (post-build and deterministic validation)
```

`tools/generate_site.py` is read-only with respect to the canonical CSV. Derived
files must not be hand-edited to synchronize facts. Before writing company
profiles, the generator removes every `.html` file in the generated company
directory whose filename is not one of the canonical company slugs.

## Validation rules

- Exactly 36 data rows and 65 unique headers.
- `company` is the canonical identifier: it must be non-empty and unique.
- Generated slugs must also be unique.
- The generated company-profile directory must contain exactly one HTML file
  for each canonical slug and no aliases, stale pages, or extra files.
- CSV and XLSX headers, company order, and normalized values must match.
- XLSX package timestamps and core `created`/`modified` metadata are fixed by
  the generator; time-separated builds must be byte-for-byte identical.
- Source fields may contain only structurally valid `http`/`https` URLs.
- Reconciled fields require a stored source URL or explicit
  `Unresolved`/`Insufficient Evidence` wording.
- Active Python/JavaScript must not read archived cited datasets.
- Legacy score columns may remain only as audit history and must not feed active
  site data, rankings, or conclusions.
- Missing score inputs return `null` / `Insufficient Evidence`; they never
  receive zero, an average, or a guessed default.
- Repeated builds separated by more than two seconds must be deterministic, and
  a build must not alter already-current generated artifacts.
- Investor-facing pages must not publish the historical beachhead, launch
  sequence, White Space, MVP, or Build/Buy hypotheses as current conclusions.
  The detailed pre-Phase-0 narrative is isolated in the site Archive.
- Substitute entity, evidence, and workflow schemas and column order must match
  the documented canonical schemas.
- Substitute IDs, evidence IDs, and workflow IDs must be non-empty and unique.
- Substitute names must remain unique after punctuation and case normalization.
- Every substitute must have an allowed classification and at least one of the
  four documented Jobs.
- Every evidence claim must have a structurally valid source URL and evidence
  type, or be explicitly `Unverified`.
- Every Job must contain the eleven workflow stages exactly once.
- Cross-table IDs must resolve; orphan substitute, evidence, Job, or existing
  competitor references fail validation.
- Existing companies must use `existing_competitor_slug` and are not appended
  to the 36-company tracker.
- Substitute strength is qualitative. The schema contains no numeric score.
- `Company Claim`, `Company Documentation`, `Inference`, and `Unverified` must
  remain visibly labeled in generated output and cannot be rendered as
  independent proof.
- Missing substitute evidence is not assigned a default value or numeric zero.

## Missing values

Use an empty value when no researched statement exists. Use `Insufficient
Evidence` when an archived or disputed assertion exists but cannot be verified.
Use `Unresolved` when traceable sources conflict.

`Not found` means the research did not find evidence; it is not proof of
non-existence. It must not be converted to a numeric weakness.

## Evidence types

- **Primary Source**: official product, legal, documentation, filing, or company
  page. A metric on a company page is still a **Company Claim** unless
  independently corroborated.
- **Company Claim**: first-party usage, traction, funding-facilitated, or
  performance statement. It establishes that the company makes the claim, not
  that the metric is independently verified.
- **Secondary Source**: database, press, review, or platform profile.
- **Regulatory/Filing Evidence**: a filing or filing aggregation; the filing
  amount may not equal total company funding.
- **Inaccessible Source**: a stored URL that could not be opened. It can explain
  an archived value but cannot newly verify it.

Phase 1 uses the more granular evidence types required by the substitute
research:

- **Independent Behavioral Evidence**: observed or experimental behavior.
- **Independent User Report**: independent qualitative user research.
- **Independent Market Evidence**: independent market, survey, or research
  evidence that is not necessarily behavioral.
- **Company Documentation**: first-party product or process capability.
- **Company Claim**: first-party metric, outcome, or performance assertion.
- **Community Discussion**: self-selected discussion; useful for workflow
  discovery but not prevalence.
- **Anecdotal Evidence**: a traceable individual example.
- **Inference**: analyst interpretation that is not a fact.
- **Unverified**: required hypothesis or alternative without defensible support.

Evidence dimensions are also separate: existence, use, effectiveness,
satisfaction, demand for an alternative, and willingness to pay or switch.
One dimension must never be silently substituted for another.

## Confidence

- **High**: directly supported by an accessible primary source with clear entity
  match.
- **Medium**: plausible and traceable, but based on a company claim, secondary
  profile, or limited conflict.
- **Low**: inaccessible source, entity ambiguity, conflicting totals, or no
  independent corroboration.
- **Insufficient Evidence**: no defensible factual or numeric conclusion.

Technical reconciliation dates are separate from `last_checked`. A row’s
research date is not advanced merely because files were synchronized.

For Phase 1, `last_verified` records when the stored source was opened. It does
not mean the described behavior is current for every target user. Generated
files carry no independent verification date and must not be edited manually.

## Adding a substitute or evidence record

1. Check normalized names and the 36-company tracker before creating an entity.
2. If the company already exists, link its canonical slug in
   `existing_competitor_slug`.
3. Add one entity row with qualitative strength and explicit uncertainty.
4. Add separate evidence rows for distinct material claims; do not hide
   multiple facts behind one unsupported narrative cell.
5. Link the evidence IDs from the entity and relevant workflow stages.
6. Use `Unverified` instead of inventing a source, outcome, adoption level,
   price, or score.
7. Run `python3 tools/build_all.py` and
   `python3 tools/validate_data.py --check-build`.
