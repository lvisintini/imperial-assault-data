// Facets: the ways a list page can filter and group a type's records, derived from the records themselves.
//   choice: records have zero or more of a fixed set of values (a field's values, its traits, its products).
//           Filtering keeps records with any ticked value; grouping puts a record under each of its values.
//   range:  records have a number, or none. Filtering keeps records within min..max, set with a two-knob slider
//           whose steps are the values' greatest common divisor (credits go in tens).
// Facets combine with AND, the values ticked within one facet with OR.
import {FKS} from './relations.js';
import {PRODUCT as PRODUCT_SORT, defaultSort} from './sort.js';
import {TYPE, fieldLabel, fileOf, kindLabel, title} from './types.js';

const SKIPPED = new Set(['id', 'name', 'description', 'iaspec']);
const MAX_CHOICES = 20;  // more distinct strings than this aren't a facet (e.g. names)
const MAX_PARENTS = 50;  // a parent facet (hero, Imperial class, agenda deck) with more choices than this isn't one
export const PRODUCT = 'source';
export const WAVE = 'wave';
export const PRODUCT_TYPE = 'product_type';

const compareKeys = (a, b) => a.localeCompare(b, undefined, {numeric: true});

// Product types in the products page's Type order (Core Game, Expansion, Ally Pack, Villain Pack...).
const PRODUCT_TYPES = TYPE.sources.order.type;
const byType = (a, b) => (PRODUCT_TYPES.indexOf(a) >>> 0) - (PRODUCT_TYPES.indexOf(b) >>> 0);

// The products' order in the Product filter: the Core Game and the expansions by product code; then the products
// without a code, in the products file's order (the Luke Skywalker and Darth Vader packs in the Core Set, the app);
// then every other product (ally and villain packs, map mats) by product code.
const BOXES = new Set(['Core Game', 'Expansion']);
const productRank = ({record}) => BOXES.has(record.type) ? 0 : record.product_code == null ? 1 : 2;
const byProductOrder = (a, b) => productRank(a) - productRank(b)
  || (a.record.product_code ?? '').localeCompare(b.record.product_code ?? '') || a.index - b.index;

// `heading` is a value's group heading, when it isn't its label.
function choice(id, label, of, keys, labels = {}, headings = {}) {
  const choices = keys.map(key => ({key, label: labels[key] ?? key, heading: headings[key] ?? labels[key] ?? key}));
  return {id, label, kind: 'choice', of, choices};
}

// Yes/No in the filter panel; as group headings, "Elite" / "Not elite" unless given.
function booleanFacet(id, label, of, {keys = ['true', 'false'], headings} = {}) {
  headings ??= {true: label, false: `Not ${label.toLowerCase()}`};
  return choice(id, label, of, keys, {true: 'Yes', false: 'No'}, headings);
}

// A trait as a yes/no facet ("Skirmish upgrade"), records without it first: {id, label, trait, yes, no}.
function traitFacet({id, label, trait, yes, no}) {
  const of = ({record}) => [String(record.traits?.includes(trait) ?? false)];
  const headings = {true: yes ?? label, false: no ?? `Not ${label.toLowerCase()}`};
  return booleanFacet(id, label, of, {keys: ['false', 'true'], headings});
}

// A content_type value (a mission's kind) named by its collection: the missions page's agenda cards are agenda missions.
const typeLabel = kindLabel;

// A choice over a field of the record's children through a foreign key in FKS (relations.js): a map's missions' kinds
// ({id, label, children: 'missions', field: 'content_type', none}). Values follow the children type's `order`; `none`
// names a choice for records without children, when given.
function childFacet({id, label, children, field, none}, refs, db) {
  const of = ref => {
    const kids = db.children.get(ref)?.find(group => group.rel.child === children)?.refs ?? [];
    const keys = [...new Set(kids.map(kid => kid.record[field]).filter(v => v != null))];
    return keys.length || !none ? keys : ['none'];
  };
  const found = new Set(refs.flatMap(of));
  const order = TYPE[children].order?.[field] ?? [];
  const keys = [...order.filter(k => found.has(k)),
    ...[...found].filter(k => !order.includes(k) && k !== 'none').sort(compareKeys), ...found.has('none') ? ['none'] : []];
  const labels = Object.fromEntries(keys.map(k => [k, k === 'none' ? none : field === 'content_type' ? typeLabel(k) : k]));
  return keys.length ? choice(id, label, of, keys, labels) : null;
}

