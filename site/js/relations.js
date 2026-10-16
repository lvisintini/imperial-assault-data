// How the data files relate. Mirrors docs/data-model.md; keep the two in sync (tests/test_site.py checks coverage).

// sources 1─* source-contents *─1 <any content type>, polymorphic through content_type + content_id.
export const JOIN = {parent: 'sources', via: 'source-contents', fk: 'source_id', type: 'content_type', id: 'content_id'};

// Child → parent foreign keys.
export const FKS = [
  {child: 'agenda-cards', field: 'agenda_id', parent: 'agenda-decks'},
  {child: 'hero-class-cards', field: 'hero_id', parent: 'heroes'},
  {child: 'imperial-class-cards', field: 'class_id', parent: 'imperial-classes'},
];

// card-backs point at a content type; when it has several backs, `variant` matches a different field per type.
// Types not listed here have a single back that covers every record. Child cards (FKS) take their parent's back.
const byName = ({record}, variant) => record.name === variant;
const bySourceName = (ref, variant, db) => db.sources(ref).some(source => source.record.name === variant);

export const CARD_BACK_MATCH = {
  'deployment-cards': ({record}, variant) => record.affiliation === variant,
  'heroes': byName,
  'imperial-classes': byName,
  'condition-cards': byName,
  'upgrade-cards': ({record}, variant) => `Tier ${record.tier}` === variant,
  'story-mission-cards': bySourceName,
  'threat-mission-cards': bySourceName,
};
