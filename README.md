# Imperial Assault Data

An easy-to-use collection of data and images from the [Imperial Assault](https://www.fantasyflightgames.com/en/products/star-wars-imperial-assault/) game by [Fantasy Flight Games](https://www.fantasyflightgames.com).

## What you can find inside

You can browse everything in the [data explorer](https://lvisintini.github.io/imperial-assault-data/): every record
with its images, metadata and links to the records it relates to.

In the `data` directory you will find all the data for the game in JSON formatted files.
The data structure loosely mimics that of a relational database.

For example, with the `.data/source-contents.json` file you can determine the contents of a particular product by filtering the entries by `source_id`.

The [data model](docs/data-model.md) page has an Entity-Relationship diagram of how the files relate. In short:

```
sources 1──* source-contents *──1 <any content type>   (content_type + content_id; quantity = copies)
agenda-decks     1──* agenda-cards          (agenda_id)
heroes           1──* hero-class-cards      (hero_id)
imperial-classes 1──* imperial-class-cards  (class_id)
card-backs       1──* <any card>            (back_id)
missions         1──1 <mission card>        (content_type + content_id; products and rewards attach here)
maps             1──* missions              (map_id; a map is in its missions' products)
maps             1──* map-layouts *──1 map-tiles   (map_id, tile_id; side and count; tiles are in products)
missions         1──* mission-rewards       (mission_id; content_type + content_id, or credits)
missions         1──* epilogue-cards        (mission_id)
sources          *──* miniatures            (source-contents; quantity = figures in the product)
record-links     <any record> ──relation──> <any record>   (from_type + from_id, to_type + to_id; relation and
                 reverse_relation: figure-of / has-figure, form-of / has-form, elite-of / regular-of,
                 campaign-of / skirmish-of, document-for / has-document, requires / required-by,
                 expands / expanded-by)
```

You can find an example on how to do this in the `./examples` folder, along with other examples.

Most entries have an associated image (or 2) that you can find inside the `./images/large` (for high resolution images) and the `./images/small` folder (for low resolution images).

FFG's documents for the game (rulebooks, campaign logs, the FAQ, player sheets, tournament documents, and scans of the packs' and expansions' rules sheets) are PDFs in `./documents`, listed in `data/documents.json`. Both release zips include them; the [data explorer](https://lvisintini.github.io/imperial-assault-data/) links to the copies here on GitHub.

The images rotated and aligned so that they are not askew, and they all have consistent sizes (check the [Image Sizes](#image-sizes) section for more on this).



## Usage

There are several ways you could include this in your project.

- Via [Git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules#Starting-with-Submodules):
```
git submodule add https://github.com/lvisintini/imperial-assault-data.git
```
- By downloading the release zip files. All releases for this project include 2 builds
    - one with the low-res images and,
    - one with the high-res images.

I do not know what would be the best way to distribute these assets, as they are meant to be cross platform.

I this regard, the project is open to suggestions


## Bugs / Issues / Suggestions

Please [open a ticket](https://github.com/lvisintini/imperial-assault-data/issues/new) on Github.

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :tada:

When adding images please use [TinyPNG](https://tinypng.com/) to reduce their file size as much as possible without affecting image quality.

If you want to contribute to the project and you know how to program in python, you may be interesting on setting up a development environment, although this is optional.

The project uses [uv](https://docs.astral.sh/uv/) and requires Python 3.12 or newer (uv will fetch one for you if needed).

```
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone git@github.com:lvisintini/imperial-assault-data.git
cd ./imperial-assault-data
uv sync

uv run pytest
```

The [data explorer](https://lvisintini.github.io/imperial-assault-data/) lives in `site/` (plain HTML, CSS and JavaScript, no build step).
Run `uv run python serve_site.py` to try it locally on http://localhost:8000. It's deployed automatically when `site/`,
`data/`, `images/` or `docs/` change on `master`.

## Testing

Each change in the dataset is checked against a multitude of test that are meant to preserve the integrity of the data.
This is done automatically for each code change on this repo.

Alternatively, you can also run the test suit yourself by setting up your environment and running `uv run pytest`


## Versioning

This project uses [SemVer](http://semver.org/). Given a `MAJOR.MINOR.PATCH` version number, we will increment the:
- `MAJOR` version when existing content is changed in such a way that it can break consumers of the data
- `MINOR` version when new content is added in a backwards-compatible manner, or existing content is changed in a backwards-compatible manner
- `PATCH` version when fixing mistakes in existing content

### Releasing

1. Bump `[project].version` in `pyproject.toml` (following the rules above) in a PR.
2. Once it is merged, tag that commit on `master` and push the tag: `git tag vX.Y.Z && git push origin vX.Y.Z`.
3. The [Release workflow](.github/workflows/release.yml) checks that the tag matches the version, runs the tests, builds the
   high-res and low-res zips, and publishes them as a GitHub Release with generated notes. A tag with a suffix
   (e.g. `v1.2.0-rc1`) is published as a pre-release. Edit the release notes on GitHub if needed.


## Contributors

The initial load of images and data was put together by scraping http://cards.boardwars.eu/, I do not know this guys
personally, but I'm grateful to them for putting together such a great source of data.


# Image sizes

What follows is a list of all the image types and their sizes for large and small.

|                        | Large     | Small   |
|------------------------|-----------|---------|
| **Source**             | 300x300   | 300x300 |
| **Standard**           | 476x740   | 301x470 |
| **Standard (Flipped)** | 740x476   | 470x301 |
| **Mini**               | 424x657   | 293x454 |
| **Mini (Flipped)**     | 657x424   | 454x293 |
| **Hero Sheet**         | 1490x1186 | 650x515 |

The table bellow shows you the expected sizes for all the different images included in this data set. A card back (`card-backs.image`) has the size of the cards whose `back_id` it is. A map (`Any`) keeps its own size, and its small image is the same file as its large one. A map tile's side (`Tile`) is cut on its outline: 64 px per square, plus 32 px on each axis that has connector tabs, and its small image is the same file as its large one.

|                                                       | Source  | Standard | Standard (Flipped) | Mini    | Mini (Flipped) | Hero Sheet | Any | Tile |
|-------------------------------------------------------|---------|----------|--------------------|---------|----------------|------------|-----|------|
| sources.image                                         | ✔       |          |                    |         |                |            |     |      |
| maps.image                                            |         |          |                    |         |                |            | ✔   |      |
| agenda-cards.image                                    |         | ✔        |                    |         |                |            |     |      |
| command-cards.image                                   |         |          |                    | ✔       |                |            |     |      |
| condition-cards.image                                 |         |          |                    | ✔       |                |            |     |      |
| deployment-cards.image                                |         | ✔        |                    |         |                |            |     |      |
| heroes.healthy                                        |         |          |                    |         |                | ✔          |     |      |
| heroes.wounded                                        |         |          |                    |         |                | ✔          |     |      |
| hero-class-cards.image                                |         |          |                    | ✔       |                |            |     |      |
| imperial-class-cards.image                            |         |          |                    | ✔       |                |            |     |      |
| supply-cards.image                                    |         |          |                    | ✔       |                |            |     |      |
| campaign-story-mission-cards.image                    |         | ✔        |                    |         |                |            |     |      |
| campaign-hero-side-mission-cards.image                |         | ✔        |                    |         |                |            |     |      |
| campaign-ally-side-mission-cards.image                |         | ✔        |                    |         |                |            |     |      |
| campaign-regular-side-mission-cards.image             |         | ✔        |                    |         |                |            |     |      |
| reward-cards.image                                    |         |          |                    | ✔       |                |            |     |      |
| companion-cards.image                                 |         | ✔        |                    |         |                |            |     |      |
| upgrade-cards.image                                   |         |          |                    | ✔       |                |            |     |      |
| campaign-threat-mission-cards.image                   |         | ✔        |                    |         |                |            |     |      |
| form-cards.image                                      |         |          |                    |         | ✔              |            |     |      |
| skirmish-mission-cards.image                          |         |          | ✔                  |         |                |            |     |      |
| epilogue-cards.image                                  |         | ✔        |                    |         |                |            |     |      |
| map-tiles.side_a                                      |         |          |                    |         |                |            |     | ✔    |
| map-tiles.side_b                                      |         |          |                    |         |                |            |     | ✔    |
| card-backs.image(agenda-cards)                        |         | ✔        |                    |         |                |            |     |      |
| card-backs.image(command-cards)                       |         |          |                    | ✔       |                |            |     |      |
| card-backs.image(companion-cards)                     |         | ✔        |                    |         |                |            |     |      |
| card-backs.image(condition-cards)                     |         |          |                    | ✔       |                |            |     |      |
| card-backs.image(deployment-cards)                    |         | ✔        |                    |         |                |            |     |      |
| card-backs.image(imperial-class-cards)                |         |          |                    | ✔       |                |            |     |      |
| card-backs.image(hero-class-cards)                    |         |          |                    | ✔       |                |            |     |      |
| card-backs.image(upgrade-cards)                       |         |          |                    | ✔       |                |            |     |      |
| card-backs.image(reward-cards)                        |         |          |                    | ✔       |                |            |     |      |
| card-backs.image(supply-cards)                        |         |          |                    | ✔       |                |            |     |      |
| card-backs.image(campaign-hero-side-mission-cards)    |         | ✔        |                    |         |                |            |     |      |
| card-backs.image(campaign-ally-side-mission-cards)    |         | ✔        |                    |         |                |            |     |      |
| card-backs.image(campaign-regular-side-mission-cards) |         | ✔        |                    |         |                |            |     |      |
| card-backs.image(campaign-story-mission-cards)        |         | ✔        |                    |         |                |            |     |      |
| card-backs.image(campaign-threat-mission-cards)       |         | ✔        |                    |         |                |            |     |      |
| card-backs.image(form-cards)                          |         |          |                    |         | ✔              |            |     |      |
| card-backs.image(skirmish-mission-cards)              |         |          | ✔                  |         |                |            |     |      |
| card-backs.image(epilogue-cards)                      |         | ✔        |                    |         |                |            |     |      |


## Disclaimer

This project is not produced, endorsed, supported, or affiliated with Fantasy Flight Games.

The copyrightable portions of Star Wars: Imperial Assault and its expansions are © 2014 - 2018 Fantasy Flight Publishing, Inc. Star Wars, and the characters, items, events and places therein are trademarks or registered trademarks of Lucas Film Limited and are used, under license, by Fantasy Flight Games.

All Rights Reserved to their respective owners.
