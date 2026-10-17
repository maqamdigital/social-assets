"""Maqam reel toolkit: logo, free-audit end card, text helpers, sound beds, encoder."""
import os, math, wave, shutil, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = "/home/claude/out"; os.makedirs(OUT, exist_ok=True)
LIME, PINK, INK, WHITE, RED = (239,255,185), (234,202,202), (17,17,17), (255,255,255), (232,72,72)
GREYBG = (236,233,228)
GF = "/usr/share/fonts/truetype/google-fonts/"; IF = "/usr/share/fonts/opentype/inter/"
_fc = {}
def P(w, s):
    k = ("P", w, s)
    if k not in _fc: _fc[k] = ImageFont.truetype(GF + f"Poppins-{w}.ttf", s)
    return _fc[k]
def I(w, s):
    k = ("I", w, s)
    if k not in _fc: _fc[k] = ImageFont.truetype(IF + f"Inter-{w}.otf", s)
    return _fc[k]

# ---------- logo ----------
_LOGO = Image.open(os.path.join(HERE, "brand", "logo-white.png")).convert("RGBA")
_LOGO = _LOGO.crop(_LOGO.getbbox())
_lc = {}
def logo_img(col, width):
    k = (col, width)
    if k not in _lc:
        h = int(_LOGO.height * width / _LOGO.width)
        a = _LOGO.resize((width, h), Image.LANCZOS).split()[3]
        im = Image.new("RGBA", (width, h), col + (0,)); im.putalpha(a); _lc[k] = im
    return _lc[k]
def logo(img, col, x=80, y=120, width=210, alpha=1.0):
    lg = logo_img(col, width)
    if alpha < 1:
        lg = lg.copy(); lg.putalpha(lg.split()[3].point(lambda v: int(v*alpha)))
    img.alpha_composite(lg, (int(x), int(y)))

# ---------- text ----------
def ease(t): t = max(0., min(1., t)); return 1 - (1 - t) ** 3
def clamp(t): return max(0., min(1., t))
def wrap(d, text, f, maxw):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: out.append(cur); cur = w
    if cur: out.append(cur)
    return out
_D = ImageDraw.Draw(Image.new("RGB", (1, 1)))
def fit(text, weight, maxw, maxlines, start, minsize=56):
    s = start
    while s > minsize:
        f = P(weight, s); lines = wrap(_D, text, f, maxw)
        if len(lines) <= maxlines and all(_D.textlength(l, font=f) <= maxw for l in lines): return f, lines
        s -= 4
    f = P(weight, minsize); return f, wrap(_D, text, f, maxw)
