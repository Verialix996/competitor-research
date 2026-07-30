(() => {
  const normalize = value => (value || '').toString().toLowerCase().trim();
  const includesValue = (haystack, needle) =>
    !needle || (haystack || '').split('|').includes(needle);

  function setQuery(params) {
    const url = new URL(window.location.href);
    Object.entries(params).forEach(([key, value]) => {
      if (value) url.searchParams.set(key, value);
      else url.searchParams.delete(key);
    });
    window.history.replaceState({}, '', `${url.pathname}${url.search}${url.hash}`);
  }

  function setupSubstituteExplorer() {
    const grid = document.querySelector('#substituteGrid');
    if (!grid) return;
    const items = Array.from(grid.querySelectorAll('[data-explorer-item]'));
    const fields = {
      q: document.querySelector('#substituteSearch'),
      job: document.querySelector('#substituteJob'),
      category: document.querySelector('#substituteCategory'),
      strength: document.querySelector('#substituteStrength'),
      status: document.querySelector('#substituteStatus'),
      stage: document.querySelector('#substituteStage'),
    };
    const params = new URLSearchParams(window.location.search);
    Object.entries(fields).forEach(([key, field]) => {
      if (field && params.has(key)) field.value = params.get(key);
    });

    const apply = () => {
      const values = Object.fromEntries(
        Object.entries(fields).map(([key, field]) => [key, field ? field.value : ''])
      );
      let visible = 0;
      items.forEach(item => {
        const searchable = `${item.dataset.name} ${item.dataset.category} ${item.dataset.classification} ${item.dataset.persona}`;
        const show =
          (!values.q || normalize(searchable).includes(normalize(values.q))) &&
          includesValue(item.dataset.jobs, values.job) &&
          (!values.category || item.dataset.category === values.category) &&
          (!values.strength || item.dataset.strength === values.strength) &&
          (!values.status || item.dataset.status === values.status) &&
          includesValue(item.dataset.stages, values.stage);
        item.hidden = !show;
        if (show) visible += 1;
      });
      document.querySelector('#substituteCount').textContent = visible;
      document.querySelector('#substituteEmpty').hidden = visible !== 0;
      setQuery(values);
    };
    Object.values(fields).forEach(field => {
      if (!field) return;
      field.addEventListener('input', apply);
      field.addEventListener('change', apply);
    });
    document.querySelector('#resetSubstituteFilters')?.addEventListener('click', () => {
      Object.values(fields).forEach(field => { if (field) field.value = ''; });
      apply();
    });
    document.querySelectorAll('[data-view]').forEach(button => {
      button.addEventListener('click', () => {
        const expanded = button.dataset.view === 'expanded';
        grid.classList.toggle('expanded', expanded);
        grid.querySelectorAll(':scope > article > details').forEach(detail => {
          detail.open = expanded;
        });
        document.querySelectorAll('[data-view]').forEach(candidate => {
          candidate.setAttribute('aria-pressed', String(candidate === button));
        });
      });
    });
    apply();
  }

  function setupLandscapeExplorer() {
    const grid = document.querySelector('#landscapeGrid');
    if (!grid) return;
    const items = Array.from(grid.querySelectorAll('[data-explorer-item]'));
    const fields = {
      lq: document.querySelector('#landscapeSearch'),
      relationship: document.querySelector('#landscapeRelationship'),
      company_category: document.querySelector('#landscapeCategory'),
      company_confidence: document.querySelector('#landscapeConfidence'),
    };
    const params = new URLSearchParams(window.location.search);
    Object.entries(fields).forEach(([key, field]) => {
      if (field && params.has(key)) field.value = params.get(key);
    });
    const apply = () => {
      const values = Object.fromEntries(
        Object.entries(fields).map(([key, field]) => [key, field ? field.value : ''])
      );
      let visible = 0;
      items.forEach(item => {
        const searchable = `${item.dataset.name} ${item.dataset.category} ${item.dataset.job}`;
        const show =
          (!values.lq || normalize(searchable).includes(normalize(values.lq))) &&
          (!values.relationship || item.dataset.relationship === values.relationship) &&
          (!values.company_category || item.dataset.category === values.company_category) &&
          (!values.company_confidence || item.dataset.confidence === values.company_confidence);
        item.hidden = !show;
        if (show) visible += 1;
      });
      document.querySelector('#landscapeCount').textContent = visible;
      document.querySelector('#landscapeEmpty').hidden = visible !== 0;
      setQuery(values);
    };
    Object.values(fields).forEach(field => {
      if (!field) return;
      field.addEventListener('input', apply);
      field.addEventListener('change', apply);
    });
    document.querySelector('#resetLandscapeFilters')?.addEventListener('click', () => {
      Object.values(fields).forEach(field => { if (field) field.value = ''; });
      apply();
    });
    apply();
  }

  function setupPresentation() {
    const shell = document.querySelector('[data-presentation]');
    if (!shell) return;
    const slides = Array.from(shell.querySelectorAll('[data-slide]'));
    const links = Array.from(shell.querySelectorAll('.presentation-index a'));
    let current = Math.max(0, slides.findIndex(slide => `#${slide.id}` === window.location.hash));
    const update = index => {
      current = Math.max(0, Math.min(index, slides.length - 1));
      slides[current].scrollIntoView({ block: 'start', behavior: 'smooth' });
      links.forEach((link, linkIndex) => {
        link.toggleAttribute('aria-current', linkIndex === current);
      });
      document.querySelector('#presentationProgress').textContent = `${current + 1} / ${slides.length}`;
      document.querySelector('#presentationStatus').textContent = `Section ${current + 1} of ${slides.length}`;
      history.replaceState({}, '', `#${slides[current].id}`);
    };
    document.querySelector('[data-presentation-prev]')?.addEventListener('click', () => update(current - 1));
    document.querySelector('[data-presentation-next]')?.addEventListener('click', () => update(current + 1));
    links.forEach((link, index) => link.addEventListener('click', event => {
      event.preventDefault();
      update(index);
    }));
    document.addEventListener('keydown', event => {
      if (event.target.matches('input, select, textarea, button')) return;
      if (event.key === 'ArrowRight' || event.key === 'PageDown') update(current + 1);
      if (event.key === 'ArrowLeft' || event.key === 'PageUp') update(current - 1);
    });
    update(current);
  }

  setupSubstituteExplorer();
  setupLandscapeExplorer();
  setupPresentation();
})();
