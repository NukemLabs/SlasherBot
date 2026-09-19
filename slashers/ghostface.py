from .base import Slasher

GHOSTFACE = Slasher(
    key="ghostface",
    name="Ghostface",
    emoji="📞",
    title="THE CALLER",
    kill_chance=0.52,
    intro_lines=(
        "A phone starts ringing. Nobody recognizes the number.",
        "Someone swears they saw a black-robed figure disappear around a corner.",
        "An unknown caller keeps ringing. The server suddenly feels a lot quieter.",
    ),
    stalk_lines=(
        "Your phone rings again. This time, the caller says nothing.",
        "A shadow slips past the doorway just as you turn around.",
        "The caller seems to know exactly where you are.",
        "You hear footsteps, then a phone ringing somewhere nearby.",
    ),
    kill_lines=(
        "{victim} answered one call too many.",
        "{victim} thought the room was empty. It wasn't.",
        "{victim} turned around just a second too late.",
    ),
    escape_lines=(
        "{victim} fights back and sends Ghostface stumbling long enough to escape.",
        "{victim} gets outside and finds help before Ghostface can catch up.",
        "{victim} escapes. The phone stops ringing.",
    ),
    kill_methods=(
        "Ambushed and stabbed after answering the phone.",
        "Cornered in the hallway and taken down with a knife.",
        "Tripped while running and caught before reaching the door.",
        "Pulled back inside before help could arrive.",
        "Caught hiding after the ringing phone gave away the location.",
    ),
)
