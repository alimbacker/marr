"""Scene A — a gopuram at pale dawn. The camera starts on the kalasams, sinks down
the tower and pushes through the gateway into darkness."""
import math
import numpy as np
from kit import *

STONE_L = hexc("#e1d8c9")
STONE_M = hexc("#c9bdab")
STONE_D = hexc("#9c907f")
STONE_DD = hexc("#6f6558")
VOID = hexc("#1b1511")
BRONZE = hexc("#a67f55")
BRONZE_HI = hexc("#d9b98e")
SHADOW_SOFT = (60, 50, 42, 70)  # translucent
WALL_WHITE = hexc("#eee5d6")
WALL_RED = hexc("#a54634")

GOP_Z = 100.0



def rect(x, y_top, w, h):
    return [(x, y_top), (x + w, y_top), (x + w, y_top + h), (x, y_top + h)]


def ellipse_pts(cx, cy, rx, ry, a0=0, a1=2 * math.pi, n=28):
    return [(cx + rx * math.cos(a0 + (a1 - a0) * i / (n - 1)),
             cy + ry * math.sin(a0 + (a1 - a0) * i / (n - 1))) for i in range(n)]


def width_at(y):
    t = (y - (-19.4)) / (-80.0 - (-19.4))
    return 56.0 + (28.0 - 56.0) * t


LIFT = None


