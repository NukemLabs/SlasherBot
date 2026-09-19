from .base import Slasher

KLOWNS = Slasher(
    key="klowns",
    name="Killer Klowns",
    emoji="🤡",
    title="FROM OUTER SPACE",
    kill_chance=0.57,
    intro_lines=(
        "A circus tune plays outside while a glowing tent appears where nothing stood before.",
        "Bright footprints lead toward a spaceship shaped suspiciously like a circus tent.",
        "A clown with a ray gun waves cheerfully from across the street.",
    ),
    stalk_lines=(
        "The Klowns fan out while colorful shadows move between the buildings.",
        "A cotton-candy ray flashes past and coats the wall behind you.",
        "One Klown distracts you while another quietly circles around.",
    ),
    kill_lines=(
        "{victim} learns the circus was never here to entertain anyone.",
        "{victim} gets surrounded before finding the exit.",
        "{victim} discovers the colorful ray gun is not a toy.",
    ),
    escape_lines=(
        "{victim} gets away while the Klowns argue over who had the better shot.",
        "{victim} escapes before the cotton-candy ray can fire again.",
        "{victim} survives as the circus ship disappears into the night.",
    ),
    kill_methods=(
        "Captured by a Killer Klown's cotton-candy weapon.",
        "Cornered by the Klowns before reaching the exit.",
        "Caught when the Klowns surrounded the escape route.",
    ),
)
