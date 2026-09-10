"""Scene B — inside the gateway: a long pillared corridor lit by oil lamps, a
painted ceiling, and daylight at the far door with a kolam on the threshold."""
import math
import numpy as np
from kit import *

EYE = 4.4
DOOR_Z = 78.0
PILLAR_X = 6.2
PILLAR_W = 1.5
PILLAR_H = 9.0
CEIL = -10.2
PILLAR_ZS = [6.0 + 6.0 * i for i in range(12)]

FOG_DARK = hexc("#24170e")
FOG_GOLD = hexc("#f0c893")
STONE_FRONT = hexc("#6f5a44")
STONE_SIDE = hexc("#8d7153")
STONE_HI = hexc("#a88a66")
STONE_LO = hexc("#4a3a2b")
WALL = hexc("#3b2c20")
FLOOR_NEAR = hexc("#3a2a1d")
FLOOR_FAR = hexc("#6c5236")
PAINT = [hexc("#7d2d1d"), hexc("#b0802f"), hexc("#2f5953"), hexc("#d6bd8e"), hexc("#8a3a22")]
KOLAM = hexc("#f4ecdc")

_tex = value_noise(512, 512, 33, scale=40.0)


class Cam3:
    def __init__(self, W, H, cz, cx=0.0):
        self.W, self.H, self.cz, self.cx = W, H, cz, cx
        self.f = 0.78 * W if W >= H else 1.18 * W
        self.hz = 0.5 * H

    def d(self, z):
        return max(0.05, z - self.cz)

    def pt(self, x, y, z):
        d = self.d(z)
        return self.W / 2 + self.f * (x - self.cx) / d, self.hz + self.f * (y + EYE) / d

    def poly(self, pts3):
        return [self.pt(*p) for p in pts3]


def fogcol(z):
    t = clamp01((z - 38) / (DOOR_Z - 38)) ** 2.2
    return mixc(FOG_DARK, FOG_GOLD, t)


def fogged(col, z, cam, density=36.0):
    d = cam.d(z)
    k = 1 - math.exp(-d / density)
    return mixc(col, fogcol(z), k)


def kolam_strokes():
    """Lotus kolam in the floor plane, centred at the origin, radius ~2."""
    strokes = []
    # eight petals
    for i in range(8):
        a = i * math.pi / 4
        pts = []
        for j in range(25):
            t = j / 24
            r = 0.55 + 1.35 * math.sin(math.pi * t) ** 0.8
            ang = a + (t - 0.5) * 0.78
            pts.append((r * math.cos(ang) * (1 if j in (0, 24) else 1), r * math.sin(ang)))
        strokes.append(pts)
    # inner ring and outer loops
    strokes.append([(0.52 * math.cos(t * 2 * math.pi / 40), 0.52 * math.sin(t * 2 * math.pi / 40)) for t in range(41)])
    outer = []
    for t in range(161):
        ang = t * 2 * math.pi / 160
        r = 2.05 + 0.16 * math.sin(ang * 16)
        outer.append((r * math.cos(ang), r * math.sin(ang)))
    strokes.append(outer)
    dots = [(0.0, 0.0)]
    for i in range(8):
        a = i * math.pi / 4 + math.pi / 8
        dots.append((1.35 * math.cos(a), 1.35 * math.sin(a)))
        dots.append((2.45 * math.cos(a), 2.45 * math.sin(a)))
    return strokes, dots


KOLAM_STROKES, KOLAM_DOTS = kolam_strokes()
KOLAM_Z = 72.5


def camera_path(u, W, H):
    cz = mix(0.5, 64.0, ease_io(u) * 0.35 + u * 0.65)
    cx = 0.35 * math.sin(u * 2.2)
    return Cam3(W, H, cz, cx)


