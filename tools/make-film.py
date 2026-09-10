#!/usr/bin/env python3
"""Turn your own footage into the scroll film.

  python3 tools/make-film.py film.mp4                      one landscape video
  python3 tools/make-film.py wide.mp4 --portrait tall.mp4  plus a 9:16 cut for phones
  python3 tools/make-film.py clips/                        every clip in the folder, in name order

Replaces film/desktop, film/mobile, film/stills, the posters and film/manifest.js
next to index.html. Needs ffmpeg (ffmpeg.org) and Pillow (pip install pillow).
--chapters: six numbers from 0 (start) to 1 (end), where each chapter's words sit.
"""
import argparse, glob, json, os, shutil, subprocess, sys, tempfile
try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit('Pillow is missing: pip install pillow')

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILM = os.path.join(SITE, 'film')
VIDEO = ('.mp4', '.mov', '.m4v', '.webm', '.mkv', '.avi')
STILL = ('.jpg', '.jpeg', '.png', '.webp')
SIZES = {'desktop': (1280, 720), 'mobile': (576, 1024)}


def duration(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'default=nw=1:nk=1', path], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        sys.exit('Could not read %s (is ffmpeg installed?)' % path)


def grab(path, count, tmp, tag):
    """count frames spread evenly across one clip"""
    pattern = os.path.join(tmp, tag + '_%05d.png')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-vf', 'fps=%.6f' % (count / duration(path)),
                    '-frames:v', str(count), pattern], check=True)
    got = sorted(glob.glob(os.path.join(tmp, tag + '_*.png')))
    if not got:
        sys.exit('No frames came out of ' + path)
    return got


def frames_from(source, n, tmp, tag):
    files = [source] if os.path.isfile(source) else sorted(
        f for f in glob.glob(os.path.join(source, '*')) if f.lower().endswith(VIDEO + STILL))
    if not files:
        sys.exit('Nothing usable in ' + source)
    clips = [f for f in files if f.lower().endswith(VIDEO)]
    if clips:
        lengths = [duration(c) for c in clips]
        out = []
        for k, (c, d) in enumerate(zip(clips, lengths)):
            out += grab(c, max(2, round(n * d / sum(lengths))), tmp, '%s%02d' % (tag, k))
    else:
        out = files
    return [out[min(len(out) - 1, i * len(out) // n)] for i in range(n)]   # exactly n


def lum(im):
    band = im.convert('L').resize((64, 64)).crop((12, 18, 52, 38))
    px = list(band.getdata())
    return round(sum(px) / len(px) / 255.0, 3)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('source', help='a video, or a folder of videos or stills')
    ap.add_argument('--portrait', help='9:16 video or folder for phones (otherwise the landscape film is cropped)')
    ap.add_argument('--frames', type=int, default=200, help='frames in the film, 24-999 (default 200)')
    ap.add_argument('--chapters', default='0.03,0.35,0.47,0.65,0.86,0.985', help='default %(default)s')
    ap.add_argument('--focus', type=float, default=0.5, help='phone crop of a landscape film: 0 = left, 1 = right')
    ap.add_argument('--quality', type=int, default=72, help='WebP quality (default 72)')
    a = ap.parse_args()
    n = max(24, min(999, a.frames))
    marks = [float(x) for x in a.chapters.split(',')]
    with tempfile.TemporaryDirectory() as tmp:
        wide = frames_from(a.source, n, tmp, 'w')
        tall = frames_from(a.portrait, n, tmp, 't') if a.portrait else None
        for sub in ('desktop', 'mobile', 'stills'):
            shutil.rmtree(os.path.join(FILM, sub), ignore_errors=True)
            os.makedirs(os.path.join(FILM, sub))
        lums = {name: [] for name in SIZES}
        for i in range(n):
            src = Image.open(wide[i]).convert('RGB')
            for name, (w, h) in SIZES.items():
                base = Image.open(tall[i]).convert('RGB') if (name == 'mobile' and tall) else src
                focus = a.focus if (name == 'mobile' and not tall) else 0.5
                im = ImageOps.fit(base, (w, h), Image.LANCZOS, centering=(focus, 0.5))
                im.save(os.path.join(FILM, name, '%03d.webp' % i), 'WEBP', quality=a.quality, method=5)
                lums[name].append(lum(im))
            print('\rframe %d/%d' % (i + 1, n), end='', flush=True)
        print()
    chapters = [min(n - 1, max(0, round(m * (n - 1)))) for m in marks]
    for name in SIZES:
        for k, f in enumerate(chapters):
            shutil.copy(os.path.join(FILM, name, '%03d.webp' % f), os.path.join(FILM, 'stills', '%s-%d.webp' % (name, k + 1)))
        Image.open(os.path.join(FILM, name, '%03d.webp' % chapters[0])).convert('RGB').save(
            os.path.join(FILM, 'poster-%s.jpg' % name), quality=82)
    og = Image.open(os.path.join(FILM, 'desktop', '%03d.webp' % chapters[0])).convert('RGB')
    ImageOps.fit(og, (1200, 630), Image.LANCZOS).save(os.path.join(FILM, 'og.jpg'), quality=84)
    man = {'frames': n, 'pad': 3, 'ext': 'webp', 'chapters': chapters,
           'variants': {name: {'w': w, 'h': h, 'dir': 'film/' + name, 'lum': lums[name]} for name, (w, h) in SIZES.items()}}
    with open(os.path.join(FILM, 'manifest.js'), 'w') as fh:
        fh.write('/* Generated by tools/make-film.py */\nwindow.FILM = ' + json.dumps(man, separators=(',', ':')) + ';\n')
    print('Done: %d frames, chapters at frames %s. Open index.html to check.' % (n, chapters))


if __name__ == '__main__':
    main()
