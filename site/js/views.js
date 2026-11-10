import {html} from './html.js';
import {BACK, FKS, LINK_RELATIONS, UNDER} from './relations.js';
import {anyActive, applyFilters, counts, defaultGroups, facetsFor, readFilters, writeFilters} from './facets.js';
import {defaultSort, parseSort, sameKeys, sortRefs, sortableFields} from './sort.js';
import {TYPE, TYPES, fieldLabel, inNav, kindLabel, title} from './types.js';

// Stand-ins for a missing image (`icon` in types.js): a PDF page, and simple emblems for each affiliation (a cog for
// the Empire, a bird for the Rebellion, a crosshair for mercenaries).
const SPOKE = 'M-3.5 -11 L3.5 -11 L6 -25 L-6 -25 Z';
const ICONS = {
  pdf: html`<svg viewBox="0 0 48 60" aria-hidden="true">
    <path d="M4 2h28l12 12v42a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z" fill="var(--surface)"
      stroke="currentColor" stroke-width="2"/>
    <path d="M32 2v12h12" fill="none" stroke="currentColor" stroke-width="2"/>
    <rect x="0" y="30" width="40" height="16" rx="2" fill="#c62828"/>
    <text x="20" y="42.5" text-anchor="middle" font-size="12" font-weight="700" fill="#fff"
      font-family="system-ui, sans-serif">PDF</text>
  </svg>`,
  Imperial: html`<svg viewBox="-32 -32 64 64" aria-hidden="true" class="emblem imperial">
    <circle r="28" fill="none" stroke="currentColor" stroke-width="4"/>
    <circle r="8" fill="none" stroke="currentColor" stroke-width="4"/>
    ${[0, 60, 120, 180, 240, 300].map(a => html`<path d="${SPOKE}" transform="rotate(${a})" fill="currentColor"/>`)}
  </svg>`,
  Rebel: html`<svg viewBox="-32 -32 64 64" aria-hidden="true" class="emblem rebel">
    <path d="M0 -30 L4 -8 L4 22 L0 30 L-4 22 L-4 -8 Z" fill="currentColor"/>
    <path d="M7 -22 C27 -12 29 14 11 27 L9 19 C20 9 20 -5 7 -13 Z" fill="currentColor"/>
    <path d="M-7 -22 C-27 -12 -29 14 -11 27 L-9 19 C-20 9 -20 -5 -7 -13 Z" fill="currentColor"/>
  </svg>`,
  Mercenary: html`<svg viewBox="-32 -32 64 64" aria-hidden="true" class="emblem mercenary">
    <circle r="20" fill="none" stroke="currentColor" stroke-width="4"/>
    <path d="M0 -30 V-12 M0 12 V30 M-30 0 H-12 M12 0 H30" stroke="currentColor" stroke-width="4"/>
    <circle r="4" fill="currentColor"/>
  </svg>`,
  Neutral: html`<svg viewBox="-32 -32 64 64" aria-hidden="true" class="emblem">
    <circle r="24" fill="none" stroke="currentColor" stroke-width="4"/>
  </svg>`,
};

function iconOf(ref) {
  const icon = TYPE[ref.type].icon;
  return icon === 'affiliation' ? ICONS[ref.record.affiliation] ?? ICONS.Neutral : ICONS[icon];
}

const MERMAID_URL = 'https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.esm.min.mjs';
const DATA_MODEL_URL = 'https://github.com/lvisintini/imperial-assault-data/blob/master/docs/data-model.md';
// Documents' PDFs stay off GitHub Pages: link to the repository's copy, which GitHub shows in its PDF viewer.
const DOCUMENTS_URL = 'https://github.com/lvisintini/imperial-assault-data/blob/master/documents';
const VISIBLE = TYPES.filter(t => !t.hidden);

// A mission's page is its missions row's, whichever card it has (a missions row looks like its card). An agenda card
// links to its own page, which shows the same when it's a mission (app.js).
// A form card's page is under a deployment card's (relations.js UNDER).
export const href = ref => ref.type === 'missions' || TYPE[ref.type]?.page === 'missions' && ref.row
  ? `#/missions/${(ref.row ?? ref).key}`
  : ref.under ? childHref(ref.under, ref) : `#/${ref.type}/${ref.key}`;

// A child's address under its parent's page: #/agenda-decks/<id>/agenda-cards/<id>.
export const childHref = (parent, child) => `${href(parent)}/${child.type}/${child.key}`;

// In the given order, or the type's default one (lists of a single type).
const sorted = (refs, keys) => refs.length ? sortRefs(refs, keys ?? defaultSort(refs[0].type)) : refs;

const ownImage = ref => ref.record[TYPE[ref.type].images.find(f => ref.record[f])];
const backImage = (ref, db) => db.back.get(ref)?.ref.record.image;

// Tiles show a record's own image, or its card back when it has none (agenda decks, imperial classes) or its type
// asks for it (`thumb: 'back'`: heroes), or, for a mission with neither (raids), its map. The peek prefers the
// record's own image.
function thumbPath(ref, db) {
  ref = ref.card ?? ref;
  return (TYPE[ref.type].thumb === 'back'
    ? backImage(ref, db) ?? ownImage(ref) : ownImage(ref) ?? backImage(ref, db)) ?? mapImage(ref, db);
}

const peekPath = (ref, db) => {
  ref = ref.card ?? ref;
  return ownImage(ref) ?? backImage(ref, db) ?? mapImage(ref, db);
};

