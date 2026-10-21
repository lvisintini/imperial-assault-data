import {CARD_BACK_MATCH, FKS, JOIN, MISSIONS, REQUIREMENTS, REWARDS} from './relations.js';
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
// source-contents and mission-rewards, which have no ids; index is its position in the file, used to keep a stable
// order. A missions row's ref also has `card`, the mission card it stands for.
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
    this.mission = new Map();   // mission card ref → its missions row
    this.rewards = new Map();   // mission card ref → [{ref (null for credits), credits, choice}]
    this.rewardOf = new Map();  // reward ref → mission card refs
    this.requires = new Map();  // ref → [{relation, ref: source ref}]
    this.requiredBy = new Map();  // source ref → [{relation, ref}]
    this.#linkSources();
    this.#linkMissions();
    this.#linkRequirements();
    this.#linkParents();
    this.#linkChildProducts();
    this.#linkBacks();
  }

  get(type, key) {
    return this.keyed[type]?.get(key);
  }

  // A mission card's products are its missions row's.
  sources(ref) {
    return this.foundIn.get(this.mission.get(ref) ?? ref) ?? [];
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

  #linkMissions() {
    for (const row of this.refs[MISSIONS.table]) {
      const card = this.get(row.record[MISSIONS.type], row.record[MISSIONS.id]);
      if (!card) {
        console.warn('Unresolved missions row', row.record);
        continue;
      }
      row.card = card;
      this.mission.set(card, row);
    }
    for (const {record} of this.refs[REWARDS.table]) {
      const card = this.get(MISSIONS.table, record[REWARDS.mission])?.card;
      const reward = record.credits ? null : this.get(record[REWARDS.type], record[REWARDS.id]);
      if (!card || (!record.credits && !reward)) {
        console.warn('Unresolved mission-rewards row', record);
        continue;
      }
      push(this.rewards, card, {ref: reward, credits: record.credits, choice: record.choice});
      if (reward) push(this.rewardOf, reward, card);
    }
  }

  #linkRequirements() {
    for (const {record} of this.refs[REQUIREMENTS.table]) {
      const ref = this.get(record[REQUIREMENTS.type], record[REQUIREMENTS.id]);
      const source = this.get(JOIN.parent, record[REQUIREMENTS.source]);
      if (!ref || !source) {
        console.warn('Unresolved requirements row', record);
        continue;
      }
      push(this.requires, ref, {relation: record.relation, ref: source});
      push(this.requiredBy, source, {relation: record.relation, ref});
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
      if (back && !this.back.has(child)) this.#setBack(child, back.ref, parent);
    }
  }

  #setBack(ref, back, via) {
    this.back.set(ref, {ref: back, via});
    push(this.backOf, back, ref);
  }
}
