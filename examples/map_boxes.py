"""Write a self-contained HTML page that draws a map as boxes, one per placed tile, from map-layouts.json.

    uv run python examples/map_boxes.py "Into a Corner"                 # writes build/Into a Corner.html
    uv run python examples/map_boxes.py "Moisture Farm" -o moisture.html

Run from the repo root (it reads ./data and the tiles' image sizes in ./images/small, 64 px per square). The page has the map's placements
in it, so it opens with a double click, no server needed.

Each box is a tile's grid: it starts at the placement's (x, y) square and is as many squares wide and tall as the
tile, turned by its rotation (a 90 or 270 degree turn swaps width and height). A tile's squares are its image's size
divided by 64, leaving out the 16 px tab margins: an image 64 * w + 32 px wide (tabs) or 64 * w px wide (none) is w
squares. The map's image and each hidden section have their own colour and can be shown or hidden.
"""
import argparse
import html
import json
import struct
from pathlib import Path

SQUARE = 64  # px per square in the tiles' small images


def load(name):
    return json.loads(Path('data', f'{name}.json').read_text(encoding='utf-8'))


def squares(path):
    """(width, height) in squares of a tile side's image, unturned: a PNG's size is in its IHDR chunk."""
    with open(Path('images', 'small', path), 'rb') as image:
        width, height = struct.unpack('>II', image.read(24)[16:24])
    return width // SQUARE, height // SQUARE


def boxes(record):
    """The map's placements as boxes: [{"tile", "side", "section", "x", "y", "w", "h", "rotation"}]."""
    tiles = {t['id']: t for t in load('map-tiles')}
    found = []
    for row in load('map-layouts'):
        if row['map_id'] != record['id']:
            continue
        tile = tiles[row['tile_id']]
        w, h = squares(tile['side_a' if row['side'] == 'A' else 'side_b'])
        for p in row['placements']:
            turned = p['rotation'] in (90, 270)
            found.append({'tile': tile['name'], 'side': row['side'], 'section': p['section'], 'x': p['x'], 'y': p['y'],
                          'w': h if turned else w, 'h': w if turned else h, 'rotation': p['rotation']})
    return found


PAGE = """<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  body {{ font: 14px system-ui, sans-serif; margin: 16px; background: #f4f4f4; color: #222; }}
  label {{ margin-right: 12px; }}
  .map {{ position: relative; margin-top: 12px; background: #fff; }}
  .box {{ position: absolute; box-sizing: border-box; border: 1px solid #333; font-size: 11px; line-height: 1.2;
          padding: 2px; overflow: hidden; opacity: .85; }}
  .box:hover {{ outline: 2px solid #000; z-index: 1; opacity: 1; }}
  .swatch {{ display: inline-block; width: 12px; height: 12px; vertical-align: middle; border: 1px solid #333; }}
</style>
<h1>{title}</h1>
<p>One box per placed tile, at its grid's top-left square, as many squares as the tile once turned
  (<code>map-layouts.json</code> placements). Hover a box for its tile, side, square and rotation.</p>
<div id="sections"></div>
<div class="map" id="map"></div>
<script>
const MAP = {data};
const PX = 28;  // screen px per square
const COLOURS = ['#9ecae1', '#fdae6b', '#a1d99b', '#bcbddc', '#fc9272', '#c7e9c0', '#fdd0a2', '#dadaeb'];
const sections = [null, ...MAP.hidden_sections];
const colour = s => COLOURS[sections.indexOf(s) % COLOURS.length];
const shown = new Set([null]);

function draw() {{
  const map = document.getElementById('map');
  map.replaceChildren();
  const boxes = MAP.boxes.filter(b => shown.has(b.section));
  map.style.width = `${{Math.max(0, ...MAP.boxes.map(b => b.x + b.w)) * PX}}px`;
  map.style.height = `${{Math.max(0, ...MAP.boxes.map(b => b.y + b.h)) * PX}}px`;
  for (const b of boxes) {{
    const box = document.createElement('div');
    box.className = 'box';
    Object.assign(box.style, {{left: `${{b.x * PX}}px`, top: `${{b.y * PX}}px`, width: `${{b.w * PX}}px`,
                              height: `${{b.h * PX}}px`, background: colour(b.section)}});
    box.textContent = `${{b.tile.replace('Core Set', 'Core')}} ${{b.side}}`;
    box.title = `${{b.tile}} ${{b.side}}${{b.section ? ` (${{b.section}})` : ''}}: square ${{b.x}}, ${{b.y}}, ` +
                `${{b.w}} x ${{b.h}} squares, turned ${{b.rotation}}° clockwise`;
    map.append(box);
  }}
}}

const choices = document.getElementById('sections');
for (const s of sections) {{
  const label = document.createElement('label');
  const box = document.createElement('input');
  box.type = 'checkbox';
  box.checked = shown.has(s);
  box.onchange = () => {{ box.checked ? shown.add(s) : shown.delete(s); draw(); }};
  const swatch = document.createElement('span');
  swatch.className = 'swatch';
  swatch.style.background = colour(s);
  label.append(box, ' ', swatch, ` ${{s ?? 'The map'}}`);
  choices.append(label);
}}
draw();
</script>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('map', help="the map's name, as in data/maps.json")
    parser.add_argument('-o', '--out', help='the HTML file to write (default: build/<map>.html)')
    args = parser.parse_args()

    maps = {m['name']: m for m in load('maps')}
    if args.map not in maps:
        raise SystemExit(f'No map named {args.map!r}')
    record = maps[args.map]
    data = {'name': record['name'], 'hidden_sections': [h['name'] for h in record['hidden_sections']],
            'boxes': boxes(record)}
    out = Path(args.out or Path('build', f'{args.map}.html'))
    out.parent.mkdir(parents=True, exist_ok=True)
    # Embedded in a <script>: escape "</" so a name can't end the script early.
    out.write_text(PAGE.format(title=html.escape(record['name']), data=json.dumps(data).replace('</', '<\\/')),
                   encoding='utf-8')
    print(f"{out}: {len(data['boxes'])} tiles"
          + (f", {len(data['hidden_sections'])} hidden sections" if data['hidden_sections'] else ''))


if __name__ == '__main__':
    main()
