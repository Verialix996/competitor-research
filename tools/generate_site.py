#!/usr/bin/env python3
import csv
import json
import re
from html import escape
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "competitive-research-tracker.csv"
SUBSTITUTES_PATH = ROOT / "data" / "substitutes-research.csv"
SUBSTITUTE_EVIDENCE_PATH = ROOT / "data" / "substitute-evidence.csv"
SUBSTITUTE_WORKFLOWS_PATH = ROOT / "data" / "substitute-workflows.csv"
SITE = ROOT / "sites" / "full-report-site"
COMPANY_SITE = SITE / "companies"
CITATION_SITE = ROOT / "sites" / "citation-site"
REPORTS = ROOT / "reports"
RECONCILIATION_DATE = "2026-07-30"

SUBSTITUTE_JOB_LABELS = {
    "JOB-COFOUNDER": "Founder seeking a co-founder",
    "JOB-FOUNDER-INVESTOR": "Founder seeking an investor",
    "JOB-INVESTOR-SOURCING": "Investor sourcing startups or founders",
    "JOB-TRUSTED-PROGRESSION": "Founder and investor progressing to trusted interaction",
}

FEATURES = [
    ("swipe_card_interface", "Swipe/card interface"),
    ("mutual_match", "Mutual match"),
    ("ai_matching_scoring", "AI matching/scoring"),
    ("ai_deck_scoring", "AI deck scoring"),
    ("founder_to_founder_flow", "Founder-to-founder flow"),
    ("founder_to_investor_flow", "Founder-to-investor flow"),
    ("project_profiles", "Profiles/projects"),
    ("nda_gated_unlock", "NDA/access gate"),
    ("data_room", "Data room/document controls"),
    ("e_signature", "E-signature"),
    ("messaging_collaboration", "Messaging/collaboration"),
    ("meeting_prep_ai_briefing", "AI meeting/diligence briefing"),
    ("mobile_app", "Mobile app"),
    ("web_app", "Web app"),
]

JOURNEY_STAGES = [
    ("cofounder", "Founder/cofounder matching", "founder_to_founder_flow"),
    ("investor", "Founder/investor discovery", "founder_to_investor_flow"),
    ("mutual", "Mutual match", "mutual_match"),
    ("profiles", "User/project profiles", "project_profiles"),
    ("conversation", "Structured conversation", "messaging_collaboration"),
    ("collaboration", "Project collaboration", "messaging_collaboration"),
    ("nda", "NDA gate", "nda_gated_unlock"),
    ("disclosure", "Controlled document disclosure", "data_room"),
    ("meeting", "Meeting or due-diligence preparation", "meeting_prep_ai_briefing"),
    ("journey", "End-to-end journey coverage", None),
]

PRIORITY_ORDER = ["CoffeeSpace", "Cherub", "Foundersuite", "YC Co-Founder Matching", "OpenVC", "Foundersbase"]

LEGACY_SCORE_FIELDS = [
    "product_overlap_score",
    "feature_maturity_score",
    "market_traction_score",
    "funding_strength_score",
    "ai_depth_score",
    "nda_security_strength_score",
    "network_moat_score",
    "direct_threat_score",
]

# These are the pre-existing analytical weights. They are preserved for audit and
# documentation only. The required explicit research inputs do not yet exist in
# the 65-column canonical schema, so no numeric relationship score is published.
RELATIONSHIP_SCORE_MODELS = {
    "competitive": {
        "matches": ("Direct competitor", "Substitute"),
        "components": (
            ("User/use-case overlap", "relationship_use_case_overlap_score", 0.30),
            ("Product-process overlap", "relationship_workflow_overlap_score", 0.25),
            ("Traction/network effect", "relationship_traction_network_score", 0.20),
            ("Geographic/niche fit", "relationship_geographic_fit_score", 0.10),
            ("Business/pricing model", "relationship_pricing_overlap_score", 0.10),
            ("Technology/AI depth", "relationship_ai_depth_score", 0.05),
        ),
    },
    "feature": {
        "matches": ("Feature benchmark",),
        "components": (
            ("Capability quality", "relationship_capability_quality_score", 0.30),
            ("Maturity", "relationship_maturity_score", 0.25),
            ("Price", "relationship_price_score", 0.15),
            ("UX", "relationship_ux_score", 0.15),
            ("Ease to integrate/imitate", "relationship_ease_score", 0.15),
        ),
    },
    "infrastructure": {
        "matches": ("Infrastructure / potential partner",),
        "components": (
            ("Security", "relationship_security_score", 0.25),
            ("API/integration", "relationship_api_score", 0.20),
            ("Pricing", "relationship_price_score", 0.15),
            ("MVP fit", "relationship_mvp_fit_score", 0.15),
            ("Build-versus-buy", "relationship_build_buy_score", 0.15),
            ("NDA/controlled disclosure fit", "relationship_nda_fit_score", 0.10),
        ),
    },
}

STRATEGIC = {
    "Cherub": ("Direct competitor", "Founder-investor matching", "One-page deal profile, investor discovery, mutual interest, controlled document sharing", "Create a browsable startup deal profile and connect it with relevant investors"),
    "Comatch": ("Direct competitor", "Cofounder matching", "mobile swipe, personality matching, chat", "Founder/cofounder discovery; lightweight matching-to-chat flow"),
    "CoffeeSpace": ("Direct competitor", "Cofounder matching", "swipe/card, mutual match, AI recommendations, mobile app, talent marketplace", "Founder/cofounder discovery; founder/talent matching; mobile matching UX"),
    "SwipeDeck": ("Direct competitor", "Founder-investor matching", "swipe/card, mutual match, investor discovery, document upload", "Founder/investor discovery; fast investor-card screening"),
    "Foundersbase": ("Direct competitor", "Founder and startup professional network", "Professional profiles, community discovery, co-founder discovery, investor visibility", "Build a startup identity and discover founders, collaborators and investors"),
    "Swipe Invest": ("Substitute", "Founder-investor event/discovery", "swipe concept, investor access, early-stage Europe", "Investor discovery and event-based access"),
    "SWIP": ("Substitute", "Pre-launch cofounder matching", "waitlist, AI match simulator, founder cohorts", "Founder/cofounder discovery concept benchmark"),
    "YC Co-Founder Matching": ("Substitute / network threat", "Cofounder matching network", "Free matching product, mutual interest, founder profiles, YC ecosystem trust", "Find a potential co-founder through a trusted startup ecosystem"),
    "CoFoundersLab": ("Substitute", "Cofounder matching network", "founder profiles, community, advisor/investor paths", "Founder/cofounder discovery; large cofounder network"),
    "Cofounder.org": ("Substitute", "Cofounder matching", "curated matching, founder profiles", "Founder/cofounder discovery"),
    "Tertle": ("Substitute", "Cofounder matching", "founder discovery, AI claims, messaging", "Founder/cofounder discovery"),
    "FounderCloud": ("Substitute", "Founder network", "founder profiles, startup community", "Founder discovery and startup community"),
    "AngelList": ("Substitute", "Startup fundraising/network", "investor discovery, fundraising workflows, network effects", "Fundraising discovery; investor network access"),
    "Gust": ("Substitute", "Startup fundraising workspace", "investor relations, application/fundraising workflows", "Fundraising workspace and investor application management"),
    "Crunchbase": ("Substitute", "Company/investor discovery database", "discovery, research, investor/company data", "Investor/company discovery and market research"),
    "Republic": ("Substitute", "Investment marketplace", "startup investing, investor network, fundraising marketplace", "Capital access and investor network growth"),
    "StartEngine": ("Substitute", "Investment marketplace", "crowdfunding, investor network, issuer onboarding", "Capital access and investor acquisition"),
    "OpenVC": ("Substitute", "Investor database and discovery platform", "Investor database, search, filters, outreach, fundraising readiness", "Find, filter and contact relevant investors"),
    "Visible.vc": ("Substitute", "Investor relations workspace", "updates, data room-like sharing, investor discovery", "Investor updates and fundraising workspace"),
    "Signal (NFX)": ("Substitute", "Investor discovery network", "investor matching, NFX network, AI scoring claims", "Investor discovery and warm-intro substitute"),
    "Foundersuite": ("Substitute", "Investor database and fundraising workspace", "Investor database, research, outreach, CRM, pipeline tracking", "Find relevant investors and manage the fundraising pipeline"),
    "PitchBob": ("Feature benchmark", "AI pitch deck review", "deck feedback, AI startup tools, templates", "Pitch-deck review as supporting workflow"),
    "PitchGrade": ("Feature benchmark", "AI pitch deck review", "deck scoring, feedback", "Pitch-deck review as supporting workflow"),
    "Slidebean": ("Feature benchmark", "Pitch deck tooling", "deck review, design, fundraising content", "Pitch-deck review and presentation workflow"),
    "Evalyze": ("Feature benchmark", "AI fundraising readiness", "deck analysis, investor matching campaign, readiness score", "Pitch-deck review and investor-readiness support"),
    "SeedBlink": ("Feature benchmark", "Pitch/fundraising readiness", "deck review, investor platform, funding path", "Pitch-deck review and fundraising-readiness support"),
    "PitchLeague": ("Feature benchmark", "AI pitch leaderboard", "deck scoring, benchmarking, investor visibility", "Pitch-deck review and public benchmarking"),
    "Inodash": ("Feature benchmark", "AI validation and deck review", "deck review, idea validation, collaboration", "Pitch-deck review and idea-validation support"),
    "Peachscore": ("Feature benchmark", "Startup scoring and acceleration", "AI scoring, investor readiness, accelerator workflow", "Startup scoring and investor-readiness support"),
    "DocSend": ("Infrastructure / potential partner", "Secure document sharing", "document analytics, controlled links, data room-like sharing", "Controlled project/deck disclosure and investor analytics"),
    "Digify": ("Infrastructure / potential partner", "Secure data room", "watermark, permissions, audit trail, document security", "Controlled project disclosure and secure document access"),
    "SecureDocs": ("Infrastructure / potential partner", "Virtual data room", "data room, security, audit trail, permissions", "NDA/data-room infrastructure for controlled disclosure"),
    "Ansarada": ("Infrastructure / potential partner", "Virtual data room", "data room, AI document handling, deal workflow", "Secure disclosure and diligence room infrastructure"),
    "Carta Data Rooms": ("Infrastructure / potential partner", "Startup data room", "startup data room, cap table adjacent, investor diligence", "Data room benchmark and possible startup-stack adjacency"),
    "Dropbox Sign": ("Infrastructure / potential partner", "E-signature", "legally binding signatures, templates, API", "NDA signing infrastructure"),
    "PandaDoc": ("Infrastructure / potential partner", "Document workflow and e-signature", "documents, templates, e-signature, API", "NDA and document workflow infrastructure"),
}

