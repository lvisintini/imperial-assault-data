import {html} from './html.js';
import {BACK, FKS, LINK_RELATIONS} from './relations.js';
import {anyActive, applyFilters, counts, defaultGroups, facetsFor, readFilters, writeFilters} from './facets.js';
import {defaultSort, parseSort, sameKeys, sortRefs, sortableFields} from './sort.js';
import {TYPE, TYPES, fieldLabel, title} from './types.js';

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

// A missions row links to, and looks like, its mission card.
export const href = ref => `#/${(ref.card ?? ref).type}/${(ref.card ?? ref).key}`;

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

// A map's or a tile's small image is its large one (same file), so the site only publishes images/small/maps and
// images/small/map-tiles (pages.yml).
const SMALL_ONLY = ['maps/', 'map-tiles/'];
const imageUrl = (size, path) =>
  `images/${SMALL_ONLY.some(folder => path.startsWith(folder)) ? 'small' : size}/${encodeURI(path)}`;

// A mission card's map, through its missions row.
const mapOf = (ref, db) => db.parent.get(db.mission.get(ref))?.ref;
const mapImage = (ref, db) => mapOf(ref, db)?.record.image;

function subtitle(ref, db) {
  if (ref.card) return TYPE[ref.card.type].singular;
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
function tile(ref, db, copies) {
  const peek = peekPath(ref, db);
  const name = title(ref);
  return html`<a class="tile" href="${href(ref)}"${peek ? html` data-peek="${imageUrl('large', peek)}"` : ''}>
    <span class="thumb">${thumb(ref, db)}</span>
    <span class="tile-title">${name}${copies > 1 ? html` <span class="copies">×${copies}</span>` : ''}</span>
    <span class="tile-sub">${subtitle(ref, db)}</span>
  </a>`;
}

// copiesOf: ref → how many copies to show on its tile (see tile).
const grid = (refs, db, keys, copiesOf = () => null) =>
  html`<div class="grid">${sorted(refs, keys).map(ref => tile(ref, db, copiesOf(ref)))}</div>`;

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
function grouped(refs, db, copiesOf) {
  const byType = Map.groupBy(refs, ref => ref.type);
  return TYPES.filter(t => byType.has(t.file)).map(t => html`
    <h3><a href="#/${t.file}">${t.label}</a> <span class="count">${byType.get(t.file).length}</span></h3>
    ${grid(byType.get(t.file), db, undefined, copiesOf)}`);
}

const section = (heading, count, body) => html`
  <section class="related">
    <h2>${heading}${count == null ? '' : html` <span class="count">${count}</span>`}</h2>
    ${body}
  </section>`;

export function landing(db) {
  const tiles = VISIBLE.map(t => {
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
  if (value == null || (Array.isArray(value) && !value.length)) return html`<span class="none">—</span>`;
  if (Array.isArray(value)) return value.join(', ');
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  return String(value);
}

// A map's tile sides, each with how many times the map places it.
function layoutList(rows, db) {
  return html`<div class="grid">${rows.map(({ref, side, count}) => {
    const path = ref.record[side === 'A' ? 'side_a' : 'side_b'];
    return html`<a class="tile" href="${href(ref)}" data-peek="${imageUrl('large', path)}">
      <span class="thumb"><img loading="lazy" src="${imageUrl('small', path)}" alt=""></span>
      <span class="tile-title">${title(ref)}${side}${count > 1 ? html` <span class="copies">×${count}</span>` : ''}</span>
      <span class="tile-sub">Side ${side}</span>
    </a>`;
  })}</div>`;
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

export function detail(db, ref) {
  const t = TYPE[ref.type];
  const name = title(ref);
  const images = t.images.filter(f => ref.record[f]).map(f => html`
    <figure>
      <a href="${imageUrl('large', ref.record[f])}">
        <img src="${imageUrl('large', ref.record[f])}" alt="${name}${t.images.length > 1 ? ` (${f})` : ''}">
      </a>
      ${t.images.length > 1 ? html`<figcaption>${fieldLabel(f)}</figcaption>` : ''}
    </figure>`);

  const related = [];
  const contents = db.contents.get(ref);
  if (contents) {
    const refs = [...contents.values()].flat();
    const copies = db.copies.get(ref);
    related.push(section('Contents', refs.length, grouped(refs, db, content => copies?.get(content))));
  }
  const sources = db.sources(ref);
  if (sources.length) {
    const content = db.mission.get(ref) ?? ref;  // a mission card's products are its missions row's
    related.push(section('Found in', sources.length, grid(sources, db, undefined, source => db.copies.get(source)?.get(content))));
  }
  const parent = db.parent.get(ref);
  if (parent) related.push(section(parent.rel.label ?? TYPE[parent.rel.parent].singular, null, grid([parent.ref], db)));
  // A mission card's own children, and its missions row's (its epilogues).
  for (const {rel, refs} of [...db.children.get(ref) ?? [], ...db.children.get(db.mission.get(ref)) ?? []]) {
    related.push(section(rel.childrenLabel ?? TYPE[rel.child].label, refs.length, grid(refs, db)));
  }
  // Record links, a section per relation as read from this end: "Figure of" on a miniature, "Miniatures" on what it
  // stands for, "Required by" on a product.
  for (const [relation, heading] of Object.entries(LINK_RELATIONS)) {
    const refs = (db.links.get(ref) ?? []).filter(link => link.relation === relation).map(link => link.ref);
    if (refs.length) related.push(section(heading, refs.length, grouped(refs, db)));
  }
  const map = mapOf(ref, db);
  if (map) related.push(section('Map', null, grid([map], db)));
  const layout = db.layout.get(ref);
  if (layout) related.push(section('Tiles', layout.length, layoutList(layout, db)));
  const usedIn = db.usedIn.get(ref);
  if (usedIn) related.push(section('Used in', usedIn.length, grid(usedIn, db)));
  const rewards = db.rewards.get(ref);
  if (rewards) related.push(section('Rewards', rewards.length, rewardList(rewards, db)));
  const rewardOf = db.rewardOf.get(ref);
  if (rewardOf) related.push(section('Reward from', rewardOf.length, grouped(rewardOf, db)));
  const back = db.back.get(ref);
  if (back) {
    const via = back.via ? ` (on its ${TYPE[back.via.type].label.toLowerCase()})` : '';
    related.push(section(`Card back${via}`, null, grid([back.ref], db)));
  }
  const backOf = db.backOf.get(ref);
  if (backOf) related.push(section('Back of', backOf.length, grouped(backOf, db)));

  return {
    title: name,
    body: html`
      <p class="crumbs"><a href="#/${ref.type}">${t.label}</a></p>
      <h1>${name}</h1>
      <div class="detail">
        ${images.length ? html`<div class="images">${images}</div>` : ''}
        <dl class="fields">${Object.entries(ref.record).map(([field, value]) => html`
          <dt>${fieldLabel(field)}</dt><dd>${fieldValue(ref, field, value, db)}</dd>`)}
        </dl>
      </div>
      ${related}`,
  };
}

export function search(db, query) {
  const q = query.trim().toLowerCase();
  // missions rows are named after their cards, which are found already.
  // ... and agenda missions are agenda cards.
  const matches = q ? VISIBLE.filter(t => t.file !== 'missions' && !t.of)
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
