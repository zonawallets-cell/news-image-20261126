#!/usr/bin/env python3
"""Render the 26 November 2026 world-news front page.

Draws a dense newspaper front page, 1024x1024, deterministic:
no clock, no network, no randomness. Output: entry.png
"""
import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (18, 18, 18)
RULE = (60, 60, 60)
RED = (178, 34, 34)
NAVY = (24, 42, 74)
MAP_OCEAN = (203, 222, 231)
MAP_LAND = (216, 205, 180)
MAP_EDGE = (138, 127, 99)
GREY = (90, 90, 90)
FAINT = (180, 180, 180)

FDIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)


def wrap(draw, text, fnt, width):
    """Greedy word wrap returning a list of lines that fit width."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, text, fnt, x, y, width, fill=INK, spacing=4,
                 max_lines=None):
    lines = wrap(draw, text, fnt, width)
    if max_lines is not None:
        assert len(lines) <= max_lines, (
            "text overflow: %r needs %d lines, max %d"
            % (text[:40], len(lines), max_lines))
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += fnt.size + spacing
    return y


# --- world map: rough lon/lat polygons, equirectangular projection ---
MAP = (24, 424, 1000, 544)  # x0, y0, x1, y1


def project(lon, lat):
    x0, y0, x1, y1 = MAP
    x = x0 + (lon + 180.0) / 360.0 * (x1 - x0)
    y = y0 + (75.0 - lat) / 135.0 * (y1 - y0)
    return (x, y)


CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 76),
     (-75, 72), (-65, 60), (-55, 52), (-60, 47), (-70, 42), (-75, 35),
     (-80, 26), (-85, 20), (-90, 15), (-95, 18), (-105, 20), (-115, 28),
     (-125, 40), (-125, 49), (-140, 60), (-155, 58), (-165, 60)],
    # South America
    [(-80, 10), (-75, 5), (-70, 0), (-60, -5), (-50, -5), (-40, -10),
     (-35, -20), (-40, -30), (-50, -35), (-60, -40), (-70, -50),
     (-73, -40), (-72, -25), (-75, -15), (-80, -5)],
    # Africa
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31),
     (35, 28), (40, 15), (43, 11), (48, 10), (51, 12), (43, 0),
     (40, -10), (35, -20), (30, -30), (20, -35), (15, -25), (12, -15),
     (8, 4), (-8, 5), (-15, 10)],
    # Eurasia
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (35, 65),
     (45, 68), (60, 69), (70, 72), (90, 75), (110, 76), (130, 72),
     (150, 70), (170, 66), (178, 65), (170, 60), (160, 55), (155, 50),
     (142, 45), (140, 40), (130, 35), (127, 33), (122, 30), (120, 25),
     (110, 20), (105, 10), (100, 8), (95, 15), (90, 22), (85, 20),
     (80, 15), (77, 8), (72, 20), (66, 25), (60, 25), (57, 26),
     (52, 28), (50, 30), (48, 30), (44, 29), (40, 36), (36, 36),
     (30, 36), (26, 38), (23, 40), (19, 42), (15, 44), (12, 44),
     (8, 44), (3, 43), (-2, 37), (-9, 37)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32),
     (132, -32), (137, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (150, -25), (146, -20), (142, -15), (142, -11),
     (136, -12), (132, -11), (126, -14), (122, -17), (118, -20)],
    # Britain
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37), (141, 39),
     (141, 41), (142, 44), (144, 44), (142, 42), (140, 38)],
    # Greenland
    [(-45, 60), (-40, 64), (-30, 68), (-22, 70), (-25, 76), (-40, 80),
     (-55, 76), (-58, 70), (-53, 64)],
    # Indonesia
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10),
     (125, -8), (130, -3), (135, -2), (140, -4), (138, -8), (130, -10),
     (120, -10)],
]

# pins: (number, lon, lat, label, label dx, label dy)
PINS = [
    (1, 56.5, 26.5, "HORMUZ", 14, -8),
    (2, 50.0, 26.6, "RAS TANURA", 16, 8),
    (3, 56.5, 26.5, None, 0, 0),          # same strait: offset below
    (4, 34.5, 31.5, "GAZA", -52, 10),
    (5, 98.5, 39.8, "JIUQUAN", 12, -16),
    (6, -77.0, 38.9, "WASHINGTON", -96, 10),
    (7, -74.0, 40.7, "NEW YORK", 12, -18),
    (8, -16.0, 28.3, "CANARY IS.", -88, -4),
    (9, -0.1, 51.5, "LONDON", -70, -14),
    (10, 30.7, 46.5, "ODESA", 12, -14),
]


def draw_map(draw):
    x0, y0, x1, y1 = MAP
    draw.rectangle([x0, y0, x1, y1], fill=MAP_OCEAN, outline=RULE, width=1)
    for poly in CONTINENTS:
        pts = [project(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=MAP_LAND, outline=MAP_EDGE)
    for num, lon, lat, label, dx, dy in PINS:
        px, py = project(lon, lat)
        if num == 3:
            px, py = px + 14, py + 12
        if num == 2:
            px, py = px - 6, py + 10
        r = 11
        draw.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                     outline=(255, 255, 255), width=2)
        fnt = SANS_B(13)
        tw = draw.textlength(str(num), font=fnt)
        draw.text((px - tw / 2, py - 7), str(num), font=fnt,
                  fill=(255, 255, 255))
        if label:
            lf = SANS_B(11)
            lx, ly = px + dx, py + dy
            draw.line([px, py, lx + (8 if dx >= 0 else -8), ly + 6],
                      fill=RED, width=1)
            draw.text((lx, ly), label, font=lf, fill=RED)


def story_block(draw, x, y, width, num, kicker, headline, body,
                head_size=18, head_lines=2, body_size=13, body_lines=3):
    """One numbered story; returns y just below the block."""
    chip = 22
    draw.ellipse([x, y, x + chip, y + chip], fill=RED)
    fnt = SANS_B(13)
    tw = draw.textlength(str(num), font=fnt)
    draw.text((x + (chip - tw) / 2, y + 4), str(num), font=fnt,
              fill=(255, 255, 255))
    kx = x + chip + 8
    draw.text((kx, y + 3), kicker, font=SANS_B(11), fill=RED)
    y += 26
    y = draw_wrapped(draw, headline, SERIF_B(head_size), x, y, width,
                     max_lines=head_lines, spacing=2)
    y += 2
    y = draw_wrapped(draw, body, SANS(body_size), x, y, width,
                     max_lines=body_lines, spacing=3)
    return y


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead (0-112) ----
    d.text((512, 8), "THE WORLD IN ONE DAY", font=SERIF_B(54),
           fill=INK, anchor="ma")
    d.line([24, 76, 1000, 76], fill=RULE, width=2)
    d.text((512, 82), "THURSDAY, 26 NOVEMBER 2026", font=SANS_B(20),
           fill=RED, anchor="ma")
    d.text((24, 86), "ONE DAY", font=SANS_B(13), fill=GREY)
    d.text((1000, 86), "TEN STORIES  •  EVERY REGION", font=SANS_B(13),
           fill=GREY, anchor="ra")
    d.line([24, 112, 1000, 112], fill=RULE, width=3)

    # ---- lead story (left, 122-400) ----
    lx, lw = 24, 576
    d.text((lx, 124), "1  •  STRAIT OF HORMUZ", font=SANS_B(12), fill=RED)
    y = draw_wrapped(d, "Two tankers hit mines and burn in the Strait of Hormuz",
                     SERIF_B(33), lx, 144, lw, max_lines=3, spacing=2)
    y += 4
    y = draw_wrapped(
        d,
        "Iran's Revolutionary Guards said two oil tankers struck naval "
        "mines and exploded in the Strait of Hormuz, the world's busiest "
        "oil waterway, and warned ships using unauthorised routes face "
        "attack. Tehran vowed tighter control of the strait as the U.S. "
        "naval blockade bites.",
        SANS(15), lx, y, lw, max_lines=5, spacing=4)
    # small drawn scene: tanker, smoke, sea
    sy = 352
    d.rectangle([lx, sy, lx + lw, sy + 46], fill=MAP_OCEAN, outline=RULE)
    d.rectangle([lx + 120, sy + 32, lx + 460, sy + 42], fill=(40, 40, 40))
    d.rectangle([lx + 150, sy + 20, lx + 190, sy + 32], fill=(40, 40, 40))
    d.rectangle([lx + 400, sy + 24, lx + 430, sy + 32], fill=(40, 40, 40))
    for cx, cy, cr in [(170, 16, 9), (190, 12, 11), (215, 16, 8),
                       (420, 15, 8), (440, 11, 10)]:
        d.ellipse([lx + cx - cr, sy + cy - cr, lx + cx + cr, sy + cy + cr],
                  fill=(120, 120, 120))
    d.text((lx + 8, sy + 5), "TANKERS BURN IN THE STRAIT",
           font=SANS_B(10), fill=NAVY)

    # ---- right column: stories 2-4 (122-400) ----
    rx, rw = 624, 376
    d.line([608, 122, 608, 400], fill=RULE, width=1)
    y = story_block(
        d, rx, 122, rw, 2, "SAUDI ARABIA",
        "Houthis strike Ras Tanura refinery",
        "Houthis hit Saudi Arabia's largest refinery; the coalition said "
        "it downed seven drones over Ras Tanura.",
        head_size=17, head_lines=1, body_size=13, body_lines=2)
    y += 6
    d.line([rx, y, rx + rw, y], fill=FAINT, width=1)
    y += 8
    y = story_block(
        d, rx, y, rw, 3, "THE STRAIT",
        "Iran offers to reopen Hormuz in 48h",
        "Tehran offered to reopen Hormuz in 48 hours if the U.S. lifts "
        "its blockade, via Qatari mediators.",
        head_size=17, head_lines=1, body_size=13, body_lines=2)
    y += 6
    d.line([rx, y, rx + rw, y], fill=FAINT, width=1)
    y += 8
    y = story_block(
        d, rx, y, rw, 4, "GAZA",
        "Israel kills Hamas security chief",
        "Israel killed Hamas security chief Mohammad Abuelouf, his wife "
        "and two children in Gaza, medics said.",
        head_size=17, head_lines=1, body_size=13, body_lines=2)
    assert y <= 402, "right column overflow: %d" % y

    # ---- map band (408-544) ----
    d.text((24, 408), "WHERE IT HAPPENED", font=SANS_B(12), fill=RED)
    d.text((1000, 408), "NUMBERS MATCH THE STORIES", font=SANS_B(11),
           fill=GREY, anchor="ra")
    draw_map(d)

    # ---- stories 5-10, two columns (556-884) ----
    y0 = 556
    col_w = 468
    left = [
        (5, "SPACE",
         "Pakistan's first astronaut reaches orbit",
         "China's Shenzhou-24 carried Pakistani pilot Muhammad Zeeshan Ali "
         "to Tiangong, the first foreign astronaut in China's crewed "
         "programme."),
        (6, "UNITED STATES",
         "U.S. economy grew 4.3% in Q3",
         "America's economy grew 4.3% in Q3, the fastest in three years, "
         "the BEA said, revising its 3.4% estimate sharply up."),
        (7, "UNITED STATES",
         "Thanksgiving storms threaten 250 million",
         "Twin storms batter both U.S. coasts on the busiest travel day, "
         "with 70 mph gusts in the east and record king tides in "
         "San Francisco."),
    ]
    right = [
        (8, "SPAIN",
         "Record 2,100 migrants reach Canary Islands",
         "More than 2,100 migrants reached Spain's Canary Islands in 24 "
         "hours, a daily record. One was found dead; another gave birth "
         "en route."),
        (9, "UKRAINE WAR",
         "Kremlin rejects Johnson's Ukraine force call",
         "The Kremlin rejected Boris Johnson's call for a token Western "
         "force in Ukraine as unacceptable, as Kyiv keeps hitting oil "
         "plants."),
        (10, "UKRAINE WAR",
         "Russia strikes Odesa, killing two",
         "A Russian strike on Odesa region killed two and injured three, "
         "including a child, the governor said, as Russian forces also "
         "hit Kyiv."),
    ]
    for col_x, stories in ((24, left), (532, right)):
        y = y0
        for i, (num, kicker, head, body) in enumerate(stories):
            y = story_block(d, col_x, y, col_w, num, kicker, head, body,
                            head_size=18, head_lines=2, body_size=13,
                            body_lines=2)
            if i < 2:
                y += 10
                d.line([col_x, y, col_x + col_w, y], fill=FAINT, width=1)
                y += 10
        assert y <= 884, "column overflow: %d" % y
    d.line([516, y0, 516, 884], fill=RULE, width=1)

    # ---- ALSO TODAY band (892-968) ----
    by = 888
    d.rectangle([24, by, 1000, by + 88], fill=NAVY)
    d.text((40, by + 8), "ALSO TODAY", font=SANS_B(13), fill=(255, 210, 90))
    also = (
        "Eurostar cancels London\u2013Paris\u2013Brussels trains in strike  \u2022  "
        "Iraq's top court lets Baghdad deploy troops in Kurdistan  \u2022  "
        "Senegal reinstated as Africa Cup of Nations champions  \u2022  "
        "U.S. warns citizens at 10 Middle East missions  \u2022  "
        "Iran's rial passes 2.85m to the dollar  \u2022  "
        "U.S. core PCE hits 3.3%  \u2022  "
        "Abrego Garcia reaches Spain  \u2022  "
        "U.S. Army detonates 5 tons of bomb chemicals in Iowa  \u2022  "
        "100th Macy's parade balloons may be grounded")
    draw_wrapped(d, also, SANS(13), 40, by + 30, 944, fill=(255, 255, 255),
                 max_lines=3, spacing=4)

    # ---- footer ----
    d.line([24, 984, 1000, 984], fill=RULE, width=1)
    d.text((24, 992),
           "Sources: Reuters, AP, BBC, TRT World. All stories first reported "
           "Wednesday 25 November 2026.",
           font=SANS(11), fill=GREY)
    d.text((1000, 992), "make.fun  •  news-image-20261126",
           font=SANS(11), fill=GREY, anchor="ra")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, format="PNG", optimize=True)
    data = open(out, "rb").read()
    print("wrote %s %d bytes sha256 %s"
          % (out, len(data), hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
