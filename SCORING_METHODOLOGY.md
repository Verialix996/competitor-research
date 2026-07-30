# Scoring Methodology — Phase 0

## Current status

`relationship_score` is currently `null` for all companies and is displayed as
`Insufficient Evidence`. No company is ranked.

The 65-column canonical schema does not contain explicit, independently sourced
inputs for all required components. Phase 0 therefore removed company-name
lists, word-based price detection, numeric defaults, duplicated UX/maturity
inputs, network-moat proxies for ease, and hand-assigned API/MVP/Build-Buy
values.

## Preserved weights

The weights below are unchanged from the pre-Phase-0 implementation. They are
preserved analytical choices and **require approval** before future scoring.

| Relationship type | Inputs and weights |
|---|---|
| Direct competitor / Substitute | User/use-case overlap 30%; product-process overlap 25%; traction/network effect 20%; geographic/niche fit 10%; business/pricing overlap 10%; technology/AI depth 5% |
| Feature benchmark | Capability quality 30%; maturity 25%; price 15%; UX 15%; ease to integrate/imitate 15% |
| Infrastructure / potential partner | Security 25%; API/integration 20%; pricing 15%; MVP fit 15%; Build-versus-buy 15%; NDA/controlled-disclosure fit 10% |

Formula when all inputs are complete:

```text
relationship_score = sum(component_score * documented_weight)
```

## Required input contract

Every component must eventually have:

- an explicit raw research value;
- a source URL;
- evidence type;
- checked date;
- confidence;
- a documented raw-to-score conversion rule;
- the preserved weight.

The current implementation names these future fields explicitly in
`RELATIONSHIP_SCORE_MODELS`. It does not fall back to legacy scores.

## Missing-data policy

If any required component or its evidence metadata is missing/invalid:

- score value is `null`;
- status is `Insufficient Evidence`;
- missing field names are returned;
- zero, midpoint, average, identity-based value, and keyword-derived value are
  forbidden;
- the company is not ranked.

Comparison is allowed only within the same `competitive_relationship` and only
when every compared company is `Comparable` under the same model and evidence
contract.

## Legacy/deprecated scores

The following canonical columns are historical audit data only:

- `product_overlap_score`
- `feature_maturity_score`
- `market_traction_score`
- `funding_strength_score`
- `ai_depth_score`
- `nda_security_strength_score`
- `network_moat_score`
- `direct_threat_score`

They are excluded from generated site data and active rankings. The old ranker
JavaScript is isolated under `archive/legacy-scoring/`.
