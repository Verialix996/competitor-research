# Phase B — Contradiction & Unsupported-Claim Triage

> **Historical triage:** Current canonical decisions and score status are in
> `RECONCILIATION_REPORT.md` and `SCORING_METHODOLOGY.md`. Legacy scores
> referenced below are deprecated and do not feed active outputs.

Updated: 2026-07-25

Triage of every contradiction (32) and unsupported-claim (30) flag in
`archive/data/bizmatch-competitive-research-cited.csv`, sorted into three buckets so
finalization effort goes only where it changes the corpus.

## Summary

| Bucket | Count | Action |
|---|---|---|
| **Resolved** — flag documents an already-applied correction | ~20 | None — keep as audit trail |
| **Cosmetic** — unauditable self-reported metric, correctly labeled | ~12 | Cap wording as "company-reported"; no fieldwork |
| **Material / open** — genuine unresolved item | **8** | Address in Phases A/C/D (below) |

**Bottom line:** the flags are overwhelmingly healthy — they show the research
*caught and fixed* bad automated data. Only 8 items need any further action, and
most fold into work already planned.

---

## Resolved — no action needed

These flags exist only to record a correction the researcher already made. Common
pattern: an automated first pass misread a number, and the cited pass fixed it.

- **CoffeeSpace** — "$10M funding" was the FAQ describing *target customers*, not CoffeeSpace's raise (~$500K). Fixed.
- **SecureDocs** — "$250 funding" was the $250/month price. Fixed (bootstrapped).
- **Dropbox Sign** — "$15; $100 funding" was pricing tiers. Fixed.
- **Ansarada** — "$1.1B–$24B funding" was marquee *deal values run through the platform*, moved to deals-facilitated. Fixed.
- **Digify** — "$500M funding" was customer fundraising facilitated, not Digify's ~$3.9M raise. Fixed.
- **Swipe Invest** — "$45B funding" was a macro-ecosystem stat misparse. Fixed.
- **Cherub / Comatch / SWIP / YC / PitchGrade / Foundersbase / Cofounder.org / Tertle / Evalyze** — spurious `nda_gated_unlock` / `e_signature` / `swipe_card_interface` "yes" flags from the automated pass, downgraded to "not found" after real research.
- **Carta Data Rooms** — NDA-gating contradiction explicitly RESOLVED: native in the *paid* Data Room tier (per Carta's own support docs), absent in the free cap-table tier.
- **Crunchbase** — market-data article values conflated with corporate funding; ignored as unsupported.

## Cosmetic — self-reported metrics (cap wording, don't chase)

Unaudited homepage/marketing figures. Correctly flagged already; they can't be
independently verified without company cooperation. Recommend a consistent
"company-reported, unaudited" label rather than any fieldwork.

- **SwipeDeck** — "95%→25% effort / 15%→85% success" (no methodology)
- **PitchBob** — "60,183" vs "35k+" entrepreneurs (inconsistent rolling counters)
- **CoffeeSpace** — 30K users / 2.5M swipes / 65K matches
- **Evalyze** — "10,500+ founders", readiness score /850
- **Peachscore** — "$220M+ raised", "1,500+ startups"
- **SeedBlink** — "half a billion euros invested"
- **Slidebean** — "$350M raised by customers"
- **PitchGrade** — "4,000+ companies / 10k+ decks"
- **PitchLeague** — "3000+ founders" (dataset size *is* corroborated — fine)
- **Gust** — "800k founders" vs "850k+ startups" (stat drift over time)
- **Republic / OpenVC / Signal / Foundersuite** — cumulative-capital / investor-count figures that vary by page or date snapshot

---

## Material / open — the only 8 items needing action

| # | Company | Issue | Routes to |
|---|---|---|---|
| 1 | **CoFoundersLab** | Swipe-card vs search/filter UI unresolved — needs a logged-in in-app check | **Phase A** (account) |
| 2 | **DocSend** | Pricing + mobile-app existence blocked by Cloudflare/403; on secondary sources only | **Phase A** / retry direct |
| 3 | **AngelList** | "AI matching" capability could not be verified — may lower its `ai_depth`=3 score | **Phase D** re-check + rescore |
| 4 | **PandaDoc** | NDA-gating in Deal Rooms downgraded to "not found" — verify feature docs | **Phase D** |
| 5 | **Ansarada** | E-signature / NDA-gating "pending direct product-page verification" | **Phase D** |
| 6 | **Peachscore** | Crunchbase org is under legal name **"Createnu Ventures"** — actionable funding lead | **Phase C** |
| 7 | **FounderCloud** | HQ conflict: STARTHAWK LIMITED (Accrington) vs CB Insights (London) | **Phase D** (minor) |
| 8 | **Visible.vc** | Founded year / funding / round count differ across 4 sources | **Phase D** (low-conf) |

### Notes for the rescore check (item 3)
Only **AngelList** has a flag that could move a *score* (its AI-matching claim underpins
`ai_depth`=3). Every other material item affects a fact or feature flag, not a 1–5 score,
so the composite/threat rankings are stable regardless of how they resolve.

---

## Effect on "Definition of Done"

- Phase B is **complete as a triage**: 20 resolved, 12 cosmetic (label-only), 8 routed.
- No contradiction requires *new* fieldwork beyond what Phases A/C/D already cover.
- Recommended copy change for the 12 cosmetic rows: prefix such metrics with
  "company-reported:" wherever they appear in cards, so nothing reads as verified fact.
