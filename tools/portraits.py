"""Procedural leader portraits (our own art, no game files, ~2 s).

Draws a painted-looking bust for every leader in tools/data/leaders_509bc.py, in the dress of his or her
people (Roman laurel and toga, Persian crenellated crown, Scythian pointed hat, Greek helmet, ...), and writes
gfx/leaders/ante/<TAG>_<key>.dds (156 x 210 RGBA, the base game's portrait size). tools/content.py points the
characters at these files. `--preview FILE` also writes a contact sheet PNG.
"""
import hashlib
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

MOD = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from data.leaders_509bc import LEADERS  # noqa: E402

W, H, S = 156, 210, 4  # portrait size, supersampling

SKIN = {"med": (196, 152, 114), "pale": (226, 186, 158), "olive": (184, 140, 100), "dark": (104, 66, 44),
        "brown": (160, 112, 78)}
HAIR = {"black": (34, 28, 24), "brown": (82, 56, 36), "fair": (176, 140, 82), "red": (140, 70, 36),
        "grey": (150, 146, 140)}

# style per country: skin, hair choices, clothes colour, accent, headgear, beard, extras
STYLE = {
    "roman": dict(skin="med", hair=["black", "brown"], cloth=(226, 220, 204), accent=(110, 30, 70), head="laurel",
                  beard="none", hairstyle="short", bg=(70, 30, 30)),
    # the kings of Rome (Tarquinius): toga picta, beard, golden crown (accent = crown colour)
    "roman_king": dict(skin="med", hair=["black", "brown"], cloth=(120, 40, 80), accent=(212, 170, 60), head="crown",
                       beard="full", hairstyle="short", bg=(90, 30, 50)),
    "etruscan": dict(skin="med", hair=["black"], cloth=(150, 50, 40), accent=(200, 160, 60), head="diadem",
                     beard="short", hairstyle="long", bg=(60, 40, 30)),
    "latin": dict(skin="med", hair=["black", "brown"], cloth=(170, 150, 120), accent=(120, 60, 40), head="none",
                  beard="short", hairstyle="short", bg=(55, 45, 35)),
    "greek": dict(skin="olive", hair=["black", "brown"], cloth=(210, 200, 180), accent=(40, 70, 130), head="none",
                  beard="full", hairstyle="curly", bg=(30, 45, 70)),
    "spartan": dict(skin="olive", hair=["black", "brown"], cloth=(150, 30, 30), accent=(190, 150, 70),
                    head="corinthian", beard="full", hairstyle="long", bg=(60, 25, 25)),
    "macedonian": dict(skin="olive", hair=["brown", "black"], cloth=(120, 40, 60), accent=(200, 170, 80),
                       head="kausia", beard="full", hairstyle="curly", bg=(40, 35, 55)),
    "persian": dict(skin="olive", hair=["black"], cloth=(90, 40, 110), accent=(214, 176, 70), head="crown",
                    beard="long", hairstyle="bun", bg=(70, 55, 25)),
    "punic": dict(skin="olive", hair=["black"], cloth=(120, 30, 80), accent=(210, 180, 90), head="cone",
                  beard="long", hairstyle="short", bg=(50, 25, 50)),
    "kushite": dict(skin="dark", hair=["black"], cloth=(230, 220, 190), accent=(214, 176, 70), head="kushite",
                    beard="none", hairstyle="none", bg=(70, 50, 25)),
    "libyan": dict(skin="brown", hair=["black"], cloth=(170, 120, 70), accent=(200, 200, 190), head="feathers",
                   beard="short", hairstyle="lock", bg=(80, 60, 35)),
    "scythian": dict(skin="med", hair=["brown", "red", "fair"], cloth=(150, 50, 30), accent=(210, 170, 60),
                     head="pointed", beard="full", hairstyle="long", bg=(60, 45, 30)),
    "saka": dict(skin="med", hair=["black", "brown"], cloth=(70, 80, 50), accent=(210, 170, 60), head="tall",
                 beard="full", hairstyle="long", bg=(50, 50, 35)),
    "thracian": dict(skin="med", hair=["brown", "red"], cloth=(110, 60, 40), accent=(200, 160, 60), head="fox",
                     beard="full", hairstyle="long", bg=(45, 40, 30)),
    "illyrian": dict(skin="med", hair=["brown", "black"], cloth=(90, 70, 50), accent=(190, 150, 70), head="cap",
                     beard="full", hairstyle="long", bg=(40, 40, 40)),
    "celtic": dict(skin="pale", hair=["fair", "red", "brown"], cloth=(60, 100, 60), accent=(214, 176, 70),
                   head="none", beard="moustache", hairstyle="flowing", bg=(30, 50, 35)),
    "iberian": dict(skin="med", hair=["black", "brown"], cloth=(36, 32, 30), accent=(150, 40, 30), head="none",
                    beard="short", hairstyle="short", bg=(55, 35, 30)),
    "arabian": dict(skin="brown", hair=["black"], cloth=(220, 210, 190), accent=(150, 110, 60), head="wrap",
                    beard="full", hairstyle="none", bg=(85, 65, 40)),
    "anatolian": dict(skin="olive", hair=["black", "brown"], cloth=(70, 70, 120), accent=(160, 40, 40),
                      head="phrygian", beard="full", hairstyle="curly", bg=(45, 35, 55)),
    "caucasian": dict(skin="med", hair=["black", "brown"], cloth=(90, 50, 40), accent=(200, 160, 60), head="fur",
                      beard="full", hairstyle="none", bg=(40, 40, 45)),
    "nuragic": dict(skin="med", hair=["black"], cloth=(110, 80, 50), accent=(170, 130, 60), head="horned",
                    beard="short", hairstyle="long", bg=(45, 40, 30)),
    "northern": dict(skin="pale", hair=["fair", "red", "brown"], cloth=(80, 90, 60), accent=(214, 176, 70),
                     head="none", beard="full", hairstyle="flowing", bg=(30, 45, 40)),
}
LEADER_STYLE = {"ROM_tarquinius": "roman_king"}   # a leader who looks unlike his people
TAG_STYLE = {"ROM": "roman", "CAR": "punic", "PRS": "persian", "ATH": "greek", "LAK": "spartan", "CLU": "etruscan",
             "LAT": "latin", "MKD": "macedonian", "SCY": "scythian", "KSH": "kushite", "KYR": "greek",
             "SAK": "saka", "AGA": "scythian", "KRO": "greek", "ODR": "thracian", "MSG": "saka", "SAU": "scythian",
             "NEU": "northern", "FEN": "northern", "SIG": "saka", "GTA": "thracian", "PAN": "illyrian",
             "BUD": "northern", "AES": "northern", "GAE": "libyan", "LUG": "northern", "THY": "scythian",
             "ISS": "saka", "SYR": "greek", "THL": "greek", "SEN": "celtic"}


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3])