PRIORITY = {
    "CoffeeSpace": ("Benchmark for matching and swipe UX.", "Founder/cofounder discovery with mobile mutual matching.", "Use frequent recommendations, profile quality prompts, and simple match-to-chat UX.", "Do not copy the broad talent marketplace before BizMatch has trust and collaboration depth.", "High", "High"),
    "Cherub": ("Benchmark for startup one-pagers, investor discovery, and controlled disclosure.", "Create a browsable startup deal profile and connect it with relevant investors.", "Use a concise public project profile before requesting access to sensitive materials.", "Do not claim or build around an explicit NDA/e-signature step until the workflow is validated and sourced.", "High", "High"),
    "Foundersuite": ("Benchmark for investor database plus fundraising workflow continuity.", "Find relevant investors and manage the fundraising pipeline.", "Maintain continuity from investor discovery through outreach and follow-up.", "Do not build a complete fundraising CRM before the match-to-collaboration workflow is validated.", "Medium-High", "High"),
    "YC Co-Founder Matching": ("Network threat because it is free, trusted, and connected to the YC ecosystem.", "Find a potential co-founder through a trusted startup ecosystem.", "Learn from trust-by-network, free access, and a low-friction founder profile loop.", "Do not describe or compete with it as the YC program itself.", "High", "High"),
    "OpenVC": ("Substitute for investor search, filtering, and outreach.", "Find, filter and contact relevant investors.", "Provide searchable investor fit and actionable outreach context.", "Do not make a static investor list the center of BizMatch.", "Medium-High", "High"),
    "Foundersbase": ("Relevant because of founder-network overlap and possible Israeli ecosystem relevance.", "Build a startup identity and discover founders, collaborators and investors.", "Use professional identity and local network density.", "Do not rely on unstructured profile browsing without matching and gated collaboration.", "Medium", "Medium"),
}

STRATEGIC_DETAILS = {
    "Cherub": {
        "plain_language_description": "Founders provide structured information about their startup to create a browsable one-page deal profile. Investors can discover these project profiles and, when interested, access or request additional startup materials.",
        "primary_job_solved": "Create a browsable startup deal profile and connect it with relevant investors",
        "product_model": "Structured startup submission creates a concise deal profile or one-pager for investor discovery; additional materials can be shared through a controlled document experience.",
        "bizmatch_lesson": "Use a concise public project profile before requesting access to sensitive materials.",
        "do_not_copy": "Do not claim or build around an explicit NDA/e-signature step until the workflow is validated and sourced.",
        "important_clarification": "Controlled access is confirmed, but an explicit NDA/e-signature step was not found. The public/browsable deal profile and additional private materials are not necessarily the same level of disclosure.",
    },
    "Foundersuite": {
        "plain_language_description": "Foundersuite is a fundraising workspace built around an investor database, investor research, outreach and pipeline management.",
        "primary_job_solved": "Find relevant investors and manage the fundraising pipeline",
        "product_model": "Search and filter an investor database, research targets, manage outreach, and continue into fundraising CRM and pipeline follow-up.",
        "bizmatch_lesson": "Maintain continuity from investor discovery through outreach and follow-up.",
        "do_not_copy": "Do not build a complete fundraising CRM before the match-to-collaboration workflow is validated.",
        "important_clarification": "Investor database plus fundraising workflow, not merely a CRM.",
    },
    "Foundersbase": {
        "plain_language_description": "Foundersbase operates like a LinkedIn-style professional network for founders, potential co-founders, startup contributors and investors.",
        "primary_job_solved": "Build a startup identity and discover founders, collaborators and investors",
        "product_model": "Profile and community-driven professional network for discovering founders, co-founders, collaborators, and investors; broader and less workflow-structured than BizMatch.",
        "bizmatch_lesson": "Use professional identity and local network density.",
        "do_not_copy": "Do not rely on unstructured profile browsing without matching and gated collaboration.",
        "important_clarification": "LinkedIn-style is an explanatory analogy, not an affiliation. Relevance to BizMatch comes from founder-network overlap and possible Israeli ecosystem relevance.",
    },
    "YC Co-Founder Matching": {
        "plain_language_description": "YC Co-Founder Matching is a free co-founder-matching network operated by Y Combinator and connected to the YC and Startup School ecosystem.",
        "primary_job_solved": "Find a potential co-founder through a trusted startup ecosystem",
        "product_model": "Free ecosystem-supported matching network where founders create profiles, browse or receive potential matches, and connect through mutual interest.",
        "bizmatch_lesson": "Learn from trust-by-network, free access, strong brand trust, and network effects.",
        "do_not_copy": "Do not compete on generic co-founder discovery alone, and do not describe it as the YC program itself.",
        "important_clarification": "Matching-product participation does not imply acceptance into YC. It is not an investor database and not a full BizMatch-style protected-collaboration platform.",
    },
    "OpenVC": {
        "plain_language_description": "OpenVC is primarily a searchable investor database and fundraising platform that helps founders find, filter and approach relevant investors.",
        "primary_job_solved": "Find, filter and contact relevant investors",
        "product_model": "Searchable investor database with investor-fit information, filters, outreach support, and fundraising-readiness tools.",
        "bizmatch_lesson": "Provide searchable investor fit and actionable outreach context.",
        "do_not_copy": "Do not make a static investor list the center of BizMatch.",
        "important_clarification": "Primarily an investor database and outreach tool, not mutual matching or a match-to-collaboration platform.",
    },
}

VALIDATION_ROADMAP = [
    ("High-quality profiles", "Better profile completeness will make recommendations credible enough to engage with.", "Founder/project profile review and manual approval loop.", "Completed and approved profile rate", "Profile revision rate", "Many registrations stay incomplete or cannot be approved.", "Phase 1"),
    ("Matching", "Curated recommendations can outperform generic browsing for first-time founders.", "Founder/cofounder recommendation batches.", "Relevant-match acceptance rate", "Recommendation dismissal reason quality", "Users reject most recommendations as irrelevant.", "Phase 1"),
    ("Explained matching", "Explaining fit will increase trust and acceptance versus unexplained recommendations.", "Show concise fit rationale for each recommendation.", "Acceptance uplift compared with unexplained recommendations", "Profile views per recommendation", "Explanations do not improve acceptance or create confusion.", "Phase 1"),
    ("Mutual match", "Mutual consent will increase willingness to start a serious conversation.", "Two-sided accept/request-to-connect flow.", "Match-to-first-message conversion", "Accepted-match rate", "Matches do not convert into messages.", "Phase 1"),
    ("Structured conversation", "Guided prompts can move matches from interest to substance faster than open chat.", "Conversation prompts around role fit, project stage, commitment, and next steps.", "Meaningful reply rate", "Prompt completion rate", "Users bypass prompts or replies remain shallow.", "Phase 2"),
    ("Access request", "Private project access should be requested only after qualified conversations.", "Request-access action with reason and owner approval.", "Qualified conversations requesting private access", "Access request approval rate", "Access is requested too early or rarely requested at all.", "Phase 2"),
    ("NDA", "NDA completion can be introduced without breaking momentum if tied to clear disclosure value.", "Partner-provided NDA/e-sign flow.", "NDA completion rate", "Time from access approval to signed NDA", "NDA drop-off blocks otherwise qualified matches.", "Phase 2"),
    ("Controlled disclosure", "Selective document access can turn qualified curiosity into investor or partner meetings.", "Permissioned project/deck/document disclosure.", "Document-view-to-meeting conversion", "Documents viewed per approved access request", "Documents are viewed but meetings do not follow.", "Phase 2"),
    ("Meetings", "Continuity from match to meeting is the strongest proof the workflow matters.", "Meeting scheduling and short prep brief.", "Match-to-meeting conversion", "Meeting completion rate", "Conversations stall before scheduling.", "Phase 3"),
    ("Network health", "Local liquidity should improve before expanding beyond the first wedge.", "Cohort health dashboard and manual liquidity review.", "Median time to first relevant match", "Repeat weekly active qualified users", "Qualified users wait too long for relevant matches.", "Phase 1-3"),
    ("Growth", "Referrals from satisfied matches can seed trusted local density.", "Invite/referral flow for founders, mentors, and angels.", "Referral or invitation rate", "Invite acceptance rate", "Invites are low-quality or do not convert.", "Phase 3"),
]

RUBRIC = {
    "Use-case overlap": ("Solves a distant or supporting job.", "Competes for one important BizMatch job.", "Competes for the same users and primary workflow."),
    "Workflow overlap": ("Touches one isolated workflow step.", "Covers several adjacent steps but not the full journey.", "Covers discovery, matching, trust, disclosure, and follow-up in one flow."),
    "Traction and network effects": ("Little public usage or no visible network signal.", "Some credible usage, customers, or community adoption.", "Large active network or strong usage signals that compound over time."),
    "Geographic/niche fit": ("Weak relevance to Israel or BizMatch's first wedge.", "Some relevance to early-stage founders or adjacent local communities.", "Direct relevance to the Israeli pre-seed/cofounder wedge."),
    "Pricing/business-model overlap": ("Different buyer or revenue model.", "Partially similar monetization or buyer.", "Competes for the same buyer budget and launch monetization path."),
    "AI depth": ("No public AI evidence or only generic claims.", "AI assists a bounded feature such as recommendations or scoring.", "AI is central, explained, and visible across the workflow."),
    "Capability quality": ("Basic or unproven implementation.", "Usable focused capability with public evidence.", "Mature, differentiated capability with credible proof."),
    "Maturity": ("Early, waitlisted, or sparse product evidence.", "Live product with some adoption or paid use.", "Established product with durable customer/process evidence."),
    "Security": ("No meaningful security/disclosure evidence.", "Basic gating, permissions, or trust controls.", "Strong document security, auditability, and controlled access."),
    "Integration/API suitability": ("Hard to integrate or no public integration path.", "Potential integration exists but is unclear or limited.", "Clear API, partner path, or embeddable workflow."),
    "MVP fit": ("Too broad, heavy, or misaligned for early BizMatch.", "Useful later but not essential for first launch.", "Directly supports a first-launch workflow requirement."),
    "Build-versus-buy value": ("Likely cheaper or more strategic to build internally.", "Could buy temporarily but may need replacement.", "Buying saves major time/risk without weakening differentiation."),
}

RELATION_ORDER = ["Direct competitor", "Substitute / network threat", "Substitute", "Feature benchmark", "Infrastructure / potential partner"]

def slug(name):
    cleaned = name.lower().replace("&", "and").replace("/", " ").replace("(", "").replace(")", "").replace(".", "-").replace(" ", "-")
    return re.sub(r"-+", "-", cleaned).strip("-")

def urls(text):
    return re.findall(r"https?://[^\s;,)]+", text or "")

def source_anchor(u):
    try:
        host = urlparse(u).netloc.replace("www.", "")
    except Exception:
        host = u
    return f'<a href="{escape(u)}" rel="noopener" target="_blank">{escape(host)}</a>'

def source_title(u):
    try:
        parsed = urlparse(u)
        host = parsed.netloc.replace("www.", "")
        path = parsed.path.strip("/").replace("-", " ").replace("_", " ")
        if not path:
            return host
        last = path.split("/")[-1] or host
        return f"{host}: {last[:80]}"
    except Exception:
        return u

def source_cards(row, claim="Company profile evidence"):
    cards = []
    for u in urls(row.get("primary_sources", "")):
        cards.append((u, "Primary / Company claim", "Company site or official product page"))
    for u in urls(row.get("secondary_sources", "")):
        cards.append((u, "Secondary", "External publication, database, or listing"))
    if not cards:
        return '<p class="muted">No source URL recorded.</p>'
    return "".join(
        f"""<article class="source-card"><h3><a href="{escape(u)}" rel="noopener" target="_blank">{escape(source_title(u))}</a></h3><dl class="mini-dl"><dt>Source type</dt><dd>{escape(kind)}</dd><dt>Publication</dt><dd>{escape(urlparse(u).netloc.replace('www.', '') or org)}</dd><dt>Checked</dt><dd>{escape(row.get('last_checked','') or 'not recorded')}</dd><dt>Supports</dt><dd>{escape(claim)}</dd></dl>{'<p class="source-note">Company-reported; not independently verified.</p>' if 'Company claim' in kind else ''}</article>"""
        for u, kind, org in cards
    )

