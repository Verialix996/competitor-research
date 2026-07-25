const DATA = window.RANKER_DATA;

const yes = (d, key) => d.features[key] ? 5 : 1;
const boolAvg = (d, keys) => keys.reduce((sum, key) => sum + yes(d, key), 0) / keys.length;
const clamp = value => Math.max(1, Math.min(5, value));
const avg = values => values.reduce((sum, value) => sum + value, 0) / values.length;

function categoryFit(d) {
  if (d.category === 'Direct competitors') return 5;
  if (d.category === 'Cofounder-matching platforms') return 4.4;
  if (d.category === 'Capital & discovery marketplaces') return 4.1;
  if (d.category === 'AI pitch-deck reviewers') return 3.3;
  if (d.category === 'NDA & deal-room tools') return 3.0;
  return 2.5;
}

const CRITERIA = [
  {
    key: 'market_collision',
    label: 'Market collision',
    desc: 'Direct overlap with BizMatch users, jobs-to-be-done, and competitor group',
    why: 'This is the first filter because a weaker product can still be dangerous if it attacks the same founder/investor workflow.',
    score: d => clamp(
      d.product_overlap_score * 0.4 +
      d.direct_threat_score * 0.25 +
      categoryFit(d) * 0.2 +
      boolAvg(d, ['founder_to_founder_flow', 'founder_to_investor_flow']) * 0.15
    )
  },
  {
    key: 'workflow_coverage',
    label: 'Workflow coverage',
    desc: 'How much of the match-to-deal workflow the product already covers',
    why: 'BizMatch is exposed to products that can connect discovery, profiles, matching, data exchange, and signing without forcing users into separate tools.',
    score: d => clamp(
      d.feature_maturity_score * 0.3 +
      boolAvg(d, ['founder_to_founder_flow', 'founder_to_investor_flow']) * 0.25 +
      boolAvg(d, ['data_room', 'e_signature']) * 0.25 +
      boolAvg(d, ['web_app', 'mobile_app']) * 0.2
    )
  },
  {
    key: 'ai_leverage',
    label: 'AI leverage',
    desc: 'Depth of AI matching, scoring, and pitch/deck analysis',
    why: 'The research graph separates AI pitch reviewers from marketplaces, so this criterion rewards companies that can use AI inside an actual matching or capital workflow.',
    score: d => clamp(
      d.ai_depth_score * 0.45 +
      yes(d, 'ai_matching_scoring') * 0.25 +
      yes(d, 'ai_deck_scoring') * 0.2 +
      (d.features.ai_matching_scoring && d.features.ai_deck_scoring ? 5 : 1) * 0.1
    )
  },
  {
    key: 'secure_deal_readiness',
    label: 'Secure deal readiness',
    desc: 'NDA/data-room/e-signature strength for gated collaboration',
    why: 'Data-room and NDA-gated flows are a distinct competitor cluster in the graph, and they matter when BizMatch moves beyond discovery into private deal execution.',
    score: d => clamp(
      d.nda_security_strength_score * 0.55 +
      yes(d, 'data_room') * 0.3 +
      yes(d, 'e_signature') * 0.15
    )
  },
  {
    key: 'traction_resilience',
    label: 'Traction resilience',
    desc: 'Evidence of usage, funding, and defensible network effects',
    why: 'Market traction and network effects decide whether a feature-similar product can keep compounding after BizMatch enters the same surface area.',
    score: d => clamp(
      d.market_traction_score * 0.45 +
      d.network_moat_score * 0.35 +
      d.funding_strength_score * 0.2
    )
  },
  {
    key: 'founder_ux_readiness',
    label: 'Founder UX readiness',
    desc: 'Polished founder-facing usability across web/mobile and match mechanics',
    why: 'The registration-flow assets show that onboarding and interaction quality are part of the competitive surface, not just backend feature coverage.',
    score: d => clamp(
      d.feature_maturity_score * 0.35 +
      boolAvg(d, ['web_app', 'mobile_app']) * 0.25 +
      boolAvg(d, ['swipe_card_interface', 'mutual_match']) * 0.25 +
      d.product_overlap_score * 0.15
    )
  }
];

const PRESETS = {
  recommended: {
    market_collision: 3,
    workflow_coverage: 3,
    traction_resilience: 2,
    ai_leverage: 2,
    secure_deal_readiness: 2,
    founder_ux_readiness: 1
  },
  collision: { market_collision: 3, workflow_coverage: 2, founder_ux_readiness: 1 },
  ai: { ai_leverage: 3, market_collision: 2, workflow_coverage: 1 },
  transaction: { workflow_coverage: 3, secure_deal_readiness: 3, market_collision: 1 },
  all: CRITERIA.reduce((acc, c) => { acc[c.key] = 1; return acc; }, {})
};

