from __future__ import annotations

import io
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = ROOT / "assets" / "slasher_vhs_frame.png"


def _font_candidates(*, bold: bool = False, mono: bool = False) -> tuple[str, ...]:
    if mono:
        return (
            "C:/Windows/Fonts/consolab.ttf"
            if bold
            else "C:/Windows/Fonts/consola.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
            if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        )

    if bold:
        return (
            "C:/Windows/Fonts/impact.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        )

    return (
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )


def _font(
    size: int,
    *,
    bold: bool = False,
    mono: bool = False,
) -> ImageFont.ImageFont:
    for candidate in _font_candidates(bold=bold, mono=mono):
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue

    # Railway/Linux may not have every system font installed.
    # Pillow can still provide a scalable built-in fallback.
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _clean(text: str) -> str:
    text = text.replace("**", "").replace("*", "").replace("`", "")
    text = text.replace("@everyone", "everyone").replace("@here", "here")
    return re.sub(r"\s+", " ", text).strip()


def _text_width(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def _fit_single_line_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    *,
    max_width: int,
    start_size: int,
    min_size: int,
    bold: bool = False,
    mono: bool = False,
) -> ImageFont.ImageFont:
    size = start_size

    while size > min_size:
        font = _font(
            size,
            bold=bold,
            mono=mono,
        )

        if _text_width(draw, text, font) <= max_width:
            return font

        size -= 2

    return _font(
        min_size,
        bold=bold,
        mono=mono,
    )


def _wrap(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    *,
    max_width: int,
    max_lines: int,
) -> list[str]:
    words = _clean(text).split()

    if not words:
        return [""]

    lines: list[str] = []
    current = ""

    for word in words:
        candidate = word if not current else f"{current} {word}"

        if _text_width(draw, candidate, font) <= max_width:
            current = candidate
            continue

        if current:
            lines.append(current)
            current = word
        else:
            lines.append(word)
            current = ""

        if len(lines) >= max_lines:
            break

    if current and len(lines) < max_lines:
        lines.append(current)

    rendered_count = len(" ".join(lines).split())

    if rendered_count < len(words) and lines:
        last = lines[-1].rstrip(" .,:;-")

        while last:
            candidate = last + "..."

            if _text_width(draw, candidate, font) <= max_width:
                lines[-1] = candidate
                break

            if " " not in last:
                lines[-1] = "..."
                break

            last = last.rsplit(" ", 1)[0]

    return lines[:max_lines]


def _wrap_all(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    *,
    max_width: int,
) -> list[str]:
    words = _clean(text).split()

    if not words:
        return [""]

    lines: list[str] = []
    current = ""

    for word in words:
        candidate = word if not current else f"{current} {word}"

        if _text_width(draw, candidate, font) <= max_width:
            current = candidate
            continue

        if current:
            lines.append(current)
            current = word
        else:
            lines.append(word)
            current = ""

    if current:
        lines.append(current)

    return lines


def _fit_scene_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    *,
    max_width: int,
    max_lines: int = 3,
) -> tuple[ImageFont.ImageFont, list[str]]:

    # Start slightly larger and BOLD for better readability in Discord.
    # Only shrink if the complete scene cannot fit in 3 lines.
    for size in range(44, 29, -1):
        font = _font(
            size,
            mono=True,
            bold=True,
        )

        lines = _wrap_all(
            draw,
            text,
            font,
            max_width=max_width,
        )

        if len(lines) <= max_lines:
            return font, lines

    # Very long lines still keep every word.
    font = _font(
        30,
        mono=True,
        bold=True,
    )

    lines = _wrap_all(
        draw,
        text,
        font,
        max_width=max_width,
    )

    return font, lines


def render_hunt_card(
    *,
    victim_name: str,
    killer_name: str,
    scene: str,
    action_labels: tuple[str, ...],
) -> io.BytesIO:

    image = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(image)

    # Coordinates for the black center panel
    left = 455
    right = 1210
    top = 292
    bottom = 682

    panel_width = right - left

    # Slightly brighter for Discord's image compression/scaling
    red = (238, 46, 52)
    warm_white = (244, 239, 226)
    gray = (190, 184, 173)

    victim = _clean(victim_name)

    if not victim.startswith("@"):
        victim = "@" + victim

    victim = victim[:32]

    killer_line = f"{_clean(killer_name).upper()} IS HUNTING"

    choices = "   |   ".join(
        _clean(label).upper()
        for label in action_labels
    )

    # -----------------------
    # Fonts
    # -----------------------

    victim_font = _fit_single_line_font(
        draw,
        victim,
        max_width=panel_width,
        start_size=68,
        min_size=46,
        bold=True,
    )

    killer_font = _fit_single_line_font(
        draw,
        killer_line,
        max_width=panel_width,
        start_size=54,
        min_size=38,
        bold=True,
        mono=True,
    )

    choices_font = _fit_single_line_font(
        draw,
        choices,
        max_width=panel_width,
        start_size=40,
        min_size=30,
        bold=True,
    )

    brand_font = _font(
        26,
        mono=True,
    )

    # -----------------------
    # Victim
    # -----------------------

    draw.text(
        (left, top),
        victim,
        font=victim_font,
        fill=red,
        stroke_width=1,
        stroke_fill=(35, 0, 0),
    )

    # -----------------------
    # Killer title
    # -----------------------

    y = top + 78

    draw.text(
        (left, y),
        killer_line,
        font=killer_font,
        fill=warm_white,
        stroke_width=1,
        stroke_fill=(0, 0, 0),
    )

    # -----------------------
    # Scene text
    # -----------------------

    y += 68

    scene_font, scene_lines = _fit_scene_text(
        draw,
        scene,
        max_width=panel_width,
        max_lines=3,
    )

    scene_size = getattr(
        scene_font,
        "size",
        32,
    )

    line_height = scene_size + 11

    for line in scene_lines:
        draw.text(
            (left, y),
            line,
            font=scene_font,
            fill=warm_white,
            stroke_width=1,
            stroke_fill=(0, 0, 0),
        )

        y += line_height

    # -----------------------
    # Divider
    # -----------------------

    divider_y = bottom - 88

    draw.line(
        (
            left,
            divider_y,
            right,
            divider_y,
        ),
        fill=red,
        width=3,
    )

    # -----------------------
    # Choices
    # -----------------------

    draw.text(
        (
            left,
            divider_y + 16,
        ),
        choices,
        font=choices_font,
        fill=red,
        stroke_width=1,
        stroke_fill=(35, 0, 0),
    )

    # -----------------------
    # Branding
    # -----------------------

    brand = "NukemLabs  |  Slasher Bot"

    brand_width = _text_width(
        draw,
        brand,
        brand_font,
    )

    draw.text(
        (
            right - brand_width,
            bottom - 20,
        ),
        brand,
        font=brand_font,
        fill=gray,
    )

    # -----------------------
    # Save
    # -----------------------

    output = io.BytesIO()

    image.save(
        output,
        format="JPEG",
        quality=88,
        optimize=True,
        progressive=True,
    )

    output.seek(0)

    return output