// A map's or a tile's small image is its large one halved (64 px per square, against 128), and the site only publishes
// images/small/maps and images/small/map-tiles (pages.yml: the large ones would take it over Pages' 1 GB).
const SMALL_ONLY = ['maps/', 'map-tiles/'];
const imageUrl = (size, path) =>
  `images/${SMALL_ONLY.some(folder => path.startsWith(folder)) ? 'small' : size}/${encodeURI(path)}`;

// A mission card's map, through its missions row.
const mapOf = (ref, db) => db.parent.get(db.mission.get(ref))?.ref;
const mapImage = (ref, db) => mapOf(ref, db)?.record.image;

function subtitle(ref, db) {
  if (ref.card) return kindLabel(ref.card.type, true);
  const {record} = ref;
  const parent = db.parent.get(ref);
  if (parent) return title(parent.ref);
  switch (ref.type) {
    case 'sources': return record.wave != null ? `${record.type} · Wave ${record.wave}` : record.type;
    // Enough to tell apart same-named cards: elite/regular pairs and campaign/skirmish versions.
    case 'deployment-cards': return [
      record.description,
      record.affiliation,
      record.elite ? 'Elite' : 'Regular',
      record.modes.length === 1 && `${record.modes[0]} only`,
    ].filter(Boolean).join(' · ');
    case 'upgrade-cards': return `Tier ${record.tier}`;
    case 'skirmish-missions': return [mapOf(ref, db) && title(mapOf(ref, db)), record.scenario,
      record.format !== 'Standard' && record.format].filter(Boolean).join(' · ');
    case 'miniatures': return record.description;
    case 'documents': return [record.category, record.version && `Version ${record.version}`].filter(Boolean).join(' · ');
    case 'card-backs': return [...new Set((db.backOf.get(ref) ?? []).map(card => TYPE[card.type].label))].join(', ');
  }
}

// A tile's thumbnail: its image, its type's icon, or nothing.
function thumb(ref, db, none = html`<span class="no-image">No image</span>`) {
  const path = thumbPath(ref, db);
  if (path) return html`<img loading="lazy" src="${imageUrl('small', path)}" alt="">`;
  const icon = iconOf(ref.card ?? ref);
  return icon ? html`<span class="icon">${icon}</span>` : none;
}

// copies: how many of it the product shown has (product contents, "Found in"), when more than one.
// link: the tile's address, when not the record's own (a deck's cards, under the deck).
function tile(ref, db, copies, link = href(ref)) {
  const peek = peekPath(ref, db);
  const name = title(ref);
  return html`<a class="tile" href="${link}"${peek ? html` data-peek="${imageUrl('large', peek)}"` : ''}>
    <span class="thumb">${thumb(ref, db)}</span>
    <span class="tile-title">${name}${copies > 1 ? html` <span class="copies">×${copies}</span>` : ''}</span>
    <span class="tile-sub">${subtitle(ref, db)}</span>
  </a>`;
}

// copiesOf: ref → how many copies to show on its tile (see tile).
// linkOf: ref → the tile's address, when not the record's own.
const grid = (refs, db, keys, copiesOf = () => null, linkOf = href) =>
  html`<div class="grid">${sorted(refs, keys).map(ref => tile(ref, db, copiesOf(ref), linkOf(ref)))}</div>`;

// Nested sections by facet (facets.js): <h2> for the first level, <h3> below it. Records with several values (traits,
// products) appear under each of them; records with none come last.
function sections(refs, levels, db, keys, depth = 0) {
  if (!levels.length) return grid(refs, db, keys);
  const [facet, ...rest] = levels;
  const groups = facet.choices.map(c => [c.heading, refs.filter(ref => facet.of(ref).includes(c.key))]);
  groups.push([`No ${facet.label.toLowerCase()}`, refs.filter(ref => !facet.of(ref).length)]);
  return groups.filter(([, members]) => members.length).map(([heading, members]) => {
    const count = html` <span class="count">${members.length}</span>`;
    return html`<section class="group">
      ${depth ? html`<h3>${heading}${count}</h3>` : html`<h2>${heading}${count}</h2>`}
      ${sections(members, rest, db, keys, depth + 1)}
    </section>`;
  });
}

const SORT_LEVELS = 3;

// "Sort by [field] [direction] then by …": a level per key, plus an empty one to add a key, up to SORT_LEVELS.
function sortControls(type, fields, keys) {
  const levels = keys.slice(0, SORT_LEVELS);
  if (levels.length < Math.min(SORT_LEVELS, fields.length)) levels.push('');
  return html`<span class="sort-label">Sort by</span>${levels.map((key, i) => {
    const field = key.replace(/^-/, '');
    const desc = key.startsWith('-');
    return html`<span class="sort-level">${i ? html`<span class="sort-label">then</span>` : ''}
      <select data-level="${i}" aria-label="${i ? `Then sort by` : 'Sort by'}">
        <option value="">—</option>
        ${fields.map(f => html`<option value="${f}"${f === field ? html` selected` : ''}>${fieldLabel(f)}</option>`)}
      </select>
      ${field ? html`<button type="button" data-direction="${i}" aria-pressed="${desc ? 'true' : 'false'}"
        aria-label="${fieldLabel(field)}: ${desc ? 'descending' : 'ascending'}">${desc ? '↓ Desc' : '↑ Asc'}</button>` : ''}
    </span>`;
  })}${sameKeys(keys, defaultSort(type)) ? '' : html`<button type="button" data-reset>Reset</button>`}`;
}

const GROUP_LEVELS = 2;

