// One entry per data/<file>.json, in navigation order. `images` lists the record's image fields (paths relative to
// images/large and images/small); `hidden` keeps a type out of navigation and routing. `sort` is the default order
// (field names, '-' for descending; name when missing). `thumb: 'back'` makes tiles show the record's card back
// instead of its own image, which the peek still shows.
// List pages filter and group by facets (facets.js), derived from the records' fields plus the products they come in
// ('source', 'wave'; a source is its own product). `facets` picks and orders them, and can add a trait as a yes/no
// facet with its own labels; `groups` is the default grouping (facet ids); `order` fixes the order of a field's
// values, in facets, groups and sorting; `labels` renames a field's facet. A content_type field's values are shown as
// the types' labels.
export const TYPES = [
  {
    file: 'sources', label: 'Sources', singular: 'Source', images: ['image'],
    sort: ['product_code'],
    facets: [
      'type', 'wave',
    ],
    order: {type: ['Core Game', 'Expansion', 'Ally Pack', 'Villain Pack', 'App']},
  },
  {file: 'heroes', label: 'Heroes', singular: 'Hero', images: ['healthy', 'wounded'], thumb: 'back'},
  {file: 'hero-class-cards', label: 'Hero class cards', singular: 'Hero class card', images: ['image']},
  {file: 'imperial-classes', label: 'Imperial classes', singular: 'Imperial class', images: []},
  {file: 'imperial-class-cards', label: 'Imperial class cards', singular: 'Imperial class card', images: ['image']},
  {
    file: 'deployment-cards', label: 'Deployment cards', singular: 'Deployment card', images: ['image'],
    sort: ['-unique', 'name', '-deployment_cost'],
    facets: [
      {id: 'skirmish-upgrade', label: 'Skirmish upgrade', trait: 'Skirmish Upgrade',
        no: 'Deployments', yes: 'Skirmish upgrades'},
      'affiliation', 'elite', 'unique', 'modes', 'traits', 'deployment_cost', 'reinforce_cost', 'health', 'speed',
      'deployment_group', 'source', 'wave',
    ],
    groups: ['skirmish-upgrade', 'affiliation'],
    order: {affiliation: ['Rebel', 'Imperial', 'Mercenary', 'Neutral']},
  },
  {file: 'command-cards', label: 'Command cards', singular: 'Command card', images: ['image']},
  {file: 'companion-cards', label: 'Companion cards', singular: 'Companion card', images: ['image']},
  {file: 'form-cards', label: 'Form cards', singular: 'Form card', images: ['image']},
  {file: 'agenda-decks', label: 'Agenda decks', singular: 'Agenda deck', images: []},
  {file: 'agenda-cards', label: 'Agenda cards', singular: 'Agenda card', images: ['image']},
  {
    file: 'missions', label: 'Missions', singular: 'Mission', images: [],
    sort: ['content_type'],
    facets: [
      'content_type', 'source', 'wave',
    ],
    groups: ['content_type'],
    labels: {content_type: 'Kind'},
    order: {content_type: [
      'campaign-story-mission-cards', 'campaign-threat-mission-cards', 'campaign-hero-side-mission-cards',
      'campaign-ally-side-mission-cards', 'campaign-regular-side-mission-cards', 'agenda-cards',
    ]},
  },
  {file: 'campaign-story-mission-cards', label: 'Story missions', singular: 'Story mission', images: ['image']},
  {file: 'campaign-threat-mission-cards', label: 'Threat missions', singular: 'Threat mission', images: ['image']},
  {
    file: 'campaign-hero-side-mission-cards', label: 'Hero side missions', singular: 'Hero side mission',
    images: ['image'],
  },
  {
    file: 'campaign-ally-side-mission-cards', label: 'Ally side missions', singular: 'Ally side mission',
    images: ['image'],
  },
  {
    file: 'campaign-regular-side-mission-cards', label: 'Regular side missions', singular: 'Regular side mission',
    images: ['image'],
  },
  {file: 'reward-cards', label: 'Reward cards', singular: 'Reward card', images: ['image']},
  {file: 'supply-cards', label: 'Supply cards', singular: 'Supply card', images: ['image']},
  {file: 'upgrade-cards', label: 'Upgrade cards', singular: 'Upgrade card', images: ['image']},
  {file: 'condition-cards', label: 'Condition cards', singular: 'Condition card', images: ['image']},
  {file: 'maps', label: 'Maps', singular: 'Map', images: ['image']},
  {file: 'card-backs', label: 'Card backs', singular: 'Card back', images: ['image'], sort: ['deck', 'variant']},
  {file: 'source-contents', label: 'Source contents', singular: 'Source content', images: [], hidden: true},
  {file: 'mission-rewards', label: 'Mission rewards', singular: 'Mission reward', images: [], hidden: true},
];

export const TYPE = Object.fromEntries(TYPES.map(t => [t.file, t]));

export function title(ref) {
  const {type, record} = ref;
  if (ref.card) return title(ref.card);  // a missions row is named by its mission card
  if (type === 'card-backs') return record.variant ? `${record.deck}: ${record.variant}` : record.deck;
  return record.name ?? '';
}

export function fieldLabel(field) {
  const words = field.replaceAll('_', ' ');
  return words[0].toUpperCase() + words.slice(1);
}