def render(u, W, H, seed=0):
    cam = camera_path(u, W, H)
    rng = np.random.default_rng(seed + 101)
    flick = lambda i: 0.86 + 0.14 * math.sin(u * 83 + i * 2.3) * math.sin(u * 51 + i * 1.1)

    px = np.zeros((H, W, 3), np.float32) + f3(FOG_DARK)
    L = Layer(W, H)

    # end wall and the bright doorway
    zf = DOOR_Z
    L.poly(cam.poly([(-11, 0, zf), (11, 0, zf), (11, CEIL, zf), (-11, CEIL, zf)]), fogged(WALL, zf, cam, 60))
    rgb, a = L.arrays()
    px = comp(px, rgb, a)
    x0, y0 = cam.pt(-2.6, -7.6, zf)
    x1, y1 = cam.pt(2.6, 0.0, zf)
    xi0, xi1 = int(max(0, x0)), int(min(W, x1))
    yi0, yi1 = int(max(0, y0)), int(min(H, y1))
    if xi1 > xi0 and yi1 > yi0:
        yy, xx = np.mgrid[yi0:yi1, xi0:xi1].astype(np.float32)
        tv = (yy - y0) / max(1, (y1 - y0))
        th = np.abs((xx - (x0 + x1) / 2) / max(1, (x1 - x0) / 2))
        door = np.stack([np.full_like(tv, 1.0), 0.95 - 0.08 * tv, 0.86 - 0.16 * tv], -1)
        door *= (1.0 - 0.10 * th ** 2)[..., None]
        # a flagstaff and a tree beyond, lost in the glare
        stripe = np.exp(-((xx - (x0 + (x1 - x0) * 0.68)) / max(1, (x1 - x0) * 0.012)) ** 2) * (tv < 0.93)
        door *= (1 - 0.18 * stripe)[..., None]
        px[yi0:yi1, xi0:xi1] = door

    L = Layer(W, H)
    for xa, xb in ((-3.4, -2.6), (2.6, 3.4)):
        L.poly(cam.poly([(xa, 0, zf - 0.05), (xb, 0, zf - 0.05), (xb, -8.4, zf - 0.05), (xa, -8.4, zf - 0.05)]),
               fogged(STONE_SIDE, zf, cam, 60))
    L.poly(cam.poly([(-3.4, -7.6, zf - 0.05), (3.4, -7.6, zf - 0.05), (3.4, -8.6, zf - 0.05), (-3.4, -8.6, zf - 0.05)]),
           fogged(STONE_HI, zf, cam, 60))
    for side in (-1, 1):
        nx = 6.4 * side
        L.poly(cam.poly([(nx - 1.0, -2.2, zf - 0.04), (nx + 1.0, -2.2, zf - 0.04), (nx + 1.0, -5.6, zf - 0.04), (nx - 1.0, -5.6, zf - 0.04)]),
               fogged(STONE_LO, zf, cam, 60))
    rgb, a = L.arrays()
    px = comp(px, rgb, a)
    for side in (-1, 1):
        X, Y = cam.pt(6.4 * side, -3.2, zf - 0.1)
        s_ = cam.f / cam.d(zf)
        add_glow_fast(px, X, Y, 1.4 * s_, hexc("#ff9a3c"), 0.35)
        add_glow_fast(px, X, Y, 0.18 * s_, hexc("#fff0c8"), 1.2, sx=0.7, sy=1.3)

    # side walls
    L = Layer(W, H)
    for side in (-1, 1):
        zn = cam.cz + 0.6
        L.poly(cam.poly([(10 * side, 0, zn), (10 * side, 0, zf), (10 * side, CEIL, zf), (10 * side, CEIL, zn)]),
               fogged(WALL, 30, cam, 30))
    # ceiling: aisles and nave, painted panels
    L.poly(cam.poly([(-10, CEIL, cam.cz + 0.6), (10, CEIL, cam.cz + 0.6), (10, CEIL, zf), (-10, CEIL, zf)]),
           fogged(hexc("#2e2118"), 30, cam, 30))
    rgb, a = L.arrays()
    px = comp(px, rgb, a)
    # wall shading gradient (darker near camera) + floor
    L = Layer(W, H)
    zn = cam.cz + 0.6
    L.poly(cam.poly([(-10, 0, zn), (10, 0, zn), (10, 0, zf), (-10, 0, zf)]), FLOOR_NEAR)
    rgb, a = L.arrays()
    xx, yy = grid(W, H)
    # floor: brighter towards the door, reflection streak of the doorway
    _, yfar = cam.pt(0, 0, zf)
    t = np.clip((yy - yfar) / max(1.0, H - yfar), 0, 1)
    floor = f3(FLOOR_FAR) * (1 - t[..., None]) ** 1.5 + f3(FLOOR_NEAR) * (1 - (1 - t[..., None]) ** 1.5)
    dcx, _ = cam.pt(0, 0, zf)
    streak = np.exp(-((xx - dcx) / (W * 0.07 + (yy - yfar).clip(0) * 0.35)) ** 2) * np.exp(-t * 2.2)
    floor = floor + f3(hexc("#f3cf96")) * (streak * 0.55)[..., None]
    ftex = sample_tex(_tex, (xx - W / 2) / np.maximum(yy - cam.hz, 1) * 60 + 2000,
                      cam.f * EYE / np.maximum(yy - cam.hz, 1) * 6 + cam.cz * 6)
    floor = floor * (0.9 + 0.2 * ftex)[..., None]
    px = px * (1 - a) + floor * a

    # painted ceiling panels in the nave
    L = Layer(W, H)
    for i in range(len(PILLAR_ZS) - 1, -1, -1):
        za, zb = PILLAR_ZS[i] + 0.8, PILLAR_ZS[i] + 5.2
        if zb < cam.cz + 0.8:
            continue
        za = max(za, cam.cz + 0.8)
        zc = PILLAR_ZS[i] + 3.0
        base = fogged(hexc("#4a3526"), zc, cam)
        L.poly(cam.poly([(-5.4, CEIL, za), (5.4, CEIL, za), (5.4, CEIL, zb), (-5.4, CEIL, zb)]), base)
        if zc - 2.0 < cam.cz + 0.8:
            continue
        for ring, (r, ci) in enumerate([(2.05, 0), (1.75, 3), (1.45, 2), (1.05, 1), (0.7, 4), (0.35, 3)]):
            pts = [(r * math.cos(k * math.pi / 24), CEIL, zc + r * math.sin(k * math.pi / 24)) for k in range(48)]
            L.poly(cam.poly(pts), fogged(mixc(PAINT[ci], hexc("#4a3526"), 0.25), zc, cam))
            if ring == 1:
                for p in range(12):
                    a0 = p * math.pi / 6
                    petal = [(0, CEIL, zc)]
                    for k in range(7):
                        aa = a0 - 0.2 + 0.4 * k / 6
                        rr = 1.05 + 0.55 * math.sin(math.pi * k / 6)
                        petal.append((rr * math.cos(aa), CEIL, zc + rr * math.sin(aa)))
                    L.poly(cam.poly(petal), fogged(PAINT[2], zc, cam))
    rgb, a = L.arrays()
    px = comp(px, rgb, a)

    # kolam on the threshold
    L = Layer(W, H)
    if KOLAM_Z - 2.6 > cam.cz + 0.5:
        kd = cam.d(KOLAM_Z)
        wline = max(0.8, 0.085 * cam.f / kd)
        for stroke in KOLAM_STROKES:
            L.line(cam.poly([(x, 0, KOLAM_Z + z) for x, z in stroke]), KOLAM, wline)
        for x, z in KOLAM_DOTS:
            X, Y = cam.pt(x, 0, KOLAM_Z + z)
            r = 0.11 * cam.f / cam.d(KOLAM_Z + z)
            L.ellipse(X, Y, r * 1.2, r * 0.6, KOLAM)
        # marigold heads at the centre
        for k in range(9):
            ang = k * 2 * math.pi / 9
            X, Y = cam.pt(0.28 * math.cos(ang), -0.05, KOLAM_Z + 0.28 * math.sin(ang))
            r = 0.2 * cam.f / kd
            L.ellipse(X, Y, r, r * 0.7, hexc("#e8871e") if k % 2 else hexc("#f2b632"))
        rgb, a = L.arrays(blur=0.35)
        fade = 1 - math.exp(-cam.d(KOLAM_Z) / 45)
        px = comp(px, rgb * (1 - fade * 0.4), a)

    # pillars, far to near, with their lamps
    lamps = []
    items = []
    for i, z in enumerate(PILLAR_ZS):
        for side in (-1, 1):
            items.append((z, side, i))
    items.sort(key=lambda it: -it[0])
    L = Layer(W, H)
    for z, side, i in items:
        zfront = z - PILLAR_W / 2
        zback = z + PILLAR_W / 2
        if zfront < cam.cz + 0.35:
            continue
        xin = PILLAR_X * side - side * PILLAR_W / 2
        xout = PILLAR_X * side + side * PILLAR_W / 2
        # inner side face (towards the aisle centre)
        L.poly(cam.poly([(xin, 0, zfront), (xin, 0, zback), (xin, -PILLAR_H, zback), (xin, -PILLAR_H, zfront)]),
               fogged(STONE_SIDE, z, cam))
        # front face
        front = [(xin, 0, zfront), (xout, 0, zfront), (xout, -PILLAR_H, zfront), (xin, -PILLAR_H, zfront)]
        L.poly(cam.poly(front), fogged(STONE_FRONT, z, cam))
        # carved bands and medallions on the front face
        xa, xb = min(xin, xout), max(xin, xout)
        for yb, hb, c in [(-0.2, 0.9, STONE_HI), (-3.1, 0.35, STONE_LO), (-5.9, 0.35, STONE_LO), (-8.1, 0.6, STONE_HI)]:
            L.poly(cam.poly([(xa, yb, zfront), (xb, yb, zfront), (xb, yb - hb, zfront), (xa, yb - hb, zfront)]),
                   fogged(c, z, cam))
        for ym in (-1.9, -4.5, -7.0):
            m = 0.5
            cxm = (xa + xb) / 2
            L.poly(cam.poly([(cxm - m, ym + m, zfront), (cxm + m, ym + m, zfront), (cxm + m, ym - m, zfront), (cxm - m, ym - m, zfront)]),
                   fogged(STONE_HI, z, cam))
            L.poly(cam.poly([(cxm + 0.36 * math.cos(k * math.pi / 8), ym + 0.36 * math.sin(k * math.pi / 8), zfront) for k in range(16)]),
                   fogged(STONE_LO, z, cam))
        # bracket capital
        cap = [(xa - 0.35, -PILLAR_H, zfront - 0.05), (xb + 0.35, -PILLAR_H, zfront - 0.05),
               (xb + 0.35, CEIL, zfront - 0.05), (xa - 0.35, CEIL, zfront - 0.05)]
        L.poly(cam.poly(cap), fogged(STONE_SIDE, z, cam))
        drop = [(xa, -PILLAR_H + 0.05, zfront - 0.06), (xb, -PILLAR_H + 0.05, zfront - 0.06),
                ((xa + xb) / 2, -PILLAR_H + 0.95, zfront - 0.06)]
        L.poly(cam.poly(drop), fogged(STONE_HI, z, cam))
        # beam across the nave above this pillar pair
        if side == 1:
            beam = [(-PILLAR_X, CEIL + 0.9, zfront), (PILLAR_X, CEIL + 0.9, zfront), (PILLAR_X, CEIL, zfront), (-PILLAR_X, CEIL, zfront)]
            L.poly(cam.poly(beam), fogged(STONE_FRONT, z, cam))
        lamps.append((xin - side * 0.25, -4.7, z, i * 2 + (side > 0)))
    rgb, a = L.arrays()
    px = comp(px, rgb * 0.8, a)

    # stone texture over everything solid
    tex = sample_tex(_tex, xx * 0.9 + 100, yy * 0.9)
    px = px * (0.92 + 0.16 * tex)[..., None]

    # lamps: flames, glows, pools on the floor
    for x, y, z, i in lamps:
        d = cam.d(z)
        if d < 0.6:
            continue
        fl = flick(i)
        X, Y = cam.pt(x, y, z)
        s = cam.f / d
        fk = math.exp(-d / 70)
        add_glow_fast(px, X, Y, 2.1 * s, hexc("#ff9a3c"), 0.34 * fl * fk)
        add_glow_fast(px, X, Y - 0.12 * s, 0.55 * s, hexc("#ffcf7a"), 0.7 * fl * fk)
        add_glow_fast(px, X, Y - 0.1 * s, 0.13 * s, hexc("#fff4d6"), 1.4 * fk, sx=0.7, sy=1.3)
        Xf, Yf = cam.pt(x * 0.8, 0, z)
        add_glow_fast(px, Xf, Yf, 1.6 * s, hexc("#c56f2a"), 0.20 * fl * fk, sx=1.6, sy=0.45)

    # daylight through the door: bloom and shafts
    dx, dy = cam.pt(0, -3.8, zf)
    sd = cam.f / cam.d(zf)
    dd = cam.d(zf)
    px += glow(W, H, dx, dy, 3.4 * sd, hexc("#f6c98a"), 0.22 + 0.4 * sstep(40, 8, dd), 1.6)
    ang = (xx - dx) / np.maximum(yy - dy + 3 * sd, 1)
    shafts = np.exp(-((ang * 5.2) % 1.0 - 0.5) ** 2 * 18) * np.clip((yy - dy) / H, 0, 1) * \
        np.exp(-np.abs(xx - dx) / (W * 0.35))
    px += (shafts * 0.10)[..., None] * f3(hexc("#f6d4a0"))

    # motes drifting in the light
    for k in range(40):
        mx = (rng.random() * 2 - 1) * 5
        my = -rng.random() * 8
        mz = cam.cz + 3 + rng.random() * 30
        my += 0.4 * math.sin(u * 7 + k)
        X, Y = cam.pt(mx, my, mz)
        if 0 <= X < W and 0 <= Y < H:
            add_glow_fast(px, X, Y, max(0.8, 0.05 * cam.f / cam.d(mz)), hexc("#ffe2b0"), 0.35 * math.exp(-cam.d(mz) / 20))

    px = bloom(px, 0.78, 22, 0.42)
    # walking into the light
    white = sstep(0.86, 1.0, u) ** 1.4
    px = px * (1 - white * 0.3) + f3(hexc("#fbe9cc")) * white * 0.92
    return px
