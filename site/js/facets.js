// Facets: the ways a list page can filter and group a type's records, derived from the records themselves.
//   choice: records have zero or more of a fixed set of values (a field's values, its traits, its products).
//           Filtering keeps records with any ticked value; grouping puts a record under each of its values.
//   range:  records have a number, or none. Filtering keeps records within min..max, set with a two-knob slider
//           whose steps are the values' greatest common divisor (credits go in tens).
// Facets combine with AND, the values ticked within one facet with OR.
import {FKS} from './relations.js';
import {TYPE, TYPES, fieldLabel, fileOf, title} from './types.js';

const SKIPPED = new Set(['id', 'name', 'description', 'iaspec']);
const MAX_CHOICES = 20;  // more distinct strings than this aren't a facet (e.g. names)
const MAX_PARENTS = 50;  // a parent facet (hero, Imperial class, agenda deck) with more choices than this isn't one
export const PRODUCT = 'source';
export const WAVE = 'wave';

const compareKeys = (a, b) => a.localeCompare(b, undefined, {numeric: true});

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

// A content type named by its page: the missions page's agenda cards are agenda missions.
const typeLabel = k => TYPES.find(t => t.of === k)?.label ?? TYPE[k]?.label ?? k;

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

function productFacets(refs, db) {
  // A product is its own (db.productsOf), so the products page gets the same Wave facet, in place of a range on its
  // wave field.
  const found = new Map(refs.map(ref => [ref, db.productsOf(ref)]));
  const sources = [...new Set([...found.values()].flat())].sort((a, b) => a.index - b.index);
  if (!sources.length) return [];
  const waveKey = source => source.record.wave == null ? 'none' : String(source.record.wave);
  const waves = [...new Set(sources.map(waveKey))].sort(compareKeys);
  return [
    choice(PRODUCT, 'Product', ref => found.get(ref).map(s => String(s.key)), sources.map(s => String(s.key)),
      Object.fromEntries(sources.map(s => [String(s.key), s.record.name]))),
    choice(WAVE, 'Wave', ref => [...new Set(found.get(ref).map(waveKey))], waves,
      Object.fromEntries(waves.map(w => [w, w === 'none' ? 'No wave' : `Wave ${w}`]))),
  ];
}

// Every facet of a type's records: from its fields, plus product and wave; `facets` in types.js picks and orders them.
export function facetsFor(type, refs, db) {
  const t = TYPE[type];
  const fields = [...new Set(refs.flatMap(ref => Object.keys(ref.record)))]
    .filter(f => !SKIPPED.has(f) && !f.endsWith('_id') && !t.images.includes(f));
  const derived = new Map([...parentFacets(type, refs, db), ...fields.map(f => fieldFacet(type, f, refs)),
    ...productFacets(refs, db)].filter(Boolean).map(f => [f.id, f]));
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
