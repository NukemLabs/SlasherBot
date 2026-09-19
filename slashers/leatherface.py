from .base import Slasher

LEATHERFACE = Slasher(
    key="leatherface",
    name="Leatherface",
    emoji="🪚",
    title="THE BUTCHER",
    kill_chance=0.66,
    intro_lines=(
        "A chainsaw sputters to life somewhere nearby.",
        "The sound of a heavy door slamming echoes through the building.",
        "A chainsaw revs once... then goes silent.",
    ),
    stalk_lines=(
        "The chainsaw starts again, much closer this time.",
        "Heavy footsteps crash through the next room.",
        "Something slams into the wall behind you.",
        "Leatherface barrels through the doorway, chainsaw screaming.",
    ),
    kill_lines=(
        "{victim} chose the wrong house to run through.",
        "{victim} heard the chainsaw too late.",
        "{victim} nearly made it outside.",
    ),
    escape_lines=(
        "{victim} slips through a narrow opening before Leatherface can follow.",
        "{victim} reaches the road while the chainsaw roars behind them.",
        "{victim} escapes as Leatherface rages in the distance.",
    ),
    kill_methods=(
        "Caught at the doorway and taken down by the chainsaw.",
        "Knocked to the floor before Leatherface finished the attack.",
        "Cornered in the house with nowhere left to run.",
        "Caught in the yard before reaching the road.",
        "Dragged back inside after the escape route was cut off.",
    ),
)
