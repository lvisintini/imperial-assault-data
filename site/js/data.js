import {CARD_BACK_MATCH, FKS, JOIN} from './relations.js';
import {TYPES} from './types.js';

export async function load() {
  const tables = await Promise.all(TYPES.map(async ({file}) => {
    const res = await fetch(`data/${file}.json`);
    if (!res.ok) throw new Error(`data/${file}.json: HTTP ${res.status}`);
    return [file, await res.json()];
  }));
  return new Db(Object.fromEntries(tables));
}

function push(map, key, value) {
  const list = map.get(key);
  if (list) list.push(value);
  else map.set(key, [value]);
}

// Records are wrapped in refs, {type, key, index, record}: key is the record's id (a UUID), or its array index in
// source-contents, which has no ids; index is its position in the file, used to keep a stable order.
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
    this.parent = new Map();    // child ref → {rel, ref}
    this.children = new Map();  // parent ref → [{rel, refs}]
    this.back = new Map();      // ref → {ref: card-back ref, via: parent ref when inherited}
    this.backOf = new Map();    // card-back ref → refs
    this.#linkSources();
    this.#linkParents();
    this.#linkBacks();
  }

  get(type, key) {
    return this.keyed[type]?.get(key);
  }

  sources(ref) {
    return this.foundIn.get(ref) ?? [];
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
    }
  }

  #linkParents() {
    for (const rel of FKS) {
      for (const child of this.refs[rel.child]) {
        const parent = this.get(rel.parent, child.record[rel.field]);
        if (!parent) continue;
        this.parent.set(child, {rel, ref: parent});
        const groups = this.children.get(parent) ?? [];
        if (!this.children.has(parent)) this.children.set(parent, groups);
        const group = groups.find(g => g.rel === rel);
        if (group) group.refs.push(child);
        else groups.push({rel, refs: [child]});
      }
    }
  }

  #linkBacks() {
    const backsByType = new Map();
    for (const back of this.refs['card-backs']) push(backsByType, back.record.content_type, back);

    for (const [type, backs] of backsByType) {
      const match = CARD_BACK_MATCH[type];
      if (!match && backs.length > 1) console.warn(`${type} has ${backs.length} card backs but no match rule`);
      for (const ref of this.refs[type]) {
        const back = match ? backs.find(b => match(ref, b.record.variant, this)) : backs[0];
        if (back) this.#setBack(ref, back);
        else console.warn(`No card back for ${type}/${ref.key}`);
      }
    }
    for (const [child, {ref: parent}] of this.parent) {
      const back = this.back.get(parent);
      if (back) this.#setBack(child, back.ref, parent);
    }
  }

  #setBack(ref, back, via) {
    this.back.set(ref, {ref: back, via});
    push(this.backOf, back, ref);
  }
}
