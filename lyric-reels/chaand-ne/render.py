"""Lyric reel: moonrise over the sea, Urdu lyrics 2 to 3 words at a time.

Usage:
  python3 render.py --audio song.mp4 --font NotoNastaliqUrdu.woff --out reel.mp4 [--bg stock.mp4]

--audio  any file holding the song (the reference clip works; timings below match it)
--font   Noto Nastaliq Urdu (npm pack @fontsource/noto-nastaliq-urdu, files/*arabic-500-normal.woff)
--bg     optional stock clip (Pexels/Pixabay etc). Without it the sky/sea scene is generated.
"""
import argparse, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
HORIZON = 1180

# (word, start, end) in seconds, read off the reference clip
WORDS = [("کیا", .30, 1.23), ("کہا", 1.23, 1.93), ("ہے", 2.07, 2.67), ("چاند", 2.67, 3.40), ("نے", 3.40, 4.77),
         ("جس", 4.77, 5.70), ("کو", 5.83, 6.47), ("سن", 6.47, 6.97), ("کے", 6.97, 7.43), ("چاندنی", 7.43, 9.50),
         ("ہر", 9.50, 10.43), ("لہر", 10.43, 11.60), ("میں", 11.60, 12.00), ("جھوم", 12.00, 12.90), ("کے", 12.90, 14.33),
         ("کیوں", 14.33, 15.33), ("یہ", 15.33, 15.97), ("ناچنے", 16.23, 17.50), ("لگی", 17.50, 18.03),
         ("چاہت", 18.03, 20.17), ("کا", 20.17, 20.63), ("ہے", 20.63, 21.27), ("ہر", 21.27, 21.63), ("سو", 21.63, 22.07),
         ("اثر", 22.07, 23.27), ("پھر", 23.27, 23.93), ("کیوں", 23.93, 24.77), ("مجھ", 24.77, 25.27), ("کو", 25.27, 25.83),
         ("لگتا", 25.83, 26.30), ("ہے", 26.30, 26.80), ("ڈر", 26.80, 27.90)]
# word counts per on-screen group
GROUPS = [3, 2, 2, 3, 3, 2, 2, 2, 3, 3, 2, 2, 3]
DUR = 28.07


def smooth(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)


def noise2d(h, w, seed, beta=1.8, stretch=1.0):
    """Tileable fractal (1/f) noise in 0..1; stretch > 1 makes it streaky along x."""
    rng = np.random.default_rng(seed)
    fy = np.fft.fftfreq(h)[:, None]; fx = np.fft.fftfreq(w)[None, :] * stretch
    f = np.sqrt(fx ** 2 + fy ** 2); f[0, 0] = 1
    spec = np.fft.fft2(rng.normal(size=(h, w))) / f ** beta; spec[0, 0] = 0
    out = np.real(np.fft.ifft2(spec))
    lo, hi = np.percentile(out, [1, 99])
    return np.clip((out - lo) / (hi - lo), 0, 1).astype(np.float32)


def smooth_arr(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)


def lerp(a, b, t): return a + (b - a) * t


