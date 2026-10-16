import {load} from './data.js';
import {TYPE, TYPES} from './types.js';
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
  if (key === undefined) return views.index(db, type, q);
  const ref = /^\d+$/.test(key) ? db.get(type, Number(key)) : undefined;
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
  view.mount?.(app);
  window.scrollTo(0, 0);
}

searchForm.addEventListener('submit', event => {
  event.preventDefault();
  location.hash = `#/search?q=${encodeURIComponent(searchInput.value.trim())}`;
});

const nav = document.getElementById('nav');
nav.innerHTML = TYPES.filter(t => !t.hidden)
  .map(t => `<a href="#/${t.file}">${t.label}</a>`).join('');

try {
  const db = await load();
  window.addEventListener('hashchange', () => render(db));
  render(db);
} catch (error) {
  console.error(error);
  app.innerHTML = `<h1>Couldn't load the data</h1><p class="status"></p>`;
  app.querySelector('.status').textContent = `${error.message}. Running locally? Serve it with "uv run python serve_site.py".`;
}
