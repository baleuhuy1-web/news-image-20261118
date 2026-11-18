#!/usr/bin/env python3
"""Compose entry.png: a one-page newspaper front page for 18 November 2026.

Six AI-illustrated panels live in assets/.  This script arranges them in a
2x3 grid on a cream "newsprint" canvas and draws every piece of text itself
with PIL, so no lettering is ever left to the image model (which garbles
text).  The result is written to entry.png next to this script, at exactly
1024x1024 pixels and under the competition's 1 MiB limit.
"""

import os

from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
OUT_PATH = os.path.join(HERE, "entry.png")
MAX_BYTES = 1_048_576

SIZE = 1024
MARGIN = 28
GUTTER = 16
PAPER = (247, 242, 231)
INK = (22, 20, 18)
GREY = (74, 70, 64)
CRIMSON = (178, 24, 43)
WHITE = (255, 255, 255)
BLACK = (17, 17, 17)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_BOLD = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")

# (panel file, headline, subline, vertical crop focus 0=top .. 1=bottom)
STORIES = [
    ("panel1.png", "APEC OPENS IN SHENZHEN",
     "Xi urges open trade as Trump and Putin arrive in China", 0.45),
    ("panel2.png", "US SINKS FIVE IRANIAN TANKERS",
     "Tehran strikes back near Hormuz and at a base in Jordan", 0.58),
    ("panel3.png", "UKRAINE STRIKES CRIMEAN BRIDGE",
     "Record drone barrage as Russia pounds Kyiv's bridges", 0.50),
    ("panel4.png", "UN WARNS OF GAZA WINTER DEATHS",
     "1.7 million displaced face the cold without shelter", 0.50),
    ("panel5.png", "COP31 ENTERS DECISIVE PHASE",
     "Draft climate deal in Antalya still has 144 disputed items", 0.50),
    ("panel6.png", "SPACEX CATCHES A FALLING STARSHIP",
     "Tower arms catch the booster in a first for reuse", 0.45),
]

FOOTER_LINES = [
    "TRUMP MEETS MARCOS IN MANILA • NORTH KOREA FIRES BALLISTIC MISSILE",
    "PATTINSON NAMED NEW JAMES BOND",
]


def load_font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(draw, text, path, max_width, start_size, min_size=12):
    """Largest font (<= start_size) whose text fits within max_width."""
    size = start_size
    while size > min_size:
        candidate = load_font(path, size)
        if draw.textlength(text, font=candidate) <= max_width:
            return candidate
        size -= 1
    return load_font(path, min_size)


def wrap_text(draw, text, font, max_width):
    """Greedy word wrap; returns a list of lines that each fit max_width."""
    lines, current = [], ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_centered(draw, cx, y, text, font, fill):
    width = draw.textlength(text, font=font)
    draw.text((cx - width / 2, y), text, font=font, fill=fill)


def build():
    canvas = Image.new("RGB", (SIZE, SIZE), PAPER)
    draw = ImageDraw.Draw(canvas)
    content_w = SIZE - 2 * MARGIN
    cx = SIZE // 2

    # ---- masthead ------------------------------------------------------
    y = 20
    draw.rectangle([MARGIN, y, SIZE - MARGIN, y + 5], fill=INK)
    y += 10
    draw.rectangle([MARGIN, y, SIZE - MARGIN, y + 2], fill=INK)
    y += 14
    title_font = fit_font(draw, "THE WORLD TODAY", SERIF_BOLD, content_w, 118)
    bbox = draw.textbbox((0, 0), "THE WORLD TODAY", font=title_font)
    draw_centered(draw, cx, y - bbox[1], "THE WORLD TODAY", title_font, INK)
    y += (bbox[3] - bbox[1]) + 14

    band_h = 46
    draw.rectangle([MARGIN, y, SIZE - MARGIN, y + band_h], fill=CRIMSON)
    date_font = fit_font(draw, "WEDNESDAY 18 NOVEMBER 2026", SANS_BOLD,
                          content_w - 40, 28)
    dbbox = draw.textbbox((0, 0), "WEDNESDAY 18 NOVEMBER 2026", font=date_font)
    date_y = y + (band_h - (dbbox[3] - dbbox[1])) // 2 - dbbox[1]
    draw_centered(draw, cx, date_y, "WEDNESDAY 18 NOVEMBER 2026",
                  date_font, WHITE)
    y += band_h + 8
    draw.rectangle([MARGIN, y, SIZE - MARGIN, y + 2], fill=INK)
    grid_top = y + 14

    # ---- story grid ----------------------------------------------------
    footer_h = 68
    grid_bottom = SIZE - footer_h - 12
    col_w = (content_w - GUTTER) // 2
    row_h = (grid_bottom - grid_top) // 3

    head_font = load_font(SANS_BOLD, 23)
    sub_font = load_font(SANS, 16)
    head_lh, sub_lh, cap_gap = 27, 20, 4

    for row in range(3):
        pair = STORIES[row * 2: row * 2 + 2]
        # Wrap both captions first so the row's images share one height.
        wrapped = []
        cap_h = 0
        for _, headline, subline, _ in pair:
            h_lines = wrap_text(draw, headline, head_font, col_w)
            s_lines = wrap_text(draw, subline, sub_font, col_w)
            wrapped.append((h_lines, s_lines))
            height = len(h_lines) * head_lh + cap_gap + len(s_lines) * sub_lh
            cap_h = max(cap_h, height)
        img_h = row_h - cap_h - 8
        row_y = grid_top + row * row_h

        for col, (story, (h_lines, s_lines)) in enumerate(zip(pair, wrapped)):
            fname, _, _, focus = story
            x = MARGIN + col * (col_w + GUTTER)
            panel = Image.open(os.path.join(ASSETS, fname)).convert("RGB")
            panel = ImageOps.fit(panel, (col_w, img_h),
                                 method=Image.LANCZOS,
                                 centering=(0.5, focus))
            canvas.paste(panel, (x, row_y))
            draw.rectangle([x, row_y, x + col_w - 1, row_y + img_h - 1],
                           outline=INK, width=2)
            ty = row_y + img_h + 6
            for line in h_lines:
                draw.text((x, ty), line, font=head_font, fill=INK)
                ty += head_lh
            ty += cap_gap
            for line in s_lines:
                draw.text((x, ty), line, font=sub_font, fill=GREY)
                ty += sub_lh

    # ---- footer band ---------------------------------------------------
    fy = SIZE - footer_h
    draw.rectangle([0, fy, SIZE, SIZE], fill=BLACK)
    foot_font = load_font(SANS_BOLD, 20)
    line_h = 27
    total = line_h * len(FOOTER_LINES)
    ty = fy + (footer_h - total) // 2
    for line in FOOTER_LINES:
        draw_centered(draw, cx, ty, line, foot_font, WHITE)
        ty += line_h

    # ---- save, respecting the 1 MiB cap --------------------------------
    canvas.save(OUT_PATH, optimize=True)
    size = os.path.getsize(OUT_PATH)
    if size > MAX_BYTES:
        quantized = canvas.quantize(colors=256, method=Image.MEDIANCUT)
        quantized.save(OUT_PATH, optimize=True)
        size = os.path.getsize(OUT_PATH)
    print(f"entry.png: {canvas.size[0]}x{canvas.size[1]}, {size} bytes")
    return size


if __name__ == "__main__":
    build()
