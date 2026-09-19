from .base import Slasher

XENOMORPH = Slasher(
    key="xenomorph",
    name="Xenomorph",
    emoji="👽",
    title="THE PERFECT ORGANISM",
    kill_chance=0.69,
    intro_lines=(
        "Something moves inside the ventilation shaft above you.",
        "A motion tracker chirps once. Then twice. The signal is getting closer.",
        "A long shape crawls silently across the ceiling and disappears into a vent.",
    ),
    stalk_lines=(
        "The Xenomorph moves through the vents without making another sound.",
        "Drool hits the floor before the creature lowers itself from the ceiling.",
        "The motion tracker says the signal is close enough to be impossible.",
    ),
    kill_lines=(
        "{victim} hears the vent open directly overhead.",
        "{victim} discovers the corridor was never empty.",
        "{victim} turns around and finds the Xenomorph already there.",
    ),
    escape_lines=(
        "{victim} seals the bulkhead just before the Xenomorph reaches it.",
        "{victim} stays quiet long enough for the creature to move past.",
        "{victim} escapes while the motion tracker signal moves away.",
    ),
    kill_methods=(
        "Caught by the Xenomorph after it dropped from the vents.",
        "Cornered in a sealed corridor by the creature.",
        "Overpowered at close range by the Xenomorph.",
    ),
)
