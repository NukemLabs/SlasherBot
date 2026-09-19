from __future__ import annotations

import random

import discord

from slashers.base import Slasher


# Extra dialogue lives here so individual killer files do not become enormous.
# The original dialogue in each slasher file remains valid and is mixed with these.
EXTRA_INTROS: dict[str, tuple[str, ...]] = {
    "michael": (
        "A motionless figure is standing beneath a streetlight. When you look again, it's closer.",
        "A porch light flickers. A white mask is visible for half a second.",
        "Someone closes the blinds. A shape is already standing on the other side.",
    ),
    "jason": (
        "The lake is completely still. Then something heavy steps onto the dock.",
        "A cabin door swings open by itself. Muddy footprints lead inside.",
        "Something large moves between the trees without making a sound.",
    ),
    "ghostface": (
        "An unknown number sends one message: 'Don't turn around.'",
        "A phone vibrates on the table. The caller ID simply says UNKNOWN.",
        "Someone in a black robe crosses the hallway and disappears.",
    ),
    "leatherface": (
        "The smell of gasoline hangs in the air. Somewhere nearby, an engine coughs.",
        "A heavy metal door slams shut. Then comes the pull of a chainsaw cord.",
        "Something crashes through the next room, followed by sudden silence.",
    ),
    "chucky": (
        "A toy box opens by itself. Something inside giggles.",
        "A doll-sized footprint appears in the dust, followed by another.",
        "A voice from beneath the furniture mutters something extremely unfriendly.",
    ),
    "spaulding": (
        "A cheap carnival jingle starts playing from somewhere it shouldn't.",
        "A clown-painted sign swings slowly despite there being no wind.",
        "A loud laugh erupts from the next room, followed by sarcastic applause.",
    ),
    "art": (
        "A black balloon drifts through the doorway. Art follows a moment later.",
        "A tiny horn sounds once. Then twice. The second HONK is much closer.",
        "Art is standing in the corner, smiling like he's been there the whole time.",
    ),
    "freddy": (
        "The lights dim. For a second, the walls look like rusted boiler-room pipes.",
        "Someone hears metal blades scraping together just before the room goes quiet.",
        "The clock changes to a time that doesn't exist. Somewhere, Freddy laughs.",
    ),
    "candyman": (
        "A single bee lands on the mirror. Then another. Then hundreds.",
        "The mirror fogs from the inside and a name slowly appears in the glass.",
        "A deep voice whispers from the reflection even though nobody is there.",
    ),
    "pinhead": (
        "The puzzle box turns by itself. Every light in the room dies at once.",
        "A metallic click echoes through the server. Chains answer from somewhere beyond the walls.",
        "The configuration opens one piece at a time. Something on the other side notices.",
    ),
}

EXTRA_STALKS: dict[str, tuple[str, ...]] = {
    "michael": (
        "Every time you check behind you, Michael is standing a few feet closer.",
        "You lock one door. A different door slowly opens.",
        "The Shape stands perfectly still until you blink.",
    ),
    "jason": (
        "A machete blade catches the moonlight between the trees.",
        "The cabin floor creaks under footsteps far too heavy to be yours.",
        "You hear water dripping. Jason is standing at the end of the dock.",
    ),
    "ghostface": (
        "The phone rings. When you answer, your own breathing comes through the speaker.",
        "Ghostface trips over something, recovers, and keeps coming.",
        "A knife flashes around the corner before the figure disappears again.",
    ),
    "leatherface": (
        "The chainsaw dies for a moment. The silence is somehow worse.",
        "Leatherface crashes through a door instead of bothering to open it.",
        "The engine roars while furniture gets thrown out of the way.",
    ),
    "chucky": (
        "You hear a tiny voice swear from somewhere under the bed.",
        "A cabinet door opens at floor level. Chucky is no longer where you left him.",
        "Small footsteps circle the room faster than you can track them.",
    ),
    "spaulding": (
        "Spaulding keeps insulting your escape plan while casually following you.",
        "He whistles, laughs, and points toward an exit that is obviously a terrible idea.",
        "The taunting suddenly stops. That is much worse.",
    ),
    "art": (
        "Art holds up a handwritten sign that simply says 'RUN.'",
        "He mimes an elaborate death scene, bows, then points directly at you.",
        "Art produces an absurdly large weapon from a bag that should not be able to hold it.",
    ),
    "freddy": (
        "Every exit leads back to the same boiler room.",
        "Freddy appears at the end of the hallway and casually taps his blades together.",
        "You wake up for half a second... then realize that was part of the dream too.",
    ),
    "candyman": (
        "Your reflection looks over its shoulder before you do.",
        "The buzzing gets louder every time you get closer to an exit.",
        "Candyman's silhouette appears behind you in the mirror, but not in the room.",
    ),
    "pinhead": (
        "Hooks hang motionless in the air, waiting.",
        "The walls peel away into darkness while Pinhead watches without moving.",
        "The box clicks again. More chains begin sliding across the floor.",
    ),
}

