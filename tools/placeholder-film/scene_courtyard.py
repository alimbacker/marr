"""Scene C — the temple tank at sunrise: stone steps, floating lamps, a pavilion
in the water, towers and trees mirrored in the still surface."""
import math
import numpy as np
from kit import *

SKY = [(0.0, hexc("#8ea6bb")), (0.28, hexc("#c9c2bb")), (0.45, hexc("#eec79a")),
       (0.58, hexc("#f5b56d")), (0.66, hexc("#f2a45a")), (1.0, hexc("#f2a45a"))]
SIL_NEAR = hexc("#2a1e16")
SIL_MID = hexc("#5a4030")
HORIZON = hexc("#efb27a")
RIM = hexc("#ffd38a")

_tex = value_noise(512, 512, 77, scale=48.0)


class Cam:
    def __init__(self, W, H, cz, eye, cx=0.0):
        self.W, self.H, self.cz, self.eye, self.cx = W, H, cz, eye, cx
        self.f = 0.72 * W if W >= H else 1.25 * W
        self.hz = 0.62 * H

    def d(self, z):
        return max(0.05, z - self.cz)

    def pt(self, x, y, z):
        d = self.d(z)
        return self.W / 2 + self.f * (x - self.cx) / d, self.hz + self.f * (y + self.eye) / d

    def poly(self, pts, z):
        return [self.pt(x, y, z) for x, y in pts]


def tree_blob(rng, cx, h, r):
    """Canopy outline as a lumpy closed polygon (world, y up negative)."""
    pts = []
    lumps = [(rng.uniform(0, 2 * math.pi), rng.uniform(0.1, 0.25)) for _ in range(7)]
    for k in range(90):
        a = k * 2 * math.pi / 90
        rr = r * (1 + sum(amp * math.cos(3 * a + ph) for ph, amp in lumps[:3]) / 2
                  + 0.06 * math.sin(a * 17 + lumps[3][0]))
        pts.append((cx + rr * 1.35 * math.cos(a), -h + rr * 0.8 * math.sin(a)))
    return pts


def build():
    rng = np.random.default_rng(19)
    trees = []
    for cx, z, h, r in [(-60, 170, 22, 13), (-34, 190, 18, 10), (48, 175, 20, 12),
                        (80, 200, 25, 15), (-95, 210, 24, 16), (115, 220, 20, 12)]:
        trunk = [(cx - 0.8, 0), (cx + 0.8, 0), (cx + 0.5, -h + 3), (cx - 0.5, -h + 3)]
        trees.append((z, [trunk, tree_blob(rng, cx, h, r)]))
    # vimana over the sanctum
    v = []
    base_w, y = 26.0, 0.0
    v.append([(-base_w / 2, 0), (base_w / 2, 0), (base_w / 2, -9), (-base_w / 2, -9)])
    y = -9.0
    w = base_w - 2
    for k in range(4):
        h = 4.2 - 0.4 * k
        v.append([(-w / 2, y), (w / 2, y), (w / 2 - 1.2, y - h), (-w / 2 + 1.2, y - h)])
        for i in range(-2, 3):  # little kutas on each storey
            xk = i * (w / 5.2)
            v.append([(xk - 1.0, y - h), (xk + 1.0, y - h), (xk + 0.8, y - h - 1.2), (xk, y - h - 1.8), (xk - 0.8, y - h - 1.2)])
        y -= h
        w -= 4.6
    dome = [(math.cos(a) * 5.2, y - 0.5 + math.sin(a) * 4.6) for a in np.linspace(math.pi, 2 * math.pi, 30)]
    v.append([(-5.6, y), (5.6, y)] + dome[::-1])
    v.append([(-0.5, y - 4.8), (0.5, y - 4.8), (0.9, y - 6.0), (0, y - 8.2), (-0.9, y - 6.0)])
    return trees, v


TREES, VIMANA = build()


def sil_layer(W, H, polys_proj, col, blur=0.0):
    L = Layer(W, H)
    for p in polys_proj:
        L.poly(p, col)
    return L.arrays(blur)


def rim(a, sx, sy, strength):
    """Light the edges of a silhouette that face the sun."""
    a = a[..., 0] if a.ndim == 3 else a
    sh = np.roll(np.roll(a, int(round(sy)), 0), int(round(sx)), 1)
    return np.clip(a - sh, 0, 1) * strength