class Scene:
    def __init__(self):
        y = np.arange(H, dtype=np.float32)[:, None]
        x = np.arange(W, dtype=np.float32)[None, :]
        self.x, self.y = x, y
        top, mid, hor = np.array([14, 18, 44]), np.array([64, 58, 104]), np.array([236, 158, 118])
        t = np.clip(y / HORIZON, 0, 1)[..., None]
        sky = np.where(t < 0.55, lerp(top, mid, np.clip(t / 0.55, 0, 1)), lerp(mid, hor, np.clip((t - 0.55) / 0.45, 0, 1) ** 1.4))
        self.sky = np.broadcast_to(sky, (H, W, 3)).astype(np.float32).copy()
        rng = np.random.default_rng(3)
        n = 260; self.stars = (rng.random(n) * W, rng.random(n) ** 1.8 * HORIZON * 0.7, rng.random(n), rng.random(n) * 6.28)
        self.clouds = noise2d(H // 2, W, 7, 1.7, stretch=3.5)
        self.crater = noise2d(256, 256, 11, 1.4)
        # distant hills on the horizon
        hx = np.arange(W); r = np.random.default_rng(5)
        hill = 40 * np.sin(hx / 210 + 1.3) + 22 * np.sin(hx / 77) + 10 * np.sin(hx / 23 + r.random())
        self.hill = (HORIZON - np.clip(hill + 18, 0, None) * np.clip((hx - 520) / 300, 0, 1) ** 0.6).astype(int)
        # water depth: 0 at horizon, 1 at the bottom
        self.depth = np.clip((y - HORIZON) / (H - HORIZON), 0, 1)
        self.ripples = noise2d(256, 1024, 21, 1.6)
        self.birds = [(1.2, 9.0, 330, 0.9, 1), (4.0, 13.0, 260, 0.7, -1), (11.5, 19.5, 420, 1.0, 1),
                      (12.3, 20.5, 470, 0.75, 1), (19.0, 27.0, 300, 0.85, -1)]

    def frame(self, t):
        img = self.sky.copy()
        x, y = self.x, self.y
        mx, my = 540.0, lerp(1010.0, 840.0, smooth(t / DUR))  # moon rises
        mr = 92.0
        # stars, fading in as the sky darkens
        sx, sy, sb, sp = self.stars
        tw = (0.55 + 0.45 * np.sin(t * 2.2 + sp)) * sb * (1 - sy / (HORIZON * 0.7)) * 200
        ix, iy = sx.astype(int), sy.astype(int)
        for dx, dy, k in ((0, 0, 1.0), (1, 0, .35), (0, 1, .35)):
            img[np.clip(iy + dy, 0, H - 1), np.clip(ix + dx, 0, W - 1)] += (tw * k)[:, None]
        # moon glow
        d = np.sqrt((x - mx) ** 2 + (y - my) ** 2)
        glow = np.exp(-np.clip(d - mr, 0, None) / 170) * 0.55 + np.exp(-np.clip(d - mr, 0, None) / 40) * 0.35
        img += glow[..., None] * np.array([255, 226, 190]) * 0.55
        # moon disc with soft craters
        disc = np.clip(mr - d + 1.5, 0, 1)
        y0, x0 = int(my - mr), int(mx - mr)
        cr = np.asarray(Image.fromarray((self.crater * 255).astype(np.uint8)).resize((int(2 * mr), int(2 * mr))), np.float32) / 255
        moon = np.zeros((H, W), np.float32); moon[y0:y0 + cr.shape[0], x0:x0 + cr.shape[1]] = cr
        mt = smooth_arr((moon - 0.35) * 2.2)[..., None]
        mcol = lerp(np.array([255, 249, 236]), np.array([222, 216, 210]), mt * 0.8)
        img = img * (1 - disc[..., None]) + mcol * disc[..., None]
        # drifting clouds, lit from below by the moon
        c = np.asarray(Image.fromarray((self.clouds * 255).astype(np.uint8)).resize((W * 2, H)), np.float32) / 255
        sh = int(t * 12) % W
        c = c[:, sh:sh + W]
        band = np.exp(-((y - 560) / 220) ** 2) * 0.9 + np.exp(-((y - 1000) / 90) ** 2) * 0.7
        ca = smooth_arr((c - 0.5) * 2.6) * band
        lit = np.clip(np.exp(-d / 300) + np.clip((y - 700) / 500, 0, 1) * 0.5, 0, 1)[..., None]
        ccol = lerp(np.array([30, 28, 56]), np.array([214, 140, 132]), lit)
        img = img * (1 - ca[..., None] * .85) + ccol * ca[..., None] * .85
        # sea
        dep = self.depth
        water = lerp(np.array([92, 74, 96]), np.array([8, 12, 28]), dep[..., None] ** 0.5)
        sea = (y >= HORIZON)[..., None]
        # horizon reflection of the sky glow
        water = water + np.array([150, 92, 70]) * np.exp(-dep * 18)[..., None]
        # moonlight path: glints on moving ripples, widening toward the viewer
        Z = 1.0 / (dep + 0.02)
        X = (x - mx) * Z / 740
        n = self.ripples[(Z * 9 + t * 2).astype(np.int32) % 256, (X * 40 + 512).astype(np.int32) % 1024]
        ph = n * 7
        h = (np.sin(78 * Z + 2.1 * t + ph) * 0.5 + np.sin(47 * Z + 5 * X - 1.6 * t + ph * 0.7) * 0.3
             + np.sin(61 * Z - 7 * X + 1.3 * t + ph * 1.3) * 0.2)
        h = h * (0.6 + 0.8 * n)
        fade = np.clip(dep * 6, 0, 1) ** 0.8
        width = 22 + dep * 190
        path = np.exp(-((x - mx) / width) ** 2)
        sharp = np.clip((h - 0.35) * 2.2, 0, 1) ** 2
        glint = path * (sharp * fade + (1 - fade) * 0.45) * (0.55 + dep * 0.6)
        water = water + np.array([255, 238, 210]) * glint[..., None]
        water = water + np.array([40, 34, 60]) * (np.clip(h, 0, 1) * 0.6 * fade)[..., None]
        img = np.where(sea, water, img)
        # hills
        hm = (y >= self.hill[None, :]) & (y < HORIZON + 2)
        img[hm] = img[hm] * 0.15 + np.array([24, 20, 40]) * 0.85
        # birds
        pil = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
        dr = ImageDraw.Draw(pil)
        for t0, t1, by, s, dirn in self.birds:
            if t0 <= t <= t1:
                p = (t - t0) / (t1 - t0)
                bx = lerp(-80, W + 80, p) if dirn > 0 else lerp(W + 80, -80, p)
                byy = by + 30 * math.sin(p * 5) - p * 60
                flap = math.sin(t * 9 + t0) * 14 * s
                L = 26 * s
                pts = [(bx - L, byy - flap), (bx - L * 0.45, byy - flap * 0.4 - 4 * s), (bx, byy + 3 * s),
                       (bx + L * 0.45, byy - flap * 0.4 - 4 * s), (bx + L, byy - flap)]
                dr.line(pts, fill=(18, 16, 30), width=max(3, int(4 * s)), joint="curve")
        out = np.asarray(pil, np.float32)
        # vignette and grain
        v = 1 - 0.38 * (((x - W / 2) / (W * 0.75)) ** 2 + ((y - H / 2) / (H * 0.7)) ** 2)
        out = out * v[..., None] + np.random.default_rng(int(t * FPS)).normal(0, 4, (H, W, 1))
        return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


class Lyrics:
    def __init__(self, font_path):
        self.font = ImageFont.truetype(font_path, 92, layout_engine=ImageFont.Layout.RAQM)
        self.groups, i = [], 0
        for n in GROUPS:
            ws = WORDS[i:i + n]; i += n
            text = " ".join(w for w, _, _ in ws)
            layer = Image.new("L", (W, 360), 0)
            ImageDraw.Draw(layer).text((W / 2, 180), text, font=self.font, fill=255, anchor="mm",
                                        direction="rtl", language="ur")
            full = self.font.getlength(text, direction="rtl", language="ur")
            right = W / 2 + full / 2
            # x where each word ends (RTL: words grow leftward from the right edge)
            edges = [right - self.font.getlength(" ".join(w for w, _, _ in ws[:k + 1]), direction="rtl", language="ur") - 12
                     for k in range(n)]
            edges[-1] = 0
            self.groups.append((ws, layer, edges))
        assert i == len(WORDS)
        for gi, (ws, _, _) in enumerate(self.groups):
            nxt = self.groups[gi + 1][0][0][1] if gi + 1 < len(self.groups) else DUR
            self.groups[gi] += (min(nxt, ws[-1][2] + 0.6),)

    def overlay(self, img, t, cy=560):
        xs = np.arange(W, dtype=np.float32)[None, :]
        for ws, layer, edges, end in self.groups:
            if not (ws[0][1] - 0.05 <= t < end): continue
            out_a = 1 - smooth((t - (end - 0.18)) / 0.18)
            mask = np.zeros((1, W), np.float32); lift = 0.0
            prev_edge = W
            for (w, st, en), edge in zip(ws, edges):
                a = smooth((t - st + 0.05) / 0.2)
                seg = ((xs >= edge) & (xs < prev_edge)).astype(np.float32)
                mask = np.maximum(mask, seg * a)
                prev_edge = edge
            a = np.asarray(layer, np.float32) / 255 * mask * out_a
            yoff = int(cy - 180 + lift)
            alpha = Image.fromarray((a * 255).astype(np.uint8))
            shadow = alpha.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.55))
            img.paste((10, 8, 24), (0, yoff + 4), shadow)
            img.paste((255, 250, 240), (0, yoff), alpha)
        return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True); ap.add_argument("--font", required=True)
    ap.add_argument("--out", default="reel.mp4"); ap.add_argument("--bg")
    ap.add_argument("--preview", type=float, nargs="*")
    a = ap.parse_args()
    lyr = Lyrics(a.font)
    if a.preview is not None:
        sc = Scene()
        for t in a.preview: lyr.overlay(sc.frame(t), t).save(f"preview_{t:05.2f}.jpg", quality=90)
        return
    n = int(DUR * FPS)
    if a.bg:
        src = subprocess.Popen(["ffmpeg", "-v", "error", "-stream_loop", "-1", "-i", a.bg, "-t", str(DUR), "-vf",
                                f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},eq=brightness=-0.06",
                                "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        get = lambda t: Image.frombytes("RGB", (W, H), src.stdout.read(W * H * 3))
    else:
        sc = Scene(); get = sc.frame
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-i", a.audio, "-map", "0:v", "-map", "1:a", "-t", str(DUR),
                            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", a.out], stdin=subprocess.PIPE)
    for i in range(n):
        t = i / FPS
        enc.stdin.write(lyr.overlay(get(t), t).tobytes())
    enc.stdin.close(); enc.wait()


if __name__ == "__main__":
    main()
