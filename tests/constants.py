class CONTENT_TYPES:
    FORM_CARDS = 'form-cards'
    SOURCE = 'sources'
    SOURCE_CONTENTS = 'source-contents'
    SKIRMISH_MAP = 'skirmish-maps'
    AGENDA = 'agenda-cards'
    AGENDA_DECKS = 'agenda-decks'
    COMMAND = 'command-cards'
    CONDITION = 'condition-cards'
    DEPLOYMENT = 'deployment-cards'
    HERO = 'heroes'
    HERO_CLASS = 'hero-class-cards'
    IMPERIAL_CLASSES = 'imperial-classes'
    IMPERIAL_CLASS_CARD = 'imperial-class-cards'
    SUPPLY = 'supply-cards'
    STORY_MISSION = 'story-mission-cards'
    SIDE_MISSION = 'side-mission-cards'
    REWARD = 'reward-cards'
    COMPANION = 'companion-cards'
    UPGRADE = 'upgrade-cards'
    CARD = 'card-backs'
    THREAT_MISSION = 'threat-mission-cards'

    as_list = [
        SOURCE,
        SOURCE_CONTENTS,
        SKIRMISH_MAP,
        AGENDA,
        AGENDA_DECKS,
        COMMAND,
        CONDITION,
        DEPLOYMENT,
        HERO,
        HERO_CLASS,
        IMPERIAL_CLASSES,
        IMPERIAL_CLASS_CARD,
        SUPPLY,
        STORY_MISSION,
        SIDE_MISSION,
        REWARD,
        COMPANION,
        UPGRADE,
        CARD,
        THREAT_MISSION,
        FORM_CARDS,
    ]

    without_ids = [
        SOURCE_CONTENTS,
        SKIRMISH_MAP,
        CONDITION,
        CARD,
    ]


class DEPLOYMENT_TRAITS:
    SPY = 'Spy'
    BRAWLER = 'Brawler'
    FORCE_USER = 'Force User'
    SKIRMISH_UPGRADE = 'Skirmish Upgrade'
    WOOKIEE = 'Wookiee'
    GUARDIAN = 'Guardian'
    TROOPER = 'Trooper'
    CREATURE = 'Creature'
    HEAVY_WEAPON = 'Heavy Weapon'
    LEADER = 'Leader'
    SMUGGLER = 'Smuggler'
    VEHICLE = 'Vehicle'
    HUNTER = 'Hunter'
    DROID = 'Droid'


class SUPPLY_TRAITS:
    CONSUMABLE = 'Consumable'
    DROID = 'Droid'
    ENERGY = 'Energy'
    EXPLOSIVE = 'Explosive'
    INTEL = 'Intel'
    MEDICAL = 'Medical'
    TOOL = 'Tool'
    VALUABLE = 'Valuable'


class BUFF_TRAITS:
    ACCESSORY = 'Accessory'
    ARMOR = 'Armor'
    BALANCE = 'Balance'
    BARREL = 'Barrel'
    BLADE = 'Blade'
    BLASTER = 'Blaster'
    CLUB = 'Club'
    CONSUMABLE = 'Consumable'
    DISRUPTOR = 'Disruptor'
    ENERGY = 'Energy'
    ENHANCEMENT = 'Enhancement'
    EXPLOSIVE = 'Explosive'
    FIST = 'Fist'
    HEAVY = 'Heavy'
    HELMET = 'Helmet'
    IMPACT = 'Impact'
    LIGHT = 'Light'
    LIGHTSABER = 'Lightsaber'
    MEDICAL = 'Medical'
    MEDIUM = 'Medium'
    MODIFICATION = 'Modification'
    PISTOL = 'Pistol'
    PROJECTILE = 'Projectile'
    RIFLE = 'Rifle'
    SIGHTS = 'Sights'
    STAFF = 'Staff'
    AMMUNITION = 'Ammunition'


class BUFF_TYPES:
    EQUIPMENT = 'Equipment'
    MELEE = 'Melee Weapon'
    RANGED = 'Ranged Weapon'
    ARMOR = 'Armor'
    MELEE_MOD = 'Melee Weapon Modification'
    RANGED_MOD = 'Ranged Weapon Modification'
    FEAT = 'Feat'


class GAME_MODES:
    CAMPAIGN = 'Campaign'
    SKIRMISH = 'Skirmish'


class AFFILIATION:
    REBEL = 'Rebel'
    IMPERIAL = 'Imperial'
    MERCENARY = 'Mercenary'
    NEUTRAL = 'Neutral'
