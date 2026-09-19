from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ActionResult:
    key: str
    label: str
    emoji: str
    description: str


ACTIONS: dict[str, ActionResult] = {
    "run": ActionResult(
        key="run",
        label="RUN",
        emoji="🏃",
        description="You bolt for the nearest way out.",
    ),
    "hide": ActionResult(
        key="hide",
        label="HIDE",
        emoji="🫥",
        description="You disappear into the nearest hiding place.",
    ),
    "fight": ActionResult(
        key="fight",
        label="FIGHT",
        emoji="👊",
        description="You decide you're not going down without a fight.",
    ),
    "solve_box": ActionResult(
        key="solve_box",
        label="SOLVE THE BOX",
        emoji="🧩",
        description="You grab the configuration and try to reverse what was opened.",
    ),
    "beg": ActionResult(
        key="beg",
        label="BEG",
        emoji="🙏",
        description="You stop running and plead for another way out.",
    ),
    "wake_up": ActionResult(
        key="wake_up",
        label="WAKE UP",
        emoji="⏰",
        description="You fight the dream and force yourself to wake up.",
    ),
    "say_name": ActionResult(
        key="say_name",
        label="SAY HIS NAME",
        emoji="🪞",
        description="You face the mirror and call Candyman by name.",
    ),
    "stay_silent": ActionResult(
        key="stay_silent",
        label="STAY SILENT",
        emoji="🤫",
        description="You refuse to speak and slowly back away from the mirror.",
    ),
    "face_fear": ActionResult(
        key="face_fear",
        label="FACE YOUR FEAR",
        emoji="🎈",
        description="You stop running and refuse to feed Pennywise your fear.",
    ),
    "look_away": ActionResult(
        key="look_away",
        label="LOOK AWAY",
        emoji="🙈",
        description="You refuse to look directly at what Pennywise is showing you.",
    ),
    "stay_quiet": ActionResult(
        key="stay_quiet",
        label="STAY QUIET",
        emoji="🤫",
        description="You stop moving and try not to draw the Xenomorph's attention.",
    ),
    "pop_nose": ActionResult(
        key="pop_nose",
        label="HIT THE NOSE",
        emoji="🔴",
        description="You aim for the Klown's bright red weak point.",
    ),
    "recite_passage": ActionResult(
        key="recite_passage",
        label="RECITE THE PASSAGE",
        emoji="📕",
        description="You use the book and try to send the evil back.",
    ),
    "play_game": ActionResult(
        key="play_game",
        label="PLAY THE GAME",
        emoji="⏱️",
        description="You stop panicking and work through Jigsaw's instructions.",
    ),
    "panic": ActionResult(
        key="panic",
        label="PANIC",
        emoji="😱",
        description="You pull at everything at once while the timer keeps falling.",
    ),
    "cheat": ActionResult(
        key="cheat",
        label="CHEAT",
        emoji="🛠️",
        description="You try to bypass the intended solution.",
    ),
    "return_gold": ActionResult(
        key="return_gold",
        label="RETURN THE GOLD",
        emoji="🪙",
        description="You give the Leprechaun exactly what he came for.",
    ),
    "test_blood": ActionResult(
        key="test_blood",
        label="TEST THE BLOOD",
        emoji="🧪",
        description="You test the group before trusting anyone.",
    ),
    "trust_someone": ActionResult(
        key="trust_someone",
        label="TRUST SOMEONE",
        emoji="🤝",
        description="You pick someone who still looks human and hope you're right.",
    ),
    "find_sunlight": ActionResult(
        key="find_sunlight",
        label="FIND SUNLIGHT",
        emoji="☀️",
        description="You make a desperate move toward the first light of dawn.",
    ),
    "freeze": ActionResult(
        key="freeze",
        label="DO NOTHING",
        emoji="😨",
        description="Fear takes over. You hesitate for too long.",
    ),
}


CHOICE_SETS: dict[str, tuple[str, ...]] = {
    "pinhead": ("solve_box", "run", "beg"),
    "freddy": ("wake_up", "run", "fight"),
    "candyman": ("stay_silent", "run", "say_name"),
    "pennywise": ("face_fear", "run", "look_away"),
    "xenomorph": ("stay_quiet", "run", "fight"),
    "klowns": ("pop_nose", "run", "hide"),
    "deadites": ("recite_passage", "run", "fight"),
    "jigsaw": ("play_game", "panic", "cheat"),
    "leprechaun": ("return_gold", "run", "fight"),
    "thing": ("test_blood", "run", "trust_someone"),
    "nosferatu": ("find_sunlight", "run", "hide"),
}

