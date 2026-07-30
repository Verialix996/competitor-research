#!/usr/bin/env node
/**
 * Dependency-free Chrome DevTools audit.
 *
 * Start Chrome with --remote-debugging-port=9223, serve the repository, then run:
 *   node tools/browser_audit.mjs http://127.0.0.1:8765
 */

import { mkdir, writeFile } from 'node:fs/promises';

const base = process.argv[2] || 'http://127.0.0.1:8765';
const devtools = process.env.BIZMATCH_CDP || 'http://127.0.0.1:9223';
const output = '/tmp/bizmatch-ux-audit';

async function createTarget() {
  const response = await fetch(`${devtools}/json/new?${encodeURIComponent('about:blank')}`, {
    method: 'PUT',
  });
  if (!response.ok) throw new Error(`Could not create Chrome target: ${response.status}`);
  return response.json();
}

class CDP {
  constructor(url) {
    this.id = 0;
    this.pending = new Map();
    this.socket = new WebSocket(url);
  }

  async ready() {
    await new Promise((resolve, reject) => {
      this.socket.addEventListener('open', resolve, { once: true });
      this.socket.addEventListener('error', reject, { once: true });
    });
    this.socket.addEventListener('message', event => {
      const message = JSON.parse(event.data);
      if (!message.id || !this.pending.has(message.id)) return;
      const { resolve, reject } = this.pending.get(message.id);
      this.pending.delete(message.id);
      if (message.error) reject(new Error(message.error.message));
      else resolve(message.result);
    });
  }

  send(method, params = {}) {
    const id = ++this.id;
    this.socket.send(JSON.stringify({ id, method, params }));
    return new Promise((resolve, reject) => this.pending.set(id, { resolve, reject }));
  }

  async evaluate(expression) {
    const result = await this.send('Runtime.evaluate', {
      expression,
      awaitPromise: true,
      returnByValue: true,
    });
    if (result.exceptionDetails) throw new Error(result.exceptionDetails.text);
    return result.result.value;
  }
}

const target = await createTarget();
const cdp = new CDP(target.webSocketDebuggerUrl);
await cdp.ready();
await cdp.send('Page.enable');
await cdp.send('Runtime.enable');
await cdp.send('Network.enable');
await cdp.send('Network.setCacheDisabled', { cacheDisabled: true });
await mkdir(output, { recursive: true });

const failures = [];
const passes = [];
const check = (condition, message) => {
  (condition ? passes : failures).push(message);
};

async function navigate(path, width, height, screenshot) {
  await cdp.send('Emulation.setDeviceMetricsOverride', {
    width,
    height,
    deviceScaleFactor: 1,
    mobile: width < 600,
  });
  await cdp.send('Page.navigate', { url: `${base}${path}` });
  await new Promise(resolve => setTimeout(resolve, 450));
  const state = await cdp.evaluate(`(() => ({
    title: document.title,
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    main: Boolean(document.querySelector('#main-content')),
    skip: Boolean(document.querySelector('.skip-link')),
    activeNav: document.querySelectorAll('nav [aria-current="page"]').length,
    h1: document.querySelector('h1')?.textContent.trim()
  }))()`);
  check(state.overflow <= 1, `${path} has no page-level horizontal overflow at ${width}px`);
  check(state.main && state.skip && state.activeNav === 1, `${path} has landmarks, skip link, and one active nav item`);
  check(state.h1 && !state.h1.includes('copetitor'), `${path} uses clean visible BizMatch branding`);
  if (screenshot) {
    const image = await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
    await writeFile(`${output}/${screenshot}`, Buffer.from(image.data, 'base64'));
  }
}

for (const [path, name] of [
  ['/', 'overview'],
  ['/findings-conclusions/', 'findings'],
  ['/market-research/', 'market-research'],
  ['/sites/full-report-site/category-analysis.html', 'landscape'],
  ['/sites/full-report-site/alternative-workflows.html', 'workflows'],
  ['/presentation/', 'presentation'],
]) {
  await navigate(path, 1440, 1000, `${name}-desktop.png`);
  await navigate(path, 375, 812, `${name}-mobile.png`);
}

await navigate('/market-research/', 1024, 800);
const marketResult = await cdp.evaluate(`(() => {
  const sectionLinks = [...document.querySelectorAll('.market-section-nav a')];
  const targetsResolve = sectionLinks.every(link => {
    const id = link.getAttribute('href')?.slice(1);
    return id && document.getElementById(id);
  });
  const footer = document.querySelector('.market-footer')?.textContent || '';
  const evidenceRows = document.querySelectorAll('.evidence-register-table tbody tr').length;
  const phases = document.querySelectorAll('.research-phase').length;
  return {
    sectionLinks: sectionLinks.length,
    targetsResolve,
    evidenceRows,
    phases,
    footerScoped: !/Competitor tracker|Substitute entities|numeric threat ranking/i.test(footer)
  };
})()`);
check(marketResult.sectionLinks === 11 && marketResult.targetsResolve, 'Market Research on-page navigation resolves all major sections');
check(marketResult.evidenceRows === 7, 'Market Research renders seven anonymized claim-level evidence records');
check(marketResult.phases === 5, 'Market Research renders the five-phase next-research plan');
check(marketResult.footerScoped, 'Market Research footer excludes competitor-specific datasets and ranking language');

