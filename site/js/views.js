import {html} from './html.js';
import {FKS} from './relations.js';
import {anyActive, applyFilters, counts, defaultGroups, facetsFor, readFilters, writeFilters} from './facets.js';
import {defaultSort, parseSort, sameKeys, sortRefs, sortableFields} from './sort.js';
import {TYPE, TYPES, fieldLabel, title} from './types.js';

const MERMAID_URL = 'https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.esm.min.mjs';
const DATA_MODEL_URL = 'https://github.com/lvisintini/imperial-assault-data/blob/master/docs/data-model.md';
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

const imageUrl = (size, path) => `images/${size}/${encodeURI(path)}`;

// A mission card's map, through its missions row.
const mapOf = (ref, db) => db.parent.get(db.mission.get(ref))?.ref;
const mapImage = (ref, db) => mapOf(ref, db)?.record.image;

function subtitle(ref, db) {
  if (ref.card) return TYPE[ref.card.type].singular;
  const {record} = ref;
  const parent = db.parent.get(ref);
  if (parent && ref.type !== 'sources') return title(parent.ref);  // a pack in the Core Set is still a pack
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
    case 'skirmish-mission-cards': return [mapOf(ref, db) && title(mapOf(ref, db)), record.scenario,
      record.format !== 'Standard' && record.format].filter(Boolean).join(' · ');
    case 'card-backs': return TYPE[record.content_type]?.label;
  }
}

function tile(ref, db) {
  const path = thumbPath(ref, db);
  const peek = peekPath(ref, db);
  const name = title(ref);
  return html`<a class="tile" href="${href(ref)}"${peek ? html` data-peek="${imageUrl('large', peek)}"` : ''}>
    <span class="thumb">${path
      ? html`<img loading="lazy" src="${imageUrl('small', path)}" alt="">`
      : html`<span class="no-image">No image</span>`}</span>
    <span class="tile-title">${name}</span>
    <span class="tile-sub">${subtitle(ref, db)}</span>
  </a>`;
}

const grid = (refs, db, keys) => html`<div class="grid">${sorted(refs, keys).map(ref => tile(ref, db))}</div>`;

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

// A fieldset per facet: checkboxes (their counts are filled in by the page) or a min/max pair.
function filterPanel(facets, filters) {
  return facets.map(facet => facet.kind === 'range' ? html`
    <fieldset class="facet">
      <legend>${facet.label}</legend>
      <span class="range">${['min', 'max'].map((bound, i) => html`${i ? html`<span aria-hidden="true">–</span>` : ''}
        <input type="number" inputmode="numeric" data-facet="${facet.id}" data-bound="${bound}" min="${facet.min}"
          max="${facet.max}" placeholder="${facet[bound]}" value="${filters[facet.id]?.[bound] ?? ''}"
          aria-label="${facet.label}: ${i ? 'at most' : 'at least'}">`)}
      </span>
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
function grouped(refs, db) {
  const byType = Map.groupBy(refs, ref => ref.type);
  return TYPES.filter(t => byType.has(t.file)).map(t => html`
    <h3><a href="#/${t.file}">${t.label}</a> <span class="count">${byType.get(t.file).length}</span></h3>
    ${grid(byType.get(t.file), db)}`);
}

const section = (heading, count, body) => html`
  <section class="related">
    <h2>${heading}${count == null ? '' : html` <span class="count">${count}</span>`}</h2>
    ${body}
  </section>`;

export function landing(db) {
  const tiles = VISIBLE.map(t => {
    const first = sorted(db.refs[t.file])[0];
    const path = first && thumbPath(first, db);
    return html`<a class="tile" href="#/${t.file}">
      <span class="thumb">${path ? html`<img loading="lazy" src="${imageUrl('small', path)}" alt="">` : ''}</span>
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
        <p>How the data files relate. The full write-up, including how card backs are matched, is in
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
        for (const bound of panel?.querySelectorAll('input[type=number]') ?? []) bound.value = '';
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
      let typing = null;
      panel?.addEventListener('input', event => {
        const bound = event.target.closest('input[type=number]');
        if (!bound) return;
        const read = side => {
          const value = panel.querySelector(`[data-facet="${bound.dataset.facet}"][data-bound="${side}"]`).value;
          return value === '' ? null : Number(value);
        };
        clearTimeout(typing);
        typing = setTimeout(() => {
          state.filters[bound.dataset.facet] = {min: read('min'), max: read('max')};
          update();
        }, 250);
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
  const fk = FKS.find(rel => rel.child === ref.type && rel.field === field);
  if (fk) {
    const parent = db.get(fk.parent, value);
    if (parent) return html`<a href="${href(parent)}">${title(parent)}</a>`;
  }
  if (ref.type === 'card-backs' && field === 'content_type' && TYPE[value]) {
    return html`<a href="#/${value}">${TYPE[value].label}</a>`;
  }
  if (TYPE[ref.type].images.includes(field) && value) {
    return html`<a href="${imageUrl('large', value)}"><code>${value}</code></a>`;
  }
  if (value == null || (Array.isArray(value) && !value.length)) return html`<span class="none">—</span>`;
  if (Array.isArray(value)) return value.join(', ');
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  return String(value);
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
    related.push(section('Contents', refs.length, grouped(refs, db)));
  }
  const sources = db.sources(ref);
  if (sources.length) related.push(section('Found in', sources.length, grid(sources, db)));
  const parent = db.parent.get(ref);
  if (parent) related.push(section(parent.rel.label ?? TYPE[parent.rel.parent].singular, null, grid([parent.ref], db)));
  for (const {rel, refs} of db.children.get(ref) ?? []) {
    related.push(section(rel.childrenLabel ?? TYPE[rel.child].label, refs.length, grid(refs, db)));
  }
  const map = mapOf(ref, db);
  if (map) related.push(section('Map', null, grid([map], db)));
  const rewards = db.rewards.get(ref);
  if (rewards) related.push(section('Rewards', rewards.length, rewardList(rewards, db)));
  const rewardOf = db.rewardOf.get(ref);
  if (rewardOf) related.push(section('Reward from', rewardOf.length, grouped(rewardOf, db)));
  const back = db.back.get(ref);
  if (back) {
    const via = back.via ? ` (same as its ${TYPE[back.via.type].singular.toLowerCase()})` : '';
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
  const matches = q ? VISIBLE.filter(t => t.file !== 'missions')
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
