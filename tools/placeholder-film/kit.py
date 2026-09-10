"""Small rendering kit for the placeholder film: numpy for light, PIL for shapes."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SS = 2  # supersampling for shapes


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def f3(c):
    return np.array(c, np.float32) / 255.0


def clamp01(x):
    return max(0.0, min(1.0, x))


def sstep(a, b, x):
    t = clamp01((x - a) / (b - a)) if b != a else float(x >= a)
    return t * t * (3 - 2 * t)


def ease_io(t):
    t = clamp01(t)
    return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def mix(a, b, t):
    return a + (b - a) * t


def mixc(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


class Layer:
    """RGBA surface drawn at SS x and flattened to premultiplied float arrays."""

    def __init__(self, W, H):
        self.W, self.H = W, H
        self.im = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)


    @staticmethod
    def _c(col, a):
        return (int(round(col[0])), int(round(col[1])), int(round(col[2])), int(round(a)))

    def poly(self, pts, col, a=255):
        if len(pts) < 3:
            return
        self.d.polygon([(x * SS, y * SS) for x, y in pts], fill=self._c(col, a))

    def ellipse(self, cx, cy, rx, ry, col, a=255):
        if rx <= 0 or ry <= 0:
            return
        self.d.ellipse([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS],
                       fill=self._c(col, a))

    def line(self, pts, col, width, a=255):
        if len(pts) < 2:
            return
        self.d.line([(x * SS, y * SS) for x, y in pts], fill=self._c(col, a),
                    width=max(1, int(round(width * SS))), joint="curve")

    def arrays(self, blur=0.0):
        im = self.im.convert("RGBa").resize((self.W, self.H), Image.BOX)
        if blur > 0:
            im = im.filter(ImageFilter.GaussianBlur(blur))
        a = np.asarray(im, np.float32) / 255.0
        return a[..., :3], a[..., 3:4]


class MLayer:
    """Opaque colour surface + separate coverage mask. Draws blend (so shadows can
    darken what is underneath) and only solid shapes add to the silhouette."""

    def __init__(self, W, H, base=(128, 128, 128)):
        self.W, self.H = W, H
        self.rgb = Image.new("RGB", (W * SS, H * SS), tuple(int(c) for c in base))
        self.mask = Image.new("L", (W * SS, H * SS), 0)
        self.d = ImageDraw.Draw(self.rgb, "RGBA")
        self.dm = ImageDraw.Draw(self.mask)

    def poly(self, pts, col, a=255, solid=True):
        if len(pts) < 3:
            return
        q = [(x * SS, y * SS) for x, y in pts]
        self.d.polygon(q, fill=(int(col[0]), int(col[1]), int(col[2]), int(a)))
        if solid:
            self.dm.polygon(q, fill=255)

    def arrays(self, blur=0.0):
        rgb = self.rgb.resize((self.W, self.H), Image.BOX)
        m = self.mask.resize((self.W, self.H), Image.BOX)
        if blur > 0:
            rgb = rgb.filter(ImageFilter.GaussianBlur(blur))
            m = m.filter(ImageFilter.GaussianBlur(blur))
        rgb = np.asarray(rgb, np.float32) / 255.0
        a = np.asarray(m, np.float32)[..., None] / 255.0
        return rgb * a, a


def comp(px, layer_rgb_p, layer_a):
    """Premultiplied over."""
    return px * (1.0 - layer_a) + layer_rgb_p


def vgrad(W, H, stops):
    """stops: [(y_fraction, (r,g,b) 0-255), ...] -> HxWx3 float."""
    y = (np.arange(H, dtype=np.float32) + 0.5) / H
    ys = [s[0] for s in stops]
    cols = np.stack([np.interp(y, ys, [s[1][i] / 255.0 for s in stops]) for i in range(3)], -1)
    return np.repeat(cols[:, None, :], W, axis=1).astype(np.float32)


_grid_cache = {}


def grid(W, H):
    key = (W, H)
    if key not in _grid_cache:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        _grid_cache[key] = (xx + 0.5, yy + 0.5)
    return _grid_cache[key]


def glow(W, H, cx, cy, r, color, strength=1.0, power=2.0, sx=1.0, sy=1.0):
    """Additive soft glow; returns HxWx3."""
    xx, yy = grid(W, H)
    d2 = ((xx - cx) / (r * sx)) ** 2 + ((yy - cy) / (r * sy)) ** 2
    g = np.exp(-d2 * power) * strength
    return g[..., None] * f3(color)[None, None, :]


def glow_fast(W, H, cx, cy, r, color, strength=1.0, sx=1.0, sy=1.0):
    """Same as glow() but only touches the bounding box (for many small lights)."""
    out_w = int(3 * r * sx) + 2
    out_h = int(3 * r * sy) + 2
    x0, x1 = max(0, int(cx - out_w)), min(W, int(cx + out_w))
    y0, y1 = max(0, int(cy - out_h)), min(H, int(cy + out_h))
    if x0 >= x1 or y0 >= y1:
        return None
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    d2 = ((xx + 0.5 - cx) / (r * sx)) ** 2 + ((yy + 0.5 - cy) / (r * sy)) ** 2
    g = np.exp(-d2 * 2.0) * strength
    return (slice(y0, y1), slice(x0, x1)), g[..., None] * f3(color)[None, None, :]


def add_glow_fast(px, *args, **kw):
    r = glow_fast(px.shape[1], px.shape[0], *args, **kw)
    if r is not None:
        (sy, sx), g = r
        px[sy, sx] += g


def value_noise(w, h, seed, octaves=4, scale=64.0, beta=2.0):
    """Tileable cloudy noise in 0..1 built in the frequency domain."""
    rng = np.random.default_rng(seed)
    fx = np.fft.fftfreq(w)[None, :]
    fy = np.fft.fftfreq(h)[:, None]
    f = np.sqrt(fx * fx + fy * fy)
    f0 = 1.0 / scale
    amp = np.where(f < f0, (f0 ** (-beta / 2)) * (f / f0), np.maximum(f, 1e-9) ** (-beta / 2))
    amp[0, 0] = 0
    spec = (rng.normal(size=(h, w)) + 1j * rng.normal(size=(h, w))) * amp
    n = np.real(np.fft.ifft2(spec))
    n = (n - n.min()) / (n.max() - n.min() + 1e-9)
    return n.astype(np.float32)


def sample_tex(tex, u, v):
    """Wrap-sample a 2D texture with float coordinate arrays (bilinear)."""
    th, tw = tex.shape[:2]
    u0 = np.floor(u)
    v0 = np.floor(v)
    fu = (u - u0).astype(np.float32)
    fv = (v - v0).astype(np.float32)
    iu0 = np.mod(u0.astype(np.int64), tw)
    iv0 = np.mod(v0.astype(np.int64), th)
    iu1 = np.mod(iu0 + 1, tw)
    iv1 = np.mod(iv0 + 1, th)
    a = tex[iv0, iu0] * (1 - fu) + tex[iv0, iu1] * fu
    b = tex[iv1, iu0] * (1 - fu) + tex[iv1, iu1] * fu
    return a * (1 - fv) + b * fv


def finish(px, seed, grain=0.022, vignette=0.28, lift=0.0):
    """Film finish: gentle curve, vignette, grain."""
    H, W = px.shape[:2]
    xx, yy = grid(W, H)
    nx = (xx / W - 0.5) * 2
    ny = (yy / H - 0.5) * 2
    v = 1.0 - vignette * np.clip((nx * nx * 0.55 + ny * ny * 0.75), 0, 1.6) ** 1.3
    px = px * v[..., None]
    px = px + lift
    rng = np.random.default_rng(seed)
    n = rng.normal(0, grain, (H // 2 + 1, W // 2 + 1)).astype(np.float32)
    n = np.repeat(np.repeat(n, 2, 0), 2, 1)[:H, :W]
    px = px + n[..., None] * (0.6 + 0.4 * px)
    # soft shoulder so highlights roll off instead of clipping
    px = np.where(px > 0.82, 0.82 + (1 - np.exp(-(px - 0.82) * 3.2)) * 0.18 / 1.0, px)
    return np.clip(px, 0, 1)


def bloom(px, threshold=0.72, radius=18, strength=0.55):
    H, W = px.shape[:2]
    hi = np.clip(px - threshold, 0, None)
    small = Image.fromarray(np.clip(hi * 255 * 2, 0, 255).astype(np.uint8)).resize(
        (max(1, W // 4), max(1, H // 4)), Image.BILINEAR)
    small = small.filter(ImageFilter.GaussianBlur(radius / 4))
    big = np.asarray(small.resize((W, H), Image.BILINEAR), np.float32) / 255.0 / 2
    return px + big * strength


def to_image(px):
    return Image.fromarray((np.clip(px, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")


def blur_arr(px, radius):
    im = to_image(px).filter(ImageFilter.GaussianBlur(radius))
    return np.asarray(im, np.float32) / 255.0


def spot(px, cx, cy, rx, ry, col, s=1.0):
    """Add a small elliptical gaussian glow in place (touches only its box)."""
    H, W = px.shape[:2]
    if rx < 0.3 or ry < 0.3:
        return px
    x0, x1 = int(max(0, cx - 3 * rx)), int(min(W, cx + 3 * rx + 1))
    y0, y1 = int(max(0, cy - 3 * ry)), int(min(H, cy + 3 * ry + 1))
    if x0 >= x1 or y0 >= y1:
        return px
    ys, xs = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    g = np.exp(-(((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2) * 0.5) * s
    px[y0:y1, x0:x1] += g[..., None] * f3(col)
    return px
