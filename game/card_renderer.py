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
            if bold else
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
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

    # Linux hosts such as Railway may not have the Windows or DejaVu
    # font files installed. Pillow 12 can scale its built-in fallback,
    # so preserve the requested font size instead of using the tiny
    # legacy bitmap fallback.
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
        font = _font(size, bold=bold, mono=mono)
        if _text_width(draw, text, font) <= max_width:
            return font
        size -= 2

    return _font(min_size, bold=bold, mono=mono)


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
    consumed = 0

    for word in words:
        candidate = word if not current else f"{current} {word}"

        if _text_width(draw, candidate, font) <= max_width:
            current = candidate
            consumed += 1
            continue

        if current:
            lines.append(current)
            current = word
            consumed += 1
        else:
            lines.append(word)
            consumed += 1
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
    # Start large for Discord readability. Only shrink if the COMPLETE
    # Gemini/built-in scene will not fit inside three lines.
    for size in range(41, 27, -1):
        font = _font(size, mono=True)
        lines = _wrap_all(
            draw,
            text,
            font,
            max_width=max_width,
        )
        if len(lines) <= max_lines:
            return font, lines

    # Very unusually long text: keep every word rather than adding "...".
    # The writer already aims for short scenes, so this is mainly a safeguard.
    font = _font(28, mono=True)
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

    # The user's frame is 1664 x 936. These coordinates sit safely
    # inside the black center panel.
    left = 455
    right = 1210
    top = 292
    bottom = 682
    panel_width = right - left

    red = (224, 42, 47)
    warm_white = (226, 220, 207)
    gray = (174, 168, 158)

    victim = _clean(victim_name)
    if not victim.startswith("@"):
        victim = "@" + victim
    victim = victim[:32]

    killer_line = f"{_clean(killer_name).upper()} IS HUNTING"
    choices = "   |   ".join(
        _clean(label).upper()
        for label in action_labels
    )

    victim_font = _fit_single_line_font(
        draw,
        victim,
        max_width=panel_width,
        start_size=66,
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


    choices_font = _fit_single_line_font(
        draw,
        choices,
        max_width=panel_width,
        start_size=38,
        min_size=28,
        bold=True,
    )

    brand_font = _font(26, mono=True)

    # Victim
    draw.text(
        (left, top),
        victim,
        font=victim_font,
        fill=red,
    )

    # Killer
    y = top + 78
    draw.text(
        (left, y),
        killer_line,
        font=killer_font,
        fill=warm_white,
    )

    # Scene: deliberately short so the card remains easy to read.
    y += 68
    scene_font, scene_lines = _fit_scene_text(
        draw,
        scene,
        max_width=panel_width,
        max_lines=3,
    )

    # Scale line spacing with whichever font size was needed.
    scene_size = getattr(scene_font, "size", 32)
    line_height = scene_size + 11

    for line in scene_lines:
        draw.text(
            (left, y),
            line,
            font=scene_font,
            fill=warm_white,
        )
        y += line_height

    # Divider near bottom.
    divider_y = bottom - 88
    draw.line(
        (left, divider_y, right, divider_y),
        fill=red,
        width=3,
    )

    # Visual reminder of the buttons below the image.
    draw.text(
        (left, divider_y + 16),
        choices,
        font=choices_font,
        fill=red,
    )

    # Small bot branding.
    brand = "NukemLabs  |  Slasher Bot"
    brand_width = _text_width(draw, brand, brand_font)

    draw.text(
        (right - brand_width, bottom - 20),
        brand,
        font=brand_font,
        fill=gray,
    )

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
