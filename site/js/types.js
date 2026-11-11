// One entry per data/<file>.json, in navigation order. `images` lists the record's image fields (paths relative to
// images/large and images/small); `hidden` keeps a type out of navigation and routing; `page: 'missions'` sends its
// addresses to the missions page (the mission collections: a mission's page is its missions row's, views.js mission;
// maps: a map's is its first mission's, which shows it).
// `nav: false` keeps a type out of the navigation and the landing page, its pages still there (reached through other
// records'): a record's crumbs are its parent's list and page, then `crumb`: its name ("Missions › Executive
// Overreach › Epilogue: …"), and the navigation marks its parent's type. `list: false` leaves a type without a list
// page (form cards, companions and epilogue cards, reached through the cards they're forms of, what puts them into
// play, or their missions): out of the navigation and the landing page,
// its records' crumbs are its `menu`'s list, which the navigation marks. `menu` puts a type in another type's submenu,
// in this order. `of` + `where` make a page that isn't a file: some of another type's records, shown and linked as that
// type's (none today). `sort` is the default order (field names, '-' for descending; when
// missing, by product, the earliest release date and product code of the products a record comes in, then name;
// 'product' names that key, and a sort starting with '-product' also lists the type's products newest first, in the
// Product facet and its groups).
// `thumb: 'back'` makes tiles show the record's card back instead of its own image, which the peek still shows;
// `icon` stands in for a missing image: 'pdf', or 'affiliation' (the record's affiliation's emblem); on its tiles, and
// with `pageIcon: true` on its page too, where the image would be (a miniature's). `imageSections`
// lists fields holding [{name, image}] (a map's hidden sections); `pageImages` maps an image field to the heading of
// the section of its own it's shown in on its missions' pages (a map's whole-map image); both sections stay closed
// until opened by their heading.
// `columns` shows a child type's records under the fields table, beside the image, in a column per value of a field,
// labelled (`label` and the value, or `none` for none, first) and by the type's sort within (an Imperial class's
// cards by XP).
// `related` shows records in one Related row under the fields table, beside the image, each tile labelled: child types
// and record-link relations, each with its label (a hero's side mission, miniature, companion and Skirmish version).
// `sideBySide: true` puts each image in a column of its own beside the fields table (a tile's two sides; style.css
// moves the table under them, then everything into one column, as the screen narrows).
// `altThumb: {field, label}` adds a checkbox (`label`) to the list page that makes its tiles show the `field` image
// instead (a tile's side B), kept in the address as ?thumb=<field>.
// `pageBack: true` makes a record's page, when it has no images of its own, show its cards' back as its image (an
// Imperial class, an agenda deck). Card backs have no pages (`hidden`): each shows on its cards, which turn over to it.
// List pages filter and group by facets (facets.js), derived from the records' fields plus the products they come in
// ('source', 'wave', 'product_type': the products' types; a source is its own product; they come first, as Product,
// Product type, Wave). `facets` picks and orders them, and can add a trait as a yes/no
// facet with its own labels, or a field of the record's children (a map's missions' kinds); `groups` is the default grouping (facet ids); `order` fixes the order of a field's
// values, in facets, groups and sorting; `labels` renames a field's facet; `choices` lists number fields filtered by
// checkboxes, a value each, instead of a range (an upgrade card's tier). A content_type field's values are shown as
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
  {
    file: 'heroes', label: 'Heroes', singular: 'Hero', images: ['healthy', 'wounded'], thumb: 'back',
    related: {
      'campaign-hero-side-missions': 'Side mission', 'has-figure': 'Miniature', 'has-companion': 'Companion',
      'campaign-of': 'Skirmish version',
    },
  },
  {
    file: 'hero-class-cards', label: 'Hero class cards', singular: 'Hero class card', images: ['image'],
    menu: 'heroes', sort: ['hero', 'xp', 'name'],
  },
  {
    file: 'imperial-classes', label: 'Imperial classes', singular: 'Imperial class', images: [], pageBack: true,
    columns: {child: 'imperial-class-cards', field: 'xp', label: 'XP', none: 'No XP'},
  },
  {
    file: 'imperial-class-cards', label: 'Imperial class cards', singular: 'Imperial class card', images: ['image'],
    menu: 'imperial-classes', sort: ['class', 'xp', 'name'],
  },
  {
    file: 'deployment-cards', label: 'Deployment cards', singular: 'Deployment card', images: ['image'],
    sort: ['-unique', 'name', '-deployment_cost'],
    facets: [
      'source', 'product_type', 'wave',
      {id: 'skirmish-upgrade', label: 'Skirmish upgrade', trait: 'Skirmish Upgrade',
        no: 'Deployments', yes: 'Skirmish upgrades'},
      'affiliation', 'elite', 'unique', 'modes', 'traits', 'deployment_cost', 'reinforce_cost', 'health', 'speed',
      'deployment_group',
    ],
    groups: ['skirmish-upgrade', 'affiliation'],
    order: {affiliation: ['Rebel', 'Imperial', 'Mercenary', 'Neutral']},
  },
  {
    file: 'companion-cards', label: 'Companion cards', singular: 'Companion card', images: ['image'],
    menu: 'deployment-cards', list: false,
  },
  {
    file: 'form-cards', label: 'Form cards', singular: 'Form card', images: ['image'], menu: 'deployment-cards',
    list: false,
  },
  {
    file: 'command-cards', label: 'Command cards', singular: 'Command card', images: ['image'],
    sort: ['cost', 'limit'],
  },
  {file: 'agenda-decks', label: 'Agenda decks', singular: 'Agenda deck', images: [], pageBack: true},
  {
    file: 'agenda-cards', label: 'Agenda cards', singular: 'Agenda card', images: ['image'], menu: 'agenda-decks',
    sort: ['agenda', 'influence'],
  },
  {
    file: 'missions', label: 'Missions', singular: 'Mission', images: [],
    sort: ['content_type'],
    facets: [
      'source', 'product_type', 'wave',
      'content_type',
    ],
    groups: ['content_type'],
    labels: {content_type: 'Kind'},
    order: {content_type: [
      'campaign-story-missions', 'campaign-threat-missions', 'campaign-hero-side-missions',
      'campaign-ally-side-missions', 'campaign-regular-side-missions', 'agenda-cards',
      'skirmish-missions', 'raid-missions',
    ]},
  },
  // The mission collections: no pages of their own (`page: 'missions'`), their cards are shown on the missions page.
  {
    file: 'campaign-story-missions', label: 'Story missions', singular: 'Story mission', images: ['image'],
    hidden: true, page: 'missions',
  },
  {
    file: 'campaign-threat-missions', label: 'Threat missions', singular: 'Threat mission', images: ['image'],
    hidden: true, page: 'missions',
  },
  {
    file: 'campaign-hero-side-missions', label: 'Hero side missions', singular: 'Hero side mission',
    images: ['image'], hidden: true, page: 'missions',
  },
  {
    file: 'campaign-ally-side-missions', label: 'Ally side missions', singular: 'Ally side mission',
    images: ['image'], hidden: true, page: 'missions',
  },
  {
    file: 'campaign-regular-side-missions', label: 'Regular side missions', singular: 'Regular side mission',
    images: ['image'], hidden: true, page: 'missions',
  },
  {
    file: 'skirmish-missions', label: 'Skirmish missions', singular: 'Skirmish mission', images: ['image'],
    hidden: true, page: 'missions',
  },
  {
    file: 'raid-missions', label: 'Raid missions', singular: 'Raid mission', images: [], hidden: true,
    page: 'missions',
  },
  // Epilogues are reached through their missions' pages, under which their crumbs put them.
  {
    file: 'epilogue-cards', label: 'Epilogue cards', singular: 'Epilogue card', images: ['image'], nav: false,
    list: false, crumb: 'Epilogue',
  },
  {
    file: 'documents', label: 'Documents', singular: 'Document', images: [], icon: 'pdf',
    facets: [
      'source', 'product_type', 'wave',
      'category',
    ],
    groups: ['category'],
  },
  {
    file: 'miniatures', label: 'Miniatures', singular: 'Miniature', images: [], icon: 'affiliation', pageIcon: true,
    facets: [
      'source', 'product_type', 'wave',
      'affiliation', 'squares',
    ],
    groups: ['affiliation'],
    order: {affiliation: ['Rebel', 'Imperial', 'Mercenary', 'Neutral']},
  },
  {
    file: 'reward-cards', label: 'Reward cards', singular: 'Reward card', images: ['image'],
    facets: [
      'source', 'product_type', 'wave',
      'for', 'class', 'type', 'traits',
    ],
    groups: ['for'],
    order: {for: ['Rebel players', 'Imperial player'], class: ['Regular', 'Boon', 'Bane']},
  },
  {file: 'supply-cards', label: 'Supply cards', singular: 'Supply card', images: ['image']},
  {
    file: 'upgrade-cards', label: 'Upgrade cards', singular: 'Upgrade card', images: ['image'],
    sort: ['tier', 'credits'], choices: ['tier'],
  },
  {file: 'condition-cards', label: 'Condition cards', singular: 'Condition card', images: ['image']},
  {
    // Shown on their missions' pages, which their addresses go to.
    file: 'maps', label: 'Maps', singular: 'Map', images: ['image'], imageSections: ['hidden_sections'],
    pageImages: {whole_image: 'Whole map'}, hidden: true, page: 'missions',
  },
  {
    file: 'map-tiles', label: 'Map tiles', singular: 'Map tile', images: ['side_a', 'side_b'],
    sideBySide: true, altThumb: {field: 'side_b', label: 'Show B sides'},
    sort: ['product', 'number'],
    facets: [
      'source', 'product_type', 'wave',
      'squares', 'connections',
    ],
    groups: ['source'],
  },
  {file: 'card-backs', label: 'Card backs', singular: 'Card back', images: ['image'], hidden: true},
  {file: 'source-contents', label: 'Source contents', singular: 'Source content', images: [], hidden: true},
  {file: 'mission-rewards', label: 'Mission rewards', singular: 'Mission reward', images: [], hidden: true},
  {file: 'record-links', label: 'Record links', singular: 'Record link', images: [], hidden: true},
  {file: 'map-layouts', label: 'Map layouts', singular: 'Map layout', images: [], hidden: true},
  {file: 'map-tile-matches', label: 'Map tile matches', singular: 'Map tile match', images: [], hidden: true},
];

export const TYPE = Object.fromEntries(TYPES.map(t => [t.file, t]));

// The data file a page's records come from: its own, or the type it shows some of (`of`).
export const fileOf = type => TYPE[type].of ?? type;

// The navigation: each visible type that isn't in a submenu, with the types in its submenu.
export const inNav = t => !t.hidden && t.nav !== false && t.list !== false;
export const MENU = TYPES.filter(t => inNav(t) && !t.menu)
  .map(t => ({type: t, children: TYPES.filter(c => inNav(c) && c.menu === t.file)}));

// A mission's kind, named after its collection (a missions row's content_type); agenda cards are agenda missions.
export const kindLabel = (type, one = false) => type === 'agenda-cards'
  ? (one ? 'Agenda mission' : 'Agenda missions') : TYPE[type]?.[one ? 'singular' : 'label'] ?? type;

export function title(ref) {
  const {record} = ref;
  if (ref.card) return title(ref.card);  // a missions row is named by its mission card
  return record.name ?? '';
}

export function fieldLabel(field) {
  const words = field.replaceAll('_', ' ');
  return words[0].toUpperCase() + words.slice(1);
}
