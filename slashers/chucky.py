from .base import Slasher

CHUCKY = Slasher(
    key="chucky",
    name="Chucky",
    emoji="🧸",
    title="THE KILLER DOLL",
    kill_chance=0.50,
    intro_lines=(
        "A child's toy laughs somewhere nearby. Nobody remembers bringing one.",
        "Tiny footsteps race across the floor and suddenly stop.",
        "A red-haired doll is sitting somewhere it definitely wasn't before.",
    ),
    stalk_lines=(
        "Something small darts behind the furniture.",
        "A tiny laugh comes from directly behind you.",
        "The doll is gone from where you last saw it.",
        "You hear little footsteps moving much faster than they should.",
    ),
    kill_lines=(
        "{victim} underestimated the doll.",
        "{victim} looked down one second too late.",
        "{victim} finally found Chucky. Unfortunately, Chucky found them first.",
    ),
    escape_lines=(
        "{victim} kicks Chucky across the room and makes a run for it.",
        "{victim} gets the door shut before Chucky can reach them.",
        "{victim} survives while Chucky screams threats from somewhere behind them.",
    ),
    kill_methods=(
        "Ambushed from below and taken down with a knife.",
        "Caught off guard after Chucky hid beneath the furniture.",
        "Dragged down before reaching the door.",
        "Cornered after following the sound of Chucky's laughter.",
        "Caught during the struggle and stabbed before escape was possible.",
    ),
)
