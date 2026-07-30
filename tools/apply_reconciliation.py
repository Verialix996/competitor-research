#!/usr/bin/env python3
"""Apply the reviewed nine-field reconciliation to the canonical CSV.

This script is intentionally narrow and idempotent. It refuses to overwrite an
unexpected value so historical/user edits are not silently lost.
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "competitive-research-tracker.csv"

CHANGES = {
    ("Comatch", "total_funding"): {
        "accepted_old": {
            "not found / no public source - no Crunchbase/press funding record found; appears to be an independently/self-funded small studio (ZDTech Group Ltd)",
        },
        "value": (
            "Insufficient Evidence - no verified funding amount for the cofounder-matching app "
            "operated by ZDTech Group Ltd. Do not attribute funding reported for the unrelated "
            "German consulting marketplace named COMATCH."
        ),
    },
    ("FounderCloud", "hq_country"): {
        "accepted_old": {
            "United Kingdom - STARTHAWK LIMITED, Accrington, UK per terms; CB Insights lists London, England",
        },
        "value": (
            "United Kingdom - current site terms identify STARTHAWK LIMITED at 4 Blackburn Rd, "
            "Accrington; the site footer says Starthawk LTD, while a secondary profile lists "
            "London. Current legal-entity naming and city designation remain Unresolved."
        ),
    },
    ("FounderCloud", "notes"): {
        "accepted_old": {
            "FounderCloud is a lightweight cofounder/community marketplace. Its overlap is founder profiles, idea listings, filtering, messaging, and freemium community monetization rather than investor deal rooms or AI scoring.",
        },
        "value": (
            "FounderCloud is a lightweight cofounder/community marketplace. Its overlap is "
            "founder profiles, idea listings, filtering, messaging, and freemium community "
            "monetization rather than investor deal rooms or AI scoring. Liveness was rechecked "
            "on 2026-07-30: the site showed a current founder feed and a blog item dated "
            "2026-07-28."
        ),
    },
    ("Gust", "users_traction"): {
        "accepted_old": {
            "850,000+ startups, 85,000+ investment professionals; official platform for angel federations and accelerators",
        },
        "value": (
            "Company Claim: 850,000+ startups have used Gust and connected with 85,000+ "
            "investment professionals; Gust also calls itself the official platform of leading "
            "angel federations and venture accelerators."
        ),
    },
    ("OpenVC", "users_traction"): {
        "accepted_old": {
            "6,000+ VC firms/angel networks/family offices; 500+ pitches weekly; 40,000+ startups; 20,000+ verified investors; startups have gone on to raise $1B+",
        },
        "value": (
            "Company Claim: 6,000+ VC firms, angel networks and family offices; 500+ pitches "
            "weekly; 40,000+ startups; 20,000+ verified investors; OpenVC startups have gone on "
            "to raise more than $1B. These figures are not independently verified."
        ),
    },
    ("Visible.vc", "hq_country"): {
        "accepted_old": {
            "United States",
        },
        "value": (
            "United States - Chicago, Illinois, according to the company's LinkedIn profile "
            "(Company Claim / secondary platform profile)."
        ),
    },
    ("Visible.vc", "total_funding"): {
        "accepted_old": {
            "$2.16M per CB Insights; FilingFlow totals $2,189,990 SEC Form D filings; Owler says $2.5M",
        },
        "value": (
            "Unresolved - secondary sources conflict: CB Insights reports $2.16M; FilingFlow "
            "totals $2,189,990 across SEC Form D filings; Owler reports $2.5M. No single total "
            "was independently verified."
        ),
    },
    ("Peachscore", "total_funding"): {
        "accepted_old": {
            "not found / no public source for Peachscore's own funding amount - raised an undisclosed Convertible Note from Plug and Play and Root and Shoot Ventures (amount undisclosed)",
            "Insufficient Evidence - exact company funding amount not verified. The archived cited dataset claims $1.7M via Crunchbase under Createnu Ventures, but the existing Crunchbase page was inaccessible during reconciliation; Peachscore's company page confirms investor/shareholder relationships but states no amount.",
        },
        "value": (
            "Insufficient Evidence - exact company funding amount not verified. The existing "
            "Crunchbase page under Createnu Ventures was inaccessible during reconciliation; "
            "Peachscore's company page confirms investor/shareholder relationships but states "
            "no amount."
        ),
    },
    ("Peachscore", "funding_rounds"): {
        "accepted_old": {
            "Convertible Note (amount and date undisclosed)",
            "Insufficient Evidence - round count not verified. The archived cited dataset claims 4 rounds via Crunchbase under Createnu Ventures, but that existing page was inaccessible during reconciliation.",
        },
        "value": (
            "Insufficient Evidence - round count not verified. The existing Crunchbase page "
            "under Createnu Ventures was inaccessible during reconciliation, and no accessible "
            "stored source states the number of rounds."
        ),
    },
}

LEGACY_LABEL_CLEANUP = {
    ("PitchLeague", "notes"): (
        "PitchLeague is a free, gamified deck-scoring tool built by athlete-investing platform Sequel primarily as a deal-sourcing and research/data asset, not a standalone monetized product - it has no investor-matching, NDA, or messaging features and the lowest direct_threat_score in the batch. Its differentiator is the large proprietary research dataset (17,546 decks) rather than platform depth.",
        "PitchLeague is a free, gamified deck-scoring tool built by athlete-investing platform Sequel primarily as a deal-sourcing and research/data asset, not a standalone monetized product - the recorded research found no investor-matching, NDA, or messaging features. Its differentiator is the large proprietary research dataset (17,546 decks) rather than platform depth. The former direct-threat comparison is deprecated.",
    ),
    ("PitchLeague", "plain_language_description"): (
        "PitchLeague is a free, gamified deck-scoring tool built by athlete-investing platform Sequel primarily as a deal-sourcing and research/data asset, not a standalone monetized product - it has no investor-matching, NDA, or messaging features and the lowest direct_threat_score in the batch. Its differentiator is the large proprietary research dataset (17,546 decks) rather than platform depth.",
        "PitchLeague is a free, gamified deck-scoring tool built by athlete-investing platform Sequel primarily as a deal-sourcing and research/data asset, not a standalone monetized product - the recorded research found no investor-matching, NDA, or messaging features. Its differentiator is the large proprietary research dataset (17,546 decks) rather than platform depth. The former direct-threat comparison is deprecated.",
    ),
}

LEGACY_PHRASE_CLEANUP = (
    (
        "Cofounder.org",
        ("notes", "plain_language_description"),
        " Lowest direct-threat score of the batch given near-total absence of traction/security/AI evidence.",
        " Any comparative threat conclusion based on the legacy score is deprecated.",
    ),
    (
        "Dropbox Sign",
        ("notes", "plain_language_description"),
        "Dropbox Sign is the weakest direct competitive analog to BizMatch in this batch (product_overlap_score 1) - it is a pure e-signature tool with NO data room, NO NDA-gating mechanism, and NO document-tracking/analytics layer.",
        "Dropbox Sign is a pure e-signature tool; the recorded research found no data room, NDA-gating mechanism, or document-tracking/analytics layer.",
    ),
    (
        "Inodash",
        ("notes", "plain_language_description"),
        "It is a standalone deck-scoring/idea-validation micro-tool with zero investor-connection or matchmaking flow, making it a low direct threat to BizMatch's core model.",
        "It is a standalone deck-scoring/idea-validation micro-tool with no investor-connection or matchmaking flow in the recorded evidence; any direct-threat conclusion based on the legacy score is deprecated.",
    ),
    (
        "Digify",
        ("notes", "plain_language_description"),
        "Digify is a document security/VDR company, not a matchmaking platform - product_overlap_score reduced from prior pass's 5 to 2 to reflect the category mismatch (BizMatch is swipe/match-based, Digify is document-gating).",
        "Digify is a document security/VDR company, not a matchmaking platform.",
    ),
    (
        "Carta Data Rooms",
        ("notes", "plain_language_description"),
        "Carta is the most directly comparable case in this batch to BizMatch's founder-investor NDA-gated flow, since it's explicitly positioned for startup fundraising data rooms (not just enterprise M&A). Its funding_strength_score (5) reflects the WELL-FUNDED PARENT COMPANY, not the Data Room product line specifically, which is a minor feature/revenue line within Carta's broader business.",
        "Carta's Data Room is positioned for startup fundraising data rooms rather than only enterprise M&A. Recorded corporate funding refers to the parent company, not the Data Room product line, and is not used as an active relationship-score input.",
    ),
)


def main():
    needs_newline_normalization = b"\r\n" in CSV_PATH.read_bytes()
    with CSV_PATH.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        rows = list(reader)
    if fieldnames is None:
        raise SystemExit("Canonical CSV has no header")

    by_company = {row["company"]: row for row in rows}
    if len(by_company) != len(rows):
        raise SystemExit("Duplicate company identifiers found; refusing reconciliation")

    changed = 0
    for (company, field), change in CHANGES.items():
        row = by_company.get(company)
        if row is None:
            raise SystemExit(f"Missing expected company: {company}")
        current = row[field]
        target = change["value"]
        if current == target:
            continue
        if current not in change["accepted_old"]:
            raise SystemExit(
                f"Unexpected value for {company}.{field}; refusing to overwrite user changes"
            )
        row[field] = target
        changed += 1

    for (company, field), (old, target) in LEGACY_LABEL_CLEANUP.items():
        current = by_company[company][field]
        if current == target:
            continue
        if current != old:
            raise SystemExit(
                f"Unexpected value for {company}.{field}; refusing legacy-label cleanup"
            )
        by_company[company][field] = target
        changed += 1

    for company, fields, old_phrase, replacement in LEGACY_PHRASE_CLEANUP:
        for field in fields:
            current = by_company[company][field]
            if old_phrase in current:
                by_company[company][field] = current.replace(old_phrase, replacement)
                changed += 1
            elif replacement not in current:
                raise SystemExit(
                    f"Expected legacy phrase missing from {company}.{field}; refusing cleanup"
                )

    if changed or needs_newline_normalization:
        with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    print(f"Reconciliation applied: {changed} field(s) changed; 9 reviewed decisions present")


if __name__ == "__main__":
    main()
