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
            "C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
            if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        )

    if bold:
        return (
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
    for size in range(start_size, min_size - 1, -2):
        font = _font(size, bold=bold, mono=mono)
        if _text_width(draw, text, font) <= max_width:
            return font

    return _font(min_size, bold=bold, mono=mono)


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
        else:
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
    # Large, bold scene text. Shrinks only when needed to keep the
    # complete Gemini/built-in scene on the VHS card.
    for size in range(44, 29, -1):
        font = _font(size, bold=True)
        lines = _wrap_all(
            draw,
            text,
            font,
            max_width=max_width,
        )

        if len(lines) <= max_lines:
            return font, lines

    font = _font(30, bold=True)
    return font, _wrap_all(draw, text, font, max_width=max_width)


def render_hunt_card(
    *,
    victim_name: str,
    killer_name: str,
    scene: str,
    action_labels: tuple[str, ...],
) -> io.BytesIO:
    # action_labels are intentionally not drawn on the VHS.
    # The real Discord buttons below the card already show the choices.
    _ = action_labels

    image = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(image)

    # Existing black center panel on the VHS artwork.
    left = 455
    right = 1210
    top = 292
    bottom = 682

    panel_width = right - left

    red = (238, 46, 52)
    warm_white = (244, 239, 226)
    gray = (198, 192, 182)
    black = (0, 0, 0)

    victim = _clean(victim_name)
    if not victim.startswith("@"):
        victim = "@" + victim
    victim = victim[:32]

    killer_line = f"{_clean(killer_name).upper()} IS HUNTING"

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
        start_size=52,
        min_size=36,
        bold=True,
        mono=True,
    )

    # Victim name
    draw.text(
        (left, top),
        victim,
        font=victim_font,
        fill=red,
        stroke_width=1,
        stroke_fill=(45, 0, 0),
    )

    # Killer line
    y = top + 78
    draw.text(
        (left, y),
        killer_line,
        font=killer_font,
        fill=warm_white,
        stroke_width=1,
        stroke_fill=black,
    )

    # Scene
    y += 66

    scene_font, scene_lines = _fit_scene_text(
        draw,
        scene,
        max_width=panel_width,
        max_lines=3,
    )

    scene_size = getattr(scene_font, "size", 34)
    line_height = scene_size + 10

    for line in scene_lines[:3]:
        draw.text(
            (left, y),
            line,
            font=scene_font,
            fill=warm_white,
            stroke_width=1,
            stroke_fill=black,
        )
        y += line_height

    # Bottom branding only — no RUN / HIDE / FIGHT duplicated on the VHS.
    brand = "NukemLabs  |  Slasher Bot"
    brand_font = _font(22, bold=True)

    brand_width = _text_width(draw, brand, brand_font)
    brand_x = left + (panel_width - brand_width) // 2

    brand_y = bottom - 34

    # Small centered divider keeps the footer intentional without clutter.
    line_width = 300
    line_x1 = left + (panel_width - line_width) // 2
    line_x2 = line_x1 + line_width

    draw.line(
        (line_x1, brand_y - 10, line_x2, brand_y - 10),
        fill=(105, 34, 37),
        width=2,
    )

    draw.text(
        (brand_x, brand_y),
        brand,
        font=brand_font,
        fill=gray,
        stroke_width=1,
        stroke_fill=black,
    )

    output = io.BytesIO()

    image.save(
        output,
        format="JPEG",
        quality=90,
        optimize=True,
        progressive=True,
    )

    output.seek(0)
    return output
