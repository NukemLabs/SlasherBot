from .base import Slasher

JASON = Slasher(
    key="jason",
    name="Jason Voorhees",
    emoji="🏒",
    title="THE TERROR OF CRYSTAL LAKE",
    kill_chance=0.68,
    intro_lines=(
        "Something heavy moves through the trees near the lake.",
        "A hockey mask catches the moonlight for just a second.",
        "The woods go silent. Then a branch snaps.",
    ),
    stalk_lines=(
        "The victim runs. The footsteps behind them never seem to get faster.",
        "A shadow moves between the cabins.",
        "The path to the road suddenly feels much longer than it did before.",
        "A machete scrapes against the side of the cabin.",
    ),
    kill_lines=(
        "{victim} almost reached the road. Almost.",
        "{victim} chose the wrong cabin to hide in.",
        "{victim} made one mistake: going anywhere near the lake.",
    ),
    escape_lines=(
        "{victim} gets the engine started and tears away from the lake.",
        "{victim} reaches the highway before Jason can close the distance.",
        "{victim} survives. Behind them, Jason disappears back into the woods.",
    ),
    kill_methods=(
        "Struck down with a machete near the cabins.",
        "Head smashed against a rock near the lake.",
        "Dragged from hiding and finished with a machete.",
        "Thrown into a cabin wall before the final blow landed.",
        "Caught at the shoreline and pulled back into the darkness.",
    ),
)
