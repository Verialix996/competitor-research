# BizMatch Substitute Research — Phase 1

## Research boundary

This phase examines how people currently pursue four Jobs without assuming they
need a dedicated BizMatch-like matching platform:

1. `JOB-COFOUNDER` — founder seeking a co-founder.
2. `JOB-FOUNDER-INVESTOR` — founder seeking an investor.
3. `JOB-INVESTOR-SOURCING` — investor sourcing startups or founders.
4. `JOB-TRUSTED-PROGRESSION` — founder and investor progressing from discovery
   to a trusted interaction.

The work is based on repository commit
`bc9e4701e01367b84329374aa87607d029d355f6`. Phase 0 reconciliation
decisions, the 36-company canonical tracker, legacy-score isolation, and
relationship-score handling were not changed.

This is not a White Space analysis, a product-market-fit conclusion, an MVP
recommendation, or a Build/Buy decision. “Evidence suggests” below means that
the cited evidence supports a bounded interpretation; it does not mean the
claim was proven for BizMatch’s target market.

## Canonical data model

Phase 1 uses a separate normalized research layer:

- `data/substitutes-research.csv` — one row per substitute pattern.
- `data/substitute-evidence.csv` — one row per material evidence claim.
- `data/substitute-workflows.csv` — one row per Job and workflow stage.

The entity table is the entry point; evidence and workflow tables are canonical
children linked by IDs. Pipe (`|`) separates multiple values. Existing
companies such as Crunchbase, OpenVC, DocSend, Dropbox Sign, and the YC
ecosystem are linked to canonical competitor slugs rather than inserted again
into the 36-company tracker.

Generated, non-editable views:

- `SUBSTITUTE_MATRIX.md`
- `SUBSTITUTE_WORKFLOWS.md`
- `SUBSTITUTE_EVIDENCE_REGISTER.md`
- `sites/full-report-site/alternative-workflows.html`
- `sites/full-report-site/substitutes-data.js`

## Classification method

Classification is based on the Job and workflow covered, not marketing
language:

- `Direct Competitor` — intentionally serves the same core audience and owns
  bilateral matching plus material parts of the relationship workflow.
- `Adjacent Competitor` — purpose-built for a relevant Job but does not own the
  whole BizMatch relationship.
- `Workflow Substitute` — replaces a sequence of user actions across one or
  more stages.
- `Service Substitute` — a person or organization performs the work using
  judgment, relationships, or managed execution.
- `Community/Network Substitute` — value depends primarily on membership,
  relationships, reputation, or social density.
- `Manual Process` — users execute and coordinate the work themselves.
- `Do Nothing` — users defer, continue the current process, change the Job, or
  stop.
- `Infrastructure Tool` — replaces a bounded technical step such as search,
  tracking, scheduling, signing, analysis, or disclosure.
- `Unclear` — evidence is insufficient to classify.

Qualitative strength is constrained to `Strong Substitute`, `Partial
Substitute`, `Weak Substitute`, `Complementary Tool`, or `Insufficient
Evidence`. No numeric score is calculated.

A strong substitute has evidence of broad Job coverage, embedded adoption, a
trust or network advantage, meaningful switching cost, or the ability to
complete a critical process. It need not be pleasant or efficient. Manual work
is not treated as failure merely because it is manual.

## Evidence method

The evidence register separates:

- existence of a solution;
- observed use;
- effectiveness;
- satisfaction;
- active search for an alternative; and
- willingness to pay or change behavior.

These are not interchangeable. Vendor pages establish capabilities or Company
Claims. Community discussions provide user reports or hypotheses but are not
representative samples. Inference is labeled and is not presented as fact.

The strongest behavioral evidence in this phase includes:

- a survey of 889 institutional VCs at 681 firms documenting network-heavy
  sourcing and a multi-stage investment funnel (`EV-001`–`EV-003`);
- a randomized field experiment involving 4,500 early-stage investors and
  nearly 17,000 emails (`EV-034`);
- a field setting showing that investor exposure can affect later fundraising,
  with unequal effects across participants (`EV-029`);
- an entrepreneurial-alumni survey and interviews documenting use and mixed
  effectiveness of LinkedIn, Facebook, WhatsApp, alumni networks, and in-person
  networking (`EV-004`, `EV-005`);
- entrepreneurial-team research showing effects of shared education and prior
  work experience (`EV-006`);
- a six-founder interview study documenting both hackathon benefits and weak
  continuity (`EV-010`, `EV-011`).

Important limitations:

- the largest VC-practice survey was fielded in 2015–2016;
- several studies use selective populations such as institutional VCs, MBA
  students, one alumni network, or one competition;
