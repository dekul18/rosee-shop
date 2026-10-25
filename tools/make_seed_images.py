"""Generates the illustrated sample product images in store/seed_images/. Run: python tools/make_seed_images.py"""
import math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

W, H, S = 800, 1000, 2
OUT = Path(__file__).resolve().parent.parent / "store" / "seed_images"
RG = (196, 139, 123)  # rose gold


def hx(h):
    h = h.lstrip('#')
    if len(h) == 3: h = ''.join(ch * 2 for ch in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def sh(c, f): return tuple(max(0, min(255, int(v * f))) for v in c)
def sc(pts): return [(x * S, y * S) for x, y in pts]


def background(b1, b2):
    img = Image.new("RGB", (W * S, H * S)); d = ImageDraw.Draw(img)
    for y in range(H * S):
        t = y / (H * S)
        d.line([(0, y), (W * S, y)], fill=tuple(int(b1[i] + (b2[i] - b1[i]) * t) for i in range(3)))
    arch = Image.new("RGBA", img.size, (0, 0, 0, 0)); a = ImageDraw.Draw(arch)
    a.ellipse(sc([(130, 100), (670, 640)]), fill=(255, 255, 255, 90))
    a.rectangle(sc([(130, 370), (670, 930)]), fill=(255, 255, 255, 90))
    img.paste(arch, (0, 0), arch)
    return img


class Pen:
    def __init__(self):
        self.im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); self.d = ImageDraw.Draw(self.im)
    def poly(self, pts, fill): self.d.polygon(sc(pts), fill=fill)
    def ell(self, box, fill, outline=None, w=0): self.d.ellipse(sc(box), fill=fill, outline=outline, width=w * S)
    def rect(self, box, fill, r=0): self.d.rounded_rectangle(sc(box), radius=r * S, fill=fill)
    def line(self, pts, fill, w=3): self.d.line(sc(pts), fill=fill, width=w * S, joint="curve")
    def hanger(self, y=150):
        self.d.arc(sc([(385, y - 40), (415, y - 10)]), 180, 450, fill=RG, width=5 * S)
        self.line([(400, y - 10), (400, y + 10), (250, y + 90)], RG, 5); self.line([(400, y + 10), (550, y + 90)], RG, 5)


def finish(bg, pen, name, z=1.22):
    # zoom the garment about the frame centre so it fills more of the picture
    big = pen.im.resize((int(W * S * z), int(H * S * z)), Image.LANCZOS)
    layer = Image.new("RGBA", pen.im.size, (0, 0, 0, 0))
    layer.paste(big, (int(400 * S - 400 * S * z), int(540 * S - 540 * S * z)), big)
    pen.im = layer
    shadow = Image.new("RGBA", pen.im.size, (0, 0, 0, 0))
    shadow.putalpha(pen.im.getchannel("A").point(lambda v: int(v * 0.28)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14 * S))
    bg.paste(shadow, (10 * S, 16 * S), shadow); bg.paste(pen.im, (0, 0), pen.im)
    bg.resize((W, H), Image.LANCZOS).save(OUT / name, quality=90)


def folds(p, c, pts_pairs):
    for (a, b) in pts_pairs: p.line([a, b], sh(c, 1.1), 3)
    for (a, b) in pts_pairs: p.line([(a[0] + 9, a[1]), (b[0] + 14, b[1])], sh(c, .88), 3)


def dress_slip(p, c, a):
    p.hanger(); p.line([(345, 235), (352, 310)], sh(c, .85), 8); p.line([(455, 235), (448, 310)], sh(c, .85), 8)
    p.poly([(335, 300), (465, 300), (452, 445), (348, 445)], c)
    p.poly([(348, 445), (452, 445), (575, 870), (225, 870)], c); p.ell([(225, 835), (575, 905)], c)
    p.ell([(365, 290), (435, 345)], (0, 0, 0, 0)); p.rect([(345, 436), (455, 452)], sh(c, .85), 6)
    folds(p, c, [((385, 460), (335, 880)), ((415, 460), (445, 885)), ((440, 460), (520, 870))])


