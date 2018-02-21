# Imperial Assault Data

An easy-to-use collection of data and images from the [Imperial Assault](https://www.fantasyflightgames.com/en/products/star-wars-imperial-assault/) game by [Fantasy Flight Games](https://www.fantasyflightgames.com).

## What you can find inside

In the `data` directory you will find all the data for the game in JSON format, separated by type.
The data structure loosely mimics that of a relational database.

 - `data/sources.json` (contains data for the Products and Expansions available in for the game)
 - `data/source-contents.json` (the contents of this file tie together the products in `data/sources.json` with their contents in the files below)
 - `data/deployment-cards.json`
 - `data/companion-cards.json`
 - `data/form-cards.json` (contains data for the form cards introduced in "Heart of the Empire" expansion box)
 - `data/heroes.json`
 - `data/hero-class-cards.json`
 - `data/imperial-classes.json`
 - `data/imperial-class-cards.json`
 - `data/agenda-decks.json`
 - `data/agenda-cards.json`
 - `data/story-mission-cards.json`
 - `data/side-mission-cards.json`
 - `data/threat-mission-cards.json`
 - `data/supply-cards.json`
 - `data/reward-cards.json`
 - `data/upgrade-cards.json`
 - `data/command-cards.json`
 - `data/condition-cards.json`
 - `data/skirmish-maps.json`
 - `data/card-backs` (contains the data for the images of the back of the different decks you will find in the game)


With `data/source-contents.json` you can find the contents of a particular product by filtering the entries on this file by the `source_id`.
After that, you can use the value of `content_type` and `content_id` the components contained in the product file.

You can also use this file to determine the sources on which a particular component can be found.
You you this by filter in the entries on this using the id of the component and it's type.

The structure in this file can also be expanded to accommodate for additional data (number of copies, etc.)

All entries have an associated image that you can find inside the `images` folder.

The `images` folder has 2 sub-folders, `small` and `large` and contain what you would expect.
All images in the `large` folder have a scaled version inside the `small` folder and all the file paths found in the
data files are valid for both sub-folders.

The images rotated and aligned using fairly complex image manipulation via OpenCV.
The images also have consistent sizes (except skirmish maps):


**Large:**
 - 300x300
    - sources
 - 476x740
    - story-mission-cards
    - threat-mission-cards
    - card-backs
    - deployment-cards
    - side-mission-cards
    - agenda-cards
    - companion-cards
 - 424x657
    - card-backs
    - hero-class-cards
    - upgrade-cards
    - reward-cards
    - imperial-class-cards
    - condition-cards
    - supply-cards
    - command-cards
 - 657x424
    - form-cards
 - 1490x1186
    - heroes

 - 473x729
    - card-backs
 - 482x740
    - card-backs
 - 655x424
    - card-backs


**Small:**
 - 300x300
    - sources
 - 301x470
    - story-mission-cards
    - threat-mission-cards
    - card-backs
    - deployment-cards
    - side-mission-cards
    - agenda-cards
    - companion-cards
 - 293x454
    - card-backs
    - hero-class-cards
    - upgrade-cards
    - reward-cards
    - imperial-class-cards
    - condition-cards
    - supply-cards
    - command-cards
 - 454x293
    - form-cards
 - 650x515
    - heroes

 - 299x465
    - card-backs
 - 482x740
    - card-backs
 - 655x424
    - card-backs


## Versioning

This project uses [SemVer](http://semver.org/). Given a `MAJOR.MINOR.PATCH` version number, we will increment the:
- `MAJOR` version when existing content is changed in such a way that it can break consumers of the data
- `MINOR` version when new content is added in a backwards-compatible manner, or existing content is changed in a backwards-compatible manner
- `PATCH` version when fixing mistakes in existing content


## Contributors

The initial load of images and data was put together by scraping http://cards.boardwars.eu/, I do not know this guys
personally, but I'm grateful to them for putting together such a great source of data.


## Disclaimer

This project is not produced, endorsed, supported, or affiliated with Fantasy Flight Games.
The copyrightable portions of Star Wars: Imperial Assault and its expansions are © 2014 - 2018 Fantasy Flight Publishing, Inc. Star Wars, and the characters, items, events and places therein are trademarks or registered trademarks of Lucas Film Limited and are used, under license, by Fantasy Flight Games. All Rights Reserved to their respective owners.