#!/usr/bin/env python3
import csv
import json
import re
from html import escape
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "competitive-research-tracker.csv"
SITE = ROOT / "sites" / "full-report-site"
REPORTS = ROOT / "reports"
TODAY = "2026-07-29"

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

SCORE_FIELDS = [
    "product_overlap_score",
    "feature_maturity_score",
    "market_traction_score",
    "ai_depth_score",
    "nda_security_strength_score",
    "network_moat_score",
]

STRATEGIC = {
    "Cherub": ("Direct competitor", "Founder-investor matching", "swipe/card, mutual match, investor trust, lightweight data room", "Founder/investor discovery; trust-gated investor intros; controlled startup disclosure"),
    "Comatch": ("Direct competitor", "Cofounder matching", "mobile swipe, personality matching, chat", "Founder/cofounder discovery; lightweight matching-to-chat flow"),
    "CoffeeSpace": ("Direct competitor", "Cofounder matching", "swipe/card, mutual match, AI recommendations, mobile app, talent marketplace", "Founder/cofounder discovery; founder/talent matching; mobile matching UX"),
    "SwipeDeck": ("Direct competitor", "Founder-investor matching", "swipe/card, mutual match, investor discovery, document upload", "Founder/investor discovery; fast investor-card screening"),
    "Foundersbase": ("Direct competitor", "Cofounder and startup network", "cofounder discovery, startup profiles, local ecosystem relevance", "Founder/cofounder discovery; Israeli ecosystem scanning; community network"),
    "Swipe Invest": ("Substitute", "Founder-investor event/discovery", "swipe concept, investor access, early-stage Europe", "Investor discovery and event-based access"),
    "SWIP": ("Substitute", "Pre-launch cofounder matching", "waitlist, AI match simulator, founder cohorts", "Founder/cofounder discovery concept benchmark"),
    "YC Co-Founder Matching": ("Substitute", "Cofounder matching network", "mutual interest, founder profiles, YC network", "Founder/cofounder discovery; free high-trust network access"),
    "CoFoundersLab": ("Substitute", "Cofounder matching network", "founder profiles, community, advisor/investor paths", "Founder/cofounder discovery; large cofounder network"),
    "Cofounder.org": ("Substitute", "Cofounder matching", "curated matching, founder profiles", "Founder/cofounder discovery"),
    "Tertle": ("Substitute", "Cofounder matching", "founder discovery, AI claims, messaging", "Founder/cofounder discovery"),
    "FounderCloud": ("Substitute", "Founder network", "founder profiles, startup community", "Founder discovery and startup community"),
    "AngelList": ("Substitute", "Startup fundraising/network", "investor discovery, fundraising workflows, network effects", "Fundraising discovery; investor network access"),
    "Gust": ("Substitute", "Startup fundraising workspace", "investor relations, application/fundraising workflows", "Fundraising workspace and investor application management"),
    "Crunchbase": ("Substitute", "Company/investor discovery database", "discovery, research, investor/company data", "Investor/company discovery and market research"),
    "Republic": ("Substitute", "Investment marketplace", "startup investing, investor network, fundraising marketplace", "Capital access and investor network growth"),
    "StartEngine": ("Substitute", "Investment marketplace", "crowdfunding, investor network, issuer onboarding", "Capital access and investor acquisition"),
    "OpenVC": ("Substitute", "Investor discovery and outreach", "investor database, AI pitch/review tools, outreach", "Investor discovery and fundraising outreach"),
    "Visible.vc": ("Substitute", "Investor relations workspace", "updates, data room-like sharing, investor discovery", "Investor updates and fundraising workspace"),
    "Signal (NFX)": ("Substitute", "Investor discovery network", "investor matching, NFX network, AI scoring claims", "Investor discovery and warm-intro substitute"),
    "Foundersuite": ("Substitute", "Fundraising CRM/workspace", "investor pipeline, CRM, documents, email workflows", "Fundraising pipeline management and investor follow-up"),
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
    "Cherub": ("Benchmark for founder-investor matching plus trust cues.", "Founder/investor discovery and controlled startup disclosure.", "Learn from investor verification, lightweight data-room language, and paid founder-side packaging.", "Do not treat creator/influencer equity flows as BizMatch's core wedge.", "High", "High"),
    "Foundersuite": ("Benchmark for fundraising process management.", "Investor pipeline, CRM, outreach, and fundraising workspace.", "Learn pipeline discipline and workspace continuity after a match.", "Do not build a full fundraising CRM before the match-to-collaboration workflow works.", "Medium-High", "High"),
    "YC Co-Founder Matching": ("Network threat because it is free, trusted, and attached to YC.", "Founder/cofounder discovery.", "Learn from trust-by-network and a low-friction founder profile loop.", "Do not compete on generic 'find a cofounder' breadth alone.", "High", "High"),
    "OpenVC": ("Substitute for investor search and access.", "Investor discovery, outreach, and fundraising readiness.", "Learn searchable investor fit and practical outreach data.", "Do not let investor lists become the product center of gravity.", "Medium-High", "High"),
    "Foundersbase": ("Relevant because of Israeli/ecosystem proximity and founder-network overlap.", "Founder/cofounder discovery and startup community.", "Learn from local network density and community positioning.", "Do not copy low-structure community browsing without gated collaboration depth.", "Medium", "Medium"),
}

