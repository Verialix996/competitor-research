# BizMatch Competitive Research — Historical Finalization Plan

> **Phase 1 status (2026-07-30):** Substitute research is maintained separately
> in `data/substitutes-research.csv`, `data/substitute-evidence.csv`, and
> `data/substitute-workflows.csv`. See `SUBSTITUTE_RESEARCH.md`; this historical
> Phase 0 plan does not define Phase 1 findings or completion.

> **Phase 0 status (2026-07-30):** This file preserves the pre-reconciliation
> plan and claims for audit. It is not the current source-of-truth description.
> The only active source is `data/competitive-research-tracker.csv`; the cited
> datasets moved to `archive/data/`. The former scoring-complete and four-surface
> sync claims are deprecated because they relied on legacy scores and were not
> protected by reproducible consistency tests. See `RECONCILIATION_REPORT.md`,
> `DATA_INTEGRITY.md`, and `SCORING_METHODOLOGY.md`.

Updated: 2026-07-25

Companion to `kanban.md`. This document captures the exact state of the research
corpus and the work required to consider it **final**. It is resumable: each phase
lists concrete company targets so any session (or Hermes sub-agent) can pick up mid-stream.

Current tracker of record: `data/competitive-research-tracker.csv` (36 companies,
65 columns). Historical tracker referenced below:
`archive/data/bizmatch-competitive-research-cited.csv`.

---

## 1. Current state — what is done

- **36 companies** fully profiled across 5 competitor groups, with cited primary/secondary sources.
- **Historical scoring exists but is deprecated**: the old 1–5 inputs and
  composite score are retained only for audit. Active relationship scores are
  `null` / `Insufficient Evidence`.
- **Registration-flow screenshots captured for all 36** (103 images in
  `sites/full-report-site/assets/registration-flows/`) — but visitor-side only (see Gap A).
- **Published surfaces**: research table (`sites/full-report-site/index.html`), 36 company
  cards, citation site, the ChatGPT competitor ranker (`ranker-chatgpt.html`), and the preserved Claude competitor ranker (`ranker-claude.html`).

## 2. Remaining gaps — what is NOT final

### Gap A — Post-signup field audit — ⏸ DEFERRED (out of scope for now)
Every registration flow currently **stops at the signup form**; documenting post-signup
onboarding was scoped in `status/hermes-signup-audit-prompt.md` with a board in
`signup-audit-kanban.md`. **Deferred by decision (2026-07-25)** — not part of finalizing the
doc now. The scaffold is parked and resumable whenever it's picked back up. The corpus is
treated as final *without* the post-signup audit.

### Gap B — Unverified funding (22 of 36)
`total_funding` = "not found" / paywall-blocked. By category:
- Capital & discovery marketplaces (8/9): AngelList, Gust, Crunchbase, Republic, StartEngine, OpenVC, Signal (NFX), Foundersuite
- AI pitch-deck reviewers (6/8): Evalyze, Peachscore, PitchGrade, PitchBob, PitchLeague, Inodash
- Cofounder-matching platforms (4/6): Foundersbase, Cofounder.org, Tertle, FounderCloud
- Direct competitors (4/6): Comatch, SwipeDeck, Swipe Invest, SWIP
- NDA & deal-room tools: 0/7 — all known ✓

### Gap C — Low-confidence rows (5)
Thinnest evidence base; re-verify or explicitly cap:
- SwipeDeck (Low), SWIP (Low), Swipe Invest (Low-Medium) — all Direct competitors
- Cofounder.org (Low) — Cofounder-matching
- Inodash (Low) — AI pitch-deck reviewers

### Gap D — Flag triage — ✅ DONE (see `phase-b-triage.md`)
Contradictions (32) and unsupported claims (30) triaged: ~20 already-resolved corrections,
~12 cosmetic self-reported metrics (label-only), and **8 material items** routed to Phases A/C/D.
Only **AngelList** has a flag that could move a score (its `ai_depth` rests on an unverified
AI-matching claim). Remaining work is captured in the phase table below.

