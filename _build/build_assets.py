"""Builds assets/ for afterlife-film.com from the full-resolution originals in the repo root
plus a few shared files from the Art Kid Media site (fonts, logo, favicons, poster, headshot).
Run from the repo root:  python3 _build/build_assets.py
(Jekyll skips folders that start with an underscore, so _build/ is never published.)"""
import os, shutil, subprocess
from PIL import Image, ImageOps

ART = os.path.expanduser("~/Projects/artkid-website/assets")
OUT = "assets"
os.makedirs(f"{OUT}/fonts", exist_ok=True)

def cwebp(src_img, dst, q=80):
    tmp = dst + ".tmp.png"
    src_img.save(tmp)
    subprocess.run(["cwebp", "-quiet", "-q", str(q), "-m", "6", "-sharp_yuv", tmp, "-o", dst], check=True)
    os.remove(tmp)

# shared Art Kid Media files (same fonts, logo, icons; the laurel poster and headshot already built for artkid.media)
for f in ("inter-var-latin-v20.woff2", "plexmono-400-latin-v20.woff2"):
    shutil.copyfile(f"{ART}/fonts/{f}", f"{OUT}/fonts/{f}")
for f in ("logo-128.webp", "favicon-16.png", "favicon-32.png", "apple-touch-icon.png"):
    shutil.copyfile(f"{ART}/{f}", f"{OUT}/{f}")
shutil.copyfile(os.path.expanduser("~/Projects/artkid-website/favicon.ico"), "favicon.ico")
shutil.copyfile(f"{ART}/afterlife-poster-laurels.webp", f"{OUT}/poster-laurels.webp")       # 1000x1333, option 1 (sides)
shutil.copyfile(f"{ART}/csb-headshot.webp", f"{OUT}/csb-headshot.webp")                     # 600x600, Scott's pick
shutil.copyfile(os.path.expanduser("~/Projects/_DELIVERABLES/Afterlife_TFF_2026-10-02/01_Poster_Six_Laurels/"
                                   "AFTERLIFE_POSTER_6LAURELS_OPTION1_SIDES_web_2025x3000.jpg"),
                f"{OUT}/afterlife-poster-3000px.jpg")                              # download for press

# stills: 1920 and 960 wide WebP from the 3600-wide PNGs
STILLS = ["001", "002", "004", "005", "006", "007", "008", "009", "011"]
for n in STILLS:
    im = Image.open(f"Afterlife_Screenshot_Kilbourn_{n}.png").convert("RGB")
    for w in (1920, 960):
        h = round(im.height * w / im.width)
        cwebp(im.resize((w, h), Image.LANCZOS), f"{OUT}/still-{n}-{w}.webp", q=80)

# behind the scenes, 720 px tall; BTS5 loses the phone's MOTION badge (top 40 px)
for i, f in enumerate(["BTS1.jpg", "BTS2.jpg", "BTS3.jpg", "BTS4.jpg", "BTS5.png"], 1):
    im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
    if f == "BTS5.png":
        im = im.crop((0, 40, im.width, im.height))
    w = round(im.width * 720 / im.height)
    cwebp(im.resize((w, 720), Image.LANCZOS), f"{OUT}/bts-{i}.webp", q=78)

# social share image 1200x630 from still 011 (dock at sunset), centered crop
im = Image.open("Afterlife_Screenshot_Kilbourn_011.png").convert("RGB")
tw = round(im.height * 1200 / 630)
left = (im.width - tw) // 2
im.crop((left, 0, left + tw, im.height)).resize((1200, 630), Image.LANCZOS).save(f"{OUT}/og-image.jpg", quality=86, optimize=True, progressive=True)

for f in sorted(os.listdir(OUT)):
    p = f"{OUT}/{f}"
    if os.path.isfile(p):
        try:
            sz = Image.open(p).size if not f.endswith(".woff2") else ""
        except Exception:
            sz = ""
        print(f"{f:44s} {os.path.getsize(p)//1024:6d} KB  {sz}")