DEFAULT_CHOICES = ("run", "hide", "fight")


def choices_for_slasher(slasher_key: str) -> tuple[str, ...]:
    return CHOICE_SETS.get(slasher_key, DEFAULT_CHOICES)


def choice_footer(slasher_key: str) -> str:
    if slasher_key == "pinhead":
        return "30 seconds to SOLVE THE BOX, RUN, or BEG."
    if slasher_key == "freddy":
        return "30 seconds to WAKE UP, RUN, or FIGHT."
    if slasher_key == "candyman":
        return "30 seconds to STAY SILENT, RUN, or SAY HIS NAME."
    if slasher_key == "pennywise":
        return "30 seconds to FACE YOUR FEAR, RUN, or LOOK AWAY."
    if slasher_key == "xenomorph":
        return "30 seconds to STAY QUIET, RUN, or FIGHT."
    if slasher_key == "klowns":
        return "30 seconds to HIT THE NOSE, RUN, or HIDE."
    if slasher_key == "deadites":
        return "30 seconds to RECITE THE PASSAGE, RUN, or FIGHT."
    if slasher_key == "jigsaw":
        return "30 seconds to PLAY THE GAME, PANIC, or CHEAT."
    if slasher_key == "leprechaun":
        return "30 seconds to RETURN THE GOLD, RUN, or FIGHT."
    if slasher_key == "thing":
        return "30 seconds to TEST THE BLOOD, RUN, or TRUST SOMEONE."
    if slasher_key == "nosferatu":
        return "30 seconds to FIND SUNLIGHT, RUN, or HIDE."
    return "30 seconds to RUN, HIDE, or FIGHT."


# Positive numbers make death MORE likely.
# Negative numbers make death LESS likely.
KILL_CHANCE_MODIFIERS: dict[str, dict[str, float]] = {
    "michael": {
        "run": -0.08,
        "hide": +0.12,
        "fight": +0.05,
        "freeze": +0.10,
    },
    "jason": {
        "run": +0.08,
        "hide": -0.10,
        "fight": +0.15,
        "freeze": +0.10,
    },
    "ghostface": {
        "run": -0.02,
        "hide": +0.05,
        "fight": -0.20,
        "freeze": +0.12,
    },
    "art": {
        "run": 0.00,
        "hide": 0.00,
        "fight": 0.00,
        "freeze": +0.10,
    },
    "pinhead": {
        "solve_box": -0.25,
        "run": +0.18,
        "beg": +0.08,
        "freeze": +0.20,
    },
    "spaulding": {
        "run": -0.08,
        "hide": +0.08,
        "fight": +0.04,
        "freeze": +0.12,
    },
    "freddy": {
        "wake_up": -0.24,
        "run": +0.14,
        "fight": +0.08,
        "freeze": +0.20,
    },
    "leatherface": {
        "run": +0.12,
        "hide": -0.10,
        "fight": +0.16,
        "freeze": +0.12,
    },
    "chucky": {
        "run": -0.04,
        "hide": +0.08,
        "fight": -0.18,
        "freeze": +0.12,
    },
    "candyman": {
        "stay_silent": -0.22,
        "run": +0.05,
        "say_name": +0.20,
        "freeze": +0.16,
    },
    "pumpkinhead": {
        "run": +0.06, "hide": -0.04, "fight": +0.12, "freeze": +0.16,
    },
    "jack": {
        "run": -0.08, "hide": -0.03, "fight": +0.07, "freeze": +0.12,
    },
    "pennywise": {
        "face_fear": -0.25, "run": +0.12, "look_away": -0.05, "freeze": +0.22,
    },
    "norman": {
        "run": -0.08, "hide": +0.05, "fight": -0.08, "freeze": +0.12,
    },
    "xenomorph": {
        "stay_quiet": -0.18, "run": +0.12, "fight": +0.20, "freeze": +0.16,
    },
    "klowns": {
        "pop_nose": -0.24, "run": +0.03, "hide": +0.05, "freeze": +0.14,
    },
    "deadites": {
        "recite_passage": -0.20, "run": +0.06, "fight": +0.04, "freeze": +0.18,
    },
    "jigsaw": {
        "play_game": -0.22, "panic": +0.22, "cheat": +0.08, "freeze": +0.25,
    },
    "leprechaun": {
        "return_gold": -0.26, "run": +0.06, "fight": +0.10, "freeze": +0.16,
    },
    "thing": {
        "test_blood": -0.22, "run": +0.06, "trust_someone": +0.18, "freeze": +0.18,
    },
    "nosferatu": {
        "find_sunlight": -0.26, "run": +0.04, "hide": +0.14, "freeze": +0.18,
    },
}


