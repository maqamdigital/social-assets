# Lyric reel: "Kya kaha hai chaand ne"

Moonrise over the sea, Urdu lyrics shown 2 to 3 words at a time, each word fading in as it is sung.
1080x1920, 30 fps, 28 s. Word timings in `render.py` were read off the reference clip, so they line up with that audio.

## Render
```
npm pack @fontsource/noto-nastaliq-urdu && tar xzf fontsource-noto-nastaliq-urdu-*.tgz
python3 render.py --audio reference.mp4 \
  --font package/files/noto-nastaliq-urdu-arabic-500-normal.woff --out reel.mp4
```
- `--bg stock.mp4` swaps the generated sky/sea for any stock clip (Pexels, Pixabay, Mixkit). It is scaled and cropped to 9:16 and darkened slightly so the text stays readable.
- `--preview 1.5 8.5 27` writes still frames instead of the video, for quick checks.
- Change `GROUPS` to regroup words on screen (counts must add up to 32).

The song audio is not stored here. For Instagram/TikTok, the safer route is to upload a silent cut and pick the same song from the in-app music library.