// "Group by [facet] then [facet]", from the facets with fixed values.
function groupControls(groupable, groups, defaults) {
  const levels = groups.slice(0, GROUP_LEVELS);
  if (levels.length < Math.min(GROUP_LEVELS, groupable.length)) levels.push('');
  return html`<span class="sort-label">Group by</span>${levels.map((id, i) => html`<span class="sort-level">
      ${i ? html`<span class="sort-label">then</span>` : ''}
      <select data-group-level="${i}" aria-label="${i ? 'Then group by' : 'Group by'}">
        <option value="">—</option>
        ${groupable.map(f => html`<option value="${f.id}"${f.id === id ? html` selected` : ''}>${f.label}</option>`)}
      </select>
    </span>`)}${sameKeys(groups, defaults) ? '' : html`<button type="button" data-group-reset>Reset</button>`}`;
}

// A range's slider, its knobs at the filter's bounds (the facet's ends when unset), the span between them filled in
// (--lo and --hi, as percentages of the track).
function rangeSlider(facet, filter) {
  const lo = filter?.min ?? facet.min, hi = filter?.max ?? facet.max;
  const percent = value => ((value - facet.min) / (facet.max - facet.min)) * 100;
  return html`<span class="range-value" data-range-value="${facet.id}">${lo} – ${hi}</span>
    <span class="dual-range" data-range="${facet.id}" style="--lo: ${percent(lo)}%; --hi: ${percent(hi)}%">
      ${[['min', lo, 'at least'], ['max', hi, 'at most']].map(([bound, value, words]) => html`
        <input type="range" data-facet="${facet.id}" data-bound="${bound}" min="${facet.min}" max="${facet.max}"
          step="${facet.step}" value="${value}" aria-label="${facet.label}: ${words}">`)}
    </span>`;
}

// A fieldset per facet: checkboxes (their counts are filled in by the page) or a two-knob slider.
function filterPanel(facets, filters) {
  return facets.map(facet => facet.kind === 'range' ? html`
    <fieldset class="facet">
      <legend>${facet.label}</legend>
      ${rangeSlider(facet, filters[facet.id])}
    </fieldset>` : html`
    <fieldset class="facet${facet.choices.length > 8 ? ' long' : ''}">
      <legend>${facet.label}</legend>
      ${facet.choices.map(c => html`<label class="choice">
        <input type="checkbox" data-facet="${facet.id}" data-key="${c.key}"
          ${filters[facet.id]?.has(c.key) ? html`checked` : ''}>
        <span class="choice-label">${c.label}</span> <span class="count" data-count="${facet.id}:${c.key}"></span>
      </label>`)}
    </fieldset>`);
}

// Groups from ?group=: facet ids; "none" for no grouping; the type's default when missing.
function readGroups(param, groupable, defaults) {
  if (param == null) return defaults;
  const ids = param.split(',').filter(id => groupable.some(f => f.id === id));
  return [...new Set(ids)].slice(0, GROUP_LEVELS);
}

// Re-render a control group, keeping focus on the same control (matched by its data attributes) or its first select.
function rerender(container, markup) {
  const active = container.contains(document.activeElement) ? document.activeElement : null;
  const selector = active && Object.entries(active.dataset)
    .map(([k, v]) => `[data-${k.replace(/[A-Z]/g, c => `-${c.toLowerCase()}`)}="${v}"]`).join('');
  container.innerHTML = String(markup);
  if (active) (selector && container.querySelector(selector) || container.querySelector('select'))?.focus();
}

// Refs of mixed types, one sub-heading per type, in navigation order.
// linkOf: ref → its tile's address, when not the record's own (see grid).
function grouped(refs, db, copiesOf, linkOf = href) {
  const byType = Map.groupBy(refs, ref => ref.type);
  return TYPES.filter(t => byType.has(t.file)).map(t => html`
    <h3>${t.list === false ? t.label : html`<a href="#/${t.file}">${t.label}</a>`} <span class="count">${byType.get(t.file).length}</span></h3>
    ${grid(byType.get(t.file), db, undefined, copiesOf, linkOf)}`);
}

const heading2 = (heading, count) => html`<h2>${heading}${count == null ? '' : html` <span class="count">${count}</span>`}</h2>`;
// A related section closed until the viewer opens it by its heading.
const closed = (heading, count, body) => html`
  <details class="related closed">
    <summary>${heading2(heading, count)}</summary>
    ${body}
  </details>`;
const section = (heading, count, body) => html`
  <section class="related">
    ${heading2(heading, count)}
    ${body}
  </section>`;

export function landing(db) {
  const tiles = TYPES.filter(inNav).map(t => {
    const first = sorted(db.refs[t.file])[0];
    return html`<a class="tile" href="#/${t.file}">
      <span class="thumb">${first ? thumb(first, db, '') : ''}</span>
      <span class="tile-title">${t.label}</span>
      <span class="tile-sub">${db.refs[t.file].length} records</span>
    </a>`;
  });
  return {
    body: html`
      <p class="lede">Every card, map and product in the
        <a href="https://github.com/lvisintini/imperial-assault-data">imperial-assault-data</a> dataset, with its images,
        metadata and links to every related record.</p>
      <div class="grid">${tiles}</div>
      <section class="related">
        <h2>Data model</h2>
        <p>How the data files relate. The full write-up is in
          <a href="${DATA_MODEL_URL}">docs/data-model.md</a>.</p>
        <div id="diagrams"><p class="status">Loading diagrams…</p></div>
      </section>`,
    mount: el => renderDiagrams(el.querySelector('#diagrams')),
  };
}

