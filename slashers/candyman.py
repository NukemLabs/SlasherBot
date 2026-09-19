from .base import Slasher

CANDYMAN = Slasher(
    key="candyman",
    name="Candyman",
    emoji="🐝",
    title="THE LEGEND IN THE MIRROR",
    kill_chance=0.61,
    intro_lines=(
        "A mirror catches the light. For a moment, someone is standing inside it.",
        "The faint sound of bees fills the room.",
        "A deep voice whispers a name from somewhere behind the glass.",
    ),
    stalk_lines=(
        "Bees begin gathering around the mirror.",
        "The reflection moves a fraction of a second too late.",
        "A hook scrapes slowly against the other side of the glass.",
        "The room fills with the sound of wings.",
    ),
    kill_lines=(
        "{victim} discovered that some legends should stay legends.",
        "{victim} looked into the mirror for too long.",
        "{victim} called to something that answered.",
    ),
    escape_lines=(
        "{victim} refuses to speak and the reflection finally disappears.",
        "{victim} gets away as the swarm vanishes into the darkness.",
        "{victim} survives. The mirror is empty again.",
    ),
    kill_methods=(
        "Pulled toward the mirror and struck down by Candyman's hook.",
        "Caught as the swarm closed in around the room.",
        "Taken after the reflection stepped out of the glass.",
        "Cornered beside the mirror with nowhere left to escape.",
        "The hook found its mark before the legend faded away.",
    ),
)
