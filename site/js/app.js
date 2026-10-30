import {load} from './data.js';
import {initPeek} from './peek.js';
import {html} from './html.js';
import {MENU, TYPE} from './types.js';
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
  if (!TYPE[type] || TYPE[type].hidden || rest.length) return views.notFound();
  if (key === undefined) return views.index(db, type, params);
  const ref = db.get(type, key);
  return ref ? views.detail(db, ref) : views.notFound();
}

function render(db) {
  const view = resolve(db);
  app.innerHTML = String(view.body);
  document.title = view.title ? `${view.title} · Imperial Assault Data` : 'Imperial Assault Data';
  const {parts: [route], params} = parse(location.hash);
  searchInput.value = route === 'search' ? params.get('q') ?? '' : '';
  for (const link of nav.querySelectorAll('a')) {
    if (link.getAttribute('href') === `#/${route}`) link.setAttribute('aria-current', 'page');
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
  window.addEventListener('hashchange', () => render(db));
  render(db);
} catch (error) {
  console.error(error);
  app.innerHTML = `<h1>Couldn't load the data</h1><p class="status"></p>`;
  app.querySelector('.status').textContent = `${error.message}. Running locally? Serve it with "uv run python serve_site.py".`;
}