async function renderDiagrams(el) {
  try {
    const res = await fetch('docs/data-model.md');
    if (!res.ok) throw new Error(`docs/data-model.md: HTTP ${res.status}`);
    const blocks = [...(await res.text()).matchAll(/```mermaid\n([\s\S]*?)```/g)].map(m => m[1]);
    const {default: mermaid} = await import(MERMAID_URL);
    const dark = matchMedia('(prefers-color-scheme: dark)').matches;
    mermaid.initialize({startOnLoad: false, theme: dark ? 'dark' : 'default'});
    const svgs = [];
    for (const [i, block] of blocks.entries()) svgs.push((await mermaid.render(`diagram-${i}`, block)).svg);
    // The diagrams are scaled down to the page width; the link opens one at full size.
    el.innerHTML = svgs.map(svg => {
      const url = URL.createObjectURL(new Blob([svg], {type: 'image/svg+xml'}));
      return `<figure class="diagram">${svg}<figcaption><a href="${url}" target="_blank">Open full size</a></figcaption></figure>`;
    }).join('');
  } catch (error) {
    console.warn('Could not render the data model diagrams', error);
    el.innerHTML = String(html`<p class="status">Couldn't load the diagrams. See
      <a href="${DATA_MODEL_URL}">docs/data-model.md</a> instead.</p>`);
  }
}

export function index(db, type, params) {
  const t = TYPE[type];
  const refs = db.refs[type];
  const fields = sortableFields(type, refs);
  const facets = facetsFor(type, refs, db);
  const groupable = facets.filter(f => f.kind === 'choice');
  const defaults = defaultGroups(type, facets);
  const state = {
    q: params.get('q') ?? '',
    keys: parseSort(type, params.get('sort'), fields),
    groups: readGroups(params.get('group'), groupable, defaults),
    filters: readFilters(params, facets),
  };
  const matching = () => applyFilters(refs, facets, state.filters, state.q);
  const list = shown => {
    if (!shown.length) return html`<p class="status">No matches.</p>`;
    const levels = state.groups.map(id => groupable.find(f => f.id === id));
    return levels.length ? sections(shown, levels, db, state.keys) : grid(shown, db, state.keys);
  };
  return {
    title: t.label,
    body: html`
      <h1>${t.label} <span class="count">${refs.length}</span></h1>
      <div class="controls">
        <input type="search" id="filter" class="filter" placeholder="Filter by name" aria-label="Filter by name"
          value="${state.q}">
        <div class="sort" id="sort">${sortControls(type, fields, state.keys)}</div>
        ${groupable.length
          ? html`<div class="sort" id="group">${groupControls(groupable, state.groups, defaults)}</div>` : ''}
      </div>
      <div class="browse">
        ${facets.length ? html`<details class="filters" id="filters">
          <summary>Filters</summary>
          <div class="filters-body">${filterPanel(facets, state.filters)}</div>
        </details>` : ''}
        <div class="results">
          <p class="summary" id="summary"></p>
          <div id="list">${list(matching())}</div>
        </div>
      </div>`,
    mount: el => {
      const input = el.querySelector('#filter');
      const sortEl = el.querySelector('#sort');
      const groupEl = el.querySelector('#group');
      const panel = el.querySelector('#filters');
      const listEl = el.querySelector('#list');
      const summary = el.querySelector('#summary');

      const writeUrl = () => {
        const parts = [
          state.q.trim() && `q=${encodeURIComponent(state.q.trim())}`,
          !sameKeys(state.keys, defaultSort(type)) && `sort=${state.keys.join(',')}`,
          !sameKeys(state.groups, defaults) && `group=${state.groups.join(',') || 'none'}`,
          ...writeFilters(state.filters, facets),
        ].filter(Boolean);
        // replaceState doesn't fire hashchange, so changing the controls doesn't re-render the page (or steal focus).
        history.replaceState(null, '', `#/${type}${parts.length ? `?${parts.join('&')}` : ''}`);
      };
      const update = ({rerenderList = true} = {}) => {
        const shown = matching();
        if (rerenderList) listEl.innerHTML = String(list(shown));
        const filtered = anyActive(state.filters) || state.q.trim();
        summary.innerHTML = String(html`Showing ${shown.length} of ${refs.length}${filtered
          ? html` <button type="button" data-clear>Clear filters</button>` : ''}`);
        const tally = counts(refs, facets, state.filters, state.q);
        for (const count of panel?.querySelectorAll('[data-count]') ?? []) {
          const at = count.dataset.count.indexOf(':');
          const [id, key] = [count.dataset.count.slice(0, at), count.dataset.count.slice(at + 1)];
          const n = tally[id]?.[key] ?? 0;
          const box = count.parentElement.querySelector('input');
          count.textContent = n;
          box.disabled = !box.checked && n === 0;
          count.parentElement.classList.toggle('empty', box.disabled);
        }
        writeUrl();
      };

      input.addEventListener('input', () => {
        state.q = input.value;
        update();
      });
      summary.addEventListener('click', event => {
        if (!event.target.closest('[data-clear]')) return;
        state.filters = {};
        state.q = input.value = '';
        for (const box of panel?.querySelectorAll('input[type=checkbox]') ?? []) box.checked = false;
        for (const facet of facets.filter(f => f.kind === 'range')) showRange(facet, null);
        update();
        input.focus();
      });

      panel?.addEventListener('change', event => {
        const box = event.target.closest('input[type=checkbox]');
        if (!box) return;
        const chosen = state.filters[box.dataset.facet] ??= new Set();
        if (box.checked) chosen.add(box.dataset.key);
        else chosen.delete(box.dataset.key);
        update();
      });
      // Redraw a slider for a filter (null: unset), without re-rendering it (the knob being dragged keeps focus).
      const showRange = (facet, filter) => {
        const slider = panel.querySelector(`[data-range="${facet.id}"]`);
        const [low, high] = slider.querySelectorAll('input');
        low.value = filter?.min ?? facet.min;
        high.value = filter?.max ?? facet.max;
        const percent = value => ((Number(value) - facet.min) / (facet.max - facet.min)) * 100;
        slider.style.setProperty('--lo', `${percent(low.value)}%`);
        slider.style.setProperty('--hi', `${percent(high.value)}%`);
        panel.querySelector(`[data-range-value="${facet.id}"]`).textContent = `${low.value} – ${high.value}`;
      };
      let sliding = null;
      panel?.addEventListener('input', event => {
        const knob = event.target.closest('input[type=range]');
        if (!knob) return;
        const facet = facets.find(f => f.id === knob.dataset.facet);
        const [low, high] = panel.querySelector(`[data-range="${facet.id}"]`).querySelectorAll('input');
        // The knobs don't pass each other: the one moved stops at the other.
        if (Number(low.value) > Number(high.value)) knob.value = knob === low ? high.value : low.value;
        const min = Number(low.value), max = Number(high.value);
        // A knob at its end of the track sets no bound, so records without a value aren't left out by default.
        const filter = {min: min > facet.min ? min : null, max: max < facet.max ? max : null};
        showRange(facet, filter);
        clearTimeout(sliding);
        sliding = setTimeout(() => {
          state.filters[facet.id] = filter;
          update();
        }, 150);
      });
      // Open beside the list on wide screens; on narrow ones only when filters are already set.
      const wide = globalThis.matchMedia?.('(min-width: 900px)').matches;
      if (panel && (wide || anyActive(state.filters))) panel.open = true;

      const setKeys = next => {
        state.keys = next.length ? next : defaultSort(type);
        rerender(sortEl, sortControls(type, fields, state.keys));
        update();
      };
      sortEl.addEventListener('change', event => {
        const i = Number(event.target.dataset.level);
        const field = event.target.value;
        const next = [...state.keys];
        if (!field) next.splice(i, 1);
        else next[i] = (next[i]?.startsWith('-') ? '-' : '') + field;
        setKeys(next.filter((key, j) => !field || j === i || key.replace(/^-/, '') !== field));
      });
      sortEl.addEventListener('click', event => {
        const button = event.target.closest('button');
        if (!button) return;
        if (button.dataset.reset !== undefined) return setKeys(defaultSort(type));
        const i = Number(button.dataset.direction);
        setKeys(state.keys.map((key, j) => j !== i ? key : key.startsWith('-') ? key.slice(1) : `-${key}`));
      });

      const setGroups = next => {
        state.groups = next;
        rerender(groupEl, groupControls(groupable, state.groups, defaults));
        update();
      };
      groupEl?.addEventListener('change', event => {
        const i = Number(event.target.dataset.groupLevel);
        const id = event.target.value;
        const next = [...state.groups];
        if (!id) next.splice(i, 1);
        else next[i] = id;
        setGroups(next.filter((g, j) => !id || j === i || g !== id));
      });
      groupEl?.addEventListener('click', event => {
        if (event.target.closest('[data-group-reset]')) setGroups(defaults);
      });

      update({rerenderList: false});
    },
  };
}

