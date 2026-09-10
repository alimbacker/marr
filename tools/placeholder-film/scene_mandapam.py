"""Scene D — the wedding hall's entrance dressed for the morning: a pandal of
coconut fronds, marigold strands, a mango-leaf thoranam over a teak door,
banana plants and brass kuthuvilakku lamps. The camera drifts through the
hanging strands toward the doorway, which glows with the hall inside."""
import math
import numpy as np
from kit import *

WALL = hexc("#ecd9b6")
KAAVI = hexc("#983824")
WOOD = hexc("#4a2a18")
WOOD_HI = hexc("#8a5a34")
BRASS = hexc("#b8862e")
BRASS_HI = hexc("#f3d07a")
BRASS_LO = hexc("#6e4a1a")
LEAVES = [hexc("#4c7a2c"), hexc("#6d9a3a"), hexc("#3f6a26"), hexc("#83ab46")]
MANGO = [hexc("#2f5a22"), hexc("#46762c"), hexc("#5d8a34")]
STEM = hexc("#b4bd78")
FLOOR = hexc("#c4a07a")
PANDAL = hexc("#3a2719")
MARI = [(hexc("#e2700e"), hexc("#f8a03a")), (hexc("#eea012"), hexc("#fdd35a")),
        (hexc("#d45c0b"), hexc("#f3862a"))]
JAS = (hexc("#e3dccb"), hexc("#fffaf0"))
WALL_Z = 30.0
_tex = value_noise(512, 512, 91, scale=40.0)


class Cam:
    def __init__(self, W, H, cz, eye, cx, hz):
        self.W, self.H, self.cz, self.eye, self.cx = W, H, cz, eye, cx
        self.f = 0.72 * W if W >= H else 1.25 * W
        self.hz = hz * H

    def d(self, z):
        return max(0.05, z - self.cz)

    def s(self, z):
        return self.f / self.d(z)

    def pt(self, x, y, z):
        d = self.d(z)
        return self.W / 2 + self.f * (x - self.cx) / d, self.hz + self.f * (y + self.eye) / d

    def poly(self, pts, z):
        return [self.pt(x, y, z) for x, y in pts]


def camera_path(u, W, H):
    wide = W >= H
    e = ease_io(u)
    return Cam(W, H, mix(0.0, 10.0 if wide else 6.0, e), mix(4.3, 4.6, e),
               0.3 * math.sin(u * 2.2), 0.70 if wide else 0.56)


def flower(L, sx, sy, r, pal):
    L.ellipse(sx, sy, r, r, pal[0])
    L.ellipse(sx - 0.2 * r, sy - 0.22 * r, r * 0.62, r * 0.58, pal[1])


def chain(L, cam, path, r, seed, jas=0, clip=0.5):
    rng = np.random.default_rng(seed)
    for i, (x, y, z) in enumerate(path):
        pal = JAS if (jas and i % jas == jas - 1) else MARI[int(rng.integers(3))]
        if z < cam.cz + clip:
            continue
        sx, sy = cam.pt(x, y, z)
        rr = r * cam.s(z) * (0.72 if pal is JAS else 1.0)
        if rr < 0.35 or sx < -3 * rr or sx > cam.W + 3 * rr or sy < -3 * rr or sy > cam.H + 3 * rr:
            continue
        flower(L, sx, sy, rr, pal)


def swag(x0, x1, y0, sag, z, sp):
    n = max(3, int(abs(x1 - x0) * (1 + 0.25 * sag) / sp))
    return [(mix(x0, x1, t), y0 + sag * 4 * t * (1 - t), z) for t in np.linspace(0, 1, n)]


def strand(x, y0, y1, z, sp, wob=0.0, ph=0.0):
    n = max(3, int(abs(y1 - y0) / sp))
    return [(x + wob * math.sin(ph + k * 0.45), mix(y0, y1, k / (n - 1)), z) for k in range(n)]