def first_source(row):
    return (urls(row.get("primary_sources", "")) or urls(row.get("secondary_sources", "")) or [""])[0]

def overall_confidence(text):
    t = (text or "").strip()
    if t.startswith("High"):
        return "High"
    if t.startswith("Medium"):
        return "Medium"
    if t.startswith("Low"):
        return "Low"
    return "Insufficient Evidence"

def text_status(text):
    t = (text or "").strip().lower()
    if not t:
        return "Not found"
    if t.startswith("no") or t.startswith("not offered"):
        return "Not found"
    if t.startswith("not a matching product") or t.startswith("not a founder-matching product") or t.startswith("not a capital") or t.startswith("not a cofounder"):
        return "Not applicable"
    if "not applicable" in t:
        return "Not applicable"
    if "not found" in t or "no evidence" in t or "no public source" in t:
        return "Not found"
    if t.startswith("yes in a limited") or "limited sense" in t or "closest equivalent" in t or "generic" in t:
        return "Partial"
    if t.startswith("yes"):
        return "Confirmed"
    return "Partial"

def delivery_type(feature_key, status, note):
    if status in ("Not found", "Not applicable"):
        return "Not applicable"
    n = (note or "").lower()
    if "partner" in n:
        return "Partner-provided"
    if "api" in n or "integration" in n:
        return "Integration"
    if "marketing" in n or "claim" in n or "not documented" in n:
        return "Marketing claim"
    return "Native"

def confidence(row, status):
    base = row.get("source_confidence", "")
    if status == "Confirmed":
        if base.startswith("High"):
            return "High"
        if "Low" in base:
            return "Low"
        return "Medium"
    if status == "Partial":
        return "Medium" if "High" in base else "Low"
    return "Medium" if base.startswith("High") else "Low"

def relationship_score(row):
    relationship = (row.get("competitive_relationship") or "").strip()
    selected = None
    for model in RELATIONSHIP_SCORE_MODELS.values():
        if any(relationship == match or relationship.startswith(match) for match in model["matches"]):
            selected = model
            break
    if selected is None:
        return {
            "value": None,
            "status": "Insufficient Evidence",
            "formula": "No approved model for this relationship type.",
            "components": {},
            "missing_inputs": ["approved relationship scoring model"],
        }

    components = {}
    missing = []
    for label, field, weight in selected["components"]:
        raw = (row.get(field) or "").strip()
        component = {
            "field": field,
            "raw": raw or None,
            "source": None,
            "evidence_type": None,
            "checked_at": None,
            "confidence": None,
            "weight": weight,
            "score": None,
        }
        if not raw:
            missing.append(field)
        else:
            try:
                numeric = float(raw)
            except ValueError:
                missing.append(field)
            else:
                if 1 <= numeric <= 5:
                    component["score"] = numeric
                    component["source"] = row.get(f"{field}_source") or None
                    component["evidence_type"] = row.get(f"{field}_evidence_type") or None
                    component["checked_at"] = row.get(f"{field}_checked_at") or None
                    component["confidence"] = row.get(f"{field}_confidence") or None
                    if not all(
                        component[key]
                        for key in ("source", "evidence_type", "checked_at", "confidence")
                    ):
                        missing.append(field)
                else:
                    missing.append(field)
        components[label] = component

    formula = " + ".join(f"{weight:.0%} {label}" for label, _field, weight in selected["components"])
    if missing:
        return {
            "value": None,
            "status": "Insufficient Evidence",
            "formula": formula,
            "components": components,
            "missing_inputs": sorted(set(missing)),
        }

    value = sum(component["score"] * component["weight"] for component in components.values())
    return {
        "value": round(value, 2),
        "status": "Comparable",
        "formula": formula,
        "components": components,
        "missing_inputs": [],
    }

def enrich(rows):
    for row in rows:
        row["overall_confidence"] = overall_confidence(row.get("source_confidence", ""))
        row["confidence_note"] = row.get("source_confidence", "")
        caps = {}
        for key, label in FEATURES:
            note = row.get(key, "")
            status = text_status(note)
            caps[key] = {
                "label": label,
                "status": status,
                "delivery_type": delivery_type(key, status, note),
                "evidence_url": first_source(row) if status in ("Confirmed", "Partial") else "",
                "checked_at": row.get("last_checked", ""),
                "note": note or "No researched note in canonical tracker.",
                "confidence": confidence(row, status),
            }
        row["capabilities"] = caps
        score_result = relationship_score(row)
        row["relationship_score"] = score_result["value"]
        row["score_status"] = score_result["status"]
        row["score_formula"] = score_result["formula"]
        row["score_components"] = score_result["components"]
        row["score_missing_inputs"] = score_result["missing_inputs"]
    return rows

def nav(active, prefix=""):
    items = [
        ("index.html", "Evidence Status"),
        ("alternative-workflows.html", "Alternative Workflows"),
        ("priority-competitors.html", "Priority Competitors"),
        ("research-table.html", "Full Research Table"),
        ("category-analysis.html", "Category Analysis"),
        ("sources-methodology.html", "Sources & Methodology"),
        ("archive.html", "Archive"),
    ]
    return '<div class="nav">' + "".join(
        f'<a class="{"active" if label == active else ""}" href="{prefix}{href}">{label}</a>' for href, label in items
    ) + "</div>"

def page(title, active, body, subtitle="", prefix="", data_prefix="../../"):
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/><meta content="width=device-width, initial-scale=1" name="viewport"/><title>{escape(title)}</title><link rel="icon" href="data:,"><link href="{prefix}style.css" rel="stylesheet"/></head><body>
<header class="site-header"><div class="header-inner"><h1>{escape(title)}</h1><p>{escape(subtitle)}</p>{nav(active, prefix)}</div></header>
<main>{body}<p class="footer">Canonical sources are separated by scope: <a href="{data_prefix}data/competitive-research-tracker.csv">competitor tracker</a> for the 36-company research and <a href="{data_prefix}data/substitutes-research.csv">substitutes research</a> with linked <a href="{data_prefix}data/substitute-evidence.csv">evidence</a> and <a href="{data_prefix}data/substitute-workflows.csv">workflow stages</a>. Technical reconciliation: {RECONCILIATION_DATE}.</p></main></body></html>"""

def confidence_badge(text):
    t = escape(overall_confidence(text) if text not in ("High", "Medium", "Low") else text)
    klass = "confidence-high" if t == "High" else "confidence-low" if t == "Low" else "confidence-medium"
    return f'<span class="badge {klass}">{t}</span>'

def relationship_badge(rel):
    return f'<span class="badge rel-{slug(rel)}">{escape(rel)}</span>'

def status_badge(status, planned=False):
    label = "Planned for BizMatch" if planned else status
    klass = "status-planned" if planned else f"status-{slug(status)}"
    return f'<span class="badge {klass}">{escape(label)}</span>'

def status_rank(status):
    return {"Confirmed": 3, "Partial": 2, "Planned for BizMatch": 2, "Not found": 1, "Not applicable": 0}.get(status, 0)

def one_sentence(text, fallback="Research note not available."):
    text = re.sub(r"\s+", " ", (text or "").strip())
    if not text:
        return fallback
    parts = re.split(r"(?<=[.!?])\s+", text)
    return parts[0][:240]

def row_strength(row):
    if row.get("bizmatch_lesson"):
        return row["bizmatch_lesson"]
    return one_sentence(row.get("secondary_capabilities") or row.get("notes"), "Clear capability evidence exists in the tracker.")

def row_weakness(row):
    if row.get("important_clarification"):
        return row["important_clarification"]
    note = row.get("notes", "")
    if "weak" in note.lower():
        return one_sentence(note[note.lower().find("weak"):])
    if row.get("contradictions"):
        return one_sentence(row.get("contradictions"))
    return one_sentence(row.get("unsupported_claims"), "Main gap requires deeper validation.")

def stage_status(row, stage_key, feature_key):
    if feature_key is None:
        covered = [stage_status(row, k, f) for k, _label, f in JOURNEY_STAGES if f]
        covered_count = sum(1 for s in covered if s in ("Confirmed", "Partial"))
        return "Confirmed" if covered_count >= 8 else "Partial" if covered_count >= 4 else "Not found"
    status = row["capabilities"][feature_key]["status"]
    if stage_key in ("conversation", "collaboration") and status == "Confirmed":
        note = row["capabilities"][feature_key]["note"].lower()
        if not any(x in note for x in ("structured", "prompt", "collaboration", "crm", "updates", "workspace", "brief")):
            return "Partial"
    return status

def coverage_matrix(rows):
    selected = [next(r for r in rows if r["company"] == name) for name in PRIORITY_ORDER]
    head = "".join(f"<th>{escape(label)}</th>" for _key, label, _feature in JOURNEY_STAGES)
    comp_rows = []
    for r in selected:
        cells = []
        for stage_key, label, feature_key in JOURNEY_STAGES:
            st = stage_status(r, stage_key, feature_key)
            note = "Not found is an evidence gap, not proof the feature does not exist." if st == "Not found" else (r["capabilities"][feature_key]["note"] if feature_key else "Derived from the count of evidenced journey-stage capabilities in the canonical tracker.")
            cells.append(f'<td data-label="{escape(label)}" class="status-cell">{status_badge(st)}<small>{escape(one_sentence(note))}</small></td>')
        comp_rows.append(f'<tr><th><a href="companies/{slug(r["company"])}.html">{escape(r["company"])}</a></th>{"".join(cells)}</tr>')
    biz_cells = "".join(f'<td data-label="{escape(label)}" class="status-cell planned-cell">{status_badge("Planned for BizMatch", planned=True)}<small>Intended product design, not competitor evidence.</small></td>' for _key, label, _feature in JOURNEY_STAGES)
    comp_rows.append(f'<tr class="bizmatch-row"><th>BizMatch intended design</th>{biz_cells}</tr>')
    legend = "".join(status_badge(s) for s in ["Confirmed", "Partial", "Not found", "Not applicable"]) + status_badge("Planned for BizMatch", planned=True)
    return f"""
