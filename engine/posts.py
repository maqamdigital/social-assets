"""Carousels and static posts (1080x1350) with the Maqam logo, plus the checklist PDF."""
import os
from PIL import Image, ImageDraw
from mq import P, LIME, PINK, INK, WHITE, logo_img, wrap, _D

OUT = "/home/claude/out"; HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1350
GREEN_NUM = (190, 205, 140)

def base(bg, fg, idx=None, total=None):
    img = Image.new("RGBA", (W, H), bg + (255,)); img.alpha_composite(logo_img(fg, 200), (90, 72))
    d = ImageDraw.Draw(img)
    if idx: d.text((W - 90 - d.textlength(f"{idx}/{total}", font=P("Medium", 30)), 90), f"{idx}/{total}", font=P("Medium", 30), fill=fg)
    return img, d
def para(d, xy, text, f, col, maxw, lh=1.3):
    x, y = xy
    for ln in wrap(d, text, f, maxw): d.text((x, y), ln, font=f, fill=col); y += f.size*lh
    return y
def pill(d, x, y, text, f, bg, fg):
    tw = d.textlength(text, font=f); h = f.size + 50
    d.rounded_rectangle([x, y, x + tw + 90, y + h], radius=h//2, fill=bg); d.text((x + 45, y + 18), text, font=f, fill=fg)
    return y + h
def save(slides, prefix):
    paths = []
    for i, s in enumerate(slides):
        p = os.path.join(OUT, f"{prefix}-{i+1:02d}.jpg"); s.convert("RGB").save(p, quality=92); paths.append(p)
    n = len(slides); cols = min(n, 4); rows = (n + cols - 1)//cols
    sh = Image.new("RGB", (cols*280 - 10, rows*347 - 10), (128,128,128))
    for i, s in enumerate(slides): sh.paste(s.convert("RGB").resize((270, 337)), ((i % cols)*280, (i//cols)*347))
    sh.save(os.path.join(HERE, f"sheet_{prefix}.png"))
    return paths
THEMES = [(WHITE, INK), (INK, WHITE), (PINK, INK)]
def num_col(bg): return LIME if bg == INK else (GREEN_NUM if bg == WHITE else INK)

def audit_cta(d, y, bg, fg):
    acc_bg, acc_fg = (LIME, INK) if bg == INK else (INK, LIME)
    d.text((90, y), "Free website audit:", font=P("Bold", 54), fill=fg)
    y = pill(d, 90, y + 90, "Comment AUDIT", P("Bold", 60), acc_bg, acc_fg)
    y = para(d, (90, y + 30), "or DM us your website link.", P("Medium", 42), fg, 900)
    return y

# ---------- carousel 1: monthly WordPress check ----------
WP = [
    ("Take a backup, and test it restores.", "A backup you've never restored is a guess.", "Restore it to a staging copy, or use your host's restore option."),
    ("Update one thing at a time.", "If something breaks, you know what caused it.", "WordPress core, then theme, then plugins. Check the site after each."),
    ("Send yourself a test enquiry.", "Forms break quietly, and missed enquiries cost the most.", "Fill in every form on the site and check the email arrives."),
    ("Check mobile speed.", "Google treats a Largest Contentful Paint of 2.5s or less as good.", "Run your homepage through PageSpeed Insights, mobile tab."),
    ("Update hours and contact details.", "Wrong hours send customers to a closed door.", "Make sure your website and Google Business Profile match."),
    ("Check domain and SSL renewal dates.", "An expired domain or certificate takes the whole site offline.", "Put both renewal dates in your calendar."),
]
def checklist_carousel(cover_title, cover_sub, items, cta_title, keyword, keyword_sub, prefix, why_how=True):
    total = len(items) + 2; slides = []
    img, d = base(LIME, INK, 1, total)
    y = para(d, (90, 330), cover_title, P("Bold", 104), INK, 900, 1.08)
    y = para(d, (90, y + 40), cover_sub, P("Regular", 44), INK, 860)
    pill(d, 90, y + 60, "Save this", P("Bold", 40), INK, LIME)
    d.text((90, H - 140), "Swipe for the list", font=P("Medium", 36), fill=INK); slides.append(img)
    for i, it in enumerate(items):
        bg, fg = THEMES[i % 3]; img, d = base(bg, fg, i + 2, total)
        d.text((84, 190), f"{i+1:02d}", font=P("Bold", 200), fill=num_col(bg))
        if why_how:
            title, why, how = it
            y = para(d, (90, 470), title, P("Bold", 78), fg, 900, 1.12) + 50
            d.text((90, y), "WHY", font=P("Bold", 30), fill=fg); y = para(d, (90, y + 46), why, P("Regular", 44), fg, 880) + 40
            d.text((90, y), "HOW", font=P("Bold", 30), fill=fg); para(d, (90, y + 46), how, P("Regular", 44), fg, 880)
        else:
            title, points = it
            y = para(d, (90, 470), title, P("Bold", 78), fg, 900, 1.12) + 40
            for pt in points:
                d.ellipse([92, y + 18, 108, y + 34], fill=fg); y = para(d, (130, y), pt, P("Regular", 42), fg, 860) + 22
        slides.append(img)
    img, d = base(INK, LIME, total, total)
    y = para(d, (90, 300), cta_title, P("Bold", 84), WHITE, 900, 1.1)
    if keyword:
        d.text((90, y + 40), "Comment", font=P("Bold", 56), fill=LIME)
        y = pill(d, 90, y + 130, keyword, P("Bold", 76), LIME, INK)
        y = para(d, (90, y + 30), keyword_sub, P("Regular", 42), WHITE, 880) + 60
        d.line([(90, y), (W - 90, y)], fill=(70,70,70), width=2); y += 50
        d.text((90, y), "Want a free website audit?", font=P("Bold", 46), fill=WHITE)
        para(d, (90, y + 70), "DM us your website link.", P("Regular", 42), LIME, 880)
    else:
        audit_cta(d, y + 60, INK, WHITE)
    d.text((90, H - 130), "@maqamdigital", font=P("Bold", 40), fill=LIME); slides.append(img)
    return save(slides, prefix)

c1 = checklist_carousel("The monthly WordPress check", "Six checks that stop most website emergencies before they start.", WP,
                        "Want it as a printable checklist?", "CHECKLIST", "and we'll send you the PDF.", "maqam-C1-wordpress-check")

# ---------- carousel 2: local SEO checklist ----------
SEO = [
    ("Google Business Profile", ["The most accurate primary category", "Every service you offer listed", "Real photos of your work and team", "Hours kept current, holidays included"]),
    ("Your website", ["One page per service", "Page titles with the service and the town", "Name, address and phone in the footer", "Tap-to-call on mobile"]),
    ("Reviews", ["Ask after every finished job", "Send a direct review link", "Reply to every review, good or bad"]),
    ("Consistency", ["Same business name, address and phone everywhere", "Check directories, social profiles and maps", "Fix old addresses and numbers"]),
    ("Area pages", ["Only for areas you actually serve", "Real local detail: jobs, landmarks, travel times", "Never the same page with the town swapped"]),
    ("Speed and mobile", ["Test with PageSpeed Insights, mobile tab", "Compress large images", "Keep the call button visible on phones"]),
]
c2 = checklist_carousel("The local SEO checklist", "For trades, clinics and service businesses that want to show up nearby.", SEO,
                        "Want us to check yours?", None, None, "maqam-C2-local-seo-checklist", why_how=False)

# ---------- static post: free audit offer (pin this) ----------
img, d = base(LIME, INK)
y = para(d, (90, 250), "Free website audit", P("Bold", 120), INK, 900, 1.02)
y = para(d, (90, y + 20), "For WordPress, WooCommerce and Shopify sites.", P("Regular", 42), INK, 900) + 40
for pt in ["Mobile speed", "How it works on a phone", "Google visibility", "Forms, buttons and call links", "Trust: reviews, contact details, SSL"]:
    d.ellipse([92, y + 16, 110, y + 34], fill=INK); y = para(d, (134, y), pt, P("Medium", 44), INK, 860) + 12
y += 40
d.rounded_rectangle([60, y, W - 60, y + 330], radius=36, fill=INK)
d.text((100, y + 40), "How to get it", font=P("Bold", 44), fill=LIME)
yy = para(d, (100, y + 110), "Comment AUDIT or DM us your link, plus your business type, city and main goal.", P("Regular", 40), WHITE, 860)
para(d, (100, yy + 16), "We send back your top 3 fixes.", P("Bold", 40), LIME, 860)
c3 = save([img], "maqam-P1-free-audit-offer")

# ---------- PDF ----------
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
GF = "/usr/share/fonts/truetype/google-fonts/"
for w in ("Bold", "Regular", "Medium"): pdfmetrics.registerFont(TTFont("Pop-" + w, GF + f"Poppins-{w}.ttf"))
pw, ph = A4; c = canvas.Canvas(os.path.join(OUT, "Maqam-Monthly-WordPress-Checklist.pdf"), pagesize=A4)
c.setTitle("Monthly WordPress Checklist - Maqam Digital"); c.setAuthor("Maqam Digital")
c.setFillColorRGB(239/255, 1, 185/255); c.rect(0, ph - 170, pw, 170, stroke=0, fill=1)
lg = logo_img(INK, 400); lp = os.path.join(HERE, "logo_ink.png"); lg.save(lp)
c.drawImage(ImageReader(lp), 40, ph - 58, width=90, height=90*lg.height/lg.width, mask="auto")
c.setFillColorRGB(17/255, 17/255, 17/255)
c.setFont("Pop-Bold", 26); c.drawString(40, ph - 100, "The monthly WordPress check")
c.setFont("Pop-Regular", 11); c.drawString(40, ph - 124, "Six checks that stop most website emergencies. Do them on the 1st of every month.")
months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
y = ph - 205
for i, (title, why, how) in enumerate(WP):
    c.setFillColorRGB(17/255, 17/255, 17/255)
    c.setFont("Pop-Bold", 12.5); c.drawString(40, y, f"{i+1}. {title}"); y -= 16
    c.setFont("Pop-Regular", 9.5); c.drawString(54, y, "Why: " + why); y -= 13; c.drawString(54, y, "How: " + how); y -= 18
    c.setFont("Pop-Medium", 6.5); c.setLineWidth(0.7)
    for m, mo in enumerate(months):
        x = 54 + m*40; c.rect(x, y - 2, 10, 10, stroke=1, fill=0); c.drawString(x + 13, y, mo)
    y -= 18
    c.setStrokeColorRGB(0.85, 0.85, 0.85); c.line(40, y + 4, pw - 40, y + 4); c.setStrokeColorRGB(17/255, 17/255, 17/255); y -= 14
c.setFillColorRGB(17/255, 17/255, 17/255); c.roundRect(40, 50, pw - 80, 92, 14, stroke=0, fill=1)
c.setFillColorRGB(239/255, 1, 185/255); c.setFont("Pop-Bold", 15); c.drawString(62, 112, "Rather have this done for you?")
c.setFillColorRGB(1, 1, 1); c.setFont("Pop-Regular", 10.5)
c.drawString(62, 92, "Free audit: send us your link. Website care from £95/month.")
c.drawString(62, 74, "maqamdigital.com  ·  obaid@maqamdigital.com  ·  WhatsApp +92 302 6559858")
c.save(); print("ok", len(c1), len(c2), len(c3))