BANK_Z = 98.0
WALL_Z = 105.0
WATER = hexc("#2b2627")
STEPS = [(-2.4, 8.0, 12.0), (-1.8, 12.0, 14.5), (-1.2, 14.5, 17.0), (-0.6, 17.0, 19.5)]
DIYAS = [(-7.0, 30.0), (-3.5, 24.0), (2.5, 34.0), (6.0, 27.0), (-11.0, 40.0), (9.5, 45.0),
         (0.5, 50.0), (-5.0, 62.0), (13.0, 36.0), (-14.0, 55.0), (4.0, 70.0), (-9.0, 78.0)]


def mandapam(x0):
    """Neerazhi mandapam: an open pavilion standing in the middle of the tank."""
    P = [[(x0 - 6.6, 0.0), (x0 + 6.6, 0.0), (x0 + 6.6, -1.6), (x0 - 6.6, -1.6)],
         [(x0 - 7.0, -1.6), (x0 + 7.0, -1.6), (x0 + 7.0, -2.2), (x0 - 7.0, -2.2)]]
    for xp in (-5.4, -1.9, 1.9, 5.4):
        P.append([(x0 + xp - 0.5, -2.2), (x0 + xp + 0.5, -2.2), (x0 + xp + 0.5, -7.4), (x0 + xp - 0.5, -7.4)])
        P.append([(x0 + xp - 0.8, -6.9), (x0 + xp + 0.8, -6.9), (x0 + xp + 0.8, -7.4), (x0 + xp - 0.8, -7.4)])
    P.append([(x0 - 6.9, -7.4), (x0 + 6.9, -7.4), (x0 + 7.7, -8.5), (x0 - 7.7, -8.5)])
    w, y = 6.3, -8.5
    for k in range(3):
        h = 1.7 - 0.3 * k
        P.append([(x0 - w, y), (x0 + w, y), (x0 + w - 0.9, y - h), (x0 - w + 0.9, y - h)])
        for i in (-1, 0, 1):
            xk = x0 + i * (w * 0.62)
            P.append([(xk - 0.6, y - h), (xk + 0.6, y - h), (xk, y - h - 0.9)])
        y -= h
        w -= 1.6
    dome = [(x0 + math.cos(a) * 2.3, y + math.sin(a) * 2.1) for a in np.linspace(math.pi, 2 * math.pi, 24)]
    P.append([(x0 - 2.5, y), (x0 + 2.5, y)] + dome[::-1])
    P.append([(x0 - 0.25, y - 2.0), (x0 + 0.25, y - 2.0), (x0 + 0.45, y - 2.6), (x0, y - 3.6), (x0 - 0.45, y - 2.6)])
    return P


MANDAPAM = mandapam(0.0)


def camera_path(u, W, H):
    e = ease_io(u)
    cz = mix(0.0, 20.0, e * 0.4 + u * 0.6)
    eye = mix(5.2, 3.2, e)
    return Cam(W, H, cz, eye, 0.5 * math.sin(u * 1.3))