<section class="panel" id="coverage-matrix"><h2>Competitive-Coverage Matrix</h2>
<p class="muted">Built from capability evidence in the canonical tracker. Not found means the research did not find support for a capability; it is not proof that the feature does not exist.</p>
<div class="legend">{legend}</div>
<div class="table-wrap matrix-wrap"><table class="coverage-table"><thead><tr><th>Company</th>{head}</tr></thead><tbody>{"".join(comp_rows)}</tbody></table></div></section>"""

def roadmap_table():
    rows = "".join(
        f"<tr><th>{escape(priority)}</th><td>{escape(hypothesis)}</td><td>{escape(feature)}</td><td>{escape(primary)}</td><td>{escape(supporting)}</td><td>{escape(failure)}</td><td>{escape(phase)}</td></tr>"
        for priority, hypothesis, feature, primary, supporting, failure, phase in VALIDATION_ROADMAP
    )
    return f'<div class="table-wrap"><table><thead><tr><th>Priority</th><th>Strategic hypothesis</th><th>Feature or experiment</th><th>Primary metric</th><th>Supporting metric</th><th>Failure signal</th><th>Recommended phase</th></tr></thead><tbody>{rows}</tbody></table></div>'

def historical_strategic_page(rows):
    groups = {rel: [r for r in rows if r["competitive_relationship"] == rel] for rel in RELATION_ORDER}
    priority_cards = "".join(priority_card(next(r for r in rows if r["company"] == name), compact=True) for name in PRIORITY_ORDER)
    implications = [
        "Swipe is an interface mechanism, not durable differentiation.",
        "AI matching must explain why two sides fit, not only display a score.",
        "NDA alone is not the product; the product value is the progression from match to qualified disclosure and meeting.",
        "AI pitch-deck review is a supporting feature, not the core product.",
        "Network effects are the central strategic risk.",
        "Use an external signing or secure-document provider in the MVP instead of building enterprise data-room infrastructure.",
    ]
    not_yet = ["Full enterprise data room.", "Cap table system.", "In-platform investment execution.", "Self-built e-signature infrastructure.", "AI expansion not connected to the core workflow."]
    win_not = ["Swipe alone.", "Generic founder discovery.", "A large investor directory.", "Pitch-deck scoring alone.", "NDA signing alone.", "Enterprise data-room depth."]
    win_can = ["A curated Israeli founder network.", "Higher-quality and explained matching.", "Trust and verification.", "Structured progression after the match.", "Controlled project disclosure.", "Match-to-meeting continuity.", "Local ecosystem partnerships."]
    differentiation = ["Matching combined with project profiles.", "Mutual-match workflow.", "Structured business conversation.", "Access request.", "NDA before private disclosure.", "Controlled project disclosure.", "Meeting and due-diligence preparation."]
    defensibility = ["Local network density.", "Verified founder and investor identities.", "Reputation accumulated across interactions.", "Behavioural matching and collaboration data.", "Trust signals from completed interactions.", "Access and disclosure history.", "Partnerships with universities, accelerators, angels, and founder communities.", "Data generated across the match-to-collaboration funnel."]
    open_decisions = ["Exact founder segment.", "Technical vs. non-technical founder balance.", "Whether investors enter in the first or second launch phase.", "Industry scope.", "Geographic scope beyond Israel.", "Verification requirements.", "First acquisition partners."]
    cold_start = ["Recruit a curated founder/co-founder cohort.", "Verify and improve profiles manually.", "Guarantee a minimum number of relevant recommendations.", "Measure match quality and response rate.", "Add invited mentors and angels.", "Introduce project disclosure and NDA flows.", "Expand only after local match liquidity reaches an acceptable level."]
    body = f"""
<section class="panel warning-panel"><h2>ARCHIVED — not current investor conclusions</h2><p>This page is preserved only as an audit copy of the pre-Phase-0 strategic narrative. Phase 0 did not re-run White Space, MVP, Build/Buy, launch-sequence, or strategy research. Previous numeric threat scores are deprecated. Nothing below is an approved or score-backed recommendation.</p></section>
<section class="hero-panel">
  <p class="eyebrow">Executive summary</p>
  <h2>Historical hypothesis: no single researched competitor appeared to own the full BizMatch journey.</h2>
  <p>The prior analysis observed that most researched companies solve one slice. Its proposed opening is retained for future validation, not asserted as a verified White Space conclusion.</p>
  <p class="positioning">BizMatch connects founders, partners, and investors and manages the journey from initial compatibility to a verified, protected, and structured business collaboration.</p>
  <div class="journey">Discovery <span>-></span> Mutual Match <span>-></span> Structured Conversation <span>-></span> Access Request <span>-></span> NDA <span>-></span> Controlled Disclosure <span>-></span> Meeting <span>-></span> Collaboration</div>
</section>
<section class="panel decision-panel"><h2>Where BizMatch Can Win</h2><div class="split-grid"><div><h3>Do not try to win through</h3><ul class="clean-list">{"".join(f"<li>{escape(x)}</li>" for x in win_not)}</ul></div><div><h3>Potential opening</h3><ul class="clean-list">{"".join(f"<li>{escape(x)}</li>" for x in win_can)}</ul></div></div></section>
{coverage_matrix(rows)}
<section class="panel"><h2>Differentiation vs. Defensibility</h2><div class="split-grid"><div><h3>Current product differentiation</h3><ul class="clean-list">{"".join(f"<li>{escape(x)}</li>" for x in differentiation)}</ul></div><div><h3>Potential long-term defensibility BizMatch must build</h3><ul class="clean-list">{"".join(f"<li>{escape(x)}</li>" for x in defensibility)}</ul></div></div><p class="warning-callout">Workflow integration is differentiation, but it is not automatically a moat. Defensibility must be created through network density, trust, proprietary interaction data, and ecosystem partnerships.</p></section>
<section class="panel"><h2>Recommended Israeli Beachhead</h2><p><strong>Recommended hypothesis:</strong> Israeli pre-seed and first-time founders seeking a co-founder, especially founders seeking a technical or product partner.</p><div class="split-grid"><div><h3>Initial supply strategy</h3><ul class="clean-list"><li>Recruit founders through Israeli universities, accelerators, entrepreneurship programs, reserve-service networks, and startup communities.</li><li>Build a curated initial cohort rather than opening a completely unfiltered marketplace.</li><li>Prioritize quality and response rate over total registrations.</li><li>Introduce investors only after the platform contains enough complete and credible projects.</li></ul></div><div><h3>Initial investor role</h3><ul class="clean-list"><li>Begin with a small invited group of angels and mentors.</li><li>Use them for project feedback, validation, and selected introductions.</li><li>Do not depend on a large investor marketplace in the first launch.</li></ul></div></div></section>
<section class="panel"><h2>Priority Competitors</h2><p class="muted">Short homepage summary. The dedicated page expands the counter-positioning and evidence.</p><div class="priority-grid">{priority_cards}</div></section>
<section class="panel"><h2>Strategic Implications</h2><ul class="clean-list">{"".join(f"<li>{escape(x)}</li>" for x in implications)}</ul></section>
<section class="panel"><h2>Cold-Start and Network Strategy</h2><div class="brief-grid"><article><h3>Which side enters first?</h3><p>Founders/co-founder seekers enter first through a curated cohort.</p></article><article><h3>Which side is scarce?</h3><p>High-quality technical/product co-founder candidates and credible projects are the scarce supply.</p></article><article><h3>First 100 qualified users</h3><p>Recruit through named local partners, founder communities, reserve-service networks, accelerators, and universities.</p></article><article><h3>Avoid empty feeds</h3><p>Manual profile review, curated recommendation batches, and minimum relevant-match guarantees before broad opening.</p></article><article><h3>Why not LinkedIn, WhatsApp, YC, or communities?</h3><p>BizMatch must offer curated fit, explained recommendations, trust checks, and structured movement toward disclosure and meetings.</p></article><article><h3>When investors enter</h3><p>After credible project supply exists, starting with invited mentors and angels for feedback and selected introductions.</p></article><article><h3>Expansion metrics</h3><p>Median time to first relevant match, acceptance rate, response rate, match-to-meeting conversion, and referral/invitation rate.</p></article></div><h3>Proposed launch sequence</h3><ol class="clean-list numbered">{"".join(f"<li>{escape(x)}</li>" for x in cold_start)}</ol></section>
<section class="panel"><h2>Validation Roadmap</h2>{roadmap_table()}</section>
<section class="panel"><h2>What Not To Build Yet</h2><ul class="clean-list">{"".join(f"<li>{escape(x)}</li>" for x in not_yet)}</ul></section>
<section class="panel warning-panel"><h2>Open Decisions</h2><ul class="clean-list">{"".join(f"<li>{escape(x)}</li>" for x in open_decisions)}</ul></section>
<section class="panel"><h2>Research Limitations</h2><p>Not found is not proof that a feature does not exist. Several traction and funding claims are company-reported or secondary-source claims. See <a href="sources-methodology.html">Sources & Methodology</a> for the scoring rubric, source-of-truth rules, and research backlog.</p></section>
"""
    return page(
        "Historical Strategic Hypotheses — Archived",
        "Archive",
        body,
        "Audit material only; not an investor-facing conclusion or approved launch plan.",
    )


def evidence_status_page(rows):
    body = f"""
<section class="panel warning-panel"><h2>No current strategic recommendation is published</h2>
<p>Phase 0 established data integrity; it did not validate White Space, an Israeli beachhead, MVP scope, Build/Buy choices, or a launch sequence. Those topics require separate approved research before they can be presented as conclusions.</p></section>
<section class="hero-panel">
  <p class="eyebrow">Phase 0 integrity · Phase 1 substitute evidence</p>
  <h2>{len(rows)} canonical company records are available for evidence review.</h2>
  <p>The competitor tracker remains isolated. Phase 1 adds a separate canonical substitute layer for behavior, evidence, and four Job workflows. Numeric relationship and threat rankings remain paused because the required sourced inputs are incomplete.</p>
</section>
<section class="panel"><h2>Safe current uses</h2><ul class="clean-list">
  <li>Review recorded competitor facts and their source confidence.</li>
  <li>Inspect capability evidence and explicit research gaps.</li>
  <li>Review how users combine networks, services, manual work, infrastructure, and non-adoption.</li>
  <li>Audit reconciled conflicts and unresolved findings.</li>
</ul><div class="archive-list"><a href="alternative-workflows.html">Open alternative workflows</a><a href="research-table.html">Open the canonical research table</a><a href="category-analysis.html">Review evidence groups without ranking</a><a href="sources-methodology.html">Read sources and methodology</a></div></section>
<section class="panel"><h2>Not approved for investor presentation</h2><ul class="clean-list">
  <li>White Space claims or claims that BizMatch owns an unserved journey.</li>
  <li>Recommended market beachhead, launch sequence, or first-user acquisition plan.</li>
  <li>MVP priorities, Build/Buy recommendations, or defensibility claims.</li>
  <li>Numeric threat or relationship rankings.</li>
</ul><p>Historical strategic material is retained only in the Archive for audit and is intentionally excluded from this active page.</p></section>
"""
    return page(
        "Evidence Status",
        "Evidence Status",
        body,
        "Canonical research evidence and the conclusions that remain unvalidated.",
    )

def priority_card(row, compact=False):
    if compact:
        return f"""
<article class="priority-card">
  <h3><a href="companies/{slug(row['company'])}.html">{escape(row['company'])}</a></h3>
  <p>{relationship_badge(row['competitive_relationship'])} {confidence_badge(row.get('overall_confidence',''))}</p>
  <p>{escape(row.get('plain_language_description') or row.get('notes',''))}</p>
</article>"""
    return f"""
<article class="priority-card">
  <h3><a href="companies/{slug(row['company'])}.html">{escape(row['company'])}</a></h3>
  <p>{relationship_badge(row['competitive_relationship'])} {confidence_badge(row.get('overall_confidence',''))}</p>
  <dl class="mini-dl"><dt>What it is</dt><dd>{escape(row.get('plain_language_description') or row.get('notes',''))}</dd><dt>Primary job</dt><dd>{escape(row.get('primary_job_solved') or row.get('bizmatch_jobs_competed_for',''))}</dd><dt>Lesson</dt><dd>{escape(row.get('bizmatch_lesson',''))}</dd><dt>Do not copy</dt><dd>{escape(row.get('do_not_copy',''))}</dd></dl>
