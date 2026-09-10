# Prompts for generating real footage

The film in this folder is a drawn placeholder. For something closer to a filmed
look, generate four short clips with an AI video tool (Veo, Kling, Runway, Sora,
Pika…) and feed them to `tools/make-film.py`. Each clip is one unbroken, steady
forward camera move. Make every clip twice: 16:9 for computers and 9:16 for phones.

General settings: 8–10 seconds, 1080p, no people, no text or logos, no cuts,
slow and steady camera, natural light.

## 1 · The beginning — gopuram at first light
> Slow, steady cinematic shot at pale dawn: the camera starts on the bronze kalasams
> at the top of a towering South Indian temple gopuram against a soft blue-grey sky,
> then sinks smoothly down the tower past tiers of carved and painted figures, and
> glides toward the carved stone gateway, which darkens as the camera passes through.
> Morning haze, a few birds, warm granite. Photoreal, 35mm lens, no people, no text.

## 2 · The blessing and the threshold — corridor of lamps
> Smooth dolly forward along a long pillared corridor inside a Tamil Nadu temple:
> carved granite pillars, painted ceiling mandalas, rows of brass oil lamps with
> flickering flames and warm pools of light on polished stone. The camera ends on a
> white rice-flour kolam scattered with marigold petals at a doorway filled with
> bright morning light, and moves into the glow. Photoreal, no people, no text.

## 3 · The muhurtham — temple tank at sunrise
> From the stone steps of a temple tank at sunrise, the camera glides low and slowly
> over still water toward a small stone pavilion standing in the middle of the tank.
> Clay lamps float and flicker on the surface; gopurams and palm trees stand on the
> far side; the sun rises golden over the wall and everything is mirrored in the water.
> Soft haze, birds. Photoreal, no people, no text.

## 4 · The gathering and the promise — the wedding hall's doorway
> Slow push through hanging strands of orange marigold and white jasmine under a
> coconut-frond pandal, toward the decorated entrance of a Tamil wedding hall:
> a mango-leaf thoranam over a carved teak door, banana plants tied on either side,
> tall brass kuthuvilakku lamps burning, the doorway glowing with warm light from
> inside. Festive morning, photoreal, no people, no text.

## Putting it together
1. Name the clips in order, e.g. `clips/1.mp4 … clips/4.mp4` and `clips-9x16/1.mp4 … 4.mp4`.
2. Run:
   ```
   python3 tools/make-film.py clips/ --portrait clips-9x16/ --chapters 0.03,0.32,0.47,0.63,0.84,0.985
   ```
   With four equal clips those numbers put chapter 1 at the start of clip 1, chapters 2
   and 3 in clip 2, chapter 4 in clip 3, and chapters 5 and 6 in clip 4.
3. Open `index.html` and scroll through. If a chapter's words land on a busy moment,
   nudge its number and run the command again.

Check what the tool's licence allows before publishing generated footage.