def centered(img, lines, f, col, cy, lh=1.08, alpha=1.0, scale=1.0, dy=0):
    layer = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(layer)
    total = len(lines) * f.size * lh; y = cy - total/2 + dy
    for ln in lines:
        tw = d.textlength(ln, font=f); d.text(((W - tw)/2, y), ln, font=f, fill=col + (int(255*clamp(alpha)),)); y += f.size*lh
    if scale != 1.0:
        sw, sh = int(W*scale), int(H*scale); layer = layer.resize((sw, sh), Image.BILINEAR)
        layer = layer.crop(((sw-W)//2, (sh-H)//2, (sw-W)//2 + W, (sh-H)//2 + H))
    img.alpha_composite(layer)
    return cy - total/2, cy + total/2
def left(img, xy, text, f, col, maxw, lh=1.25, alpha=1.0, dy=0):
    x, y = xy; y += dy
    layer = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(layer)
    for ln in wrap(d, text, f, maxw):
        d.text((x, y), ln, font=f, fill=col + (int(255*clamp(alpha)),)); y += f.size*lh
    if alpha > 0: img.alpha_composite(layer)
    return y - dy
def pop(lt, amt=0.10): return 1.0 + amt*(1 - ease(lt/0.14))
def pill(img, cx, cy, text, f, bg, fg, p=1.0, strike=0.0, pad=56):
    p = ease(p)
    if p <= 0: return
    tw = _D.textlength(text, font=f); w = tw + pad*2; h = f.size + 64; sc = 0.85 + 0.15*p
    layer = Image.new("RGBA", (W, H), (0,0,0,0)); ld = ImageDraw.Draw(layer)
    x0, y0 = cx - w*sc/2, cy - h*sc/2
    ld.rounded_rectangle([x0, y0, x0 + w*sc, y0 + h*sc], radius=int(h*sc/2), fill=bg + (int(255*p),))
    ft = P("Bold", max(10, int(f.size*sc)))
    ld.text((cx - ld.textlength(text, font=ft)/2, cy - ft.size*0.64), text, font=ft, fill=fg + (int(255*p),))
    if strike > 0: ld.line([(x0-20, cy), (x0-20 + (w*sc+40)*ease(strike), cy)], fill=RED, width=12)
    img.alpha_composite(layer)
def tick(d, cx, cy, r, col, w=6):
    d.line([(cx - r*0.45, cy), (cx - r*0.1, cy + r*0.38), (cx + r*0.5, cy - r*0.35)], fill=col, width=w, joint="curve")
def stars(d, x, y, r, col, n=5):
    for k in range(n):
        cx = x + k*r*2.3; pts = []
        for j in range(10):
            a = -math.pi/2 + j*math.pi/5; rr = r if j % 2 == 0 else r*0.45
            pts.append((cx + rr*math.cos(a), y + rr*math.sin(a)))
        d.polygon(pts, fill=col)

# ---------- standard free-audit end card ----------
AUDIT_SUB = "Speed, mobile, Google visibility and your enquiry flow. We send back your top 3 fixes."
def audit_card(lt, bg=LIME, fg=INK, head="Free website audit"):
    img = Image.new("RGBA", (W, H), bg + (255,))
    logo(img, fg, x=(W-300)/2, y=210, width=300, alpha=ease(lt/0.3))
    f, lines = fit(head, "Bold", 900, 2, 112)
    _, b = centered(img, lines, f, fg, 640, scale=pop(lt))
    centered(img, ["Comment"], P("Bold", 64), fg, b + 110, alpha=ease((lt-0.25)/0.3))
    pill(img, W/2, b + 250, "AUDIT", P("Bold", 120), fg, bg, p=(lt-0.35)/0.25)
    centered(img, ["or DM us your website link"], P("Medium", 50), fg, b + 420, alpha=ease((lt-0.6)/0.3))
    sf = P("Regular", 40); lines = wrap(_D, AUDIT_SUB, sf, 860)
    centered(img, lines, sf, fg, b + 590, lh=1.32, alpha=ease((lt-1.0)/0.4)*0.85)
    return img

def flash(img, lt, dur=0.22):
    if lt < dur: img.alpha_composite(Image.new("RGBA", img.size, (255,255,255,int(150*(1-lt/dur)))))

# ---------- phone frame ----------
def phone(img, site_fn, x0=230, y0=600, pw=620, ph=860, yoff=0):
    d = ImageDraw.Draw(img); y0 = y0 + yoff
    d.rounded_rectangle([x0-16, y0-16, x0+pw+16, y0+ph+16], radius=70, fill=(40,40,40))
    scr = Image.new("RGBA", (pw, ph), WHITE + (255,)); site_fn(scr)
    mask = Image.new("L", (pw, ph), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw, ph], radius=56, fill=255)
    img.paste(scr, (int(x0), int(y0)), mask)
def chip(img, x, y, text, bg, fg, f=None):
    f = f or P("Medium", 26); d = ImageDraw.Draw(img); w = d.textlength(text, font=f)
    d.rounded_rectangle([x, y, x + w + 40, y + f.size + 22], radius=30, fill=bg); d.text((x + 20, y + 9), text, font=f, fill=fg)

# ---------- audio ----------
def synth(path, dur, bpm=120, mood="beat", events=(), key="major"):
    sr = 44100; tt = np.arange(int(sr*dur))/sr; rng = np.random.default_rng(5); out = np.zeros_like(tt); beat = 60/bpm
    if mood == "beat":
        roots = [65.41, 49.0, 55.0, 43.65] if key == "major" else [55.0, 43.65, 49.0, 41.2]
        bar = beat*4
        for k in range(int(dur/bar) + 1):
            f0 = roots[k % 4]; s = k*bar
            for j in range(8):
                b = s + j*beat/2; i = (tt >= b) & (tt < b + beat/2*0.9); x = tt[i] - b
                out[i] += np.sign(np.sin(2*np.pi*f0*x))*np.exp(-x*7)*0.055 + np.sin(2*np.pi*f0*2*x)*np.exp(-x*5)*0.05
        for b in np.arange(0, dur, beat):
            i = (tt >= b) & (tt < b + 0.3); x = tt[i] - b
            out[i] += np.sin(2*np.pi*(48 + 90*np.exp(-x*30))*x)*np.exp(-x*11)*0.42
        for b in np.arange(beat, dur, beat*2):
            i = (tt >= b) & (tt < b + 0.2); x = tt[i] - b
            out[i] += rng.normal(0, 1, i.sum())*np.exp(-x*22)*0.15 + np.sin(2*np.pi*190*x)*np.exp(-x*30)*0.11
        for b in np.arange(beat/2, dur, beat/2):
            i = (tt >= b) & (tt < b + 0.05); x = tt[i] - b
            out[i] += rng.normal(0, 1, i.sum())*np.exp(-x*120)*0.045
    else:  # lofi
        chords = [[261.63,329.63,392.0,493.88],[220.0,261.63,329.63,392.0],[174.61,220.0,261.63,329.63],[196.0,246.94,293.66,349.23]]
        bar = beat*4
        for k in range(int(dur/bar) + 1):
            ch = chords[k % 4]; s = k*bar; e = s + bar; m = (tt >= s) & (tt < e); x = tt[m]
            env = np.clip((x-s)/0.25, 0, 1)*np.clip((e-x)/0.3, 0, 1)
            for f in ch: out[m] += env*(np.sin(2*np.pi*f*x) + 0.25*np.sin(4*np.pi*f*x))*0.045
        for b in np.arange(0, dur, beat):
            i = (tt >= b) & (tt < b + 0.3); x = tt[i] - b
            out[i] += np.sin(2*np.pi*(50 + 80*np.exp(-x*28))*x)*np.exp(-x*12)*0.24
        for b in np.arange(beat, dur, beat*2):
            i = (tt >= b) & (tt < b + 0.18); x = tt[i] - b
            out[i] += rng.normal(0, 1, i.sum())*np.exp(-x*25)*0.07
        cr = np.zeros_like(tt); idx = rng.integers(0, len(tt), int(dur*40)); cr[idx] = rng.normal(0, 0.08, len(idx)); out += cr
        out = np.convolve(out, np.ones(6)/6, mode="same")
    for t0, kind in events:
        if kind == "type":
            i = (tt >= t0) & (tt < t0 + 0.03); x = tt[i] - t0; out[i] += rng.normal(0, 1, i.sum())*np.exp(-x*220)*0.16
        elif kind == "pop":
            i = (tt >= t0) & (tt < t0 + 0.12); x = tt[i] - t0; out[i] += np.sin(2*np.pi*(950 - 500*x/0.12)*x)*np.exp(-x*35)*0.30
        elif kind == "msg":
            i = (tt >= t0) & (tt < t0 + 0.18); x = tt[i] - t0; out[i] += (np.sin(2*np.pi*1200*x) + 0.6*np.sin(2*np.pi*1800*x))*np.exp(-x*30)*0.18
        elif kind == "whoosh":
            i = (tt >= t0 - 0.28) & (tt < t0 + 0.05); x = (tt[i] - (t0 - 0.28))/0.33; out[i] += rng.normal(0, 1, i.sum())*np.sin(np.pi*x)**2*0.11
        elif kind == "riser":
            i = (tt >= t0 - 1.0) & (tt < t0); x = tt[i] - (t0 - 1.0)
            out[i] += np.sin(2*np.pi*(200 + 700*x**2)*x)*x**2*0.12 + rng.normal(0, 1, i.sum())*x**3*0.08
        elif kind == "hit":
            i = (tt >= t0) & (tt < t0 + 0.6); x = tt[i] - t0; out[i] += (np.sin(2*np.pi*45*x)*0.5 + rng.normal(0, 1, i.sum())*0.25)*np.exp(-x*7)
    out *= np.clip(tt/0.05, 0, 1)*np.clip((dur - tt)/0.6, 0, 1)
    out = np.tanh(out*1.4); out = out/np.max(np.abs(out))*0.89
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((out*32767).astype(np.int16).tobytes())

def encode(name, render, dur, wav):
    fr = os.path.join(HERE, "fr_" + name); shutil.rmtree(fr, ignore_errors=True); os.makedirs(fr)
    for i in range(int(round(dur*FPS))):
        render(i/FPS).convert("RGB").save(os.path.join(fr, f"f{i:04d}.png"), compress_level=1)
    mp4 = os.path.join(OUT, name + ".mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(fr, "f%04d.png"), "-i", wav,
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", mp4], check=True)
    shutil.rmtree(fr, ignore_errors=True)
    return mp4
