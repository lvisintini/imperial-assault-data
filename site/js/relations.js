// How the data files relate. Mirrors docs/data-model.md; keep the two in sync (tests/test_site.py checks coverage).

// sources 1─* source-contents *─1 <any content type>, polymorphic through content_type + content_id.
export const JOIN = {parent: 'sources', via: 'source-contents', fk: 'source_id', type: 'content_type', id: 'content_id'};

// missions indexes every mission, whichever collection its card is in: a row per card, through content_type +
// content_id. Missions reach their products through their row (source-contents points at it), and it holds their map.
export const MISSIONS = {table: 'missions', type: 'content_type', id: 'content_id'};

// mission-rewards: what a mission (its index row) gives, a record of any type through content_type + content_id, or
// credits (no record). Rows with `choice` are alternatives: the player picks one.
export const REWARDS = {table: 'mission-rewards', mission: 'mission_id', type: 'content_type', id: 'content_id'};

// Child → parent foreign keys. `label`/`childrenLabel` name the relation on the child's and the parent's pages, when
// the types' own labels don't read well (a source "Included in" another). `products: 'children'` gives the parent its
// children's products (a map is in the products its missions are in).
export const FKS = [
  {child: 'agenda-cards', field: 'agenda_id', parent: 'agenda-decks'},
  {child: 'hero-class-cards', field: 'hero_id', parent: 'heroes'},
  {child: 'imperial-class-cards', field: 'class_id', parent: 'imperial-classes'},
  {child: 'sources', field: 'included_in', parent: 'sources', label: 'Included in', childrenLabel: 'Includes'},
  {child: 'campaign-hero-side-mission-cards', field: 'hero_id', parent: 'heroes', label: 'For hero'},
  {child: 'missions', field: 'map_id', parent: 'maps', label: 'Map', products: 'children'},
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
};