function fieldValue(ref, field, value, db) {
  const fk = field === BACK.field ? BACK : FKS.find(rel => rel.child === ref.type && rel.field === field);
  if (fk) {
    const parent = db.get(fk.parent, value);
    if (parent) return html`<a href="${href(parent)}">${title(parent)}</a>`;
  }
  if (ref.type === 'documents' && field === 'file') {
    return html`<a href="${DOCUMENTS_URL}/${value}"><code>${value}</code></a>`;
  }
  if (TYPE[ref.type].images.includes(field) && value) {
    return html`<a href="${imageUrl('large', value)}"><code>${value}</code></a>`;
  }
  if (TYPE[ref.type].pageImages?.[field] && value) {
    return html`<a href="${imageUrl('large', value)}"><code>${value}</code></a>`;
  }
  if (TYPE[ref.type].imageSections?.includes(field) && value?.length) {
    return html`${value.map(({name, image}, i) => html`${i ? ', ' : ''}${name}: <a href="${imageUrl('large', image)}"><code>${image}</code></a>`)}`;
  }
  if (value == null || (Array.isArray(value) && !value.length)) return html`<span class="none">—</span>`;
  if (Array.isArray(value)) return value.join(', ');
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  return String(value);
}

// A map's tile sides grouped by the product the tiles come in, newest product first (the map tiles' default order),
// then by number and side; each with how many copies the mission takes.
function layoutGroups(rows, db) {
  const tiles = sorted([...new Set(rows.map(row => row.ref))]);
  const ordered = [...rows].sort((a, b) => tiles.indexOf(a.ref) - tiles.indexOf(b.ref) || a.side.localeCompare(b.side));
  const groups = new Map();
  for (const row of ordered) {
    const product = db.sources(row.ref)[0];
    const key = product ? title(product) : '';
    if (!groups.has(key)) groups.set(key, {product, rows: []});
    groups.get(key).rows.push(row);
  }
  return [...groups.values()];
}

// The thumbnails of a map's tile sides, a group per product.
function layoutList(rows, db) {
  return layoutGroups(rows, db).map(({product, rows}) => html`
    ${product ? html`<h3><a href="${href(product)}">${title(product)}</a> <span class="count">${rows.length}</span></h3>` : ''}
    <div class="grid">${rows.map(({ref, side, count}) => {
      const path = ref.record[side === 'A' ? 'side_a' : 'side_b'];
      return html`<a class="tile" href="${href(ref)}" data-peek="${imageUrl('large', path)}">
        <span class="thumb"><img loading="lazy" src="${imageUrl('small', path)}" alt=""></span>
        <span class="tile-title">${title(ref)}${side}${count > 1 ? html` <span class="copies">×${count}</span>` : ''}</span>
        <span class="tile-sub">Side ${side}</span>
      </a>`;
    })}</div>`);
}

