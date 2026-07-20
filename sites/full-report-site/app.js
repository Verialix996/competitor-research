
const state = { sortKey: 'company', sortDir: 1 };
const rows = Array.from(document.querySelectorAll('#researchTable tbody tr'));
const allCols = Array.from(document.querySelectorAll('[data-col]')).map(el => el.dataset.col);
const uniqueCols = [...new Set(allCols)];
function norm(x){ return (x || '').toString().toLowerCase(); }
function applyFilters(){
  const q = norm(document.querySelector('#search').value);
  const category = document.querySelector('#categoryFilter').value;
  const confidence = document.querySelector('#confidenceFilter').value;
  const minThreat = parseFloat(document.querySelector('#threatFilter').value || '0');
  const feature = document.querySelector('#featureFilter').value;
  let visible = 0;
  rows.forEach(row => {
    const text = norm(row.dataset.search);
    const threat = parseFloat(row.dataset.directThreat || '0') || 0;
    let ok = true;
    if (q && !text.includes(q)) ok = false;
    if (category && row.dataset.category !== category) ok = false;
    if (confidence && row.dataset.confidence !== confidence) ok = false;
    if (minThreat && threat < minThreat) ok = false;
    if (feature && norm(row.dataset[feature]) !== 'yes') ok = false;
    row.style.display = ok ? '' : 'none';
    if (ok) visible++;
  });
  document.querySelector('#visibleCount').textContent = visible;
}
function sortTable(key){
  if (state.sortKey === key) state.sortDir *= -1; else { state.sortKey = key; state.sortDir = 1; }
  const tbody = document.querySelector('#researchTable tbody');
  rows.sort((a,b) => {
    const av = a.querySelector(`[data-col="${key}"]`)?.dataset.sort || '';
    const bv = b.querySelector(`[data-col="${key}"]`)?.dataset.sort || '';
    const an = parseFloat(av), bn = parseFloat(bv);
    if (!Number.isNaN(an) && !Number.isNaN(bn)) return (an - bn) * state.sortDir;
    return av.localeCompare(bv) * state.sortDir;
  });
  rows.forEach(r => tbody.appendChild(r));
}
function toggleCol(col, show){
  document.querySelectorAll(`[data-col="${col}"]`).forEach(el => { el.style.display = show ? '' : 'none'; });
}
function setPreset(preset){
  const sets = {
    core: ['company','source_category','current_status','account_created','target_users','product_category','pricing_model','total_funding','users_traction','direct_threat_score','source_confidence'],
    flows: ['company','swipe_card_interface','mutual_match','ai_matching_scoring','ai_deck_scoring','founder_to_founder_flow','founder_to_investor_flow','project_profiles','data_room','e_signature','messaging_collaboration','mobile_app','web_app'],
    funding: ['company','pricing_model','business_model','total_funding','funding_rounds','investors','funding_source_type','last_funding_date','deals_funding_facilitated','source_confidence'],
    all: uniqueCols
  };
  const active = new Set(sets[preset] || sets.core);
  document.querySelectorAll('.col-toggle').forEach(cb => { cb.checked = active.has(cb.value); toggleCol(cb.value, cb.checked); });
}
document.querySelectorAll('#researchTable th').forEach(th => th.addEventListener('click', () => sortTable(th.dataset.col)));
document.querySelectorAll('#search,#categoryFilter,#confidenceFilter,#threatFilter,#featureFilter').forEach(el => el.addEventListener('input', applyFilters));
document.querySelectorAll('.col-toggle').forEach(cb => cb.addEventListener('change', () => toggleCol(cb.value, cb.checked)));
document.querySelector('#resetFilters').addEventListener('click', () => { document.querySelector('#search').value=''; document.querySelector('#categoryFilter').value=''; document.querySelector('#confidenceFilter').value=''; document.querySelector('#threatFilter').value=''; document.querySelector('#featureFilter').value=''; applyFilters(); });
document.querySelectorAll('[data-preset]').forEach(btn => btn.addEventListener('click', () => setPreset(btn.dataset.preset)));
setPreset('core');
applyFilters();
