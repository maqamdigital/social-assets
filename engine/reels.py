import sys, os, math
from mq import *

BEAT = 0.5
def hdr(img, col): logo(img, col, x=80, y=150, width=250)
def fgfor(bg): return LIME if bg == INK else INK

# =============== R1 homepage kinetic ===============
R1 = [(2, LIME, "text", {"t": "Your homepage"}), (2, INK, "text", {"t": "has seconds, not minutes."}),
      (2, PINK, "q", {"n": "01", "t": "What do you do?"}), (2, INK, "q", {"n": "02", "t": "Who is it for?"}),
      (2, LIME, "q", {"n": "03", "t": "What do I do next?"}), (2, INK, "text", {"t": "Miss one, lose them."})]
def kin_frame(cards, t, end_bg, end_fg, head):
    tt = 0
    for beats, bg, kind, data in cards:
        if t < tt + beats*BEAT: return kin_card(t - tt, bg, kind, data)
        tt += beats*BEAT
    return audit_card(t - tt, end_bg, end_fg, head)
def kin_card(lt, bg, kind, data):
    fg = fgfor(bg); img = Image.new("RGBA", (W, H), bg + (255,)); hdr(img, fg)
    if kind == "text":
        f, lines = fit(data["t"], "Bold", 900, 3, data.get("big", 160)); centered(img, lines, f, fg, 880, scale=pop(lt))
    elif kind == "q":
        centered(img, [data["n"]], P("Bold", 120), fg, 580, alpha=0.5, scale=pop(lt))
        f, lines = fit(data["t"], "Bold", 900, 3, 150); centered(img, lines, f, fg, 900, scale=pop(lt))
    elif kind == "word":
        centered(img, [data["top"]], P("Medium", 64), fg, 700, alpha=0.75)
        f, lines = fit(data["t"], "Bold", 860, 2, 150); centered(img, lines, f, fg, 900, scale=pop(lt, 0.14))
    elif kind == "swap":
        old_bg = (205,200,200) if bg != INK else (70,70,70); old_fg = (80,80,80) if bg != INK else (200,200,200)
        pill(img, W/2, 700, data["old"], P("Bold", 84), old_bg, old_fg, p=lt/0.15, strike=(lt - BEAT)/0.2 if lt > BEAT else 0)
        if lt > 2*BEAT:
            d = ImageDraw.Draw(img); d.polygon([(W/2-26, 880), (W/2+26, 880), (W/2, 920)], fill=fg)
            nbg = LIME if bg == INK else INK
            pill(img, W/2, 1060, data["new"], P("Bold", 84), nbg, LIME if nbg == INK else INK, p=(lt - 2*BEAT)/0.18)
    return img
def kin_events(cards, extra=()):
    ev, tt = [], 0
    for beats, bg, kind, data in cards:
        if tt > 0: ev.append((tt, "whoosh"))
        if kind == "swap": ev += [(tt + BEAT, "pop"), (tt + 2*BEAT, "pop")]
        tt += beats*BEAT
    return ev + [(tt, "whoosh"), (tt + 0.35, "pop")] + list(extra), tt

# =============== R2 buttons ===============
R2 = [(2, PINK, "text", {"t": "Your buttons"}), (2, INK, "text", {"t": "are costing you enquiries.", "big": 124}),
      (4, INK, "swap", {"old": "Submit", "new": "Send my enquiry"}), (4, PINK, "swap", {"old": "Click here", "new": "Book a call"}),
      (4, LIME, "swap", {"old": "Learn more", "new": "See prices"})]

# =============== R4 services beat ===============
R4 = [(2, INK, "text", {"t": "We build websites that bring enquiries.", "big": 120})] + \
     [(1, bg, "word", {"top": "we do", "t": w}) for bg, w in zip([LIME, INK, PINK, LIME, INK, PINK],
       ["WordPress", "WooCommerce", "Shopify", "Local SEO", "Speed fixes", "Care plans"])] + \
     [(3, INK, "text", {"t": "for businesses in the UK, Europe, US, Australia and NZ.", "big": 96})]

