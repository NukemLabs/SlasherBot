from .base import Slasher

MICHAEL = Slasher(
    key="michael",
    name="Michael Myers",
    emoji="🎃",
    title="THE SHAPE",
    kill_chance=0.58,
    intro_lines=(
        "A figure in a white mask is standing where nobody was a moment ago.",
        "Someone notices a pale mask at the far end of the street.",
        "The server goes quiet. Somewhere in the distance, slow footsteps begin.",
    ),
    stalk_lines=(
        "The footsteps stop whenever the victim looks back.",
        "A curtain moves. There is nobody at the window anymore.",
        "He isn't running. He doesn't need to.",
        "The shape disappears behind a doorway... then appears much closer.",
    ),
    kill_lines=(
        "{victim} locked the door. Michael was already inside.",
        "{victim} made it to the porch. The Shape was waiting in the dark.",
        "{victim} looked away for one second. That was enough.",
    ),
    escape_lines=(
        "{victim} reaches safety and looks back. Michael is simply... gone.",
        "{victim} gets away. Across the street, Michael watches without moving.",
        "{victim} slams the door, calls for help, and survives the night.",
    ),
    kill_methods=(
        "Pinned to the wall with a kitchen knife.",
        "Stabbed in the chest in the dark hallway.",
        "Dragged back inside and finished with a silent knife strike.",
        "Caught at the door and slashed before escape was possible.",
        "Lifted off the floor and driven back into the wall.",
    ),
)
