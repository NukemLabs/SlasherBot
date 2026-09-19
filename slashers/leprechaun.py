from .base import Slasher

LEPRECHAUN = Slasher(
    key="leprechaun",
    name="Leprechaun",
    emoji="🍀",
    title="WHERE'S ME GOLD?",
    kill_chance=0.55,
    intro_lines=(
        "A gold coin rolls across the floor and stops at your feet.",
        "A tiny laugh comes from beside a pot of gold that definitely was not there before.",
        "Something small moves through the shadows while coins begin disappearing.",
    ),
    stalk_lines=(
        "The Leprechaun follows the trail of missing gold straight toward you.",
        "A rhyme comes from the next room, followed by angry little footsteps.",
        "The Leprechaun appears on a shelf, grins, and asks about his gold.",
    ),
    kill_lines=(
        "{victim} learns why stealing a Leprechaun's gold is a terrible idea.",
        "{victim} runs out of luck at exactly the wrong moment.",
        "{victim} discovers the Leprechaun never forgets what belongs to him.",
    ),
    escape_lines=(
        "{victim} returns the gold and backs away while the Leprechaun counts it.",
        "{victim} escapes while the Leprechaun is distracted by his missing coins.",
        "{victim} survives with considerably less gold than before.",
    ),
    kill_methods=(
        "Caught by the Leprechaun while trying to keep his gold.",
        "Cornered after the Leprechaun followed the stolen coins.",
        "Ran out of luck before escaping the Leprechaun.",
    ),
)