# =============== R3 looping question ===============
R3_T, R3_DUR = 5.0, 10.0
R3_A, R3_B = "Website not bringing enquiries?", "Let's fix that."
PIV = (540, -560); LEN = 1500; AMP = 0.50
def r3(t):
    tau = t + 1.0
    ang = AMP*math.sin(2*math.pi*tau/R3_T)
    bx, by = PIV[0] + LEN*math.sin(ang), PIV[1] + LEN*math.cos(ang)
    tau = t + R3_T/4
    ang = AMP*math.sin(2*math.pi*tau/R3_T)
    bx, by = PIV[0] + LEN*math.sin(ang), PIV[1] + LEN*math.cos(ang)
    ph = (tau - R3_T/4) % R3_T
    if ph < R3_T/2: new, old, new_side = R3_A, R3_B, "right"
    else: new, old, new_side = R3_B, R3_A, "left"
    def layer_for(text):
        L = Image.new("RGBA", (W, H), (0,0,0,0)); f, lines = fit(text, "Bold", 900, 3, 128)
        centered(L, lines, f, INK, 900); return L
    img = Image.new("RGBA", (W, H), LIME + (255,)); hdr(img, INK)
    A, B = layer_for(new), layer_for(old)
    m = Image.new("L", (W, H), 0); md = ImageDraw.Draw(m)
    bxc = min(max(bx, 0), W)
    if new_side == "right": md.rectangle([bxc, 0, W, H], fill=255)
    else: md.rectangle([0, 0, bxc, H], fill=255)
    comp = Image.composite(A, B, m); img.alpha_composite(comp)
    d = ImageDraw.Draw(img)
    d.line([PIV, (bx, by)], fill=INK, width=6)
    s = 170; tile = Image.new("RGBA", (s+40, s+40), (0,0,0,0)); td = ImageDraw.Draw(tile)
    td.rounded_rectangle([20, 20, 20+s, 20+s], radius=34, fill=INK)
    mf = P("Bold", 120); td.text((20 + (s - td.textlength("M", font=mf))/2, 20 + 4), "M", font=mf, fill=LIME)
    tile = tile.rotate(-math.degrees(ang), resample=Image.BICUBIC, expand=False)
    img.alpha_composite(tile, (int(bx - (s+40)/2), int(by - 10)))
    centered(img, ["Free website audit:"], P("Medium", 44), INK, 1500)
    pill(img, W/2, 1610, "Comment AUDIT", P("Bold", 56), INK, LIME)
    return img
def r3_ev(): return [(R3_T/4 + k*R3_T/2, "whoosh") for k in range(4)]

# =============== R5 notes checklist: what's in the audit ===============
R5_ITEMS = ["Mobile speed, tested with Google PageSpeed Insights", "How your site looks and works on a phone",
            "Can Google tell what you do and where?", "Your Google Business Profile basics",
            "Every form, button and call link, tested", "Trust: reviews, contact details, SSL",
            "Then your top 3 fixes, in plain English"]
