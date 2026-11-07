"""Draw a map as a PNG from map-layouts.json's placements and the map tiles' images.

    uv run python examples/draw_map.py "Moisture Farm"                  # the map's image
    uv run python examples/draw_map.py "Into a Corner" --section Landing  # one hidden section's image
    uv run python examples/draw_map.py "Into a Corner" --whole            # the map and every hidden section
    uv run python examples/draw_map.py "Moisture Farm" -o moisture-farm.png

Run from the repo root (it reads ./data and ./images). Each placement is a tile side's image turned clockwise by
`rotation`, its grid's top-left square at (`x`, `y`). A side's image is 64 px per square plus a 16 px margin at each
end of an axis with connector tabs, so the image goes at x * 64 minus that margin (and the same for y). Drawn in the
file's order, then cropped to the tiles, this gives the map images in images/large/maps (up to the order in which
tiles whose tabs overlap are drawn).
"""
import argparse
import json
from pathlib import Path

from PIL import Image

SQUARE = 64  # px per square in the tiles' images


def load(name):
    return json.loads(Path('data', f'{name}.json').read_text(encoding='utf-8'))


def pieces(map_name, sections):
    """[(side image path, placement)] for the placements on these sections (None is the map's image), in the order the
    map's images are drawn in: the map's image, then its hidden sections in order."""
    maps = {m['name']: m for m in load('maps')}
    if map_name not in maps:
        raise SystemExit(f'No map named {map_name!r}')
    record = maps[map_name]
    order = [None] + [h['name'] for h in record['hidden_sections']]
    unknown = [s for s in sections if s not in order]
    if unknown:
        raise SystemExit(f'{map_name} has no hidden section {unknown[0]!r}; it has {order[1:] or "none"}')
    tiles = {t['id']: t for t in load('map-tiles')}
    found = []
    for row in load('map-layouts'):
        if row['map_id'] != record['id']:
            continue
        image = tiles[row['tile_id']]['side_a' if row['side'] == 'A' else 'side_b']
        found += [(image, p) for p in row['placements'] if p['section'] in sections]
    return sorted(found, key=lambda f: order.index(f[1]['section']))


def draw(found):
    """The tiles drawn on a transparent page, cropped to them."""
    layers = []
    for path, placement in found:
        # rotate() turns counter-clockwise: a negative angle turns clockwise. expand keeps the whole tile.
        image = Image.open(Path('images', 'large', path)).convert('RGBA').rotate(-placement['rotation'], expand=True)
        margin_x = (image.width - image.width // SQUARE * SQUARE) // 2
        margin_y = (image.height - image.height // SQUARE * SQUARE) // 2
        layers.append((image, placement['x'] * SQUARE - margin_x, placement['y'] * SQUARE - margin_y))
    left = min(x for _, x, _ in layers)
    top = min(y for _, _, y in layers)
    width = max(x + image.width for image, x, _ in layers) - left
    height = max(y + image.height for image, _, y in layers) - top
    page = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    for image, x, y in layers:
        layer = Image.new('RGBA', page.size, (0, 0, 0, 0))
        layer.paste(image, (x - left, y - top))
        page = Image.alpha_composite(page, layer)  # a tab drawn over its neighbour's notch blends into it
    return page.crop(page.getbbox())


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('map', help='the map\'s name, as in data/maps.json')
    which = parser.add_mutually_exclusive_group()
    which.add_argument('--section', help='one of the map\'s hidden sections, by name')
    which.add_argument('--whole', action='store_true', help='the map\'s image and every hidden section')
    parser.add_argument('-o', '--out', help='the PNG to write (default: build/<map>.png)')
    args = parser.parse_args()

    maps = {m['name']: m for m in load('maps')}
    hidden = [h['name'] for h in maps[args.map]['hidden_sections']] if args.map in maps else []
    sections = [args.section] if args.section else [None] + hidden if args.whole else [None]
    image = draw(pieces(args.map, sections))
    out = Path(args.out or Path('build', f"{args.map}{f' - {args.section}' if args.section else ''}"
                                         f"{' (whole)' if args.whole else ''}.png"))
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out)
    print(f'{out}: {image.width} x {image.height} px, {image.width / SQUARE:.1f} x {image.height / SQUARE:.1f} squares')


if __name__ == '__main__':
    main()