def render(u, W, H, seed=0):
    import scene_gopuram as A
    cam = camera_path(u, W, H)
    wide = W >= H
    xx, yy = grid(W, H)
    sky = vgrad(W, H, [(p * cam.hz / H, c) for p, c in SKY[:-1]] + [(1.0, SKY[-1][1])])
    px = sky.copy()
    sun_x = W * (0.58 if wide else 0.64)
    sun_y = mix(cam.hz * 0.95, cam.hz * 0.52, ease_io(u) * 0.7 + u * 0.3)
    R = 0.028 * max(W, H)
    px += glow(W, H, sun_x, sun_y, R * 16, hexc("#ffb866"), 0.45, 1.2)
    px += glow(W, H, sun_x, sun_y, R * 4.5, hexc("#ffd9a0"), 0.55, 1.6)
    d2 = ((xx - sun_x) ** 2 + (yy - sun_y) ** 2) / (R * R)
    px += np.clip(1.6 - d2, 0, 1)[..., None] * f3(hexc("#fff6e4")) * 1.4

    def haze_mix(rgb, a, z, amt=0.9, zref=260.0):
        k = amt * (1 - math.exp(-cam.d(z) / zref))
        return rgb * (1 - k) + f3(HORIZON) * k * a

    # distant towers
    ty = min(y for poly, col in A.TOWER for x, y in poly)
    for sc, xo, zt in ((70.0, -52.0, 480.0), (46.0, 88.0, 560.0)):
        L = MLayer(W, H)
        k = sc / abs(ty)
        for poly, col in A.TOWER:
            if len(col) == 4:
                continue
            L.poly(cam.poly([(x * k + xo * (1 if wide else 0.55), y * k) for x, y in poly], zt), SIL_MID)
        rgb, a = L.arrays(1.0)
        px = comp(px, haze_mix(rgb, a, zt, 0.93, 200.0), a)

    for z, polys in sorted(TREES, key=lambda t: -t[0]):
        rgb, a = sil_layer(W, H, [cam.poly(p, z) for p in polys], SIL_MID, 1.2)
        n = sample_tex(_tex, xx * 0.8, yy * 0.8)
        a = a * np.clip(0.75 + 0.5 * n[..., None], 0, 1)
        rgb = rgb * np.clip(0.75 + 0.5 * n[..., None], 0, 1)
        px = comp(px, haze_mix(rgb, a, z, 0.8, 200.0), a)

    z = 150.0
    rgb, a = sil_layer(W, H, [cam.poly([(x + 26, y) for x, y in p], z) for p in VIMANA], SIL_MID)
    px = comp(px, haze_mix(rgb, a, z, 0.7, 220.0), a)
    px += rim(a, (sun_x - W / 2) * 0.004 + 2, 3, 0.8)[..., None] * f3(RIM)

    # prakaram wall beyond the tank, then the far bank's steps
    L = Layer(W, H)
    L.poly(cam.poly([(-400, -1.6), (400, -1.6), (400, -12.6), (-400, -12.6)], WALL_Z), SIL_MID)
    L.poly(cam.poly([(-400, -12.6), (400, -12.6), (400, -13.8), (-400, -13.8)], WALL_Z), hexc("#7a5840"))
    for i in range(-80, 81):
        x = i * 5.0
        L.poly(cam.poly([(x, -3.0), (x + 2.5, -3.0), (x + 2.5, -11.8), (x, -11.8)], WALL_Z), hexc("#6d3a2a"))
    rgb, a = L.arrays()
    px = comp(px, haze_mix(rgb, a, WALL_Z, 0.55, 180.0), a)
    px += rim(a, 0, 2, 0.6)[..., None] * f3(RIM)
    L = Layer(W, H)
    L.poly(cam.poly([(-400, 0.0), (400, 0.0), (400, -1.6), (-400, -1.6)], BANK_Z), hexc("#c29868"))
    for k in range(1, 4):
        yk = -0.4 * k
        L.poly(cam.poly([(-400, yk + 0.08), (400, yk + 0.08), (400, yk), (-400, yk)], BANK_Z), hexc("#8a6446"))
    rgb, a = L.arrays()
    px = comp(px, haze_mix(rgb, a, BANK_Z, 0.5, 180.0), a)

    _, ym = cam.pt(0, -3.0, 100.0)
    band = np.exp(-((yy - ym) / (H * 0.05)) ** 2)
    n = sample_tex(_tex, xx * 0.6 + u * 120, yy * 1.2 + 50)
    k = (band * 0.5 * n)[..., None]
    px = px * (1 - k) + f3(hexc("#f6c48e")) * k

    # the water holds everything above it
    up = px.copy()
    y_w = float(cam.pt(0, 0, BANK_Z)[1])
    t = np.clip((yy - y_w) / max(1.0, H - y_w), 0, 1)
    n1 = sample_tex(_tex, xx * 0.03 + u * 12, yy * 0.8) - 0.5
    my = np.clip(2 * y_w - yy + n1 * (1 + 12 * t), 0, H - 1).astype(np.int64)
    mx = np.clip(xx + n1 * (2 + 26 * t), 0, W - 1).astype(np.int64)
    upb = blur_arr(up, 2.5)
    refl = up[my, mx] * (1 - t[..., None]) + upb[my, mx] * t[..., None]
    k = (0.8 - 0.36 * t)[..., None]
    water = refl * k + f3(WATER) * (1 - k)
    glint = np.exp(-((xx - sun_x) / (W * 0.015 + t * W * 0.07)) ** 2) * np.exp(-t * 2.2)
    streak = np.clip(sample_tex(_tex, xx * 0.02 + 40, yy * 3.0 - u * 30) - 0.45, 0, 1) * 2.2
    water += (glint * (0.5 + streak))[..., None] * f3(hexc("#ffd49a")) * 0.6
    px = np.where((yy > y_w)[..., None], water, px)

    # pavilion in the water, with its reflection
    mz, mxo = 64.0, (-13.0 if wide else -7.5)
    L = Layer(W, H)
    for poly in MANDAPAM:
        L.poly(cam.poly([(x + mxo, -y) for x, y in poly], mz), hexc("#3a2a22"))
    rgb, a = L.arrays(1.6)
    px = comp(px, rgb * 0.55, a * 0.55)
    L = Layer(W, H)
    for poly in MANDAPAM:
        L.poly(cam.poly([(x + mxo, y) for x, y in poly], mz), SIL_MID)
    rgb, a = L.arrays()
    px = comp(px, haze_mix(rgb, a, mz, 0.55, 180.0), a)
    px += rim(a, 2, 2, 0.8)[..., None] * f3(RIM)

    # floating lamps
    L = Layer(W, H)
    flames = []
    for i, (dx, dz) in enumerate(DIYAS):
        if dz < cam.cz + 1.5:
            continue
        sx, sy = cam.pt(dx if wide else dx * 0.6, 0.0, dz)
        s = cam.f / cam.d(dz)
        L.ellipse(sx, sy, 0.7 * s, 0.16 * s, hexc("#2d3a1c"))
        L.ellipse(sx, sy - 0.1 * s, 0.32 * s, 0.12 * s, hexc("#8a5a2a"))
        flames.append((sx, sy - 0.32 * s, s, i))
    rgb, a = L.arrays()
    px = comp(px, rgb, a)
    for sx, sy, s, i in flames:
        fl = 1 + 0.2 * math.sin(u * 50 + i * 2.1)
        spot(px, sx, sy, 0.16 * s * fl, 0.28 * s * fl, hexc("#fff1c4"), 1.3)
        spot(px, sx, sy, 0.9 * s, 0.9 * s, hexc("#ffa446"), 0.35)
        for q in range(1, 5):
            spot(px, sx, sy + (0.4 + 0.35 * q) * s, 0.22 * s, 0.12 * s, hexc("#ffb866"), 0.35 / q)

    # the near steps of the tank
    L = Layer(W, H)
    for yt, z0, z1 in STEPS:
        z0c = max(z0, cam.cz + 0.6)
        if z1 <= z0c:
            continue
        L.poly([cam.pt(-300, yt, z0c), cam.pt(300, yt, z0c), cam.pt(300, yt, z1), cam.pt(-300, yt, z1)], hexc("#b48a5f"))
        L.poly([cam.pt(-300, yt, z1), cam.pt(300, yt, z1), cam.pt(300, yt + 0.6, z1), cam.pt(-300, yt + 0.6, z1)], hexc("#5e412c"))
    rgb, a = L.arrays()
    tex = (0.82 + 0.3 * sample_tex(_tex, xx * 0.5, yy * 0.5))[..., None]
    px = comp(px, rgb * tex, a)

    L = Layer(W, H)
    rng = np.random.default_rng(8)
    for i in range(9):
        bx = (rng.uniform(0.1, 0.5) + u * rng.uniform(0.25, 0.4)) * W
        by = (rng.uniform(0.1, 0.26) - u * 0.05) * H
        sz = rng.uniform(4, 8) * max(W, H) / 1280
        flap = math.sin(u * 70 + i * 1.3) * 0.5
        L.line([(bx - sz, by - sz * (0.3 + flap * 0.4)), (bx, by), (bx + sz, by - sz * (0.3 - flap * 0.4))],
               hexc("#3a2c24"), 1.3 * max(W, H) / 1280)
    rgb, a = L.arrays()
    px = comp(px, rgb, a)

    px = bloom(px, 0.8, 30, 0.5)
    white = 1 - sstep(0.0, 0.1, u)
    px = px * (1 - white * 0.3) + f3(hexc("#fbe9cc")) * white * 0.9
    return px
