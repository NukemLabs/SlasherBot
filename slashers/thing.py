from .base import Slasher

THING = Slasher(
    key="thing",
    name="The Thing",
    emoji="🧬",
    title="WHO GOES THERE?",
    kill_chance=0.66,
    intro_lines=(
        "Someone at the station is acting completely normal. That is the problem.",
        "A blood sample moves when nobody is touching it.",
        "The radio goes silent while footsteps cross the snow outside.",
    ),
    stalk_lines=(
        "Every person in the room looks human. One of them is not.",
        "Something shifts beneath a familiar face before becoming still again.",
        "The station lights fail just as the blood-test equipment disappears.",
    ),
    kill_lines=(
        "{victim} trusts the wrong person at the station.",
        "{victim} discovers the imitation only after it is too close.",
        "{victim} never finds out which face stopped being human.",
    ),
    escape_lines=(
        "{victim} catches the imitation before it can get close.",
        "{victim} uses the blood test and gets away from the infected group.",
        "{victim} reaches the snowcat while everyone else keeps watching one another.",
    ),
    kill_methods=(
        "Assimilated after trusting the wrong person.",
        "Caught when the imitation revealed itself at close range.",
        "Overtaken by The Thing inside the isolated station.",
    ),
)