</article>"""

def priority_page(rows):
    selected = [next(r for r in rows if r["company"] == name) for name in PRIORITY_ORDER]
    compare_rows = "".join(
        f"<tr><th><a href='#pc-{slug(r['company'])}'>{escape(r['company'])}</a></th><td>{relationship_badge(r['competitive_relationship'])}</td><td>{escape(r.get('primary_job_solved') or r.get('bizmatch_jobs_competed_for',''))}</td><td>Insufficient Evidence</td><td>{confidence_badge(r.get('overall_confidence',''))}</td></tr>"
        for r in selected
    )
    sections = []
    for r in selected:
        coverage = "".join(
            f"<li><strong>{escape(label)}:</strong> {escape(stage_status(r, key, feature))}</li>"
            for key, label, feature in JOURNEY_STAGES
        )
        sections.append(f"""
<section class="panel competitor-deep" id="pc-{slug(r['company'])}">
  <h2>{escape(r['company'])}</h2>
  <p>{relationship_badge(r['competitive_relationship'])} {confidence_badge(r.get('overall_confidence',''))} <span class="score-pill">Insufficient Evidence</span></p>
  <div class="profile-card quick-read"><h3>Product model</h3><dl class="field-grid"><dt>What it is</dt><dd>{escape(r.get('plain_language_description') or r.get('notes',''))}</dd><dt>Who uses it</dt><dd>{escape(r.get('target_users',''))}</dd><dt>Primary job solved</dt><dd>{escape(r.get('primary_job_solved') or r.get('bizmatch_jobs_competed_for',''))}</dd><dt>How it works</dt><dd>{escape(r.get('product_model') or r.get('product_category',''))}</dd><dt>Why it matters to BizMatch</dt><dd>{escape(r.get('bizmatch_lesson',''))}</dd><dt>Important clarification</dt><dd>{escape(r.get('important_clarification') or row_weakness(r))}</dd></dl></div>
  <div class="split-grid"><div><dl class="field-grid"><dt>Competitive relationship</dt><dd>{escape(r['competitive_relationship'])}</dd><dt>Primary category</dt><dd>{escape(r['primary_category'])}</dd><dt>Secondary capabilities</dt><dd>{escape(r['secondary_capabilities'])}</dd><dt>Evidence-backed traction</dt><dd>{escape(r.get('users_traction',''))}</dd><dt>Pricing model</dt><dd>{escape(r.get('pricing_model',''))}</dd><dt>Important weaknesses or gaps</dt><dd>{escape(row_weakness(r))}</dd></dl></div><div><h3>Relevant workflow coverage</h3><ul class="clean-list">{coverage}</ul></div></div>
  <div class="split-grid"><div><h3>What BizMatch should learn</h3><p>{escape(r.get('bizmatch_lesson',''))}</p><h3>What BizMatch should not copy</h3><p>{escape(r.get('do_not_copy',''))}</p><h3>Historical counter-positioning hypothesis</h3><p>Retained for future validation; Phase 0 did not re-run strategic analysis.</p></div><aside class="score-box"><h3>Relationship score</h3><p><strong>Insufficient Evidence</strong></p><p class="muted">Missing explicit, sourced component inputs. This company is not ranked.</p></aside></div>
  <h3>Sources</h3><div class="source-grid">{source_cards(r, 'Priority-competitor claims, traction, pricing, and workflow coverage')}</div>
</section>""")
    body = f"""
<section class="panel warning-panel"><h2>Priority list status</h2><p>This is the pre-existing editorial review list, not a score-based ranking. Phase 0 retained its scope but removed numeric threat bands because explicit score inputs are missing.</p></section>
<section class="panel"><h2>Priority Competitors</h2><div class="table-wrap"><table><thead><tr><th>Company</th><th>Relationship</th><th>Job solved</th><th>Score status</th><th>Confidence</th></tr></thead><tbody>{compare_rows}</tbody></table></div></section>
{"".join(sections)}"""
    return page("Priority Competitors", "Priority Competitors", body, "Pre-existing review scope with score status and evidence.")

def research_table(rows):
    table_rows = []
    for idx, r in enumerate(rows):
        links = urls(r.get("primary_sources", ""))[:2] + urls(r.get("secondary_sources", ""))[:1]
        company_text = " ".join([
            r["company"],
            r.get("primary_category",""),
            r.get("primary_job_solved",""),
            r.get("plain_language_description",""),
            r.get("product_model",""),
            r.get("important_clarification",""),
        ])
        capability_text = " ".join(c["label"] + " " + c["status"] + " " + c["note"] for c in r["capabilities"].values())
        evidence_text = " ".join(str(v) for k, v in r.items() if isinstance(v, str) and k not in ("company", "primary_category", "bizmatch_jobs_competed_for"))
        caps = "".join(f"<li><strong>{escape(c['label'])}:</strong> {escape(c['status'])} - {escape(one_sentence(c['note']))}</li>" for c in r["capabilities"].values())
        table_rows.append(f"""<tr class="company-row" data-row-id="{idx}" data-company-name="{escape(r['company'].lower())}" data-companies-search="{escape(company_text.lower())}" data-capabilities-search="{escape(capability_text.lower())}" data-evidence-search="{escape(evidence_text.lower())}" data-relationship="{escape(r['competitive_relationship'])}" data-confidence="{escape(r.get('overall_confidence',''))}">
<td><a class="company-link" href="companies/{slug(r['company'])}.html">{escape(r['company'])}</a><div class="match-note" aria-live="polite"></div></td>
<td>{relationship_badge(r['competitive_relationship'])}</td>
<td>{escape(r['primary_category'])}</td>
<td>{escape(r.get('primary_job_solved') or r['bizmatch_jobs_competed_for'])}</td>
<td><span class="score-pill">Insufficient Evidence</span></td>
<td>{confidence_badge(r.get('overall_confidence',''))}</td>
<td>{escape(row_strength(r))}</td>
<td>{escape(row_weakness(r))}</td>
<td><a href="companies/{slug(r['company'])}.html">Open profile</a></td>
</tr>
<tr class="detail-row" data-detail-for="{idx}"><td colspan="9"><details><summary>Research details</summary><div class="split-grid"><dl class="field-grid"><dt>What it is</dt><dd>{escape(r.get('plain_language_description',''))}</dd><dt>Product model</dt><dd>{escape(r.get('product_model',''))}</dd><dt>Important clarification</dt><dd>{escape(r.get('important_clarification',''))}</dd><dt>Target users</dt><dd>{escape(r.get('target_users',''))}</dd><dt>Funding</dt><dd>{escape(r.get('total_funding',''))}</dd><dt>Traction</dt><dd>{escape(r.get('users_traction',''))}</dd><dt>Confidence note</dt><dd>{escape(r.get('confidence_note',''))}</dd><dt>Score status</dt><dd>Insufficient Evidence — missing: {escape(', '.join(r['score_missing_inputs']))}</dd><dt>Unsupported claims</dt><dd>{escape(r.get('unsupported_claims',''))}</dd><dt>Contradictions</dt><dd>{escape(r.get('contradictions',''))}</dd><dt>Sources</dt><dd>{" ".join(source_anchor(u) for u in links)}</dd></dl><div><h3>Capability evidence</h3><ul class="clean-list">{caps}</ul></div></div></details></td>
</tr>""")
    filters = "".join(f'<option value="{escape(rel)}">{escape(rel)}</option>' for rel in RELATION_ORDER)
    body = f"""
<section class="panel"><h2>Filters</h2><div class="controls"><div><label for="search">Search</label><input id="search" placeholder="CoffeeSpace, NDA, Israel, pitch deck..."></div><div><label for="searchScope">Search scope</label><select id="searchScope"><option value="all">All</option><option value="companies">Companies</option><option value="capabilities">Capabilities</option><option value="evidence">Evidence</option></select></div><div><label for="relationshipFilter">Competition type</label><select id="relationshipFilter"><option value="">All</option>{filters}</select></div><div><label for="confidenceFilter">Confidence</label><select id="confidenceFilter"><option value="">All</option><option>High</option><option>Medium</option><option>Low</option></select></div><div><label>&nbsp;</label><button class="secondary" id="resetFilters">Reset</button></div></div></section>
<section class="panel warning-panel"><h2>Numeric ranking paused</h2><p>The canonical schema does not yet contain the explicit, sourced inputs required by the documented relationship-score formulas. Missing data is not assigned a default; every company is therefore shown as Insufficient Evidence and is not ranked.</p></section>
<section class="panel"><h2>Full Research Table <span class="muted">(<span id="visibleCount">{len(rows)}</span> visible)</span></h2><p class="muted">Expand a row or open the company profile for funding, traction, sources, capability evidence, contradictions, unsupported claims, and missing score inputs.</p><div class="table-wrap"><table id="researchTable"><thead><tr><th>Company</th><th>Competitive relationship</th><th>Primary category</th><th>Main job competed for</th><th>Relationship score</th><th>Overall confidence</th><th>One key strength</th><th>One key weakness</th><th>Profile link</th></tr></thead><tbody>{"".join(table_rows)}</tbody></table></div></section>
<script src="app.js"></script>"""
    return page("Full Research Table", "Full Research Table", body, "Canonical tracker table with strategic relationship filters and source-linked claims.")

def category_page(rows):
    blocks = []
    for rel in RELATION_ORDER:
        rs = [r for r in rows if r["competitive_relationship"] == rel]
        formula = rs[0]["score_formula"] if rs else ""
        cards = "".join(f'<article class="category-card"><h3><a href="companies/{slug(r["company"])}.html">{escape(r["company"])}</a></h3><p>{confidence_badge(r.get("overall_confidence",""))} <span class="score-pill">Insufficient Evidence</span></p><p>{escape(one_sentence(r.get("plain_language_description") or r.get("notes"), r["bizmatch_jobs_competed_for"]))}</p><p class="muted"><strong>Job:</strong> {escape(r.get("primary_job_solved") or r["bizmatch_jobs_competed_for"])}</p></article>' for r in rs)
        blocks.append(f'<section class="panel"><h2>{escape(rel)}</h2><p class="muted"><strong>Preserved analytical weights:</strong> {escape(formula)}. No ranking is produced until every required component has an explicit value and evidence metadata.</p><div class="category-grid">{cards}</div></section>')
    return page("Category Analysis", "Category Analysis", "".join(blocks), "Relationship groups shown without unsupported numeric rankings.")

def methodology_page(rows):
    limitations = [
        "Some traction data is self-reported by the companies.",
        "Registered users are not the same as active users.",
        "Company funding is different from capital raised through a platform.",
        "Prices may change after the checked date.",
        "Not found does not mean a capability does not exist.",
        "Secondary-source information is marked as lower-confidence context where applicable.",
        "Data behind a paywall is not treated as fully verified.",
    ]
    backlog = [
        "App Store and Google Play reviews.",
        "G2, Capterra, Product Hunt, and Reddit reviews.",
        "Active users rather than registered users only.",
        "Mystery shopping and complete onboarding flows.",
        "Quality and supply of profiles in Israel.",
        "Time to first match.",
        "Conversion from match to conversation and meeting.",
        "Identity and investor verification mechanisms.",
        "Reporting, blocking, moderation, and fraud prevention.",
        "Document permissions, revoke access, watermark, and audit log.",
        "Israeli ecosystem: accelerators, angels, universities, and founder communities.",
    ]
    formula_blocks = []
    for rel in RELATION_ORDER:
        sample = next((r for r in rows if r["competitive_relationship"] == rel), None)
        if sample:
            formula_blocks.append(f"<article class='category-card'><h3>{escape(rel)}</h3><p>{escape(sample['score_formula'])}</p></article>")
    rubric_rows = "".join(
        f"<tr><th>{escape(name)}</th><td>{escape(v1)}</td><td>{escape(v3)}</td><td>{escape(v5)}</td></tr>"
        for name, (v1, v3, v5) in RUBRIC.items()
    )
    body = f"""
