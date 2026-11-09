// Boxes over a map image's tiles (views.js mapFrame), from map-layouts placements: a box per placement, its tile
// side's grid turned, positioned in percent of the image so it follows the image's size on screen. A map's small images
// (the ones the site has) are 64 px per square, framed on their tiles' squares plus 16 px all round, so square (x, y)
// starts at 16 + (x - the image's smallest x) * 64 px. A side's grid is its small image's size in squares (64 px each,
// inside the 16 px tab margins): read from the image, since each side is stored with its number pill upright, which can
// turn it from the other side's.
const SQUARE = 64;
const MARGIN = 16;

const grids = new Map();  // side image URL → Promise of [width, height] in squares, or null

function gridOf(src) {
  if (!grids.has(src)) {
    grids.set(src, new Promise(resolve => {
      const image = new Image();
      image.onload = () => resolve([Math.floor(image.naturalWidth / SQUARE), Math.floor(image.naturalHeight / SQUARE)]);
      image.onerror = () => resolve(null);
      image.src = src;
    }));
  }
  return grids.get(src);
}

const percent = value => `${(value * 100).toFixed(4)}%`;

async function fill(frame) {
  const boxes = JSON.parse(frame.dataset.boxes);
  const sizes = await Promise.all(boxes.map(box => gridOf(box.src)));
  const placed = boxes.flatMap((box, i) => {
    if (!sizes[i]) return [];
    const [w, h] = sizes[i];
    const turned = box.rotation % 180 !== 0;
    return [{...box, w: turned ? h : w, h: turned ? w : h}];
  });
  if (!placed.length) return;
  const left = Math.min(...placed.map(b => b.x));
  const top = Math.min(...placed.map(b => b.y));
  const width = (Math.max(...placed.map(b => b.x + b.w)) - left) * SQUARE + 2 * MARGIN;
  const height = (Math.max(...placed.map(b => b.y + b.h)) - top) * SQUARE + 2 * MARGIN;
  // Later sections on top (as drawn); within one, smaller tiles over larger ones, whose boxes cover their notches.
  placed.sort((a, b) => a.layer - b.layer || b.w * b.h - a.w * a.h);
  frame.querySelector('.tile-boxes').replaceChildren(...placed.map(b => {
    const box = document.createElement('span');
    box.className = 'tile-box';
    box.title = b.title;
    Object.assign(box.style, {
      left: percent((MARGIN + (b.x - left) * SQUARE) / width), top: percent((MARGIN + (b.y - top) * SQUARE) / height),
      width: percent(b.w * SQUARE / width), height: percent(b.h * SQUARE / height),
    });
    const label = document.createElement('span');
    label.className = 'tile-label';
    label.textContent = b.label;
    box.append(label);
    return box;
  }));
}

// After each render: fill the page's map images' boxes; "Show tile names" (data-show-tiles) names every tile at once.
export function initTileBoxes(root) {
  root.classList.remove('show-tiles');
  for (const frame of root.querySelectorAll('.map-frame[data-boxes]')) fill(frame);
}

export function initTileToggle(root) {
  root.addEventListener('change', event => {
    if (event.target.matches('[data-show-tiles]')) root.classList.toggle('show-tiles', event.target.checked);
  });
}