def mix(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


class Canvas:
    def __init__(self):
        self.im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 255))
        self.d = ImageDraw.Draw(self.im)

    def P(self, pts):
        return [(x * S, y * S) for x, y in pts]

    def ell(self, box, fill, outline=None, width=0):
        x0, y0, x1, y1 = box
        self.d.ellipse((x0 * S, y0 * S, x1 * S, y1 * S), fill=fill, outline=outline, width=width * S)

    def poly(self, pts, fill):
        self.d.polygon(self.P(pts), fill=fill)

    def line(self, pts, fill, width):
        self.d.line(self.P(pts), fill=fill, width=int(width * S), joint="curve")

    def arc(self, box, a0, a1, fill, width):
        x0, y0, x1, y1 = box
        self.d.arc((x0 * S, y0 * S, x1 * S, y1 * S), a0, a1, fill=fill, width=int(width * S))

    def soft(self, draw_fn, blur, alpha=255):
        """draw on a separate layer, blur it and composite (shadows / highlights)"""
        layer = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        draw_fn(d)
        layer = layer.filter(ImageFilter.GaussianBlur(blur * S))
        if alpha < 255:
            a = layer.getchannel("A").point(lambda v: v * alpha // 255)
            layer.putalpha(a)
        self.im = Image.alpha_composite(self.im, layer)
        self.d = ImageDraw.Draw(self.im)


def background(cv, base, rnd):
    top, bottom = shade(base, 1.25), shade(base, 0.45)
    for y in range(H * S):
        cv.d.line((0, y, W * S, y), fill=mix(top, bottom, y / (H * S)) + (255,))
    # a lighter glow behind the head
    cv.soft(lambda d: d.ellipse((20 * S, 20 * S, 136 * S, 150 * S), fill=shade(base, 1.9) + (110,)), 22)


def portrait(style, female, seed):
    st = STYLE[style]
    rnd = random.Random(seed)
    skin = shade(SKIN[st["skin"]], rnd.uniform(0.93, 1.06))
    hair = HAIR[rnd.choice(st["hair"])]
    if not female and rnd.random() < 0.2:
        hair = mix(hair, HAIR["grey"], 0.55)
    cloth, acc = st["cloth"], st["accent"]
    cv = Canvas()
    background(cv, st["bg"], rnd)
    dark_skin, light_skin = shade(skin, 0.72), shade(skin, 1.12)
    hs = st["hairstyle"]
    beard = "none" if female else st["beard"]
    if not female and beard in ("full", "short") and rnd.random() < 0.3:  # some variety among the generic faces
        beard = rnd.choice(["short", "full", "moustache"])

    # --- hair behind the head
    if female or hs in ("long", "flowing"):
        drop = 165 if (female or hs == "flowing") else 140
        cv.poly([(46, 70), (110, 70), (116, drop), (40, drop)], hair)
        cv.ell((44, 44, 112, 100), hair)
    if hs == "bun":
        cv.ell((92, 82, 116, 112), hair)

    # --- shoulders and clothes
    cv.ell((2, 150, 154, 290), cloth)
    cv.soft(lambda d: d.ellipse((90 * S, 160 * S, 170 * S, 300 * S), fill=(0, 0, 0, 120)), 10)
    if style in ("roman", "latin", "roman_king"):  # toga: diagonal fold with a purple border
        cv.line([(30, 168), (96, 210)], shade(cloth, 0.8), 6)
        if style == "roman":
            cv.line([(22, 176), (84, 214)], acc, 5)
    elif style in ("greek", "macedonian", "punic", "kushite"):
        cv.line([(36, 162), (80, 210)], shade(cloth, 0.8), 4)
        cv.line([(120, 162), (100, 210)], shade(cloth, 0.85), 3)
    elif style == "spartan":  # bronze cuirass under the red cloak
        cv.poly([(46, 160), (110, 160), (116, 210), (40, 210)], (176, 132, 60))
        cv.line([(78, 166), (78, 210)], (130, 94, 40), 2)
    else:  # caftan / tunic with a trimmed edge
        cv.line([(78, 156), (60, 210)], acc, 4)
    # neck
    cv.poly([(64, 112), (92, 112), (94, 158), (62, 158)], dark_skin)
    if style == "celtic":  # checked cloak
        for x in range(10, 150, 14):
            cv.line([(x, 160), (x - 10, 210)], shade(cloth, 0.75), 1.5)
        for y in range(170, 210, 12):
            cv.line([(0, y), (156, y - 6)], shade(cloth, 1.2), 1.5)
    if style in ("northern", "illyrian", "thracian", "scythian", "saka", "celtic"):  # torc
        cv.arc((56, 138, 100, 170), 200, 340, acc, 5)

    # --- head
    cv.ell((46, 82, 58, 104), dark_skin)   # ears
    cv.ell((98, 82, 110, 104), dark_skin)
    cv.ell((50, 46, 106, 130), skin)
    # modelling: shadow on the right cheek, light on the forehead
    cv.soft(lambda d: d.ellipse((84 * S, 60 * S, 116 * S, 132 * S), fill=shade(skin, 0.6) + (150,)), 7)
    cv.soft(lambda d: d.ellipse((60 * S, 54 * S, 88 * S, 78 * S), fill=light_skin + (120,)), 6)

    # --- hair on top
    if hs in ("short", "curly", "long", "flowing", "lock", "bun") or female:
        cv.d.chord(((48) * S, (40) * S, (108) * S, (100) * S), 180, 360, fill=hair)
        if hs == "curly":
            for i in range(9):
                x = 52 + i * 6.3
                cv.ell((x - 4, 44 + (i % 2) * 2, x + 4, 52 + (i % 2) * 2), shade(hair, 1.25))
        if hs == "lock":  # Libyan side lock
            cv.poly([(50, 70), (56, 70), (54, 120), (48, 118)], hair)

    # --- face
    eye_y = 84
    for ex in (66, 88):
        cv.ell((ex - 6, eye_y - 3, ex + 6, eye_y + 4), (232, 226, 214))
        cv.ell((ex - 2.6, eye_y - 2.4, ex + 2.6, eye_y + 3), (40, 30, 24))
        cv.line([(ex - 7, eye_y - 7), (ex + 6, eye_y - 8)], shade(hair, 0.9), 2.2)  # brows
        cv.line([(ex - 6, eye_y - 3.5), (ex + 6, eye_y - 3.5)], shade(skin, 0.55), 1)  # lids
    cv.line([(78, 86), (76, 104), (81, 106)], shade(skin, 0.62), 1.8)  # nose
    cv.soft(lambda d: d.ellipse((72 * S, 100 * S, 84 * S, 108 * S), fill=shade(skin, 0.7) + (120,)), 2)

    # --- beard
    if beard != "none":
        bc = shade(hair, 0.95)
        if beard == "moustache":  # the long drooping moustache of the Celts
            cv.poly([(64, 106), (78, 101), (92, 106), (95, 124), (90, 124), (86, 110), (78, 107), (70, 110),
                     (66, 124), (61, 124)], bc)
        elif beard == "short":
            cv.poly([(52, 98), (60, 120), (78, 132), (96, 120), (104, 98), (98, 114), (78, 122), (58, 114)], bc)
        else:
            low = 150 if beard == "full" else 168
            cv.poly([(51, 94), (54, 118), (66, low - 10), (78, low), (90, low - 10), (102, 118), (105, 94),
                     (96, 110), (78, 114), (60, 110)], bc)
            if beard == "long":  # Persian / Punic: rows of curls
                for y in range(120, low - 6, 7):
                    cv.line([(62 + (y - 120) * 0.25, y), (94 - (y - 120) * 0.25, y)], shade(bc, 1.35), 1.5)
        if beard != "moustache":
            cv.poly([(66, 106), (78, 102), (90, 106), (86, 109), (78, 107), (70, 109)], bc)  # moustache
    mouth_c = shade(skin, 0.5) if beard == "none" else (60, 40, 34)
    cv.line([(71, 114), (78, 115), (85, 114)], mouth_c, 1.6)
    if female:
        cv.line([(72, 114), (78, 116), (84, 114)], (150, 70, 70), 2)

    # --- headgear
    head = st["head"]
    if head == "laurel":
        for i in range(11):
            t = i / 10
            x = 50 + t * 56
            y = 64 - 18 * (1 - (2 * t - 1) ** 2)
            cv.ell((x - 5, y - 3, x + 5, y + 4), (70, 110, 50))
            cv.ell((x - 3, y - 2, x + 2, y + 1), (110, 150, 70))
    elif head == "diadem":
        cv.d.arc((49 * S, 48 * S, 107 * S, 100 * S), 190, 350, fill=acc, width=4 * S)
    elif head == "corinthian":
        bronze = (184, 140, 62)
        cv.d.chord((44 * S, 32 * S, 112 * S, 106 * S), 180, 360, fill=bronze)
        cv.poly([(44, 69), (54, 69), (56, 112), (46, 104)], bronze)   # cheek guards
        cv.poly([(102, 69), (112, 69), (110, 104), (100, 112)], bronze)
        cv.poly([(75, 69), (81, 69), (80, 92), (76, 92)], bronze)     # nose guard
        cv.arc((40, 6, 116, 66), 200, 340, (170, 30, 30), 9)          # crest
        cv.soft(lambda d: d.ellipse((56 * S, 38 * S, 76 * S, 56 * S), fill=(255, 240, 200, 120)), 4)
    elif head == "kausia":
        cv.ell((36, 38, 120, 64), shade(cloth, 1.1))
        cv.ell((48, 34, 108, 56), shade(cloth, 1.2))
    elif head == "crown":
        cv.poly([(50, 62), (106, 62), (104, 30), (50, 30)], acc)
        for i in range(5):
            x = 52 + i * 11
            cv.poly([(x, 30), (x + 7, 30), (x + 3.5, 20)], acc)
        cv.line([(50, 56), (106, 56)], shade(acc, 0.7), 2)
        cv.soft(lambda d: d.ellipse((56 * S, 30 * S, 80 * S, 50 * S), fill=(255, 245, 210, 110)), 4)
    elif head == "cone":
        cv.poly([(50, 64), (106, 64), (90, 30), (66, 30)], shade(cloth, 1.15))
        cv.line([(50, 62), (106, 62)], acc, 3)
    elif head == "kushite":
        cv.d.chord((48 * S, 40 * S, 108 * S, 102 * S), 180, 360, fill=(30, 26, 26))
        cv.line([(48, 70), (108, 70)], acc, 3.5)
        for x in (72, 84):  # the two uraei
            cv.poly([(x - 3, 66), (x + 3, 66), (x + 2, 54), (x, 50), (x - 2, 54)], acc)
    elif head == "feathers":
        for x, lean in ((62, -6), (92, 6)):
            cv.poly([(x - 3, 50), (x + 3, 50), (x + lean + 2, 10), (x + lean - 2, 12)], (236, 232, 220))
    elif head == "wrap":  # Arabian head cloth falling to the shoulders, held by a cord
        cv.poly([(44, 76), (48, 44), (78, 36), (108, 44), (112, 76), (118, 160), (100, 160), (102, 80),
                 (54, 80), (56, 160), (38, 160)], cloth)
        cv.line([(48, 66), (108, 66)], (40, 34, 30), 3)
    elif head == "phrygian":  # soft cap with the tip bent forward
        cv.poly([(46, 76), (110, 76), (108, 50), (96, 32), (76, 26), (58, 30), (50, 44)], shade(acc, 1.0))
        cv.poly([(58, 30), (44, 30), (40, 40), (52, 42)], shade(acc, 0.85))
        cv.line([(46, 75), (110, 75)], shade(acc, 0.6), 2)
    elif head == "fur":  # tall fur hat of the mountains
        cv.ell((42, 32, 114, 76), (70, 56, 44))
        for i in range(8):
            cv.ell((44 + i * 8, 36 + (i % 2) * 3, 54 + i * 8, 46 + (i % 2) * 3), (96, 78, 60))
    elif head == "horned":  # the horned helmets of the Sardinian bronze figurines
        cv.d.chord((48 * S, 38 * S, 108 * S, 100 * S), 180, 360, fill=(120, 96, 56))
        cv.line([(52, 56), (40, 40), (36, 20)], (200, 186, 150), 5)
        cv.line([(104, 56), (116, 40), (120, 20)], (200, 186, 150), 5)
        cv.line([(48, 68), (108, 68)], (90, 70, 40), 2)
    elif head in ("pointed", "tall", "fox", "cap"):
        felt = {"pointed": shade(cloth, 1.2), "tall": (60, 50, 40), "fox": (170, 100, 50), "cap": (110, 90, 60)}[head]
        tip = {"pointed": (90, 4), "tall": (82, -6), "fox": (80, 22), "cap": (78, 36)}[head]
        cv.poly([(46, 74), (110, 74), (106, 50), tip, (52, 46)], felt)
        if head in ("pointed", "tall", "fox"):  # ear flaps
            cv.poly([(46, 72), (56, 72), (56, 112), (48, 110)], shade(felt, 0.9))
            cv.poly([(100, 72), (110, 72), (108, 110), (100, 112)], shade(felt, 0.9))
        cv.line([(46, 73), (110, 73)], acc if head != "fox" else (230, 220, 200), 3)

    # --- finish: zoom on the bust, brush strokes, canvas, vignette, downsample
    zw, zh = 124, 167  # crop with the portrait's aspect ratio: the head fills more of the frame
    zx, zy = (W - zw) // 2, 14
    im = cv.im.crop((zx * S, zy * S, (zx + zw) * S, (zy + zh) * S)).resize((W * 2, H * 2), Image.LANCZOS)
    im = im.convert("RGB").filter(ImageFilter.ModeFilter(5)).filter(ImageFilter.GaussianBlur(0.8))  # dabs of paint
    # canvas: coarse blotches of light and dark, plus fine grain
    blot = Image.effect_noise((W // 6, H // 6), 40).resize((W * 2, H * 2), Image.BICUBIC)
    grain = Image.effect_noise((W * 2, H * 2), 18)
    tex = Image.blend(blot, grain, 0.35)
    im = Image.blend(im, Image.merge("RGB", (tex,) * 3), 0.07)
    vig = Image.new("L", im.size, 0)
    ImageDraw.Draw(vig).ellipse((-40, -20, W * 2 + 40, H * 2 + 60), fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(40))
    im = Image.composite(im, Image.new("RGB", im.size, (8, 6, 4)), vig)
    im = im.resize((W, H), Image.LANCZOS).convert("RGBA")
    im.putalpha(255)
    return im


# culture (the name list of a country in world.py) -> portrait style of its generic leaders
CULTURE_STYLE = {"celtic": "celtic", "greek": "greek", "iapygian": "latin", "iberian": "iberian",
                 "scythian": "scythian", "italic": "latin", "northern": "northern", "libyan": "libyan",
                 "germanic": "northern", "etruscan": "etruscan", "thracian": "thracian", "arabian": "arabian",
                 "punic": "punic", "nilotic": "kushite", "caucasian": "caucasian", "anatolian": "anatolian",
                 "latin": "latin", "island": "nuragic", "none": "greek", "persian": "persian"}
GENERIC_MALE, GENERIC_FEMALE = 4, 0  # the base game lists only men for random leaders, too


def seed_of(text):
    return int(hashlib.md5(text.encode()).hexdigest()[:8], 16)


def main():
    out = MOD / "gfx" / "leaders" / "ante"
    (out / "generic").mkdir(parents=True, exist_ok=True)
    named = []
    for tag, key, name, trait, female, attested, desc in LEADERS:
        im = portrait(LEADER_STYLE.get(f"{tag}_{key}", TAG_STYLE[tag]), female, seed_of(f"{tag}_{key}"))
        im.save(out / f"{tag}_{key}.dds")
        named.append(im)
    # generic portraits: a few per people, for every leader and general the game makes up itself
    styles = sorted(set(CULTURE_STYLE.values()))
    sprites, generic = ["# Generated by tools/portraits.py", "spriteTypes = {"], {}
    sheet_g = []
    for st in styles:
        generic[st] = {"male": [], "female": []}
        for sex, n in (("male", GENERIC_MALE), ("female", GENERIC_FEMALE)):
            for i in range(1, n + 1):
                fname = f"{st}_{sex}_{i}"
                im = portrait(st, sex == "female", seed_of("generic_" + fname))
                im.save(out / "generic" / f"{fname}.dds")
                sheet_g.append(im)
                gfx = f"GFX_ante_portrait_{fname}"
                generic[st][sex].append(gfx)
                sprites += ["\tspriteType = {", f'\t\tname = "{gfx}"',
                            f'\t\ttexturefile = "gfx/leaders/ante/generic/{fname}.dds"', "\t}"]
    sprites.append("}")
    (MOD / "interface").mkdir(exist_ok=True)
    (MOD / "interface" / "ante_portraits.gfx").write_text("\n".join(sprites) + "\n", encoding="utf-8")
    # portraits/00_portraits.txt replaces the base game's (modern faces): every country gets its people's set
    import world
    C = world.countries()

    def block(st, indent):
        p = "\t" * indent
        m = " ".join(f'"{g}"' for g in generic[st]["male"])
        pol = "".join(f"{p}\t\t{ide} = {{ male = {{ {m} }} }}\n"
                      for ide in ("democratic", "fascism", "communism", "neutrality"))
        return (f"{p}army = {{ male = {{ {m} }} }}\n"
                f"{p}navy = {{ male = {{ {m} }} }}\n"
                f"{p}political = {{\n{pol}{p}}}\n")

    txt = ["# Generated by tools/portraits.py - generic ancient portraits (our own procedural art, CC0).",
           "# These are GENERIC faces of each people, used for every leader and general without a portrait of his own.",
           "default = {", '\tmale = { "GFX_portrait_unknown" }', '\tfemale = { "GFX_portrait_unknown_female" }', "}", ""]
    for cont, st in (("europe", "celtic"), ("north_america", "northern"), ("south_america", "iberian"),
                     ("australia", "greek"), ("africa", "libyan"), ("asia", "scythian"), ("middle_east", "persian")):
        txt += ["continent = {", f"\tname = {cont}", block(st, 1) + "}", ""]
    for tag, c in sorted(C.items()):
        txt += [f"{tag} = {{", block(CULTURE_STYLE.get(c["names"], "greek"), 1) + "}", ""]
    (MOD / "portraits").mkdir(exist_ok=True)
    (MOD / "portraits" / "00_portraits.txt").write_text("\n".join(txt), encoding="utf-8")
    if "--preview" in sys.argv:
        ims = named + sheet_g
        cols = 10
        sheet = Image.new("RGB", (W * cols, H * ((len(ims) + cols - 1) // cols)), (0, 0, 0))
        for i, im in enumerate(ims):
            sheet.paste(im.convert("RGB"), ((i % cols) * W, (i // cols) * H))
        sheet.save(sys.argv[sys.argv.index("--preview") + 1], quality=85)
    print(f"written: {len(LEADERS)} named portraits, {len(sheet_g)} generic portraits for {len(styles)} peoples, "
          f"portrait lists for {len(C)} countries")


if __name__ == "__main__":
    main()
