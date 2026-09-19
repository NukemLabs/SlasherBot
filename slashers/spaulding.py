from .base import Slasher

SPAULDING = Slasher(
    key="spaulding",
    name="Captain Spaulding",
    emoji="🎪",
    title="THE TWISTED SHOWMAN",
    kill_chance=0.54,
    intro_lines=(
        "A filthy clown laugh echoes from somewhere nearby.",
        "A hand-painted sign appears where there definitely wasn't one before.",
        "Someone hears a carnival tune playing faintly in the distance.",
    ),
    stalk_lines=(
        "Spaulding steps into view, grinning like he already knows how this ends.",
        "A mocking laugh follows you from the next room.",
        "Spaulding keeps talking while slowly blocking the nearest exit.",
        "The clown disappears around the corner, still laughing to himself.",
    ),
    kill_lines=(
        "{victim} stayed for the show a little too long.",
        "{victim} picked the wrong clown to argue with.",
        "{victim} should have left when the laughing started.",
    ),
    escape_lines=(
        "{victim} bolts while Spaulding is still running his mouth.",
        "{victim} slips out the back while Spaulding keeps laughing.",
        "{victim} escapes, leaving Spaulding furious and shouting after them.",
    ),
    kill_methods=(
        "Clubbed down after being cornered near the exit.",
        "Caught trying to slip past and beaten to the floor.",
        "Dragged back after making a run for the door.",
        "Ambushed from behind while following the wrong way out.",
        "Cornered during the taunting and never made it past the doorway.",
    ),
)
