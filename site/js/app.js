import {load} from './data.js';
import {initPeek} from './peek.js';
import {initTileBoxes, initTileToggle} from './tiles.js';
import {html} from './html.js';
import {MENU, TYPE} from './types.js';
import {UNDER} from './relations.js';
import * as views from './views.js';

const app = document.getElementById('app');
const searchForm = document.getElementById('search');
const searchInput = searchForm.elements.q;

function parse(hash) {
  const [path, query = ''] = hash.replace(/^#\/?/, '').split('?');
  return {parts: path.split('/').filter(Boolean).map(decodeURIComponent), params: new URLSearchParams(query)};
}

function resolve(db) {
  const {parts: [type, key, ...rest], params} = parse(location.hash);
  const q = params.get('q') ?? '';
  if (!type) return views.landing(db);
  if (type === 'search' && key === undefined) return views.search(db, q);
  // The mission collections' old addresses: a list is the missions page of that kind, a card its mission's page.
  if (TYPE[type]?.page === 'missions' && !rest.length) {
    const target = key === undefined ? `#/missions?f.content_type=${type}` : views.href(db.get(type, key) ?? {});
    if (target.startsWith('#/missions')) {
      history.replaceState(null, '', target);
      return resolve(db);
    }
  }
  if (!TYPE[type] || TYPE[type].hidden) return views.notFound();
  if (key === undefined) return TYPE[type].list === false ? views.notFound() : views.index(db, type, params);
  let ref = db.get(type, key);
  // A child under its parent (relations.js FKS `nested`): #/agenda-decks/<deck id>/agenda-cards/<card id>, the
  // address of a deck page's cards, whose crumbs are the deck's; or under a record it's linked to (UNDER): a form card
  // under a deployment card it's a form of.
  let under = null;
  if (rest.length) {
    const [childType, childKey, ...more] = rest;
    const child = db.get(childType, childKey);
    const parent = child && db.parent.get(child);
    const nested = parent?.rel.nested && parent.ref === ref;
    const linked = child && UNDER[childType] && ref
      && (db.links.get(child) ?? []).some(link => link.relation === UNDER[childType] && link.ref === ref);
    if (more.length || !ref || !(nested || linked)) return views.notFound();
    [under, ref] = [ref, child];
  }
  if (!ref) return views.notFound();
  // A form card's own address goes under its deployment card.
  if (ref.under && !under) {
    history.replaceState(null, '', views.href(ref));
    return resolve(db);
  }
  // A mission's page: through the missions page, or for an agenda mission as an agenda card (the crumbs show which).
  if (ref.type === 'missions' || ref.row) return views.mission(db, ref.row ?? ref, ref.type, under);
  return views.detail(db, ref, under);
}

function render(db) {
  const view = resolve(db);
  app.innerHTML = String(view.body);
  initTileBoxes(app);
  document.title = view.title ? `${view.title} · Imperial Assault Data` : 'Imperial Assault Data';
  const {parts: [route], params} = parse(location.hash);
  searchInput.value = route === 'search' ? params.get('q') ?? '' : '';
  // A page can be under another type's in the navigation (an epilogue under Missions).
  const current = view.nav ?? route;
  for (const link of nav.querySelectorAll('a')) {
    if (link.getAttribute('href') === `#/${current}`) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  }
  // A submenu's page marks its menu too.
  for (const item of nav.querySelectorAll('.nav-item')) {
    item.classList.toggle('current', Boolean(item.querySelector('[aria-current="page"]')));
  }
  closeMenus();
  view.mount?.(app);
  window.scrollTo(0, 0);
}

searchForm.addEventListener('submit', event => {
  event.preventDefault();
  location.hash = `#/search?q=${encodeURIComponent(searchInput.value.trim())}`;
});

// The navigation: a link per top-level type; one with a submenu also has a button that opens and closes it (hovering
// the item opens it too, on devices that can hover).
const nav = document.getElementById('nav');
nav.innerHTML = String(html`${MENU.map(({type, children}) => html`<div class="nav-item">
  <a class="nav-link" href="#/${type.file}">${type.label}</a>${children.length ? html`<button type="button"
    class="nav-more" aria-expanded="false" aria-controls="menu-${type.file}" aria-label="More under ${type.label}">
    <span aria-hidden="true">▾</span></button>
  <div class="submenu" id="menu-${type.file}">${children.map(c => html`<a href="#/${c.file}">${c.label}</a>`)}</div>`
    : ''}
</div>`)}`);

function closeMenus(except = null) {
  for (const item of nav.querySelectorAll('.nav-item.open')) {
    if (item === except) continue;
    item.classList.remove('open');
    item.querySelector('.nav-more').setAttribute('aria-expanded', 'false');
  }
}

// A submenu that would run off the right edge of the page opens leftwards.
function place(item) {
  const menu = item.querySelector('.submenu');
  if (!menu) return;
  item.classList.remove('flip');
  const width = menu.offsetWidth || 200;  // 200: its min-width, while it isn't shown yet
  item.classList.toggle('flip', item.getBoundingClientRect().left + width > document.documentElement.clientWidth);
}

nav.addEventListener('click', event => {
  const button = event.target.closest('.nav-more');
  if (!button) return;
  const item = button.closest('.nav-item');
  const open = !item.classList.contains('open');
  closeMenus(item);
  item.classList.toggle('open', open);
  button.setAttribute('aria-expanded', String(open));
  if (open) place(item);
});
nav.addEventListener('mouseover', event => {
  const item = event.target.closest('.nav-item');
  if (item) place(item);
});
document.addEventListener('click', event => {
  if (!nav.contains(event.target)) closeMenus();
});
document.addEventListener('keydown', event => {
  if (event.key !== 'Escape' || !nav.querySelector('.nav-item.open')) return;
  const open = nav.querySelector('.nav-item.open .nav-more');
  closeMenus();
  open.focus();
});

try {
  const db = await load();
  initPeek(app);
  initTileToggle(app);
  window.addEventListener('hashchange', () => render(db));
  render(db);
} catch (error) {
  console.error(error);
  app.innerHTML = `<h1>Couldn't load the data</h1><p class="status"></p>`;
  app.querySelector('.status').textContent = `${error.message}. Running locally? Serve it with "uv run python serve_site.py".`;
}