R5_T0, R5_ST, R5_END, R5_DUR = 1.2, 1.25, 11.0, 15.0
def r5(t):
    if t >= R5_END: return audit_card(t - R5_END, INK, LIME, "Want yours?")
    img = Image.new("RGBA", (W, H), (251,250,246,255)); d = ImageDraw.Draw(img); amber = (224,168,0)
    d.text((70, 120), "‹ Notes", font=I("Regular", 40), fill=amber); d.text((W-200, 120), "Done", font=I("SemiBold", 40), fill=amber)
    logo(img, INK, x=W/2 - 100, y=118, width=200, alpha=0.9)
    y = left(img, (90, 300), "free website audit: what we check", I("Bold", 62), INK, 900, 1.15)
    d.text((90, y + 6), "for WordPress, WooCommerce and Shopify sites", font=I("Regular", 32), fill=(150,150,150)); y += 90
    f = I("Regular", 50)
    for k, txt in enumerate(R5_ITEMS):
        s = R5_T0 + k*R5_ST
        if t < s: break
        n = int(len(txt)*clamp((t - s)/0.7)); cx, cy = 118, y + 28; done = t >= s + 0.95
        if done:
            p = ease((t - s - 0.95)/0.2); r = 24 + 4*math.sin(p*math.pi)
            d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(200,230,90), outline=INK, width=3); tick(d, cx, cy, 24, INK, 5)
        else: d.ellipse([cx-24, cy-24, cx+24, cy+24], outline=(170,170,170), width=3)
        shown = txt[:n]; yy = y; cnt = 0
        for ln in wrap(d, txt, f, 820):
            seg = shown[cnt:cnt + len(ln)]; cnt += len(ln) + 1
            d.text((170, yy), seg, font=f, fill=INK if (not done or k == len(R5_ITEMS) - 1) else (110,110,110)); yy += 64
        y = yy + 34
    return img
def r5_ev():
    ev = []
    for k, txt in enumerate(R5_ITEMS):
        s = R5_T0 + k*R5_ST; ev += [(s + 0.7*c/len(txt), "type") for c in range(0, len(txt), 2)] + [(s + 0.95, "pop")]
    return ev + [(R5_END, "whoosh"), (R5_END + 0.35, "pop")]

# =============== R6 local SEO teardown ===============
PX0, PY0, PW, PH = 230, 640, 620, 860
def plumb_bad(s):
    d = ImageDraw.Draw(s); d.rectangle([0, 0, PW, 110], fill=(30,70,140))
    d.rounded_rectangle([30, 38, 290, 74], radius=8, fill=(200,210,230))
    for k in range(3): d.rectangle([PW-80, 38+k*14, PW-36, 44+k*14], fill=WHITE)
    d.rectangle([0, 110, PW, 420], fill=(200,210,225))
    d.text((40, 180), "Welcome to our", font=P("Bold", 44), fill=(30,40,60)); d.text((40, 236), "website", font=P("Bold", 44), fill=(30,40,60))
    d.text((40, 310), "We offer quality services at", font=P("Regular", 26), fill=(60,70,90)); d.text((40, 344), "competitive prices.", font=P("Regular", 26), fill=(60,70,90))
    d.text((40, 460), "About us", font=P("Bold", 34), fill=(30,40,60))
    for k in range(6): d.rounded_rectangle([40, 520+k*34, PW-40-(k%3)*60, 538+k*34], radius=8, fill=(225,225,230))
    d.rectangle([0, PH-130, PW, PH], fill=(235,235,240)); d.text((40, PH-95), "contact us", font=P("Regular", 22), fill=(140,140,150))
def plumb_good(s):
    d = ImageDraw.Draw(s); d.rectangle([0, 0, PW, 110], fill=INK); d.text((30, 34), "Example Plumbing", font=P("Bold", 30), fill=WHITE)
    d.rounded_rectangle([PW-170, 28, PW-24, 82], radius=27, fill=LIME); d.text((PW-146, 38), "Call now", font=P("Bold", 24), fill=INK)
    d.rectangle([0, 110, PW, 470], fill=(245,250,230))
    d.text((40, 150), "Emergency plumber", font=P("Bold", 44), fill=INK); d.text((40, 206), "in Leeds", font=P("Bold", 44), fill=INK)
    d.text((40, 278), "Boilers, leaks and blocked drains.", font=P("Regular", 26), fill=(60,60,60))
    d.rounded_rectangle([40, 370, 360, 440], radius=35, fill=INK); d.text((76, 386), "Tap to call", font=P("Bold", 28), fill=LIME)
    stars(d, 60, 520, 16, (240,170,0)); d.text((250, 504), "Google reviews", font=P("Medium", 26), fill=INK)
    d.rounded_rectangle([40, 580, PW-40, 760], radius=20, fill=(238,238,238)); d.text((70, 610), "Areas we cover", font=P("Bold", 30), fill=INK)
    d.text((70, 660), "Headingley · Roundhay · Horsforth", font=P("Regular", 24), fill=(70,70,70)); d.text((70, 700), "Morley · Chapel Allerton", font=P("Regular", 24), fill=(70,70,70))