<section class="panel"><h2>Separated Canonical Sources</h2><p><a href="../../data/competitive-research-tracker.csv">data/competitive-research-tracker.csv</a> is the only active source for the 36-company competitor research. The XLSX, generated site data, tables, company profiles, category pages, source pages, and report notices are derived from it.</p><p>Phase 1 has a separate normalized source of truth: <a href="../../data/substitutes-research.csv">substitute entities</a>, <a href="../../data/substitute-evidence.csv">claim-level evidence</a>, and <a href="../../data/substitute-workflows.csv">Job-stage workflows</a>. They generate <a href="alternative-workflows.html">How Users Solve It Today</a> and the Phase 1 registers; they never write into or rank the competitor tracker. Generators never write back to canonical CSVs.</p><p>Historical cited datasets are kept under <code>archive/data/</code>. Production code does not read them.</p></section>
<section class="panel"><h2>Substitute Evidence Method</h2><p>Each material claim is linked to a source record and labeled as Independent Behavioral Evidence, Independent User Report, Independent Market Evidence, Company Documentation, Company Claim, Community Discussion, Anecdotal Evidence, Inference, or Unverified. Existence, observed use, effectiveness, satisfaction, search for an alternative, and willingness to pay or change behavior are separate evidence dimensions.</p><p>Phase 1 publishes only qualitative substitute strength. Missing evidence stays Unverified / Insufficient Evidence; no numeric threat score, White Space, market-gap, MVP, product-market-fit, or Build/Buy conclusion is produced.</p></section>
<section class="panel"><h2>Strategic Classification Rules</h2><ul class="clean-list"><li><strong>Direct competitor:</strong> competes for a core BizMatch discovery or matching workflow.</li><li><strong>Substitute / network threat:</strong> solves an adjacent job and has unusually strong network, brand, or ecosystem pull.</li><li><strong>Substitute:</strong> solves an adjacent job users could choose instead of BizMatch.</li><li><strong>Feature benchmark:</strong> helps evaluate a supporting capability but is not the full product category.</li><li><strong>Infrastructure / potential partner:</strong> can support signing, disclosure, security, or data-room needs without being the core network.</li></ul></section>
<section class="panel warning-panel"><h2>Relationship score status</h2><p>Numeric scoring is paused. The weights below are preserved analytical choices that require approval; the required explicit component fields and per-input evidence metadata are absent from the current 65-column schema. Missing inputs return null / Insufficient Evidence, never a default number.</p></section>
<section class="panel"><h2>Preserved Segmented Weights</h2><div class="category-grid">{"".join(formula_blocks)}</div></section>
<section class="panel"><h2>Legacy Rubric — Deprecated Audit Context</h2><p class="muted">These anchors describe the historical model only. Legacy columns remain in the canonical CSV for audit but do not feed the site, rankings, or conclusions.</p><div class="table-wrap"><table><thead><tr><th>Dimension</th><th>1 meant</th><th>3 meant</th><th>5 meant</th></tr></thead><tbody>{rubric_rows}</tbody></table></div></section>
<section class="panel"><h2>Research Limitations</h2><ul class="clean-list">{"".join(f"<li>{escape(x)}</li>" for x in limitations)}</ul></section>
<section class="panel"><h2>Research Backlog</h2><ol class="clean-list numbered">{"".join(f"<li>{escape(x)}</li>" for x in backlog)}</ol></section>
<section class="panel"><h2>Capability Verification Model</h2><p>Capabilities are displayed as Confirmed, Partial, Not found, or Not applicable. Confirmed requires direct support in the canonical tracker's cited notes. Partial is used for limited analogs or marketing-level evidence. Not found is transparent uncertainty, not a negative factual claim.</p></section>"""
    return page("Sources & Methodology", "Sources & Methodology", body, "Separated canonical sources, evidence method, scoring limits, and follow-up backlog.")

def archive_page():
    body = """
<section class="panel"><h2>Archived Material</h2><p>The old cited datasets, generated reports, and strategic hypotheses are audit material only. Production code does not read them as canonical facts or active conclusions.</p><div class="archive-list"><a href="strategic-conclusions-historical.html">Historical strategic hypotheses — not current investor conclusions</a><a href="../../archive/data/bizmatch-competitive-research-cited.csv">Archived cited CSV</a><a href="../../archive/data/bizmatch-competitive-research-cited.xlsx">Archived cited XLSX</a><a href="../../reports/bizmatch-competitive-research-cited-report.html">Archived old cited report HTML</a><a href="../../reports/bizmatch-competitive-research-cited-report.md">Archived old cited report Markdown</a><a href="../../reports/competitive-research-tracker-preview.html">Archived tracker preview</a></div></section>
<section class="panel warning-panel"><h2>Known Archived Errors</h2><ul class="clean-list"><li>Cherub's $45K customer testimonial was misread as company funding.</li><li>CoffeeSpace's customer qualification threshold of $10M raised was misread as CoffeeSpace funding.</li><li>Swipe Invest's $45B European market statistic was misread as company funding.</li><li>Digify's platform/customer document-security figures were misread as funding.</li><li>Cofounder.org's '3 Matches' UI heading was misread as traction.</li><li>SWIP's target first cohort of 100 founders was misread as existing users.</li><li>SecureDocs and Carta pricing was mixed into funding or traction fields.</li></ul></section>
"""
    return page("Archive", "Archive", body, "Old generated reports kept out of the active research path.")

def company_page(row):
    caps = "".join(f"""<article class="cap-card"><h3>{escape(c['label'])}</h3><p><span class="badge status-{slug(c['status'])}">{escape(c['status'])}</span> <span class="badge">{escape(c['delivery_type'])}</span> {confidence_badge(c['confidence'])}</p><p>{escape(c['note'])}</p><p class="muted">Checked: {escape(c['checked_at'] or 'not recorded')} {source_anchor(c['evidence_url']) if c['evidence_url'] else ''}</p></article>""" for c in row["capabilities"].values())
    missing = ", ".join(row["score_missing_inputs"])
    body = f"""
<div class="profile-layout"><div>
<section class="profile-card"><h2>{escape(row['company'])}</h2><p>{relationship_badge(row['competitive_relationship'])} {confidence_badge(row.get('overall_confidence',''))}</p><dl class="field-grid"><dt>Primary category</dt><dd>{escape(row['primary_category'])}</dd><dt>Secondary capabilities</dt><dd>{escape(row['secondary_capabilities'])}</dd><dt>BizMatch jobs competed for</dt><dd>{escape(row['bizmatch_jobs_competed_for'])}</dd><dt>Status</dt><dd>{escape(row['current_status'])}</dd><dt>HQ / country</dt><dd>{escape(row['hq_country'])}</dd><dt>Target users</dt><dd>{escape(row['target_users'])}</dd><dt>Funding</dt><dd>{escape(row['total_funding'])}</dd><dt>Funding rounds</dt><dd>{escape(row['funding_rounds'])}</dd><dt>Traction</dt><dd>{escape(row['users_traction'])}</dd><dt>Confidence note</dt><dd>{escape(row.get('confidence_note',''))}</dd></dl></section>
<section class="profile-card"><h2>Strategic Positioning</h2><dl class="field-grid"><dt>What it is</dt><dd>{escape(row.get('plain_language_description',''))}</dd><dt>Primary job solved</dt><dd>{escape(row.get('primary_job_solved',''))}</dd><dt>Product model</dt><dd>{escape(row.get('product_model',''))}</dd><dt>BizMatch lesson</dt><dd>{escape(row.get('bizmatch_lesson',''))}</dd><dt>Do not copy</dt><dd>{escape(row.get('do_not_copy',''))}</dd><dt>Important clarification</dt><dd>{escape(row.get('important_clarification',''))}</dd></dl></section>
<section class="profile-card"><h2>Capability Evidence</h2><div class="cap-grid">{caps}</div></section>
<section class="profile-card"><h2>Evidence Notes</h2><dl class="field-grid"><dt>Research notes</dt><dd>{escape(row.get('notes',''))}</dd><dt>Unsupported claims</dt><dd>{escape(row.get('unsupported_claims',''))}</dd><dt>Contradictions corrected</dt><dd>{escape(row.get('contradictions',''))}</dd><dt>Last checked</dt><dd>{escape(row.get('last_checked',''))}</dd></dl></section>
<section class="profile-card"><h2>Sources</h2><div class="source-grid">{source_cards(row, 'Company profile, traction, pricing, funding, and capability evidence')}</div></section>
</div><aside class="sidebox"><h2>Relationship Score</h2><p><span class="score-pill large">N/A</span></p><p><strong>Insufficient Evidence</strong></p><p class="muted">Required inputs are absent; no default was applied and this company is not ranked.</p><details><summary>Missing inputs</summary><p>{escape(missing)}</p><p>{escape(row['score_formula'])}</p></details></aside></div>"""
    return page(row["company"], "Full Research Table", body, row["bizmatch_jobs_competed_for"], prefix="../", data_prefix="../../../")

def data_js(rows):
    public = []
    for r in rows:
        public.append({
            "company": r["company"],
            "url": r["url"],
            "profile": f"companies/{slug(r['company'])}.html",
            "source_category": r["source_category"],
            "competitive_relationship": r["competitive_relationship"],
            "primary_category": r["primary_category"],
            "secondary_capabilities": r["secondary_capabilities"],
            "bizmatch_jobs_competed_for": r["bizmatch_jobs_competed_for"],
            "plain_language_description": r["plain_language_description"],
            "primary_job_solved": r["primary_job_solved"],
            "product_model": r["product_model"],
            "bizmatch_lesson": r["bizmatch_lesson"],
            "do_not_copy": r["do_not_copy"],
            "important_clarification": r["important_clarification"],
            "source_confidence": r["source_confidence"],
            "overall_confidence": r["overall_confidence"],
            "confidence_note": r["confidence_note"],
            "relationship_score": r["relationship_score"],
            "score_status": r["score_status"],
            "score_formula": r["score_formula"],
            "score_components": r["score_components"],
            "score_missing_inputs": r["score_missing_inputs"],
            "capabilities": r["capabilities"],
        })
    return "window.BIZMATCH_RESEARCH = " + json.dumps({"source": "data/competitive-research-tracker.csv", "reconciled_at": RECONCILIATION_DATE, "companies": public}, ensure_ascii=False, indent=2) + ";\n"

def split_values(value):
    return [item.strip() for item in (value or "").split("|") if item.strip()]


