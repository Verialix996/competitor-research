# BizMatch Signup Audit Kanban (Phase A)

Updated: 2026-07-25

Sub-project board for the **post-signup required-field audit** (`status/hermes-signup-audit-prompt.md`).
One card per company (36 total). Move each card between columns as you work it.
Persona, screenshot rules, and where to write results: see the prompt file.

**Columns:** Not started → In progress → Blocked (note reason) / Completed / Needs review

⚠ = prior visitor-side pass already documented a stop-point (form-gate or anti-bot). A real Google
account may get past identity-field gates, but Cloudflare/CAPTCHA gates will likely still block.

---

## Not started (36)

### Direct competitors
- [ ] Cherub — `companies/cherub.html`
- [ ] CoffeeSpace — `companies/coffeespace.html`
- [ ] Comatch — `companies/comatch.html`
- [ ] SWIP — `companies/swip.html`
- [ ] Swipe Invest — `companies/swipe-invest.html`
- [ ] SwipeDeck — `companies/swipedeck.html`

### Cofounder-matching platforms
- [ ] CoFoundersLab — `companies/cofounderslab.html`
- [ ] Cofounder.org — `companies/cofounder-org.html`
- [ ] FounderCloud — `companies/foundercloud.html`
- [ ] Foundersbase — `companies/foundersbase.html`
- [ ] Tertle — `companies/tertle.html`
- [ ] YC Co-Founder Matching — `companies/yc-co-founder-matching.html`

### Capital & discovery marketplaces
- [ ] AngelList — `companies/angellist.html`
- [ ] Crunchbase — `companies/crunchbase.html`
- [ ] Foundersuite — `companies/foundersuite.html`
- [ ] Gust — `companies/gust.html`
- [ ] OpenVC — `companies/openvc.html`
- [ ] ⚠ Republic — `companies/republic.html` — prior pass hit **Cloudflare** before account creation
- [ ] ⚠ Signal (NFX) — `companies/signal-nfx.html` — form requires real **first/last name** to submit
- [ ] ⚠ StartEngine — `companies/startengine.html` — prior pass hit **Cloudflare 'Verify you are human'**
- [ ] ⚠ Visible.vc — `companies/visible-vc.html` — form requires real **first/last name + company name**

### AI pitch-deck reviewers
- [ ] Evalyze — `companies/evalyze.html`
- [ ] Inodash — `companies/inodash.html`
- [ ] Peachscore — `companies/peachscore.html`
- [ ] PitchBob — `companies/pitchbob.html`
- [ ] PitchGrade — `companies/pitchgrade.html`
- [ ] PitchLeague — `companies/pitchleague.html`
- [ ] SeedBlink — `companies/seedblink.html`
- [ ] Slidebean — `companies/slidebean.html`

### NDA & deal-room tools
- [ ] Ansarada — `companies/ansarada.html`
- [ ] Carta Data Rooms — `companies/carta-data-rooms.html`
- [ ] Digify — `companies/digify.html`
- [ ] ⚠ DocSend — `companies/docsend.html` — prior pass blocked (**HTTP 403 / Cloudflare bot-protection**)
- [ ] Dropbox Sign — `companies/dropbox-sign.html`
- [ ] PandaDoc — `companies/pandadoc.html`
- [ ] SecureDocs — `companies/securedocs.html`

---

## In progress (0)

_none yet_

## Blocked (0)

_none yet — record the block type (CAPTCHA / Cloudflare / phone-verification / manual review / paywall) when you move a card here_

## Completed (0)

_none yet_

## Needs review (0)

_none yet — for ambiguous results / judgment calls_