R6_CALLS = [(2.4, "1. The heading says \"Welcome\".", "Say what you do and where: \"Emergency plumber in Leeds\".", (24,160,PW-24,300)),
            (5.4, "2. No way to call in one tap.", "Put a tap-to-call button where thumbs reach.", (PW-200,14,PW-10,100)),
            (8.4, "3. No areas, no reviews.", "List the areas you cover and show genuine reviews.", (24,440,PW-24,760))]
R6_FIX, R6_END, R6_DUR = 11.4, 13.6, 17.6
def callout(img, box, q):
    x0, y0, x1, y1 = box; cx, cy = PX0 + (x0+x1)/2, PY0 + (y0+y1)/2
    hw, hh = (x1-x0)/2*(0.6+0.4*q) + 18, (y1-y0)/2*(0.6+0.4*q) + 18
    L = Image.new("RGBA", img.size, (0,0,0,0)); ImageDraw.Draw(L).rounded_rectangle([cx-hw, cy-hh, cx+hw, cy+hh], radius=30, outline=RED + (int(255*q),), width=9)
    img.alpha_composite(L)
def r6(t):
    if t >= R6_END: return audit_card(t - R6_END, LIME, INK, "Is your site invisible locally?")
    img = Image.new("RGBA", (W, H), INK + (255,)); hdr(img, LIME)
    fixed = t >= R6_FIX; phone(img, plumb_good if fixed else plumb_bad, PX0, PY0, PW, PH)
    chip(img, PX0 + PW - 262, PY0 - 78, "Illustrative example", (60,60,60), (220,220,220))
    if t < R6_CALLS[0][0]:
        p = ease(t/0.4); left(img, (90, 300), "3 reasons this plumber's website is invisible locally.", P("Bold", 60), WHITE, 900, 1.15, p, (1-p)*40)
    elif not fixed:
        k = max(i for i, c in enumerate(R6_CALLS) if t >= c[0]); s, title, sub, box = R6_CALLS[k]; lt = t - s
        p = ease(lt/0.35); y = left(img, (90, 300), title, P("Bold", 54), LIME, 900, 1.15, p, (1-p)*30)
        left(img, (90, y + 10), sub, P("Regular", 38), WHITE, 900, alpha=ease((lt - 0.35)/0.35))
        callout(img, box, ease((lt - 0.15)/0.3))
    else:
        lt = t - R6_FIX; p = ease(lt/0.35)
        left(img, (90, 300), "Same business. Now Google and customers get it.", P("Bold", 54), LIME, 900, 1.15, p, (1-p)*30)
        flash(img, lt)
    return img
def r6_ev(): return [(c[0], "whoosh") for c in R6_CALLS] + [(c[0] + 0.15, "pop") for c in R6_CALLS] + [(R6_FIX, "riser"), (R6_FIX + 0.02, "hit"), (R6_END, "whoosh"), (R6_END + 0.35, "pop")]

# =============== R7 developer stopped replying ===============
R7_MSGS = [(0.5, "Monday", "Hi, the contact form on the website isn't working.", "09:12"), (1.5, "Wednesday", "Any update?", "14:40"), (2.5, "Friday", "Hello?", "10:05")]
R7_ITEMS = ["Who is your domain registered to? A WHOIS lookup shows the registrar.", "Can you log in to your hosting account?",
            "Do you have your own admin login?", "Where is the latest backup?", "Don't click 'update all' on a site you don't know."]