def substitute_data_js(substitutes, evidence, workflows):
    payload = {
        "source": "data/substitutes-research.csv",
        "evidence_source": "data/substitute-evidence.csv",
        "workflow_source": "data/substitute-workflows.csv",
        "last_built_from_source": RECONCILIATION_DATE,
        "substitutes": substitutes,
        "evidence": evidence,
        "workflows": workflows,
    }
    return "window.BIZMATCH_SUBSTITUTES = " + json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
    ) + ";\n"


def substitute_badge(value):
    return f'<span class="badge substitute-{slug(value)}">{escape(value)}</span>'


def substitute_source_link(row):
    if not row.get("source_url"):
        return '<span class="empty">Unverified — no source recorded</span>'
    return (
        f'<a href="{escape(row["source_url"])}" target="_blank" rel="noopener">'
        f'{escape(row.get("source_title") or urlparse(row["source_url"]).netloc)}</a>'
    )


def substitutes_page(substitutes, evidence, workflows):
    evidence_by_id = {row["evidence_id"]: row for row in evidence}
    workflows_by_job = {
        job_id: sorted(
            [row for row in workflows if row["job_id"] == job_id],
            key=lambda row: int(row["stage_order"]),
        )
        for job_id in SUBSTITUTE_JOB_LABELS
    }
    substitutes_by_job = {
        job_id: [
            row
            for row in substitutes
            if job_id in split_values(row.get("job_to_be_done"))
        ]
        for job_id in SUBSTITUTE_JOB_LABELS
    }

    cards_by_job = []
    for job_id, job_label in SUBSTITUTE_JOB_LABELS.items():
        cards = []
        for row in substitutes_by_job[job_id]:
            source_types = sorted(
                {
                    evidence_by_id[evidence_id]["source_type"]
                    for evidence_id in split_values(row.get("evidence_ids"))
                    if evidence_id in evidence_by_id
                }
            )
            existing_link = ""
            if row.get("existing_competitor_slug"):
                existing_link = (
                    f'<p><a href="companies/{escape(row["existing_competitor_slug"])}.html">'
                    "Open linked canonical competitor record</a></p>"
                )
            cards.append(
                f"""<article class="substitute-card">
<h3>{escape(row['name'])}</h3>
<p>{substitute_badge(row['classification'])} {substitute_badge(row['substitute_strength'])} {confidence_badge(row['confidence'])}</p>
<dl class="mini-dl">
<dt>Category</dt><dd>{escape(row['category'])}</dd>
<dt>Current behavior</dt><dd>{escape(row['current_behavior'])}</dd>
<dt>Why chosen</dt><dd>{escape(row['why_users_choose_it'])}</dd>
<dt>Advantage</dt><dd>{escape(row['advantages'])}</dd>
<dt>Limitation</dt><dd>{escape(row['limitations'])}</dd>
<dt>Trust</dt><dd>{escape(row['trust_mechanism'])}</dd>
<dt>Switching cost</dt><dd>{escape(row['switching_cost'])}</dd>
<dt>Evidence types</dt><dd>{escape(', '.join(source_types) or row['source_type'] or 'Unverified')}</dd>
<dt>Status</dt><dd>{escape(row['research_status'])}</dd>
</dl>
<p class="source-note">{escape(row['evidence_summary'])}</p>
<p class="sources">{substitute_source_link(row)}</p>
{existing_link}</article>"""
            )
        cards_by_job.append(
            f'<section class="panel" id="{escape(job_id.lower())}"><h2>{escape(job_label)}</h2>'
            '<p class="muted">Alternatives are ordered by their canonical data order, not by a numeric rank.</p>'
            f'<div class="substitute-grid">{"".join(cards)}</div></section>'
        )

    workflow_sections = []
    for job_id, job_label in SUBSTITUTE_JOB_LABELS.items():
        rows = "".join(
            f"<tr><th>{escape(row['stage_order'])}. {escape(row['stage_id'])}</th>"
            f"<td>{escape(row['current_action'])}</td>"
            f"<td>{escape(row['tools_channels'])}</td>"
            f"<td>{escape(row['trust_requirement'])}</td>"
            f"<td>{escape(row['current_advantage'])}</td>"
            f"<td>{escape(row['current_limitation'])}</td>"
            f"<td>{escape(row['evidence_status'])} · {escape(row['confidence'])}</td></tr>"
            for row in workflows_by_job[job_id]
        )
        workflow_sections.append(
            f'<section class="panel"><h2>{escape(job_label)} — current workflow</h2>'
            '<div class="table-wrap"><table><thead><tr><th>Stage</th><th>Current action</th>'
            '<th>Tools / channels</th><th>Trust requirement</th><th>Advantage</th>'
            f'<th>Limitation</th><th>Evidence status</th></tr></thead><tbody>{rows}</tbody></table></div></section>'
        )

    evidence_cards = []
    for row in evidence:
        source_type = row["source_type"]
        source_warning = ""
        if source_type in {"Company Claim", "Company Documentation", "Inference", "Unverified"}:
            source_warning = (
                f'<p class="source-note">Interpretation boundary: {escape(source_type)} '
                "is displayed as labeled and is not independent proof of effectiveness.</p>"
            )
        evidence_cards.append(
            f"""<article class="source-card">
<h3>{escape(row['evidence_id'])} · {escape(row['claim_type'])}</h3>
<p>{substitute_badge(source_type)} {confidence_badge(row['confidence'])}</p>
<p><strong>Claim:</strong> {escape(row['claim'])}</p>
<p><strong>Dimension:</strong> {escape(row['evidence_dimension'])}</p>
<p><strong>Support:</strong> {escape(row['supporting_excerpt_or_summary'])}</p>
<p><strong>Limitation:</strong> {escape(row['limitation'])}</p>
<p class="sources">{substitute_source_link(row)}</p>
{source_warning}</article>"""
        )

    unverified = sum(1 for row in substitutes if row["research_status"] == "Unverified")
    body = f"""
<section class="panel warning-panel"><h2>Evidence boundary</h2>
<p>This Phase 1 view documents how people can solve the Jobs today. It does not assert product-market fit, a strategic opportunity, an MVP priority, or a Build/Buy recommendation. Company documentation establishes capabilities or claims only; it is not relabeled as independent behavior.</p></section>
<section class="hero-panel"><p class="eyebrow">Phase 1 · substitute workflows</p>
<h2>{len(substitutes)} alternatives across {len(SUBSTITUTE_JOB_LABELS)} separately mapped Jobs</h2>
<p>The research includes professional networks, communities, human referrals, programs, manual processes, infrastructure tools, services, and deliberate non-adoption. Strength is qualitative and evidence-constrained.</p></section>
<div class="summary-grid"><article class="metric"><span class="num">{len(substitutes)}</span><span class="label">Substitute patterns</span></article><article class="metric"><span class="num">{len(evidence)}</span><span class="label">Traceable evidence records</span></article><article class="metric"><span class="num">{len(workflows)}</span><span class="label">Mapped Job stages</span></article><article class="metric"><span class="num">{unverified}</span><span class="label">Explicitly unverified alternatives</span></article></div>
<section class="panel"><h2>How to read this view</h2><ul class="clean-list"><li><strong>Strong Substitute</strong> means the evidence supports broad Job coverage, trust or network advantage, or a costly embedded workflow; it is not a numeric threat rank.</li><li><strong>Complementary Tool</strong> means the tool replaces a bounded capability rather than the relationship.</li><li><strong>Insufficient Evidence</strong> preserves a required alternative without inventing adoption or outcomes.</li><li>Existing companies are linked to their canonical 36-company profile instead of being duplicated as new competitors.</li></ul><div class="archive-list"><a href="../../SUBSTITUTE_RESEARCH.md">Read the qualitative analysis</a><a href="../../SUBSTITUTE_MATRIX.md">Open the generated matrix</a><a href="../../SUBSTITUTE_WORKFLOWS.md">Open full workflow maps</a><a href="../../SUBSTITUTE_EVIDENCE_REGISTER.md">Open the evidence register</a></div></section>
{''.join(cards_by_job)}
<section class="panel"><h2>Workflow maps</h2><p>The tables below keep all eleven stages visible, including stages where the evidence is insufficient. They describe current behavior and do not prescribe a product workflow.</p></section>
{''.join(workflow_sections)}
<section class="panel"><h2>Source and evidence register</h2><p class="muted">A source may support existence without supporting use, effectiveness, satisfaction, desire to switch, or willingness to pay.</p><div class="source-grid">{''.join(evidence_cards)}</div></section>
"""
    return page(
        "How Users Solve It Today",
        "Alternative Workflows",
        body,
        "Evidence-based substitutes, manual processes, services, infrastructure, and non-adoption.",
    )


def compatibility_ranker_js(rows):
    del rows
    return (
        'window.RANKER_DATA = [];\n'
        'window.RANKER_DATA_STATUS = "Deprecated: numeric ranking disabled because explicit sourced inputs are missing.";\n'
    )

