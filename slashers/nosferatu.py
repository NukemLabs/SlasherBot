from .base import Slasher

NOSFERATU = Slasher(
    key="nosferatu",
    name="Count Orlok",
    emoji="🦇",
    title="NOSFERATU",
    kill_chance=0.61,
    intro_lines=(
        "A tall shadow climbs the wall even though nobody is standing nearby.",
        "Rats scatter from the hallway as an impossibly thin figure appears at the far end.",
        "The room grows colder while a long-fingered shadow reaches across the door.",
    ),
    stalk_lines=(
        "Count Orlok moves slowly through the darkness without making a sound.",
        "His shadow reaches the doorway before he does.",
        "The vampire watches from the end of the corridor as dawn remains painfully far away.",
    ),
    kill_lines=(
        "{victim} does not reach daylight before Count Orlok reaches them.",
        "{victim} watches the shadow cross the room one final time.",
        "{victim} discovers the night lasted just a little too long.",
    ),
    escape_lines=(
        "{victim} reaches the first light of dawn and Orlok retreats.",
        "{victim} gets into the daylight before the vampire can follow.",
        "{victim} survives as sunrise finally breaks across the room.",
    ),
    kill_methods=(
        "Caught by Count Orlok before sunrise.",
        "Overtaken by the vampire in the darkness.",
        "Trapped away from daylight while Orlok closed in.",
    ),
)
