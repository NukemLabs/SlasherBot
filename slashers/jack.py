from .base import Slasher

JACK = Slasher(
    key="jack",
    name="Jack Torrance",
    emoji="🪓",
    title="THE CARETAKER",
    kill_chance=0.54,
    intro_lines=(
        "A hotel corridor sits empty except for the sound of an axe striking wood.",
        "The elevator doors open on an empty hallway. Somewhere nearby, Jack is laughing.",
        "A door shakes in its frame as something heavy hits it from the other side.",
    ),
    stalk_lines=(
        "Jack drags the axe along the wall as he searches the corridor.",
        "Footsteps echo through the Overlook while Jack checks each doorway.",
        "The hotel seems to guide Jack toward you no matter which hall you choose.",
    ),
    kill_lines=(
        "{victim} chooses the wrong hallway in the Overlook.",
        "{victim} finds a locked door was not enough to stop Jack.",
        "{victim} hears the axe break through just before the room goes quiet.",
    ),
    escape_lines=(
        "{victim} loses Jack in the maze of hotel corridors.",
        "{victim} slips away while Jack searches the wrong room.",
        "{victim} gets outside before the Overlook can pull them back in.",
    ),
    kill_methods=(
        "Cornered by Jack and his fire axe inside the hotel.",
        "Caught after Jack broke through the final locked door.",
        "Trapped in the Overlook with Jack closing in.",
    ),
)
