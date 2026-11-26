#!/usr/bin/env python3
"""Render the 25 November 2026 world-news summary image.

The picture is a one-page briefing board drawn with Pillow: a navy
masthead, a crimson date strip naming the day, one lead panel, six
story cards and a footer ticker. Every story was first reported on
Wednesday 25 November 2026 (Reuters wire reports carried by
BusinessWorld, the Standard Topic world archive, the Russell Record
daily headline archive and the Open Chronicle global brief of that
date). The output is a 1024x1024 PNG under 1 MiB, identical on
every run: no randomness, no clock, no network.

SPDX-License-Identifier: MIT
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SIDE = 1024
EDGE = 30

PAPER = (250, 248, 240)
CARD = (255, 255, 253)
NAVY = (15, 31, 55)
NAVY_SOFT = (38, 58, 92)
CRIMSON = (163, 27, 35)
GOLD = (196, 152, 40)
CREAM = (246, 240, 222)
INK = (22, 24, 28)
BODY = (74, 76, 82)
HAIRLINE = (208, 204, 190)

TEAL = (10, 110, 120)
BLUE = (36, 84, 166)
PLUM = (110, 52, 140)
GREEN = (28, 118, 66)
RUST = (188, 92, 24)
BROWN = (140, 84, 30)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
OUT = Path(__file__).resolve().parent / "assets" / "entry.png"


def load(name, size):
    return ImageFont.truetype(str(FONT_DIR / name), size)


def serif(size):
    return load("DejaVuSerif-Bold.ttf", size)


def sans(size):
    return load("DejaVuSans.ttf", size)


def bold(size):
    return load("DejaVuSans-Bold.ttf", size)


def wrap(draw, text, face, width):
    """Split text into lines that fit width, measured on the canvas."""
    lines, current = [], ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=face) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def paragraph(draw, xy, text, face, fill, width, leading):
    x, y = xy
    for line in wrap(draw, text, face, width):
        draw.text((x, y), line, font=face, fill=fill)
        y += leading
    return y


def centered(draw, y, text, face, fill):
    w = draw.textlength(text, font=face)
    draw.text(((SIDE - w) / 2, y), text, font=face, fill=fill)


# ---------------------------------------------------------------- motifs

def motif_orbit(draw, box):
    """A rocket climbing past a space station inside an orbit ring."""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    draw.ellipse([cx - 118, cy - 62, cx + 118, cy + 62], outline=NAVY_SOFT, width=3)
    for sx, sy in ((x0 + 26, y0 + 22), (x1 - 34, y0 + 40), (x0 + 52, y1 - 30),
                   (x1 - 22, y1 - 52), (cx + 66, y0 + 14)):
        draw.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=GOLD)
    # station: core bar with two solar wings
    draw.rectangle([cx - 16, cy - 52, cx + 16, cy - 30], fill=NAVY)
    draw.rectangle([cx - 74, cy - 50, cx - 22, cy - 32], fill=TEAL)
    draw.rectangle([cx + 22, cy - 50, cx + 74, cy - 32], fill=TEAL)
    draw.line([cx - 74, cy - 41, cx + 74, cy - 41], fill=NAVY, width=3)
    # rocket, nose up, body along a rising diagonal
    tip = (cx + 44, cy + 2)
    tail = (cx - 6, cy + 62)
    draw.polygon([tip, (cx + 8, cy + 40), (cx + 30, cy + 66)], fill=CRIMSON)
    draw.polygon([tip, (cx + 62, cy + 30), (cx + 30, cy + 66)], fill=(214, 70, 60))
    draw.ellipse([cx + 26, cy + 24, cx + 42, cy + 40], fill=CREAM)
    draw.polygon([(cx + 2, cy + 52), (cx - 16, cy + 78), (cx + 14, cy + 70)], fill=GOLD)
    # small green flag of Pakistan on a pole by the station
    draw.line([cx - 96, cy + 6, cx - 96, cy + 58], fill=INK, width=3)
    draw.rectangle([cx - 96, cy + 6, cx - 58, cy + 30], fill=(1, 102, 52))
    draw.rectangle([cx - 96, cy + 6, cx - 86, cy + 30], fill=(245, 245, 245))
    draw.arc([cx - 76, cy + 11, cx - 64, cy + 25], start=90, end=300, fill=(245, 245, 245), width=2)


def icon_tower(draw, x, y, colour):
    draw.rectangle([x + 16, y + 6, x + 30, y + 44], outline=colour, width=3)
    draw.line([x + 23, y + 6, x + 23, y], fill=colour, width=3)
    for wy in (14, 24, 34):
        draw.rectangle([x + 20, y + wy, x + 26, y + wy + 4], fill=colour)


def icon_shield(draw, x, y, colour):
    draw.polygon([(x + 23, y + 2), (x + 42, y + 9), (x + 42, y + 24),
                  (x + 23, y + 46), (x + 4, y + 24), (x + 4, y + 9)], outline=colour, width=3)
    draw.line([x + 13, y + 24, x + 20, y + 31], fill=colour, width=3)
    draw.line([x + 20, y + 31, x + 34, y + 15], fill=colour, width=3)


def icon_chip(draw, x, y, colour):
    draw.rectangle([x + 10, y + 10, x + 36, y + 36], outline=colour, width=3)
    draw.rectangle([x + 18, y + 18, x + 28, y + 28], fill=colour)
    for p in (14, 23, 32):
        draw.line([x + p, y + 2, x + p, y + 10], fill=colour, width=3)
        draw.line([x + p, y + 36, x + p, y + 44], fill=colour, width=3)
        draw.line([x + 2, y + p, x + 10, y + p], fill=colour, width=3)
        draw.line([x + 36, y + p, x + 44, y + p], fill=colour, width=3)


def icon_chart(draw, x, y, colour):
    draw.line([x + 4, y + 42, x + 44, y + 42], fill=colour, width=3)
    for i, h in enumerate((14, 24, 34)):
        bx = x + 8 + i * 12
        draw.rectangle([bx, y + 42 - h, bx + 8, y + 42], fill=colour)
    draw.line([x + 6, y + 16, x + 40, y + 4], fill=GOLD, width=3)


def icon_tag(draw, x, y, colour):
    draw.polygon([(x + 6, y + 6), (x + 26, y + 6), (x + 42, y + 22),
                  (x + 22, y + 42), (x + 6, y + 26)], outline=colour, width=3)
    draw.ellipse([x + 12, y + 12, x + 18, y + 18], fill=colour)
    draw.text((x + 17, y + 20), "%", font=bold(17), fill=colour)


def icon_flame(draw, x, y, colour):
    draw.polygon([(x + 23, y + 2), (x + 34, y + 20), (x + 38, y + 30),
                  (x + 32, y + 42), (x + 14, y + 42), (x + 8, y + 30),
                  (x + 13, y + 18)], outline=colour, width=3)
    draw.ellipse([x + 18, y + 26, x + 28, y + 40], fill=colour)


# ---------------------------------------------------------------- layout

def masthead(draw):
    draw.rectangle([0, 0, SIDE, 148], fill=NAVY)
    draw.text((EDGE + 6, 30), "THE WORLD IN ONE DAY", font=serif(57), fill=CREAM)
    draw.text((EDGE + 8, 104), "One image summing up the day's world news",
              font=sans(23), fill=(178, 192, 214))
    label = "ONE DAY · ONE IMAGE"
    w = draw.textlength(label, font=bold(21))
    draw.text((SIDE - EDGE - w, 108), label, font=bold(21), fill=GOLD)
    draw.rectangle([0, 148, SIDE, 156], fill=GOLD)


def date_strip(draw):
    draw.rectangle([0, 156, SIDE, 228], fill=CRIMSON)
    centered(draw, 172, "WEDNESDAY · 25 NOVEMBER 2026", bold(45), (255, 250, 244))


def lead_panel(draw):
    top, bottom = 242, 470
    draw.rectangle([EDGE, top, SIDE - EDGE, bottom], fill=CARD, outline=NAVY, width=3)
    draw.rectangle([EDGE, top, EDGE + 10, bottom], fill=TEAL)
    draw.text((EDGE + 30, top + 16), "SCIENCE & SPACE — CHINA · PAKISTAN",
              font=bold(22), fill=TEAL)
    headline = "Pakistan's first astronaut reaches China's station"
    lines = wrap(draw, headline, serif(37), 612)
    y = top + 50
    for line in lines:
        draw.text((EDGE + 30, y), line, font=serif(37), fill=INK)
        y += 46
    paragraph(draw, (EDGE + 30, y + 12),
              "Shenzhou-24 docked at Tiangong with Muhammad Zeeshan Ali "
              "aboard — a first for a foreign astronaut.",
              sans(22), BODY, 612, 30)
    motif_orbit(draw, (668, top + 20, 968, top + 208))


CARDS = [
    ("MIDDLE EAST", CRIMSON, icon_tower,
     "Houthi strike hits Riyadh tower; 11 wounded",
     "Iran says mines hit tankers in Hormuz; the US disputes it."),
    ("EUROPE", BLUE, icon_shield,
     "30+ nations: Russia must stop chemical weapons in Ukraine",
     "A joint call to halt toxic agents used as weapons."),
    ("TECH & LAW", PLUM, icon_chip,
     "Huawei convicted in US trial over its Iran business",
     "A New York jury found the tech giant guilty on 10 of 12 counts."),
    ("ECONOMY", GREEN, icon_chart,
     "US prepares new tariffs on 14 trading partners",
     "After a Washington probe into excess factory capacity abroad."),
    ("ASIA", RUST, icon_tag,
     "Bangladesh raises garment workers' pay by 36%",
     "Minimum wage rises to $139 a month after protests."),
    ("AFRICA", BROWN, icon_flame,
     "Fuel-tanker crash in Cairo kills at least 30",
     "It overturned and caught fire on the ring road, engulfing cars."),
]


def story_card(draw, x, y, w, h, card):
    kicker, colour, icon, headline, detail = card
    draw.rectangle([x, y, x + w, y + h], fill=CARD, outline=HAIRLINE, width=2)
    draw.rectangle([x, y, x + w, y + 7], fill=colour)
    draw.text((x + 16, y + 15), kicker, font=bold(19), fill=colour)
    icon(draw, x + w - 58, y + 10, colour)
    paragraph(draw, (x + 16, y + 44), headline, bold(22), INK, w - 32, 26)
    paragraph(draw, (x + 16, y + h - 45), detail, sans(17), BODY, w - 32, 21)


def footer(draw):
    top = 852
    draw.rectangle([0, top, SIDE, SIDE], fill=NAVY)
    draw.text((EDGE + 6, top + 14), "ALSO ON 25 NOVEMBER", font=bold(20), fill=GOLD)
    paragraph(draw, (EDGE + 6, top + 46),
              "Spain heads to a snap general election on Sunday · Jannik Sinner "
              "sidelined after knee surgery · London Museum reopens in a restored "
              "Victorian market · US charges 800+ defendants in a global anti-scam crackdown",
              sans(20), CREAM, SIDE - 2 * EDGE - 12, 27)


def render():
    img = Image.new("RGB", (SIDE, SIDE), PAPER)
    draw = ImageDraw.Draw(img)
    masthead(draw)
    date_strip(draw)
    lead_panel(draw)
    col_w, gap = 309, 18
    row_h = 168
    for i, card in enumerate(CARDS):
        x = EDGE + (i % 3) * (col_w + gap)
        y = 486 + (i // 3) * (row_h + 14)
        story_card(draw, x, y, col_w, row_h, card)
    footer(draw)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    render()
