# Phase C/D — Desk-Research Findings (public sources)

Updated: 2026-07-25

Results of the public-source verification pass for the 8 material items from
`phase-b-triage.md` plus the funding gaps that affect ranking. **These are findings to
apply during Phase E reconcile** — the canonical CSV and cards are generated as one pass,
so nothing here is written into them yet (avoids partial-edit drift).

Legend: ✅ resolved · 🟡 improved but still ranged · ⚠ new item needing review

---

## Resolved / improved

| Company | Field | Before | Finding | Src |
|---|---|---|---|---|
| **Peachscore** | total_funding | not found | ✅ **$1.7M across 4 rounds** (Crunchbase org filed under legal name *Createnu Ventures*) | Crunchbase |
| **AngelList** | AI matching / `ai_depth`=3 | unverified (Phase B flag) | ✅ **Confirmed** — AI deal-scoring + matching on sector/check-size/co-investor fit. Score holds; no rescore. | multiple 2026 reviews |
| **Visible.vc** | founded_launch_year | not verified | ✅ **2014** | Tracxn / CB Insights |
| **Visible.vc** | hq_country | not verified | ✅ **Chicago, IL, US** | CB Insights |
| **Visible.vc** | total_funding | differs across sources | 🟡 **~$2.2M–$5.3M** (PitchBook $5.3M; others lower) — cite as range | PitchBook / Crunchbase |
| **FounderCloud** | hq_country | Accrington vs London conflict | ✅ Explained: **registered office Accrington** (STARTHAWK LIMITED, Companies House #12400556); **Crunchbase lists London** | Companies House / Crunchbase |

## New items needing review

| Company | Issue | Detail | Action |
|---|---|---|---|
| ✅ **FounderCloud** | Liveness | RESOLVED by live re-fetch (2026-07-25): foundercloud.com is **fully live** — active user profiles, ideas dated July 2026, footer "© 2026 Starthawk LTD", contact hello@starthawk.io. The dissolved **STARTHAWK LIMITED** (#12400556, dissolved 2023-11-21) is a **prior/renamed entity**; current operator is **Starthawk LTD**. `current_status` = live holds; no downgrade. | Optional: update the corporate-entity note in the card to "Starthawk LTD (formerly STARTHAWK LIMITED, dissolved 2023)". |
| ⚠ **Comatch** | Funding misattribution risk | The tracked Comatch is the **cofounder-matching app** (comatch.me / comatch.ai). The widely-cited "**€8M Series B / €4M Series A**" belongs to a **different** company — the consulting matchmaker Comatch (Germany, 2014, ex-McKinsey). | Keep tracked Comatch funding = **not found**; add note: "not the €12M consulting-firm Comatch." Prevents a wrong merge. |

## Funding still not public (mark "final")

Prior pass already searched these with real effort; this pass confirms no public company-funding figure exists (they are pre-seed micro-tools). Recommend marking **"not public — final"** rather than leaving as an open gap:

- **SWIP**, **SwipeDeck**, **Swipe Invest** (Direct competitors)
- Remaining large-marketplace names (AngelList, Gust, Crunchbase, Republic, etc.) have *platform/asset* figures but not clean *corporate* funding — already correctly labeled; leave as-is.

---

## Net effect on the phases

- **Phase C**: Peachscore filled (+$1.7M). Comatch disambiguated. Direct-competitor funding confirmed "not public — final." The remaining 22-row gap is now either resolved, correctly-labeled-as-unavailable, or dependent on paid databases — **no open desk work remains** unless the user wants paid-source drill-down.
- **Phase D**: AngelList ✅, Visible.vc ✅ (founded/HQ), FounderCloud HQ + liveness ✅. **PandaDoc / Ansarada NDA-feature verification — SKIPPED by decision (2026-07-25).** Their current NDA/e-sign flags stay "not found / partial" as last verified; not pursued further.
- **Score impact**: none. The only score-linked flag (AngelList `ai_depth`) verified *in favor* of the existing value. Composite/threat rankings unchanged.
