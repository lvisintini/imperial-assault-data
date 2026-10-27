# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A data-only dataset (no library/package) for FFG's *Star Wars: Imperial Assault*: JSON data files, JSON Schemas, and card images. Consumers use it as a git submodule or via release zips. Python exists only for tests, the release builder, the explorer's dev server, and an example. `site/` holds a static data explorer published to GitHub Pages.

## Layout

- `data/<content-type>.json` — one JSON array per content type. Structure mimics a relational DB:
  - `sources.json` = products (core game, expansions, ally/villain packs).
  - `source-contents.json` = join table `{source_id, content_type, content_id, quantity}` mapping products to their contents, with how many copies each has (from the wiki's "(xN)" markers).
  - Child → parent FKs: `agenda-cards.agenda_id → agenda-decks`, `hero-class-cards.hero_id → heroes`, `imperial-class-cards.class_id → imperial-classes`, `campaign-hero-side-mission-cards.hero_id → heroes`, `missions.map_id → maps` (nullable), `mission-rewards.mission_id → missions` and `epilogue-cards.mission_id → missions`. A product that ships inside another (the Luke and Vader packs, in the Core Set) is a `source-contents` row with `content_type: "sources"`.
  - `miniatures.json`: every miniature sculpt (`affiliation`, `squares` = footprint, `description` only for a later sculpt of the same name, e.g. "Stormtroopers" / "2nd pose"; a file slug would combine them), in its products through `source-contents` with `quantity` = how many figures. No images.
  - `documents.json`: FFG's documents (`name`, `category`, `version`, `file` = a PDF in `documents/`, which is in the release zips but not on Pages; the explorer links to GitHub). A book in a product's box is a `source-contents` row; a document published for a product is a `document-for` link; organized-play documents belong to no product.
  - `record-links.json` (no ids): `{from_type, from_id, to_type, to_id, relation, reverse_relation}` between records of any types, readable from either end. The schema's `oneOf` ties each relation to its reverse and the types it links: `figure-of`/`has-figure` (a miniature → the deployment cards and hero it stands for), `form-of`/`has-form` (a form card → both Clawdite Shapeshifter cards), `elite-of`/`regular-of` (an elite deployment card → its regular one), `campaign-of`/`skirmish-of` (a Campaign-only deployment card → its Skirmish-only twin), `document-for`/`has-document` (a document → a source), `requires`/`required-by` and `expands`/`expanded-by` (any record → a source).
  - `missions.json` indexes every mission card (the five `campaign-*-mission-cards` files, `skirmish-mission-cards`, `raid-missions`, and `agenda-cards` with `mission: true`) through `content_type` + `content_id`. Missions reach products only through their index row (`source-contents` rows with `content_type: "missions"`); `mission-rewards.json` (no ids) lists each mission's rewards: a card through `content_type` + `content_id`, or `credits: true`; `choice: true` rows are pick-one alternatives.
  - `card-backs.json` is a catalog of backs (`name`, `image`); every card points at its back through `back_id`. Heroes, Imperial classes and agenda decks have none: their backs are on their cards' `back_id`.
- `schemas/<content-type>.json` — Draft-04 JSON Schema per data file; shared enums (affiliations, traits, buff types, image path pattern) live in `schemas/definitions.json` and are pulled in via `$ref`. Schemas set `additionalProperties: false` and list all fields as `required` (nullable fields use `oneOf [..., null]`).
- `images/large/` and `images/small/` — mirror trees (`<content-type>/<slug>.png`); data `image`/`healthy`/`wounded` fields are paths relative to these roots. Do not open image files when evaluating data; they are ~500MB of binaries.
- `docs/data-model.md` — Mermaid ER diagrams of the relationships above, and how card backs, missions and epilogues work. Keep it in sync when relationships change.
- `site/` — the data explorer (https://lvisintini.github.io/imperial-assault-data/): static HTML/CSS/ES modules, no build, one pinned CDN library (Mermaid). It fetches `data/`, `images/` and `docs/` as siblings of itself, so it only runs as assembled by `pages.yml` or served by `serve_site.py`. `js/types.js` lists the content types, with each type's default sort (`sort`, used by `js/sort.js`), whether its tiles show the card back (`thumb`), and its list page's facets, default grouping and value order (`facets`, `groups`, `order`, used by `js/facets.js`, which derives filters and grouping from the data, and by sorting); `js/peek.js` shows a card's large image on hover; `js/relations.js` holds the relationships from `docs/data-model.md` (including `BACK`, the `back_id` link, and which parents show their cards' back); `tests/test_site.py` checks both against the data model and schemas.
- `tests/constants.py` — `CONTENT_TYPES` registry (`as_list`, `without_ids`) plus Python mirrors of the trait/type enums.
- `pyproject.toml` — holds the dataset `version` (`[project].version`, SemVer, see README; `build_release.py` reads it), the `dev` dependency group, and pytest config. Non-package uv project; `uv.lock` is committed.
- `.github/workflows/test.yml` — runs `uv run pytest` on push/PR against Python 3.12 and 3.14.
- `.github/workflows/pages.yml` — on master pushes touching `site/`, `data/`, `images/` or `docs/` (and `workflow_dispatch`): moves `site/` to `_site/`, moves `data/`, `images/` and `docs/` into it, drops `images/large/maps` (a map's small image is the same file, and the explorer reads maps from `small`), and deploys with Pages' Actions deployment. Images are never committed twice.
- `.github/workflows/release.yml` — on a `v*.*.*` tag push: checks the tag equals `v` + `[project].version`, runs tests, runs `build_release.py`, and `gh release create`s with both zips (tags with a `-suffix` become pre-releases). `workflow_dispatch` is a dry run that uploads the zips as a workflow artifact instead.

## Invariants enforced by tests

- Every record validates against its schema (`tests/test_schemas.py`).
- Ids are UUIDs (`definitions.json#/definitions/uuid`), unique across the dataset; only `source-contents`, `mission-rewards` and `record-links` have none. 1.x records have uuid5 ids derived from their old numeric ids, and new records get a uuid4 (`docs/data-model.md` → Ids). Ids never change; files keep their order.
- `source-contents` FKs and the child→parent FKs above must resolve. The Core Set's copies per content type match FFG's component list (`CORE_SET_COPIES`). Every mission card has exactly one `missions` row, no `source-contents` row points at a mission card directly, agenda missions' rows have their deck's products, skirmish and raid missions have a map, a map used by a mission has no `source-contents` rows of its own (it's in its missions' products), and `mission-rewards` rows resolve (credits ⇔ no record; a `choice` group has ≥ 2 rows).
- Every document's PDF is in `documents/` and every PDF there is a document's.
- Record links resolve and don't repeat (the schema checks relation pairs and types); every hero and every deployment card but skirmish upgrades has a miniature, and every miniature is `figure-of` something and in a product. Form cards are `form-of` the deployment cards their images are named after; `elite-of` and `campaign-of` links are exactly the pairs their rules give (same name, description and affiliation; an elite and a regular card with overlapping modes, or a Campaign-only and a Skirmish-only card with the same `elite`), and every Campaign-only card has its twin.
- Card backs: every card's `back_id` resolves, every back is used by cards of one size, back names are unique, a hero's, Imperial class's or agenda deck's cards share one back, and every type with images has `back_id` except `sources`, `maps` and `heroes` (`tests/test_integrity.py` `TestCardBacksIntegrity`).
- Reward cards: a Boon is for the Rebel players and a Bane for the Imperial player; agenda missions' reward cards are for the Imperial player.
- Deployment rules: skirmish upgrades have no health/speed/group/reinforce cost and are Skirmish-only; unique ⇒ group 1, no reinforce cost; group > 1 ⇔ reinforce cost.
- `iaspec` values are unique across deployment, command and companion cards, every IA Skirmish Specification key (`tests/fixtures/iaspec-spec.json`) is one of them, and they follow the rule in `TestCanonicalNames` (`docs/data-model.md`): name, with `elite` only when a regular card of the same name exists; then, only while another card would get the same value, `campaign` (a Campaign-only card; its Skirmish twin keeps the bare value), then affiliation, then description; six spec spellings (`SPEC_SPELLINGS`) are kept as they are.
- No deployment, command, companion or form card has Elite, Regular, Skirmish or Campaign in its name or description.
- Images (`tests/test_images.py`): every referenced file exists in both `large` and `small`, every file on disk is referenced (no orphans), and pixel sizes match the table in README (`ImageTestHelper` holds the expected dims).

## Adding a new content type

Touch all of: `data/`, `schemas/`, `schemas/definitions.json` (`content_type` enum), `tests/constants.py` (`as_list`, maybe `without_ids`), `ImageTestHelper.definitions` (large + small; a card type also needs `back_id`, and its backs are sized from it), the README image tables, `docs/data-model.md`, `site/js/types.js` and maybe `site/js/relations.js`, and the `SOURCES` list in `examples/show_source_contents.py`.

## Tools (sibling repo)

New content is added with `ia_tools` in [imperial-assault-tools](https://github.com/lvisintini/imperial-assault-tools), checked out next to this repo at `../imperial-assault-tools` (this project's `.claude/settings.local.json` adds it as a working directory). It finds this repo through `IA_DATA_ROOT` (default `../imperial-assault-data`). The workflow:

1. `uv run --project ../imperial-assault-tools ia scrape <boardwars album url>` stages the product in the tools repo's `staging/` (or `ia audit` to look for gaps across all of boardwars). For images boardwars doesn't have, `ia stage <slug> --type <content type> [files] [--tts <save>]` stages files or a Tabletop Simulator save the same way.
2. The user runs `ia enter` and goes through the cards in the browser. Card text and visual checks are theirs; never open image files, only inspect them programmatically (size, format, hash).
3. `ia import <product> --check`, then `ia import <product>`, writes records, `source-contents` rows and images here. Then run `uv run pytest`, and open a PR that names the tools commit used.

Images come from cards.boardwars.eu, so the dataset stays consistent. The exceptions, for content boardwars lacks, are listed in `docs/data-model.md`: skirmish mission cards (the wiki), maps (the Skirmish Map Project), epilogue cards (a Tabletop Simulator save), and the Heroic and Legendary reward cards and the skirmish mission back (the maintainer's scans).

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