REACTION_LINES: dict[str, dict[str, tuple[str, ...]]] = {
    "michael": {
        "run": (
            "You run. Behind you, Michael just keeps walking.",
            "You sprint for the exit. The footsteps never speed up... but they never stop.",
        ),
        "hide": (
            "You hide and hold your breath. Michael stops just outside.",
            "The room goes silent. A shadow passes beneath the door.",
        ),
        "fight": (
            "You grab the nearest weapon and turn around. Michael doesn't flinch.",
            "You stand your ground. The Shape tilts his head.",
        ),
        "freeze": (
            "You hesitate. Michael keeps getting closer.",
            "You wait one second too long.",
        ),
    },
    "jason": {
        "run": (
            "You run for the road. Jason cuts through the trees after you.",
            "You sprint away from the lake. Heavy footsteps follow.",
        ),
        "hide": (
            "You duck into hiding and stay perfectly still.",
            "Jason passes nearby. For the moment, he doesn't see you.",
        ),
        "fight": (
            "You turn and fight. Jason barely reacts.",
            "You swing first. Jason keeps coming.",
        ),
        "freeze": (
            "You freeze. Jason closes the distance.",
            "You lose precious seconds deciding what to do.",
        ),
    },
    "ghostface": {
        "run": (
            "You take off running. Ghostface immediately gives chase.",
            "You bolt for the exit and hear Ghostface stumble behind you.",
        ),
        "hide": (
            "You hide. A phone starts ringing somewhere dangerously close.",
            "You duck out of sight, but Ghostface starts checking every room.",
        ),
        "fight": (
            "You turn and swing. Ghostface was not expecting that.",
            "You fight back and Ghostface crashes into the nearest wall.",
        ),
        "freeze": (
            "You hesitate. Ghostface takes advantage immediately.",
            "You freeze when the phone rings again.",
        ),
    },
    "art": {
        "run": (
            "You run. Art enthusiastically waves goodbye... then starts following.",
            "You sprint away. Behind you comes one tiny, ridiculous HONK.",
        ),
        "hide": (
            "You hide. Art slowly peeks around the corner and silently grins.",
            "You stay perfectly still. A tiny horn sounds right outside.",
        ),
        "fight": (
            "You swing at Art. He looks offended for about half a second.",
            "You fight back. Art pauses, applauds silently, then reaches into his bag.",
        ),
        "freeze": (
            "You freeze. Art points at you, then pretends to check an invisible watch.",
            "You wait too long. Art gives you an exaggerated disappointed look.",
        ),
    },
    "pinhead": {
        "solve_box": (
            "You twist the final section. The chains suddenly hesitate.",
            "The box clicks into a new configuration. Pinhead watches in silence.",
            "You force the mechanism backward. The doorway begins to flicker.",
        ),
        "run": (
            "You run. Chains tear across the room after you.",
            "You bolt for the door, but the hallway seems to stretch endlessly.",
        ),
        "beg": (
            "You plead for mercy. Pinhead regards you with cold amusement.",
            "You beg for another chance. The chains continue to move.",
        ),
        "freeze": (
            "You stare at the open configuration as the chains draw closer.",
            "You hesitate while the doorway opens wider.",
        ),
    },
    "spaulding": {
        "run": (
            "You bolt while Spaulding is still laughing at his own joke.",
            "You make a break for the door. Spaulding shouts after you and gives chase.",
        ),
        "hide": (
            "You hide. Spaulding loudly announces that this is getting boring.",
            "You duck out of sight while Spaulding starts checking rooms and heckling you.",
        ),
        "fight": (
            "You swing first. Spaulding stumbles back, then looks genuinely offended.",
            "You decide to fight. Spaulding's grin disappears for just a second.",
        ),
        "freeze": (
            "You hesitate. Spaulding laughs and starts closing the distance.",
            "You stand there too long while Spaulding keeps taunting you.",
        ),
    },
    "freddy": {
        "wake_up": (
            "You focus on the real world. The nightmare begins to crack apart.",
            "You force your eyes open as Freddy reaches for you.",
            "You fight the dream itself. Freddy's grin starts to fade.",
        ),
        "run": (
            "You run, but the hallway keeps stretching farther ahead.",
            "You sprint through the nightmare while Freddy strolls behind you laughing.",
        ),
        "fight": (
            "You turn and swing. Freddy laughs like this is exactly what he wanted.",
            "You fight back, but nothing in this dream obeys normal rules.",
        ),
        "freeze": (
            "You freeze as Freddy's blades scrape slowly across the wall.",
            "You hesitate. The nightmare closes in around you.",
        ),
    },
    "leatherface": {
        "run": (
            "You sprint for the road as the chainsaw screams behind you.",
            "You run. Leatherface crashes through everything between you and the exit.",
        ),
        "hide": (
            "You duck into a cramped hiding place while the chainsaw passes nearby.",
            "You stay silent as Leatherface storms through the next room.",
        ),
        "fight": (
            "You turn to fight. Leatherface answers by revving the chainsaw.",
            "You stand your ground. Leatherface charges straight at you.",
        ),
        "freeze": (
            "You hesitate. The chainsaw gets louder.",
            "You lose precious seconds while Leatherface closes the distance.",
        ),
    },
    "chucky": {
        "run": (
            "You take off running. Tiny footsteps race after you.",
            "You bolt for the door while Chucky screams insults behind you.",
        ),
        "hide": (
            "You hide. Unfortunately, Chucky can fit almost anywhere.",
            "You duck out of sight and hear tiny footsteps searching the room.",
        ),
        "fight": (
            "You turn and kick Chucky across the room. He is absolutely furious.",
            "You fight back. Chucky goes flying, then immediately starts getting back up.",
        ),
        "freeze": (
            "You hesitate. Chucky takes advantage of every second.",
            "You freeze while a tiny laugh comes from beneath you.",
        ),
    },
    "candyman": {
        "stay_silent": (
            "You refuse to speak. The bees slowly begin to disperse.",
            "You stay silent and step away from the mirror. The reflection hesitates.",
            "You say nothing. Candyman watches from inside the glass.",
        ),
        "run": (
            "You run, but the sound of bees follows you through the hallway.",
            "You bolt from the mirror while the swarm pours into the room.",
        ),
        "say_name": (
            "You say his name. The reflection smiles.",
            "You call Candyman by name. The mirror ripples like water.",
            "You speak the name aloud. Something steps closer on the other side.",
        ),
        "freeze": (
            "You stare into the mirror while the swarm grows louder.",
            "You hesitate as a figure takes shape behind your reflection.",
        ),
    },
    "pumpkinhead": {
        "run": ("You run. Pumpkinhead follows without hurrying.",),
        "hide": ("You hide while claws scrape slowly past the wall.",),
        "fight": ("You turn to fight. Pumpkinhead barely slows down.",),
        "freeze": ("You hesitate, and the growling gets closer.",),
    },
    "jack": {
        "run": ("You sprint down the hotel corridor while Jack gives chase.",),
        "hide": ("You duck into a room as Jack drags the axe past the door.",),
        "fight": ("You stand your ground. Jack raises the axe again.",),
        "freeze": ("You hesitate while the next axe strike lands closer.",),
    },
    "pennywise": {
        "face_fear": ("You stop running and refuse to be afraid. Pennywise's smile flickers.",),
        "run": ("You run. The hallway bends and puts Pennywise ahead of you again.",),
        "look_away": ("You shut out the illusion, but the laughter keeps moving closer.",),
        "freeze": ("Fear takes over. Pennywise notices immediately.",),
    },
    "norman": {
        "run": ("You bolt from the motel room and head for the highway.",),
        "hide": ("You hide while footsteps stop outside the bathroom door.",),
        "fight": ("You turn on Norman before he can surprise you.",),
        "freeze": ("You hesitate as the bathroom door begins to open.",),
    },
    "xenomorph": {
        "stay_quiet": ("You stop moving. The Xenomorph pauses in the vent above you.",),
        "run": ("You sprint down the corridor as the motion tracker screams.",),
        "fight": ("You fight back, but getting close to the Xenomorph is its own problem.",),
        "freeze": ("You freeze while something lowers itself from the ceiling.",),
    },
    "klowns": {
        "pop_nose": ("You aim for the bright red nose. The Klown suddenly looks worried.",),
        "run": ("You run while colorful ray blasts hit everything behind you.",),
        "hide": ("You hide as oversized shoes squeak past the doorway.",),
        "freeze": ("You hesitate. A Klown waves and raises the ray gun.",),
    },
    "deadites": {
        "recite_passage": ("You begin the passage. The Deadites immediately stop laughing.",),
        "run": ("You run as the cabin erupts with voices behind you.",),
        "fight": ("You fight back while the Deadite taunts you the entire time.",),
        "freeze": ("You hesitate, and another possessed voice joins the room.",),
    },
    "jigsaw": {
        "play_game": ("You focus on the instructions instead of the timer.",),
        "panic": ("You panic and pull at the mechanism while the timer keeps falling.",),
        "cheat": ("You try to bypass the game. Somewhere, another lock clicks.",),
        "freeze": ("You do nothing. The timer does not care.",),
    },
    "leprechaun": {
        "return_gold": ("You return the gold. The Leprechaun immediately starts counting it.",),
        "run": ("You run while angry rhyming follows close behind.",),
        "fight": ("You fight back. The Leprechaun is small, furious, and extremely persistent.",),
        "freeze": ("You hesitate while another gold coin disappears from your pocket.",),
    },
    "thing": {
        "test_blood": ("You heat the wire and begin testing. Everyone suddenly looks nervous.",),
        "run": ("You run into the snow without knowing which person follows.",),
        "trust_someone": ("You choose someone to trust. They smile just a little too calmly.",),
        "freeze": ("You hesitate while every face in the room watches you.",),
    },
    "nosferatu": {
        "find_sunlight": ("You race toward the first light of dawn. Orlok recoils from the doorway.",),
        "run": ("You run while Orlok's shadow stretches along the wall beside you.",),
        "hide": ("You hide in the dark, exactly where Orlok is strongest.",),
        "freeze": ("You hesitate as the vampire's shadow reaches your feet.",),
    },
}


