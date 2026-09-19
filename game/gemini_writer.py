from __future__ import annotations

import asyncio
import json
import logging
import os
import random
from collections import defaultdict, deque
from dataclasses import dataclass

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from lore.profiles import KillerLore, get_lore


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class AIHuntScript:
    intro: str
    stalk: str
    reactions: dict[str, str]
    kill_line: str
    escape_line: str
    kill_method: str
    fakeout_line: str

    def reaction_for(self, action_key: str) -> str | None:
        return self.reactions.get(action_key)


class ReactionOutput(BaseModel):
    action: str = Field(
        description="One allowed player action key exactly as supplied in the prompt."
    )
    line: str = Field(
        description="One short killer-specific reaction sentence."
    )


class HuntScriptOutput(BaseModel):
    intro: str = Field(
        description="One very short punchy atmospheric sentence."
    )
    stalk: str = Field(
        description="One short sentence showing the killer stalking {victim}."
    )
    reactions: list[ReactionOutput] = Field(
        description="Exactly one reaction for every allowed player action."
    )
    kill_line: str = Field(
        description="A concise cinematic setup for a kill outcome using {victim}."
    )
    escape_line: str = Field(
        description="A concise cinematic survival outcome using {victim}."
    )
    kill_method: str = Field(
        description="A short cause-of-death description faithful to the killer's weapons and methods."
    )
    fakeout_line: str = Field(
        description="A creepy non-lethal appearance that ends without an attack, using {victim}."
    )


SYSTEM_INSTRUCTION = """
You are the punchy scene writer for a fast Discord horror minigame called The Slasher.

The Python game engine controls all mechanics. You NEVER choose the victim, player
action, survival result, rarity, odds, stats, or timing. You only write flavor text.

STYLE:
- SHORT, FUN, DARK, and immediately readable in Discord.
- Think horror-game notification, not horror novel.
- One sentence per field whenever possible.
- No long setup, no purple prose, no paragraphs.
- Prefer a sharp image, joke, scare, or killer-specific beat.
- Keep the energy moving.

LORE:
- Treat the supplied killer profile as authoritative.
- Never invent weapons, powers, speech habits, or personality traits that conflict with it.
- Silent killers NEVER speak.
- Never copy or closely reproduce movie dialogue. All dialogue must be original.
- Kill methods must fit the killer's weapons or established physical methods.

FORMAT:
- Use the literal placeholder {victim} whenever the victim is mentioned.
- No @everyone, @here, URLs, markdown headings, code blocks, or Discord commands.
- Do not mention AI, prompts, profiles, or game mechanics.
- Horror violence can be cinematic, but avoid detailed gore.
- Return only the requested structured data.
""".strip()