- Reddit evidence is self-selected and anecdotal;
- vendor documentation does not prove adoption, satisfaction, or outcomes;
- this phase did not create accounts, contact users, or observe private groups;
- no evidence collected here estimates Israeli target-market prevalence,
  conversion, willingness to pay, or switching intent.

## Findings by Job

### 1. Founder seeking a co-founder

#### Current process

Evidence suggests a common path starts inside an existing social graph:
friends, former coworkers, classmates, alumni, professional communities, and
friends-of-friends. Founders then widen discovery through LinkedIn, private or
public communities, meetups, accelerators, and events. Screening relies on work
history, mutual contacts, portfolios, references, role expectations, and
repeated conversation. Some founders use a side project or hackathon to observe
actual contribution before discussing equity.

The high-trust path is rarely just profile → match → commitment. It is more
often:

`known context or referral → initial conversation → repeated interaction or
trial work → references and expectation-setting → legal commitment or fallback`

The full stage-by-stage map is generated in `SUBSTITUTE_WORKFLOWS.md`.

#### Strong substitutes

| Substitute | Why it appears strong | Evidence boundary |
| --- | --- | --- |
| Friends, former coworkers, and friends-of-friends | Prior work and shared context supply behavioral information and social accountability that a profile cannot recreate. | Academic team-formation evidence supports association, not universal team quality (`EV-006`); user stories are anecdotal (`EV-008`). |
| Alumni, university, local, and professional communities | Shared affiliation creates reachable candidates, trust transfer, and local density. | Access is unequal and homophily can narrow diversity (`EV-006`, `EV-029`). |
| LinkedIn plus direct contact | Broad search, professional history, mutual connections, groups, and messaging already exist in one familiar identity graph. | Independent survey evidence supports use, but reports mixed effectiveness for fundraising and talent sourcing (`EV-004`, `EV-005`). |
| Hackathons, side projects, and work trials | Real work reveals execution, communication, and reliability before founder-level commitment. | Small interview evidence also documents team attrition, project abandonment, short duration, and IP concerns (`EV-010`, `EV-011`). |
| Build solo or hire | It changes the Job rather than solving matching; Carta’s dataset shows this is a material observed path. | Carta is a Company Claim based on its customer data and does not prove superiority (`EV-032`). |

#### Supported advantages

- Existing ties can provide richer trust and compatibility signals than a
  self-authored profile (`EV-006`, `EV-008`, `EV-009`).
- LinkedIn and established communication channels have low onboarding cost and
  existing identity context (`EV-004`, `EV-012`, `EV-013`).
- Trial collaboration can produce direct behavioral evidence (`EV-009`,
  `EV-010`).
- Communities can support repeated interaction and referrals, especially when
  curated or private (`EV-014`), though the evidence is low confidence.

#### Supported failures or constraints

- Network-based formation can reproduce homophily and unequal access
  (`EV-006`, `EV-029`).
- Open groups may degrade into spam or low-signal promotion (`EV-015`), based
  on low-confidence community reports.
- Hackathon relationships and projects do not necessarily persist
  (`EV-011`).

#### Not established

This phase did not establish how many founders lack a usable network, how long
the search takes, which verification signals predict durable teams, whether
founders will disclose enough for algorithmic matching, or whether a Swipe
interface increases or reduces seriousness.

### 2. Founder seeking an investor

#### Current process

The observed stack is modular:

1. define the round and target criteria;
2. build a list through investor databases, fund sites, LinkedIn, portfolio
   research, events, programs, advisers, and referrals;
3. identify warm paths and record targets in a spreadsheet, Notion, Airtable,
   or fundraising CRM;
4. request a warm introduction or send targeted cold email;
5. share a one-pager or deck and hold repeated conversations;
6. grant deeper document access as interest increases;
7. progress through references, diligence, partner review, terms, and legal
   close—or bootstrap, defer, or continue nurturing.

#### Strong substitutes

| Substitute | Why it appears strong | Evidence boundary |
| --- | --- | --- |
| Warm introductions | VC sourcing evidence assigns a large role to professional networks, other investors, and portfolio companies. The introducer transfers attention and context. | Warm paths are not the only path: proactive sourcing was also material, and cold outreach remains a documented practice (`EV-001`, `EV-022`). |
| Investor databases and manual research | Structured filtering plus fund and portfolio research can identify target investors without mutual matching. | Product documentation proves capability, not data completeness or successful fundraising (`EV-020`, `EV-021`). |
| Accelerators and demo days | Selection, coaching, community, investor access, and reputation are bundled in a human-supported process. | YC documentation is a strong workflow example but is not representative of every program (`EV-018`, `EV-019`). |
| Fundraising advisers and trusted professionals | Human operators can combine materials, targeting, introductions, follow-up, and negotiation. | Quality and incentives vary; U.S. broker-dealer rules may apply to some compensation arrangements (`EV-030`, `EV-031`). |
| Lightweight CRM and email | A spreadsheet or Notion plus email can be sufficient to run a bounded pipeline. | Evidence is current but anecdotal and does not establish outcome quality (`EV-016`). |

