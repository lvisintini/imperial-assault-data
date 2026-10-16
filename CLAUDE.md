# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A data-only dataset (no library/package) for FFG's *Star Wars: Imperial Assault*: JSON data files, JSON Schemas, and card images. Consumers use it as a git submodule or via release zips. Python exists only for tests, the release builder, and an example.

## Layout

- `data/<content-type>.json` — one JSON array per content type. Structure mimics a relational DB:
  - `sources.json` = products (core game, expansions, ally/villain packs).
  - `source-contents.json` = join table `{source_id, content_type, content_id}` mapping products to their contents.
  - Child → parent FKs: `agenda-cards.agenda_id → agenda-decks`, `hero-class-cards.hero_id → heroes`, `imperial-class-cards.class_id → imperial-classes`.
  - `card-backs.json` keys on `content_type` (+ `variant`), not an id.
- `schemas/<content-type>.json` — Draft-04 JSON Schema per data file; shared enums (affiliations, traits, buff types, image path pattern) live in `schemas/definitions.json` and are pulled in via `$ref`. Schemas set `additionalProperties: false` and list all fields as `required` (nullable fields use `oneOf [..., null]`).
- `images/large/` and `images/small/` — mirror trees (`<content-type>/<slug>.png`); data `image`/`healthy`/`wounded` fields are paths relative to these roots. Do not open image files when evaluating data; they are ~500MB of binaries.
- `docs/data-model.md` — Mermaid ER diagrams of the relationships above, plus the card-back `variant` matching rules (which field `variant` matches per content type). Keep it in sync when relationships change.
- `tests/constants.py` — `CONTENT_TYPES` registry (`as_list`, `without_ids`) plus Python mirrors of the trait/type enums.
- `pyproject.toml` — holds the dataset `version` (`[project].version`, SemVer, see README; `build_release.py` reads it), the `dev` dependency group, and pytest config. Non-package uv project; `uv.lock` is committed.
- `.github/workflows/test.yml` — runs `uv run pytest` on push/PR against Python 3.12 and 3.14.
- `.github/workflows/pages.yml` — deploys the data explorer (https://lvisintini.github.io/imperial-assault-data/) on master pushes touching `data/`, `images/` or `docs/`, and on `workflow_dispatch`. It checks out the orphan `gh-pages` branch (site source only: static HTML/CSS/ES modules, no build) and moves master's `data/`, `images/` and `docs/` into it before deploying, so images are never committed twice. Pushes to `gh-pages` start it through `gh-pages`' own `trigger.yml`, because the `github-pages` environment only accepts deployments from master. The site's relationship config (`js/relations.js` on gh-pages) mirrors `docs/data-model.md`.
- `.github/workflows/release.yml` — on a `v*.*.*` tag push: checks the tag equals `v` + `[project].version`, runs tests, runs `build_release.py`, and `gh release create`s with both zips (tags with a `-suffix` become pre-releases). `workflow_dispatch` is a dry run that uploads the zips as a workflow artifact instead.

## Invariants enforced by tests

- Every record validates against its schema (`tests/test_schemas.py`).
- Ids are exactly `0..len-1`, contiguous, with no duplicates (for types not in `CONTENT_TYPES.without_ids`). New records get the next id; never renumber.
- `source-contents` FKs and the child→parent FKs above must resolve.
- Deployment rules: skirmish upgrades have no health/speed/group/reinforce cost and are Skirmish-only; unique ⇒ group 1, no reinforce cost; group > 1 ⇔ reinforce cost.
- `iaspec` values are unique across deployment, command and companion cards.
- Images (`tests/test_images.py`): every referenced file exists in both `large` and `small`, every file on disk is referenced (no orphans), and pixel sizes match the table in README (`ImageTestHelper` holds the expected dims).

## Adding a new content type

Touch all of: `data/`, `schemas/`, `schemas/definitions.json` (`content_type` enum), `tests/constants.py` (`as_list`, maybe `without_ids`), `ImageTestHelper.definitions` (large + small, plus a card-back entry), the README image tables, `docs/data-model.md`, `js/types.js` and maybe `js/relations.js` on the `gh-pages` branch, and the `SOURCES` list in `examples/show_source_contents.py`.

## Commands

```bash
uv sync                                     # create .venv with the dev group (Python >= 3.12)
uv run pytest                               # full suite (~8.4k parametrized tests, ~1 min)
uv run pytest tests/test_schemas.py         # single file
uv run pytest -k deployment                 # subset
uv run python build_release.py              # writes build/imperial-assault-data-v<version>-{high,low}-res.zip
git tag v<version> && git push origin v<version>   # after the version bump is merged: triggers the Release workflow
uv run python examples/show_source_contents.py   # run from repo root (uses ./data relative paths)
```