EXTRA_KILLS: dict[str, tuple[str, ...]] = {
    "michael": (
        "{victim} thought the locked door bought them time. It didn't.",
        "{victim} made it outside. Michael was already waiting.",
    ),
    "jason": (
        "{victim} reached the dock and discovered there was nowhere left to go.",
        "{victim} hid in the cabin. Jason did not bother using the door.",
    ),
    "ghostface": (
        "{victim} finally stopped the phone from ringing.",
        "{victim} fought hard, but Ghostface got the last surprise.",
    ),
    "leatherface": (
        "{victim} could hear the road just beyond the fence.",
        "{victim} found an exit. Leatherface found it first.",
    ),
    "chucky": (
        "{victim} laughed at the doll exactly once.",
        "{victim} remembered too late that small doesn't mean harmless.",
    ),
    "spaulding": (
        "{victim} finally stopped hearing Spaulding laugh.",
        "{victim} followed the clown's directions. That was the mistake.",
    ),
    "art": (
        "{victim} saw Art reach into the bag one final time.",
        "{victim} got one last cheerful wave from Art.",
    ),
    "freddy": (
        "{victim} almost woke up.",
        "{victim} heard the alarm clock. Freddy heard it too.",
    ),
    "candyman": (
        "{victim} watched the reflection step through the glass.",
        "{victim} finally understood why nobody says the name.",
    ),
    "pinhead": (
        "{victim} solved most of the configuration. Most wasn't enough.",
        "{victim} discovered there are doors that should never be opened.",
    ),
}

EXTRA_ESCAPES: dict[str, tuple[str, ...]] = {
    "michael": (
        "{victim} reaches the street. Michael stops at the edge of the darkness and watches.",
        "{victim} survives. When the police arrive, there is nobody there.",
    ),
    "jason": (
        "{victim} gets across the lake. Jason simply watches from the opposite shore.",
        "{victim} reaches the road as the woods fall silent behind them.",
    ),
    "ghostface": (
        "{victim} knocks Ghostface down long enough to get away.",
        "{victim} escapes. A final UNKNOWN CALL flashes on the phone, then stops.",
    ),
    "leatherface": (
        "{victim} reaches the road and does not look back at the house.",
        "{victim} squeezes through an opening Leatherface cannot follow through.",
    ),
    "chucky": (
        "{victim} locks Chucky in the room and runs before he can find another way out.",
        "{victim} sends Chucky flying and wisely does not wait to see where he lands.",
    ),
    "spaulding": (
        "{victim} gets away while Spaulding is still shouting insults from the doorway.",
        "{victim} escapes. Spaulding responds with an extremely rude farewell.",
    ),
    "art": (
        "{victim} escapes. Art gives an enthusiastic thumbs-up like this was all great fun.",
        "{victim} survives. Art silently throws a tantrum, then honks the horn once.",
    ),
    "freddy": (
        "{victim} wakes up gasping. The room is normal again... mostly.",
        "{victim} forces the nightmare apart and wakes before Freddy can reach them.",
    ),
    "candyman": (
        "{victim} backs away from the mirror until the bees finally disappear.",
        "{victim} survives. Their reflection returns to normal a second later.",
    ),
    "pinhead": (
        "{victim} snaps the configuration shut. Every chain drops at once.",
        "{victim} closes the doorway with seconds to spare.",
    ),
}