// A tile's interchangeable sides (map-tile-matches): for each of its sides, the other tiles' sides with the same art.
function matchList(rows, db) {
  return ['A', 'B'].filter(side => rows.some(row => row.side === side)).map(side => {
    const others = rows.filter(row => row.side === side).map(row => ({ref: row.ref, side: row.otherSide}));
    return html`<h3>Side ${side} <span class="count">${others.length}</span></h3>
      ${layoutList(others, db)}`;
  });
}

// A product's short name in a map's tile list, as the Vassal Imperial Assault modules prefix its tiles (the Core Set's
// have none there).
const SHORT = {
  'Imperial Assault': 'Core', 'Twin Shadows': 'TS', 'Return to Hoth': 'H', 'The Bespin Gambit': 'BG',
  "Jabba's Realm": 'JR', 'Heart of the Empire': 'HotE', 'Tyrants of Lothal': 'ToL',
};

// A tile side's short name: "Core 32A", "ToL 01B".
const tileName = (tile, side, db) => {
  const product = db.sources(tile)[0];
  return `${product ? SHORT[product.record.name] ?? title(product) : ''} ${String(tile.record.number).padStart(2, '0')}${side}`.trim();
};

// A map's image (or a hidden section's, or the whole map's) with a box over each tile on it, which names the tile on
// hover, or always with the page's "Show tile names" (tiles.js sizes the boxes once the tiles' images load, from
// map-layouts placements). sections: the placements' sections the image shows (null: the map's own image), in the
// order they're drawn.
function mapFrame(ref, db, sections, image, alt) {
  const boxes = (db.layout.get(ref) ?? []).flatMap(({ref: tile, side, placements}) => placements
    .filter(p => sections.includes(p.section))
    .map(p => ({src: imageUrl('small', tile.record[side === 'A' ? 'side_a' : 'side_b']), x: p.x, y: p.y,
                rotation: p.rotation, layer: sections.indexOf(p.section), label: tileName(tile, side, db),
                title: `${title(tile)}, side ${side}${p.section ? ` (${p.section})` : ''}`})));
  return html`<a class="map-frame" href="${imageUrl('large', image)}"${boxes.length ? html` data-boxes="${JSON.stringify(boxes)}"` : ''}>
    <img loading="lazy" src="${imageUrl('large', image)}" alt="${alt}"><span class="tile-boxes"></span>
  </a>`;
}

// A map's tile sides as plain text, a line per product (newest first): "ToL  01A, 03A" … "Core  32A(2), 36A(4)", the
// copies in brackets when the mission takes more than one.
function layoutText(rows, db) {
  return html`<dl class="tile-list">${layoutGroups(rows, db).map(({product, rows}) => html`
    <dt title="${product ? title(product) : ''}">${product ? SHORT[product.record.name] ?? title(product) : 'No product'}</dt>
    <dd>${rows.map(({ref, side, count}) =>
      `${String(ref.record.number).padStart(2, '0')}${side}${count > 1 ? `(${count})` : ''}`).join(', ')}</dd>`)}</dl>`;
}

// The sections of a map revealed during its mission, in order, each under its name.
function hiddenList(ref, db, sections) {
  return html`<div class="hidden-sections">${sections.map(({name, image}) => html`
    <figure>
      <figcaption>${name}</figcaption>
      ${mapFrame(ref, db, [name], image, name)}
    </figure>`)}</div>`;
}

// A mission's rewards: those it always gives, then its alternatives ("Choose 1"). Credits have no record to show.
function rewardList(rewards, db) {
  const block = rows => html`${rows.some(r => r.credits) ? html`<p>Credits</p>` : ''}${
    rows.some(r => r.ref) ? html`<div class="grid">${rows.filter(r => r.ref).map(r => tile(r.ref, db))}</div>` : ''}`;
  const always = rewards.filter(r => !r.choice);
  const choice = rewards.filter(r => r.choice);
  return html`${always.length ? block(always) : ''}${choice.length
    ? html`<h3>Choose 1 <span class="count">${choice.length}</span></h3>${block(choice)}` : ''}`;
}

// A fields table: [label, value] rows.
const fieldsTable = rows => html`<dl class="fields">${rows.map(([label, value]) => html`<dt>${label}</dt><dd>${value}</dd>`)}
  </dl>`;

// The products a record comes in, each with how many copies it has of it, when more than one.
const foundIn = (ref, sources, db) =>
  section('Found in', sources.length, grid(sources, db, undefined, source => db.copies.get(source)?.get(ref)));

// A child's parent: a hero class card's hero, a hero side mission's ("For hero"), an epilogue's mission.
const parentSection = ({rel, ref}, db) => section(rel.label ?? TYPE[rel.parent].singular, null, grid([ref], db));

// Record links, a section per relation as read from this end: "Figure of" on a miniature, "Miniatures" on what it
// stands for, "Required by" on a product.
// Records whose pages are under the linked ones (relations.js UNDER: a deployment card's forms) link under this one.
function linkSections(ref, db) {
  const linkOf = other => UNDER[other.type] && (db.links.get(other) ?? [])
    .some(link => link.relation === UNDER[other.type] && link.ref === ref) ? childHref(ref, other) : href(other);
  return Object.entries(LINK_RELATIONS).flatMap(([relation, heading]) => {
    const refs = (db.links.get(ref) ?? []).filter(link => link.relation === relation).map(link => link.ref);
    return refs.length ? [section(heading, refs.length, grouped(refs, db, undefined, linkOf))] : [];
  });
}

