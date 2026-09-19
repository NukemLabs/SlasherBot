from .base import Slasher

PUMPKINHEAD = Slasher(
    key="pumpkinhead",
    name="Pumpkinhead",
    emoji="🎃",
    title="THE VENGEANCE DEMON",
    kill_chance=0.65,
    intro_lines=(
        "Something tall moves between the trees while the night goes completely still.",
        "Claw marks appear in the mud beside a trail that wasn't there a moment ago.",
        "A distant growl rolls through the woods, followed by heavy movement in the dark.",
    ),
    stalk_lines=(
        "Pumpkinhead follows without rushing, as if it already knows where you're going.",
        "A long silhouette moves along the tree line and vanishes behind the next trunk.",
        "The creature's claws scrape across wood somewhere just out of sight.",
    ),
    kill_lines=(
        "{victim} learns that vengeance does not get tired.",
        "{victim} reaches the edge of the woods, but Pumpkinhead is already there.",
        "{victim} discovers the creature has no interest in giving up the hunt.",
    ),
    escape_lines=(
        "{victim} gets beyond the creature's reach before the night closes in again.",
        "{victim} survives as Pumpkinhead disappears back into the woods.",
        "{victim} reaches safety while the growling fades into the distance.",
    ),
    kill_methods=(
        "Caught by Pumpkinhead's claws before reaching safety.",
        "Overpowered by the vengeance demon in the woods.",
        "Cornered after Pumpkinhead cut off the escape route.",
    ),
)