def leaf(base, ang, Ln, wmax, droop, rng, n=28, cuts=0.2):
    Lp, Rp, mid = [], [], []
    c1 = rng.random(n + 1) < cuts
    c2 = rng.random(n + 1) < cuts * 0.6
    for i in range(n + 1):
        t = i / n
        cx = base[0] + math.cos(ang) * Ln * t
        cy = base[1] + math.sin(ang) * Ln * t + droop * t * t
        tx, ty = math.cos(ang) * Ln, math.sin(ang) * Ln + 2 * droop * t
        nl = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / nl, tx / nl
        w = wmax * math.sin(math.pi * t) ** 0.7 if 0 < t < 1 else 0.0
        wl = w * (0.3 if c1[i] else 1.0)
        wr = w * (0.3 if c2[i] else 1.0)
        Lp.append((cx + nx * wl, cy + ny * wl))
        Rp.append((cx - nx * wr, cy - ny * wr))
        mid.append((cx, cy))
    return Lp + Rp[::-1], mid


def banana(L, cam, x, z, side, u, seed):
    rng = np.random.default_rng(seed)
    s = cam.s(z)
    w = max(1.0, 0.05 * s)
    dry, _ = leaf((x + side * 0.25, -8.4), math.pi / 2 - side * 0.12, 6.0, 0.55, 0.0, rng, cuts=0.35)
    L.poly(cam.poly(dry, z + 0.3), hexc("#8c6b3c"))
    L.poly(cam.poly([(x - 0.52, 0), (x + 0.52, 0), (x + 0.38, -9.3), (x - 0.38, -9.3)], z), STEM)
    for k in range(6):
        f = (k + 0.5) / 6 - 0.5
        L.line(cam.poly([(x + f * 0.95, -0.1), (x + f * 0.7, -9.2)], z), hexc("#93a05c"), w)
    for j, a in enumerate([-2.4, -2.0, -1.62, -1.2, -0.7]):
        ang = a if side > 0 else math.pi - a
        sway = 0.035 * math.sin(u * 3.0 + j * 1.3)
        poly, mid = leaf((x, -9.0 - 0.18 * j), ang + sway, rng.uniform(6.2, 8.0),
                         rng.uniform(1.0, 1.3), rng.uniform(1.6, 3.4), rng)
        L.poly(cam.poly(poly, z), LEAVES[j % 4])
        L.line(cam.poly(mid, z), hexc("#cdd88f"), w * 1.2)
    bx = x - side * 0.62
    L.line(cam.poly([(x - side * 0.15, -8.9), (bx, -8.4), (bx, -5.4)], z), hexc("#7d8a3c"), w * 2)
    for h in range(4):
        yh = -8.0 + h * 0.6
        for k in range(6):
            fx = bx + (k - 2.5) * (0.2 - 0.02 * h)
            ex, ey = cam.pt(fx, yh, z)
            L.ellipse(ex, ey, 0.085 * s, 0.26 * s, hexc("#9fb24a") if k % 2 else hexc("#8ea23f"))
    hx, hy = bx, -5.5
    heart = [(hx + 0.46 * math.sin(math.pi * t ** 0.7), hy + 1.6 * t) for t in np.linspace(0, 1, 16)]
    heart += [(hx - 0.46 * math.sin(math.pi * t ** 0.7), hy + 1.6 * t) for t in np.linspace(1, 0, 16)]
    L.poly(cam.poly(heart, z), hexc("#6b2334"))
    ex, ey = cam.pt(hx - 0.12, hy + 0.6, z)
    L.ellipse(ex, ey, 0.1 * s, 0.35 * s, hexc("#9a4052"))


