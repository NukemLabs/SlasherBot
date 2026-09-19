from .base import Slasher

PENNYWISE = Slasher(
    key="pennywise",
    name="Pennywise",
    emoji="🎈",
    title="THE DANCING CLOWN",
    kill_chance=0.64,
    intro_lines=(
        "A single red balloon floats where there is no wind.",
        "Something laughs softly from inside a storm drain.",
        "The lights flicker and a clown-shaped shadow stretches across the wall.",
    ),
    stalk_lines=(
        "Pennywise changes shape each time you look away.",
        "A red balloon drifts after you while laughter echoes from nowhere.",
        "The hallway bends into somewhere you remember being afraid of.",
    ),
    kill_lines=(
        "{victim} lets the fear take over, and Pennywise notices.",
        "{victim} follows the wrong balloon into the dark.",
        "{victim} realizes too late that the thing smiling back is not a clown.",
    ),
    escape_lines=(
        "{victim} refuses to give Pennywise the fear it wants.",
        "{victim} stands their ground until the illusion begins to collapse.",
        "{victim} escapes as the laughter fades back into the dark.",
    ),
    kill_methods=(
        "Overwhelmed after Pennywise turned fear against them.",
        "Caught when Pennywise's illusion became real enough.",
        "Taken after following the red balloon too far.",
    ),
)