const DEFAULT_STATE = { ...PRESETS.recommended };

const FEATURES = [
  { key: 'swipe_card_interface', label: 'Swipe/card interface' },
  { key: 'mutual_match', label: 'Mutual match' },
  { key: 'ai_matching_scoring', label: 'AI matching/scoring' },
  { key: 'ai_deck_scoring', label: 'AI deck scoring' },
  { key: 'founder_to_founder_flow', label: 'Founder-to-founder' },
  { key: 'founder_to_investor_flow', label: 'Founder-to-investor' },
  { key: 'data_room', label: 'Data room' },
  { key: 'e_signature', label: 'E-signature' },
  { key: 'mobile_app', label: 'Mobile app' },
  { key: 'web_app', label: 'Web app' }
];

const CATEGORIES = [...new Set(DATA.map(d => d.category))].sort();
const state = { weights: { ...DEFAULT_STATE }, cats: new Set(CATEGORIES), features: new Set() };

const criteriaExplainerEl = document.querySelector('#criteriaExplainer');
const critListEl = document.querySelector('#critList');
const catListEl = document.querySelector('#catList');
const featListEl = document.querySelector('#featList');
const resultsEl = document.querySelector('#rankerResults');
const summaryEl = document.querySelector('#rankerSummary');

CRITERIA.forEach(c => {
  const card = document.createElement('div');
  card.className = 'ranker-criteria-card';
  card.innerHTML = `<h3>${c.label}</h3><p>${c.why}</p>`;
  criteriaExplainerEl.appendChild(card);
});

function buildCritRow(c) {
  const row = document.createElement('div');
  row.className = 'ranker-crit-row';
  row.dataset.key = c.key;

  const cb = document.createElement('input');
  cb.type = 'checkbox';
  cb.id = 'cb-' + c.key;
  cb.addEventListener('change', () => {
    if (cb.checked) state.weights[c.key] = state.weights[c.key] || 1;
    else delete state.weights[c.key];
    render();
  });

  const label = document.createElement('label');
  label.className = 'ranker-crit-label';
  label.htmlFor = cb.id;
  label.innerHTML = `${c.label}<span class="ranker-crit-desc">${c.desc}</span>`;

  const weightBtns = document.createElement('div');
  weightBtns.className = 'ranker-weight-btns';
  [1, 2, 3].forEach(w => {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'ranker-weight-btn';
    b.textContent = w + 'x';
    b.setAttribute('aria-label', `${c.label} weight ${w}x`);
    b.addEventListener('click', () => {
      state.weights[c.key] = w;
      cb.checked = true;
      render();
    });
    weightBtns.appendChild(b);
  });

  row.append(cb, label, weightBtns);
  critListEl.appendChild(row);
}
CRITERIA.forEach(buildCritRow);

CATEGORIES.forEach(cat => {
  const row = document.createElement('label');
  row.className = 'ranker-cat-row';
  const cb = document.createElement('input');
  cb.type = 'checkbox';
  cb.checked = true;
  cb.addEventListener('change', () => {
    if (cb.checked) state.cats.add(cat); else state.cats.delete(cat);
    render();
  });
  row.append(cb, document.createTextNode(cat));
  catListEl.appendChild(row);
});

FEATURES.forEach(f => {
  const row = document.createElement('label');
  row.className = 'ranker-cat-row';
  const cb = document.createElement('input');
  cb.type = 'checkbox';
  cb.addEventListener('change', () => {
    if (cb.checked) state.features.add(f.key); else state.features.delete(f.key);
    render();
  });
  row.append(cb, document.createTextNode(f.label));
  featListEl.appendChild(row);
});

function syncControls() {
  CRITERIA.forEach(c => {
    const row = critListEl.querySelector(`.ranker-crit-row[data-key="${c.key}"]`);
    const checked = Object.prototype.hasOwnProperty.call(state.weights, c.key);
    const w = state.weights[c.key] || 0;
    row.dataset.checked = checked;
    row.querySelector('input[type="checkbox"]').checked = checked;
    row.querySelectorAll('.ranker-weight-btn').forEach((btn, i) => {
      btn.dataset.active = checked && (i + 1) === w;
    });
  });
}

function tierFor(score) {
  if (score >= 3.4) return 'high';
  if (score >= 2.4) return 'mid';
  return 'low';
}

function scoreCriterion(d, key) {
  return CRITERIA.find(c => c.key === key).score(d);
}

function computeScore(d) {
  const keys = Object.keys(state.weights);
  if (keys.length === 0) return null;
  let sum = 0, wsum = 0;
  keys.forEach(k => {
    const w = state.weights[k];
    sum += scoreCriterion(d, k) * w;
    wsum += w * 5;
  });
  return { raw: sum / Object.values(state.weights).reduce((total, w) => total + w, 0), pct: sum / wsum };
}

