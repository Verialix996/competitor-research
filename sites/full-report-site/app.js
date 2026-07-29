
const rows = Array.from(document.querySelectorAll('#researchTable tbody tr'));
const norm = value => (value || '').toString().toLowerCase();

function applyFilters() {
  const searchEl = document.querySelector('#search');
  const relationshipEl = document.querySelector('#relationshipFilter');
  const confidenceEl = document.querySelector('#confidenceFilter');
  const visibleEl = document.querySelector('#visibleCount');
  if (!searchEl || !visibleEl) return;

  const query = norm(searchEl.value);
  const relationship = relationshipEl ? relationshipEl.value : '';
  const confidence = confidenceEl ? confidenceEl.value : '';
  let visible = 0;

  rows.forEach(row => {
    const rowConfidence = row.dataset.confidence || '';
    let ok = true;
    if (query && !norm(row.dataset.search).includes(query)) ok = false;
    if (relationship && row.dataset.relationship !== relationship) ok = false;
    if (confidence && !rowConfidence.includes(confidence)) ok = false;
    row.hidden = !ok;
    if (ok) visible += 1;
  });

  visibleEl.textContent = visible;
}

document.querySelectorAll('#search,#relationshipFilter,#confidenceFilter').forEach(el => {
  el.addEventListener('input', applyFilters);
});

const reset = document.querySelector('#resetFilters');
if (reset) {
  reset.addEventListener('click', () => {
    ['#search', '#relationshipFilter', '#confidenceFilter'].forEach(selector => {
      const el = document.querySelector(selector);
      if (el) el.value = '';
    });
    applyFilters();
  });
}

applyFilters();