R7_CARD, R7_STEP, R7_END, R7_DUR = 4.2, 1.7, 13.4, 17.4
def r7(t):
    if t >= R7_END: return audit_card(t - R7_END, PINK, INK, "Not sure what state your site is in?")
    img = Image.new("RGBA", (W, H), GREYBG + (255,)); d = ImageDraw.Draw(img)
    d.rectangle([0, 230, W, 380], fill=WHITE); d.ellipse([60, 260, 150, 350], fill=(190,190,190))
    d.text((180, 260), "Web developer", font=I("SemiBold", 42), fill=INK); d.text((180, 314), "last seen 3 weeks ago", font=I("Regular", 30), fill=(140,140,140))
    hdr(img, INK)
    y = 700
    for s, day, msg, tm in R7_MSGS:
        if t < s: break
        p = ease((t - s)/0.3)
        dl = d.textlength(day, font=I("Medium", 28)); d.rounded_rectangle([W/2-dl/2-24, y-70, W/2+dl/2+24, y-24], radius=20, fill=(220,216,208))
        d.text((W/2 - dl/2, y - 64), day, font=I("Medium", 28), fill=(90,90,90))
        lines = wrap(d, msg, I("Regular", 40), 620); bw = max(d.textlength(l, font=I("Regular", 40)) for l in lines) + 60; bh = len(lines)*52 + 80
        x1 = W - 70; x0 = x1 - bw; L = Image.new("RGBA", img.size, (0,0,0,0)); ld = ImageDraw.Draw(L); yy = y + (1-p)*30
        ld.rounded_rectangle([x0, yy, x1, yy + bh], radius=28, fill=(220,248,198,int(255*p)))
        for k, l in enumerate(lines): ld.text((x0 + 30, yy + 20 + k*52), l, font=I("Regular", 40), fill=INK + (int(255*p),))
        ld.text((x1 - 170, yy + bh - 46), tm, font=I("Regular", 26), fill=(120,120,120,int(255*p)))
        img.alpha_composite(L); y += bh + 120
    if t < R7_CARD:
        p = ease(t/0.35); L = Image.new("RGBA", img.size, (0,0,0,0)); ImageDraw.Draw(L).rounded_rectangle([60, 410, W-60, 590], radius=30, fill=INK + (int(235*p),)); img.alpha_composite(L)
        left(img, (100, 440), "Your web developer stopped replying.", P("Bold", 52), LIME, 860, 1.12, p)
    else:
        lt = t - R7_CARD; p = ease(lt/0.4)
        img.alpha_composite(Image.new("RGBA", img.size, (0,0,0,int(140*p))))
        L = Image.new("RGBA", img.size, (0,0,0,0)); top = 380 + (1-p)*200
        ImageDraw.Draw(L).rounded_rectangle([60, top, W-60, top + 1080], radius=36, fill=WHITE + (int(255*p),)); img.alpha_composite(L)
        left(img, (110, top + 50), "Check these before you panic:", P("Bold", 52), INK, 860, alpha=p)
        y = top + 180; d = ImageDraw.Draw(img)
        for k, it in enumerate(R7_ITEMS):
            q = ease((lt - 0.6 - k*R7_STEP)/0.3)
            if q <= 0: break
            d.ellipse([110, y + 4, 160, y + 54], fill=(200,230,90)); tick(d, 135, y + 29, 22, INK, 5)
            y = left(img, (190, y), it, P("Regular", 40), INK, 760, 1.25, q) + 34
    return img
def r7_ev(): return [(s, "msg") for s, *_ in R7_MSGS] + [(R7_CARD, "whoosh")] + [(R7_CARD + 0.6 + k*R7_STEP, "pop") for k in range(5)] + [(R7_END, "whoosh"), (R7_END + 0.35, "pop")]