#### Supported advantages

- Network context and known referrers can improve access (`EV-001`, `EV-029`).
- Existing databases and productivity tools let founders control criteria and
  retain their data (`EV-016`, `EV-020`, `EV-021`).
- Cold email can reach beyond the existing network; it is not defensible to
  claim that all investor contact requires a warm introduction (`EV-022`).
- Data rooms, signature tools, scheduling, and general AI already replace
  bounded workflow steps (`EV-023`–`EV-028`).

#### Supported failures or constraints

- Access to investors is unequal, and exposure effects need not benefit every
  group equally (`EV-029`).
- Network use produced both effective and unsuccessful fundraising reports in
  one survey (`EV-005`).
- Community reports describe cold-outreach noise and inconsistent response,
  but no representative response-rate estimate was found (`EV-017`).
- Early-stage VC NDAs can create enough administrative or conflict friction
  that an investor declines the process (`EV-026`).

#### Not established

There is insufficient evidence that founders want one integrated product
instead of their current stack, that fragmentation reduces funding outcomes,
that AI pitch review improves investor response, or that founders will pay to
replace relationships and manual control.

### 3. Investor sourcing startups or founders

#### Current process

The strongest end-to-end substitute is the investor’s existing operating
system, not a single public product:

`fund thesis → network and proactive sourcing → originator screen → management
meeting(s) → partner review → references, market work, peer comparison and
document diligence → term sheet → legal close or rejection/nurture`

The NBER survey found that network sources and proactive generation dominated
company-management inbound in its sample (`EV-001`). It also documented roughly
100 considered opportunities for each closed deal at the median firm
(`EV-002`), with substantial diligence time and reference calls (`EV-003`).
The randomized AngelList experiment found that founding-team information
causally affected average investor response (`EV-034`).

#### Strong substitutes

| Substitute | Why it appears strong | Evidence boundary |
| --- | --- | --- |
| Internal sourcing and selection funnel | It integrates fund-specific judgment, governance, partner review, references, and legal accountability. | The primary survey is older and institutionally weighted (`EV-001`–`EV-003`). |
| Professional and portfolio networks | They supply contextual, filtered deal flow and reputation transfer. | Network quality varies and can reinforce unequal access. |
| Proactive research plus databases | Investors do not depend only on inbound; structured data supports active market mapping and screening. | Database effectiveness is not independently isolated here. |
| Curated programs and demo days | Selection and cohort reputation create dense, reviewable deal flow. | Company documentation establishes the mechanism, not universal return or selection quality. |

#### Supported advantages

- The current process is tailored to a fund’s thesis and governance.
- Human review can evaluate team, context, references, and conflicts that a
  generic feed may not encode (`EV-002`, `EV-034`).
- Existing networks, databases, CRM, meetings, data rooms, and professional
  review already interoperate, even when the handoffs are manual.

#### Supported failures or constraints

- Sourcing and diligence are resource-intensive (`EV-001`–`EV-003`).
- Network access can create systematic frictions and unequal exposure
  (`EV-029`).
- High-volume funnels discard most opportunities; the evidence does not show
  that a new feed would improve selection rather than add volume (`EV-002`).

#### Not established

This phase did not determine whether Israeli angels, micro-VCs, corporate VCs,
family offices, and institutional funds use the same workflow; whether they
want additional inbound; what would cause them to trust a new source; or what
verified signal would justify joining a new two-sided platform.

### 4. Progressing from discovery to trusted interaction

#### Current process

Trust is assembled from multiple mechanisms:

- referrer and institutional reputation;
- professional history and shared affiliations;
- repeated conversations and consistent follow-through;
- references from customers, founders, colleagues, and investors;
- staged disclosure;
- narrow legal agreements when context requires them;
- controlled document access and audit trails;
- partner, lawyer, accountant, and expert review;
- written decisions, signed documents, and explicit next actions.

Infrastructure tools cover the technical transitions well:

- Calendly and calendars cover scheduling (`EV-023`);
- DocSend and data rooms cover controlled disclosure and access history
  (`EV-024`);
- Dropbox Sign and similar tools cover signature and audit trails (`EV-025`);
- ChatGPT and general AI can analyze supplied files or prepare summaries
  (`EV-028`).