class GeminiWriter:
    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash-lite",
        ).strip()

        self.client = (
            genai.Client(api_key=self.api_key)
            if self.api_key
            else None
        )

        self.last_error: str | None = None

        self._cache: dict[str, deque[AIHuntScript]] = defaultdict(
            lambda: deque(maxlen=8)
        )

    @property
    def available(self) -> bool:
        return self.client is not None

    def status_text(self) -> str:
        if not self.api_key:
            return "Gemini API key not configured."

        if self.last_error:
            # Keep Discord status messages readable instead of dumping a huge API traceback.
            short = self.last_error.replace("\n", " ")
            if len(short) > 180:
                short = short[:177] + "..."
            return f"Configured with **{self.model}**. Last error: `{short}`"

        return f"Configured and ready with **{self.model}**."

    async def generate_script(
        self,
        *,
        killer_key: str,
        action_keys: tuple[str, ...],
        rarity: str,
    ) -> AIHuntScript | None:
        if self.client is None:
            self.last_error = "GEMINI_API_KEY is missing"
            return self._cached(killer_key)

        lore = get_lore(killer_key)
        if lore is None:
            self.last_error = f"No lore profile for {killer_key}"
            return self._cached(killer_key)

        try:
            script = await asyncio.wait_for(
                asyncio.to_thread(
                    self._generate_sync,
                    lore,
                    action_keys,
                    rarity,
                ),
                timeout=12.0,
            )
        except asyncio.TimeoutError:
            self.last_error = "Gemini request timed out"
            logger.warning("Gemini writer timed out for %s.", killer_key)
            return self._cached(killer_key)
        except Exception as exc:
            self.last_error = f"{type(exc).__name__}: {exc}"
            logger.warning(
                "Gemini writer failed for %s: %s",
                killer_key,
                self.last_error,
            )
            return self._cached(killer_key)

        self.last_error = None
        self._cache[killer_key].append(script)
        return script

    def _cached(self, killer_key: str) -> AIHuntScript | None:
        cached = self._cache.get(killer_key)
        if not cached:
            return None
        return random.choice(tuple(cached))

    def _generate_sync(
        self,
        lore: KillerLore,
        action_keys: tuple[str, ...],
        rarity: str,
    ) -> AIHuntScript:
        assert self.client is not None

        profile = {
            "name": lore.name,
            "identity": lore.identity,
            "personality": list(lore.personality),
            "speech_rules": list(lore.speech_rules),
            "weapons": list(lore.weapons),
            "methods": list(lore.methods),
            "settings": list(lore.settings),
            "visual_motifs": list(lore.visual_motifs),
            "lore_rules": list(lore.lore_rules),
        }

        prompt = (
            "Write one fresh hunt script for The Slasher.\n\n"
            f"KILLER PROFILE:\n{json.dumps(profile, indent=2)}\n\n"
            f"Encounter rarity: {rarity}\n"
            f"Allowed player actions: {', '.join(action_keys)}\n\n"
            "Requirements:\n"
            "- reactions must contain exactly one entry for every allowed action.\n"
            "- each reaction object's action value must exactly match an allowed action key.\n"
            "- use {victim} as the victim placeholder.\n"
            "- intro: max 75 characters, one sentence.\n"
            "- stalk: max 105 characters, one sentence.\n"
            "- each reaction: max 85 characters, one sentence.\n"
            "- kill_line: max 95 characters, one sentence.\n"
            "- escape_line: max 95 characters, one sentence.\n"
            "- kill_method: max 65 characters.\n"
            "- fakeout_line: max 95 characters, one sentence.\n"
            "- make it punchy, playful when appropriate, and killer-specific.\n"
            "- avoid flowery descriptions and multiple clauses.\n"
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                # Let the current Google GenAI SDK translate this Pydantic
                # model into the schema dialect supported by Gemini.
                response_schema=HuntScriptOutput,
                max_output_tokens=700,
            ),
        )

        # google-genai may expose an already parsed Pydantic object.
        parsed = getattr(response, "parsed", None)

        if isinstance(parsed, HuntScriptOutput):
            output = parsed
        else:
            if not response.text:
                raise RuntimeError("Gemini returned no text")
            output = HuntScriptOutput.model_validate_json(response.text)

        return self._validate(output, action_keys)

    def _validate(
        self,
        output: HuntScriptOutput,
        action_keys: tuple[str, ...],
    ) -> AIHuntScript:
        def clean(value: str, field: str, limit: int) -> str:
            text = " ".join(value.strip().split())

            if not text:
                raise ValueError(f"{field} was empty")

            text = text.replace("@everyone", "everyone")
            text = text.replace("@here", "here")

            if len(text) > limit:
                shortened = text[:limit]
                if " " in shortened:
                    shortened = shortened.rsplit(" ", 1)[0]
                text = shortened.rstrip(" ,.;:-") + "…"

            return text

        reactions: dict[str, str] = {}

        for item in output.reactions:
            if item.action not in action_keys:
                continue

            reactions[item.action] = clean(
                item.line,
                f"reaction:{item.action}",
                85,
            )

        for action in action_keys:
            if action not in reactions:
                raise ValueError(f"missing reaction for {action}")

        return AIHuntScript(
            intro=clean(output.intro, "intro", 75),
            stalk=clean(output.stalk, "stalk", 105),
            reactions=reactions,
            kill_line=clean(output.kill_line, "kill_line", 95),
            escape_line=clean(output.escape_line, "escape_line", 95),
            kill_method=clean(output.kill_method, "kill_method", 65),
            fakeout_line=clean(output.fakeout_line, "fakeout_line", 95),
        )
