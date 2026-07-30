const DATA = window.RANKER_DATA;

const CRITERIA = [
  { key: 'product_overlap_score', label: 'Product overlap', desc: 'How closely the product maps to BizMatch' },
  { key: 'feature_maturity_score', label: 'Feature maturity', desc: 'Depth/polish of shipped features' },
  { key: 'market_traction_score', label: 'Market traction', desc: 'Users, activity, momentum' },
  { key: 'funding_strength_score', label: 'Funding strength', desc: 'Capital raised and runway' },
  { key: 'ai_depth_score', label: 'AI depth', desc: 'Sophistication of AI matching/scoring' },
  { key: 'network_moat_score', label: 'Network moat', desc: 'Defensibility from network effects' }
];

const PRESETS = {
  recommended: {
    product_overlap_score: 3,
    market_traction_score: 3,
    feature_maturity_score: 2,
    ai_depth_score: 2,
    funding_strength_score: 2,
    network_moat_score: 1
  },
  ai: { ai_depth_score: 1, product_overlap_score: 1, feature_maturity_score: 1 },
  growth: { market_traction_score: 1, funding_strength_score: 1, network_moat_score: 1 },
  all: CRITERIA.reduce((acc, c) => { acc[c.key] = 1; return acc; }, {})
};
// Default ranking: product overlap and market traction carry the most weight
// (strongest direct evidence of real competitive collision), feature maturity,
// AI depth, and funding strength count moderately, network moat least - moat
// determines defensibility over time rather than immediate threat.
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

const critListEl = document.querySelector('#critList');
const catListEl = document.querySelector('#catList');
const featListEl = document.querySelector('#featList');
const resultsEl = document.querySelector('#rankerResults');
const summaryEl = document.querySelector('#rankerSummary');

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
    b.textContent = w + '×';
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
    const checked = state.weights.hasOwnProperty(c.key);
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

function computeScore(d) {
  const keys = Object.keys(state.weights);
  if (keys.length === 0) return null;
  let sum = 0, wsum = 0, wTotal = 0;
  keys.forEach(k => {
    const w = state.weights[k];
    sum += d[k] * w;
    wsum += w * 5;
    wTotal += w;
  });
  return { raw: sum / wTotal, pct: sum / wsum };
}

function render() {
  syncControls();
  const activeCriteria = CRITERIA.filter(c => state.weights.hasOwnProperty(c.key));

  const requiredFeatures = [...state.features];

  const ranked = DATA
    .filter(d => state.cats.has(d.category))
    .filter(d => requiredFeatures.every(fk => d.features[fk]))
    .map(d => ({ d, score: computeScore(d) }))
    .filter(r => r.score !== null)
    .sort((a, b) => b.score.raw - a.score.raw);

  const critLabel = activeCriteria.length
    ? activeCriteria.map(c => c.label + (state.weights[c.key] > 1 ? ` (${state.weights[c.key]}×)` : '')).join(', ')
    : 'none selected';

  const featLabel = requiredFeatures.length
    ? ` with <strong>${requiredFeatures.length}</strong> required feature${requiredFeatures.length === 1 ? '' : 's'}`
    : '';

  summaryEl.innerHTML = `Ranking <strong>${ranked.length}</strong> of ${DATA.length} companies by ` +
    `<strong>${activeCriteria.length}</strong> criteri${activeCriteria.length === 1 ? 'on' : 'a'}${featLabel} &mdash; ` +
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
    site.textContent = 'Official site ↗';
    top.append(name, tag, site);
    main.appendChild(top);

    const bars = document.createElement('div');
    bars.className = 'ranker-crit-bars';
    activeCriteria.forEach(c => {
      const chip = document.createElement('span');
      chip.className = 'ranker-chip';
      const val = r.d[c.key];
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
