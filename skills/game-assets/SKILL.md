---
name: game-assets
description: Make and import art and audio for a game. Covers sprites, sprite sheets and animation frames, tilesets, icons and UI, backgrounds and parallax layers, key art, seamless textures, PBR materials, 3D models (image-to-3D, remesh, auto-rig), 3D-rendered sprites, sound effects, music and voice lines. Assets are generated with fal (its MCP server or `um fal`), converted into engine-exact frames, and imported with the right settings for Godot, Unity, Unreal, web, Bevy, LÖVE, pygame or MonoGame. Use whenever a game needs new art, audio or models, or the user mentions fal, sprites, sprite sheets, tilesets, textures, 3D models, SFX, music, voice lines, placeholder art, a style guide, or "make it look better".
---

# Game assets

The flow is always the same: **style bible → generate → convert → import → look at it in the game →
credit it.** Most bad game art comes from skipping the first step or the fifth.

The recipes and prompting rules here are adapted from universal-modder's `fal-assets` and `asset-pipeline`
skills (MIT), with the engine-import side added for games whose source you own.

## 0. Before generating anything
- **The style bible** lives in `GAME_PLAN.md` (game-plan skill, step 5): resolution or pixels-per-unit,
  palette, outline, camera and perspective, light direction, frame counts, naming. Put its key words in a
  reusable **style suffix** for prompts.
- **The asset list:** name, size, frame count and pivot for each asset. Code refers to stable names
  (`assets/sprites/enemy_slime.png`), so placeholders and final art are interchangeable.
- **Placeholders first:** coloured shapes at the right size and pivot let you finish the code before the
  art exists.
- **Check the rules:** many game jams ban AI-generated assets, and stores ask you to disclose them. Ask the
  user when it's unclear.