FAKEOUT_LINES: dict[str, tuple[str, ...]] = {
    "michael": (
        "{victim} looks outside and sees Michael standing beneath a streetlight. A car passes between them. He is gone.",
        "Michael watches {victim} from across the street for several minutes... then simply disappears.",
    ),
    "jason": (
        "{victim} hears footsteps circling the cabin. By the time the door opens, the woods are empty.",
        "A hockey mask appears between the trees behind {victim}. Moments later, there is nothing there.",
    ),
    "ghostface": (
        "{victim}'s phone rings. A distorted voice whispers, 'Wrong number.' The call ends.",
        "Ghostface appears behind {victim} for one terrifying second, then runs off before attacking.",
    ),
    "leatherface": (
        "A chainsaw roars near {victim}, sputters, and dies. Whoever started it never appears.",
        "{victim} hears Leatherface crash through the next room... then the sound moves away.",
    ),
    "chucky": (
        "{victim} hears a tiny laugh beneath the table. When they look, only a toy knife is left behind.",
        "Chucky waves at {victim} from the doorway, flips them off, and vanishes.",
    ),
    "spaulding": (
        "Spaulding spends thirty seconds insulting {victim}, laughs at his own joke, and leaves.",
        "{victim} hears a clown laughing outside the door. Nobody ever comes in.",
    ),
    "art": (
        "Art silently approaches {victim}, raises a tiny horn... HONK... then walks away.",
        "Art points at {victim}, pretends to slash his throat, laughs silently, and disappears around the corner.",
    ),
    "freddy": (
        "{victim} jolts awake after seeing Freddy at the foot of the bed. The clock says only one minute passed.",
        "Freddy whispers to {victim} from inside a dream, then snaps his fingers and vanishes.",
    ),
    "candyman": (
        "{victim}'s reflection smiles without them. A swarm of bees appears, then dissolves into nothing.",
        "Candyman appears behind {victim} in the mirror but never steps through.",
    ),
    "pinhead": (
        "The configuration opens in front of {victim}. Pinhead looks through the doorway... and closes it himself.",
        "Chains surround {victim} but stop inches away. The box snaps shut and everything vanishes.",
    ),
    "pumpkinhead": (
        "Pumpkinhead watches {victim} from the tree line, then disappears back into the woods.",
    ),
    "jack": (
        "{victim} hears an axe strike the door once. When it opens, the hotel corridor is empty.",
    ),
    "pennywise": (
        "A red balloon stops beside {victim}. It pops, and the laughter immediately stops.",
    ),
    "norman": (
        "{victim} sees someone watching from the Bates house window. The curtain closes.",
    ),
    "xenomorph": (
        "The motion tracker spikes beside {victim}, then the signal disappears into the vents.",
    ),
    "klowns": (
        "A Killer Klown waves at {victim}, honks once, and walks back into the glowing circus tent.",
    ),
    "deadites": (
        "A Deadite laughs through the cabin wall at {victim}, then the voice abruptly goes silent.",
    ),
    "jigsaw": (
        "Billy appears on a screen in front of {victim}. The timer reads 00:00, then the monitor shuts off.",
    ),
    "leprechaun": (
        "The Leprechaun checks {victim}'s pockets, finds no gold, mutters angrily, and leaves.",
    ),
    "thing": (
        "Someone identical to {victim}'s friend watches from across the station, then calmly walks away.",
    ),
    "nosferatu": (
        "Count Orlok's shadow reaches toward {victim}, but the first hint of dawn makes it retreat.",
    ),
}