RELATION_ORDER = ["Direct competitor", "Substitute", "Feature benchmark", "Infrastructure / potential partner"]

def slug(name):
    return name.lower().replace("&", "and").replace("(", "").replace(")", "").replace(".", "-").replace(" ", "-").replace("--", "-").strip("-")

def urls(text):
    return re.findall(r"https?://[^\s;,)]+", text or "")

def source_anchor(u):
    try:
        host = urlparse(u).netloc.replace("www.", "")
    except Exception:
        host = u
    return f'<a href="{escape(u)}" rel="noopener" target="_blank">{escape(host)}</a>'

def first_source(row):
    return (urls(row.get("primary_sources", "")) or urls(row.get("secondary_sources", "")) or [""])[0]

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

def score(row, key, default=1.0):
    try:
        return float(row.get(key, default) or default)
    except ValueError:
        return default

def relationship_score(row):
    rel = row["competitive_relationship"]
    if rel in ("Direct competitor", "Substitute"):
        components = {
            "User/use-case overlap": score(row, "product_overlap_score"),
            "Product-process overlap": score(row, "feature_maturity_score"),
            "Traction/network effect": (score(row, "market_traction_score") + score(row, "network_moat_score")) / 2,
            "Geographic/niche fit": 4 if row["company"] in ("Foundersbase", "CoffeeSpace", "Cherub", "YC Co-Founder Matching", "OpenVC") else 3,
            "Business/pricing model": 3 if "free" in row.get("pricing_model", "").lower() else 2.5,
            "Technology/AI depth": score(row, "ai_depth_score"),
        }
        weights = [0.30, 0.25, 0.20, 0.10, 0.10, 0.05]
        formula = "30% use-case overlap + 25% workflow overlap + 20% traction/network + 10% geography/niche + 10% pricing + 5% AI. Funding is context only."
    elif rel == "Feature benchmark":
        components = {
            "Capability quality": max(score(row, "ai_depth_score"), score(row, "feature_maturity_score")),
            "Maturity": score(row, "feature_maturity_score"),
            "Price": 4 if "free" in row.get("pricing_model", "").lower() else 3,
            "UX": score(row, "feature_maturity_score"),
            "Ease to integrate/imitate": 4 if score(row, "network_moat_score") <= 3 else 2,
        }
        weights = [0.30, 0.25, 0.15, 0.15, 0.15]
        formula = "30% capability quality + 25% maturity + 15% price + 15% UX + 15% ease to integrate or imitate."
    else:
        components = {
            "Security": score(row, "nda_security_strength_score"),
            "API/integration": 4 if row["company"] in ("Dropbox Sign", "PandaDoc", "DocSend", "Digify") else 3,
            "Pricing": 3 if "custom" in row.get("pricing_model", "").lower() else 4,
            "MVP fit": 5 if row["company"] in ("Dropbox Sign", "DocSend", "PandaDoc", "Digify") else 3,
            "Build-versus-buy": 5 if row["company"] in ("Dropbox Sign", "DocSend", "Digify") else 3,
            "NDA/controlled disclosure fit": score(row, "nda_security_strength_score"),
        }
        weights = [0.25, 0.20, 0.15, 0.15, 0.15, 0.10]
        formula = "25% security + 20% API/integration + 15% pricing + 15% MVP fit + 15% build-vs-buy + 10% NDA/disclosure fit."
    val = sum(v * w for v, w in zip(components.values(), weights))
    return round(val, 2), formula, components

