"""Write map/terrain/colormap_rgb_cityemissivemask_a.dds - the colour of the land on the map.

usage: python tools/colormap.py             paint it from terrain.bmp + heightmap.bmp (no game needed)
       python tools/colormap.py --vanilla   crop and zoom the game's own colormap (needs the game)

RGB of this texture tints the terrain (and everything drawn over it, country colours included);
the alpha channel is the mask of the city lights. The first generator resized the vanilla file as
one RGBA image. An RGBA resize premultiplies by alpha, and alpha is 0 almost everywhere (no city
lights), so the colours came out black: a black and white map on which no country had a colour.
Colour and alpha must be resized separately.
"""
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
MOD = TOOLS.parent
MAP = MOD / "map"
OUT = MAP / "terrain" / "colormap_rgb_cityemissivemask_a.dds"

# terrain.bmp palette index -> land colour. The index meanings were read off the map itself
# (which province terrain each index mostly lies on); the colours are muted, natural tones.
TERRAIN_RGB = {
    0: (104, 114, 70),    # plains
    1: (60, 82, 50),      # forest
    2: (112, 108, 76),    # hills
    3: (178, 158, 112),   # desert
    4: (68, 88, 56),      # forest (darker, northern)
    5: (122, 124, 74),    # farmland
    6: (150, 126, 92),    # dry hills
    7: (198, 178, 130),   # sand desert
    8: (142, 124, 98),    # desert mountain
    9: (76, 92, 68),      # marsh
    10: (134, 122, 100),  # dry mountain
    11: (120, 116, 104),  # mountain
    12: (150, 142, 96),   # steppe / dry plains
    13: (118, 114, 98),   # urban
    15: (40, 58, 72),     # water (only shows through at the shore)
    16: (182, 184, 188),  # snowy mountain
    17: (96, 106, 68),    # wooded hills
    19: (226, 229, 233),  # glacier
    20: (146, 144, 138),  # high mountain
    22: (56, 84, 46),     # jungle
    31: (172, 152, 122),  # barren
}
DEFAULT_RGB = (110, 110, 84)
GREEN = (0, 1, 2, 4, 5, 9, 17)             # types that dry out towards the south


def bmp8(path):
    raw = path.read_bytes()
    off = struct.unpack("<I", raw[10:14])[0]
    w, h = struct.unpack("<ii", raw[18:26])
    stride = (w + 3) & ~3
    return np.frombuffer(raw, np.uint8, count=stride * h, offset=off).reshape(h, stride)[::-1, :w]


def city_mask(size):
    """the alpha channel of the existing file (the resize never damaged it); none -> no city lights"""
    if OUT.exists():
        try:
            a = Image.open(OUT).convert("RGBA").getchannel("A")
            if a.size == size:
                return a
        except Exception as exc:  # unreadable file: start again without lights
            print("WARN: could not read the existing colormap:", exc)
    return Image.new("L", size, 0)


def painted():
    terrain = bmp8(MAP / "terrain.bmp")
    height = bmp8(MAP / "heightmap.bmp").astype(np.float32)
    h, w = terrain.shape
    lut = np.tile(np.array(DEFAULT_RGB, np.float32), (256, 1))
    for i, c in TERRAIN_RGB.items():
        lut[i] = c
    rgb = lut[terrain]                                              # (h, w, 3)
    # climate: green land turns yellower towards the south, greyer in the far north
    lat = (np.arange(h, dtype=np.float32) / h)[:, None]
    green = np.isin(terrain, GREEN)
    dry = np.clip((lat - 0.50) / 0.30, 0, 1) * 0.55
    cold = np.clip((0.16 - lat) / 0.16, 0, 1) * 0.45
    for k, (d, c) in enumerate(zip((158, 146, 98), (128, 130, 118))):
        ch = rgb[..., k]
        ch[:] = np.where(green, ch * (1 - dry) + d * dry, ch)
        ch[:] = np.where(green, ch * (1 - cold) + c * cold, ch)
    # relief: light from the north-west, and high ground a little paler
    gy, gx = np.gradient(height)
    shade = np.clip(1.0 - 0.03 * (gx + gy), 0.76, 1.16)
    pale = np.clip((height - 120) / 110, 0, 1)[..., None] * 0.16
    rgb = rgb * (1 - pale) + 200 * pale
    rgb *= shade[..., None]
    # broad, gentle variation so that large plains are not one flat colour
    rng = np.random.default_rng(245)
    noise = Image.fromarray((rng.random((h // 32 + 2, w // 32 + 2)) * 255).astype(np.uint8))
    noise = np.asarray(noise.resize((w, h), Image.BICUBIC), np.float32) / 255.0
    rgb *= (0.93 + 0.14 * noise)[..., None]
    land = terrain != 15
    rgb[~land] = TERRAIN_RGB[15]
    img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB")
    img = img.resize((w // 2, h // 2), Image.BOX).filter(ImageFilter.GaussianBlur(1.2))
    return img


def from_vanilla():
    import newmap as N
    src = Image.open(N.VMAP / "terrain" / "colormap_rgb_cityemissivemask_a.dds").convert("RGBA")
    args = (N.X0 / 2, N.Y0 / 2, N.SCALE, N.W // 2, N.H // 2, Image.BICUBIC)
    # colour and alpha separately: resizing RGBA as one image blackens the colour where alpha is 0
    return N.resample(src.convert("RGB"), *args), N.resample(src.getchannel("A"), *args)


def main():
    if "--vanilla" in sys.argv:
        rgb, alpha = from_vanilla()
    else:
        rgb = painted()
        alpha = city_mask(rgb.size)
    Image.merge("RGBA", (*rgb.split(), alpha)).save(OUT)
    a = np.asarray(rgb, np.float32)
    print(f"{OUT.name}: {rgb.size[0]}x{rgb.size[1]}, mean colour {[round(float(v)) for v in a.reshape(-1, 3).mean(0)]}")


if __name__ == "__main__":
    main()
