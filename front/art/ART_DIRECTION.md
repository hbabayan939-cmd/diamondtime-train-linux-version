# Last Train carriage art direction

This is the art and asset guide for the Linux source fork. The asset files and artwork workflow are platform-independent; run project commands from a Linux terminal at the repository root.

## Scene specification

- **Logical canvas:** 836 × 470 pixels, matching the 16:9 carriage illustration. Every displayed raster layer uses this coordinate system. The browser scales it with nearest-neighbor sampling and crops with `xMidYMid slice` on narrow screens.
- **Visual density:** wood grain, brass rivets, fabric flecks, tree branches, mountain strata, masonry, glass drops, and highlights should resolve into 1–4 logical-pixel clusters. Large untextured silhouettes are reserved for distant shadow only.
- **Palette:** ink `#0a152b`, midnight `#101b2a`, indigo `#302f65`, mist `#708da0`, muted pine `#244047`, velvet `#4b203d`, warm brass `#b98e6e`, lamp amber `#ffd087`. Amber covers small focal areas; blue-violet carries most of the scene.
- **Mood:** quiet dark fantasy, with candlelike carriage light and weathered materials. No horror imagery.

## Layer order and motion

1. Stage-colored valley raster at six journey phases: dawn, morning, afternoon, sunset, twilight, night. The station roof, arcade, hilltop ruin, bridge, rock face, and river receive deliberate 1–4-pixel detail clusters. Adjacent phases crossfade from journey progress, including long journeys with multiple cycles.
2. Architecture lights, water glints, thin fog, and distant birds add independent low-speed motion. Transparent middle and near pine strips and a gravel-and-vegetation strip scroll at progressively faster speeds. Their parallax stops when the journey pauses or arrives, and slows on final approach.
3. Four distinct falling-rain frames, fixed glass beads, runoff streaks, reflections, and a four-frame firefly sprite sit between scenery and interior. Rain intensity follows the existing journey-progress weather window.
4. Transparent carriage artwork contains the window openings. Additional pixels enrich wood grain, upholstery and brass, followed by a dithered amber light-spill layer and drifting dust motes.
5. Route board, diary notebook, statistics ticket, and radio remain interactive DOM elements above the artwork.

The board, heading, notebook, and radio use small transparent material tiles so their surfaces share the scene's pixel grain.

The six valley variants preserve one location. Weather and time change while recognizable structures remain in place. This establishes visual quality before adding more biomes.

## Source and reproduction

The two source PNGs in `source/` are original images generated with OpenAI's built-in image generation tool for this project. No third-party asset license is needed. The final source prompts were:

```text
Use case: stylized-concept
Asset type: original pixel-art landscape layer for an interactive train-window scene
Primary request: a richly detailed dark-fantasy railway valley at blue hour, viewed horizontally from a moving train, with layered distant jagged mountains, pine forest, small warm-lit stone station ruins and an old viaduct, subtle low fog, tiny amber lights, rain-softened atmosphere. No horror.
Style/medium: authentic premium 2D game pixel art, hard-edged deliberate small pixel clusters, dense manual-looking dithering and selective highlights, consistent pixel grid, no smooth brush strokes, no vector gradients, no 3D.
Composition/framing: wide side-scrolling environment, uninterrupted left and right edges, horizon in upper third, no train interior, no UI.
Color palette: midnight navy, muted violet, desaturated blue-green with scarce warm amber windows.
Constraints: original artwork, no text, no logos, no characters, no watermark.
```

```text
Use case: stylized-concept
Asset type: original foreground environment art for a React train-compartment game scene
Primary request: an empty cozy old wooden train carriage interior, straight-on symmetrical view, with THREE large rectangular adjacent windows spanning the middle 80 percent of the image from about 16 percent to 60 percent image height; lower 40 percent includes a broad dark walnut table, worn velvet seat corners, brass trim and rivets. Two compact amber wall lamps near the top corners. Through the windows show only featureless deep blue darkness because the actual moving landscape will be composited separately. No people, no written signs, no objects that look like UI.
Style/medium: premium high-density 2D pixel-art game background, deliberate tiny hard-edged pixel clusters, detailed wood grain, carved seams, upholstery texture, dark fantasy warmth, no horror, no vector look, no smooth brush strokes.
Lighting/mood: deep midnight blues and muted purples, warm amber practical lamps with nuanced falloff and reflected highlights.
Composition/framing: wide straight-on elevation, three window openings have straight clean edges and wide ornate wooden mullions; no perspective tilt; crisp 16:9.
Constraints: original art, no text, no logos, no watermark.
```

Run `python3 front/scripts/build_pixel_art.py` from the repository root with Pillow installed to rebuild `front/public/art/`. The script cuts true alpha window openings, generates stage color variants, and draws deterministic transparent parallax, terrain, glass, four-frame rain, lighting, and firefly layers. Keep master assets in `source/`; edit them at native resolution before rebuilding. Do not apply a pixelation filter to vector stand-ins.

The script also writes static [afternoon](previews/afternoon.png), [night](previews/night.png), and [rainy night](previews/rainy-night.png) composition previews for visual review. They omit moving sprites and HTML controls.

## Artwork still needed

The near-tree and weather layers are procedural. Artist-authored silhouette passes, more varied weather sequences, and additional original locations would further improve the scene. The carriage and primary valley artwork are already present and original.
