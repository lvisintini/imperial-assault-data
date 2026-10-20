import {TYPE} from './types.js';

// Sort keys are field names, '-' first for descending: ['-unique', 'name'].
export const defaultSort = type => TYPE[type].sort ?? ['name'];

const SCALARS = ['string', 'number', 'boolean'];

// Fields worth sorting a type by: plain values only, not lists, image paths, ids or foreign keys.
export function sortableFields(type, refs) {
  const fields = new Set(refs.flatMap(ref => Object.keys(ref.record)));
  return [...fields].filter(field => field !== 'id' && !TYPE[type].images.includes(field) && !field.endsWith('_id')
    && refs.every(({record}) => record[field] == null || SCALARS.includes(typeof record[field])));
}

// Keys from a ?sort= value, keeping only the given fields; the type's default when none are left.
export function parseSort(type, param, fields) {
  const keys = (param ?? '').split(',').filter(key => fields.includes(key.replace(/^-/, '')));
  return keys.length ? keys : defaultSort(type);
}

export const sameKeys = (a, b) => a.join(',') === b.join(',');

// Values listed in the field's `order` (types.js) come first, in that order; the rest follow, compared as usual.
function compareValues(a, b, ranked = []) {
  const rank = value => ranked.indexOf(value) + 1 || ranked.length + 1;
  return rank(a) - rank(b) || (typeof a === 'string' ? a.localeCompare(b, undefined, {numeric: true}) : a - b);
}

export function sortRefs(refs, keys) {
  const orders = TYPE[refs[0]?.type]?.order ?? {};
  const order = keys.map(key => {
    const field = key.replace(/^-/, '');
    return {field, sign: key.startsWith('-') ? -1 : 1, ranked: orders[field]};
  });
  return [...refs].sort((a, b) => {
    for (const {field, sign, ranked} of order) {
      const x = a.record[field], y = b.record[field];
      if (x == null || y == null) {
        if (x != null || y != null) return x == null ? 1 : -1;  // missing values last, in either direction
        continue;
      }
      const diff = compareValues(x, y, ranked);
      if (diff) return sign * diff;
    }
    return a.index - b.index;  // ties keep the file's order
  });
}
