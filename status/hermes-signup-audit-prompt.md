# Prompt for Hermes: Post-Signup Required-Field Audit

Paste everything below the line into Hermes.

---

## Task

For the BizMatch competitive research project (`/mnt/ssd/.hermes/atlas/projects/bizmatch-competitive-research/`), the registration-flow screenshots captured so far stop at the point of reaching the signup form — they document what a *visitor* sees, but not what happens *after* an account is actually created (post-signup onboarding often asks for more: company details, team size, funding stage, role, etc.). Your job is to complete real signups on the sites listed below using a Google account where possible, using the fake persona provided, and document every field requested at every step — before and after account creation — through to the first real in-app screen.

Create and maintain a Kanban board for this sub-project, one card per company, so progress is trackable and resumable.

## Kanban board

Create `status/signup-audit-kanban.md` in this project (same style as the existing `status/kanban.md`) with columns:

- **Not started**
- **In progress**
- **Blocked** (CAPTCHA / Cloudflare / phone-verification / manual review queue / other — note which)
- **Completed**
- **Needs review** (ambiguous result, judgment call needed)

One card per company, pulled from `sites/full-report-site/companies/*.html` (36 total). Update the card's column as you work each one. Update the `Updated:` date at the top each session.

## The persona (use consistently across every site)

Use this fake identity everywhere a form asks for personal/company details. It is fictitious — does not correspond to a real person or company — so it's safe to reuse across all 36 signups.

| Field | Value |
|---|---|
| Full name | Jordan Ellis |
| First / Last | Jordan / Ellis |
| Email | `alonshir184@gmail.com`. If a site's email field rejects Gmail "+" aliasing or a form validation error suggests it, that's fine — plain address works everywhere. (Optional: `alonshir184+bizmatch@gmail.com` still delivers to the same inbox and is filterable by alias if a given site accepts it — use it opportunistically, but fall back to the plain address on any rejection rather than treating it as a real blocker.) |
| Google account for OAuth | The Google account behind `alonshir184@gmail.com` — use "Sign in/up with Google" wherever offered instead of filling an email/password form |
| Phone | Use a real receivable number (Google Voice or similar) if SMS verification is required — do not type a fake number into a phone field; if a site requires SMS/phone verification to proceed, that itself is a finding worth recording, and you may stop there and mark the card Blocked rather than forcing it through |
| Password | Generate a unique strong password per site; do not reuse across sites; do not screenshot or publish the password value |
| Company name | Lumen Peak Labs |
| Company website | `https://lumenpeaklabs.example` (placeholder — do not register a real domain) |
| Role / Title | Founder & CEO |
| Company stage | Pre-seed / early-stage (adjust to whatever the dropdown offers if "pre-seed" isn't an option) |
| Location | San Francisco, CA, US |
| Team size | 2-5 |
| LinkedIn | Do not connect a real LinkedIn account. If a LinkedIn URL is a free-text field (not OAuth), leave it blank first and only fill it if the field is required to proceed — note whether it was required or optional |
| "What are you building" / pitch | "AI-assisted scheduling tool for early-stage teams" |

If a site's Google OAuth path skips the profile-detail form entirely (auto-fills from Google), still capture what fields Google prefills / what the site pulls in, and continue into onboarding to see what it asks for that Google didn't supply.

## What to do, per company

1. Start from wherever the existing registration-flow screenshots in `sites/full-report-site/assets/registration-flows/<company>/` left off — don't repeat steps already documented and confirmed accurate (funding/pricing text is out of scope; ignore it).
2. Complete the actual signup using the persona above (Google OAuth first if offered, else email/password).
3. Continue through every onboarding screen after account creation until you reach the first real in-app/dashboard screen, or hit a paywall/gate you can't pass without payment.
4. If you hit a CAPTCHA, Cloudflare challenge, or anti-bot block that the existing screenshots already documented, don't attempt to bypass it — mark the card Blocked and move on.
5. If a step asks for something not on the persona list above, invent a plausible fake value consistent with the persona (fictitious startup, no real identity) and record what was asked.

## Screenshots to take

Continue the existing numbering in `sites/full-report-site/assets/registration-flows/<company>/` (e.g. if the last file is `04-04-foo.png`, your next is `05-05-<slug>.png`). For each company, capture:

1. The actual signup/account-creation form, **filled in** (values visible) but **before submitting**.
2. The immediate post-submit state (welcome screen, verification-pending screen, or straight into onboarding).
3. Every distinct onboarding step that asks for additional info (one screenshot per step/screen, not per field).
4. The first real in-app screen you reach (dashboard, home feed, empty state) — this marks the end of the flow.
5. Any paywall/plan-selection screen if one blocks further progress.

Sanitize every screenshot before saving: no password value visible, no email verification codes/links, no session tokens/cookies visible in dev tools, no browser chrome/URL bar unless the URL itself is the finding (e.g. a redirect worth noting). This matches the sanitization rule already stated on every company page ("credentials, tokens, verification links/codes, browser chrome, and private identifiers are not intentionally published").

## Where to write the results

For each company, append to the existing `<section class="profile-card registration-flow" id="registration-flow">` in `sites/full-report-site/companies/<company>.html`:

- New numbered `<li>` steps continuing the existing list, describing each post-signup screen and exactly what fields/info it required (mark each as required vs optional if the UI distinguishes).
- New `<figure>` entries in the `registration-gallery` div for each new screenshot, following the exact markup pattern already used in that file.
- If the original `Outcome` / `Stop point` in the flow-summary said the flow stopped before account creation, update it to reflect that the flow now continues through to onboarding (or wherever you actually stopped).

Do not touch any other section of the company profile (Profile, Product Flows, Pricing/Funding, Scores, Evidence Notes).

## Definition of done

- Kanban board fully updated, every card in Completed or Blocked (with reason).
- Every company's registration-flow section reflects the full flow through onboarding, or clearly documents why it couldn't go further.
- No real personal data, no real company identity, no live credentials or tokens committed to any screenshot or text.