def dress_floral(p, c, a, seed=3):
    rnd = random.Random(seed); p.hanger()
    p.ell([(300, 270), (390, 350)], c); p.ell([(410, 270), (500, 350)], c)
    p.poly([(335, 285), (465, 285), (455, 430), (345, 430)], c)
    p.poly([(345, 430), (455, 430), (560, 800), (240, 800)], c); p.ell([(240, 770), (560, 830)], c)
    p.rect([(342, 420), (458, 446)], sh(c, .8), 8); p.ell([(368, 280), (432, 335)], (0, 0, 0, 0))
    for _ in range(26):
        y = rnd.randint(470, 790); half = 55 + (y - 430) / 370 * 105
        x = 400 + rnd.uniform(-half + 14, half - 14)
        for k in range(5):
            ang = k * 2 * math.pi / 5; p.ell([(x + 9 * math.cos(ang) - 6, y + 9 * math.sin(ang) - 6), (x + 9 * math.cos(ang) + 6, y + 9 * math.sin(ang) + 6)], a)
        p.ell([(x - 4, y - 4), (x + 4, y + 4)], (255, 232, 150))


def dress_puff(p, c, a):
    p.hanger(); p.poly([(335, 300), (465, 300), (455, 450), (345, 450)], c)
    p.ell([(255, 290), (355, 400)], c); p.ell([(445, 290), (545, 400)], c)
    p.ell([(262, 365), (350, 420)], sh(c, .9)); p.ell([(450, 365), (538, 420)], sh(c, .9))
    p.poly([(345, 450), (455, 450), (590, 680), (210, 680)], c)
    for i in range(9): p.ell([(210 + i * 42.5, 650), (252 + i * 42.5, 705)], c)
    p.rect([(330, 300), (470, 316)], (255, 255, 255, 235), 6); p.rect([(342, 440), (458, 458)], sh(c, .8), 6)
    folds(p, c, [((385, 465), (320, 690)), ((415, 465), (480, 690))])


def top_bow(p, c, a):
    p.hanger(); p.poly([(250, 420), (300, 270), (345, 255), (360, 255), (440, 255), (455, 255), (500, 270), (550, 420), (505, 450), (475, 380), (480, 620), (320, 620), (325, 380), (295, 450)], c)
    p.ell([(360, 232), (440, 310)], (0, 0, 0, 0))
    for x in range(335, 476, 14): p.line([(x, 330), (x - 1, 612)], sh(c, .93), 2)
    p.poly([(400, 405), (330, 365), (330, 445)], a); p.poly([(400, 405), (470, 365), (470, 445)], a); p.ell([(384, 388), (416, 422)], sh(a, .85))


def shirt_linen(p, c, a):
    p.hanger(); p.poly([(240, 440), (290, 270), (400, 250), (510, 270), (560, 440), (515, 465), (480, 370), (485, 590), (315, 590), (320, 370), (285, 465)], c)
    p.poly([(400, 250), (345, 262), (385, 330)], (255, 255, 255, 255)); p.poly([(400, 250), (455, 262), (415, 330)], (255, 255, 255, 255))
    p.line([(400, 320), (400, 585)], sh(c, .85), 3)
    for y in (360, 420, 480, 540): p.ell([(394, y), (406, y + 12)], (255, 255, 255, 255))
    for y in range(290, 585, 22): p.line([(322, y), (478, y)], sh(c, .97), 1)


def skirt_pleated(p, c, a):
    p.hanger(); p.rect([(320, 300), (480, 345)], sh(c, .82), 6)
    p.poly([(325, 345), (475, 345), (610, 860), (190, 860)], c)
    for i in range(1, 12):
        t = i / 12; x0, x1 = 325 + 150 * t, 190 + 420 * t
        p.line([(x0, 350), (x1, 860)], sh(c, .9 if i % 2 else 1.1), 5)
    for i in range(13): p.ell([(190 + i * 33, 835), (225 + i * 33, 885)], c)


def skirt_denim(p, c, a):
    p.hanger(); p.rect([(318, 300), (482, 340)], sh(c, .85), 6)
    p.poly([(320, 340), (480, 340), (570, 770), (230, 770)], c)
    for x0, x1 in ((330, 245), (470, 555)): p.line([(x0, 345), (x1, 765)], (240, 225, 190), 2)
    p.line([(236, 750), (564, 750)], (240, 225, 190), 2); p.line([(400, 345), (400, 760)], sh(c, .78), 3)
    p.ell([(388, 312), (412, 336)], RG); p.d.arc(sc([(335, 360), (400, 450)]), 0, 90, fill=(240, 225, 190), width=3 * S)
    p.d.arc(sc([(400, 360), (465, 450)]), 90, 180, fill=(240, 225, 190), width=3 * S)


