from .base import Slasher

ART = Slasher(
    key="art",
    name="Art the Clown",
    emoji="🤡",
    title="THE SILENT CLOWN",
    kill_chance=0.60,
    intro_lines=(
        "A silent clown is standing at the far end of the hallway... smiling.",
        "Someone finds a black-and-white clown hat where there definitely wasn't one before.",
        "A tiny horn sounds somewhere in the dark. HONK.",
    ),
    stalk_lines=(
        "Art waves cheerfully... then reaches into a garbage bag.",
        "Art points at you, points at himself, and silently laughs.",
        "A tiny horn sounds again. Somehow, he's much closer now.",
        "Art disappears behind a doorway, then leans back into view with a grin.",
    ),
    kill_lines=(
        "{victim} should not have waited to see what Art pulled out of the bag.",
        "{victim} made the mistake of assuming the clown was joking.",
        "{victim} saw Art smile. That was the last warning.",
    ),
    escape_lines=(
        "{victim} gets away while Art angrily honks a tiny horn behind them.",
        "{victim} escapes. Art watches them leave... then gives a sarcastic little wave.",
        "{victim} survives. Art looks disappointed, shrugs, and disappears.",
    ),
    kill_methods=(
        "Blindsided by something Art pulled from the garbage bag.",
        "Knocked to the floor after one mocking little HONK.",
        "Caught in the hallway and beaten down before escape was possible.",
        "Dragged back into the room while Art silently waved goodbye.",
        "Cornered after Art blocked the only way out.",
    ),
)
