from .base import Slasher

FREDDY = Slasher(
    key="freddy",
    name="Freddy Krueger",
    emoji="🔥",
    title="THE DREAM STALKER",
    kill_chance=0.62,
    intro_lines=(
        "The server goes strangely quiet. Somewhere, children can be heard singing.",
        "A boiler room door appears where there definitely wasn't one before.",
        "A scraping sound drags slowly across metal in the distance.",
    ),
    stalk_lines=(
        "The hallway stretches farther every time you look away.",
        "Freddy's laugh echoes from somewhere that shouldn't exist.",
        "Four blades scrape slowly across a pipe behind you.",
        "You try to wake up. Nothing happens.",
    ),
    kill_lines=(
        "{victim} realized too late that this wasn't a normal hunt.",
        "{victim} tried to wake up. Freddy had other plans.",
        "{victim} found out just how dangerous falling asleep can be.",
    ),
    escape_lines=(
        "{victim} jolts awake before Freddy can finish the job.",
        "{victim} forces themselves awake and escapes the nightmare.",
        "{victim} survives as the dream collapses around Freddy.",
    ),
    kill_methods=(
        "Dragged deeper into the nightmare and struck down by Freddy's glove.",
        "Caught in the boiler room before waking was possible.",
        "Pulled back into the dream just as escape seemed possible.",
        "Cornered in the nightmare and finished with the bladed glove.",
        "Never woke up before Freddy closed in.",
    ),
)
