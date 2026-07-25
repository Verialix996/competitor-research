# BizMatch Competitive Research — Finalization Plan

Updated: 2026-07-25

Companion to `kanban.md`. This document captures the exact state of the research
corpus and the work required to consider it **final**. It is resumable: each phase
lists concrete company targets so any session (or Hermes sub-agent) can pick up mid-stream.

Tracker of record: `data/bizmatch-competitive-research-cited.csv` (36 companies, 8 scored dimensions).

---

## 1. Current state — what is done

- **36 companies** fully profiled across 5 competitor groups, with cited primary/secondary sources.
- **Scoring complete**: all 36 rated 1–5 on product overlap, feature maturity, market traction,
  funding strength, AI depth, NDA/security, network moat, plus the composite direct-threat score.
- **Registration-flow screenshots captured for all 36** (103 images in
  `sites/full-report-site/assets/registration-flows/`) — but visitor-side only (see Gap A).
- **Published surfaces**: research table (`sites/full-report-site/index.html`), 36 company
  cards, citation site, and the interactive Competitor Ranker (`ranker.html`).

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
| **C** | Second-pass funding | ✅ **Desk work done** (`phase-cd-findings.md`): Peachscore +$1.7M, Comatch disambiguated, direct-comp funding = "not public, final". Paid-DB drill-down optional. | — | Low |
| **D** | Re-verify low-confidence + material facts | ✅ **Done** (`phase-cd-findings.md`): AngelList ✅, Visible.vc founded/HQ ✅, FounderCloud HQ + liveness ✅. PandaDoc / Ansarada NDA-feature checks **skipped by decision**. | — | — |
| **E** | Reconcile & close | ✅ **DONE (2026-07-25)** — findings applied to CSV + XLSX + 6 cards + research table (see below) | Code session | Final |

### Phase E — what was applied (2026-07-25, directly in this repo)
Findings from `phase-cd-findings.md` written to **CSV + XLSX + 6 company cards + research table**,
kept byte-consistent across all four surfaces (verified):
- **Peachscore** — `total_funding` $1.7M/4 rounds + `funding_rounds` (Crunchbase as "Createnu Ventures")
- **Visible.vc** — `hq_country` → Chicago, IL; `total_funding` + PitchBook $5.3M datapoint
- **Comatch** — `total_funding` disambiguation note (not the consulting-firm Comatch)
- **FounderCloud** — `hq_country` entity clarification (Starthawk LTD); `notes` liveness re-confirmed
- **Gust, OpenVC** — `users_traction` prefixed "Company-reported:"

**Cosmetic-label decision:** the triage's 12 self-reported-metric rows were reviewed; 10 already
attribute their stats in-text ("homepage claim", "site claim", "Company states"), so only the 2
that led with bare unattributed platform stats (Gust, OpenVC) got the "Company-reported:" prefix.
Blanket-prefixing the other 10 would have created redundant double-hedges.

> ⚠ **Sync caveat:** these edits live in this repo only. If the external Hermes pipeline
> (`/mnt/ssd/.hermes/...`) ever re-exports, it will overwrite them. This repo is now the
> working copy of record for these corrections.

### Remaining optional decision
- **Paid-DB funding drill-down** — remaining unresolved funding sits behind Crunchbase/PitchBook
  paywalls. Recommendation: **mark "not public, final"** — no free-source path remains.

---

## 4. Definition of done

- [⏸] Post-signup onboarding audit — **deferred**, out of scope for this finalization (Gap A).
- [x] All contradiction / unsupported-claim flags triaged (`phase-b-triage.md`); material ones resolved or skipped.
- [x] Funding cited or marked "not public — final" — desk pass done (`phase-cd-findings.md`); Peachscore filled, rest labeled.
- [x] Low-confidence facts re-checked: Visible.vc founded/HQ verified, FounderCloud liveness confirmed live. SwipeDeck/SWIP/Swipe Invest/Cofounder.org/Inodash genuinely thin — cap wording in Phase E.
- [x] **Phase E** — findings applied to CSV + XLSX + 6 cards + research table, verified consistent (2026-07-25).
- [x] No real personal data, company identity, or live credentials/tokens introduced (all edits are public-source facts).
