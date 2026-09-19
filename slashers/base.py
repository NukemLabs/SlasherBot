from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True, slots=True)
class Slasher:
    key: str
    name: str
    emoji: str
    title: str
    kill_chance: float
    intro_lines: Sequence[str]
    stalk_lines: Sequence[str]
    kill_lines: Sequence[str]
    escape_lines: Sequence[str]
    kill_methods: Sequence[str]