def lamp(L, cam, x, z, u, k, flames):
    s = cam.s(z)

    def P(pts):
        return cam.poly(pts, z)
    L.poly(P([(x - 1.0, 0), (x + 1.0, 0), (x + 0.85, -0.32), (x - 0.85, -0.32)]), BRASS_LO)
    L.poly(P([(x - 0.8, -0.32), (x + 0.8, -0.32), (x + 0.42, -0.78), (x - 0.42, -0.78)]), BRASS)
    L.poly(P([(x - 0.62, -0.34), (x - 0.48, -0.34), (x - 0.3, -0.74), (x - 0.38, -0.74)]), BRASS_HI)
    L.poly(P([(x - 0.12, -0.78), (x + 0.12, -0.78), (x + 0.08, -3.3), (x - 0.08, -3.3)]), BRASS)
    for yn in (-1.3, -2.05, -2.75):
        ex, ey = cam.pt(x, yn, z)
        L.ellipse(ex, ey, 0.25 * s, 0.12 * s, BRASS)
        ex, ey = cam.pt(x - 0.08, yn - 0.03, z)
        L.ellipse(ex, ey, 0.09 * s, 0.045 * s, BRASS_HI)
    L.poly(P([(x - 0.95, -3.34), (x + 0.95, -3.34), (x + 0.55, -3.02), (x - 0.55, -3.02)]), BRASS)
    L.poly(P([(x - 0.97, -3.44), (x + 0.97, -3.44), (x + 0.95, -3.34), (x - 0.95, -3.34)]), BRASS_HI)
    L.poly(P([(x - 0.05, -3.44), (x + 0.05, -3.44), (x + 0.04, -4.35), (x - 0.04, -4.35)]), BRASS)
    L.poly(P([(x - 0.24, -4.3), (x + 0.24, -4.3), (x, -5.0)]), BRASS)
    for i in range(5):
        fx = x + (i - 2) * 0.42
        fl = 1 + 0.16 * math.sin(u * 55 + i * 1.7 + k * 3.1) + 0.07 * math.sin(u * 131 + i * 2.3)
        ex, ey = cam.pt(fx, -3.66, z)
        L.ellipse(ex, ey - 0.08 * s * fl, 0.065 * s, 0.17 * s * fl, hexc("#fff2c8"))
        flames.append((ex, ey - 0.1 * s, s, fl))


def rangoli(L, cam, zc, R):
    """A flower kolam on the floor: leaf, marigold, jasmine, rose and marigold rings."""
    rings = [(1.0, hexc("#3f6a26")), (0.86, hexc("#e2700e")), (0.72, hexc("#fbf6ea")), (0.58, hexc("#b3222e")),
             (0.44, hexc("#f2ad17")), (0.3, hexc("#e2700e")), (0.16, hexc("#fff0c4"))]
    for k, (f, col) in enumerate(rings):
        pts = []
        for i in range(120):
            a = i * 2 * math.pi / 120
            rr = R * f * (1 + (0.07 if k % 2 == 0 else 0.035) * math.cos(a * (16 if k < 3 else 8)))
            pts.append(cam.pt(rr * math.cos(a), 0.0, zc + rr * math.sin(a)))
        L.poly(pts, col)


