import {BACK, FKS, JOIN, LAYOUTS, LINKS, MATCHES, MISSIONS, REWARDS, UNDER} from './relations.js';
import {TYPES} from './types.js';

// The missions' maps (missions.map_id).
const MAP = FKS.find(rel => rel.child === MISSIONS.table && rel.parent === 'maps');

export async function load() {
  const tables = await Promise.all(TYPES.filter(t => !t.of).map(async ({file}) => {
    const res = await fetch(`data/${file}.json`);
    if (!res.ok) throw new Error(`data/${file}.json: HTTP ${res.status}`);
    return [file, await res.json()];
  }));
  const db = new Db(Object.fromEntries(tables));
  // Pages that show some of another type's records (agenda missions): those refs, as they are.
  for (const t of TYPES.filter(t => t.of)) db.refs[t.file] = db.refs[t.of].filter(ref => t.where(ref.record));
  return db;
}

function push(map, key, value) {
  const list = map.get(key);
  if (list) list.push(value);
  else map.set(key, [value]);
}

// Records are wrapped in refs, {type, key, index, record}: key is the record's id (a UUID), or its array index in
// source-contents and mission-rewards, which have no ids; index is its position in the file, used to keep a stable
// order. A missions row's ref also has `card`, the mission card it stands for (whose ref has `row`), and every ref has `release`, its
// earliest product's release date and product code ("2014-12-15|SWI01"), or null when it's in no product: the default
// sort's 'product' key (sort.js). A record whose pages are under another's (relations.js UNDER) has `under`.
class Db {
  constructor(tables) {
    this.refs = {};
    this.keyed = {};
    for (const [type, records] of Object.entries(tables)) {
      this.refs[type] = records.map((record, i) => ({type, key: record.id ?? i, index: i, record}));
      this.keyed[type] = new Map(this.refs[type].map(ref => [ref.key, ref]));
    }
    this.foundIn = new Map();   // content ref → source refs
    this.contents = new Map();  // source ref → Map(type → content refs)
    this.copies = new Map();    // source ref → Map(content ref → quantity), when more than 1
    this.parent = new Map();    // child ref → {rel, ref}
    this.children = new Map();  // parent ref → [{rel, refs}]
    this.back = new Map();      // ref → {ref: card-back ref, via: a child ref when it's its cards' back}
    this.mission = new Map();   // mission card ref → its missions row
    this.rewards = new Map();   // mission card ref → [{ref (null for credits), credits, choice}]
    this.rewardOf = new Map();  // reward ref → missions rows
    this.links = new Map();     // ref → [{relation, ref}]: its record-links, read from its end
    this.layout = new Map();    // map ref → [{ref: tile ref, side, count, placements: [{section, x, y, rotation}]}]
    this.usedIn = new Map();    // tile ref → {A: map refs, B: map refs}: the maps that use each of its sides
    this.matches = new Map();   // tile ref → [{side, ref: another tile ref, otherSide}]: its interchangeable sides
    this.#linkSources();
    this.#linkMissions();
    this.#linkRecords();
    this.#linkLayouts();
    this.#linkMatches();
    this.#linkParents();
    this.#linkChildProducts();
    this.#linkBacks();
    for (const refs of Object.values(this.refs)) for (const ref of refs) ref.release = this.#release(ref);
  }

  get(type, key) {
    return this.keyed[type]?.get(key);
  }

  // A mission card's products are its missions row's.
  sources(ref) {
    return this.foundIn.get(this.mission.get(ref) ?? ref) ?? [];
  }

  // The products a record comes in: its own source-contents rows, or its parent's (hero class cards, agenda cards, ...).
  // A product is its own.
  productsOf(ref) {
    if (ref.type === JOIN.parent) return [ref];
    const own = this.sources(ref);
    const parent = this.parent.get(ref);
    return own.length || !parent ? own : this.sources(parent.ref);
  }

