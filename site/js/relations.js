// How the data files relate. Mirrors docs/data-model.md; keep the two in sync (tests/test_site.py checks coverage).

// sources 1─* source-contents *─1 <any content type>, polymorphic through content_type + content_id, with how many
// copies the product has (quantity). The content can be a source: a product that ships inside another (the Luke
// Skywalker and Darth Vader packs, in the Core Set).
export const JOIN = {parent: 'sources', via: 'source-contents', fk: 'source_id', type: 'content_type', id: 'content_id',
  quantity: 'quantity'};

// missions indexes every mission, whichever collection its card is in: a row per card, through content_type +
// content_id. Missions reach their products through their row (source-contents points at it), and it holds their map.
export const MISSIONS = {table: 'missions', type: 'content_type', id: 'content_id'};

// record-links: a record of any type linked to another (from → to), with how the link reads from each end: `relation`
// on the from record's page, `reverse` (reverse_relation) on the to record's. LINK_RELATIONS names each one's section,
// in page order.
export const LINKS = {table: 'record-links', fromType: 'from_type', from: 'from_id', toType: 'to_type', to: 'to_id',
  relation: 'relation', reverse: 'reverse_relation'};
export const LINK_RELATIONS = {
  'figure-of': 'Figure of',
  'has-figure': 'Miniatures',
  'form-of': 'Form of',
  'has-form': 'Forms',
  'elite-of': 'Regular version',
  'regular-of': 'Elite version',
  'campaign-of': 'Skirmish version',
  'skirmish-of': 'Campaign version',
  'document-for': 'Document for',
  'has-document': 'Documents',
  'requires': 'Requires',
  'required-by': 'Required by',
  'expands': 'Expands',
  'expanded-by': 'Expanded by',
};

// mission-rewards: what a mission (its index row) gives, a record of any type through content_type + content_id, or
// credits (no record). Rows with `choice` are alternatives: the player picks one.
export const REWARDS = {table: 'mission-rewards', mission: 'mission_id', type: 'content_type', id: 'content_id'};

// Child → parent foreign keys. `label`/`childrenLabel` name the relation on the child's and the parent's pages, when
// the types' own labels don't read well (a hero side mission's "For hero"). `products: 'children'` gives the parent its
// children's products (a map is in the products its missions are in); `back: 'children'` gives it their card back.
export const FKS = [
  {child: 'agenda-cards', field: 'agenda_id', parent: 'agenda-decks', back: 'children'},
  {child: 'hero-class-cards', field: 'hero_id', parent: 'heroes', back: 'children'},
  {child: 'imperial-class-cards', field: 'class_id', parent: 'imperial-classes', back: 'children'},
  {child: 'campaign-hero-side-mission-cards', field: 'hero_id', parent: 'heroes', label: 'For hero'},
  {child: 'missions', field: 'map_id', parent: 'maps', label: 'Map', products: 'children'},
  {child: 'epilogue-cards', field: 'mission_id', parent: 'missions', label: 'Mission', childrenLabel: 'Epilogues'},
];

// Every card's back: back_id → card-backs, on each type whose records have the field. A parent whose FKS entry has
// `back: 'children'` has its cards' back (a hero's back is on its class cards).
export const BACK = {field: 'back_id', parent: 'card-backs'};
