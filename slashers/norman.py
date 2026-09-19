from .base import Slasher

NORMAN = Slasher(
    key="norman",
    name="Norman Bates",
    emoji="🚿",
    title="THE BATES MOTEL",
    kill_chance=0.49,
    intro_lines=(
        "The Bates Motel office light turns on even though nobody entered.",
        "A silhouette appears in the upstairs window of the house behind the motel.",
        "Water starts running in an empty motel bathroom.",
    ),
    stalk_lines=(
        "Norman watches from behind the motel-office curtain.",
        "A shadow crosses the bathroom door while the shower keeps running.",
        "Someone moves between the motel rooms without turning on a single light.",
    ),
    kill_lines=(
        "{victim} should have checked out of the Bates Motel sooner.",
        "{victim} hears the bathroom door open behind them.",
        "{victim} discovers the motel has one guest too many.",
    ),
    escape_lines=(
        "{victim} gets the motel-room door open and runs for the highway.",
        "{victim} slips past Norman and leaves the Bates Motel behind.",
        "{victim} reaches the car before the upstairs silhouette moves again.",
    ),
    kill_methods=(
        "Caught in the motel by Norman with a kitchen knife.",
        "Ambushed after ignoring the movement behind the bathroom door.",
        "Cornered inside a Bates Motel room.",
    ),
)
