// How the data files relate. Mirrors docs/data-model.md; keep the two in sync (tests/test_site.py checks coverage).

// sources 1─* source-contents *─1 <any content type>, polymorphic through content_type + content_id. The content can be
// a source: a product that ships inside another (the Luke Skywalker and Darth Vader packs, in the Core Set).
export const JOIN = {parent: 'sources', via: 'source-contents', fk: 'source_id', type: 'content_type', id: 'content_id'};

// missions indexes every mission, whichever collection its card is in: a row per card, through content_type +
// content_id. Missions reach their products through their row (source-contents points at it), and it holds their map.
export const MISSIONS = {table: 'missions', type: 'content_type', id: 'content_id'};

// requirements: a record of any type (content_type + content_id) that requires or expands a source (`relation`).
export const REQUIREMENTS = {table: 'requirements', type: 'content_type', id: 'content_id', source: 'source_id'};
// How each relation reads on the record's page, and on the source's.
export const RELATIONS = {
  requires: {label: 'Requires', reverse: 'Required by'},
  expands: {label: 'Expands', reverse: 'Expanded by'},
};

// mission-rewards: what a mission (its index row) gives, a record of any type through content_type + content_id, or
// credits (no record). Rows with `choice` are alternatives: the player picks one.
export const REWARDS = {table: 'mission-rewards', mission: 'mission_id', type: 'content_type', id: 'content_id'};

// Child → parent foreign keys. `label`/`childrenLabel` name the relation on the child's and the parent's pages, when
// the types' own labels don't read well (a hero side mission's "For hero"). `products: 'children'` gives the parent its
// children's products (a map is in the products its missions are in).
export const FKS = [
  {child: 'agenda-cards', field: 'agenda_id', parent: 'agenda-decks'},
  {child: 'hero-class-cards', field: 'hero_id', parent: 'heroes'},
  {child: 'imperial-class-cards', field: 'class_id', parent: 'imperial-classes'},
  {child: 'campaign-hero-side-mission-cards', field: 'hero_id', parent: 'heroes', label: 'For hero'},
  {child: 'missions', field: 'map_id', parent: 'maps', label: 'Map', products: 'children'},
  {child: 'epilogue-cards', field: 'mission_id', parent: 'missions', label: 'Mission', childrenLabel: 'Epilogues'},
];

// card-backs point at a content type; when it has several backs, `variant` matches a different field per type.
// Types not listed here have a single back that covers every record. Child cards (FKS) without backs of their own take
// their parent's.
const byName = ({record}, variant) => record.name === variant;
const bySourceName = (ref, variant, db) => db.sources(ref).some(source => source.record.name === variant);

export const CARD_BACK_MATCH = {
  'deployment-cards': ({record}, variant) => record.affiliation === variant,
  'heroes': byName,
  'imperial-classes': byName,
  'condition-cards': byName,
  'upgrade-cards': ({record}, variant) => `Tier ${record.tier}` === variant,
  'campaign-story-mission-cards': bySourceName,
  'campaign-threat-mission-cards': bySourceName,
  // An epilogue's back names the mission it ends.
  'epilogue-cards': (ref, variant, db) => db.parent.get(ref)?.ref.card?.record.name === variant,
};