def render(u, W, H, seed=0):
    cam = camera_path(u, W, H)
    wide = W >= H
    big = max(W, H) / 1280
    xx, yy = grid(W, H)
    # inside the hall: warm light and lamp bokeh
    px = vgrad(W, H, [(0.0, hexc("#ffe7c2")), (0.6, hexc("#f6c98a")), (1.0, hexc("#e9a864"))])
    cx_, cy_ = cam.pt(0, -5.5, 62)
    spot(px, cx_, cy_, 7 * cam.s(62), 5 * cam.s(62), hexc("#fff4dc"), 0.8)
    rng = np.random.default_rng(5)
    for i in range(26):
        bx, by, bz = rng.uniform(-5, 5), rng.uniform(-11, -2), rng.uniform(45, 70)
        ex, ey = cam.pt(bx, by, bz)
        r = cam.s(bz) * rng.uniform(0.25, 0.5)
        spot(px, ex, ey, r, r, hexc("#ffd27a") if i % 3 else hexc("#fff0c8"), 0.5)
    L = Layer(W, H)  # the doors, swung open inside
    for sd in (-1, 1):
        L.poly([cam.pt(3.5 * sd, 0, 30.2), cam.pt(3.5 * sd, -10, 30.2), cam.pt(3.4 * sd, -10, 33.6),
                cam.pt(3.4 * sd, 0, 33.6)], WOOD)
    rgb, a = L.arrays()
    px = comp(px, rgb, a)

    # lime-plastered wall with the doorway cut out
    L = Layer(W, H)
    z = WALL_Z
    for poly in ([(-60, 0), (-3.5, 0), (-3.5, -16), (-60, -16)], [(3.5, 0), (60, 0), (60, -16), (3.5, -16)],
                 [(-3.5, -10), (3.5, -10), (3.5, -16), (-3.5, -16)]):
        L.poly(cam.poly(poly, z), WALL)
    for sd in (-1, 1):
        L.poly(cam.poly([(3.5 * sd, 0), (60 * sd, 0), (60 * sd, -1.3), (3.5 * sd, -1.3)], z), KAAVI)
    L.poly(cam.poly([(-60, -14.6), (60, -14.6), (60, -15.2), (-60, -15.2)], z), KAAVI)
    rgb, a = L.arrays()
    light = (0.84 + 0.2 * (1 - xx / W) + 0.06 * (yy / H))[..., None]
    tex = (0.9 + 0.16 * sample_tex(_tex, xx * 0.7, yy * 0.7))[..., None]
    px = comp(px, rgb * light * tex, a)

    # carved teak door frame with brass studs
    L = Layer(W, H)
    fz = WALL_Z - 0.15
    for sd in (-1, 1):
        L.poly(cam.poly([(3.5 * sd, 0), (4.7 * sd, 0), (4.7 * sd, -11.4), (3.5 * sd, -11.4)], fz), WOOD)
        L.poly(cam.poly([(3.5 * sd, 0), (3.72 * sd, 0), (3.72 * sd, -10), (3.5 * sd, -10)], fz), WOOD_HI)
        for j in range(8):
            ex, ey = cam.pt(4.1 * sd, -0.7 - j * 1.3, fz)
            r = 0.1 * cam.s(fz)
            L.ellipse(ex, ey, r, r, BRASS_HI)
    L.poly(cam.poly([(-4.7, -10), (4.7, -10), (4.7, -11.4), (-4.7, -11.4)], fz), WOOD)
    L.poly(cam.poly([(-5.2, -11.4), (5.2, -11.4), (5.2, -11.8), (-5.2, -11.8)], fz), WOOD_HI)
    for j in range(11):
        ex, ey = cam.pt(-3.9 + j * 0.78, -10.7, fz)
        r = 0.2 * cam.s(fz)
        L.ellipse(ex, ey, r, r, WOOD_HI)
        L.ellipse(ex, ey, r * 0.45, r * 0.45, BRASS)
    L.poly(cam.poly([(-5.0, 0.0), (5.0, 0.0), (5.0, -0.45), (-5.0, -0.45)], fz - 0.6), hexc("#8e6a48"))
    rgb, a = L.arrays()
    px = comp(px, rgb, a)

    # mango-leaf thoranam
    L = Layer(W, H)
    rng = np.random.default_rng(3)
    tz = WALL_Z - 0.3
    for j in range(27):
        poly, _ = leaf((-5.3 + j * 0.41, -11.75), math.pi / 2 + rng.uniform(-0.12, 0.12), 1.55, 0.2, 0.0,
                       rng, n=10, cuts=0.0)
        L.poly(cam.poly(poly, tz), MANGO[j % 3])
    L.line(cam.poly([(-5.4, -11.75), (5.4, -11.75)], tz), hexc("#c9a060"), max(1, 0.05 * cam.s(tz)))
    rgb, a = L.arrays()
    px = comp(px, rgb, a)

    # garlands: over the door, down its sides, and swagged along the wall
    L = Layer(W, H)
    chain(L, cam, swag(-4.9, 4.9, -11.7, 1.8, tz - 0.2, 0.3), 0.19, 11, jas=5)
    for sd in (-1, 1):
        chain(L, cam, strand(4.95 * sd, -11.7, -2.6, tz - 0.25, 0.32), 0.18, 12 + sd, jas=6)
    for k in range(-5, 5):
        x0 = k * 6.0 + 3.0
        chain(L, cam, swag(x0 - 3.0, x0 + 3.0, -15.3, 1.1, WALL_Z - 0.2, 0.3), 0.16, 20 + k, jas=4)
        chain(L, cam, strand(x0 - 3.0, -15.3, -13.7, WALL_Z - 0.2, 0.3), 0.14, 40 + k)
    rgb, a = L.arrays()
    px = comp(px, rgb, a)

    # eave with a festoon, the pandal of fronds, the floor
    L = Layer(W, H)
    L.poly(cam.poly([(-60, -16), (60, -16), (60, -19), (-60, -19)], WALL_Z), hexc("#5a3a24"))
    for j in range(-45, 45):
        x0 = j * 0.9
        L.poly(cam.poly([(x0, -16), (x0 + 0.9, -16), (x0 + 0.45, -15.35)], WALL_Z - 0.05),
               KAAVI if j % 2 else hexc("#d6a03a"))
    zn = cam.cz + 0.8
    L.poly([cam.pt(-60, -19, zn), cam.pt(60, -19, zn), cam.pt(60, -19, WALL_Z), cam.pt(-60, -19, WALL_Z)], PANDAL)
    for xk in np.arange(-40, 40, 0.9):
        L.line([cam.pt(xk, -19, zn), cam.pt(xk * 1.01, -19, WALL_Z)], hexc("#5e4128"), max(1.0, 2.2 * big))
    for zk in (8, 14, 20, 26):
        if zk > zn:
            L.line([cam.pt(-60, -19, zk), cam.pt(60, -19, zk)], hexc("#24170e"), max(1.0, 0.2 * cam.s(zk)))
    L.poly([cam.pt(-60, 0, zn), cam.pt(60, 0, zn), cam.pt(60, 0, WALL_Z), cam.pt(-60, 0, WALL_Z)], FLOOR)
    for zk in np.arange(2, 30, 2.0):
        if zk > zn:
            L.line([cam.pt(-60, 0, zk), cam.pt(60, 0, zk)], hexc("#a88660"), max(1.0, 0.04 * cam.s(zk)))
    for xk in np.arange(-30, 31, 2.0):
        L.line([cam.pt(xk, 0, zn), cam.pt(xk, 0, WALL_Z)], hexc("#a88660"), 1.0)
    if 24.0 - 2.6 > cam.cz + 0.5:
        rangoli(L, cam, 24.0, 2.6)
    rgb, a = L.arrays()
    px = comp(px, rgb, a)

    # banana plants tied either side of the door
    L = Layer(W, H)
    bxp = 7.0 if wide else 6.6
    banana(L, cam, -bxp, WALL_Z - 1.6, -1, u, 7)
    banana(L, cam, bxp, WALL_Z - 1.6, 1, u, 8)
    rgb, a = L.arrays()
    px = comp(px, rgb, a)

    # brass lamps
    L = Layer(W, H)
    flames = []
    lamp(L, cam, -3.6, 22.0, u, 0, flames)
    lamp(L, cam, 3.6, 22.0, u, 1, flames)
    rgb, a = L.arrays()
    px = comp(px, rgb, a)
    for ex, ey, s, fl in flames:
        spot(px, ex, ey, 0.32 * s * fl, 0.42 * s * fl, hexc("#ffc060"), 0.9)
        spot(px, ex, ey, 1.6 * s, 1.5 * s, hexc("#ff9a3a"), 0.12)
    for sd in (-1, 1):
        ex, ey = cam.pt(sd * 3.6, -3.7, 22.0)
        spot(px, ex, ey, 3.5 * cam.s(22), 3.0 * cam.s(22), hexc("#ffb060"), 0.10)

    # marigold strands hanging from the pandal, close to the lens
    rng = np.random.default_rng(21)
    buckets = {0: [], 1: [], 2: []}
    xs = 1.0 if wide else 0.55
    for i in range(14):
        sd = -1 if i % 2 else 1
        x = sd * rng.uniform(1.4, 6.5) * xs
        zz = rng.uniform(3.0, 11.0) if wide else rng.uniform(2.5, 9.0)
        y1 = rng.uniform(-4.8, -2.6)
        d = zz - cam.cz
        if d < 0.6:
            continue
        path = strand(x + 0.05 * math.sin(u * 4 + i), -19.0, y1, zz, 0.42, 0.03, i)
        buckets[0 if d < 3.5 else (1 if d < 7 else 2)].append((path, 300 + i))
    for b, blur in ((2, 1.2), (1, 3.5), (0, 8.0)):
        if not buckets[b]:
            continue
        L = Layer(W, H)
        for path, sd_ in buckets[b]:
            chain(L, cam, path, 0.26, sd_, jas=7, clip=0.6)
        rgb, a = L.arrays(blur * big)
        px = comp(px, rgb * 0.92, a)

    px += glow(W, H, -0.1 * W, -0.15 * H, 1.1 * max(W, H), hexc("#ffdcae"), 0.22, 1.5)
    px = bloom(px, 0.8, 26, 0.45)
    return px
