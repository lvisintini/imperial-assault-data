// One entry per data/<file>.json, in navigation order. `images` lists the record's image fields (paths relative to
// images/large and images/small); `hidden` keeps a type out of navigation and routing. `sort` is the default order
// (field names, '-' for descending; name when missing).
// List pages filter and group by facets (facets.js), derived from the records' fields plus the products they come in
// ('source', 'wave'). `facets` picks and orders them, and can add a trait as a yes/no facet with its own labels;
// `groups` is the default grouping (facet ids); `order` fixes the order of a field's values.
export const TYPES = [
  {file: 'sources', label: 'Sources', singular: 'Source', images: ['image'], sort: ['product_code']},
  {file: 'heroes', label: 'Heroes', singular: 'Hero', images: ['healthy', 'wounded']},
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
  {file: 'story-mission-cards', label: 'Story missions', singular: 'Story mission', images: ['image']},
  {file: 'side-mission-cards', label: 'Side missions', singular: 'Side mission', images: ['image']},
  {file: 'threat-mission-cards', label: 'Threat missions', singular: 'Threat mission', images: ['image']},
  {file: 'reward-cards', label: 'Reward cards', singular: 'Reward card', images: ['image']},
  {file: 'supply-cards', label: 'Supply cards', singular: 'Supply card', images: ['image']},
  {file: 'upgrade-cards', label: 'Upgrade cards', singular: 'Upgrade card', images: ['image']},
  {file: 'condition-cards', label: 'Condition cards', singular: 'Condition card', images: ['image']},
  {file: 'skirmish-maps', label: 'Skirmish maps', singular: 'Skirmish map', images: ['image']},
  {file: 'card-backs', label: 'Card backs', singular: 'Card back', images: ['image'], sort: ['deck', 'variant']},
  {file: 'source-contents', label: 'Source contents', singular: 'Source content', images: [], hidden: true},
];

export const TYPE = Object.fromEntries(TYPES.map(t => [t.file, t]));

export function title({type, record}) {
  if (type === 'card-backs') return record.variant ? `${record.deck}: ${record.variant}` : record.deck;
  return record.name ?? '';
}

export function fieldLabel(field) {
  const words = field.replaceAll('_', ' ');
  return words[0].toUpperCase() + words.slice(1);
}
