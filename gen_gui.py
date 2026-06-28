from PIL import Image, ImageDraw

W, H = 256, 256
img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# ── Palette ──────────────────────────────────────────────
BG        = (18, 18, 34, 255)
PANEL     = (24, 24, 46, 255)
TITLE_BG  = (14, 14, 28, 255)
SLOT_F    = ( 8,  8, 18, 255)
SLOT_SH   = ( 4,  4,  8, 255)
SLOT_HL   = (46, 46, 90, 255)
ACCENT    = (79,195,247, 255)
ACCENT_D  = (28, 80,110, 255)
BORDER    = (34, 34, 68, 255)
DIV       = (40, 40, 80, 255)
OUT_BG    = (20, 20, 42, 255)

def slot(sx, sy):
    d.rectangle([sx, sy, sx+15, sy+15], fill=SLOT_F)
    d.line([(sx-1, sy-1), (sx+15, sy-1)], fill=SLOT_SH)
    d.line([(sx-1, sy-1), (sx-1, sy+15)], fill=SLOT_SH)
    d.line([(sx-1, sy+16), (sx+16, sy+16)], fill=SLOT_HL)
    d.line([(sx+16, sy-1), (sx+16, sy+16)], fill=SLOT_HL)

# ── Full background ──────────────────────────────────────
d.rectangle([0, 0, 175, 165], fill=BG)

# ── Crafting panel ───────────────────────────────────────
d.rectangle([0, 0, 175, 76], fill=PANEL)
d.rectangle([0, 0, 175, 76], outline=BORDER)

# Title strip
d.rectangle([1, 1, 174, 13], fill=TITLE_BG)
d.line([(2, 13), (173, 13)], fill=DIV)
d.line([(2, 14), (173, 14)], fill=(10, 10, 20, 255))

# ── Left fuel column (x=0-30) ────────────────────────────
d.rectangle([1, 15, 28, 75], fill=(20, 20, 40, 255))
d.line([(29, 15), (29, 75)], fill=DIV)
d.line([(30, 16), (30, 74)], fill=(12, 12, 22, 255))

# Lava slot at (8, 35) — drawn with orange border in screen code, no slot here

# FE bar track border at (7,62)-(22,74); interior is (8,63)-(21,73)
d.rectangle([7, 62, 22, 74], fill=(6, 6, 14, 255))
d.rectangle([7, 62, 22, 74], outline=ACCENT_D)

# ── Main inputs area ─────────────────────────────────────
slot(44, 35)
slot(80, 35)

# "+" between inputs: center x=(61+80)//2=70, center y=43
cx, cy = 70, 43
d.rectangle([cx-4, cy-1, cx+4, cy+1], fill=ACCENT_D)
d.rectangle([cx-1, cy-4, cx+1, cy+4], fill=ACCENT_D)

# ── Output section tint (x=127-157) ──────────────────────
d.rectangle([127, 15, 157, 75], fill=OUT_BG)
d.line([(127, 15), (127, 75)], fill=DIV)
d.line([(128, 16), (128, 74)], fill=(12, 12, 22, 255))

# Output slot with teal glow rings
slot(134, 35)
d.rectangle([133, 34, 151, 52], outline=ACCENT_D)
d.rectangle([132, 33, 152, 53], outline=(18, 55, 75, 255))

# ── Progress bar track (99,31)-(130,48) ──────────────────
d.rectangle([99, 31, 130, 48], fill=(6, 6, 14, 255))
d.rectangle([99, 31, 130, 48], outline=ACCENT_D)
# Dim baked arrow hint
for i in range(5):
    y1, y2 = 36 + i, 43 - i
    if y2 >= y1:
        d.line([(121+i, y1), (121+i, y2)], fill=(26, 26, 52, 255))

# ── Corner accents on crafting panel ─────────────────────
for pts in [
    ([2, 2, 7, 3],   [2, 2,   3,  7]),
    ([168,2,173,3],  [172,2, 173,  7]),
    ([2, 73,7, 74],  [2, 69,  3,  74]),
    ([168,73,173,74],[172,69,173, 74]),
]:
    for r in pts:
        d.rectangle(r, fill=ACCENT_D)

# ── Separator (crafting → inventory) ─────────────────────
d.line([(7, 78), (168, 78)], fill=DIV)
d.line([(7, 79), (168, 79)], fill=(10, 10, 20, 255))

# ── Player inventory 3×9 at (8, 84) ──────────────────────
for row in range(3):
    for col in range(9):
        slot(8 + col*18, 84 + row*18)

# Separator (inventory → hotbar)
d.line([(7, 140), (168, 140)], fill=DIV)
d.line([(7, 141), (168, 141)], fill=(10, 10, 20, 255))

# ── Hotbar 9 slots at (8, 142) ───────────────────────────
for col in range(9):
    slot(8 + col*18, 142)

out = r'C:\Users\thoma\Desktop\AbyssalWeapons\src\main\resources\assets\abyssalweapons\textures\gui\nicronium_infuser.png'
img.save(out)
print("Saved:", out)