---

## 3. Plan to finalize

| Phase | Task | Targets | Owner | Priority |
|---|---|---|---|---|
| **A** | Post-signup onboarding audit | ⏸ **DEFERRED** — parked scaffold (`signup-audit-kanban.md`); not part of finalizing now | Human / Hermes | Deferred |
| **B** | Triage contradictions + unsupported claims | ✅ **DONE** — `phase-b-triage.md` (20 resolved, 12 cosmetic, 8 routed) | — | — |
| **C** | Second-pass funding | ⚠ **Historical pass superseded** (`phase-cd-findings.md`): its Peachscore amount/round-count claim was withdrawn as `Insufficient Evidence`; Comatch remains disambiguated. | — | Superseded |
| **D** | Re-verify low-confidence + material facts | ✅ **Done** (`phase-cd-findings.md`): AngelList ✅, Visible.vc founded/HQ ✅, FounderCloud HQ + liveness ✅. PandaDoc / Ansarada NDA-feature checks **skipped by decision**. | — | — |
| **E** | Historical reconcile claim | ⚠ Superseded by reproducible Phase 0 reconciliation on 2026-07-30; see `RECONCILIATION_REPORT.md` | Code session | Superseded |

### Historical Phase E claim — not current validation evidence
Findings from `phase-cd-findings.md` written to **CSV + XLSX + 6 company cards + research table**,
claimed consistency across four surfaces without the current automated
CSV/XLSX/site consistency suite:
- **Peachscore** — the historical `$1.7M/4 rounds` claim is now
  `Insufficient Evidence`; the stored Crunchbase page was inaccessible during
  Phase 0 reconciliation.
- **Visible.vc** — `hq_country` → Chicago, IL; funding remains `Unresolved`
  because stored secondary-source figures conflict and the historical PitchBook
  datapoint was not linked in the source fields.
- **Comatch** — `total_funding` disambiguation note (not the consulting-firm Comatch)
- **FounderCloud** — `hq_country` entity clarification (Starthawk LTD); `notes` liveness re-confirmed
- **Gust, OpenVC** — `users_traction` prefixed "Company-reported:"

**Cosmetic-label decision:** the triage's 12 self-reported-metric rows were reviewed; 10 already
attribute their stats in-text ("homepage claim", "site claim", "Company states"), so only the 2
that led with bare unattributed platform stats (Gust, OpenVC) got the "Company-reported:" prefix.
Blanket-prefixing the other 10 would have created redundant double-hedges.

> **Historical pipeline caveat:** the 2026-07-25 edits were repo-local and could
> have been overwritten by the former external Hermes export. Phase 0 replaces
> this claim with a tested local canonical build rooted in
> `data/competitive-research-tracker.csv`.

### Remaining optional decision
- **Paid-DB funding drill-down** — remaining unresolved funding sits behind Crunchbase/PitchBook
  paywalls. Recommendation: **mark "not public, final"** — no free-source path remains.

---

## 4. Definition of done

- [⏸] Post-signup onboarding audit — **deferred**, out of scope for this finalization (Gap A).
- [x] All contradiction / unsupported-claim flags triaged (`phase-b-triage.md`); material ones resolved or skipped.
- [ ] Funding fully resolved — Phase 0 withdrew the Peachscore amount and round
  count and left Comatch, Visible.vc, and Peachscore explicitly unresolved or
  `Insufficient Evidence`.
- [x] Low-confidence facts re-checked: Visible.vc founded/HQ verified, FounderCloud liveness confirmed live. SwipeDeck/SWIP/Swipe Invest/Cofounder.org/Inodash genuinely thin — cap wording in Phase E.
- [x] **Phase 0 replacement for Phase E** — canonical CSV, regenerated XLSX,
  six affected cards, and research table passed the reproducible integrity suite
  on 2026-07-30. This is technical consistency, not new factual verification.
- [x] No real personal data, company identity, or live credentials/tokens introduced (all edits are public-source facts).