// A map's hidden sections and its whole map (its image and every hidden section in one frame, the later on top): each
// a section that stays closed until the viewer opens it. Nothing for other records.
function mapSections(ref, db) {
  const t = TYPE[ref.type];
  const hidden = (t.imageSections ?? []).flatMap(field => ref.record[field] ?? []);
  const out = hidden.length ? [closed('Hidden sections', hidden.length, hiddenList(ref, db, hidden))] : [];
  for (const [field, heading] of Object.entries(t.pageImages ?? {})) {
    const image = ref.record[field];
    const every = [null, ...hidden.map(h => h.name)];
    if (image) out.push(closed(heading, null, html`<div class="hidden-sections">
      ${mapFrame(ref, db, every, image, `${heading}: ${title(ref)}`)}
    </div>`));
  }
  return out;
}

function backSection(ref, db) {
  const back = db.back.get(ref);
  const via = back.via ? ` (on its ${TYPE[back.via.type].label.toLowerCase()})` : '';
  return section(`Card back${via}`, null, grid([back.ref], db));
}

const SHOW_TILES = html`<label class="tile-toggle"><input type="checkbox" data-show-tiles> Show tile names</label>`;

// The crumbs of a record's page, and the navigation link to mark:
// - a child under its parent's address (a deck's agenda card, a deployment card's form card): the parent's list and
//   page, "Agenda decks › Agents of the Empire";
// - elsewhere, a child of a `nested` relation (relations.js FKS): its parent's list and its own, "Agenda decks › Agenda
//   cards";
// - a type left out of the navigation (types.js `nav: false`, epilogue cards): its parent's list and page, then
//   `crumb`: its name, "Missions › Executive Overreach › Epilogue: Sparks";
// - else its type's list, or for a type without one (types.js `list: false`, form cards) its menu's.
function crumbs(ref, under, db) {
  const t = TYPE[ref.type];
  const list = type => html`<a href="#/${type}">${TYPE[type].label}</a>`;
  const page = parent => html`${list(parent.type)} › <a href="${href(parent)}">${title(parent)}</a>`;
  const parent = db.parent.get(ref);
  if (under) return {nav: under.type, html: page(under)};
  if (parent?.rel.nested) return {nav: ref.type, html: html`${list(parent.rel.parent)} › ${list(ref.type)}`};
  if (t.nav === false && parent) {
    return {nav: parent.ref.type, html: html`${page(parent.ref)} › ${t.crumb ?? t.singular}: ${title(ref)}`};
  }
  const home = t.list === false ? t.menu : ref.type;  // a type without a list page: its menu's (form cards)
  return {nav: home, html: list(home)};
}

// under: the parent whose address the page is under (app.js), or null.
export function detail(db, ref, under = null) {
  const t = TYPE[ref.type];
  const name = title(ref);
  const layout = db.layout.get(ref);
  const images = t.images.filter(f => ref.record[f]).map(f => html`
    <figure>
      ${layout ? mapFrame(ref, db, [null], ref.record[f], name) : html`<a href="${imageUrl('large', ref.record[f])}">
        <img src="${imageUrl('large', ref.record[f])}" alt="${name}${t.images.length > 1 ? ` (${f})` : ''}">
      </a>`}
      ${t.images.length > 1 ? html`<figcaption>${fieldLabel(f)}</figcaption>` : ''}
    </figure>`);
  if (layout?.some(row => row.placements.length)) images.push(SHOW_TILES);

  const related = [];
  // Next to the image instead of the fields table (types.js aside): the tile list, then the products and the children
  // side by side.
  const aside = t.aside ? [] : null;
  const columns = t.aside ? [] : null;
  if (aside && layout) aside.push(section('Tiles', layout.length, layoutText(layout, db)));
  const contents = db.contents.get(ref);
  if (contents) {
    const refs = [...contents.values()].flat();
    const copies = db.copies.get(ref);
    related.push(section('Contents', refs.length, grouped(refs, db, content => copies?.get(content))));
  }
  const sources = db.sources(ref);
  if (sources.length) (columns ?? related).push(foundIn(ref, sources, db));
  const parent = db.parent.get(ref);
  if (parent) related.push(parentSection(parent, db));
  for (const {rel, refs} of db.children.get(ref) ?? []) {
    const linkOf = rel.nested ? child => childHref(ref, child) : href;
    (columns ?? related).push(section(rel.childrenLabel ?? TYPE[rel.child].label, refs.length,
      grid(refs, db, undefined, undefined, linkOf)));
  }
  related.push(...linkSections(ref, db), ...mapSections(ref, db));
  // A tile's maps, under the side each uses (a map that uses both sides is under each).
  const usedIn = db.usedIn.get(ref);
  if (usedIn) {
    const sides = ['A', 'B'].filter(side => usedIn[side]);
    related.push(section('Used in', new Set(sides.flatMap(side => usedIn[side])).size, sides.map(side => html`
      <h3>Side ${side} <span class="count">${usedIn[side].length}</span></h3>
      ${grid(usedIn[side], db)}`)));
  }
  const matches = db.matches.get(ref);
  if (matches) related.push(section('Interchangeable with', matches.length, matchList(matches, db)));
  const rewardOf = db.rewardOf.get(ref);
  if (rewardOf) related.push(section('Reward from', rewardOf.length, grouped(rewardOf, db)));
  if (db.back.has(ref)) related.push(backSection(ref, db));
  const backOf = db.backOf.get(ref);
  if (backOf) related.push(section('Back of', backOf.length, grouped(backOf, db)));
  // Last: a map's tiles' images, by product (beside the image, a map's aside lists them by name).
  if (layout) related.push(section(aside ? 'Tile images' : 'Tiles', layout.length, layoutList(layout, db)));

  const trail = crumbs(ref, under, db);
  return {
    title: name,
    nav: trail.nav,
    body: html`
      <p class="crumbs">${trail.html}</p>
      <h1>${name}</h1>
      <div class="detail">
        ${images.length ? html`<div class="images">${images}</div>` : ''}
        ${aside ? html`<div class="aside">${aside}${columns.length ? html`<div class="aside-columns">${columns}</div>` : ''}</div>` : fieldsTable(Object.entries(ref.record).map(
          ([field, value]) => [fieldLabel(field), fieldValue(ref, field, value, db)]))}
      </div>
      ${related}`,
  };
}

