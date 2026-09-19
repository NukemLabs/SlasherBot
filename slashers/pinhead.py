from .base import Slasher

PINHEAD = Slasher(
    key="pinhead",
    name="Pinhead",
    emoji="⛓️",
    title="THE HELL PRIEST",
    kill_chance=0.64,
    intro_lines=(
        "A strange puzzle box appears where nobody left one.",
        "Chains rattle somewhere in the dark, even though nothing is moving.",
        "The air turns cold. A geometric box slowly begins to open.",
    ),
    stalk_lines=(
        "The walls seem farther away than they were a moment ago.",
        "A chain slides across the floor and stops at your feet.",
        "The puzzle box clicks once. Something has answered.",
        "The room darkens as shapes begin moving beyond the doorway.",
    ),
    kill_lines=(
        "{victim} opened a door that should have stayed closed.",
        "{victim} learned that running was never really an escape.",
        "{victim} made one final mistake with the box.",
    ),
    escape_lines=(
        "{victim} completes the puzzle and the chains suddenly fall still.",
        "{victim} forces the box shut before the doorway can fully open.",
        "{victim} survives as the Cenobites fade back into the darkness.",
    ),
    kill_methods=(
        "Dragged into the darkness by hooked chains.",
        "Pulled through the opened doorway before the box could be closed.",
        "Caught by chains after making the wrong move with the puzzle box.",
        "Taken by the Cenobites when the configuration opened completely.",
        "The chains found their mark before escape was possible.",
    ),
)