await navigate('/market-research/', 768, 1024, 'market-research-tablet.png');
await navigate('/market-research/?audit=anchor#evidence-register', 375, 812);
await new Promise(resolve => setTimeout(resolve, 1800));
const marketEvidenceImage = await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
await writeFile(`${output}/market-evidence-mobile.png`, Buffer.from(marketEvidenceImage.data, 'base64'));
const marketMobileResult = await cdp.evaluate(`(() => {
  const table = document.querySelector('.evidence-register-table');
  const firstCell = table?.querySelector('tbody td');
  const evidenceTop = document.getElementById('evidence-register')?.getBoundingClientRect().top;
  const currentSection = document.querySelector('.market-section-nav [aria-current="location"]')?.hash || '';
  return {
    hash: location.hash,
    tableDisplay: table ? getComputedStyle(table).display : '',
    tableWidth: table?.getBoundingClientRect().width || 0,
    wrapperWidth: table?.closest('.responsive-table')?.getBoundingClientRect().width || 0,
    tableComputedWidth: table ? getComputedStyle(table).width : '',
    tableMinWidth: table ? getComputedStyle(table).minWidth : '',
    rowWidth: table?.querySelector('tbody tr')?.getBoundingClientRect().width || 0,
    firstCellWidth: firstCell?.getBoundingClientRect().width || 0,
    firstCellScrollWidth: firstCell?.scrollWidth || 0,
    firstCellLabel: firstCell ? getComputedStyle(firstCell, '::before').content : '',
    evidenceTop,
    currentSection,
    scrollY: window.scrollY,
    maxScroll: document.documentElement.scrollHeight - document.documentElement.clientHeight,
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
  };
})()`);
check(
  marketMobileResult.hash === '#evidence-register'
    && marketMobileResult.evidenceTop >= 0
    && marketMobileResult.evidenceTop < 100,
  `Market Research supports direct section-anchor navigation (top ${marketMobileResult.evidenceTop}, current ${marketMobileResult.currentSection}, scroll ${marketMobileResult.scrollY}/${marketMobileResult.maxScroll})`
);
check(marketMobileResult.tableDisplay === 'block' && marketMobileResult.firstCellLabel !== 'none', 'Market Research evidence table becomes labelled cards on mobile');
check(
  marketMobileResult.tableWidth <= marketMobileResult.wrapperWidth + 1
    && marketMobileResult.firstCellWidth <= marketMobileResult.tableWidth + 1
    && marketMobileResult.firstCellScrollWidth <= marketMobileResult.firstCellWidth + 1,
  `Market Research mobile evidence cells wrap without clipping (wrapper ${marketMobileResult.wrapperWidth}, table ${marketMobileResult.tableWidth}/${marketMobileResult.tableComputedWidth}/${marketMobileResult.tableMinWidth}, row/cell/scroll ${marketMobileResult.rowWidth}/${marketMobileResult.firstCellWidth}/${marketMobileResult.firstCellScrollWidth})`
);
check(marketMobileResult.overflow <= 1, 'Market Research evidence register has no page-level mobile overflow');

await navigate('/sites/full-report-site/alternative-workflows.html', 1024, 800);
const filterResult = await cdp.evaluate(`(() => {
  const input = document.querySelector('#substituteSearch');
  input.value = 'warm introductions';
  input.dispatchEvent(new Event('input', { bubbles: true }));
  const visible = [...document.querySelectorAll('#substituteGrid > article')].filter(item => !item.hidden);
  return { count: visible.length, total: document.querySelectorAll('#substituteGrid > article').length, query: location.search };
})()`);
check(filterResult.count > 0 && filterResult.count < filterResult.total, 'workflow search filters canonical cards');
check(filterResult.query.includes('q=warm'), 'workflow filter state is preserved in the URL');

await navigate('/presentation/', 1024, 800);
const presentationResult = await cdp.evaluate(`(() => {
  document.querySelector('[data-presentation-next]').click();
  return new Promise(resolve => setTimeout(() => resolve({
    hash: location.hash,
    status: document.querySelector('#presentationStatus').textContent
  }), 500));
})()`);
check(presentationResult.hash === '#slide-2', 'presentation next control advances to section 2');
check(presentationResult.status.includes('2 of 12'), 'presentation progress announces the current section');

const keyboardResult = await cdp.evaluate(`(() => {
  const skip = document.querySelector('.skip-link');
  skip.focus();
  return { focused: document.activeElement === skip, href: skip.getAttribute('href') };
})()`);
check(keyboardResult.focused && keyboardResult.href === '#main-content', 'skip link is keyboard focusable and targets main content');

await cdp.send('Emulation.setEmulatedMedia', { media: 'print' });
const printResult = await cdp.evaluate(`(() => ({
  slides: document.querySelectorAll('.presentation-slide').length,
  controls: getComputedStyle(document.querySelector('.presentation-controls')).display
}))()`);
check(printResult.slides === 12 && printResult.controls === 'none', 'presentation print mode includes all sections and hides controls');

if (failures.length) {
  failures.forEach(message => console.error(`FAIL: ${message}`));
  process.exitCode = 1;
} else {
  console.log(`PASS: ${passes.length} browser checks`);
  passes.forEach(message => console.log(`  - ${message}`));
  console.log(`Screenshots: ${output}`);
}

cdp.socket.close();