// A mission's page, one for every kind: its card (none for a raid or a cardless story mission) and fields, its type
// (the collection) first and its location and map last; its products, the hero or agenda deck it's for, its rewards and
// epilogues; then its map: the image with its tiles, beside it the tile list and the map's other missions, then the
// map's hidden sections, whole map and tile images; last, the card back. `via` is the page it's reached through:
// 'missions' (crumbs: Missions), or 'agenda-cards' for an agenda mission reached as an agenda card, with its card's
// crumbs: under its deck when `under` it (a deck page's link), else the agenda cards list (crumbs).
export function mission(db, row, via, under = null) {
  const card = row.card;
  const name = title(row);
  const map = db.parent.get(row)?.ref;
  const image = card.record.image;
  const fields = [
    ['Type', kindLabel(card.type, true)],
    ...Object.entries(card.record).map(([field, value]) => [fieldLabel(field), fieldValue(card, field, value, db)]),
    ...row.record.location == null ? [] : [['Location', row.record.location]],
    ['Map', map ? html`<a href="${href(map)}">${title(map)}</a>` : html`<span class="none">—</span>`],
  ];

  const related = [];
  const sources = db.sources(card);
  if (sources.length) related.push(foundIn(row, sources, db));
  const parent = db.parent.get(card);
  if (parent) related.push(parentSection(parent, db));
  const rewards = db.rewards.get(card);
  if (rewards) related.push(section('Rewards', rewards.length, rewardList(rewards, db)));
  for (const {rel, refs} of [...db.children.get(card) ?? [], ...db.children.get(row) ?? []]) {
    related.push(section(rel.childrenLabel ?? TYPE[rel.child].label, refs.length, grid(refs, db)));
  }
  related.push(...linkSections(card, db));
  if (map) related.push(...missionMap(map, row, db));
  if (db.back.has(card)) related.push(backSection(card, db));
  const layout = map && db.layout.get(map);
  if (layout) related.push(closed('Tile images', layout.length, layoutList(layout, db)));

  const trail = crumbs(via === 'missions' ? row : card, under, db);
  return {
    title: name,
    nav: trail.nav,
    body: html`
      <p class="crumbs">${trail.html}</p>
      <h1>${name}</h1>
      <div class="detail">
        ${image ? html`<div class="images"><figure><a href="${imageUrl('large', image)}">
          <img src="${imageUrl('large', image)}" alt="${name}"></a></figure></div>` : ''}
        ${fieldsTable(fields)}
      </div>
      ${related}`,
  };
}

// A mission's map: its image with a box per tile, beside it its tile list and the map's other missions (a skirmish
// map's other scenario, a campaign map's other mission); then its hidden sections and whole map.
function missionMap(map, row, db) {
  const layout = db.layout.get(map) ?? [];
  const others = (db.children.get(map) ?? []).filter(({rel}) => rel.child === 'missions')
    .flatMap(({refs}) => refs).filter(ref => ref !== row);
  const aside = [
    layout.length ? section('Tiles', layout.length, layoutText(layout, db)) : '',
    others.length ? section('Also on this map', others.length, grid(others, db)) : '',
  ];
  return [html`
    <section class="related">
      <h2>Map: <a href="${href(map)}">${title(map)}</a></h2>
      <div class="detail">
        <div class="images">
          <figure>${mapFrame(map, db, [null], map.record.image, title(map))}</figure>
          ${layout.some(r => r.placements.length) ? SHOW_TILES : ''}
        </div>
        <div class="aside">${aside}</div>
      </div>
    </section>`, ...mapSections(map, db)];
}

export function search(db, query) {
  const q = query.trim().toLowerCase();
  // Missions are found through their missions rows (named after their cards), whose collections have no pages; an
  // agenda mission is also an agenda card.
  const matches = q ? VISIBLE.filter(t => !t.of)
    .flatMap(t => db.refs[t.file].filter(ref => title(ref).toLowerCase().includes(q))) : [];
  return {
    title: q ? `Search: ${query}` : 'Search',
    body: html`
      <h1>Search${q ? html` <span class="count">${matches.length}</span>` : ''}</h1>
      ${!q ? html`<p class="status">Type a name in the search box.</p>`
        : matches.length ? grouped(matches, db)
        : html`<p class="status">Nothing is named like “${query}”.</p>`}`,
  };
}

export function notFound() {
  return {
    title: 'Not found',
    body: html`<h1>Not found</h1><p class="status">There's nothing at this address. <a href="#/">Go home</a>.</p>`,
  };
}
