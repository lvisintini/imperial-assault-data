import {html} from './html.js';
import {FKS} from './relations.js';
import {defaultSort, parseSort, sameKeys, sortRefs, sortableFields} from './sort.js';
import {TYPE, TYPES, fieldLabel, title} from './types.js';

const MERMAID_URL = 'https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.esm.min.mjs';
const DATA_MODEL_URL = 'https://github.com/lvisintini/imperial-assault-data/blob/master/docs/data-model.md';
const VISIBLE = TYPES.filter(t => !t.hidden);

export const href = ref => `#/${ref.type}/${ref.key}`;

// In the given order, or the type's default one (lists of a single type).
const sorted = (refs, keys) => refs.length ? sortRefs(refs, keys ?? defaultSort(refs[0].type)) : refs;

// Records without images of their own (agenda decks, imperial classes) show their card back.
function thumbPath(ref, db) {
  const field = TYPE[ref.type].images.find(f => ref.record[f]);
  return field ? ref.record[field] : db.back.get(ref)?.ref.record.image;
}

const imageUrl = (size, path) => `images/${size}/${encodeURI(path)}`;

function subtitle(ref, db) {
  const {record} = ref;
  const parent = db.parent.get(ref);
  if (parent) return title(parent.ref);
  switch (ref.type) {
    case 'sources': return record.wave ? `${record.type} · Wave ${record.wave}` : record.type;
    // Enough to tell apart same-named cards: elite/regular pairs and campaign/skirmish versions.
    case 'deployment-cards': return [
      record.description,
      record.affiliation,
      record.elite ? 'Elite' : 'Regular',
      record.modes.length === 1 && `${record.modes[0]} only`,
    ].filter(Boolean).join(' · ');
    case 'upgrade-cards': return `Tier ${record.tier}`;
    case 'card-backs': return TYPE[record.content_type]?.label;
  }
}

function tile(ref, db) {
  const path = thumbPath(ref, db);
  const name = title(ref);
  return html`<a class="tile" href="${href(ref)}" data-name="${name.toLowerCase()}">
    <span class="thumb">${path
      ? html`<img loading="lazy" src="${imageUrl('small', path)}" alt="">`
      : html`<span class="no-image">No image</span>`}</span>
    <span class="tile-title">${name}</span>
    <span class="tile-sub">${subtitle(ref, db)}</span>
  </a>`;
}

const grid = (refs, db, keys) => html`<div class="grid">${sorted(refs, keys).map(ref => tile(ref, db))}</div>`;

// A type's `groups` (types.js) as nested sections: <h2> for the first level, <h3> below it.
const groupOf = (level, {record}) =>
  level.trait ? (record.traits?.includes(level.trait) ? level.yes : level.no) : record[level.field];
const groupOrder = level => level.trait ? [level.no, level.yes] : level.order;

function sections(refs, levels, db, keys, depth = 0) {
  if (!levels.length) return grid(refs, db, keys);
  const [level, ...rest] = levels;
  const byGroup = Map.groupBy(refs, ref => groupOf(level, ref));
  const order = groupOrder(level);
  return [...order, ...[...byGroup.keys()].filter(g => !order.includes(g))].filter(g => byGroup.has(g)).map(g => {
    const count = html` <span class="count">${byGroup.get(g).length}</span>`;
    return html`<section class="group">
      ${depth ? html`<h3>${g}${count}</h3>` : html`<h2>${g}${count}</h2>`}
      ${sections(byGroup.get(g), rest, db, keys, depth + 1)}
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

export function index(db, type, query, sortParam) {
  const t = TYPE[type];
  const refs = db.refs[type];
  const fields = sortableFields(type, refs);
  let keys = parseSort(type, sortParam, fields);
  const list = () => t.groups ? sections(refs, t.groups, db, keys) : grid(refs, db, keys);
  return {
    title: t.label,
    body: html`
      <h1>${t.label} <span class="count">${refs.length}</span></h1>
      <div class="controls">
        <input type="search" id="filter" class="filter" placeholder="Filter by name" aria-label="Filter by name"
          value="${query}">
        <div class="sort" id="sort">${sortControls(type, fields, keys)}</div>
      </div>
      <div id="list">${list()}</div>
      <p class="status" id="no-matches" hidden>No matches.</p>`,
    mount: el => {
      const input = el.querySelector('#filter');
      const sortEl = el.querySelector('#sort');
      const listEl = el.querySelector('#list');
      const apply = () => {
        const q = input.value.trim();
        const tiles = [...listEl.querySelectorAll('.tile')];
        for (const tile of tiles) tile.hidden = !tile.dataset.name.includes(q.toLowerCase());
        for (const group of listEl.querySelectorAll('.group')) {
          const shown = group.querySelectorAll('.tile:not([hidden])').length;
          group.hidden = !shown;
          group.querySelector(':scope > :is(h2, h3) .count').textContent = shown;
        }
        el.querySelector('#no-matches').hidden = tiles.some(tile => !tile.hidden);
        const params = [q && `q=${encodeURIComponent(q)}`, !sameKeys(keys, defaultSort(type)) && `sort=${keys.join(',')}`];
        // replaceState doesn't fire hashchange, so typing or sorting doesn't re-render the page (or steal focus).
        history.replaceState(null, '', `#/${type}${params.some(Boolean) ? `?${params.filter(Boolean).join('&')}` : ''}`);
      };
      const setKeys = next => {
        // Re-rendering the controls drops focus; put it back on the same control (or the first one).
        const active = sortEl.contains(document.activeElement) ? document.activeElement.dataset : null;
        const selector = active?.level ? `[data-level="${active.level}"]`
          : active?.direction ? `[data-direction="${active.direction}"]` : 'select';
        keys = next.length ? next : defaultSort(type);
        listEl.innerHTML = String(list());
        sortEl.innerHTML = String(sortControls(type, fields, keys));
        if (active) (sortEl.querySelector(selector) ?? sortEl.querySelector('select')).focus();
        apply();
      };
      sortEl.addEventListener('change', event => {
        const i = Number(event.target.dataset.level);
        const field = event.target.value;
        const next = [...keys];
        if (!field) next.splice(i, 1);
        else next[i] = (next[i]?.startsWith('-') ? '-' : '') + field;
        setKeys(next.filter((key, j) => !field || j === i || key.replace(/^-/, '') !== field));
      });
      sortEl.addEventListener('click', event => {
        const button = event.target.closest('button');
        if (!button) return;
        if (button.dataset.reset !== undefined) return setKeys(defaultSort(type));
        const i = Number(button.dataset.direction);
        setKeys(keys.map((key, j) => j !== i ? key : key.startsWith('-') ? key.slice(1) : `-${key}`));
      });
      input.addEventListener('input', apply);
      if (query) apply();
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
  if (parent) related.push(section(TYPE[parent.rel.parent].singular, null, grid([parent.ref], db)));
  for (const {rel, refs} of db.children.get(ref) ?? []) {
    related.push(section(TYPE[rel.child].label, refs.length, grid(refs, db)));
  }
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
  const matches = q ? VISIBLE.flatMap(t => db.refs[t.file].filter(ref => title(ref).toLowerCase().includes(q))) : [];
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
