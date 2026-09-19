from .base import Slasher

JIGSAW = Slasher(
    key="jigsaw",
    name="Jigsaw",
    emoji="🧩",
    title="I WANT TO PLAY A GAME",
    kill_chance=0.58,
    intro_lines=(
        "A television turns on by itself. Billy the puppet is waiting on the screen.",
        "A cassette recorder clicks on beside a locked door.",
        "Red numbers begin counting down while Billy stares silently from a monitor.",
    ),
    stalk_lines=(
        "Billy appears on another screen as the timer keeps dropping.",
        "The room reveals one more mechanism you definitely did not notice before.",
        "A recorded voice calmly explains that your next choice matters.",
    ),
    kill_lines=(
        "{victim} runs out of time before solving the game.",
        "{victim} makes the wrong choice with seconds left on the clock.",
        "{victim} discovers the room was designed to punish panic.",
    ),
    escape_lines=(
        "{victim} completes the game before the timer reaches zero.",
        "{victim} finds the intended solution and the lock releases.",
        "{victim} survives as the mechanism powers down.",
    ),
    kill_methods=(
        "Failed Jigsaw's trap before the timer expired.",
        "Triggered the trap after choosing the wrong solution.",
        "Ran out of time inside one of Jigsaw's games.",
    ),
)