These tools do not independently verify that supplied information is true,
create bilateral trust, or cause follow-through.

#### Strong and complementary substitutes

| Substitute | Role | Strength |
| --- | --- | --- |
| Human references, advisers, lawyers, and investor teams | Contextual verification, judgment, accountability, and negotiation | Strong Substitute |
| Secure links and virtual data rooms | Progressive disclosure, permissions, access audit, and diligence organization | Complementary Tool |
| E-signature and standard NDA templates | Bounded contract-execution step | Complementary Tool |
| Calendly plus video meetings | Bounded scheduling and meeting step | Complementary Tool |
| General AI assistants | Research synthesis, drafting, review, and briefing from supplied material | Complementary Tool |

#### Supported failures or constraints

- Diligence can take significant time and multiple references (`EV-003`).
- A universal early NDA workflow conflicts with documented VC practice
  (`EV-026`).
- Technical access control does not establish the truth or quality of the
  information being shared (`EV-024` is capability evidence only).

#### Not established

Ghosting prevalence, disclosure willingness, trust in platform verification,
value of an AI-generated diligence brief, and the conversion effect of a
unified match-to-meeting workflow remain hypotheses requiring validation.

## Cross-Job assessment

### What appears “good enough”

Evidence suggests that a modular stack can be good enough for many individual
steps:

- LinkedIn or databases for discovery;
- referrals and communities for access and trust;
- email and messaging for contact;
- spreadsheets or CRM for state;
- Calendly and video tools for meetings;
- data rooms for controlled disclosure;
- e-signature for agreements;
- general AI for research and review;
- lawyers, accountants, advisers, mentors, and internal investment teams for
  judgment.

The research does not show that this stack is good enough for every user, nor
that dissatisfaction with handoffs creates willingness to adopt a new product.

### Evidence-backed weaknesses

- network access and benefits are uneven (`EV-006`, `EV-029`);
- some open communities accumulate spam or lose trust (`EV-015`, low
  confidence);
- hackathon teams and projects may not persist (`EV-011`);
- investor sourcing and diligence consume substantial resources (`EV-001`–
  `EV-003`);
- early-stage VC NDA requests can create friction (`EV-026`);
- professional networks produce mixed outcomes, not universal success
  (`EV-005`).

### Pain hypotheses, not established facts

- cross-tool fragmentation causes material information loss;
- ghosting is a dominant failure mode;
- founders cannot compare candidates effectively;
- investors want a new source of deal flow;
- founders will reveal enough private information for accurate matching;
- Swipe lowers or raises perceived seriousness;
- AI matching improves compatibility;
- AI pitch review improves fundraising;
- a unified workflow improves meeting or investment conversion;
- either side will pay or migrate its existing network and history.

## Red Team questions

### 1. Could LinkedIn + WhatsApp + email + general AI be good enough?

- Supporting evidence: independent survey evidence shows extensive use of
  LinkedIn, Facebook, and WhatsApp; product documentation confirms search,
  messaging, file analysis, and scheduling capabilities (`EV-004`, `EV-012`,
  `EV-013`, `EV-023`, `EV-028`).
- Counterevidence: network outcomes were mixed and the stack does not by itself
  provide references, diligence, or verified intent (`EV-005`).
- Unknown: how target users combine the tools, completion rates, satisfaction,
  and switching intent.
- Future Customer Discovery: reconstruct recent successful and failed journeys
  from target users and quantify tool handoffs, repeated work, and points they
  would pay to remove.

### 2. Is the real value warm introductions rather than matching?

- Supporting evidence: network and referral sources dominate the observed VC
  sourcing mix; shared ties also matter in team formation (`EV-001`, `EV-006`).
- Counterevidence: proactive investor sourcing was also material, and cold email
  remains a documented path (`EV-001`, `EV-022`).
- Unknown: whether a platform can create trusted introductions without already
  possessing the relevant network.
- Future Customer Discovery: compare introduced, cold, event, and platform
  contacts on acceptance, meeting, and follow-through while controlling for
  pre-existing fit.

### 3. Do investors want filtered trusted deal flow rather than another feed?

- Supporting evidence: investor funnels rely on trusted sources, originator
  screening, partner review, and references (`EV-001`–`EV-003`).
- Counterevidence: proactive research and quantitative sourcing exist; investors
  already use databases and curated demo-day interfaces.
- Unknown: appetite by investor type and what minimum verification would make a
  new source worth attention.
- Future Customer Discovery: interview angels, scouts, micro-VCs, and
  institutional investors separately about current inbound, rejection logic,
  and acceptable feed volume.

