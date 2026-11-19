#!/usr/bin/env python3
"""Draw the 19 November 2026 world-news infographic.

Layout (1024 x 1024, dark newsprint style):
  masthead  -> big date line, gold rule
  lead card -> the Shenzhen trilateral, full width
  three cards in a row -> GTA VI, Cyclone Akvan, US-Iran war
  bottom strip -> India-Japan 2+2 and Voyager 1, side by side
  footer -> sources line

Run: python3 draw_news.py   (writes entry.png next to this file)
Requires Pillow at build time only; the entry itself is a static PNG.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 32
CONTENT_W = W - 2 * MARGIN

# --- palette ---------------------------------------------------------------
INK = (10, 17, 34)        # page background
PANEL = (22, 35, 61)      # card background
PANEL_EDGE = (38, 56, 94) # card outline
PAPER = (245, 241, 230)   # main text
MUTED = (169, 184, 208)   # body text
GOLD = (242, 183, 5)      # date / accents
RED = (214, 69, 55)
TEAL = (46, 160, 158)
SKY = (84, 148, 220)
VIOLET = (146, 106, 214)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


F_KICKER = font("DejaVuSans-Bold.ttf", 25)
F_DATE = font("DejaVuSans-Bold.ttf", 56)
F_LEAD_HEAD = font("DejaVuSans-Bold.ttf", 38)
F_LEAD_BODY = font("DejaVuSans.ttf", 22)
F_CARD_HEAD = font("DejaVuSans-Bold.ttf", 27)
F_CARD_BODY = font("DejaVuSans.ttf", 19)
F_TAG = font("DejaVuSans-Bold.ttf", 19)
F_STRIP_LABEL = font("DejaVuSans-Bold.ttf", 22)
F_STRIP_BODY = font("DejaVuSans.ttf", 21)
F_FOOT = font("DejaVuSans.ttf", 17)


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont,
         max_w: int) -> list[str]:
    """Greedy word wrap using real text widths."""
    lines: list[str] = []
    current = ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(draw: ImageDraw.ImageDraw, lines: list[str], x: int, y: int,
               fnt: ImageFont.FreeTypeFont, fill, leading: int) -> int:
    """Draw lines top to bottom; return the y just below the last line."""
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def tag(draw: ImageDraw.ImageDraw, x: int, y: int, label: str,
        fill) -> int:
    """Draw a pill tag; return its right edge."""
    pad_x, pad_y = 14, 7
    tw = draw.textlength(label, font=F_TAG)
    th = F_TAG.size
    draw.rounded_rectangle(
        [x, y, x + tw + 2 * pad_x, y + th + 2 * pad_y],
        radius=14, fill=fill,
    )
    draw.text((x + pad_x, y + pad_y - 1), label, font=F_TAG, fill=(255, 255, 255))
    return int(x + tw + 2 * pad_x)


def panel(draw: ImageDraw.ImageDraw, box) -> None:
    draw.rounded_rectangle(box, radius=18, fill=PANEL, outline=PANEL_EDGE,
                           width=2)


# --- small geometric icon (drawn, not pasted) -------------------------------

def icon_flags(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    """Three small pennant flags on poles: US / China / Russia."""
    pole_h, gap = 74, 44
    colours = [(178, 34, 52), (222, 41, 16), (30, 90, 168)]
    for i, colour in enumerate(colours):
        px = x + i * gap
        draw.line([(px, y), (px, y + pole_h)], fill=PAPER, width=4)
        draw.polygon([(px, y), (px + 34, y + 9), (px, y + 18)], fill=colour)


# --- build -------------------------------------------------------------------

def build() -> Image.Image:
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)

    # Masthead: kicker, then the date as the hero line, gold rule below.
    d.text((MARGIN, 30), "THE WORLD IN ONE IMAGE", font=F_KICKER, fill=GOLD)
    d.text((MARGIN, 62), "THURSDAY 19 NOVEMBER 2026", font=F_DATE, fill=PAPER)
    d.rectangle([MARGIN, 148, W - MARGIN, 153], fill=GOLD)

    # ---- lead story: Shenzhen trilateral -----------------------------------
    lead = (MARGIN, 172, W - MARGIN, 424)
    panel(d, lead)
    lx, ly = lead[0] + 26, lead[1] + 20
    tag(d, lx, ly, "DIPLOMACY  ·  SHENZHEN", RED)
    icon_flags(d, lead[2] - 190, ly - 2)
    head = wrap(d, "Trump, Xi and Putin meet in Shenzhen",
                F_LEAD_HEAD, CONTENT_W - 52 - 200)
    y = draw_lines(d, head, lx, ly + 48, F_LEAD_HEAD, PAPER, 46)
    body = wrap(
        d,
        "The three leaders hold their first-ever trilateral on the APEC "
        "sidelines — Ukraine, Iran, trade and AI on the table. Trump and "
        "Putin shook hands at Wednesday's welcome event, their first "
        "face-to-face in over a year.",
        F_LEAD_BODY, CONTENT_W - 52)
    draw_lines(d, body, lx, y + 10, F_LEAD_BODY, MUTED, 27)

    # ---- three cards in a row ----------------------------------------------
    cards = [
        ("CULTURE  ·  VICE CITY", VIOLET,
         "GTA VI rolls out worldwide",
         "After 13 years and $1bn-plus in production, it unlocks at "
         "midnight in each market, starting in New Zealand — Metacritic 99."),
        ("WEATHER  ·  BENGAL", TEAL,
         "Cyclone Akvan bears down on India",
         "Extremely heavy rain is forecast for 19–20 Nov; Odisha shuts "
         "schools and postpones exams as landfall nears, due Friday."),
        ("CONFLICT  ·  GULF", RED,
         "War at sea widens — day 265",
         "Iran has struck a US base in Kuwait and kept hitting Bahrain; "
         "three US carriers are in the region."),
    ]
    gap = 20
    cw = (CONTENT_W - 2 * gap) // 3
    top, bottom = 440, 760
    for i, (label, colour, headline, text) in enumerate(cards):
        x0 = MARGIN + i * (cw + gap)
        panel(d, (x0, top, x0 + cw, bottom))
        cx, cy = x0 + 22, top + 18
        tag(d, cx, cy, label, colour)
        head = wrap(d, headline, F_CARD_HEAD, cw - 44)
        y = draw_lines(d, head, cx, cy + 48, F_CARD_HEAD, PAPER, 33)
        body = wrap(d, text, F_CARD_BODY, cw - 44)
        draw_lines(d, body, cx, y + 10, F_CARD_BODY, MUTED, 25)

    # ---- bottom strip: two more stories ------------------------------------
    strip = (MARGIN, 776, W - MARGIN, 928)
    panel(d, strip)
    d.line([(W // 2, strip[1] + 18), (W // 2, strip[3] - 18)],
           fill=PANEL_EDGE, width=2)
    halves = [
        (strip[0] + 24, "2+2 IN TOKYO",
         "India and Japan hold their 2+2 defence and foreign ministers' "
         "dialogue in Tokyo."),
        (W // 2 + 24, "VOYAGER 1",
         "NASA confirms Voyager 1 is one light-day from Earth — "
         "16 billion miles out."),
    ]
    for x, label, text in halves:
        d.text((x, strip[1] + 18), label, font=F_STRIP_LABEL, fill=GOLD)
        body = wrap(d, text, F_STRIP_BODY, CONTENT_W // 2 - 48)
        draw_lines(d, body, x, strip[1] + 52, F_STRIP_BODY, MUTED, 28)

    # ---- footer --------------------------------------------------------------
    d.text((MARGIN, 948),
           "Sources: Reuters · Le Monde · IMD · NASA — every story happened "
           "or was first reported on 19 Nov 2026.",
           font=F_FOOT, fill=MUTED)
    return img


def main() -> None:
    out = Path(__file__).resolve().parent / "entry.png"
    build().save(out, format="PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