def adjusted_kill_chance(slasher_key: str, base_chance: float, action_key: str) -> float:
    modifier = KILL_CHANCE_MODIFIERS.get(slasher_key, {}).get(action_key, 0.0)

    # Art is intentionally unpredictable.
    if slasher_key == "art":
        modifier += random.uniform(-0.15, 0.15)

    # Solving the box is Pinhead's best option, but the configuration is still
    # dangerous and can sometimes turn against the player.
    if slasher_key == "pinhead" and action_key == "solve_box":
        modifier += random.choice((-0.10, -0.05, 0.00, 0.08))

    if slasher_key == "freddy" and action_key == "wake_up":
        modifier += random.choice((-0.08, -0.03, 0.00, 0.06))

    if slasher_key == "candyman" and action_key == "stay_silent":
        modifier += random.choice((-0.06, -0.02, 0.00, 0.04))

    if slasher_key == "candyman" and action_key == "say_name":
        modifier += random.choice((0.00, 0.04, 0.08))

    if slasher_key == "pennywise" and action_key == "face_fear":
        modifier += random.choice((-0.08, -0.03, 0.00, 0.04))

    if slasher_key == "jigsaw" and action_key == "play_game":
        modifier += random.choice((-0.06, -0.02, 0.00, 0.05))

    if slasher_key == "thing" and action_key == "test_blood":
        modifier += random.choice((-0.06, -0.02, 0.00, 0.05))

    return max(0.05, min(0.95, base_chance + modifier))


def reaction_lines(slasher_key: str, action_key: str) -> tuple[str, ...]:
    return REACTION_LINES.get(slasher_key, {}).get(
        action_key,
        ("The Slasher watches your move.",),
    )