def build_gopuram():
    rng = np.random.default_rng(7)
    P = []  # (poly, color)

    # prakaram wall with the red and white temple stripes, both sides
    for side in (-1, 1):
        x0, x1 = 30.5 * side, 420 * side
        lo, hi = min(x0, x1), max(x0, x1)
        P.append((rect(lo, -12.5, hi - lo, 12.5), WALL_WHITE))
        x = 32.0
        while x < 420:
            xs = x * side
            P.append((rect(min(xs, xs + 2.6 * side), -11.0, 2.6, 9.4), WALL_RED))
            x += 5.2
        P.append((rect(lo, -13.6, hi - lo, 1.4), STONE_L))  # coping
        P.append((rect(lo, -12.5, hi - lo, 0.5), STONE_D))
        P.append((rect(lo, -1.5, hi - lo, 1.5), STONE_M))  # plinth
        # a nandi on the coping every so often
        x = 44.0
        while x < 420:
            xs = x * side
            P.append((ellipse_pts(xs, -14.5, 1.3, 0.9), STONE_M))
            P.append((ellipse_pts(xs + 1.0 * side, -15.2, 0.45, 0.5), STONE_M))
            x += 26.0

    P.append(("TOWER", None))
    # plinth
    for y0, h, w, c in [(-1.0, 1.0, 64, STONE_M), (-2.0, 1.0, 63, STONE_L),
                        (-2.6, 0.6, 62.4, STONE_D), (-4.2, 1.6, 63, STONE_L)]:
        P.append((rect(-w / 2, y0, w, h), c))
    # walls
    P.append(([(-30.5, -4.2), (30.5, -4.2), (30, -15.5), (-30, -15.5)], STONE_M))
    # pilasters and niches on the wall
    for x in np.arange(-28.5, 29, 4.1):
        if abs(x) < 9.5:
            continue
        P.append((rect(x - 0.35, -15.3, 0.7, 11.0), STONE_L))
    for x in (-22.3, -18.2, 18.2, 22.3, -26.4, 26.4, -14.1, 14.1):
        P.append((rect(x - 1.25, -12.6, 2.5, 6.6), STONE_D))
        hh = rng.uniform(4.6, 5.4)
        P.append((rect(x - 0.55, -6.3 - hh + 0.3, 1.1, hh - 0.6), STONE_L))
        P.append((ellipse_pts(x, -6.3 - hh - 0.2, 0.5, 0.55), STONE_L))
    # door guardians, big
    for x in (-8.3, 8.3):
        P.append((rect(x - 1.8, -14.2, 3.6, 10.0), STONE_DD))
        P.append((rect(x - 0.9, -12.2, 1.8, 7.8), STONE_L))
        P.append((ellipse_pts(x, -12.9, 0.8, 0.9), STONE_L))
        P.append((rect(x - 1.6, -10.8, 0.5, 3.2), STONE_L))
        P.append((rect(x + 1.1, -10.8, 0.5, 3.2), STONE_L))
    # gate
    P.append((rect(-6.3, -15.4, 12.6, 1.4), STONE_L))  # lintel
    P.append((rect(-6.3, -14.0, 1.5, 14.0), STONE_L))
    P.append((rect(4.8, -14.0, 1.5, 14.0), STONE_L))
    P.append((rect(-5.7, -14.0, 0.35, 14.0), STONE_D))
    P.append((rect(5.35, -14.0, 0.35, 14.0), STONE_D))
    P.append((rect(-4.8, -13.2, 9.6, 13.2), VOID))

    # cornice + hara over the base
    P.append((rect(-30.4, -15.5, 60.8, 0.6), STONE_DD))
    P.append((rect(-31.6, -17.0, 63.2, 1.5), STONE_L))
    hara(P, -19.4, -17.0, 58.0)

    # tiers
    n = 7
    th = (80.0 - 19.4) / n
    for k in range(n):
        yb = -19.4 - k * th
        yt = yb - th
        wb, wt = width_at(yb), width_at(yt)
        wall_top = yt + 2.9
        ww_b, ww_t = wb, width_at(wall_top)
        P.append(([(-ww_b / 2, yb), (ww_b / 2, yb), (ww_t / 2, wall_top), (-ww_t / 2, wall_top)], STONE_M))
        # centre opening and its arch
        P.append((ellipse_pts(0, yb - 5.0, 1.75, 1.6, math.pi, 2 * math.pi), STONE_L))
        P.append((rect(-1.35, yb - 5.0, 2.7, 4.5), VOID))
        # niches with figures
        pitch = 3.25
        m = int((ww_t / 2 - 1.6) // pitch)
        for i in range(1, m + 1):
            for side in (-1, 1):
                x = side * i * pitch
                P.append((rect(x - 1.05, yb - 5.0, 2.1, 4.4), STONE_D))
                h = rng.uniform(2.7, 3.5)
                w = rng.uniform(0.85, 1.2)
                P.append((rect(x - w / 2, yb - 0.6 - h, w, h), STONE_L))
                P.append((ellipse_pts(x, yb - 0.75 - h, 0.42, 0.45), STONE_L))
                if rng.random() < 0.45:
                    P.append((rect(x - w / 2 - 0.35, yb - 0.4 - h * 0.85, 0.28, h * 0.5), STONE_L))
                    P.append((rect(x + w / 2 + 0.07, yb - 0.4 - h * 0.85, 0.28, h * 0.5), STONE_L))
                P.append((rect(x + side * 1.45 - 0.2, yb - 5.4, 0.4, 5.2), STONE_L))
        # cornice
        wc = width_at(wall_top) + 1.8
        P.append((rect(-width_at(wall_top) / 2, wall_top, width_at(wall_top), 1.6), SHADOW_SOFT))
        P.append((rect(-width_at(wall_top) / 2, wall_top, width_at(wall_top), 0.55), STONE_DD))
        P.append((rect(-wc / 2, wall_top - 1.25, wc, 1.25), STONE_L))
        hara(P, yt, wall_top - 1.25, width_at(wall_top) - 0.6)

    # shala (barrel vault)
    P.append((rect(-15.8, -81.3, 31.6, 1.3), STONE_L))
    P.append((rect(-15.0, -87.6, 30.0, 6.3), STONE_M))
    for i in range(-15, 12, 2):
        P.append(([(i - 0.1, -81.3), (i + 0.1, -81.3), (i + 3.1, -87.6), (i + 2.9, -87.6)], STONE_D))
        P.append(([(i - 0.1, -87.6), (i + 0.1, -87.6), (i + 3.1, -81.3), (i + 2.9, -81.3)], STONE_D))
    P.append((ellipse_pts(0, -87.6, 15.0, 3.0, math.pi, 2 * math.pi, 40), STONE_L))
    P.append((rect(-15.0, -87.9, 30.0, 0.4), STONE_D))
    # the great gable arch
    arch = ellipse_pts(0, -84.6, 4.0, 4.2, math.pi * 0.92, math.pi * 2.08, 34)
    P.append((arch + [(4.2, -81.3), (-4.2, -81.3)], STONE_L))
    P.append(([(-0.9, -88.4), (0.9, -88.4), (0, -91.2)], STONE_L))
    inner = ellipse_pts(0, -84.2, 2.5, 2.9, math.pi * 0.95, math.pi * 2.05, 30)
    P.append((inner + [(2.5, -81.3), (-2.5, -81.3)], STONE_D))
    P.append((ellipse_pts(0, -84.2, 1.0, 1.25), STONE_L))
    P.append((rect(-0.55, -83.2, 1.1, 1.9), STONE_L))
    # horns
    for side in (-1, 1):
        pts_o, pts_i = [], []
        for i in range(16):
            t = i / 15
            ang = math.pi * (1.05 - 1.35 * t)
            r = 2.6 - 1.2 * t
            cx, cy = 14.4 * side, -89.2
            x = cx + side * (r * math.cos(ang) + 1.8 * t)
            y = cy - 1.2 * t - r * math.sin(ang) * 0.9
            w = 2.1 * (1 - 0.55 * t)
            pts_o.append((x - side * w * 0.5, y - w * 0.3))
            pts_i.append((x + side * w * 0.5, y + w * 0.3))
        P.append((pts_o + pts_i[::-1], STONE_L))
    # kalasams
    for i in range(-3, 4):
        x = i * 3.9
        yr = -87.6 - 3.0 * math.sqrt(max(0.0, 1 - (x / 15.0) ** 2))
        P.append((rect(x - 0.95, yr - 0.55, 1.9, 0.65), BRONZE))
        P.append((ellipse_pts(x, yr - 1.55, 1.3, 1.1), BRONZE))
        P.append((ellipse_pts(x - 0.45, yr - 1.8, 0.42, 0.5), BRONZE_HI))
        P.append((rect(x - 0.32, yr - 2.75, 0.64, 0.35), BRONZE))
        P.append((ellipse_pts(x, yr - 3.05, 0.72, 0.55), BRONZE))
        P.append(([(x - 0.34, yr - 3.4), (x + 0.34, yr - 3.4), (x, yr - 4.9)], BRONZE))
        P.append((ellipse_pts(x, yr - 4.9, 0.16, 0.16), BRONZE_HI))
    return P


def hara(P, y_top, y_bottom, width):
    """A parapet row of miniature shrines on a cornice."""
    h = y_bottom - y_top
    unit = 3.0
    n = max(3, int(width // unit))
    real = width / n
    for i in range(n):
        x0 = -width / 2 + i * real + 0.35
        w = real - 0.7
        corner = i in (0, n - 1)
        if corner:
            x0 -= 0.25 if i == 0 else -0.25
            w += 0.5
            P.append((rect(x0, y_top - 0.6 + h * 0.45, w, h * 0.55 + 0.6), STONE_M))
            P.append((ellipse_pts(x0 + w / 2, y_top - 0.6 + h * 0.45, w / 2, 1.1, math.pi, 2 * math.pi), STONE_L))
        else:
            P.append((rect(x0, y_top + h * 0.4, w, h * 0.6), STONE_M))
            P.append((ellipse_pts(x0 + w / 2, y_top + h * 0.4, w / 2, h * 0.42, math.pi, 2 * math.pi), STONE_L))


def build_palms():
    rng = np.random.default_rng(11)
    palms = []
    spots = [(-58, 170, 44, 3), (-84, 205, 52, -4), (-120, 240, 47, 5), (-160, 190, 40, -2),
             (-205, 260, 55, 4), (63, 180, 48, -4), (95, 220, 42, 3), (132, 200, 53, -5),
             (178, 250, 46, 2), (230, 230, 50, -3), (-260, 220, 43, 3), (290, 260, 48, 4)]
    for x, z, h, lean in spots:
        polys = []
        tl, tr = [], []
        for i in range(13):
            t = i / 12
            px_ = x + lean * t ** 1.6
            w = mix(1.5, 0.8, t)
            tl.append((px_ - w / 2, -h * t))
            tr.append((px_ + w / 2, -h * t))
        polys.append(tl + tr[::-1])
        tx, ty = x + lean, -h
        for k in range(12):
            ang = -math.pi / 2 + (k / 11 - 0.5) * math.pi * 1.5 + rng.uniform(-0.15, 0.15)
            length = rng.uniform(8.5, 12.5)
            droop = rng.uniform(0.45, 0.85)
            spine = []
            for i in range(10):
                t = i / 9
                spine.append((tx + math.cos(ang) * length * t,
                              ty + math.sin(ang) * length * t + droop * length * t * t))
            left, right = [], []
            for i, (sx, sy) in enumerate(spine):
                t = i / 9
                if i < 9:
                    nx_, ny_ = spine[i + 1][0] - sx, spine[i + 1][1] - sy
                else:
                    nx_, ny_ = sx - spine[i - 1][0], sy - spine[i - 1][1]
                ln = math.hypot(nx_, ny_) or 1
                ox, oy = -ny_ / ln, nx_ / ln
                w = 1.9 * math.sin(math.pi * min(1, t * 1.15)) * (1.25 if i % 2 else 0.8)
                left.append((sx + ox * w, sy + oy * w + 0.5 * w))
                right.append((sx - ox * w, sy - oy * w + 0.5 * w))
            polys.append(left + right[::-1])
        palms.append((z, polys))
    palms.sort(key=lambda p: -p[0])
    return palms


def build_treeline():
    rng = np.random.default_rng(5)
    xs = np.linspace(-900, 900, 260)
    top = -9 - 6 * np.abs(np.sin(xs / 37.0)) - rng.random(len(xs)) * 3.5
    pts = [(-900, 2)] + [(float(x), float(y)) for x, y in zip(xs, top)] + [(900, 2)]
    return pts


_ALL = build_gopuram()
_cut = [i for i, p in enumerate(_ALL) if p[0] == "TOWER"][0]
GOP = _ALL[:_cut] + _ALL[_cut + 1:]
TOWER = _ALL[_cut + 1:]
LIFT = {STONE_L, BRONZE, BRONZE_HI}
PALMS = build_palms()
TREES = build_treeline()
_tex = value_noise(1024, 1024, 21, scale=90.0)


class Cam:
    def __init__(self, W, H, f, cx, cy, cz):
        self.W, self.H, self.f, self.cx, self.cy, self.cz = W, H, f, cx, cy, cz

    def s(self, z):
        return self.f / max(0.01, z - self.cz)

    def pt(self, x, y, z):
        s = self.s(z)
        return self.W / 2 + (x - self.cx) * s, self.H / 2 + (y - self.cy) * s

    def poly(self, pts, z):
        s = self.s(z)
        return [(self.W / 2 + (x - self.cx) * s, self.H / 2 + (y - self.cy) * s) for x, y in pts]


SKY = [(0.0, hexc("#a7b6c1")), (0.3, hexc("#c8d3d8")), (0.55, hexc("#e4e7e3")),
       (0.72, hexc("#f1e8da")), (1.0, hexc("#ecdcc6"))]


def camera_path(u, W, H):
    portrait = H > W
    frac = 0.64 if portrait else 0.34  # how much of the width the shala spans at the start
    s0 = frac * W / 31.0
    f = s0 * GOP_Z
    cy0 = -96.0 - ((0.07 if portrait else 0.075) * H) / s0
    hold = sstep(0.0, 0.3, u)
    sink = ease_io(sstep(0.22, 0.72, u))
    push = sstep(0.62, 1.0, u)
    cy = cy0 + 3.0 * hold
    cy = mix(cy, -15.0, sink)
    cy = mix(cy, -6.6, ease_io(push))
    cz = 5.0 * hold
    cz = mix(cz, 38.0, sink)
    cz = mix(cz, 97.0, push ** 1.6)
    return Cam(W, H, f, 0.0, cy, cz)


def render(u, W, H, seed=0):
    cam = camera_path(u, W, H)
    px = vgrad(W, H, SKY)
    px += glow(W, H, W * 0.8, H * 0.74, max(W, H) * 0.42, hexc("#ffd9ac"), 0.28, 1.4)
    haze_col = f3(hexc("#e9e6df"))

    def hazed(z, amt):
        return amt * (1 - math.exp(-(z - cam.cz) / 140.0))

    # far tree line
    L = Layer(W, H)
    L.poly(cam.poly(TREES, 520.0), hexc("#9aa29b"))
    rgb, a = L.arrays(blur=1.2)
    k = hazed(520, 0.86)
    px = comp(px, rgb * (1 - k) + haze_col * k * a, a)

    # distant gopurams of the same temple town
    for gx, gz, tone in ((-128.0, 420.0, "#b1b2ad"), (150.0, 540.0, "#bcbcb6")):
        L = MLayer(W, H)
        for poly, col in TOWER:
            if len(col) == 4:
                continue
            L.poly(cam.poly([(x * 0.8 + gx, y * 0.8) for x, y in poly], gz), hexc(tone))
        rgb, a = L.arrays(blur=0.8)
        k = hazed(gz, 0.55)
        px = comp(px, rgb * (1 - k) + haze_col * k * a, a)

    # palms, far to near
    for z, polys in PALMS:
        L = Layer(W, H)
        for p in polys:
            L.poly(cam.poly(p, z), hexc("#3f4a3f"))
        rgb, a = L.arrays(blur=0.6)
        k = hazed(z, 0.9)
        px = comp(px, rgb * (1 - k) + haze_col * k * a, a)

    # far mist band behind the wall
    xx, yy = grid(W, H)
    _, ymist = cam.pt(0, -3.0, 150.0)
    sm = cam.s(150.0)
    band = np.exp(-((yy - ymist) / (9 * sm)) ** 2)
    n = sample_tex(_tex, xx * 0.6 + u * 90, yy * 0.9)
    px = px * (1 - band[..., None] * 0.55 * n[..., None]) + haze_col * band[..., None] * 0.55 * n[..., None]

    # the gopuram and wall, with relief shadows from a low sun on the right
    L = MLayer(W, H, STONE_M)
    s = cam.s(GOP_Z)
    sdx, sdy = -0.24 * s, 0.30 * s
    for poly, col in GOP:
        q = cam.poly(poly, GOP_Z)
        if len(col) == 4:
            L.poly(q, col[:3], col[3], solid=False)
            continue
        if col in LIFT:
            L.poly([(x + sdx, y + sdy) for x, y in q], (48, 38, 30), 105, solid=False)
        L.poly(q, col)
    rgb, a = L.arrays()
    ox, _ = cam.pt(0, 0, GOP_Z)
    shade = 0.93 + 0.12 * np.clip((xx - ox) / (34 * s), -1, 1)
    wy = (yy - H / 2) / s + cam.cy  # world y on the plane
    wx = (xx - W / 2) / s + cam.cx
    tex = sample_tex(_tex, wx * 7 + 5000, wy * 7 + 5000)
    lum = rgb.mean(-1) / np.maximum(a[..., 0], 1e-3)
    lit = shade * (0.93 + 0.14 * tex * np.clip(lum * 1.6, 0, 1))
    warm = np.clip((-wy - 40) / 60, 0, 1) * 0.05
    rgb = rgb * lit[..., None]
    rgb = rgb + a * np.stack([warm, warm * 0.5, -warm * 0.4], -1)
    k = hazed(GOP_Z, 0.34)
    px = comp(px, rgb * (1 - k) + haze_col * k * a, a)

    # warm lamp glow deep inside the gateway
    gx, gy = cam.pt(0, -2.5, GOP_Z + 6)
    add_glow_fast(px, gx, gy, 3.6 * cam.s(GOP_Z + 6), hexc("#d07a2e"), 0.55, sx=1.3, sy=0.8)

    # ground in front of the wall
    _, ybase = cam.pt(0, 0, GOP_Z)
    if ybase < H:
        g = np.clip((yy - ybase) / max(1.0, H - ybase), 0, 1)
        ground = (f3(hexc("#d8ccb8")) * (1 - g[..., None]) + f3(hexc("#b9a88f")) * g[..., None])
        m = (yy >= ybase)[..., None].astype(np.float32)
        px = px * (1 - m) + ground * m
        # stone path to the gate
        L = Layer(W, H)
        quad = []
        for x, z in [(-5.5, GOP_Z - 0.1), (5.5, GOP_Z - 0.1), (8.0, cam.cz + 1.0), (-8.0, cam.cz + 1.0)]:
            quad.append(cam.pt(x, 0, z))
        L.poly(quad, hexc("#c2b5a0"))
        rgb, a = L.arrays()
        px = comp(px, rgb, a)
    # ground mist
    _, ygm = cam.pt(0, -1.0, 90.0)
    band = np.exp(-((yy - ygm) / (5 * cam.s(90.0))) ** 2)
    n = sample_tex(_tex, xx * 0.5 - u * 140, yy * 0.8 + 300)
    k = (band * 0.5 * n)[..., None]
    px = px * (1 - k) + haze_col * k

    # birds
    L = Layer(W, H)
    rng = np.random.default_rng(3)
    for i in range(6):
        bx = (rng.uniform(0.05, 0.55) + u * rng.uniform(0.10, 0.18)) * W
        by = rng.uniform(0.12, 0.34) * H
        sz = rng.uniform(4, 7) * (W / 1280)
        flap = math.sin(u * 60 + i * 1.7) * 0.5
        L.line([(bx - sz, by - sz * (0.3 + flap * 0.4)), (bx, by), (bx + sz, by - sz * (0.3 - flap * 0.4))],
               hexc("#55504a"), 1.2 * W / 1280)
    rgb, a = L.arrays()
    px = comp(px, rgb * 0.8, a * 0.8)

    # the gate swallows the frame: darken towards the end
    dark = sstep(0.93, 1.0, u)
    px = px * (1 - dark * 0.92)
    return px
