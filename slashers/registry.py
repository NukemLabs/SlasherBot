import random

from .art import ART
from .base import Slasher
from .candyman import CANDYMAN
from .chucky import CHUCKY
from .freddy import FREDDY
from .ghostface import GHOSTFACE
from .jason import JASON
from .leatherface import LEATHERFACE
from .michael import MICHAEL
from .pinhead import PINHEAD
from .spaulding import SPAULDING
from .pumpkinhead import PUMPKINHEAD
from .jack import JACK
from .pennywise import PENNYWISE
from .norman import NORMAN
from .xenomorph import XENOMORPH
from .klowns import KLOWNS
from .deadites import DEADITES
from .jigsaw import JIGSAW
from .leprechaun import LEPRECHAUN
from .thing import THING
from .nosferatu import NOSFERATU

SLASHERS: tuple[Slasher, ...] = (
    MICHAEL,
    JASON,
    GHOSTFACE,
    LEATHERFACE,
    CHUCKY,
    SPAULDING,
    ART,
    FREDDY,
    CANDYMAN,
    PINHEAD,
    PUMPKINHEAD,
    JACK,
    PENNYWISE,
    NORMAN,
    XENOMORPH,
    KLOWNS,
    DEADITES,
    JIGSAW,
    LEPRECHAUN,
    THING,
    NOSFERATU,
)

SLASHER_BY_KEY: dict[str, Slasher] = {
    slasher.key: slasher
    for slasher in SLASHERS
}

# Higher weight = more likely to appear during normal/random hunts.
SLASHER_WEIGHTS: dict[str, int] = {
    "michael": 21,
    "jason": 21,
    "ghostface": 13,
    "leatherface": 11,
    "chucky": 10,
    "spaulding": 8,
    "art": 5,
    "freddy": 4,
    "candyman": 4,
    "pinhead": 3,
    "pumpkinhead": 4,
    "jack": 7,
    "pennywise": 3,
    "norman": 8,
    "xenomorph": 4,
    "klowns": 4,
    "deadites": 5,
    "jigsaw": 5,
    "leprechaun": 4,
    "thing": 3,
    "nosferatu": 4,
}

RARITY_LABELS: dict[str, str] = {
    "michael": "Common",
    "jason": "Common",
    "ghostface": "Uncommon",
    "leatherface": "Uncommon",
    "chucky": "Uncommon",
    "spaulding": "Uncommon",
    "art": "Rare",
    "freddy": "Rare",
    "candyman": "Rare",
    "pinhead": "Very Rare",
    "pumpkinhead": "Rare",
    "jack": "Uncommon",
    "pennywise": "Very Rare",
    "norman": "Uncommon",
    "xenomorph": "Rare",
    "klowns": "Rare",
    "deadites": "Rare",
    "jigsaw": "Rare",
    "leprechaun": "Rare",
    "thing": "Very Rare",
    "nosferatu": "Rare",
}


def random_slasher() -> Slasher:
    weights = [
        SLASHER_WEIGHTS.get(slasher.key, 1)
        for slasher in SLASHERS
    ]
    return random.choices(SLASHERS, weights=weights, k=1)[0]


def get_slasher(key: str) -> Slasher | None:
    return SLASHER_BY_KEY.get(key)


def rarity_for(key: str) -> str:
    return RARITY_LABELS.get(key, "Unknown")
