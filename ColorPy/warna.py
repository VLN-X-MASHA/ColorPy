# Warna.py
import builtins
import re

RESET = "\033[0m"

# ===== BASIC COLORS ===== #
BASIC_COLORS = {
    "BLACK": 30, "RED": 31, "GREEN": 32, "YELLOW": 33,
    "BLUE": 34, "MAGENTA": 35, "CYAN": 36, "WHITE": 37
}

# ===== TEXT STYLES ===== #
STYLES = {
    "B": 1,   # Bold
    "I": 3,   # Italic
    "U": 4    # Underline
}

# ===========================================================
# BASIC COLOR PARSER   {GREEN}, {RED(B)}, {BLUE(BG)}, {CYAN(B, BG)}
# ===========================================================
def apply_basic(match):
    name = match.group(1).upper()
    inside = match.group(2)

    if name not in BASIC_COLORS:
        return match.group(0)

    base = BASIC_COLORS[name]
    codes = [str(base)]

    if inside:
        params = [x.strip().upper() for x in inside.split(",")]

        for p in params:
            if p == "BG":  # background
                codes[0] = str(base + 10)
            elif p in STYLES:
                codes.append(str(STYLES[p]))

    return f"\033[{';'.join(codes)}m"


# ===========================================================
# 256 COLOR PARSER   {COLOR(82)}, {COLOR(200, BG)}
# ===========================================================
def apply_256(match):
    inside = match.group(1)
    parts = [x.strip().upper() for x in inside.split(",")]

    num = None
    bg = False

    for p in parts:
        if p.isdigit():
            num = int(p)
        elif p == "BG":
            bg = True

    if num is None:
        return match.group(0)

    return f"\033[{48 if bg else 38};5;{num}m"


# ===========================================================
# RGB PARSER   {RGB(255,120,20)}, {RGB(120,40,255,BG)}
# ===========================================================
def apply_rgb(match):
    parts = [x.strip().upper() for x in match.group(1).split(",")]

    if len(parts) not in (3, 4):
        return match.group(0)

    try:
        r, g, b = map(int, parts[:3])
    except:
        return match.group(0)

    bg = (len(parts) == 4 and parts[3] == "BG")

    return f"\033[{48 if bg else 38};2;{r};{g};{b}m"


# ===========================================================
# HEX PARSER   {HEX(#FF00AA)}, {HEX(FF00AA, BG)}
# ===========================================================
def apply_hex(match):
    parts = [x.strip().upper() for x in match.group(1).split(",")]

    hexcode = None
    bg = False

    for p in parts:
        if p.startswith("#"):
            hexcode = p[1:]
        elif len(p) == 6 and all(c in "0123456789ABCDEF" for c in p):
            hexcode = p
        elif p == "BG":
            bg = True

    if not hexcode or len(hexcode) != 6:
        return match.group(0)

    try:
        r = int(hexcode[0:2], 16)
        g = int(hexcode[2:4], 16)
        b = int(hexcode[4:6], 16)
    except:
        return match.group(0)

    return f"\033[{48 if bg else 38};2;{r};{g};{b}m"


# ===========================================================
# MASTER PARSER — apply ALL
# ===========================================================
def parse_color(text):
    if not isinstance(text, str):
        return text

    text = re.sub(r"\{([A-Z]+)(?:\((.*?)\))?\}", apply_basic, text)
    text = re.sub(r"\{COLOR\((.*?)\)\}", apply_256, text)
    text = re.sub(r"\{RGB\((.*?)\)\}", apply_rgb, text)
    text = re.sub(r"\{HEX\((.*?)\)\}", apply_hex, text)
    text = text.replace("{RESET}", RESET)

    return text + RESET


# ===========================================================
# OVERRIDE PRINT()
# ===========================================================
_original_print = builtins.print

def print(*args, **kwargs):
    parsed = [parse_color(a) for a in args]
    _original_print(*parsed, **kwargs)