SPECIAL_WARNING_TITLES: dict[str, str] = {
    "art": "🤡 SOMETHING IS SMILING...",
    "freddy": "🔥 DON'T FALL ASLEEP...",
    "candyman": "🐝 DON'T LOOK IN THE MIRROR...",
    "pinhead": "⛓️ THE CONFIGURATION HAS OPENED",
    "pumpkinhead": "🎃 VENGEANCE HAS BEEN SUMMONED...",
    "jack": "🪓 THE OVERLOOK IS NOT EMPTY...",
    "pennywise": "🎈 YOU'LL FLOAT TOO...",
    "xenomorph": "👽 MOTION DETECTED...",
    "klowns": "🤡 THE CIRCUS HAS ARRIVED...",
    "deadites": "📕 SOMETHING READ FROM THE BOOK...",
    "jigsaw": "🧩 A GAME HAS BEGUN...",
    "leprechaun": "🍀 SOMEBODY TOOK HIS GOLD...",
    "thing": "🧬 SOMEONE HERE ISN'T HUMAN...",
    "nosferatu": "🦇 THE SHADOW IS MOVING...",
}


def _combined(
    base: tuple[str, ...] | list[str],
    extras: dict[str, tuple[str, ...]],
    slasher_key: str,
) -> tuple[str, ...]:
    return tuple(base) + extras.get(slasher_key, ())


def pick_intro(slasher: Slasher) -> str:
    return random.choice(_combined(slasher.intro_lines, EXTRA_INTROS, slasher.key))


def pick_stalk(slasher: Slasher) -> str:
    return random.choice(_combined(slasher.stalk_lines, EXTRA_STALKS, slasher.key))


def pick_kill_line(slasher: Slasher, victim_mention: str) -> str:
    line = random.choice(_combined(slasher.kill_lines, EXTRA_KILLS, slasher.key))
    return line.format(victim=victim_mention)


def pick_escape_line(slasher: Slasher, victim_mention: str) -> str:
    line = random.choice(_combined(slasher.escape_lines, EXTRA_ESCAPES, slasher.key))
    return line.format(victim=victim_mention)


def warning_title(slasher_key: str, rarity: str) -> str:
    if slasher_key in SPECIAL_WARNING_TITLES:
        return SPECIAL_WARNING_TITLES[slasher_key]
    if rarity == "Rare":
        return "🩸 SOMETHING RARE IS STALKING THE SERVER..."
    if rarity == "Very Rare":
        return "⛓️ SOMETHING IMPOSSIBLE HAS ARRIVED..."
    if rarity == "Uncommon":
        return "⚠️ SOMETHING IS MOVING IN THE DARK..."
    return "🔪 SOMETHING IS WRONG..."


def rarity_footer(rarity: str) -> str:
    if rarity == "Very Rare":
        return "VERY RARE ENCOUNTER • Something has entered the server."
    if rarity == "Rare":
        return "RARE ENCOUNTER • Something has entered the server."
    if rarity == "Uncommon":
        return "UNCOMMON ENCOUNTER • Something has entered the server."
    return "Something has entered the server."


def rarity_color(rarity: str) -> discord.Color:
    if rarity == "Very Rare":
        return discord.Color.purple()
    if rarity == "Rare":
        return discord.Color.gold()
    if rarity == "Uncommon":
        return discord.Color.dark_orange()
    return discord.Color.dark_red()


def survival_bonus_text(rarity: str) -> str:
    if rarity == "Very Rare":
        return "\n\n⛓️ **VERY RARE ENCOUNTER SURVIVED**"
    if rarity == "Rare":
        return "\n\n🩸 **RARE ENCOUNTER SURVIVED**"
    return ""


def fakeout_text(slasher_key: str, victim_mention: str) -> str | None:
    lines = FAKEOUT_LINES.get(slasher_key)
    if not lines:
        return None
    return random.choice(lines).format(victim=victim_mention)


def fakeout_title(slasher: Slasher) -> str:
    return f"{slasher.emoji} FALSE ALARM... MAYBE"


def should_fakeout(slasher_override: Slasher | None) -> bool:
    # Specific-killer test hunts should always run fully.
    if slasher_override is not None:
        return False

    # About 1 in 12 random hunts turns into a creepy one-message appearance.
    return random.random() < 0.08
