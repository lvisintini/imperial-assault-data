# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A data-only dataset (no library/package) for FFG's *Star Wars: Imperial Assault*: JSON data files, JSON Schemas, and card images. Consumers use it as a git submodule or via release zips. Python exists only for tests, the release builder, the explorer's dev server, and an example. `site/` holds a static data explorer published to GitHub Pages.

## Layout

- `data/<content-type>.json` — one JSON array per content type. Structure mimics a relational DB:
  - `sources.json` = products (core game, expansions, ally/villain packs).
  - `source-contents.json` = join table `{source_id, content_type, content_id}` mapping products to their contents.
  - Child → parent FKs: `agenda-cards.agenda_id → agenda-decks`, `hero-class-cards.hero_id → heroes`, `imperial-class-cards.class_id → imperial-classes`, `campaign-hero-side-mission-cards.hero_id → heroes`, `missions.map_id → maps` (nullable), `mission-rewards.mission_id → missions`, and `sources.included_in → sources` (packs that ship inside the Core Set).
  - `missions.json` indexes every mission card (the five `campaign-*-mission-cards` files, `skirmish-mission-cards`, and `agenda-cards` with `mission: true`) through `content_type` + `content_id`. Missions reach products only through their index row (`source-contents` rows with `content_type: "missions"`); `mission-rewards.json` (no ids) lists each mission's rewards: a card through `content_type` + `content_id`, or `credits: true`; `choice: true` rows are pick-one alternatives.
  - `card-backs.json` is matched to cards by `content_type` (+ `variant`); its `id` isn't referenced yet (#52).
- `schemas/<content-type>.json` — Draft-04 JSON Schema per data file; shared enums (affiliations, traits, buff types, image path pattern) live in `schemas/definitions.json` and are pulled in via `$ref`. Schemas set `additionalProperties: false` and list all fields as `required` (nullable fields use `oneOf [..., null]`).
- `images/large/` and `images/small/` — mirror trees (`<content-type>/<slug>.png`); data `image`/`healthy`/`wounded` fields are paths relative to these roots. Do not open image files when evaluating data; they are ~500MB of binaries.
- `docs/data-model.md` — Mermaid ER diagrams of the relationships above, plus the card-back `variant` matching rules (which field `variant` matches per content type). Keep it in sync when relationships change.
- `site/` — the data explorer (https://lvisintini.github.io/imperial-assault-data/): static HTML/CSS/ES modules, no build, one pinned CDN library (Mermaid). It fetches `data/`, `images/` and `docs/` as siblings of itself, so it only runs as assembled by `pages.yml` or served by `serve_site.py`. `js/types.js` lists the content types, with each type's default sort (`sort`, used by `js/sort.js`), whether its tiles show the card back (`thumb`), and its list page's facets, default grouping and value order (`facets`, `groups`, `order`, used by `js/facets.js`, which derives filters and grouping from the data, and by sorting); `js/peek.js` shows a card's large image on hover; `js/relations.js` holds the relationship and card-back rules from `docs/data-model.md`; `tests/test_site.py` checks both against the data model and schemas.
- `tests/constants.py` — `CONTENT_TYPES` registry (`as_list`, `without_ids`) plus Python mirrors of the trait/type enums.
- `pyproject.toml` — holds the dataset `version` (`[project].version`, SemVer, see README; `build_release.py` reads it), the `dev` dependency group, and pytest config. Non-package uv project; `uv.lock` is committed.
- `.github/workflows/test.yml` — runs `uv run pytest` on push/PR against Python 3.12 and 3.14.
- `.github/workflows/pages.yml` — on master pushes touching `site/`, `data/`, `images/` or `docs/` (and `workflow_dispatch`): moves `site/` to `_site/`, moves `data/`, `images/` and `docs/` into it, and deploys with Pages' Actions deployment. Images are never committed twice.
- `.github/workflows/release.yml` — on a `v*.*.*` tag push: checks the tag equals `v` + `[project].version`, runs tests, runs `build_release.py`, and `gh release create`s with both zips (tags with a `-suffix` become pre-releases). `workflow_dispatch` is a dry run that uploads the zips as a workflow artifact instead.

## Invariants enforced by tests

- Every record validates against its schema (`tests/test_schemas.py`).
- Ids are UUIDs (`definitions.json#/definitions/uuid`), unique across the dataset; only `source-contents` and `mission-rewards` have none. 1.x records have uuid5 ids derived from their old numeric ids, and new records get a uuid4 (`docs/data-model.md` → Ids). Ids never change; files keep their order.
- `source-contents` FKs and the child→parent FKs above must resolve. Every mission card has exactly one `missions` row, no `source-contents` row points at a mission card directly, agenda missions' rows have their deck's products, skirmish missions have a map, a map used by a mission has no `source-contents` rows of its own (it's in its missions' products), and `mission-rewards` rows resolve (credits ⇔ no record; a `choice` group has ≥ 2 rows).
- Deployment rules: skirmish upgrades have no health/speed/group/reinforce cost and are Skirmish-only; unique ⇒ group 1, no reinforce cost; group > 1 ⇔ reinforce cost.
- `iaspec` values are unique across deployment, command and companion cards, and follow the rule in `TestCanonicalNames`: `elite` (elite, non-unique cards only) + name, adding mode, then affiliation, then description only while another card would get the same value.
- Images (`tests/test_images.py`): every referenced file exists in both `large` and `small`, every file on disk is referenced (no orphans), and pixel sizes match the table in README (`ImageTestHelper` holds the expected dims).

## Adding a new content type

Touch all of: `data/`, `schemas/`, `schemas/definitions.json` (`content_type` enum), `tests/constants.py` (`as_list`, maybe `without_ids`), `ImageTestHelper.definitions` (large + small, plus a card-back entry), the README image tables, `docs/data-model.md`, `site/js/types.js` and maybe `site/js/relations.js`, and the `SOURCES` list in `examples/show_source_contents.py`.

## Tools (sibling repo)

New content is added with `ia_tools` in [imperial-assault-tools](https://github.com/lvisintini/imperial-assault-tools), checked out next to this repo at `../imperial-assault-tools` (this project's `.claude/settings.local.json` adds it as a working directory). It finds this repo through `IA_DATA_ROOT` (default `../imperial-assault-data`). The workflow:

1. `uv run --project ../imperial-assault-tools ia scrape <boardwars album url>` stages the product in the tools repo's `staging/` (or `ia audit` to look for gaps across all of boardwars).
2. The user runs `ia enter` and goes through the cards in the browser. Card text and visual checks are theirs; never open image files, only inspect them programmatically (size, format, hash).
3. `ia import <product> --check`, then `ia import <product>`, writes records, `source-contents` rows and images here. Then run `uv run pytest`, and open a PR that names the tools commit used.

Images come from cards.boardwars.eu only, so the dataset stays consistent.

## Commands

```bash
uv sync                                     # create .venv with the dev group (Python >= 3.12)
uv run pytest                               # full suite (~8.4k parametrized tests, ~1 min)
uv run pytest tests/test_schemas.py         # single file
uv run pytest -k deployment                 # subset
uv run python build_release.py              # writes build/imperial-assault-data-v<version>-{high,low}-res.zip
git tag v<version> && git push origin v<version>   # after the version bump is merged: triggers the Release workflow
uv run python serve_site.py [port]          # data explorer on http://localhost:8000, laid out as deployed
uv run python examples/show_source_contents.py   # run from repo root (uses ./data relative paths)
```
