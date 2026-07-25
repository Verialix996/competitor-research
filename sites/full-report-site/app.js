
const state = { sortKey: 'company', sortDir: 1 };
const rows = Array.from(document.querySelectorAll('#researchTable tbody tr'));
const allCols = Array.from(document.querySelectorAll('[data-col]')).map(el => el.dataset.col);
const uniqueCols = [...new Set(allCols)];
function norm(x){ return (x || '').toString().toLowerCase(); }
function applyFilters(){
  const q = norm(document.querySelector('#search').value);
  const category = document.querySelector('#categoryFilter').value;
  const feature = document.querySelector('#featureFilter').value;
  let visible = 0;
  rows.forEach(row => {
    const text = norm(row.dataset.search);
    let ok = true;
    if (q && !text.includes(q)) ok = false;
    if (category && row.dataset.category !== category) ok = false;
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
    core: ['company','source_category','target_users','product_category','pricing_model','total_funding','users_traction'],
    flows: ['company','swipe_card_interface','mutual_match','ai_matching_scoring','ai_deck_scoring','founder_to_founder_flow','founder_to_investor_flow','project_profiles','e_signature','messaging_collaboration','mobile_app','web_app'],
    funding: ['company','pricing_model','business_model','total_funding','funding_rounds','investors','funding_source_type','last_funding_date','deals_funding_facilitated'],
    all: uniqueCols
  };
  const active = new Set(sets[preset] || sets.core);
  document.querySelectorAll('.col-toggle').forEach(cb => { cb.checked = active.has(cb.value); toggleCol(cb.value, cb.checked); });
}
document.querySelectorAll('#researchTable th').forEach(th => th.addEventListener('click', () => sortTable(th.dataset.col)));
document.querySelectorAll('#search,#categoryFilter,#featureFilter').forEach(el => el.addEventListener('input', applyFilters));
document.querySelectorAll('.col-toggle').forEach(cb => cb.addEventListener('change', () => toggleCol(cb.value, cb.checked)));
document.querySelector('#resetFilters').addEventListener('click', () => { document.querySelector('#search').value=''; document.querySelector('#categoryFilter').value=''; document.querySelector('#featureFilter').value=''; applyFilters(); });
document.querySelectorAll('[data-preset]').forEach(btn => btn.addEventListener('click', () => setPreset(btn.dataset.preset)));
setPreset('core');
applyFilters();