### 4. Will founders disclose enough for useful matching?

- Supporting evidence for concern: sensitive financial, product, team, and
  growth information is part of fundraising, while NDA expectations can
  conflict (`EV-026`).
- Counterevidence: progressive deck and data-room disclosure is an established
  capability (`EV-024`).
- Unknown: the minimum data founders will share before knowing the recipient,
  and whether that minimum is predictive.
- Future Customer Discovery: use disclosure ladders with explicit fields and
  ask founders what they would share publicly, after mutual interest, after
  verification, and after NDA.

### 5. Does an early NDA create friction rather than trust?

- Supporting evidence: legal-practice guidance says most early-stage VCs do not
  sign NDAs and may pass rather than negotiate (`EV-026`).
- Counterevidence: NDAs are common in partnerships, sales, hiring, later-stage
  fundraising, M&A, or specific trade-secret disclosure; standard terms may
  reduce friction (`EV-027`).
- Unknown: BizMatch’s mix of co-founder, partnership, and investor contexts and
  the appropriate trigger for each.
- Future Customer Discovery: test context-specific NDA expectations, not a
  universal gate.

### 6. Does Swipe reduce perceived seriousness?

- Supporting evidence: only low-confidence community analogy was found; it is
  not sufficient to support the claim.
- Counterevidence: existing direct competitors use card or Swipe mechanics, but
  their adoption claims do not establish business seriousness or outcomes.
- Unknown: perceived seriousness, information adequacy, and decision quality by
  persona and stage.
- Future Customer Discovery: compare the same candidate set in card, list, and
  referral formats using qualitative interviews and behavioral tasks.

### 7. Is the main problem verification, trust, or follow-through rather than discovery?

- Supporting evidence: investors devote substantial resources to team
  evaluation, references, and diligence; team information causally affected
  investor response (`EV-003`, `EV-034`).
- Counterevidence: database and network search remain active work, and founders
  without a network report discovery difficulty.
- Unknown: which stage creates the largest abandoned-value pool for each Job.
- Future Customer Discovery: stage-code recent journeys and identify the last
  completed step before abandonment.

### 8. Could one side receive value while the other lacks a reason to join?

- Supporting evidence: none collected directly. This remains a two-sided-market
  hypothesis.
- Counterevidence: trusted programs and networks can create reasons for both
  sides through curation, reputation, and exclusive access (`EV-018`,
  `EV-019`), but this is not evidence for BizMatch.
- Unknown: minimum viable value and participation cost for each side.
- Future Customer Discovery: test founder and investor value propositions
  separately before any joint-market conclusion.

### 9. Is the strongest substitute human and non-self-service?

- Supporting evidence: warm introductions, professional communities, advisers,
  references, partner review, and legal counsel cover trust-heavy stages
  (`EV-001`–`EV-003`, `EV-005`, `EV-030`, `EV-031`).
- Counterevidence: databases, email, scheduling, data rooms, signatures, and AI
  already automate bounded steps; proactive sourcing is material.
- Unknown: which human judgments can be standardized without losing trust or
  context.
- Future Customer Discovery: identify the exact decision each intermediary
  makes and test assisted rather than fully automated alternatives.

### 10. Are the Jobs too different for one coherent product?

- Supporting evidence: co-founder formation emphasizes compatibility and trial
  work; founder fundraising emphasizes targeting and access; investor sourcing
  emphasizes a fund-specific funnel; trusted progression emphasizes references,
  disclosure, and diligence.
- Counterevidence: identity, contact, meetings, documents, and follow-up recur
  across Jobs, and programs can bundle multiple stages.
- Unknown: whether shared primitives create enough value without making the
  product incoherent.
- Future Customer Discovery: evaluate each Job as a separate proposition and
  test cross-Job reuse only after independent demand is observed.

## Customer Discovery backlog

The following questions require interviews or observational research and were
not answered in this phase:

1. What was the last real co-founder or investor journey the participant
   attempted, and where did it stop?
2. Which tools and people were used at each step, including private groups?
3. What information was re-entered, lost, or intentionally withheld?
4. Which trust signal changed the participant’s willingness to meet, disclose,
   or proceed?
5. What false positive consumed the most time?
6. What successful outcome occurred without a dedicated matching product?
7. What would the user refuse to delegate to an algorithm?
8. What would make an investor accept a new source of opportunities?
9. Under what context would an NDA be appropriate, premature, or unacceptable?
10. Would the participant change behavior, import history, invite the other
    side, or pay—and for which bounded outcome?

No Mystery Shopping, account creation, outreach, survey, customer interview, or
product-priority work was performed.
