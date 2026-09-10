# Sivaprakash & Manthra Bai — wedding film invitation

A scroll-driven invitation. As guests scroll, a film moves under six chapters of
words; the celebrations, the full Tamil invitation, add-to-calendar, share and a
WhatsApp RSVP open in panels.

## Look at it
Double-click `index.html`. No server or install needed. To send it to guests it
has to be online — see Hosting.

## Change the words
- **Everything on screen** (chapters, schedule, venue, the Tamil invitation) is in
  `index.html`. Each chapter is a `<section class="chapter">` with a comment above it.
- **Calendar file, share message, countdown, RSVP number** are in `assets/wedding.js`.
  If you change a time or the venue, change it in both files.
- **Chapter names** in the right-hand rail: the `<nav class="rail">` list and the
  `data-name` on each chapter, in `index.html`.

## Turn on RSVP
In `assets/wedding.js` set `rsvpWhatsApp: "919876543210"` (country code + number,
digits only). "Join our celebration" then opens a short reply form that hands the
message to WhatsApp. While it is blank the RSVP buttons stay hidden and the button
opens the celebrations panel.

## Hosting
Any static host works. Quickest: drag the whole folder onto
https://app.netlify.com/drop (or use GitHub Pages, Cloudflare Pages, Vercel). Then:
1. put the address in `siteUrl` in `assets/wedding.js`, so Share sends a link;
2. change `og:image` in `index.html` to the full address (`https://…/film/og.jpg`)
   so WhatsApp and Instagram previews show the picture.

Frames load in the background: the page opens once the first chapter and a coarse
pass through the film have arrived, then fills in.

## The film
`film/` holds an original placeholder film drawn in code for this invitation
(the generator is in `tools/placeholder-film/`, Python + numpy + Pillow).
`PROMPTS.md` has prompts for generating real footage.

### Use your own footage
Needs Python 3, `pip install pillow` and ffmpeg.
```
python3 tools/make-film.py my-film.mp4
python3 tools/make-film.py wide.mp4 --portrait tall.mp4
python3 tools/make-film.py clips/ --chapters 0.03,0.32,0.47,0.63,0.84,0.985
```
- 16:9 for computers. For phones, give a 9:16 cut with `--portrait`, or the middle
  of the landscape film is cropped (`--focus 0.3` moves that crop left).
- `--chapters` are six positions from 0 (start) to 1 (end) where each chapter's words
  sit; the film slows to a crawl there. Choose calm moments with room in the middle.
- The words switch between cream and dark ink by themselves, depending on how bright
  the frame is.
- Best footage: one continuous, steady forward move per shot (gimbal or drone), no
  cuts inside a shot, 20–40 seconds in total.

## How it behaves
- Scroll moves the film frame by frame and it eases to a stop under each chapter.
- Right: chapter rail (hover for names). Bottom left: current chapter. Bottom right:
  "Scroll to unfold", and on the last chapter "Back to the beginning". Thin progress line.
- Phones get the 9:16 frames; rotating the phone switches.
- With reduced motion or data saver switched on, the film becomes six still pages.
  Without JavaScript the same still pages show, with the panels at the end.
- Printing (the Print button, or Ctrl/Cmd+P) prints just the Tamil invitation card.

## Files
```
index.html            page and all its words
assets/wedding.js     dates, venue, RSVP number, share text
assets/styles.css     design
assets/app.js         film player and panels (no need to edit)
assets/fonts.css      fonts, embedded
film/                 frames, stills, posters, manifest.js
tools/make-film.py    your footage -> film/
tools/placeholder-film/  how the placeholder film was drawn
PROMPTS.md            prompts for AI-generated footage
```

Fonts: Cormorant Garamond, Manrope, Tiro Tamil — SIL Open Font License 1.1.
