# Maqam Content Engine: weekly runbook

Brand: Maqam Digital (maqamdigital.com), a remote web studio (WordPress, WooCommerce, Shopify, local SEO, speed, care plans) for UK and international small businesses.
Metricool brand: blogId 7318390, timezone Asia/Karachi. Networks: Instagram @maqamdigital, Facebook page 517544194785127 (LinkedIn is the personal profile; do not post this pack there).

## Standing rules
- One post per day, every day, on both Instagram and Facebook.
- Instagram at 18:10 Asia/Karachi, Facebook at 18:15 (separate Metricool posts; captions differ).
- Mix per 7 days: 5 reels (1080x1920, 9 to 18 s, with sound), 1 checklist carousel (8 slides, 1080x1350), 1 static or carousel with the offer.
- Every piece carries the Maqam logo (brand/logo-white.png or logo-black.png). No "maqam digital" text in place of the logo.
- One offer everywhere: free website audit returning the top 3 fixes. CTA: "Comment AUDIT or DM us your website link". Checklist carousels may use "Comment CHECKLIST".
- Captions: Instagram = 2 to 4 short lines + 3 hashtags; Facebook = one short line with the CTA, plus a reel title.
- No em dashes anywhere. No invented stats, client names or results. Mark example sites "shown for illustration".
- Never repeat a topic already listed in LOG.md.

## Toolkit
- mq.py: palette (LIME, PINK, INK, WHITE), fonts (Poppins/Inter system fonts), logo(), wrap(), end card with the audit CTA, synth() sound beds, encode() via ffmpeg.
- reels.py: reel formats (kinetic one-word beats, phone teardown, looping question, scenario chat, before/after wipe, notes checklist). Copy a format and change the cards.
- posts.py / carousel.py: checklist carousels, static offer post, PDF checklists (reportlab).
- mq.py writes to /home/claude/out; change OUT if needed. Install missing deps with pip --break-system-packages (numpy, pillow, reportlab).
- Strategy doc (formats, research, 30-day calendar, captions, DM flow): Claude Docs project f96b1aff-08c3-4db2-9df4-9fa9175942e7, node 36f7d37e-3ca4 ("Maqam Content Engine"). Read it with the Claude Docs read tool.

## Weekly procedure
1. Read LOG.md and Metricool getScheduledPosts for the next 21 days. Find the first date with no Maqam post.
2. Plan 7 new pieces for the 7 days from that date (topics from the strategy doc calendar and themes not yet in LOG.md).
3. Render them, check a contact sheet of frames for overlaps and typos, fix, re-render.
4. Copy files to /home/claude/social-assets/<YYYY-MM-DD of first post>/, commit and push to main.
   Media URL: https://raw.githubusercontent.com/maqamdigital/social-assets/main/<folder>/<file>
5. Schedule with createScheduledPost (Instagram type REEL or POST; Facebook type REEL with a title, or POST).
6. Append the 7 rows to LOG.md, commit and push.
7. Report: what was scheduled, and any FAILED/ERROR posts in the last 7 days with their error text.
