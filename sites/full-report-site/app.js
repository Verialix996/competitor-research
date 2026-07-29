const tbody = document.querySelector('#researchTable tbody');
const rows = Array.from(document.querySelectorAll('#researchTable tbody tr.company-row'));
const detailRows = new Map(Array.from(document.querySelectorAll('#researchTable tbody tr.detail-row')).map(row => [row.dataset.detailFor, row]));
const originalOrder = rows.map(row => row.dataset.rowId);
const norm = value => (value || '').toString().toLowerCase();

function clearHighlights(row) {
  row.querySelectorAll('mark[data-search-mark]').forEach(mark => {
    mark.replaceWith(document.createTextNode(mark.textContent));
  });
  row.normalize();
}

function highlight(row, query) {
  clearHighlights(row);
  if (!query) return;
  const cells = Array.from(row.querySelectorAll('td')).slice(0, 9);
  const pattern = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const re = new RegExp(pattern, 'ig');
  cells.forEach(cell => {
    const walker = document.createTreeWalker(cell, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        if (!node.nodeValue || !re.test(node.nodeValue)) return NodeFilter.FILTER_REJECT;
        re.lastIndex = 0;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    const textNodes = [];
    while (walker.nextNode()) textNodes.push(walker.currentNode);
    textNodes.forEach(node => {
      const frag = document.createDocumentFragment();
      let last = 0;
      node.nodeValue.replace(re, (match, offset) => {
        frag.append(document.createTextNode(node.nodeValue.slice(last, offset)));
        const mark = document.createElement('mark');
        mark.dataset.searchMark = 'true';
        mark.textContent = match;
        frag.append(mark);
        last = offset + match.length;
      });
      frag.append(document.createTextNode(node.nodeValue.slice(last)));
      node.replaceWith(frag);
    });
  });
}

function searchFields(row, scope) {
  if (scope === 'companies') return [['Companies', row.dataset.companiesSearch || '']];
  if (scope === 'capabilities') return [['Capabilities', row.dataset.capabilitiesSearch || '']];
  if (scope === 'evidence') return [['Evidence', row.dataset.evidenceSearch || '']];
  return [
    ['Companies', row.dataset.companiesSearch || ''],
    ['Capabilities', row.dataset.capabilitiesSearch || ''],
    ['Evidence', row.dataset.evidenceSearch || ''],
  ];
}

function matchInfo(row, query, scope) {
  if (!query) return { ok: true, rank: 0, reason: '' };
  const company = row.dataset.companyName || '';
  if (company === query) return { ok: true, rank: 100, reason: 'Exact company-name match.' };
  if (company.startsWith(query)) return { ok: true, rank: 90, reason: 'Company-name prefix match.' };
  for (const [label, text] of searchFields(row, scope)) {
    if (text.includes(query)) {
      const hidden = label !== 'Companies';
      return {
        ok: true,
        rank: label === 'Companies' ? 80 : label === 'Capabilities' ? 60 : 40,
        reason: hidden ? `Matched ${label.toLowerCase()} text that is shown in the expanded row details or company profile.` : 'Matched visible company/category text.'
      };
    }
  }
  return { ok: false, rank: -1, reason: '' };
}

function applyFilters() {
  const searchEl = document.querySelector('#search');
  const scopeEl = document.querySelector('#searchScope');
  const relationshipEl = document.querySelector('#relationshipFilter');
  const confidenceEl = document.querySelector('#confidenceFilter');
  const visibleEl = document.querySelector('#visibleCount');
  if (!searchEl || !visibleEl || !tbody) return;

  const query = norm(searchEl.value).trim();
  const scope = scopeEl ? scopeEl.value : 'companies';
  const relationship = relationshipEl ? relationshipEl.value : '';
  const confidence = confidenceEl ? confidenceEl.value : '';
  let visible = 0;

  const ranked = rows.map((row, index) => {
    const info = matchInfo(row, query, scope);
    const rowConfidence = row.dataset.confidence || '';
    let ok = info.ok;
    if (relationship && row.dataset.relationship !== relationship) ok = false;
    if (confidence && rowConfidence !== confidence) ok = false;
    return { row, index, ok, info };
  }).sort((a, b) => {
    if (query) return (b.info.rank - a.info.rank) || (a.index - b.index);
    return originalOrder.indexOf(a.row.dataset.rowId) - originalOrder.indexOf(b.row.dataset.rowId);
  });

  ranked.forEach(({ row, ok, info }) => {
    const details = detailRows.get(row.dataset.rowId);
    row.hidden = !ok;
    if (details) details.hidden = !ok;
    const note = row.querySelector('.match-note');
    if (note) note.textContent = ok && query ? info.reason : '';
    highlight(row, ok ? query : '');
    if (details) {
      tbody.append(row);
      tbody.append(details);
    }
    if (ok) visible += 1;
  });

  visibleEl.textContent = visible;
}

document.querySelectorAll('#search,#searchScope,#relationshipFilter,#confidenceFilter').forEach(el => {
  el.addEventListener('input', applyFilters);
  el.addEventListener('change', applyFilters);
});

const reset = document.querySelector('#resetFilters');
if (reset) {
  reset.addEventListener('click', () => {
    ['#search', '#relationshipFilter', '#confidenceFilter'].forEach(selector => {
      const el = document.querySelector(selector);
      if (el) el.value = '';
    });
    const scope = document.querySelector('#searchScope');
  if (scope) scope.value = 'all';
    applyFilters();
  });
}

applyFilters();