function fieldFacet(type, field, refs) {
  const values = refs.map(ref => ref.record[field]).filter(v => v != null);
  if (!values.length) return null;
  const label = TYPE[type].labels?.[field] ?? fieldLabel(field);
  const order = TYPE[type].order?.[field] ?? [];
  const sortKeys = keys => [...order.filter(k => keys.includes(k)),
    ...keys.filter(k => !order.includes(k)).sort(compareKeys)];
  if (values.every(v => typeof v === 'boolean')) {
    return booleanFacet(field, label, ({record}) => record[field] == null ? [] : [String(record[field])]);
  }
  // A number field listed in `choices` (an upgrade card's tier) is ticked value by value, as "Tier 2" in groups.
  if (TYPE[type].choices?.includes(field) && values.every(v => typeof v === 'number')) {
    const keys = [...new Set(values)].sort((a, b) => a - b).map(String);
    return choice(field, label, ({record}) => (record[field] == null ? [] : [String(record[field])]), keys, {},
      Object.fromEntries(keys.map(k => [k, `${label} ${k}`])));
  }
  if (values.every(v => typeof v === 'number')) {
    const min = Math.min(...values), max = Math.max(...values);
    if (min === max) return null;
    return {id: field, label, kind: 'range', of: ({record}) => record[field] ?? null, min, max, step: step(values, min)};
  }
  if (values.every(v => Array.isArray(v) && v.every(x => typeof x === 'string'))) {
    const keys = [...new Set(values.flat())];
    return keys.length ? choice(field, label, ({record}) => record[field] ?? [], sortKeys(keys)) : null;
  }
  if (values.every(v => typeof v === 'string')) {
    const keys = [...new Set(values)];
    if (keys.length > MAX_CHOICES) return null;
    const labels = field === 'content_type' ? Object.fromEntries(keys.map(k => [k, typeLabel(k)])) : {};
    return choice(field, label, ({record}) => (record[field] == null ? [] : [record[field]]), sortKeys(keys), labels);
  }
  return null;
}

const gcd = (a, b) => b ? gcd(b, a % b) : a;

// The slider's step: the greatest common divisor of the values' distances from the lowest, or 'any' for fractions.
function step(values, min) {
  if (!values.every(Number.isInteger)) return 'any';
  return values.reduce((d, v) => gcd(d, v - min), 0) || 1;
}

// A choice per parent record, for children of a foreign key in FKS (relations.js): a hero class card's hero, an
// agenda card's deck. Named after the parent type, its choices in name order.
function parentFacets(type, refs, db) {
  return FKS.filter(rel => rel.child === fileOf(type)).map(rel => {
    const parents = [...new Set(refs.map(ref => db.parent.get(ref)?.ref).filter(Boolean))]
      .sort((a, b) => title(a).localeCompare(title(b)));
    if (!parents.length || parents.length > MAX_PARENTS) return null;
    return choice(rel.field, rel.label ?? TYPE[rel.parent].singular,
      ref => [db.parent.get(ref)?.ref.key].filter(Boolean), parents.map(p => p.key),
      Object.fromEntries(parents.map(p => [p.key, title(p)])));
  });
}

function productFacets(type, refs, db) {
  // A product is its own (db.productsOf), so the products page gets the same Wave facet, in place of a range on its
  // wave field. Products run in the products file's order, newest first when the type sorts by '-product'.
  const found = new Map(refs.map(ref => [ref, db.productsOf(ref)]));
  const newest = defaultSort(type)[0] === `-${PRODUCT_SORT}`;
  const sources = [...new Set([...found.values()].flat())].sort((a, b) => newest ? b.index - a.index : a.index - b.index);
  if (!sources.length) return [];
  const waveKey = source => source.record.wave == null ? 'none' : String(source.record.wave);
  const waves = [...new Set(sources.map(waveKey))].sort(compareKeys);
  // Product types in the products page's Type order (Core Game, Expansion, Ally Pack, Villain Pack...).
  const kinds = [...new Set(sources.map(s => s.record.type))].sort(byType);
  const product = choice(PRODUCT, 'Product', ref => found.get(ref).map(s => String(s.key)), sources.map(s => String(s.key)),
    Object.fromEntries(sources.map(s => [String(s.key), s.record.name])));
  // Its groups keep the products' order; its filter lists them as byProductOrder does (`options`, views.js
  // filterPanel).
  const at = new Map(product.choices.map(c => [c.key, c]));
  product.options = [...sources].sort(byProductOrder).map(s => at.get(String(s.key)));
  return [
    product,
    choice(PRODUCT_TYPE, 'Product type', ref => [...new Set(found.get(ref).map(s => s.record.type))], kinds),
    choice(WAVE, 'Wave', ref => [...new Set(found.get(ref).map(waveKey))], waves,
      Object.fromEntries(waves.map(w => [w, w === 'none' ? 'No wave' : `Wave ${w}`]))),
  ];
}