## 1. Setup: fal (check once per session)
- **Key:** `FAL_KEY` must be set (create one at https://fal.ai/dashboard/keys). `um fal` also reads it from
  a `.env` file in the working folder. Keep `.env` in `.gitignore`, and never put the key in game code or
  builds; `ugd release check` flags leaked keys.
- **MCP:** fal's hosted server is `https://mcp.fal.ai/mcp` with the header `Authorization: Bearer $FAL_KEY`.
  This repo pre-configures it for each agent: `.mcp.json` (Claude Code), `.codex/config.toml` (Codex),
  `.cursor/mcp.json` (Cursor), `.vscode/mcp.json` (VS Code / Copilot) and `gemini-extension.json` (Gemini
  CLI). Its tools: `search_models`, `recommend_model`, `get_model_schema`, `get_pricing`, `run_model`,
  `submit_job` / `check_job` / `get_job_result`, `upload_file`, `search_docs`.
- **CLI:** `um fal <recipe>`, from universal-modder (`uv tool install
  git+https://github.com/rehan-remade/universal-modder`). It uploads local inputs, waits, downloads every
  output, and appends the endpoint, inputs, seed and request id to `<out>/fal_manifest.jsonl`, so every
  asset can be traced and regenerated.
- **Which to use:** the MCP for discovery (best model for X right now, its inputs, its price); `um fal` for
  anything that lands in the project; MCP `run_model` for a quick look where a URL is enough.

## 2. Recipes
`um fal <recipe> --help` lists the options. `--model` overrides the endpoint, `--set k=v` passes extra
inputs, and `--out assets/gen` keeps generated files together. These defaults were current in September 2026
(per universal-modder). The catalog changes weekly: check `um fal search` or MCP `recommend_model` before a
big batch.

| Asset | Command | Default endpoint |
|---|---|---|
| Sprite or icon, transparent background | `um fal sprite "<subject, view, style>" --name x` | `openai/gpt-image-2` |
| Concept art, key art, backgrounds | `um fal image "<prompt>" --aspect 16:9` | `fal-ai/nano-banana-2` |
| Variants, extra frames, recolours, the same character in a new pose | `um fal edit "<change>" --ref base.png` | `fal-ai/nano-banana-2/edit` |
| Background removal | `um fal rmbg in.png` | `fal-ai/birefnet/v2` |
| Clean pixel art from any image | `um fal pixelate in.png --colors 24` | `fal-ai/image2pixel` |
| Upscale | `um fal upscale in.png --factor 2` | `fal-ai/seedvr/upscale/image` |
| Seamless tiling texture | `um fal texture "mossy cobblestone"` | `fal-ai/z-image/turbo/tiling` |
| PBR maps (basecolor, normal, roughness, metalness, height) | `um fal pbr "rusted sheet metal"` | `fal-ai/patina/material` |
| Image → textured 3D model (GLB) | `um fal model3d concept.png` (`--engine trellis2\|hunyuan\|tripo\|meshy`) | `fal-ai/trellis-2` |
| Auto-rig a humanoid, with optional animations | `um fal rig character.glb --animate` | `fal-ai/meshy/rigging` |
| Sound effect | `um fal sfx "laser shot, punchy, sci-fi" --seconds 1.2` | `fal-ai/elevenlabs/sound-effects/v2` |
| Music | `um fal music "calm village theme, chiptune, 100 bpm, loopable" --seconds 90` | `elevenlabs/music/v2.5` |
| Voice line | `um fal voice "You shouldn't be here." --voice-id Adam` | `fal-ai/elevenlabs/tts/eleven-v3` |
| Cutscene or trailer clip from a still | `um fal video still.png "slow push-in on the castle"` | `bytedance/seedance-2.5/image-to-video` |
| Anything else | `um fal run <endpoint> key=value key:=json image_url=@local.png` | any |

Other useful endpoints: game-ready remeshing (`tripo3d/tripo/remesh`, `fal-ai/meshy/v5/remesh`),
`fal-ai/trellis-2/retexture`, text-to-motion (`fal-ai/hunyuan-motion`), SVG icons
(`fal-ai/recraft/v4.1/text-to-vector`).

## 3. Prompting art that fits the game
- **Put the style bible in every prompt.** For example: *"16-bit pixel art game sprite, 32×32 grid, crisp
  dark 1 px outline, 16-colour palette, top-left light, centered, plain flat white background, no shadow,
  no text"*. Describe the style rather than naming a living artist: it prompts better and avoids imitation
  disputes.
- **State the view and orientation explicitly:** "perfectly side-on, facing right", "top-down 3/4 view",
  "isometric 2:1, facing south-east". Fixing orientation afterwards costs quality. Decide the engine
  convention once (e.g. all side-view sprites face right; the engine flips them).
- **Backgrounds:** transparent (gpt-image-2) or a flat colour that `um sprite cutout` can flood-fill. Avoid
  gradients, scenery and ground shadows.
- **A consistent set:** generate one hero image, then derive the rest with the edit endpoint and the hero as
  `--ref` ("same knight, now swinging the sword, frame 2 of 4"). Don't ask one prompt for a whole sprite
  sheet: grids come out uneven.
- **Many angles or many animation frames of one object:** go through 3D. Concept → `um fal model3d` → (rig
  and animate) → `um render3d` from the game's camera. Every heading and frame stays consistent.
- **Tilesets:** generate base textures as seamless tiles (`um fal texture`) and check them with
  `um sprite tile-preview`. Image models are unreliable at full autotile sets (16 or 47 transition
  tiles), so build the transitions with the engine's terrain tools, with masks, or by hand from a few
  generated edge pieces.
- **UI:** generate icons as a set, with the same suffix and background ("game UI icon, centered, flat
  colours, thick outline"). Generate 9-slice panels plain and set the margins in the engine. Use real
  fonts (OFL, e.g. Google Fonts), never generated lettering.
- **Parallax backgrounds:** generate each layer separately on a flat background (far, mid, near), make
  them tile horizontally, and cut them out.
- **Text and logos:** models add them uninvited. Say "no text" unless you want it, and put titles on key
  art in compositing, not in the prompt.

## 4. Convert to engine-ready files
Decide the target format once in the style bible: frame size, pixels-per-unit, pivot and sheet layout.
Every asset then goes through the same commands (`um sprite ...`, `um render3d ...`, each with `--help`).
```bash
um sprite info raw.png                                     # size, alpha coverage, corner colour
um sprite cutout raw.png cut.png                           # flat background → transparent (border flood fill keeps interior whites)
um sprite cutout raw.png cut.png --grey 150 --keep-top 0.8 # also remove a soft grey shadow or floor
um sprite fit cut.png hero.png --size 32x32 --anchor bottom --hard-alpha   # trim + ONE nearest-neighbour scale into the frame
um sprite pixelate cut.png px.png --size 32x32 --colors 16 --outline       # true pixel art from painterly art
um sprite palette px.png px2.png --from palette_ref.png    # snap to the game's palette
um sprite frames hero.png frames/ --n 4 --kind bob         # cheap idle animation (bob/squash/wobble/flash)
um sprite sheet sheet.png frames/*.png --cols 4            # grid sheet (or --vertical for a strip)
um sprite slice sheet.png out/ --frame 32x32               # the other direction
um sprite team-mask unit.png unit_grey.png --hue blue      # recolour mask for palette-swapped variants
um sprite seamless tex.png tex_tiled.png                   # fix seams on a texture
um sprite preview hero.png look.png --scale 6              # checkerboard + zoom: LOOK at it before importing
```
- **Pixel art:** scale once, with nearest neighbour, to the final size. Never scale pixel art twice. HD or
  painted art uses `fit --smooth`.
- **3D → sprites** (consistent headings and animation frames for 2D games):
  ```bash
  um fal model3d concept.png --name hero
  um render3d assets/gen/hero.glb frames/ --preset side --canvas 128 --length 110          # platformer, facing right + left
  um render3d assets/gen/unit.glb frames/ --preset iso8 --length 80 --anims idle:8:bob,walk:12:walk --shadows
  ```
  The presets are `side`, `topdown`, `iso8`, `trueiso`, `aoe2` (16 headings) and `turntable`. `--length`
  sets the model's longest horizontal side in pixels, and `--forward-yaw` turns the nose to +X (check the
  first frame). It needs Blender (`blender` on PATH or `BLENDER=...`).
- **Make it reproducible:** put the commands in a script (`tools/build_assets.sh` or `.ps1`) that rebuilds
  `assets/` from `assets/gen/`, so changing the style is one re-run, not an afternoon.

## 5. Import with the right settings
The engine decides how the file looks on screen. Most "blurry", "shimmering" or "wrong size" sprites are
import settings, not art. The essentials:
- **Pixel art:**
  - nearest filtering and no mipmaps;
  - lossless or no compression;
  - pixels-per-unit equal to the tile size;
  - integer scaling and a pixel-snapped camera.
- **Sheets:** frame size and count must match the code. Prefer engine resources that store the slicing
  (Godot `SpriteFrames`, Unity sprite slicing, Phaser atlas JSON) over magic numbers in code.
- **Make import settings code, not clicks,** so assets you add from outside the editor import correctly:
  - Godot: commit the generated `.import` files, and run `godot --headless --import` after adding files;
  - Unity: an `AssetPostprocessor` editor script applies settings by folder;
  - Unreal: a Python import script;
  - code-first engines: set the filtering in code.
- Per-engine settings (pixel art, HD sprites, audio, 3D, fonts): `references/engine-import.md`.

## 6. Audio
- **Formats:** the fal SFX and music endpoints return MP3. Convert for the engine:
  - `ffmpeg -i x.mp3 -ar 48000 x.wav` for short SFX (most engines);
  - `ffmpeg -i x.mp3 -c:a libvorbis -q:a 5 x.ogg` for music (Godot, Unity, LÖVE, Bevy);
  - on the web, test Safari, and ship MP3/M4A where OGG won't play.
- **Trim and level:** trim leading silence (`-af silenceremove=start_periods=1:start_threshold=-50dB`) and
  normalize every SFX to a common loudness (`-af loudnorm=I=-16`) before mixing with buses.
- **Variation:** generate 2-4 variants of frequent sounds (footsteps, hits, pickups) and randomize pitch
  ±5-10% in the engine.
- **Loops:** use `um fal sfx ... --loop`, or ask the music model for a loopable track. Set loop points in
  the engine's import, and listen to the seam.
- **Voice:** keep one voice id per character, and store the lines next to a subtitle/string table.

## 7. 3D assets for 3D games
- **Pipeline:** concept → `um fal model3d` → remesh to a polygon budget
  (`um fal run tripo3d/tripo/remesh mesh_url=@model.glb face_limit:=8000`) → check scale, pivot and
  orientation in Blender (a Blender MCP server helps) → GLB → engine import with collision.
- **Axes and units:**
  - glTF: Y-up, metres, front faces +Z;
  - Godot: Y-up, −Z forward (imported glTF models face +Z);
  - Unity: Y-up, +Z forward;
  - Unreal: Z-up, centimetres, +X forward;
  - Blender: Z-up (its glTF exporter converts).

  Fix orientation once in the import step, not in gameplay code.
- **Materials:** `um fal pbr` maps. Unreal wants ORM packing (occlusion, roughness, metal in RGB); Unity's
  standard workflow wants metallic + smoothness (smoothness = 1 − roughness, in alpha).
- **Characters:** `um fal rig --animate` gives a rigged GLB with animations. Retarget in the engine (Godot
  BoneMap + `SkeletonProfileHumanoid`, Unity Humanoid avatars, Unreal IK Retargeter).

## 8. Look at it in the game, then credit it
- Put one converted asset in a scene next to existing art and take a screenshot (the playtest-automation
  skill). Check scale, facing, pivot, filtering, outline and palette. Fix the recipe, then batch-convert the
  rest with the same commands.
- **Credits:** every asset gets a line in `CREDITS.md`: name, source (generated with fal + model, CC0 pack +
  author, made by hand), and license. Keep `fal_manifest.jsonl` with the assets; it records prompts, models,
  seeds and request ids, but not your key.

## Cost and etiquette
- **Price the expensive stuff:** check video, 3D and long music first (`um fal price <endpoint>` / MCP
  `get_pricing`). For more than about 20 generations, or anything video-sized, tell the user the rough cost
  before running it.
- **Iterate cheaply:** explore at low quality or resolution (`--quality low`, `--res 0.5K`), then re-run
  the winners at full quality with the same prompt (and seed where supported).
- **Licenses:** check each model's license page for commercial use. Credit fal and name the models in the
  game's credits.