function render() {
  syncControls();
  const activeCriteria = CRITERIA.filter(c => Object.prototype.hasOwnProperty.call(state.weights, c.key));
  const requiredFeatures = [...state.features];

  const ranked = DATA
    .filter(d => state.cats.has(d.category))
    .filter(d => requiredFeatures.every(fk => d.features[fk]))
    .map(d => ({ d, score: computeScore(d) }))
    .filter(r => r.score !== null)
    .sort((a, b) => b.score.raw - a.score.raw);

  const critLabel = activeCriteria.length
    ? activeCriteria.map(c => c.label + (state.weights[c.key] > 1 ? ` (${state.weights[c.key]}x)` : '')).join(', ')
    : 'none selected';

  const featLabel = requiredFeatures.length
    ? ` with <strong>${requiredFeatures.length}</strong> required feature${requiredFeatures.length === 1 ? '' : 's'}`
    : '';

  summaryEl.innerHTML = `Ranking <strong>${ranked.length}</strong> of ${DATA.length} companies by ` +
    `<strong>${activeCriteria.length}</strong> criteri${activeCriteria.length === 1 ? 'on' : 'a'}${featLabel} - ` +
    `<span class="ranker-formula">${critLabel}</span>`;

  resultsEl.innerHTML = '';

  if (activeCriteria.length === 0) {
    resultsEl.innerHTML = '<div class="ranker-empty">Select at least one criterion to rank competitors.</div>';
    return;
  }
  if (ranked.length === 0) {
    resultsEl.innerHTML = '<div class="ranker-empty">No companies match the selected segments and required features.</div>';
    return;
  }

  ranked.forEach((r, i) => {
    const row = document.createElement('div');
    row.className = 'ranker-row';
    row.dataset.tier = tierFor(r.score.raw);

    const rank = document.createElement('div');
    rank.className = 'ranker-rank';
    rank.textContent = String(i + 1).padStart(2, '0');

    const main = document.createElement('div');
    main.className = 'ranker-main';

    const top = document.createElement('div');
    top.className = 'ranker-top';
    const name = document.createElement('span');
    name.className = 'ranker-name';
    const nameLink = document.createElement('a');
    nameLink.href = r.d.profile;
    nameLink.textContent = r.d.company;
    name.appendChild(nameLink);
    const tag = document.createElement('span');
    tag.className = 'badge';
    tag.textContent = r.d.category;
    const site = document.createElement('a');
    site.href = r.d.url;
    site.target = '_blank';
    site.rel = 'noopener';
    site.className = 'ranker-site-link';
    site.textContent = 'Official site';
    top.append(name, tag, site);
    main.appendChild(top);

    const bars = document.createElement('div');
    bars.className = 'ranker-crit-bars';
    activeCriteria.forEach(c => {
      const chip = document.createElement('span');
      chip.className = 'ranker-chip';
      const val = scoreCriterion(r.d, c.key);
      chip.innerHTML = `${c.label.split(' ')[0]}` +
        `<span class="ranker-chip-bar"><span class="ranker-chip-fill" style="width:${val / 5 * 100}%"></span></span>` +
        `<span class="ranker-chip-val">${val.toFixed(1)}</span>`;
      bars.appendChild(chip);
    });
    main.appendChild(bars);

    const scoreWrap = document.createElement('div');
    scoreWrap.className = 'ranker-score';
    const scoreVal = document.createElement('div');
    scoreVal.className = 'ranker-score-val';
    scoreVal.textContent = r.score.raw.toFixed(2);
    const track = document.createElement('div');
    track.className = 'ranker-score-track';
    const fill = document.createElement('div');
    fill.className = 'ranker-score-fill';
    fill.style.width = (r.score.pct * 100) + '%';
    track.appendChild(fill);
    scoreWrap.append(scoreVal, track);

    row.append(rank, main, scoreWrap);
    resultsEl.appendChild(row);
  });
}

document.querySelectorAll('.ranker-preset-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    state.weights = { ...PRESETS[btn.dataset.preset] };
    render();
  });
});
document.querySelector('#rankerClear').addEventListener('click', () => { state.weights = {}; render(); });
document.querySelector('#rankerReset').addEventListener('click', () => {
  state.weights = { ...DEFAULT_STATE };
  state.cats = new Set(CATEGORIES);
  state.features = new Set();
  catListEl.querySelectorAll('input').forEach(cb => { cb.checked = true; });
  featListEl.querySelectorAll('input').forEach(cb => { cb.checked = false; });
  render();
});

render();