def enrich(rows):
    for row in rows:
        rel, pc, sec, jobs = STRATEGIC.get(row["company"], ("Substitute", row.get("source_category", ""), "", ""))
        row["competitive_relationship"] = rel
        row["primary_category"] = pc
        row["secondary_capabilities"] = sec
        row["bizmatch_jobs_competed_for"] = jobs
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
        s, formula, comps = relationship_score(row)
        row["relationship_score"] = s
        row["score_formula"] = formula
        row["score_components"] = comps
    return rows

def write_csv(rows):
    existing = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    fields = list(existing[0].keys())
    for f in ("competitive_relationship", "primary_category", "secondary_capabilities", "bizmatch_jobs_competed_for"):
        if f not in fields:
            fields.append(f)
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fields})

def nav(active, prefix=""):
    items = [
        ("index.html", "Strategic Conclusions"),
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
<main>{body}<p class="footer">Canonical source: <a href="{data_prefix}data/competitive-research-tracker.csv">data/competitive-research-tracker.csv</a>. Last site update: {TODAY}. Research checked mostly on 2026-07-19.</p></main></body></html>"""

def confidence_badge(text):
    t = escape(text or "Unknown")
    klass = "confidence-high" if "High" in t else "confidence-low" if "Low" in t else "confidence-medium"
    return f'<span class="badge {klass}">{t}</span>'

def relationship_badge(rel):
    return f'<span class="badge rel-{slug(rel)}">{escape(rel)}</span>'

def strategic_page(rows):
    groups = {rel: [r for r in rows if r["competitive_relationship"] == rel] for rel in RELATION_ORDER}
    priority_cards = "".join(priority_card(next(r for r in rows if r["company"] == name), compact=True) for name in PRIORITY)
    landscape = "".join(f'<section class="landscape-group"><h3>{escape(rel)}</h3><p>{len(rs)} companies</p><p>{"; ".join(escape(r["company"]) for r in rs)}</p></section>' for rel, rs in groups.items())
    implications = [
        "Swipe is an interface mechanism, not durable differentiation.",
        "AI matching must explain why two sides fit, not only display a score.",
        "NDA alone is not the moat; the gated workflow around access, disclosure, and follow-up is the moat.",
        "AI pitch-deck review is a supporting feature, not the core product.",
        "Network effects are the central strategic risk.",
        "Start with a clearly defined Israeli niche before widening the market.",
        "Use an external signing or secure-document provider in the MVP instead of building enterprise data-room infrastructure.",
    ]
    priorities = [
        "High-quality user and project profiles.",
        "Explained matching.",
        "Mutual match and structured conversation.",
        "Access request and NDA.",
        "Staged project and document disclosure.",
        "User verification and trust and safety.",
        "Meetings with AI due-diligence briefing.",
        "Fundraising workspace and investor pipeline.",
        "Partnerships and network growth.",
    ]
    not_yet = ["Full enterprise data room.", "Cap table system.", "In-platform investment execution.", "Self-built e-signature infrastructure.", "AI expansion not connected to the core workflow."]
    body = f"""
<section class="hero-panel">
  <p class="eyebrow">Executive summary</p>
  <h2>No single competitor strongly owns the full BizMatch journey.</h2>
  <p>Most researched companies solve one slice: matching, investor discovery, pitch review, document security, or e-signature. BizMatch's opportunity is the managed transition from business discovery to verified, protected, structured collaboration.</p>
  <p class="positioning">BizMatch connects founders, partners, and investors and manages the journey from initial compatibility to a verified, protected, and structured business collaboration.</p>
  <div class="journey">Discovery <span>-></span> Mutual Match <span>-></span> Structured Conversation <span>-></span> Access Request <span>-></span> NDA <span>-></span> Controlled Disclosure <span>-></span> Meeting <span>-></span> Collaboration</div>
</section>
<section class="summary-grid">
  <div class="metric"><span class="num">{len(rows)}</span><span class="label">Companies in canonical tracker</span></div>
  <div class="metric"><span class="num">{len(groups["Direct competitor"])}</span><span class="label">Direct competitors</span></div>
  <div class="metric"><span class="num">{len(groups["Substitute"])}</span><span class="label">Substitutes/network threats</span></div>
  <div class="metric"><span class="num">{len(groups["Infrastructure / potential partner"])}</span><span class="label">Infrastructure options</span></div>
</section>
<section class="panel"><h2>Competitive Landscape</h2><div class="landscape-grid">{landscape}</div></section>
<section class="panel"><h2>Priority Competitors</h2><div class="priority-grid">{priority_cards}</div></section>
<section class="panel"><h2>Strategic Implications</h2><ul class="clean-list">{"".join(f"<li>{escape(x)}</li>" for x in implications)}</ul></section>
<section class="panel"><h2>Product Priorities</h2><ol class="clean-list numbered">{"".join(f"<li>{escape(x)}</li>" for x in priorities)}</ol></section>
<section class="panel"><h2>What Not To Build Yet</h2><ul class="clean-list">{"".join(f"<li>{escape(x)}</li>" for x in not_yet)}</ul></section>
"""
    return page("Strategic Conclusions", "Strategic Conclusions", body, "Decision-oriented synthesis generated from the canonical research tracker.")

def priority_card(row, compact=False):
    why, job, learn, avoid, threat, conf = PRIORITY[row["company"]]
    return f"""
<article class="priority-card">
  <h3><a href="companies/{slug(row['company'])}.html">{escape(row['company'])}</a></h3>
  <p>{relationship_badge(row['competitive_relationship'])} {confidence_badge(conf)} <span class="score-pill">Threat: {escape(threat)}</span></p>
  <dl class="mini-dl"><dt>Why it matters</dt><dd>{escape(why)}</dd><dt>Job solved</dt><dd>{escape(job)}</dd><dt>Learn</dt><dd>{escape(learn)}</dd><dt>Do not copy</dt><dd>{escape(avoid)}</dd></dl>
</article>"""

def priority_page(rows):
    body = '<section class="panel"><h2>Priority Competitors</h2><p class="muted">These are the companies that should shape product decisions first. The list is intentionally narrower than the full tracker.</p><div class="priority-grid">' + "".join(priority_card(next(r for r in rows if r["company"] == name)) for name in PRIORITY) + '</div></section>'
    return page("Priority Competitors", "Priority Competitors", body, "Focused benchmarks and threats for BizMatch product decisions.")

def research_table(rows):
    table_rows = []
    for r in rows:
        links = urls(r.get("primary_sources", ""))[:2] + urls(r.get("secondary_sources", ""))[:1]
        table_rows.append(f"""<tr data-search="{escape(' '.join(str(v) for v in r.values() if isinstance(v, str)).lower())}" data-relationship="{escape(r['competitive_relationship'])}" data-confidence="{escape(r.get('source_confidence',''))}">
<td><a href="companies/{slug(r['company'])}.html">{escape(r['company'])}</a></td>
<td>{relationship_badge(r['competitive_relationship'])}</td>
<td>{escape(r['primary_category'])}</td>
<td>{escape(r['target_users'])}</td>
<td>{escape(r['total_funding'])}</td>
<td>{escape(r['users_traction'])}</td>
<td><span class="score-pill" title="{escape(r['score_formula'])}">{r['relationship_score']}</span><br><small>{escape(r['score_formula'])}</small></td>
<td>{confidence_badge(r.get('source_confidence',''))}</td>
<td>{" ".join(source_anchor(u) for u in links)}</td>
</tr>""")
    filters = "".join(f'<option value="{escape(rel)}">{escape(rel)}</option>' for rel in RELATION_ORDER)
    body = f"""
<section class="panel"><h2>Filters</h2><div class="controls"><div><label for="search">Search</label><input id="search" placeholder="Company, feature, source, traction..."></div><div><label for="relationshipFilter">Competition type</label><select id="relationshipFilter"><option value="">All</option>{filters}</select></div><div><label for="confidenceFilter">Confidence</label><select id="confidenceFilter"><option value="">All</option><option>High</option><option>Medium</option><option>Low</option></select></div><div><label>&nbsp;</label><button class="secondary" id="resetFilters">Reset</button></div></div></section>
<section class="panel"><h2>Full Research Table <span class="muted">(<span id="visibleCount">{len(rows)}</span> visible)</span></h2><p class="muted">Funding is supporting context only. Relationship scores are segmented by competition type and show their formula inline.</p><div class="table-wrap"><table id="researchTable"><thead><tr><th>Company</th><th>Competition type</th><th>Primary category</th><th>Target users</th><th>Funding</th><th>Traction</th><th>Segment score</th><th>Confidence</th><th>Sources</th></tr></thead><tbody>{"".join(table_rows)}</tbody></table></div></section>
<script src="app.js"></script>"""
    return page("Full Research Table", "Full Research Table", body, "Canonical tracker table with strategic relationship filters and source-linked claims.")

def category_page(rows):
    blocks = []
    for rel in RELATION_ORDER:
        rs = sorted([r for r in rows if r["competitive_relationship"] == rel], key=lambda r: r["relationship_score"], reverse=True)
        cards = "".join(f'<article class="category-card"><h3><a href="companies/{slug(r["company"])}.html">{escape(r["company"])}</a></h3><p>{confidence_badge(r.get("source_confidence",""))} <span class="score-pill" title="{escape(r["score_formula"])}">{r["relationship_score"]}</span></p><p>{escape(r["bizmatch_jobs_competed_for"])}</p><p class="muted">{escape(r["score_formula"])}</p></article>' for r in rs)
        blocks.append(f'<section class="panel"><h2>{escape(rel)}</h2><div class="category-grid">{cards}</div></section>')
    return page("Category Analysis", "Category Analysis", "".join(blocks), "Separate scoring models for each competitive relationship.")

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
    body = f"""
<section class="panel"><h2>Single Source Of Truth</h2><p>The canonical source for active research is <a href="../../data/competitive-research-tracker.csv">data/competitive-research-tracker.csv</a>. The generated site data file <code>canonical-data.js</code>, the table, company profiles, category pages, priority competitor page, and strategic conclusions are generated from that file plus the explicit strategic classification rules in <code>tools/generate_site.py</code>.</p><p>Older files under <code>reports/</code> and <code>data/bizmatch-competitive-research-cited.*</code> are archived context only and should not be used as active facts when they conflict with the canonical tracker.</p></section>
<section class="panel"><h2>Research Limitations</h2><ul class="clean-list">{"".join(f"<li>{escape(x)}</li>" for x in limitations)}</ul></section>
<section class="panel"><h2>Research Backlog</h2><ol class="clean-list numbered">{"".join(f"<li>{escape(x)}</li>" for x in backlog)}</ol></section>
<section class="panel"><h2>Capability Verification Model</h2><p>Capabilities are displayed as Confirmed, Partial, Not found, or Not applicable. Confirmed requires direct support in the canonical tracker's cited notes. Partial is used for limited analogs or marketing-level evidence. Not found is transparent uncertainty, not a negative factual claim.</p></section>"""
    return page("Sources & Methodology", "Sources & Methodology", body, "Canonical source, scoring method, research limitations, and follow-up backlog.")

def archive_page():
    body = """
<section class="panel"><h2>Archived Material</h2><p>The old auto-generated cited report is no longer part of the active research navigation because it contains known extraction errors that contradict the canonical tracker.</p><div class="archive-list"><a href="../../reports/bizmatch-competitive-research-cited-report.html">Archived old cited report HTML</a><a href="../../reports/bizmatch-competitive-research-cited-report.md">Archived old cited report Markdown</a><a href="../../reports/competitive-research-tracker-preview.html">Archived tracker preview</a></div></section>
<section class="panel warning-panel"><h2>Known Archived Errors</h2><ul class="clean-list"><li>Cherub's $45K customer testimonial was misread as company funding.</li><li>CoffeeSpace's customer qualification threshold of $10M raised was misread as CoffeeSpace funding.</li><li>Swipe Invest's $45B European market statistic was misread as company funding.</li><li>Digify's platform/customer document-security figures were misread as funding.</li><li>Cofounder.org's '3 Matches' UI heading was misread as traction.</li><li>SWIP's target first cohort of 100 founders was misread as existing users.</li><li>SecureDocs and Carta pricing was mixed into funding or traction fields.</li></ul></section>
"""
    return page("Archive", "Archive", body, "Old generated reports kept out of the active research path.")

def company_page(row):
    caps = "".join(f"""<article class="cap-card"><h3>{escape(c['label'])}</h3><p><span class="badge status-{slug(c['status'])}">{escape(c['status'])}</span> <span class="badge">{escape(c['delivery_type'])}</span> {confidence_badge(c['confidence'])}</p><p>{escape(c['note'])}</p><p class="muted">Checked: {escape(c['checked_at'] or 'not recorded')} {source_anchor(c['evidence_url']) if c['evidence_url'] else ''}</p></article>""" for c in row["capabilities"].values())
    sources = " ".join(source_anchor(u) for u in urls(row.get("primary_sources", "")) + urls(row.get("secondary_sources", "")))
    comps = "".join(f"<dt>{escape(k)}</dt><dd>{v:.1f}</dd>" for k, v in row["score_components"].items())
    body = f"""
<div class="profile-layout"><div>
<section class="profile-card"><h2>{escape(row['company'])}</h2><p>{relationship_badge(row['competitive_relationship'])} {confidence_badge(row.get('source_confidence',''))}</p><dl class="field-grid"><dt>Primary category</dt><dd>{escape(row['primary_category'])}</dd><dt>Secondary capabilities</dt><dd>{escape(row['secondary_capabilities'])}</dd><dt>BizMatch jobs competed for</dt><dd>{escape(row['bizmatch_jobs_competed_for'])}</dd><dt>Status</dt><dd>{escape(row['current_status'])}</dd><dt>Target users</dt><dd>{escape(row['target_users'])}</dd><dt>Funding</dt><dd>{escape(row['total_funding'])}</dd><dt>Traction</dt><dd>{escape(row['users_traction'])}</dd></dl></section>
<section class="profile-card"><h2>Capability Evidence</h2><div class="cap-grid">{caps}</div></section>
<section class="profile-card"><h2>Evidence Notes</h2><dl class="field-grid"><dt>Unsupported claims</dt><dd>{escape(row.get('unsupported_claims',''))}</dd><dt>Contradictions corrected</dt><dd>{escape(row.get('contradictions',''))}</dd><dt>Last checked</dt><dd>{escape(row.get('last_checked',''))}</dd><dt>Sources</dt><dd>{sources}</dd></dl></section>
</div><aside class="sidebox"><h2>Segment Score</h2><p><span class="score-pill large" title="{escape(row['score_formula'])}">{row['relationship_score']}</span></p><p class="muted">{escape(row['score_formula'])}</p><dl class="score-list">{comps}</dl></aside></div>"""
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
            "source_confidence": r["source_confidence"],
            "relationship_score": r["relationship_score"],
            "score_formula": r["score_formula"],
            "score_components": r["score_components"],
            "capabilities": r["capabilities"],
            **{k: score(r, k) for k in SCORE_FIELDS},
        })
    return "window.BIZMATCH_RESEARCH = " + json.dumps({"source": "data/competitive-research-tracker.csv", "updated_at": TODAY, "companies": public}, ensure_ascii=False, indent=2) + ";\nwindow.RANKER_DATA = window.BIZMATCH_RESEARCH.companies;\n"

