from .base import Slasher

DEADITES = Slasher(
    key="deadites",
    name="Deadites",
    emoji="📕",
    title="THE EVIL DEAD",
    kill_chance=0.60,
    intro_lines=(
        "A book bound in strange material opens by itself.",
        "A voice laughs from the cellar even though the cellar is empty.",
        "The cabin windows slam shut as something begins speaking from the woods.",
    ),
    stalk_lines=(
        "A Deadite pounds against the door while another voice laughs from behind you.",
        "The possessed figure bends in a way it absolutely should not and keeps coming.",
        "The cabin fills with overlapping voices promising you are not leaving.",
    ),
    kill_lines=(
        "{victim} waits one second too long to deal with the possession.",
        "{victim} finds out the cabin has more than one Deadite.",
        "{victim} hears the laughter continue after the lights go out.",
    ),
    escape_lines=(
        "{victim} gets clear as the Deadites are pulled back into the darkness.",
        "{victim} survives long enough for the possession to lose its grip.",
        "{victim} makes it out of the cabin while the voices scream from inside.",
    ),
    kill_methods=(
        "Overwhelmed by the Deadites inside the cabin.",
        "Caught after the possession spread through the room.",
        "Surrounded by Deadites before reaching the door.",
    ),
)
