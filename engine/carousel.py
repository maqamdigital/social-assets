"""R003 checklist carousel (1080x1350) + printable CHECKLIST PDF."""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = "/home/claude/out"; os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1350
LIME, PINK, INK, WHITE, CREAM = (239,255,185), (234,202,202), (17,17,17), (255,255,255), (250,249,244)
GF = "/usr/share/fonts/truetype/google-fonts/"
def P(w, s): return ImageFont.truetype(GF + f"Poppins-{w}.ttf", s)

ITEMS = [
    ("Take a backup, and test it restores.", "A backup you've never restored is a guess.", "Restore it to a staging copy, or use your host's restore option."),
    ("Update one thing at a time.", "If something breaks, you know what caused it.", "WordPress core, then theme, then plugins. Check the site after each."),
    ("Send yourself a test enquiry.", "Forms break quietly, and missed enquiries cost the most.", "Fill in every form on the site and check the email arrives."),
    ("Check mobile speed.", "Google treats a Largest Contentful Paint of 2.5s or less as good.", "Run your homepage through PageSpeed Insights, mobile tab."),
    ("Update hours and contact details.", "Wrong hours send customers to a closed door.", "Make sure your website and Google Business Profile match."),
    ("Check domain and SSL renewal dates.", "An expired domain or certificate takes the whole site offline.", "Put both renewal dates in your calendar."),
]

def wrap(d, text, f, maxw):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: out.append(cur); cur = w
    if cur: out.append(cur)
    return out
def para(d, xy, text, f, col, maxw, lh=1.3):
    x, y = xy
    for ln in wrap(d, text, f, maxw): d.text((x, y), ln, font=f, fill=col); y += f.size * lh
    return y
def frame(bg, fg, idx, total):
    img = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(img)
    d.text((90, 80), "maqam digital", font=P("Medium", 30), fill=fg)
    d.text((W - 90 - d.textlength(f"{idx}/{total}", font=P("Medium", 30)), 80), f"{idx}/{total}", font=P("Medium", 30), fill=fg)
    return img, d
def pill(d, x, y, text, f, bg, fg):
    tw = d.textlength(text, font=f); h = f.size + 50
    d.rounded_rectangle([x, y, x + tw + 90, y + h], radius=h // 2, fill=bg); d.text((x + 45, y + 18), text, font=f, fill=fg)
    return y + h

TOTAL = len(ITEMS) + 2
slides = []
img, d = frame(LIME, INK, 1, TOTAL)
y = para(d, (90, 340), "The monthly WordPress check", P("Bold", 112), INK, 900, 1.08)
y = para(d, (90, y + 40), "Six checks that stop most website emergencies before they start.", P("Regular", 44), INK, 860)
pill(d, 90, y + 70, "Save this for the 1st", P("Bold", 40), INK, LIME)
d.text((90, H - 140), "Swipe for the list", font=P("Medium", 36), fill=INK)
slides.append(img)

themes = [(WHITE, INK, LIME), (INK, WHITE, LIME), (PINK, INK, INK), (WHITE, INK, LIME), (INK, WHITE, LIME), (PINK, INK, INK)]
for i, (title, why, how) in enumerate(ITEMS):
    bg, fg, acc = themes[i]
    img, d = frame(bg, fg, i + 2, TOTAL)
    num_col = acc if bg == INK else (INK if acc == INK else (150, 160, 110))
    d.text((84, 190), f"{i+1:02d}", font=P("Bold", 200), fill=num_col if bg != WHITE else (190, 205, 140))
    y = para(d, (90, 470), title, P("Bold", 78), fg, 900, 1.12)
    y += 50
    lab = P("Bold", 30)
    d.text((90, y), "WHY", font=lab, fill=fg); y = para(d, (90, y + 46), why, P("Regular", 44), fg, 880) + 40
    d.text((90, y), "HOW", font=lab, fill=fg); y = para(d, (90, y + 46), how, P("Regular", 44), fg, 880)
    slides.append(img)

img, d = frame(INK, LIME, TOTAL, TOTAL)
y = para(d, (90, 380), "Want it as a printable checklist?", P("Bold", 96), WHITE, 900, 1.1)
d.text((90, y + 60), "Comment", font=P("Bold", 64), fill=LIME)
y = pill(d, 90, y + 160, "CHECKLIST", P("Bold", 84), LIME, INK)
y = para(d, (90, y + 50), "and we'll send you the PDF.", P("Regular", 46), WHITE, 880)
d.text((90, H - 140), "@maqamdigital", font=P("Bold", 40), fill=LIME)
slides.append(img)

for i, s in enumerate(slides):
    s.save(os.path.join(OUT, f"maqam-R003-carousel-{i+1:02d}.jpg"), quality=92)
sheet = Image.new("RGB", (270 * 4 + 30, 337 * 2 + 10), (128, 128, 128))
for i, s in enumerate(slides): sheet.paste(s.resize((270, 337)), ((i % 4) * 280, (i // 4) * 347))
sheet.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "carousel_sheet.png"))

# ---------- PDF ----------
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
for w in ("Bold", "Regular", "Medium"): pdfmetrics.registerFont(TTFont("Pop-" + w, GF + f"Poppins-{w}.ttf"))
pw, ph = A4; c = canvas.Canvas(os.path.join(OUT, "Maqam-Monthly-WordPress-Checklist.pdf"), pagesize=A4)
c.setTitle("Monthly WordPress Checklist - Maqam Digital"); c.setAuthor("Maqam Digital")
c.setFillColorRGB(239/255, 1, 185/255); c.rect(0, ph - 170, pw, 170, stroke=0, fill=1)
c.setFillColorRGB(17/255, 17/255, 17/255)
c.setFont("Pop-Medium", 10); c.drawString(40, ph - 40, "maqam digital")
c.setFont("Pop-Bold", 26); c.drawString(40, ph - 90, "The monthly WordPress check")
c.setFont("Pop-Regular", 11); c.drawString(40, ph - 115, "Six checks that stop most website emergencies. Do them on the 1st of every month.")
months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
y = ph - 205
for i, (title, why, how) in enumerate(ITEMS):
    c.setFillColorRGB(17/255, 17/255, 17/255)
    c.setFont("Pop-Bold", 12.5); c.drawString(40, y, f"{i+1}. {title}"); y -= 16
    c.setFont("Pop-Regular", 9.5); c.drawString(54, y, "Why: " + why); y -= 13; c.drawString(54, y, "How: " + how); y -= 18
    c.setFont("Pop-Medium", 6.5); c.setLineWidth(0.7)
    for m, mo in enumerate(months):
        x = 54 + m * 40; c.rect(x, y - 2, 10, 10, stroke=1, fill=0); c.drawString(x + 13, y, mo)
    y -= 18
    c.setStrokeColorRGB(0.85, 0.85, 0.85); c.line(40, y + 4, pw - 40, y + 4); c.setStrokeColorRGB(17/255, 17/255, 17/255)
    y -= 14
c.setFillColorRGB(17/255, 17/255, 17/255); c.roundRect(40, 50, pw - 80, 92, 14, stroke=0, fill=1)
c.setFillColorRGB(239/255, 1, 185/255); c.setFont("Pop-Bold", 15); c.drawString(62, 112, "Rather we did it for you?")
c.setFillColorRGB(1, 1, 1); c.setFont("Pop-Regular", 10.5)
c.drawString(62, 92, "Maqam Digital website care covers updates, backups and checks from £95/month.")
c.drawString(62, 74, "maqamdigital.com  ·  obaid@maqamdigital.com  ·  WhatsApp +92 302 6559858")
c.save(); print("ok", len(slides))
