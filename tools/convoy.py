"""Convoys of the ancient world: round-hulled merchant ships (no game needed, ~1 s).

The engine's convoy equipment (convoy / convoy_1) stays - trade with far-away countries and naval invasions need it.
Every country gets some at the start (world.py: set_convoys, more for more harbours). This tool only renames and
redraws it, at the base game's own paths:
  gfx/interface/archetypes/archetype_convoy.dds   (144 x 29, tan, two ships)   equipment type picture
  gfx/interface/technologies/convoy.dds           (256 x 42, two ships)        production picture
  gfx/interface/topbar/topbar_convoys.dds         (28 x 18, a ship on waves)   top bar
  localisation/english/replace/ante_convoy_l_english.yml
Run AFTER tools/world.py (it wipes localisation/english/replace).
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

MOD = Path(__file__).resolve().parent.parent
S = 8

LOC = {
    "convoy": "Merchant Ships",
    "convoy_desc": "Round-hulled sailing ships with deep holds: they carry grain, metal, wine and oil between the "
                   "harbours of the sea - and soldiers, when the city goes to war overseas.",
    "convoy_1": "Merchant Ships",
    "convoy_1_short": "Merchants",
    "convoy_1_desc": "Round-hulled sailing ships with deep holds: they carry grain, metal, wine and oil between the "
                     "harbours of the sea - and soldiers, when the city goes to war overseas.",
}


def ship_mask(w, h, scale=1.0, dx=0.0):
    """a merchant ship seen from the side, filling a w x h box (drawn S times larger)"""
    im = Image.new("L", (w * S, h * S), 0)
    d = ImageDraw.Draw(im)
    W, H = w * S, h * S

    def P(x, y):
        return (dx * W + x * W * scale, y * H)
    # deep round hull, the stern post curling up (right), a short bow (left)
    hull = [P(0.04, 0.62), P(0.12, 0.84), P(0.30, 0.95), P(0.70, 0.95), P(0.86, 0.84), P(0.95, 0.62),
            P(0.97, 0.42), P(0.93, 0.36), P(0.90, 0.48), P(0.86, 0.60), P(0.10, 0.60)]
    d.polygon(hull, 255)
    d.line([P(0.95, 0.62), P(0.98, 0.38), P(0.94, 0.30)], 255, int(0.05 * H))
    # mast, yard and the big square sail, slightly bellied
    d.line([P(0.47, 0.62), P(0.47, 0.02)], 255, max(1, int(0.045 * W * scale)))
    d.line([P(0.18, 0.08), P(0.76, 0.08)], 255, max(1, int(0.05 * H)))
    d.polygon([P(0.20, 0.10), P(0.74, 0.10), P(0.71, 0.52), P(0.47, 0.56), P(0.23, 0.52)], 255)
    # steering oar at the stern
    d.line([P(0.84, 0.58), P(0.80, 0.98)], 255, max(1, int(0.03 * W * scale)))
    return im.resize((w, h), Image.LANCZOS)


def shaded(mask, base, outline=(30, 22, 14)):
    w, h = mask.size
    grad = Image.linear_gradient("L").resize((w, h))
    light = Image.new("RGBA", (w, h), tuple(min(255, int(c * 1.3)) for c in base) + (255,))
    dark = Image.new("RGBA", (w, h), tuple(int(c * 0.6) for c in base) + (255,))
    body = Image.composite(dark, light, grad)
    edge = Image.eval(mask, lambda v: 255 if v > 0 else 0).filter(ImageFilter.MaxFilter(3))
    ol = Image.new("RGBA", (w, h), outline + (255,))
    ol.putalpha(edge)
    body.putalpha(mask)
    return Image.alpha_composite(ol, body)


def two_ships(w, h, base):
    """a little fleet in a wide picture: ships in their true shape (1.6 : 1), the ones behind smaller and darker"""
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    big = (int(h * 1.6), h)
    small = (int(h * 0.8 * 1.6), int(h * 0.8))
    n = max(2, min(3, w // big[0]))
    for i in range(n - 1, -1, -1):          # back to front
        size = small if i % 2 else big
        x = int(i * (w - big[0]) / max(1, n - 1))
        col = tuple(int(c * (0.85 if i % 2 else 1.0)) for c in base)
        out.alpha_composite(shaded(ship_mask(*size), col), (x, h - size[1]))
    return out


def main():
    gi = MOD / "gfx" / "interface"
    for sub in ("archetypes", "technologies", "topbar"):
        (gi / sub).mkdir(parents=True, exist_ok=True)
    two_ships(144, 29, (188, 150, 98)).save(gi / "archetypes" / "archetype_convoy.dds")
    two_ships(256, 42, (150, 112, 74)).save(gi / "technologies" / "convoy.dds")
    top = Image.new("RGBA", (28, 18), (0, 0, 0, 0))
    top.alpha_composite(shaded(ship_mask(22, 13), (214, 172, 104)), (3, 0))
    d = ImageDraw.Draw(top)
    for y in (14, 16):
        d.line([(2, y), (8, y - 1), (14, y), (20, y - 1), (26, y)], fill=(70, 120, 170, 255), width=1)
    top.save(gi / "topbar" / "topbar_convoys.dds")
    p = MOD / "localisation" / "english" / "replace" / "ante_convoy_l_english.yml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("l_english:\n" + "".join(f' {k}:0 "{v}"\n' for k, v in LOC.items()), encoding="utf-8-sig", newline="\n")
    print("written: merchant ships (convoy pictures and names)")


if __name__ == "__main__":
    main()