def compatibility_ranker_js(rows):
    items = []
    for r in rows:
        features = {}
        for key, _label in FEATURES:
            features[key] = r["capabilities"][key]["status"] in ("Confirmed", "Partial")
        items.append({
            "company": r["company"],
            "url": r["url"],
            "category": r["competitive_relationship"],
            "profile": f"companies/{slug(r['company'])}.html",
            "product_overlap_score": score(r, "product_overlap_score"),
            "feature_maturity_score": score(r, "feature_maturity_score"),
            "market_traction_score": score(r, "market_traction_score"),
            "funding_strength_score": score(r, "funding_strength_score"),
            "ai_depth_score": score(r, "ai_depth_score"),
            "nda_security_strength_score": score(r, "nda_security_strength_score"),
            "network_moat_score": score(r, "network_moat_score"),
            "direct_threat_score": r["relationship_score"],
            "features": features,
        })
    return "window.RANKER_DATA = " + json.dumps(items, ensure_ascii=False) + ";"

def root_entry():
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>BizMatch Competitor Research</title><link rel="icon" href="data:,"><style>body{{font-family:system-ui,-apple-system,Segoe UI,Arial,sans-serif;margin:32px;background:#f7f9fb;color:#17202a}}main{{max-width:900px;margin:auto;background:white;border:1px solid #d8e0e8;border-radius:8px;padding:24px}}a{{color:#075985;text-decoration:none;font-weight:600}}a:hover{{text-decoration:underline}}li{{margin:10px 0}}code{{background:#eef2f7;padding:2px 5px;border-radius:4px}}.card{{border:1px solid #d8e0e8;border-radius:8px;padding:16px;margin:12px 0}}.card p{{margin:4px 0 0;font-weight:400;color:#42546b}}</style></head><body><main><h1>BizMatch Competitor Research</h1><p>Strategic competitor research generated from the canonical tracker.</p><h2>Start Here</h2><div class="card"><a href="sites/full-report-site/index.html">Strategic Conclusions</a><p>Main decision page: landscape, priority competitors, implications, product priorities, and research limits.</p></div><div class="card"><a href="sites/full-report-site/priority-competitors.html">Priority Competitors</a><p>Narrow benchmark list for product decisions.</p></div><div class="card"><a href="sites/full-report-site/research-table.html">Full Research Table</a><p>Canonical table with relationship filters, source confidence, segmented scores, and source links.</p></div><div class="card"><a href="sites/full-report-site/sources-methodology.html">Sources and Methodology</a><p>Single source of truth, limitations, and follow-up research backlog.</p></div><h2>Raw Data</h2><ul><li><a href="data/competitive-research-tracker.csv">Canonical tracker CSV</a></li><li><a href="data/competitive-research-tracker.xlsx">Canonical tracker XLSX</a></li></ul><p>Archived generated drafts are kept under <a href="sites/full-report-site/archive.html">Archive</a> and are not active research facts. Last update: {TODAY}.</p></main></body></html>"""

def archive_notice(title):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)} - Archived</title><link rel="icon" href="data:,"><style>body{{font-family:system-ui,-apple-system,Segoe UI,Arial,sans-serif;margin:32px;background:#f7f9fb;color:#17202a}}main{{max-width:880px;margin:auto;background:#fff;border:1px solid #d8e0e8;border-radius:8px;padding:24px}}a{{color:#075985;font-weight:600;text-decoration:none}}li{{margin:8px 0}}.warn{{border:1px solid #fbbf24;background:#fffbeb;border-radius:8px;padding:14px}}</style></head><body><main><h1>{escape(title)} - Archived</h1><div class="warn"><p>This old auto-generated report was removed from the active research path because it contained known extraction errors and contradicted the canonical tracker.</p></div><p>Use <a href="../sites/full-report-site/index.html">Strategic Conclusions</a>, <a href="../sites/full-report-site/research-table.html">Full Research Table</a>, and <a href="../data/competitive-research-tracker.csv">data/competitive-research-tracker.csv</a> for current facts.</p><h2>Known corrected errors</h2><ul><li>Cherub: a $45K customer testimonial was not company funding.</li><li>CoffeeSpace: a $10M customer qualification threshold was not CoffeeSpace funding.</li><li>Swipe Invest: a $45B macro market statistic was not company funding.</li><li>Digify: document-security/customer figures were not company funding.</li><li>Cofounder.org: “3 Matches” was a UI heading, not traction.</li><li>SWIP: “100 founders” was a target cohort, not verified users.</li><li>SecureDocs and Carta pricing should not be shown as funding or traction.</li></ul><p>Archived on {TODAY}.</p></main></body></html>"""

def alias_page(target, label):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={escape(target)}"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(label)}</title><link rel="icon" href="data:,"><link href="../style.css" rel="stylesheet"></head><body><main><section class="panel"><h1>{escape(label)}</h1><p>This legacy profile URL now points to the canonical generated profile.</p><p><a href="{escape(target)}">Open canonical profile</a></p></section></main></body></html>"""

def main():
    rows = enrich(list(csv.DictReader(CSV_PATH.open(encoding="utf-8"))))
    write_csv(rows)
    (SITE / "canonical-data.js").write_text(data_js(rows), encoding="utf-8")
    (SITE / "ranker-data.js").write_text(compatibility_ranker_js(rows), encoding="utf-8")
    (SITE / "index.html").write_text(strategic_page(rows), encoding="utf-8")
    (SITE / "priority-competitors.html").write_text(priority_page(rows), encoding="utf-8")
    (SITE / "research-table.html").write_text(research_table(rows), encoding="utf-8")
    (SITE / "category-analysis.html").write_text(category_page(rows), encoding="utf-8")
    (SITE / "sources-methodology.html").write_text(methodology_page(rows), encoding="utf-8")
    (SITE / "archive.html").write_text(archive_page(), encoding="utf-8")
    for r in rows:
        (SITE / "companies" / f"{slug(r['company'])}.html").write_text(company_page(r), encoding="utf-8")
    (SITE / "companies" / "cofounderorg.html").write_text(alias_page("cofounder-org.html", "Cofounder.org"), encoding="utf-8")
    (SITE / "companies" / "visiblevc.html").write_text(alias_page("visible-vc.html", "Visible.vc"), encoding="utf-8")
    (ROOT / "index.html").write_text(root_entry(), encoding="utf-8")
    (ROOT / "START_HERE.html").write_text(root_entry(), encoding="utf-8")
    (ROOT / "README.html").write_text(root_entry(), encoding="utf-8")
    (REPORTS / "bizmatch-competitive-research-cited-report.html").write_text(archive_notice("Old Cited Report"), encoding="utf-8")
    (REPORTS / "competitive-research-tracker-preview.html").write_text(archive_notice("Old Tracker Preview"), encoding="utf-8")
    (REPORTS / "bizmatch-competitive-research-cited-report.md").write_text(
        "# Old Cited Report - Archived\n\n"
        "This old auto-generated report was removed from the active research path because it contained extraction errors. "
        "Use `data/competitive-research-tracker.csv` and `sites/full-report-site/index.html` for current facts.\n\n"
        f"Archived on {TODAY}.\n",
        encoding="utf-8",
    )
    for ranker in ("ranker.html", "ranker-chatgpt.html", "ranker-claude.html", "ranker-perplexity.html", "general-ranker.html"):
        (SITE / ranker).write_text(
            page(
                "Archived Unified Ranker",
                "Archive",
                '<section class="panel warning-panel"><h2>Ranker Archived</h2><p>The old unified rankers mixed direct competitors, substitutes, feature tools, and infrastructure vendors into one threat score. Use <a href="category-analysis.html">Category Analysis</a> for segmented rankings and formulas.</p></section>',
                "Old one-size-fits-all threat scoring removed from active research.",
            ),
            encoding="utf-8",
        )
    print(f"Generated {len(rows)} company profiles and strategic pages from {CSV_PATH}")

if __name__ == "__main__":
    main()