// Every facet of a type's records: product, product type and wave first, then its parent's and its fields'; `facets` in
// types.js picks and orders them.
export function facetsFor(type, refs, db) {
  const t = TYPE[type];
  const fields = [...new Set(refs.flatMap(ref => Object.keys(ref.record)))]
    .filter(f => !SKIPPED.has(f) && !f.endsWith('_id') && !t.images.includes(f));
  const derived = new Map([...productFacets(type, refs, db), ...parentFacets(type, refs, db),
    ...fields.map(f => fieldFacet(type, f, refs))].filter(Boolean).map(f => [f.id, f]));
  if (!t.facets) return [...derived.values()];
  return t.facets.map(spec => typeof spec === 'string' ? derived.get(spec)
    : spec.children ? childFacet(spec, refs, db) : traitFacet(spec)).filter(Boolean);
}

export const defaultGroups = (type, facets) => (TYPE[type].groups ?? []).filter(id => facets.some(f => f.id === id));

// Filters: {facet id: Set of choice keys | {min, max}}. Inactive filters are left out.
const isActive = filter =>
  filter instanceof Set ? filter.size > 0 : Boolean(filter) && (filter.min != null || filter.max != null);

function matches(ref, facet, filter) {
  if (facet.kind === 'range') {
    const value = facet.of(ref);
    return value != null && (filter.min == null || value >= filter.min) && (filter.max == null || value <= filter.max);
  }
  return facet.of(ref).some(key => filter.has(key));
}

// The refs that pass the name query and every filter (except one facet's, for its counts).
export function applyFilters(refs, facets, filters, query = '', except = null) {
  const q = query.trim().toLowerCase();
  const active = facets.filter(f => f.id !== except && isActive(filters[f.id]));
  return refs.filter(ref => (!q || title(ref).toLowerCase().includes(q))
    && active.every(f => matches(ref, f, filters[f.id])));
}

// How many records each value would match if ticked, given every other facet's filter.
export function counts(refs, facets, filters, query) {
  return Object.fromEntries(facets.filter(f => f.kind === 'choice').map(facet => {
    const base = applyFilters(refs, facets, filters, query, facet.id);
    const tally = Object.fromEntries(facet.choices.map(c => [c.key, 0]));
    for (const ref of base) for (const key of facet.of(ref)) if (key in tally) tally[key] += 1;
    return [facet.id, tally];
  }));
}

export const anyActive = filters => Object.values(filters).some(isActive);

// URL form: f.<facet>=key|key for choices, f.<facet>=min..max (either end may be empty) for ranges.
export function readFilters(params, facets) {
  const filters = {};
  for (const facet of facets) {
    const value = params.get(`f.${facet.id}`);
    if (!value) continue;
    if (facet.kind === 'range') {
      const [min, max] = value.split('..').map(v => v === '' || isNaN(Number(v)) ? null : Number(v));
      filters[facet.id] = {min: min ?? null, max: max ?? null};
    } else {
      const known = new Set(facet.choices.map(c => c.key));
      filters[facet.id] = new Set(value.split('|').filter(k => known.has(k)));
    }
  }
  return filters;
}

export function writeFilters(filters, facets) {
  return facets.filter(f => isActive(filters[f.id])).map(f => {
    const filter = filters[f.id];
    const value = f.kind === 'range' ? `${filter.min ?? ''}..${filter.max ?? ''}`
      : f.choices.filter(c => filter.has(c.key)).map(c => c.key).join('|');
    return `f.${f.id}=${encodeURIComponent(value).replaceAll('%7C', '|')}`;
  });
}
