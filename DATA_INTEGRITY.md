# Data Integrity and Canonical Build

## Source of truth

The only active research source is:

`data/competitive-research-tracker.csv`

The historical `bizmatch-competitive-research-cited.*` files are retained in
`archive/data/` for audit only. Production/build code must never read them.

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
