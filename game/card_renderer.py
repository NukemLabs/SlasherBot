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
            "C:/Windows/Fonts/impact.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        )

    return (
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )


def _font(size: int, *, bold: bool = False, mono: bool = False) -> ImageFont.ImageFont:
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
    for size in range(34, 21, -1):
        font = _font(size, mono=True, bold=False)
        lines = _wrap_all(draw, text, font, max_width=max_width)

        if len(lines) <= max_lines:
            return font, lines

    font = _font(22, mono=True, bold=False)
    lines = _wrap(draw, text, font, max_width=max_width, max_lines=max_lines)
    return font, lines


def _draw_title_badge(image: Image.Image) -> Image.Image:
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))

    badge = Image.new("RGBA", (360, 130), (0, 0, 0, 0))
    badge_draw = ImageDraw.Draw(badge)

    badge_draw.rounded_rectangle(
        (6, 16, 348, 112),
        radius=8,
        fill=(224, 210, 186, 235),
        outline=(82, 31, 18, 255),
        width=3,
    )

    for x in range(18, 340, 22):
        badge_draw.line(
            (x, 22, x + 12, 106),
            fill=(120, 55, 40, 28),
            width=1,
        )

    title_red = (120, 15, 15, 255)
    title_shadow = (25, 0, 0, 210)

    top_font = _font(28, bold=True)
    main_font = _font(62, bold=True)

    badge_draw.text(
        (30, 16),
        "THE",
        font=top_font,
        fill=title_red,
        stroke_width=1,
        stroke_fill=title_shadow,
    )

    badge_draw.text(
        (24, 34),
        "SLASHER",
        font=main_font,
        fill=title_red,
        stroke_width=2,
        stroke_fill=title_shadow,
    )

    rotated = badge.rotate(-9, resample=Image.Resampling.BICUBIC, expand=True)
    overlay.alpha_composite(rotated, dest=(78, 118))

    combined = Image.alpha_composite(image, overlay)
    return combined


def render_hunt_card(
    *,
    victim_name: str,
    killer_name: str,
    scene: str,
    action_labels: tuple[str, ...],
) -> io.BytesIO:
    _ = action_labels

    image = Image.open(TEMPLATE_PATH).convert("RGBA")
    image = _draw_title_badge(image)

    draw = ImageDraw.Draw(image)

    # Center text panel coordinates
    left = 455
    right = 1210
    top = 292
    bottom = 682
    panel_width = right - left

    red = (238, 46, 52)
    warm_white = (244, 239, 226)
    gray = (188, 181, 170)

    victim = _clean(victim_name)
    if not victim.startswith("@"):
        victim = "@" + victim
    victim = victim[:32]

    killer_line = f"{_clean(killer_name).upper()} IS HUNTING"
    brand = "NukemLabs   |   Slasher Bot"

    victim_font = _fit_single_line_font(
        draw,
        victim,
        max_width=panel_width,
        start_size=50,
        min_size=34,
        bold=True,
    )

    killer_font = _fit_single_line_font(
        draw,
        killer_line,
        max_width=panel_width,
        start_size=37,
        min_size=26,
        bold=False,
        mono=True,
    )

    brand_font = _fit_single_line_font(
        draw,
        brand,
        max_width=panel_width,
        start_size=18,
        min_size=14,
        bold=False,
        mono=False,
    )

    # Victim name
    draw.text(
        (left, top),
        victim,
        font=victim_font,
        fill=red,
        stroke_width=1,
        stroke_fill=(35, 0, 0),
    )

    # Killer line
    y = top + 68
    draw.text(
        (left, y),
        killer_line,
        font=killer_font,
        fill=warm_white,
        stroke_width=1,
        stroke_fill=(0, 0, 0),
    )

    # Scene text
    y += 52
    scene_font, scene_lines = _fit_scene_text(
        draw,
        scene,
        max_width=panel_width,
        max_lines=3,
    )

    scene_size = getattr(scene_font, "size", 22)
    line_height = scene_size + 8

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

    # Subtle footer divider
    divider_y = bottom - 42
    draw.line(
        (left, divider_y, right, divider_y),
        fill=(110, 24, 28),
        width=2,
    )

    # Centered branding
    brand_width = _text_width(draw, brand, brand_font)
    brand_x = left + (panel_width - brand_width) // 2

    draw.text(
        (brand_x, bottom - 26),
        brand,
        font=brand_font,
        fill=gray,
    )

    output = io.BytesIO()
    image.convert("RGB").save(
        output,
        format="JPEG",
        quality=88,
        optimize=True,
        progressive=True,
    )
    output.seek(0)
    return output