def hijab(p, c, a):
    skin = (240, 205, 185); p.poly([(300, 400), (500, 400), (640, 890), (160, 890)], c)
    p.ell([(285, 190), (515, 520)], c); p.ell([(335, 285), (465, 440)], skin)
    p.d.arc(sc([(335, 285), (465, 440)]), 190, 350, fill=sh(c, .88), width=6 * S)
    p.ell([(392, 440), (408, 456)], RG)
    folds(p, c, [((350, 470), (250, 880)), ((400, 480), (400, 890)), ((450, 470), (560, 880))])
    p.d.arc(sc([(300, 780), (500, 900)]), 0, 180, fill=sh(c, 1.12), width=4 * S)


def pearls(p, c, a):
    for gx, gy in ((250, 270), (550, 270), (250, 600), (550, 600)):
        p.rect([(gx - 120, gy - 22), (gx + 120, gy + 22)], RG, 20); p.rect([(gx - 120, gy - 14), (gx + 120, gy + 4)], (225, 175, 160), 14)
        for i in range(-3, 4):
            x = gx + i * 30; p.ell([(x - 14, gy - 14), (x + 14, gy + 14)], (252, 247, 240)); p.ell([(x - 8, gy - 9), (x - 2, gy - 3)], (255, 255, 255))


def scrunchies(p, c, a):
    for (cx, cy, col) in ((400, 300, c), (290, 560, a), (510, 600, sh(c, .88))):
        r = 130
        for ring in range(26):
            ang = ring * 2 * math.pi / 26; x, y = cx + r * math.cos(ang) * 1.0, cy + r * 0.78 * math.sin(ang)
            p.ell([(x - 46, y - 46), (x + 46, y + 46)], sh(col, 1.0 + 0.1 * math.sin(ang * 3)))
        p.ell([(cx - 62, cy - 48), (cx + 62, cy + 48)], (0, 0, 0, 0))
        p.d.ellipse(sc([(cx - 62, cy - 48), (cx + 62, cy + 48)]), fill=(0, 0, 0, 0))


# slug, drawer, (main, alt-flower/accent, bg1, bg2), second look (main, accent, bg1, bg2)
JOBS = {
    "satin-slip-dress": (dress_slip, ("#f4a6c0", "#fff", "#ffe6ee", "#f6d3ee"), ("#c9b6fb", "#fff", "#eee6ff", "#fbe4f1")),
    "floral-midi-dress": (dress_floral, ("#cbb8f8", "#f48fb1", "#f1eaff", "#ffe6ee"), ("#f9c6d3", "#9a7fe0", "#fff1e6", "#fbe4f1")),
    "puff-sleeve-mini-dress": (dress_puff, ("#ef7fa6", "#fff", "#ffe6ee", "#fff1e0"), ("#fff4e6", "#fff", "#f1eaff", "#ffe6ee")),
    "ribbed-bow-top": (top_bow, ("#fff4ea", "#f4a6c0", "#f1eaff", "#ffe6ee"), ("#f4a6c0", "#fff4ea", "#fff1e6", "#f1eaff")),
    "linen-cropped-shirt": (shirt_linen, ("#e6dcf8", "#fff", "#fff6ea", "#f1eaff"), ("#f6e4d2", "#fff", "#ffe6ee", "#fff6ea")),
    "pleated-tulle-skirt": (skirt_pleated, ("#f9b7cc", "#fff", "#f1eaff", "#ffe6ee"), ("#d4c2fa", "#fff", "#ffe6ee", "#f1eaff")),
    "denim-a-line-skirt": (skirt_denim, ("#8fb0d9", "#fff", "#ffe6ee", "#fff6ea"), ("#b9cfea", "#fff", "#f1eaff", "#ffe6ee")),
    "chiffon-hijab": (hijab, ("#e8a9b5", "#fff", "#fff1e6", "#ffe6ee"), ("#cbb8f8", "#fff", "#ffe6ee", "#f1eaff")),
    "pearl-hair-clip-set": (pearls, ("#fff", "#fff", "#ffe6ee", "#f1eaff"), ("#fff", "#fff", "#f1eaff", "#fff6ea")),
    "satin-scrunchie-trio": (scrunchies, ("#f4a6c0", "#c9b6fb", "#fff1e6", "#ffe6ee"), ("#f9d7a8", "#a8e0d0", "#f1eaff", "#ffe6ee")),
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, (fn, a, b) in JOBS.items():
        for i, (main, acc, b1, b2) in enumerate((a, b), 1):
            pen = Pen(); fn(pen, hx(main), hx(acc)); finish(background(hx(b1), hx(b2)), pen, f"{slug}-{i}.jpg")
    print("images:", len(list(OUT.glob("*.jpg"))))
