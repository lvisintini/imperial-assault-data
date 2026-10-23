class CONTENT_TYPES:
    FORM_CARDS = 'form-cards'
    SOURCE = 'sources'
    SOURCE_CONTENTS = 'source-contents'
    MAP = 'maps'
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
    STORY_MISSION = 'campaign-story-mission-cards'
    HERO_SIDE_MISSION = 'campaign-hero-side-mission-cards'
    ALLY_SIDE_MISSION = 'campaign-ally-side-mission-cards'
    REGULAR_SIDE_MISSION = 'campaign-regular-side-mission-cards'
    REWARD = 'reward-cards'
    COMPANION = 'companion-cards'
    UPGRADE = 'upgrade-cards'
    CARD = 'card-backs'
    THREAT_MISSION = 'campaign-threat-mission-cards'
    SKIRMISH_MISSION = 'skirmish-mission-cards'
    RAID_MISSION = 'raid-missions'
    EPILOGUE = 'epilogue-cards'
    MINIATURES = 'miniatures'
    MISSIONS = 'missions'
    MISSION_REWARDS = 'mission-rewards'
    RECORD_LINKS = 'record-links'

    as_list = [
        SOURCE,
        SOURCE_CONTENTS,
        MAP,
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
        HERO_SIDE_MISSION,
        ALLY_SIDE_MISSION,
        REGULAR_SIDE_MISSION,
        REWARD,
        COMPANION,
        UPGRADE,
        CARD,
        THREAT_MISSION,
        FORM_CARDS,
        SKIRMISH_MISSION,
        RAID_MISSION,
        EPILOGUE,
        MINIATURES,
        MISSIONS,
        MISSION_REWARDS,
        RECORD_LINKS,
    ]

    # The collections missions.json indexes (agenda cards only where `mission` is true).
    mission_types = [
        STORY_MISSION,
        THREAT_MISSION,
        HERO_SIDE_MISSION,
        ALLY_SIDE_MISSION,
        REGULAR_SIDE_MISSION,
        AGENDA,
        SKIRMISH_MISSION,
        RAID_MISSION,
    ]

    without_ids = [
        SOURCE_CONTENTS,
        MISSION_REWARDS,
        RECORD_LINKS,
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
