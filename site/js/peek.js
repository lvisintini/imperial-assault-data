// A larger view of a card while the pointer rests on its tile, or while keyboard focus is on it. Only where there's a
// real hover (a mouse or trackpad): on touch screens tapping a tile opens its page, as before.
const DELAY = 300;  // ms of hovering before the peek shows, so sweeping across the grid doesn't flash it
const GAP = 12;     // px between the tile and the peek, and the peek and the viewport's edges

const clamp = (value, low, high) => Math.max(low, Math.min(value, Math.max(low, high)));

export function initPeek(root, media = matchMedia('(hover: hover) and (pointer: fine)')) {
  if (!media.matches) return null;
  const panel = document.createElement('div');
  panel.className = 'peek';
  panel.setAttribute('aria-hidden', 'true');  // the tile's link is what assistive technology reads
  panel.hidden = true;
  const image = document.createElement('img');
  image.alt = '';
  panel.append(image);
  document.body.append(panel);

  let timer = null, pending = null, shown = null, keyboard = false;

  const place = () => {
    if (!shown) return;
    const tile = shown.getBoundingClientRect();
    const {offsetWidth: width, offsetHeight: height} = panel;
    let left = tile.right + GAP;
    if (left + width > innerWidth - GAP) left = tile.left - GAP - width;  // no room on the right: the left side
    panel.style.left = `${clamp(left, GAP, innerWidth - width - GAP)}px`;
    panel.style.top = `${clamp(tile.top + tile.height / 2 - height / 2, GAP, innerHeight - height - GAP)}px`;
  };
  image.addEventListener('load', place);

  const show = tile => {
    clearTimeout(timer);
    pending = null;
    shown = tile;
    const src = new URL(tile.dataset.peek, location.href).href;
    if (image.src !== src) image.src = src;
    panel.hidden = false;
    place();
  };
  const hide = () => {
    clearTimeout(timer);
    pending = shown = null;
    panel.hidden = true;
  };
  const tileOf = target => target instanceof Element ? target.closest('.tile[data-peek]') : null;

  root.addEventListener('pointerover', event => {
    const tile = tileOf(event.target);
    if (!tile || tile === pending || tile === shown) return;
    hide();
    pending = tile;
    timer = setTimeout(() => show(tile), DELAY);
  });
  root.addEventListener('pointerout', event => {
    const tile = tileOf(event.target);
    if (tile && !tile.contains(event.relatedTarget)) hide();
  });
  // Keyboard focus peeks straight away; focus that follows a click doesn't.
  addEventListener('keydown', event => {
    keyboard = true;
    if (event.key === 'Escape') hide();
  });
  addEventListener('pointerdown', () => { keyboard = false; });
  root.addEventListener('focusin', event => {
    const tile = tileOf(event.target);
    if (tile && keyboard) show(tile);
  });
  root.addEventListener('focusout', hide);
  addEventListener('scroll', hide, {passive: true});
  addEventListener('hashchange', hide);
  return {panel, show, hide};
}
