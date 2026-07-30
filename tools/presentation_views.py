"""Presentation-first HTML views backed only by canonical research sources."""

import re
from html import escape
from urllib.parse import urlparse


def _slug(value):
    return re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")


def _values(value):
    return [item.strip() for item in (value or "").split("|") if item.strip()]


def _list(items, css="clean-list"):
    return f'<ul class="{css}">' + "".join(
        f"<li>{escape(str(item))}</li>" for item in items
    ) + "</ul>"


def _active_text(value):
    """Keep canonical history intact while excluding deprecated judgments from active UI."""
    value = re.sub(r"\s+", " ", (value or "").strip())
    if not value:
        return "Insufficient Evidence"
    replacements = {
        "product-market-fit": "product validation",
        "Build-versus-buy": "integration decision",
        "Build vs Buy": "integration decision",
        "MVP fit": "implementation fit",
        "MVP": "early product",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    deprecated = (
        "weak current competitive threat",
        "strong competitive threat",
        "worth monitoring",
        "weakest fit",
        "weakest company",
        "direct-threat conclusion",
    )
    sentences = re.split(r"(?<=[.!?])\s+", value)
    kept = [s for s in sentences if not any(term in s.lower() for term in deprecated)]
    return " ".join(kept).strip() or (
        "Historical comparative language is deprecated; review the sourced facts below."
    )


class ResearchViews:
    def __init__(
        self,
        rows,
        substitutes,
        evidence,
        workflows,
        findings,
        market_research,
        render_page,
        reconciliation_date,
        job_labels,
    ):
        self.rows = rows
        self.substitutes = substitutes
        self.evidence = evidence
        self.workflows = workflows
        self.findings = findings
        self.market_research = market_research
        self.render_page = render_page
        self.reconciliation_date = reconciliation_date
        self.job_labels = job_labels
        self.competitors = {_slug(row["company"]): row for row in rows}
        self.substitute_map = {row["substitute_id"]: row for row in substitutes}
        self.evidence_map = {row["evidence_id"]: row for row in evidence}

    def badge(self, value, prefix="finding"):
        return (
            f'<span class="badge {prefix}-{_slug(value)}">'
            f"{escape(value)}</span>"
        )

    def competitor_links(self, slugs):
        links = []
        for competitor_slug in slugs:
            row = self.competitors[competitor_slug]
            links.append(
                f'<a class="entity-chip" href="/sites/full-report-site/companies/'
                f'{escape(competitor_slug)}.html">{escape(row["company"])}'
                f'<small>Company profile</small></a>'
            )
        return "".join(links) or self.badge("Insufficient Evidence")

    def substitute_links(self, ids):
        links = []
        for substitute_id in ids:
            row = self.substitute_map[substitute_id]
            links.append(
                f'<a class="entity-chip" href="/sites/full-report-site/'
                f'alternative-workflows.html#substitute-{escape(substitute_id)}">'
                f'{escape(row["name"])}<small>{escape(row["classification"])}</small></a>'
            )
        return "".join(links) or self.badge("Insufficient Evidence")

    def evidence_preview(self, evidence_id, record_anchor=False):
        row = self.evidence_map[evidence_id]
        source = row["source_title"] or urlparse(row["source_url"]).netloc
        return f"""
<article class="evidence-preview"{f' id="evidence-{escape(evidence_id)}"' if record_anchor else ""}>
  <div class="evidence-preview-head">
    <span>{self.badge(row['source_type'], 'evidence')}</span>
    <small class="internal-id">Evidence record {escape(evidence_id)}</small>
  </div>
  <h4>{escape(source)}</h4>
  <p>{escape(row['supporting_excerpt_or_summary'])}</p>
  <p class="evidence-limitation"><strong>Limitation:</strong> {escape(row['limitation'])}</p>
  <div class="evidence-actions">
    <span>Confidence: <strong>{escape(row['confidence'])}</strong></span>
    <a href="/sites/full-report-site/alternative-workflows.html#evidence-{escape(evidence_id)}">Complete evidence record</a>
    <a href="{escape(row['source_url'])}" target="_blank" rel="noopener">Open source <span class="sr-only">(opens in a new tab)</span></a>
  </div>
</article>"""

    def trace(self, item, limit=3):
        evidence_ids = item.get("evidence_ids", [])
        previews = "".join(self.evidence_preview(eid) for eid in evidence_ids[:limit])
        remaining = len(evidence_ids) - limit
        more = (
            f'<a class="trace-more" href="/sites/full-report-site/alternative-workflows.html#evidence-register">'
            f"View {remaining} more linked evidence record{'s' if remaining != 1 else ''}</a>"
            if remaining > 0
            else ""
        )
        all_links = (
            '<div class="evidence-record-links"><strong>All linked records:</strong> '
            + " ".join(
                f'<a href="/sites/full-report-site/alternative-workflows.html#evidence-{escape(eid)}">'
                f'{escape(self.evidence_map[eid]["source_title"])}'
                f'<small class="internal-id">{escape(eid)}</small></a>'
                for eid in evidence_ids
            )
            + "</div>"
            if evidence_ids
            else ""
        )
        market_refs = item.get("market_research_refs", [])
        market = (
            '<p class="market-trace"><strong>Aggregate interview trace:</strong> '
            + ", ".join(f"<code>{escape(ref)}</code>" for ref in market_refs)
            + ' · <a href="/market-research/">Open market-research assessment</a></p>'
            if market_refs
            else ""
        )
        if not previews and not market:
            return (
                '<div class="finding-trace">'
                + self.badge("Insufficient Evidence")
                + "</div>"
            )
        return (
            f'<div class="finding-trace"><div class="evidence-preview-grid">{previews}</div>'
            f"{more}{all_links}{market}</div>"
        )

    def overview(self, root=False):
        executive = self.findings["executive_conclusion"]
        boundaries = self.findings["conclusion_boundaries"]
        metrics = (
            (len(self.rows), "Company records", "Canonical competitor tracker"),
            (len(self.substitutes), "Workflow substitutes", "Separate substitute layer"),
            (len(self.evidence), "Evidence records", "Claim-level traceability"),
            (len(self.job_labels), "Jobs mapped", "Thirteen stages each"),
        )
        metric_cards = "".join(
            f'<article class="metric"><span class="num">{count}</span>'
            f'<span class="label">{escape(label)}</span><small>{escape(note)}</small></article>'
            for count, label, note in metrics
        )
        jobs = "".join(
            f'<article class="job-overview-card"><span class="job-index">0{index}</span>'
            f'<h3>{escape(job["title"])}</h3><p>{escape(job["dominant_current_workflow"])}</p>'
            f'<a href="/findings-conclusions/#{escape(job["job_id"].lower())}">View conclusion and evidence</a></article>'
            for index, job in enumerate(self.findings["jobs"], 1)
        )
        findings = "".join(
            f'<article class="executive-finding"><span>{self.badge(item["confidence"])}</span>'
            f'<h3>{escape(item["finding"])}</h3><p>{escape(item["interpretation"])}</p>'
            f'<a href="/findings-conclusions/#cross-market">See supporting evidence</a></article>'
            for item in self.findings["cross_market_findings"]
        )

        def assumptions(items, modifier):
            return "".join(
                f'<li><span class="assumption-mark {modifier}" aria-hidden="true"></span>'
                f'<div><strong>{escape(item["assumption"])}</strong>'
                f'<small>Conclusion confidence: {escape(item["confidence"])}</small></div></li>'
                for item in items
            )

        pains = "".join(
            f'<tr><th scope="row">{escape(item["pain"])}</th>'
            f'<td>{self.badge(item["status"])}</td><td>{escape(item["caveat"])}</td></tr>'
            for item in self.findings["pains"]
        )
        body = f"""
<div class="overview-page">
<section class="overview-hero">
  <p class="eyebrow">Competitive intelligence · workflow research · evidence audit</p>
  <h2>What BizMatch is really competing against</h2>
  <p class="hero-lede">{escape(executive['headline'])}</p>
  <p>{escape(executive['summary'])}</p>
  <div class="hero-actions"><a class="button-link primary" href="/presentation/">Open executive brief</a>
  <a class="button-link" href="/findings-conclusions/">Explore the findings</a></div>
  <div class="decision-strip"><span>Current research decision</span><strong>{escape(executive['current_decision'])}</strong>
  <span>Conclusion confidence: {escape(executive['confidence'])}</span></div>
</section>
<section aria-labelledby="scope-title"><div class="section-heading"><div><p class="eyebrow">Research scope</p>
<h2 id="scope-title">Separate evidence layers, one research narrative</h2></div>
<p>Counts are generated from the canonical competitor, substitute, workflow, and evidence sources.</p></div>
<div class="summary-grid overview-metrics">{metric_cards}</div></section>
<section id="jobs" aria-labelledby="jobs-title"><div class="section-heading"><div><p class="eyebrow">Four distinct Jobs-to-be-Done</p>
<h2 id="jobs-title">The market is not one coherent matching problem</h2></div>
<a href="/sites/full-report-site/alternative-workflows.html">View current workflows</a></div>
<div class="job-overview-grid">{jobs}</div></section>
<section id="key-findings" aria-labelledby="key-findings-title"><div class="section-heading"><div><p class="eyebrow">Decision-relevant findings</p>
<h2 id="key-findings-title">What the combined evidence suggests</h2></div>
<a href="/findings-conclusions/#cross-market">Full cross-market analysis</a></div>
<div class="executive-findings-grid">{findings}</div></section>
<section class="panel" id="assumptions"><div class="section-heading"><div><p class="eyebrow">Assumption audit</p>
<h2>What strengthened—and what weakened</h2></div><a href="/findings-conclusions/#assumptions">Detailed counterevidence</a></div>
<div class="assumption-columns"><div><h3>Strengthened</h3><ul class="assumption-list">{assumptions(self.findings['assumptions_strengthened'], 'positive')}</ul></div>
<div><h3>Weakened</h3><ul class="assumption-list">{assumptions(self.findings['assumptions_weakened'], 'negative')}</ul></div></div></section>
<section id="pains" class="panel"><div class="section-heading"><div><p class="eyebrow">Pain versus hypothesis</p>
<h2>Convenience is not evidence of unmet demand</h2></div><a href="/findings-conclusions/#pains">View full trace</a></div>
<div class="responsive-table"><table><caption>Current evidence status of the pains examined</caption>
<thead><tr><th>Pain</th><th>Status</th><th>Boundary</th></tr></thead><tbody>{pains}</tbody></table></div></section>
<section class="boundary-section" id="boundaries"><div class="boundary-card justified"><p class="eyebrow">Can conclude</p><h2>Supported now</h2>{_list(boundaries['justified'])}</div>
<div class="boundary-card prohibited"><p class="eyebrow">Cannot conclude</p><h2>Evidence is insufficient</h2>{_list(boundaries['prohibited'])}</div></section>
<section class="next-step-panel"><div><p class="eyebrow">Recommended next research step</p><h2>{escape(executive['current_decision'])}</h2>
<p>Focus Customer Discovery on active co-founder seekers, investor attention, and real trust or disclosure failures before making product decisions.</p></div>
<a class="button-link primary" href="/findings-conclusions/#customer-discovery">Open the research agenda</a></section>
<section class="research-map"><a href="/sites/full-report-site/category-analysis.html"><span>01</span><strong>Competitive Landscape</strong><small>36 company-level relationships</small></a>
<a href="/sites/full-report-site/alternative-workflows.html"><span>02</span><strong>How Users Solve It Today</strong><small>Networks, tools, services, and non-adoption</small></a>
<a href="/sites/full-report-site/research-table.html"><span>03</span><strong>Evidence Library</strong><small>Canonical facts and confidence</small></a>
<a href="/sites/full-report-site/sources-methodology.html"><span>04</span><strong>Methodology</strong><small>Definitions, boundaries, and limitations</small></a></section>
</div>"""
        return self.render_page(
            "BizMatch Competitive & Workflow Research",
            "Overview",
            body,
            "A skeptical, evidence-led assessment of competition, current behavior, and unresolved market assumptions.",
            prefix="sites/full-report-site/" if root else "",
            data_prefix="" if root else "../../",
        )

    def findings_page(self):
        research = self.findings
        executive = research["executive_conclusion"]
        toc = (
            ("executive", "Executive conclusion"),
            ("jobs", "Findings by Job"),
            ("cross-market", "Cross-market findings"),
            ("pressures", "Competitive pressures"),
            ("assumptions", "Assumption audit"),
            ("pains", "Pains and hypotheses"),
            ("boundaries", "Conclusion boundaries"),
            ("red-team", "Red Team"),
            ("customer-discovery", "Customer Discovery"),
            ("limitations", "Methodology limitations"),
        )
        toc_html = "".join(f'<a href="#{anchor}">{label}</a>' for anchor, label in toc)
        key_findings = "".join(
            f'<li><a href="#cross-{index}">{escape(item["finding"])}</a>'
            f'<small>Conclusion confidence: {escape(item["confidence"])}</small></li>'
            for index, item in enumerate(research["cross_market_findings"], 1)
        )
        jobs = []
        for job in research["jobs"]:
            jobs.append(f"""
<article class="job-conclusion-card" id="{escape(job['job_id'].lower())}">
  <p class="eyebrow">{escape(job['title'])}</p>
  <h3>{escape(job['dominant_current_workflow'])}</h3>
  <div class="job-snapshot">
    <div><span>Primary trust mechanism</span><strong>{escape(job['main_trust_mechanism'])}</strong></div>
    <div><span>Conclusion confidence</span><strong>{escape(job['confidence'])}</strong></div>
    <div><span>Unresolved</span><strong>{escape(job['unresolved_questions'])}</strong></div>
  </div>
  <div class="entity-groups"><div><h4>Company-level competitors</h4>{self.competitor_links(job['competitor_slugs'])}</div>
  <div><h4>Workflow substitutes</h4>{self.substitute_links(job['substitute_ids'])}</div></div>
  <details><summary>Advantages, weaknesses, and supporting evidence</summary>
    <dl class="conclusion-dl"><dt>Evidence-supported advantage</dt><dd>{escape(job['supported_advantages'])}</dd>
    <dt>Evidence-supported weakness</dt><dd>{escape(job['supported_weaknesses'])}</dd>
    <dt>Evidence quality</dt><dd>{escape(job['evidence_quality'])}</dd></dl>
    {self.trace(job)}
  </details>
</article>""")
        cross = "".join(
            f'<article class="finding-summary-card" id="cross-{index}"><span>{self.badge(item["confidence"])}</span>'
            f'<h3>{escape(item["finding"])}</h3><p>{escape(item["interpretation"])}</p>'
            f'<details><summary>Supporting evidence</summary>{self.trace(item)}</details></article>'
            for index, item in enumerate(research["cross_market_findings"], 1)
        )
        pressures = "".join(
            f'<article class="pressure-card"><h3>{escape(item["pressure"])}</h3>'
            f'<p>{escape(item["why_it_matters"])}</p>{self.substitute_links(item["substitute_ids"])}'
            f'<p><strong>Conclusion confidence:</strong> {escape(item["confidence"])}</p>'
            f'<details><summary>Supporting evidence</summary>{self.trace(item)}</details></article>'
            for item in research["competitive_pressures"]
        )

        def assumptions(items, modifier):
            return "".join(
                f'<article class="assumption-card {modifier}"><h3>{escape(item["assumption"])}</h3>'
                f'<p><strong>Supporting evidence:</strong> {escape(item["supporting_evidence"])}</p>'
                f'<p><strong>Counterevidence:</strong> {escape(item["counterevidence"])}</p>'
                f'<p><strong>Still unproven:</strong> {escape(item["unproven"])}</p>'
                f'<p><strong>Conclusion confidence:</strong> {escape(item["confidence"])}</p>'
                f'<details><summary>Evidence trace</summary>{self.trace(item)}</details></article>'
                for item in items
            )

        pains = "".join(
            f'<tr><th scope="row">{escape(item["pain"])}</th><td>{self.badge(item["status"])}</td>'
            f'<td>{escape(item["caveat"])}</td><td><details><summary>Evidence trace</summary>{self.trace(item, 2)}</details></td></tr>'
            for item in research["pains"]
        )
        boundaries = research["conclusion_boundaries"]
        red_team = "".join(
            f'<details class="red-team-card"><summary><span>{escape(item["possibility"])}</span>'
            f'<strong>Current confidence: {escape(item["confidence"])}</strong></summary>'
            f'<p><strong>Supporting evidence:</strong> {escape(item["supporting_evidence"])}</p>'
            f'<p><strong>Counterevidence:</strong> {escape(item["counterevidence"])}</p>'
            f'<p><strong>Unknowns:</strong> {escape(item["unknowns"])}</p>'
            f'<p><strong>Customer Discovery test:</strong> {escape(item["customer_discovery_test"])}</p>'
            f'{self.trace(item)}</details>'
            for item in research["red_team"]
        )
        implications = "".join(
            f'<article class="implication-card"><h3>Evidence observed</h3><p>{escape(item["evidence_observed"])}</p>'
            f'<h4>Implication if confirmed</h4><p>{escape(item["implication_if_confirmed"])}</p>'
            f'<h4>Risk of acting too early</h4><p>{escape(item["risk_of_acting_too_early"])}</p>'
            f'<h4>Validation needed</h4><p>{escape(item["validation_needed"])}</p>'
            f'<p><strong>Conclusion confidence:</strong> {escape(item["confidence"])}</p>'
            f'<details><summary>Evidence trace</summary>{self.trace(item)}</details></article>'
            for item in research["conditional_implications"]
        )
        discovery = "".join(
            f'<tr><td>{escape(item["priority"])}</td><th scope="row">{escape(self.job_labels[item["job_id"]])}</th>'
            f'<td>{escape(item["question"])}</td><td>{escape(item["decision_link"])}</td></tr>'
            for item in research["customer_discovery"]
        )
        body = f"""
<div class="findings-page">
<aside class="findings-toc" aria-label="On this page"><strong>On this page</strong>{toc_html}</aside>
<section class="findings-hero" id="executive"><p class="eyebrow">Active, evidence-linked conclusion</p>
<h2>{escape(executive['headline'])}</h2><p>{escape(executive['summary'])}</p>
<div class="decision-strip"><span>Current decision</span><strong>{escape(executive['current_decision'])}</strong>
<span>Conclusion confidence: {escape(executive['confidence'])}</span></div>
<details><summary>Executive evidence trace</summary>{self.trace(executive, 4)}</details></section>
<section class="panel evidence-legend"><h2>Evidence and uncertainty labels</h2><p>
{self.badge('Evidence suggests')} {self.badge('Independent Evidence')} {self.badge('Company Claim')}
{self.badge('Inference')} {self.badge('Unverified')} {self.badge('Insufficient Evidence')}
{self.badge('Hypothesis requiring validation')}</p>
<p>Labels are qualitative and include text, not color alone. Company Claim is never presented as independent evidence; Inference is never presented as fact.</p></section>
<section class="executive-layer"><div><p class="eyebrow">Seven-minute read</p><h2>Most decision-relevant findings</h2>
<ol>{key_findings}</ol></div><aside class="warning-panel"><h3>Most important limitation</h3>
<p>{escape(research['meta']['decision_boundary'])}</p><a href="#boundaries">See what cannot be concluded</a></aside></section>
<section class="panel terminology-callout"><h2>Two research lenses—not one ranking</h2>
<p><strong>Company-level competitive relationship</strong> describes how each of 36 companies relates to BizMatch. <strong>Workflow substitute</strong> describes how a user completes a Job through tools, people, networks, manual work, or non-adoption. A company can participate in both contexts without being duplicated across datasets.</p></section>
<section class="panel" id="jobs"><div class="section-heading"><div><p class="eyebrow">Findings by Job</p><h2>Conclusions by Job-to-be-Done</h2></div>
<a href="/sites/full-report-site/alternative-workflows.html">Compare workflow stages</a></div><div class="job-conclusion-grid">{''.join(jobs)}</div></section>
<section class="panel" id="cross-market"><h2>Cross-market findings</h2><div class="finding-summary-grid">{cross}</div></section>
<section class="panel" id="pressures"><h2>Strongest competitive pressures</h2><p>Behavioral pressure, not numeric threat ranks.</p><div class="pressure-grid">{pressures}</div></section>
<section class="panel" id="assumptions"><h2>BizMatch assumption audit</h2><div class="assumption-columns">
<div><h3>BizMatch assumptions that gained support</h3><div class="assumption-stack">{assumptions(research['assumptions_strengthened'], 'strengthened')}</div></div>
<div><h3>BizMatch assumptions that weakened</h3><div class="assumption-stack">{assumptions(research['assumptions_weakened'], 'weakened')}</div></div></div></section>
<section class="panel" id="pains"><h2>Supported pains versus hypotheses</h2><div class="responsive-table"><table>
<caption>Pain statements, qualitative evidence status, caveat, and trace</caption><thead><tr><th>Pain</th><th>Status</th><th>Caveat</th><th>Evidence</th></tr></thead>
<tbody>{pains}</tbody></table></div></section>
<section class="panel" id="boundaries"><h2>What can and cannot be concluded</h2><div class="boundary-grid">
<article class="boundary-card justified"><h3>Justified by current evidence</h3>{_list(boundaries['justified'])}</article>
<article class="boundary-card plausible"><h3>Plausible but unverified</h3>{_list(boundaries['plausible_unverified'])}</article>
<article class="boundary-card prohibited"><h3>Prohibited by insufficient evidence</h3>{_list(boundaries['prohibited'])}</article></div></section>
<section class="panel"><h2>Conditional strategic implications</h2><p>Every implication remains conditional and names the risk of acting before validation.</p>
<div class="implication-grid">{implications}</div></section>
<section class="panel" id="red-team"><h2>Required Red Team assessment</h2><p>Central risks remain visible; expand each item for support, counterevidence, unknowns, and the required test.</p>
<div class="red-team-list">{red_team}</div></section>
<section class="panel" id="customer-discovery"><h2>Customer Discovery agenda</h2><p>This is a research agenda only; it is not a product roadmap.</p>
<div class="responsive-table"><table><caption>Prioritized unresolved research questions</caption><thead><tr><th>Priority</th><th>Job</th><th>Question</th><th>Decision link</th></tr></thead><tbody>{discovery}</tbody></table></div></section>
<section class="panel" id="limitations"><h2>Methodology and evidence limitations</h2>{_list(research['methodology_limitations'])}
<div class="context-links"><a href="/sites/full-report-site/sources-methodology.html">Read methodology</a>
<a href="/SUBSTITUTE_EVIDENCE_REGISTER.md">Open evidence register</a><a href="/data/findings-and-implications.json">Inspect active conclusions source</a></div></section>
</div>"""
        return self.render_page(
            "Findings & Strategic Implications",
            "Findings",
            body,
            "The active conclusion, the strongest evidence, and the decisions current research cannot support.",
            prefix="../sites/full-report-site/",
            data_prefix="../",
        )

    def workflows_page(self):
        categories = sorted({row["category"] for row in self.substitutes})
        strengths = sorted({row["substitute_strength"] for row in self.substitutes})
        statuses = sorted({row["research_status"] for row in self.substitutes})
        stages = sorted(
            {stage for row in self.substitutes for stage in _values(row["workflow_stages_covered"])}
        )
        options = lambda values: "".join(
            f'<option value="{escape(value)}">{escape(value.replace("_", " ").title())}</option>'
            for value in values
        )
        cards = []
        for row in self.substitutes:
            jobs = _values(row["job_to_be_done"])
            job_names = [self.job_labels[job] for job in jobs]
            evidence_ids = _values(row["evidence_ids"])
            cards.append(f"""
<article class="substitute-card type-{_slug(row['classification'])}" id="substitute-{escape(row['substitute_id'])}"
 data-explorer-item data-name="{escape(row['name'].lower())}" data-category="{escape(row['category'])}"
 data-classification="{escape(row['classification'])}" data-jobs="{escape('|'.join(jobs))}"
 data-persona="{escape(row['target_persona'])}" data-strength="{escape(row['substitute_strength'])}"
 data-status="{escape(row['research_status'])}" data-stages="{escape(row['workflow_stages_covered'])}">
 <div class="card-kicker"><span>{escape(row['classification'])}</span><small class="internal-id">Record {escape(row['substitute_id'])}</small></div>
 <h3>{escape(row['name'])}</h3>
 <p>{self.badge(row['substitute_strength'], 'substitute')} {self.badge(row['confidence'], 'confidence')}</p>
 <dl class="compact-facts"><dt>Category</dt><dd>{escape(row['category'])}</dd>
 <dt>Relevant Job</dt><dd>{escape('; '.join(job_names))}</dd>
 <dt>Why users choose it</dt><dd>{escape(row['why_users_choose_it'])}</dd>
 <dt>Trust mechanism</dt><dd>{escape(row['trust_mechanism'])}</dd></dl>
 <details><summary>Workflow coverage and evidence</summary>
 <dl class="conclusion-dl"><dt>Stages covered</dt><dd>{escape(', '.join(s.replace('_', ' ') for s in _values(row['workflow_stages_covered'])))}</dd>
 <dt>Primary advantage</dt><dd>{escape(row['advantages'])}</dd><dt>Primary limitation</dt><dd>{escape(row['limitations'])}</dd>
 <dt>Switching cost</dt><dd>{escape(row['switching_cost'])}</dd><dt>Evidence quality</dt><dd>{escape(row['source_type'])}</dd></dl>
 <div class="evidence-preview-grid">{''.join(self.evidence_preview(eid) for eid in evidence_ids[:2])}</div>
 </details></article>""")
        workflow_sections = []
        for job_id, label in self.job_labels.items():
            rows = sorted(
                [row for row in self.workflows if row["job_id"] == job_id],
                key=lambda row: int(row["stage_order"]),
            )
            stages_html = "".join(
                f'<li><span>{escape(row["stage_order"])}</span><div><strong>{escape(row["stage_id"].replace("_", " ").title())}</strong>'
                f'<p>{escape(row["current_action"])}</p><small>{escape(row["tools_channels"].replace("|", " · "))}</small></div>'
                f'<em>{escape(row["confidence"])}</em></li>'
                for row in rows
            )
            workflow_sections.append(
                f'<details class="workflow-map" id="workflow-{job_id.lower()}"><summary><span>{escape(label)}</span>'
                f'<small>13 mapped stages · expand workflow</small></summary><ol>{stages_html}</ol></details>'
            )
        evidence_cards = "".join(
            self.evidence_preview(row["evidence_id"], record_anchor=True)
            for row in self.evidence
        )
        body = f"""
<section class="page-intro"><p class="eyebrow">Canonical workflow-substitute layer</p><h2>How users solve the Jobs today</h2>
<p>Users combine relationships, communities, services, manual work, infrastructure, and deliberate non-adoption. These patterns are separate from the 36-company tracker.</p>
<p class="key-takeaway"><strong>Key takeaway:</strong> A workflow substitute can be stronger than a similar-looking company because it is already embedded in trust, habit, and existing relationships.</p></section>
<section class="panel terminology-callout"><h2>Competitor versus workflow substitute</h2><p>A company-level relationship describes a researched company. This page maps complete behaviors and non-company methods. Existing companies are linked through canonical slugs and are not re-added to the competitor dataset.</p></section>
<section class="panel evidence-legend"><h2>Evidence labels</h2><p>{self.badge('Independent Evidence', 'evidence')} {self.badge('Company Claim', 'evidence')} {self.badge('Inference', 'evidence')} {self.badge('Unverified', 'evidence')} {self.badge('Insufficient Evidence', 'evidence')}</p>
<p>Company Claim and Company Documentation establish vendor-originated statements or capabilities, not independent proof of effectiveness.</p></section>
<section class="panel explorer-controls" aria-labelledby="explore-title"><div class="section-heading"><div><p class="eyebrow">Explore {len(self.substitutes)} patterns</p><h2 id="explore-title">Find the relevant substitute</h2></div>
<p><span id="substituteCount">{len(self.substitutes)}</span> visible</p></div>
<div class="controls"><div><label for="substituteSearch">Search</label><input id="substituteSearch" type="search" placeholder="Warm introductions, NDA, spreadsheet…"></div>
<div><label for="substituteJob">Job</label><select id="substituteJob"><option value="">All Jobs</option>{options(self.job_labels.keys())}</select></div>
<div><label for="substituteCategory">Category</label><select id="substituteCategory"><option value="">All categories</option>{options(categories)}</select></div>
<div><label for="substituteStrength">Strength</label><select id="substituteStrength"><option value="">All strengths</option>{options(strengths)}</select></div>
<div><label for="substituteStatus">Evidence status</label><select id="substituteStatus"><option value="">All statuses</option>{options(statuses)}</select></div>
<div><label for="substituteStage">Workflow stage</label><select id="substituteStage"><option value="">All stages</option>{options(stages)}</select></div></div>
<div class="view-actions"><button type="button" class="secondary" data-view="compact" aria-pressed="true">Compact view</button>
<button type="button" class="secondary" data-view="expanded" aria-pressed="false">Expanded view</button>
<button type="button" class="secondary" id="resetSubstituteFilters">Reset filters</button></div></section>
<section><div class="substitute-grid explorer-grid" id="substituteGrid">{''.join(cards)}</div>
<p class="empty-state" id="substituteEmpty" hidden>No substitute matches these filters.</p></section>
<section class="panel" id="workflow-maps"><div class="section-heading"><div><p class="eyebrow">Current workflows</p><h2>Four Jobs, thirteen stages each</h2></div>
<a href="/SUBSTITUTE_WORKFLOWS.md">Open full generated workflow register</a></div>{''.join(workflow_sections)}</section>
<section class="panel" id="evidence-register"><div class="section-heading"><div><p class="eyebrow">Source register</p><h2>Complete evidence records</h2></div>
<a href="/SUBSTITUTE_EVIDENCE_REGISTER.md">Open Markdown register</a></div><div class="evidence-preview-grid evidence-register">{evidence_cards}</div></section>"""
        return self.render_page(
            "How Users Solve It Today",
            "How Users Solve It Today",
            body,
            "Searchable substitute patterns and workflow maps across four Jobs-to-be-Done.",
        )

    def landscape_page(self):
        relationships = sorted({row["competitive_relationship"] for row in self.rows})
        categories = sorted({row["primary_category"] for row in self.rows})
        options = lambda values: "".join(
            f'<option value="{escape(value)}">{escape(value)}</option>' for value in values
        )
        cards = []
        for row in self.rows:
            description = _active_text(row.get("plain_language_description") or row.get("notes"))
            limitation = _active_text(
                row.get("important_clarification")
                or row.get("unsupported_claims")
                or row.get("contradictions")
            )
            cards.append(f"""
<article class="landscape-card" data-explorer-item data-name="{escape(row['company'].lower())}"
 data-category="{escape(row['primary_category'])}" data-relationship="{escape(row['competitive_relationship'])}"
 data-confidence="{escape(row['overall_confidence'])}" data-job="{escape((row.get('primary_job_solved') or row['bizmatch_jobs_competed_for']).lower())}">
 <div class="card-kicker"><span>Company-level competitive relationship</span><small>{escape(row['overall_confidence'])} confidence</small></div>
 <h3><a href="companies/{_slug(row['company'])}.html">{escape(row['company'])}</a></h3>
 <p>{self.badge(row['competitive_relationship'], 'relationship')}</p>
 <p>{escape(description)}</p>
 <dl class="compact-facts"><dt>Job addressed</dt><dd>{escape(row.get('primary_job_solved') or row['bizmatch_jobs_competed_for'])}</dd>
 <dt>Target users</dt><dd>{escape(row['target_users'])}</dd><dt>Evidence boundary</dt><dd>{escape(limitation)}</dd></dl>
 <a href="companies/{_slug(row['company'])}.html">Open evidence profile</a>
</article>""")
        body = f"""
<section class="page-intro"><p class="eyebrow">36-company canonical tracker</p><h2>Competitive Landscape</h2>
<p>Companies are grouped by their evidence-supported relationship to BizMatch. The view is descriptive and does not create an ordinal threat ranking.</p>
<p class="key-takeaway"><strong>Key takeaway:</strong> The company landscape covers matching, discovery, fundraising, pitch support, disclosure, and infrastructure—but company similarity alone does not reveal the strongest behavioral substitute.</p></section>
<section class="panel terminology-callout"><h2>How to read the classifications</h2><p><strong>Company-level competitive relationship</strong> is the canonical classification shown here. <strong>Workflow substitutes</strong> are maintained separately because they also include people, communities, manual work, supporting infrastructure, and “do nothing.”</p>
<a href="alternative-workflows.html">Compare workflow substitutes</a></section>
<section class="panel explorer-controls"><div class="section-heading"><div><p class="eyebrow">Explore the landscape</p><h2>Filter by evidence-supported context</h2></div><p><span id="landscapeCount">{len(self.rows)}</span> visible</p></div>
<div class="controls"><div><label for="landscapeSearch">Search company, Job, or capability</label><input id="landscapeSearch" type="search" placeholder="Investor discovery, co-founder, data room…"></div>
<div><label for="landscapeRelationship">Relationship</label><select id="landscapeRelationship"><option value="">All relationships</option>{options(relationships)}</select></div>
<div><label for="landscapeCategory">Category</label><select id="landscapeCategory"><option value="">All categories</option>{options(categories)}</select></div>
<div><label for="landscapeConfidence">Evidence confidence</label><select id="landscapeConfidence"><option value="">All confidence levels</option><option>High</option><option>Medium</option><option>Low</option></select></div></div>
<button type="button" class="secondary" id="resetLandscapeFilters">Reset filters</button></section>
<section><div class="landscape-explorer" id="landscapeGrid">{''.join(cards)}</div><p class="empty-state" id="landscapeEmpty" hidden>No company matches these filters.</p></section>"""
        return self.render_page(
            "Competitive Landscape",
            "Competitive Landscape",
            body,
            "Company-level relationships, evidence confidence, and Jobs addressed—without unsupported ranking.",
        )

    def evidence_page(self):
        rows = []
        for row in self.rows:
            links = [
                url.strip()
                for url in re.findall(
                    r"https?://[^\s|,]+",
                    f"{row.get('primary_sources','')} {row.get('secondary_sources','')}",
                )
            ]
            source_links = " ".join(
                f'<a href="{escape(url)}" target="_blank" rel="noopener">{escape(urlparse(url).netloc)}</a>'
                for url in links[:3]
            ) or "No source URL recorded"
            rows.append(f"""
<tr class="company-row" data-row-id="{escape(_slug(row['company']))}" data-company-name="{escape(row['company'].lower())}"
 data-companies-search="{escape((row['company']+' '+row['primary_category']+' '+row.get('bizmatch_jobs_competed_for','')).lower())}"
 data-capabilities-search="{escape((row.get('secondary_capabilities','')+' '+row.get('product_model','')).lower())}"
 data-evidence-search="{escape(_active_text(row.get('unsupported_claims','')+' '+row.get('contradictions','')+' '+row.get('notes','')).lower())}"
 data-relationship="{escape(row['competitive_relationship'])}" data-confidence="{escape(row['overall_confidence'])}">
 <td><a class="company-link" href="companies/{_slug(row['company'])}.html">{escape(row['company'])}</a></td>
 <td>{escape(row['competitive_relationship'])}</td><td>{escape(row['primary_category'])}</td>
 <td>{escape(row.get('primary_job_solved') or row['bizmatch_jobs_competed_for'])}</td>
 <td>Evidence confidence: <strong>{escape(row['overall_confidence'])}</strong></td>
 <td>{escape(_active_text(row.get('important_clarification') or row.get('unsupported_claims') or 'Insufficient Evidence'))}</td>
 <td>{source_links}</td></tr>""")
        filters = "".join(
            f'<option value="{escape(value)}">{escape(value)}</option>'
            for value in sorted({row["competitive_relationship"] for row in self.rows})
        )
        body = f"""
<section class="page-intro"><p class="eyebrow">Canonical company evidence</p><h2>Evidence Library</h2>
<p>Search the 36-company tracker by company, capability, or evidence note. Open a profile for the complete canonical record.</p>
<p class="key-takeaway"><strong>Key takeaway:</strong> “Not found” is an evidence gap, not a proven weakness. Company-reported traction remains a company claim unless independently corroborated.</p></section>
<section class="panel"><div class="controls"><div><label for="search">Search</label><input id="search" type="search" placeholder="CoffeeSpace, NDA, Israel, pitch deck…"></div>
<div><label for="searchScope">Search scope</label><select id="searchScope"><option value="all">All</option><option value="companies">Companies</option><option value="capabilities">Capabilities</option><option value="evidence">Evidence notes</option></select></div>
<div><label for="relationshipFilter">Company relationship</label><select id="relationshipFilter"><option value="">All relationships</option>{filters}</select></div>
<div><label for="confidenceFilter">Evidence confidence</label><select id="confidenceFilter"><option value="">All</option><option>High</option><option>Medium</option><option>Low</option></select></div></div>
<button class="secondary" id="resetFilters">Reset filters</button></section>
<section class="panel"><div class="section-heading"><div><p class="eyebrow">Detailed evidence view</p><h2>Company records</h2></div><p><span id="visibleCount">{len(self.rows)}</span> visible</p></div>
<div class="responsive-table"><table id="researchTable"><caption>Canonical competitor facts, confidence, caveats, and sources</caption>
<thead><tr><th>Company</th><th>Relationship</th><th>Category</th><th>Job addressed</th><th>Evidence confidence</th><th>Important limitation</th><th>Sources</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div></section>
<script src="app.js"></script>"""
        return self.render_page(
            "Evidence Library",
            "Evidence",
            body,
            "Searchable canonical company evidence, confidence, caveats, and source links.",
        )

    def company_page(self, row):
        sources = []
        for url in re.findall(
            r"https?://[^\s|,]+",
            f"{row.get('primary_sources','')} {row.get('secondary_sources','')}",
        ):
            sources.append(
                f'<a class="source-card" href="{escape(url)}" target="_blank" rel="noopener">'
                f'<strong>{escape(urlparse(url).netloc)}</strong><small>Open source</small></a>'
            )
        capabilities = "".join(
            f'<li><strong>{escape(cap["label"])}</strong><span>{escape(cap["status"])}</span>'
            f'<small>{escape(_active_text(cap["note"]))}</small></li>'
            for cap in row["capabilities"].values()
        )
        body = f"""
<section class="page-intro profile-intro"><p class="eyebrow">Company-level competitive relationship</p>
<h2>{escape(row['company'])}</h2><p>{escape(_active_text(row.get('plain_language_description') or row.get('notes')))}</p>
<p class="key-takeaway"><strong>Key takeaway:</strong> {escape(_active_text(row.get('important_clarification') or row.get('unsupported_claims') or 'The available evidence does not resolve every relevant capability or outcome.'))}</p>
<div class="profile-meta"><span>{escape(row['competitive_relationship'])}</span><span>Evidence confidence: {escape(row['overall_confidence'])}</span><span>Last checked: {escape(row['last_checked'])}</span></div></section>
<section class="panel terminology-callout"><h2>Classification context</h2><p>This profile records a <strong>company-level competitive relationship</strong>. If this company also supports a current user workflow, the separate workflow dataset links it by canonical slug rather than duplicating it.</p>
<a href="../alternative-workflows.html">Explore workflow substitutes</a></section>
<div class="profile-layout"><div>
<section class="profile-card"><h2>Company and Job</h2><dl class="field-grid">
<dt>What the company does</dt><dd>{escape(_active_text(row.get('product_model') or row['product_category']))}</dd>
<dt>Job addressed</dt><dd>{escape(row.get('primary_job_solved') or row['bizmatch_jobs_competed_for'])}</dd>
<dt>Target users</dt><dd>{escape(row['target_users'])}</dd><dt>Primary category</dt><dd>{escape(row['primary_category'])}</dd>
<dt>HQ / country</dt><dd>{escape(row['hq_country'])}</dd><dt>Operating area</dt><dd>{escape(row['operating_area'])}</dd>
<dt>Current status</dt><dd>{escape(_active_text(row['current_status']))}</dd>
<dt>Company funding</dt><dd>{escape(row['total_funding'])}</dd><dt>Funding rounds</dt><dd>{escape(row['funding_rounds'])}</dd></dl></section>
<section class="profile-card"><h2>Evidence-supported capability coverage</h2><ul class="capability-list">{capabilities}</ul></section>
<section class="profile-card"><h2>Strengths, limitations, and unknowns</h2><dl class="field-grid">
<dt>Recorded capability</dt><dd>{escape(_active_text(row.get('secondary_capabilities')))}</dd>
<dt>Evidence-supported traction</dt><dd>{escape(row.get('users_traction') or 'Insufficient Evidence')}</dd>
<dt>Important limitation</dt><dd>{escape(_active_text(row.get('important_clarification') or row.get('unsupported_claims')))}</dd>
<dt>Contradictions</dt><dd>{escape(_active_text(row.get('contradictions')))}</dd>
<dt>Canonical research note</dt><dd>{escape(_active_text(row.get('notes')))}</dd></dl></section>
<section class="profile-card"><h2>Sources</h2><div class="source-grid">{''.join(sources) or '<p>Insufficient Evidence: no source URL recorded.</p>'}</div></section>
</div><aside class="sidebox"><p class="eyebrow">Research status</p><h2>{escape(row['research_status'])}</h2>
<p><strong>Evidence confidence:</strong> {escape(row['overall_confidence'])}</p>
<p>Unknown values remain unknown; no numeric relationship or threat score is published.</p>
<a href="../research-table.html">Back to Evidence Library</a></aside></div>"""
        return self.render_page(
            row["company"],
            "Evidence",
            body,
            f"Evidence profile for {row['company']}",
            prefix="../",
            data_prefix="../../../",
        )

    def methodology_page(self):
        body = f"""
<section class="page-intro"><p class="eyebrow">Research governance</p><h2>Methodology & Evidence Boundaries</h2>
<p>The site separates company facts, workflow substitutes, aggregate interview assessment, and active conclusions so that no generated view becomes a competing source of truth.</p>
<p class="key-takeaway"><strong>Key takeaway:</strong> Existence, use, effectiveness, satisfaction, switching intent, and willingness to pay are different evidence dimensions.</p></section>
<section class="panel"><h2>Canonical data flow</h2><div class="data-flow">
<article><strong>36-company landscape</strong><code>competitive-research-tracker.csv</code><span>Validation → XLSX → profiles, evidence, landscape</span></article>
<article><strong>Workflow substitutes</strong><code>substitutes-research.csv</code><code>substitute-evidence.csv</code><code>substitute-workflows.csv</code><span>Validation → workflows, matrix, evidence register</span></article>
<article><strong>Market assessment</strong><code>market-research.json</code><span>Aggregate interview and secondary-research assessment; no participant PII</span></article>
<article><strong>Active conclusions</strong><code>findings-and-implications.json</code><span>Evidence references → findings, overview, executive brief</span></article></div></section>
<section class="panel"><h2>Competitors and substitutes use different lenses</h2>
<div class="assumption-columns"><div><h3>Company-level competitive relationship</h3><p>Classifies each canonical company by its relationship to BizMatch: direct competitor, substitute, feature benchmark, or infrastructure. It does not rank companies.</p></div>
<div><h3>Workflow substitute</h3><p>Maps how a Job is completed through products, people, communities, manual work, supporting infrastructure, or non-adoption. Existing companies link back by canonical slug.</p></div></div></section>
<section class="panel"><h2>Evidence interpretation</h2><div class="evidence-legend">
{self.badge('Independent Behavioral Evidence', 'evidence')} {self.badge('Independent Market Evidence', 'evidence')}
{self.badge('Company Documentation', 'evidence')} {self.badge('Company Claim', 'evidence')}
{self.badge('Community Discussion', 'evidence')} {self.badge('Inference', 'evidence')}
{self.badge('Unverified', 'evidence')} {self.badge('Insufficient Evidence', 'evidence')}</div>
<p>Company documentation establishes a capability or vendor statement. It does not establish adoption, satisfaction, outcomes, or willingness to switch. Inference is always labeled and never rendered as fact.</p></section>
<section class="panel"><h2>Unknown and missing values</h2><p>“Not found” means the research did not find evidence; it is not proof that the capability does not exist. Missing values receive no zero, average, or guessed default. Qualitative confidence describes the evidence supporting a claim, not the attractiveness of a company or market.</p></section>
<section class="panel"><h2>Generated versus manually maintained</h2><p>The canonical CSV and JSON sources are manually maintained under documented validation rules. HTML, XLSX, Markdown registers, profiles, overview, findings, workflow explorer, and executive brief are generated. Generated outputs must never be edited as a substitute for changing their canonical source.</p>
<div class="context-links"><a href="/DATA_INTEGRITY.md">Data integrity</a><a href="/SUBSTITUTE_RESEARCH.md">Substitute methodology</a><a href="/FINDINGS_AND_STRATEGIC_IMPLICATIONS.md">Generated findings report</a></div></section>
<details class="panel deprecated-section"><summary>Deprecated scoring framework — audit context only</summary>
<p>Legacy columns and pre-Phase-0 strategic language remain in historical source material for audit. They do not feed active pages, findings, the landscape, or the executive brief. Numeric relationship scoring remains paused because explicit sourced inputs are absent.</p>
<a href="archive.html">Open the clearly marked Archive</a></details>
<section class="panel"><h2>Current limitations</h2>{_list(self.findings['methodology_limitations'])}</section>"""
        return self.render_page(
            "Methodology & Evidence",
            "Methodology",
            body,
            "Canonical sources, classification rules, evidence labels, and uncertainty handling.",
        )

    def presentation_page(self):
        executive = self.findings["executive_conclusion"]
        jobs = "".join(
            f'<article><span>0{index}</span><h3>{escape(job["title"])}</h3>'
            f'<p>{escape(job["dominant_current_workflow"])}</p>'
            f'<a href="/findings-conclusions/#{escape(job["job_id"].lower())}">Detailed conclusion</a></article>'
            for index, job in enumerate(self.findings["jobs"], 1)
        )
        cross = "".join(
            f'<li><strong>{escape(item["finding"])}</strong><span>{escape(item["interpretation"])}</span>'
            f'<a href="/findings-conclusions/#cross-{index}">Evidence</a></li>'
            for index, item in enumerate(self.findings["cross_market_findings"], 1)
        )
        pressures = "".join(
            f'<article><h3>{escape(item["pressure"])}</h3><p>{escape(item["why_it_matters"])}</p>'
            f'<small>Conclusion confidence: {escape(item["confidence"])}</small></article>'
            for item in self.findings["competitive_pressures"]
        )
        assumptions = lambda items: "".join(
            f'<li><strong>{escape(item["assumption"])}</strong><span>{escape(item["unproven"])}</span></li>'
            for item in items
        )
        boundaries = self.findings["conclusion_boundaries"]
        questions = "".join(
            f'<li><span>{escape(item["priority"])}</span><strong>{escape(self.job_labels[item["job_id"]])}</strong>'
            f'<p>{escape(item["question"])}</p></li>'
            for item in self.findings["customer_discovery"][:5]
        )
        slides = (
            ("question", "Research question", f"<h2>What does BizMatch actually compete with?</h2><p class='slide-lede'>{escape(executive['headline'])}</p><p>The research tests the landscape and current behavior; it does not assume a unified platform is needed.</p>"),
            ("scope", "Scope & methodology", f"<h2>{len(self.rows)} companies. {len(self.substitutes)} substitute patterns. {len(self.evidence)} evidence records. Four Jobs.</h2><p>Company relationships, workflow substitutes, aggregate interviews, and active conclusions remain separate canonical layers.</p><a href='/sites/full-report-site/sources-methodology.html'>Methodology and limitations</a>"),
            ("jobs", "Four Jobs-to-be-Done", f"<h2>Different actors, incentives, and trust requirements</h2><div class='presentation-jobs'>{jobs}</div>"),
            ("landscape", "Competitive landscape", "<h2>No single company explains the competitive pressure</h2><p>Dedicated matching products compete for discovery. Databases, fundraising tools, communities, data rooms, signing tools, and human intermediaries cover other parts of the journey.</p><a href='/sites/full-report-site/category-analysis.html'>Compare the 36-company landscape</a>"),
            ("workflows", "How users solve it today", "<h2>Users assemble workflows from relationships and specialist tools</h2><p>Warm introductions, prior work, communities, direct outreach, spreadsheets, email, meetings, advisers, and controlled-document tools can together complete the Jobs.</p><a href='/sites/full-report-site/alternative-workflows.html'>Explore workflow substitutes</a>"),
            ("pressures", "Strongest substitutes", f"<h2>Behavior beats feature similarity</h2><div class='presentation-pressure-grid'>{pressures}</div>"),
            ("findings", "Cross-market findings", f"<h2>What the evidence suggests</h2><ol class='presentation-findings'>{cross}</ol>"),
            ("strengthened", "Assumptions strengthened", f"<h2>Trust, selective disclosure, and workflow continuity gained support</h2><ul class='presentation-assumptions positive'>{assumptions(self.findings['assumptions_strengthened'])}</ul><a href='/findings-conclusions/#assumptions'>Counterevidence and trace</a>"),
            ("weakened", "Assumptions weakened", f"<h2>Discovery-first and one-marketplace assumptions weakened</h2><ul class='presentation-assumptions negative'>{assumptions(self.findings['assumptions_weakened'])}</ul><a href='/findings-conclusions/#assumptions'>Supporting and opposing evidence</a>"),
            ("boundaries", "What cannot yet be concluded", f"<h2>Current evidence does not justify a product or market verdict</h2>{_list(boundaries['prohibited'], 'presentation-boundaries')}<a href='/findings-conclusions/#boundaries'>Full decision boundary</a>"),
            ("discovery", "Customer Discovery priorities", f"<h2>Test behavior, urgency, and switching—not feature preference</h2><ol class='presentation-questions'>{questions}</ol><a href='/findings-conclusions/#customer-discovery'>Complete research agenda</a>"),
            ("takeaway", "Final research takeaway", f"<h2>{escape(executive['headline'])}</h2><p class='slide-lede'>Current decision: {escape(executive['current_decision'])}</p><p>Evidence suggests narrowing the research before making claims about demand, differentiation, willingness to pay, or marketplace liquidity.</p><a class='button-link primary' href='/findings-conclusions/'>Open complete findings</a>"),
        )
        sections = "".join(
            f'<section class="presentation-slide" id="slide-{index}" data-slide="{index}">'
            f'<div class="slide-label"><span>{index:02d}</span><strong>{escape(label)}</strong></div>'
            f'<div class="slide-content">{content}</div></section>'
            for index, (_anchor, label, content) in enumerate(slides, 1)
        )
        index_links = "".join(
            f'<a href="#slide-{index}" aria-label="Go to section {index}: {escape(label)}">{index:02d}<span>{escape(label)}</span></a>'
            for index, (_anchor, label, _content) in enumerate(slides, 1)
        )
        body = f"""
<div class="presentation-shell" data-presentation>
<aside class="presentation-index" aria-label="Presentation sections"><p><strong>Executive brief</strong><span id="presentationProgress">1 / {len(slides)}</span></p>{index_links}</aside>
<div class="presentation-slides">{sections}</div>
<div class="presentation-controls"><button type="button" class="secondary" data-presentation-prev>Previous</button>
<span aria-live="polite" id="presentationStatus">Section 1 of {len(slides)}</span>
<button type="button" data-presentation-next>Next</button></div></div>"""
        return self.render_page(
            "BizMatch Research — Executive Brief",
            "Presentation",
            body,
            "A concise, evidence-traceable narrative for partners, reviewers, and investors.",
            prefix="../sites/full-report-site/",
            data_prefix="../",
        )