# =============== R8 redesign before/after ===============
SERIF = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 34)
def SF(s): return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", s)
def site_old(s):
    d = ImageDraw.Draw(s); s.paste((240,236,222), [0, 0, PW, PH]); d.text((24, 26), "Example Kitchens", font=SF(34), fill=(120,40,40))
    for k, w in enumerate(["Home","About","Gallery","Services","News","Links","FAQ","Contact"]): d.text((24 + (k%4)*146, 84 + (k//4)*30), w, font=SF(20), fill=(40,40,160))
    d.rectangle([20, 160, PW-20, 420], fill=(150,150,150)); d.text((PW/2 - 110, 250), "Welcome!!", font=SF(48), fill=(255,255,0))
    for k in range(10): d.rectangle([24, 450 + k*26, PW-24-(k%4)*40, 462 + k*26], fill=(170,165,150))
    d.text((24, 730), "click here to contact us", font=SF(20), fill=(40,40,160))
def site_new(s):
    d = ImageDraw.Draw(s); s.paste(WHITE, [0, 0, PW, PH]); d.text((30, 34), "Example Kitchens", font=P("Bold", 32), fill=INK)
    d.rounded_rectangle([20, 110, PW-20, 500], radius=28, fill=INK)
    d.text((50, 150), "Kitchen fitters", font=P("Bold", 46), fill=LIME); d.text((50, 206), "in Bristol", font=P("Bold", 46), fill=LIME)
    d.text((50, 278), "Design, supply and fitting.", font=P("Regular", 26), fill=WHITE)
    d.rounded_rectangle([50, 340, 360, 410], radius=35, fill=LIME); d.text((80, 356), "Get a quote", font=P("Bold", 26), fill=INK)
    stars(d, 66, 455, 13, (240,190,40)); d.text((222, 440), "Google reviews", font=P("Medium", 22), fill=WHITE)
    for k, lab in enumerate(["Kitchens", "Worktops", "Refits"]):
        x = 20 + k*((PW-40)/3); d.rounded_rectangle([x+6, 530, x + (PW-40)/3 - 6, 700], radius=20, fill=PINK); d.text((x + 22, 650), lab, font=P("Bold", 24), fill=INK)
R8_WIPE, R8_LIST, R8_END, R8_DUR = 3.4, 6.0, 10.2, 14.2
R8_ITEMS = ["One clear offer at the top", "Built for phones first", "A shorter enquiry form", "Reviews next to the button"]
def r8(t):
    if t >= R8_END: return audit_card(t - R8_END, LIME, INK, "Is your website showing its age?")
    if t < R8_LIST:
        img = Image.new("RGBA", (W, H), PINK + (255,)); hdr(img, INK); d = ImageDraw.Draw(img)
        p = ease(t/0.45); left(img, (90, 290), "Your website was built years ago.", P("Bold", 54), INK, 940, 1.15, p, (1-p)*30)
        q = ease((t - 0.7)/0.4); left(img, (90, 370), "Your customers can tell.", P("Bold", 54), INK, 940, 1.15, q, (1-q)*30)
        if t > 1.2:
            q = ease((t - 1.2)/0.5); yo = (1-q)*220
            d.rounded_rectangle([PX0-16, PY0-16+yo, PX0+PW+16, PY0+PH+16+yo], radius=70, fill=(40,40,40))
            old = Image.new("RGBA", (PW, PH)); site_old(old); new = Image.new("RGBA", (PW, PH)); site_new(new)
            wx = int(PW*ease((t - R8_WIPE)/0.9)) if t > R8_WIPE else 0; scr = old.copy()
            if wx > 0: scr.paste(new.crop((0, 0, wx, PH)), (0, 0))
            mask = Image.new("L", (PW, PH), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, PW, PH], radius=56, fill=255)
            img.paste(scr, (PX0, int(PY0 + yo)), mask)
            if 0 < wx < PW: d.rectangle([PX0 + wx - 4, PY0, PX0 + wx + 4, PY0 + PH], fill=LIME)
            lab, col = ("Before", RED) if t < R8_WIPE + 0.5 else ("After", INK)
            d.rounded_rectangle([PX0, PY0 - 90 + yo, PX0 + 190, PY0 - 30 + yo], radius=30, fill=col)
            d.text((PX0 + 30, PY0 - 82 + yo), lab, font=P("Bold", 32), fill=WHITE if col == RED else LIME)
            chip(img, PX0 + PW - 262, int(PY0 - 88 + yo), "Illustrative example", (200,170,170), INK)
        return img
    img = Image.new("RGBA", (W, H), INK + (255,)); hdr(img, LIME); lt = t - R8_LIST
    left(img, (90, 420), "What actually changed:", P("Bold", 66), WHITE, 900, alpha=ease(lt/0.35)); y = 600
    for k, it in enumerate(R8_ITEMS):
        p = ease((lt - 0.5 - k*0.8)/0.35)
        if p <= 0: break
        L = Image.new("RGBA", img.size, (0,0,0,0)); ld = ImageDraw.Draw(L)
        ld.ellipse([90, y + 6, 146, y + 62], fill=LIME + (int(255*p),)); ld.text((107, y + 6), str(k+1), font=P("Bold", 36), fill=INK + (int(255*p),)); img.alpha_composite(L)
        left(img, (180 + (1-p)*40, y), it, P("Medium", 50), WHITE, 800, alpha=p); y += 170
    return img
def r8_ev(): return [(1.2, "whoosh"), (R8_WIPE, "riser"), (R8_WIPE + 0.02, "hit"), (R8_LIST, "whoosh")] + [(R8_LIST + 0.5 + k*0.8, "pop") for k in range(4)] + [(R8_END, "whoosh"), (R8_END + 0.35, "pop")]

# =============== jobs ===============
def kin_job(cards, bg, fg, head, key):
    ev, tt = kin_events(cards); dur = tt + 4.0
    return (lambda t: kin_frame(cards, t, bg, fg, head)), dur, ev, ("beat", 120, key)
JOBS = {
 "01": ("maqam-01-homepage-questions",) + kin_job(R1, LIME, INK, "Free homepage audit", "major"),
 "02": ("maqam-02-button-words",) + kin_job(R2, INK, LIME, "Free website audit", "minor"),
 "03": ("maqam-03-loop-not-bringing-enquiries", r3, R3_DUR, r3_ev(), ("beat", 120, "minor")),
 "04": ("maqam-04-what-we-do",) + kin_job(R4, PINK, INK, "Free website audit", "major"),
 "05": ("maqam-05-whats-in-the-free-audit", r5, R5_DUR, r5_ev(), ("lofi", 84, "major")),
 "06": ("maqam-06-local-seo-teardown", r6, R6_DUR, r6_ev(), ("beat", 120, "minor")),
 "07": ("maqam-07-developer-stopped-replying", r7, R7_DUR, r7_ev(), ("lofi", 84, "major")),
 "08": ("maqam-08-redesign-before-after", r8, R8_DUR, r8_ev(), ("beat", 120, "major")),
}
if __name__ == "__main__":
    k = sys.argv[1]
    name, fn, dur, ev, (mood, bpm, key) = JOBS[k]
    if len(sys.argv) > 2 and sys.argv[2] == "sheet":
        n = 8; ts = [dur*(i + 0.6)/n for i in range(n)]
        fr = [fn(t).convert("RGB").resize((216, 384)) for t in ts]
        s = Image.new("RGB", (226*n - 10, 384), (128,128,128))
        for i, f in enumerate(fr): s.paste(f, (i*226, 0))
        s.save(os.path.join(HERE, f"sheet_{k}.png")); print("sheet", k, round(dur, 1))
    else:
        wav = os.path.join(HERE, f"a{k}.wav"); synth(wav, dur, bpm, mood, ev, key)
        print("done", encode(name, fn, dur, wav), round(dur, 1))