  // Products without a code of their own (the packs inside the Core Set, the app) sort after those released the same
  // day.
  #release(ref) {
    const keys = this.productsOf(ref.card ?? ref)
      .map(({record}) => `${record.release_date ?? '9999'}|${record.product_code ?? 'SWI99'}`).sort();
    return keys[0] ?? null;
  }

  #linkSources() {
    for (const {record: row} of this.refs[JOIN.via]) {
      const source = this.get(JOIN.parent, row[JOIN.fk]);
      const content = this.get(row[JOIN.type], row[JOIN.id]);
      if (!source || !content) {
        console.warn('Unresolved source-contents row', row);
        continue;
      }
      push(this.foundIn, content, source);
      if (!this.contents.has(source)) this.contents.set(source, new Map());
      push(this.contents.get(source), content.type, content);
      if (row[JOIN.quantity] > 1) {
        if (!this.copies.has(source)) this.copies.set(source, new Map());
        this.copies.get(source).set(content, row[JOIN.quantity]);
      }
    }
  }

  #linkMissions() {
    for (const row of this.refs[MISSIONS.table]) {
      const card = this.get(row.record[MISSIONS.type], row.record[MISSIONS.id]);
      if (!card) {
        console.warn('Unresolved missions row', row.record);
        continue;
      }
      row.card = card;
      card.row = row;
      this.mission.set(card, row);
      // A map has no page of its own: its address is its first mission's (views.href).
      const map = this.get(MAP.parent, row.record[MAP.field]);
      if (map && !map.row) map.row = row;
    }
    for (const {record} of this.refs[REWARDS.table]) {
      const row = this.get(MISSIONS.table, record[REWARDS.mission]);
      const reward = record.credits ? null : this.get(record[REWARDS.type], record[REWARDS.id]);
      if (!row?.card || (!record.credits && !reward)) {
        console.warn('Unresolved mission-rewards row', record);
        continue;
      }
      push(this.rewards, row.card, {ref: reward, credits: record.credits, choice: record.choice});
      if (reward) push(this.rewardOf, reward, row);
    }
  }

  #linkRecords() {
    for (const {record} of this.refs[LINKS.table]) {
      const from = this.get(record[LINKS.fromType], record[LINKS.from]);
      const to = this.get(record[LINKS.toType], record[LINKS.to]);
      if (!from || !to) {
        console.warn('Unresolved record-links row', record);
        continue;
      }
      push(this.links, from, {relation: record[LINKS.relation], ref: to});
      push(this.links, to, {relation: record[LINKS.reverse], ref: from});
    }
    // A record whose pages are under another's (UNDER): `under` is the first it's linked to, in record-links order.
    for (const [type, relation] of Object.entries(UNDER)) {
      for (const ref of this.refs[type]) ref.under = this.links.get(ref)?.find(link => link.relation === relation)?.ref;
    }
  }

  #linkLayouts() {
    for (const {record} of this.refs[LAYOUTS.table]) {
      const map = this.get('maps', record[LAYOUTS.map]);
      const tile = this.get('map-tiles', record[LAYOUTS.tile]);
      if (!map || !tile) {
        console.warn('Unresolved map-layouts row', record);
        continue;
      }
      push(this.layout, map, {ref: tile, side: record[LAYOUTS.side], count: record[LAYOUTS.count],
        placements: record[LAYOUTS.placements] ?? []});
      const sides = this.usedIn.get(tile) ?? {};
      if (!this.usedIn.has(tile)) this.usedIn.set(tile, sides);
      const side = record[LAYOUTS.side];
      if (!sides[side]?.includes(map)) (sides[side] ??= []).push(map);
    }
  }

  #linkMatches() {
    for (const {record} of this.refs[MATCHES.table]) {
      const tile = this.get('map-tiles', record[MATCHES.tile]);
      const other = this.get('map-tiles', record[MATCHES.other]);
      if (!tile || !other) {
        console.warn('Unresolved map-tile-matches row', record);
        continue;
      }
      push(this.matches, tile, {side: record[MATCHES.side], ref: other, otherSide: record[MATCHES.otherSide]});
      push(this.matches, other, {side: record[MATCHES.otherSide], ref: tile, otherSide: record[MATCHES.side]});
    }
  }

  #linkParents() {
    for (const rel of FKS) {
      for (const child of this.refs[rel.child]) {
        const parent = this.get(rel.parent, child.record[rel.field]);
        if (!parent) continue;
        this.parent.set(child, {rel, ref: parent});
        // Its parent's name, as a sort key named after the field without its _id (sort.js: a hero class card's 'hero').
        child.parents = {...child.parents, [rel.field.replace(/_id$/, '')]: parent.record.name};
        const groups = this.children.get(parent) ?? [];
        if (!this.children.has(parent)) this.children.set(parent, groups);
        const group = groups.find(g => g.rel === rel);
        if (group) group.refs.push(child);
        else groups.push({rel, refs: [child]});
      }
    }
  }

  // Parents whose products are their children's (maps, through their missions), listed in those products' contents.
  #linkChildProducts() {
    for (const [parent, groups] of this.children) {
      const sources = new Set(this.foundIn.get(parent));
      for (const {rel, refs} of groups) {
        if (rel.products !== 'children') continue;
        for (const child of refs) for (const source of this.sources(child)) sources.add(source);
      }
      const added = [...sources].filter(source => !this.foundIn.get(parent)?.includes(source));
      if (!added.length) continue;
      this.foundIn.set(parent, [...sources].sort((a, b) => a.index - b.index));
      for (const source of added) {
        if (!this.contents.has(source)) this.contents.set(source, new Map());
        push(this.contents.get(source), parent.type, parent);
      }
    }
  }

  #linkBacks() {
    for (const refs of Object.values(this.refs)) {
      for (const ref of refs) {
        const id = ref.record[BACK.field];
        if (id == null) continue;
        const back = this.get(BACK.parent, id);
        if (back) this.#setBack(ref, back);
        else console.warn(`No card back ${id} for ${ref.type}/${ref.key}`);
      }
    }
    for (const [parent, groups] of this.children) {
      const child = groups.find(({rel}) => rel.back === 'children')?.refs.find(ref => this.back.has(ref));
      if (child && !this.back.has(parent)) this.#setBack(parent, this.back.get(child).ref, child);
    }
  }

  #setBack(ref, back, via) {
    this.back.set(ref, {ref: back, via});
  }
}
