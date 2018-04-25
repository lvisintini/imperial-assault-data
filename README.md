# Imperial Assault Data [![Build Status](https://travis-ci.org/lvisintini/imperial-assault-data.svg?branch=master)](https://travis-ci.org/lvisintini/imperial-assault-data)

An easy-to-use collection of data and images from the [Imperial Assault](https://www.fantasyflightgames.com/en/products/star-wars-imperial-assault/) game by [Fantasy Flight Games](https://www.fantasyflightgames.com).

## What you can find inside

In the `data` directory you will find all the data for the game in JSON formatted files.
The data structure loosely mimics that of a relational database.

For example, with the `.data/source-contents.json` file you can determine the contents of a particular product by filtering the entries by `source_id`.

You can find an example on how to do this in the `./examples` folder, along with other examples.

All entries have an associated image (or 2) that you can find inside the `./images/large` (for high resolution images) and the `./images/small` folder (for low resolution images).

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

```
git clone git@github.com:lvisintini/imperial-assault-data.git
cd ./imperial-assault-data
sudo add-apt-repository ppa:jonathonf/python-3.6
sudo apt update
sudo apt install python3.6
sudo apt install python3.6-dev virtualwrapper
mkvirtualenv --python=/usr/bin/python3.6 imperial-assault-data
pip install -r requirements.txt

py.test
```

## Testing

Each change in the dataset is checked against a multitude of test that are meant to preserve the integrity of the data.
This is done automatically for each code change on this repo.

Alternatively, you can also run the test suit yourself by setting up your environment and running `py.test`


## Versioning

This project uses [SemVer](http://semver.org/). Given a `MAJOR.MINOR.PATCH` version number, we will increment the:
- `MAJOR` version when existing content is changed in such a way that it can break consumers of the data
- `MINOR` version when new content is added in a backwards-compatible manner, or existing content is changed in a backwards-compatible manner
- `PATCH` version when fixing mistakes in existing content


## Contributors

The initial load of images and data was put together by scraping http://cards.boardwars.eu/, I do not know this guys
personally, but I'm grateful to them for putting together such a great source of data.


# Image sizes

What follows is a list of all the image types and their sizes for large and small.

|                    | Large     | Small   |
|--------------------|-----------|---------|
| **Source**         | 300x300   | 300x300 |
| **Standard**       | 476x740   | 301x470 |
| **Mini**           | 424x657   | 293x454 |
| **Mini (Flipped)** | 657x424   | 454x293 |
| **Hero Sheet**     | 1490x1186 | 650x515 |

The table bellow shows you the expected for all the different images included in this data set.

|                                        | Source  | Standard | Mini    | Mini (Flipped) | Hero Sheet | Any |
|----------------------------------------|---------|----------|---------|----------------|------------|-----|
| sources.image                          | ✔       |          |         |                |            |     |
| skirmish-maps.image                    |         |          |         |                |            | ✔   |
| agenda-cards.image                     |         | ✔        |         |                |            |     |
| command-cards.image                    |         |          | ✔       |                |            |     |
| condition-cards.image                  |         |          | ✔       |                |            |     |
| deployment-cards.image                 |         | ✔        |         |                |            |     |
| heroes.healthy                         |         |          |         |                | ✔          |     |
| heroes.wounded                         |         |          |         |                | ✔          |     |
| hero-class-cards.image                 |         |          | ✔       |                |            |     |
| imperial-class-cards.image             |         |          | ✔       |                |            |     |
| supply-cards.image                     |         |          | ✔       |                |            |     |
| story-mission-cards.image              |         | ✔        |         |                |            |     |
| side-mission-cards.image               |         | ✔        |         |                |            |     |
| reward-cards.image                     |         |          | ✔       |                |            |     |
| companion-cards.image                  |         | ✔        |         |                |            |     |
| upgrade-cards.image                    |         |          | ✔       |                |            |     |
| threat-mission-cards.image             |         | ✔        |         |                |            |     |
| form-cards.image                       |         |          |         | ✔              |            |     |
| card-backs.image(agenda-decks)         |         | ✔        |         |                |            |     |
| card-backs.image(command-cards)        |         |          | ✔       |                |            |     |
| card-backs.image(companion-cards)      |         | ✔        |         |                |            |     |
| card-backs.image(condition-cards)      |         |          | ✔       |                |            |     |
| card-backs.image(deployment-cards)     |         | ✔        |         |                |            |     |
| card-backs.image(imperial-classes)     |         |          | ✔       |                |            |     |
| card-backs.image(heroes)               |         |          | ✔       |                |            |     |
| card-backs.image(upgrade-cards)        |         |          | ✔       |                |            |     |
| card-backs.image(reward-cards)         |         |          | ✔       |                |            |     |
| card-backs.image(supply-cards)         |         |          | ✔       |                |            |     |
| card-backs.image(side-mission-cards)   |         | ✔        |         |                |            |     |
| card-backs.image(story-mission-cards)  |         | ✔        |         |                |            |     |
| card-backs.image(threat-mission-cards) |         | ✔        |         |                |            |     |
| card-backs.image(form-cards)           |         |          |         | ✔              |            |     |


## Disclaimer

This project is not produced, endorsed, supported, or affiliated with Fantasy Flight Games.

The copyrightable portions of Star Wars: Imperial Assault and its expansions are © 2014 - 2018 Fantasy Flight Publishing, Inc. Star Wars, and the characters, items, events and places therein are trademarks or registered trademarks of Lucas Film Limited and are used, under license, by Fantasy Flight Games.

All Rights Reserved to their respective owners.
