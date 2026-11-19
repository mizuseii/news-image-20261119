#!/usr/bin/env python3
"""Draw the news-image-20261119 entry: a 1024x1024 infographic summing
up Thursday 19 November 2026's world news.

Stories (all verified against Reuters, Le Monde, IMD, NASA and AP
reporting — see NOTES.md for sources and date discipline):
  1. Trump, Xi and Putin hold their first-ever trilateral in Shenzhen.
  2. GTA VI begins its global rollout, midnight by midnight.
  3. Cyclone Akvan bears down on India's east coast.
  4. Day 265 of the US-Iran war: Gulf attacks widen.
  5. (strip) India-Japan 2+2 dialogue in Tokyo.
  6. (strip) NASA confirms Voyager 1 is one light-day away.

Build time only. Run: python3 draw_news.py  (writes entry.png next
to this file). Uses Pillow and DejaVu fonts; no network.
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024

NAVY = (11, 29, 51)
NAVY_DARK = (8, 22, 40)
PANEL = (20, 48, 76)
PANEL_ALT = (24, 56, 88)
GOLD = (242, 183, 5)
WHITE = (255, 255, 255)
BODY = (213, 222, 232)
MUTED = (150, 168, 188)
RULE = (242, 183, 5)
RED = (228, 87, 46)
TEAL = (23, 163, 152)
AMBER = (246, 174, 45)
CRIMSON = (196, 69, 54)
GREEN = (46, 160, 90)
BLUE = (46, 134, 171)
PURPLE = (138, 90, 205)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_MAST = font("DejaVuSans-Bold.ttf", 56)
F_DATE = font("DejaVuSans-Bold.ttf", 38)
F_KICK = font("DejaVuSans-Bold.ttf", 17)
F_HEAD = font("DejaVuSans-Bold.ttf", 31)
F_BODY = font("DejaVuSans.ttf", 22)
F_STRIP_HEAD = font("DejaVuSans-Bold.ttf", 24)
F_STRIP_BODY = font("DejaVuSans.ttf", 21)
F_FOOT = font("DejaVuSans.ttf", 18)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines fitting max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_panel(draw, x, y, w, h, tag, tag_color, headline, body, icon):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=18, fill=PANEL)
    # Tag chip.
    chip_w = draw.textlength(tag, font=F_KICK) + 26
    draw.rounded_rectangle([x + 22, y + 20, x + 22 + chip_w, y + 52],
                           radius=16, fill=tag_color)
    draw.text((x + 35, y + 25), tag, font=F_KICK, fill=WHITE)
    # Simple icon on the right of the tag row.
    icon(draw, x + w - 78, y + 18)
    # Headline.
    lines = wrap(draw, headline, F_HEAD, w - 44)
    ty = y + 66
    for line in lines:
        draw.text((x + 22, ty), line, font=F_HEAD, fill=WHITE)
        ty += 38
    # Body.
    by = ty + 8
    for line in wrap(draw, body, F_BODY, w - 44):
        draw.text((x + 22, by), line, font=F_BODY, fill=BODY)
        by += 29


def icon_flags(draw, x, y):
    # Three summit flags on poles: US, China, Russia.
    for i, col in enumerate([RED, GOLD, BLUE]):
        px = x + 6 + i * 20
        draw.line([px, y + 6, px, y + 58], fill=WHITE, width=3)
        draw.polygon([(px, y + 6), (px + 17, y + 12), (px, y + 20)],
                     fill=col)


def icon_controller(draw, x, y):
    # Game controller: body, grips, d-pad and buttons.
    draw.rounded_rectangle([x + 2, y + 18, x + 58, y + 44], radius=12,
                           fill=PURPLE)
    draw.polygon([(x + 6, y + 40), (x + 16, y + 40), (x + 12, y + 58),
                  (x + 4, y + 58)], fill=PURPLE)
    draw.polygon([(x + 44, y + 40), (x + 54, y + 40), (x + 56, y + 58),
                  (x + 48, y + 58)], fill=PURPLE)
    draw.rectangle([x + 10, y + 27, x + 20, y + 31], fill=WHITE)
    draw.rectangle([x + 14, y + 23, x + 16, y + 35], fill=WHITE)
    for bx, by in [(x + 42, y + 25), (x + 48, y + 30), (x + 42, y + 35)]:
        draw.ellipse([bx, by, bx + 5, by + 5], fill=GOLD)


def icon_spiral(draw, x, y):
    # Cyclone: concentric arcs.
    for r, col in [(28, AMBER), (21, WHITE), (14, AMBER), (7, WHITE)]:
        draw.arc([x + 30 - r, y + 30 - r, x + 30 + r, y + 30 + r],
                 start=20, end=300, fill=col, width=4)


def icon_ship(draw, x, y):
    # Tanker: hull, deck, funnel, waves.
    draw.polygon([(x + 2, y + 34), (x + 58, y + 34), (x + 50, y + 52),
                  (x + 10, y + 52)], fill=CRIMSON)
    draw.rectangle([x + 38, y + 20, x + 48, y + 34], fill=WHITE)
    draw.rectangle([x + 12, y + 26, x + 30, y + 34], fill=WHITE)
    for wx in (x + 2, x + 24, x + 46):
        draw.arc([wx, y + 54, wx + 12, y + 62], start=0, end=180,
                 fill=BLUE, width=3)


def main():
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    # Header band.
    draw.rectangle([0, 0, W, 158], fill=NAVY_DARK)
    draw.rectangle([0, 158, W, 164], fill=RULE)
    draw.text((36, 26), "THE WORLD IN ONE IMAGE", font=F_MAST, fill=WHITE)
    draw.text((36, 98), "THURSDAY  19  NOVEMBER  2026",
              font=F_DATE, fill=GOLD)

    # 2x2 story grid.
    gx, gy = 24, 184
    pw, ph = 476, 288
    gap = 24
    stories = [
        ("DIPLOMACY  ·  SHENZHEN", RED,
         "Trump, Xi and Putin meet in Shenzhen",
         "The three leaders hold their first-ever trilateral on the "
         "APEC sidelines — Ukraine, Iran, trade and AI on the table.",
         icon_flags),
        ("CULTURE  ·  VICE CITY", PURPLE,
         "GTA VI rolls out around the world",
         "After 13 years and $1bn-plus in production, the game "
         "unlocks at midnight in each market, starting in New "
         "Zealand — and tops Metacritic at 99.", icon_controller),
        ("WEATHER  ·  BAY OF BENGAL", AMBER,
         "Cyclone Akvan bears down on India",
         "Extremely heavy rain is forecast for 19–20 Nov; Odisha "
         "shuts schools and postpones exams as landfall nears, "
         "due Friday.", icon_spiral),
        ("CONFLICT  ·  GULF", CRIMSON,
         "War at sea widens — day 265",
         "Iran has struck a US base in Kuwait and kept hitting "
         "Bahrain; three US carriers are in the region, and Trump "
         "says he will raise the war in Shenzhen.", icon_ship),
    ]
    for i, (tag, color, head, body, ic) in enumerate(stories):
        x = gx + (i % 2) * (pw + gap)
        y = gy + (i // 2) * (ph + gap)
        draw_panel(draw, x, y, pw, ph, tag, color, head, body, ic)

    # Bottom strip: India-Japan + Voyager.
    sy = gy + 2 * ph + gap + 12
    draw.rounded_rectangle([gx, sy, W - gx, sy + 118], radius=18,
                           fill=PANEL_ALT)
    draw.text((gx + 22, sy + 14), "ALSO TODAY", font=F_STRIP_HEAD,
              fill=GOLD)
    draw.text((gx + 22, sy + 46),
              "India and Japan hold their 2+2 defence and foreign "
              "ministers' dialogue in Tokyo.",
              font=F_STRIP_BODY, fill=BODY)
    draw.text((gx + 22, sy + 76),
              "NASA confirms Voyager 1 is one light-day from Earth — "
              "16 billion miles out.",
              font=F_STRIP_BODY, fill=BODY)

    # Footer.
    fy = H - 56
    draw.rectangle([0, fy - 14, W, H], fill=NAVY_DARK)
    draw.text((36, fy), "Sources: Reuters · Le Monde · IMD · NASA — "
              "every story happened or was first reported on 19 Nov 2026.",
              font=F_FOOT, fill=MUTED)

    img.save(OUT, format="PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