def root_entry():
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>BizMatch Competitor Research</title><link rel="icon" href="data:,"><style>body{{font-family:system-ui,-apple-system,Segoe UI,Arial,sans-serif;margin:32px;background:#f7f9fb;color:#17202a}}main{{max-width:900px;margin:auto;background:white;border:1px solid #d8e0e8;border-radius:8px;padding:24px}}a{{color:#075985;text-decoration:none;font-weight:600}}a:hover{{text-decoration:underline}}li{{margin:10px 0}}code{{background:#eef2f7;padding:2px 5px;border-radius:4px}}.card{{border:1px solid #d8e0e8;border-radius:8px;padding:16px;margin:12px 0}}.card p{{margin:4px 0 0;font-weight:400;color:#42546b}}.warn{{border:1px solid #fbbf24;background:#fffbeb;border-radius:8px;padding:14px}}</style></head><body><main><h1>BizMatch Competitor Research</h1><div class="warn"><strong>Evidence boundary:</strong> numeric relationship and threat rankings are paused. Phase 1 maps substitutes and existing behavior without publishing product-market fit, MVP, Build/Buy, or launch recommendations.</div><h2>Start Here</h2><div class="card"><a href="sites/full-report-site/index.html">Evidence Status</a><p>Canonical evidence, research limits, and conclusions that remain unvalidated.</p></div><div class="card"><a href="sites/full-report-site/alternative-workflows.html">How Users Solve It Today</a><p>Phase 1 substitutes, manual workflows, services, infrastructure, and non-adoption across four Jobs.</p></div><div class="card"><a href="sites/full-report-site/priority-competitors.html">Priority Competitors</a><p>Pre-existing review scope; not a score ranking.</p></div><div class="card"><a href="sites/full-report-site/research-table.html">Full Research Table</a><p>Canonical table with relationship filters, source confidence, score status, and source links.</p></div><div class="card"><a href="sites/full-report-site/sources-methodology.html">Sources and Methodology</a><p>Separated canonical sources, missing-data policy, preserved weights, and research limits.</p></div><h2>Raw Data</h2><ul><li><a href="data/competitive-research-tracker.csv">Canonical competitor tracker CSV</a></li><li><a href="data/competitive-research-tracker.xlsx">Generated competitor tracker XLSX</a></li><li><a href="data/substitutes-research.csv">Canonical substitute entities CSV</a></li><li><a href="data/substitute-evidence.csv">Canonical substitute evidence CSV</a></li><li><a href="data/substitute-workflows.csv">Canonical substitute workflow CSV</a></li></ul><p>Archived generated drafts, historical strategic hypotheses, and cited datasets are audit material only. Technical reconciliation: {RECONCILIATION_DATE}.</p></main></body></html>"""

def archive_notice(title):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)} - Archived</title><link rel="icon" href="data:,"><style>body{{font-family:system-ui,-apple-system,Segoe UI,Arial,sans-serif;margin:32px;background:#f7f9fb;color:#17202a}}main{{max-width:880px;margin:auto;background:#fff;border:1px solid #d8e0e8;border-radius:8px;padding:24px}}a{{color:#075985;font-weight:600;text-decoration:none}}li{{margin:8px 0}}.warn{{border:1px solid #fbbf24;background:#fffbeb;border-radius:8px;padding:14px}}</style></head><body><main><h1>{escape(title)} - Archived</h1><div class="warn"><p>This old generated report is audit material only. Production code reads only the canonical tracker.</p></div><p>Use <a href="../sites/full-report-site/research-table.html">Full Research Table</a> and <a href="../data/competitive-research-tracker.csv">data/competitive-research-tracker.csv</a> for current facts.</p><p>Archived before or during the {RECONCILIATION_DATE} reconciliation.</p></main></body></html>"""

def citation_nav():
    pages = (
        ("index.html", "Index"),
        ("company-profiles.html", "Profiles"),
        ("product-flows.html", "Product"),
        ("pricing-business-model.html", "Pricing"),
        ("funding.html", "Funding"),
        ("traction-market-signal.html", "Traction"),
        ("ai-capabilities.html", "AI"),
        ("security-data-room.html", "Security"),
        ("risks-gaps.html", "Risks"),
        ("all-sources.html", "All sources"),
        ("threat-scoring.html", "Scoring status"),
    )
    return '<nav class="nav">' + "".join(
        f'<a href="{href}">{escape(label)}</a>' for href, label in pages
    ) + "</nav>"

def citation_shell(title, body):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><link rel="icon" href="data:,"><link rel="stylesheet" href="style.css"></head><body><header><h1>{escape(title)}</h1><p>Generated from the canonical CSV. No archived cited dataset is read.</p>{citation_nav()}</header><main>{body}<p class="footer">Canonical source: ../../data/competitive-research-tracker.csv · Technical reconciliation: {RECONCILIATION_DATE} · Row-level research dates are preserved.</p></main></body></html>"""

def citation_sources(row):
    links = urls(row.get("primary_sources", "")) + urls(row.get("secondary_sources", ""))
    if not links:
        return '<span class="empty">No source URL recorded</span>'
    return " ".join(
        f'<a href="{escape(link)}" target="_blank" rel="noopener">{escape(urlparse(link).netloc)}</a>'
        for link in links
    )

def citation_cards(rows, fields):
    cards = []
    for row in rows:
        values = []
        for field, label in fields:
            value = (row.get(field) or "").strip()
            rendered = escape(value) if value else '<span class="empty">Insufficient Evidence</span>'
            values.append(f"<dt>{escape(label)}</dt><dd>{rendered}</dd>")
        cards.append(
            f'<article class="card"><h2 class="company"><a href="{escape(row["url"])}" target="_blank" rel="noopener">{escape(row["company"])}</a></h2>'
            f'<p class="meta">Last checked: {escape(row.get("last_checked") or "not recorded")} · {escape(row.get("source_confidence") or "confidence not recorded")}</p>'
            f'<dl class="field-list">{"".join(values)}</dl><div class="sources">{citation_sources(row)}</div></article>'
        )
    return '<div class="grid">' + "".join(cards) + "</div>"

def write_citation_site(rows):
    page_fields = {
        "company-profiles.html": ("Company Profiles", (
            ("current_status", "Current status"),
            ("founded_launch_year", "Founded / launch year"),
            ("hq_country", "HQ / country"),
            ("operating_area", "Operating area"),
            ("target_users", "Target users"),
            ("product_category", "Product category"),
            ("acquisition_rebrand_history", "Acquisition / rebrand history"),
        )),
        "product-flows.html": ("Product & Application Flows", tuple(FEATURES)),
        "pricing-business-model.html": ("Pricing & Business Model", (
            ("pricing_model", "Pricing model"),
            ("business_model", "Business model"),
        )),
        "funding.html": ("Funding, Investors & Capital Facilitated", (
            ("total_funding", "Total funding"),
            ("funding_rounds", "Funding rounds"),
            ("investors", "Investors"),
            ("funding_source_type", "Funding source type"),
            ("last_funding_date", "Last funding date"),
            ("deals_funding_facilitated", "Capital facilitated"),
        )),
        "traction-market-signal.html": ("Traction, Partnerships & Activity", (
            ("users_traction", "Users / traction"),
            ("partnerships", "Partnerships"),
            ("media_coverage", "Media coverage"),
            ("product_update_activity", "Product update activity"),
        )),
        "ai-capabilities.html": ("AI Capabilities", (
            ("ai_matching_scoring", "AI matching / scoring"),
            ("ai_deck_scoring", "AI deck scoring"),
            ("meeting_prep_ai_briefing", "Meeting-prep AI briefing"),
        )),
        "security-data-room.html": ("Security, NDA, Data Room & E-signature", (
            ("nda_gated_unlock", "NDA / access gate"),
            ("data_room", "Data room"),
            ("e_signature", "E-signature"),
            ("messaging_collaboration", "Messaging / collaboration"),
        )),
        "risks-gaps.html": ("Unsupported Claims, Contradictions & Gaps", (
            ("unsupported_claims", "Unsupported claims"),
            ("contradictions", "Contradictions"),
            ("notes", "Notes"),
        )),
        "all-sources.html": ("All Sources by Company", (
            ("primary_sources", "Primary sources"),
            ("secondary_sources", "Secondary sources"),
            ("last_checked", "Last checked"),
            ("source_confidence", "Source confidence"),
        )),
    }
    intro = (
        '<section class="card"><h2>Canonical evidence pages</h2>'
        '<p>Every page in this section is regenerated from <code>data/competitive-research-tracker.csv</code>. '
        'Historical cited files are isolated under <code>archive/data/</code>.</p>'
        '<p>Numeric relationship rankings are paused. Missing evidence is displayed as Insufficient Evidence, never as zero or an average.</p></section>'
    )
    (CITATION_SITE / "index.html").write_text(
        citation_shell("BizMatch Citation Site", intro),
        encoding="utf-8",
    )
    for filename, (title, fields) in page_fields.items():
        (CITATION_SITE / filename).write_text(
            citation_shell(title, citation_cards(rows, fields)),
            encoding="utf-8",
        )
    scoring = (
        '<section class="card"><h2>Relationship score: Insufficient Evidence</h2>'
        '<p>The current schema lacks explicit sourced inputs for the preserved segmented formulas, so the score is null for all companies and no cross-company ranking is generated.</p></section>'
        '<section class="card"><h2>Legacy scores: Deprecated</h2>'
        f'<p>The historical columns {escape(", ".join(LEGACY_SCORE_FIELDS))} remain in the canonical CSV only for audit. Their values are not rendered here and do not feed active pages, rankings, or conclusions.</p></section>'
    )
    (CITATION_SITE / "threat-scoring.html").write_text(
        citation_shell("Scoring Status & Audit Boundary", scoring),
        encoding="utf-8",
    )

def main():
    rows = enrich(list(csv.DictReader(CSV_PATH.open(encoding="utf-8"))))
    substitutes = list(csv.DictReader(SUBSTITUTES_PATH.open(encoding="utf-8")))
    substitute_evidence = list(
        csv.DictReader(SUBSTITUTE_EVIDENCE_PATH.open(encoding="utf-8"))
    )
    substitute_workflows = list(
        csv.DictReader(SUBSTITUTE_WORKFLOWS_PATH.open(encoding="utf-8"))
    )
    expected_profiles = {f"{slug(row['company'])}.html" for row in rows}
    COMPANY_SITE.mkdir(parents=True, exist_ok=True)
    for profile in COMPANY_SITE.glob("*.html"):
        if profile.name not in expected_profiles:
            profile.unlink()
    (SITE / "canonical-data.js").write_text(data_js(rows), encoding="utf-8")
    (SITE / "substitutes-data.js").write_text(
        substitute_data_js(substitutes, substitute_evidence, substitute_workflows),
        encoding="utf-8",
    )
    (SITE / "ranker-data.js").write_text(compatibility_ranker_js(rows), encoding="utf-8")
    (SITE / "index.html").write_text(evidence_status_page(rows), encoding="utf-8")
    (SITE / "alternative-workflows.html").write_text(
        substitutes_page(substitutes, substitute_evidence, substitute_workflows),
        encoding="utf-8",
    )
    (SITE / "strategic-conclusions-historical.html").write_text(
        historical_strategic_page(rows),
        encoding="utf-8",
    )
    (SITE / "priority-competitors.html").write_text(priority_page(rows), encoding="utf-8")
    (SITE / "research-table.html").write_text(research_table(rows), encoding="utf-8")
    (SITE / "category-analysis.html").write_text(category_page(rows), encoding="utf-8")
    (SITE / "sources-methodology.html").write_text(methodology_page(rows), encoding="utf-8")
    (SITE / "archive.html").write_text(archive_page(), encoding="utf-8")
    for r in rows:
        (COMPANY_SITE / f"{slug(r['company'])}.html").write_text(
            company_page(r),
            encoding="utf-8",
        )
    write_citation_site(rows)
    (ROOT / "index.html").write_text(root_entry(), encoding="utf-8")
    (ROOT / "START_HERE.html").write_text(root_entry(), encoding="utf-8")
    (ROOT / "README.html").write_text(root_entry(), encoding="utf-8")
    (REPORTS / "bizmatch-competitive-research-cited-report.html").write_text(archive_notice("Old Cited Report"), encoding="utf-8")
    (REPORTS / "competitive-research-tracker-preview.html").write_text(archive_notice("Old Tracker Preview"), encoding="utf-8")
    (REPORTS / "bizmatch-competitive-research-cited-report.md").write_text(
        "# Old Cited Report - Archived\n\n"
        "This old auto-generated report was removed from the active research path because it contained extraction errors. "
        "Use `data/competitive-research-tracker.csv` and `sites/full-report-site/index.html` for current facts.\n\n"
        f"Phase 0 reconciliation completed on {RECONCILIATION_DATE}.\n",
        encoding="utf-8",
    )
    for ranker in ("ranker.html", "ranker-chatgpt.html", "ranker-claude.html", "ranker-perplexity.html", "general-ranker.html"):
        (SITE / ranker).write_text(
            page(
                "Archived Unified Ranker",
                "Archive",
                '<section class="panel warning-panel"><h2>Ranker Archived</h2><p>The old rankers used deprecated scores, arbitrary defaults, and non-comparable relationship types. Numeric ranking is disabled. Use <a href="category-analysis.html">Category Analysis</a> for relationship groups and evidence status.</p></section>',
                "Old one-size-fits-all threat scoring removed from active research.",
            ),
            encoding="utf-8",
        )
    print(
        f"Generated {len(rows)} company profiles and {len(substitutes)} substitute "
        f"patterns from their separated canonical sources"
    )

if __name__ == "__main__":
    main()
