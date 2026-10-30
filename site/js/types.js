// One entry per data/<file>.json, in navigation order. `images` lists the record's image fields (paths relative to
// images/large and images/small); `hidden` keeps a type out of navigation and routing. `menu` puts a type in another
// type's submenu, in this order. `of` + `where` make a page that isn't a file: some of another type's records (agenda
// missions), shown and linked as that type's. `sort` is the default order (field names, '-' for descending; when
// missing, by product, the earliest release date and product code of the products a record comes in, then name).
// `thumb: 'back'` makes tiles show the record's card back instead of its own image, which the peek still shows;
// `icon` stands in for a missing image: 'pdf', or 'affiliation' (the record's affiliation's emblem).
// List pages filter and group by facets (facets.js), derived from the records' fields plus the products they come in
// ('source', 'wave'; a source is its own product). `facets` picks and orders them, and can add a trait as a yes/no
// facet with its own labels, or a field of the record's children (a map's missions' kinds); `groups` is the default grouping (facet ids); `order` fixes the order of a field's
// values, in facets, groups and sorting; `labels` renames a field's facet. A content_type field's values are shown as
// the types' labels.
export const TYPES = [
  {
    file: 'sources', label: 'Products', singular: 'Product', images: ['image'],
    sort: ['product_code'],
    facets: [
      'type', 'wave',
    ],
    order: {type: ['Core Game', 'Expansion', 'Ally Pack', 'Villain Pack', 'App', 'Skirmish Map Mat', 'Raid Map Mat']},
  },
  {file: 'heroes', label: 'Heroes', singular: 'Hero', images: ['healthy', 'wounded'], thumb: 'back'},
  {
    file: 'hero-class-cards', label: 'Hero class cards', singular: 'Hero class card', images: ['image'],
    menu: 'heroes',
  },
  {file: 'imperial-classes', label: 'Imperial classes', singular: 'Imperial class', images: []},
  {
    file: 'imperial-class-cards', label: 'Imperial class cards', singular: 'Imperial class card', images: ['image'],
    menu: 'imperial-classes',
  },
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
  {
    file: 'companion-cards', label: 'Companion cards', singular: 'Companion card', images: ['image'],
    menu: 'deployment-cards',
  },
  {file: 'form-cards', label: 'Form cards', singular: 'Form card', images: ['image'], menu: 'deployment-cards'},
  {file: 'command-cards', label: 'Command cards', singular: 'Command card', images: ['image']},
  {file: 'agenda-decks', label: 'Agenda decks', singular: 'Agenda deck', images: []},
  {file: 'agenda-cards', label: 'Agenda cards', singular: 'Agenda card', images: ['image'], menu: 'agenda-decks'},
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
      'skirmish-mission-cards', 'raid-missions',
    ]},
  },
  {
    file: 'campaign-story-mission-cards', label: 'Story missions', singular: 'Story mission', images: ['image'],
    menu: 'missions',
  },
  {
    file: 'campaign-threat-mission-cards', label: 'Threat missions', singular: 'Threat mission', images: ['image'],
    menu: 'missions',
  },
  {
    file: 'campaign-hero-side-mission-cards', label: 'Hero side missions', singular: 'Hero side mission',
    images: ['image'], menu: 'missions',
  },
  {
    file: 'campaign-ally-side-mission-cards', label: 'Ally side missions', singular: 'Ally side mission',
    images: ['image'], menu: 'missions',
  },
  {
    file: 'campaign-regular-side-mission-cards', label: 'Regular side missions', singular: 'Regular side mission',
    images: ['image'], menu: 'missions',
  },
  {
    file: 'agenda-missions', label: 'Agenda missions', singular: 'Agenda mission', images: ['image'],
    of: 'agenda-cards', where: record => record.mission, menu: 'missions',
    facets: [
      'agenda_id', 'influence', 'source', 'wave',
    ],
  },
  {
    file: 'skirmish-mission-cards', label: 'Skirmish missions', singular: 'Skirmish mission', images: ['image'],
    menu: 'missions',
    facets: [
      'format', 'scenario', 'source', 'wave',
    ],
    order: {format: ['Standard', 'Four Player Team Battle', 'Four Player Free-For-All']},
  },
  {file: 'raid-missions', label: 'Raid missions', singular: 'Raid mission', images: [], menu: 'missions'},
  {file: 'epilogue-cards', label: 'Epilogue cards', singular: 'Epilogue card', images: ['image'], menu: 'missions'},
  {
    file: 'documents', label: 'Documents', singular: 'Document', images: [], icon: 'pdf',
    facets: [
      'category', 'source', 'wave',
    ],
    groups: ['category'],
  },
  {
    file: 'miniatures', label: 'Miniatures', singular: 'Miniature', images: [], icon: 'affiliation',
    facets: [
      'affiliation', 'squares', 'source', 'wave',
    ],
    groups: ['affiliation'],
    order: {affiliation: ['Rebel', 'Imperial', 'Mercenary', 'Neutral']},
  },
  {
    file: 'reward-cards', label: 'Reward cards', singular: 'Reward card', images: ['image'],
    facets: [
      'for', 'class', 'type', 'traits', 'source', 'wave',
    ],
    groups: ['for'],
    order: {for: ['Rebel players', 'Imperial player'], class: ['Regular', 'Boon', 'Bane']},
  },
  {file: 'supply-cards', label: 'Supply cards', singular: 'Supply card', images: ['image']},
  {file: 'upgrade-cards', label: 'Upgrade cards', singular: 'Upgrade card', images: ['image']},
  {
    file: 'condition-cards', label: 'Condition cards', singular: 'Condition card', images: ['image'],
    menu: 'sources',
  },
  {
    file: 'maps', label: 'Maps', singular: 'Map', images: ['image'],
    facets: [
      {id: 'mission-type', label: 'Mission type', children: 'missions', field: 'content_type', none: 'No mission card'},
      'source', 'wave',
    ],
    groups: ['mission-type'],
  },
  {
    file: 'map-tiles', label: 'Map tiles', singular: 'Map tile', images: ['side_a', 'side_b'], menu: 'maps',
    sort: ['name'],
    facets: [
      'source', 'wave',
    ],
    groups: ['source'],
  },
  {file: 'card-backs', label: 'Card backs', singular: 'Card back', images: ['image'], menu: 'sources'},
  {file: 'source-contents', label: 'Source contents', singular: 'Source content', images: [], hidden: true},
  {file: 'mission-rewards', label: 'Mission rewards', singular: 'Mission reward', images: [], hidden: true},
  {file: 'record-links', label: 'Record links', singular: 'Record link', images: [], hidden: true},
  {file: 'map-layouts', label: 'Map layouts', singular: 'Map layout', images: [], hidden: true},
];

export const TYPE = Object.fromEntries(TYPES.map(t => [t.file, t]));

// The data file a page's records come from: its own, or the type it shows some of (`of`).
export const fileOf = type => TYPE[type].of ?? type;

// The navigation: each visible type that isn't in a submenu, with the types in its submenu.
export const MENU = TYPES.filter(t => !t.hidden && !t.menu)
  .map(t => ({type: t, children: TYPES.filter(c => !c.hidden && c.menu === t.file)}));

export function title(ref) {
  const {record} = ref;
  if (ref.card) return title(ref.card);  // a missions row is named by its mission card
  return record.name ?? '';
}

export function fieldLabel(field) {
  const words = field.replaceAll('_', ' ');
  return words[0].toUpperCase() + words.slice(1);
}
