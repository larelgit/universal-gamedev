# Importing assets, per engine

The settings that decide how an asset looks and sounds in the game. Where possible, apply them **as code**
(project settings, import scripts, loader options) so files you add from outside the editor import the same
way every time. API names drift between engine versions. When something doesn't compile, check the docs or
the official examples **for the exact version** in `GAME_PLAN.md`.

## Contents
- [Godot 4](#godot-4)
- [Unity 6](#unity-6)
- [Unreal 5](#unreal-5)
- [Web: Phaser, three.js, PixiJS](#web-phaser-threejs-pixijs)
- [Bevy](#bevy)
- [LÖVE](#löve)
- [pygame-ce](#pygame-ce)
- [MonoGame / FNA](#monogame--fna)
- [raylib](#raylib)
- [GameMaker](#gamemaker)
- [Ren'Py](#renpy)

---

## Godot 4
- **Pixel art:**
  - Project Settings → Rendering → Textures → Canvas Textures → Default Texture Filter = **Nearest**
    (`rendering/textures/canvas_textures/default_texture_filter`);
  - Display → Window → Stretch: Mode `viewport` (low-resolution render, pixel-perfect) or `canvas_items`,
    with Scale Mode `integer`;
  - optionally Rendering → 2D → Snap → snap 2D transforms and vertices to pixel.
- **Texture import:** for 2D, Compress Mode Lossless and no mipmaps (the 2D defaults). Commit the `.import`
  sidecar files; ignore the `.godot/` folder. After adding files from outside the editor, run
  `godot --headless --import` (or open the editor once) so they're imported before tests run.
- **Sheets and animation:**
  - `Sprite2D` with `hframes` / `vframes` / `frame`;
  - `AnimatedSprite2D` with a `SpriteFrames` resource (the editor can add frames from a sheet);
  - `AnimationPlayer` to animate any property;
  - `AtlasTexture` for regions.
- **Tiles:** `TileMapLayer` nodes with a `TileSet` (atlas sources, physics and terrain layers for
  autotiling).
- **3D:** `.glb`/`.gltf` preferred; `.fbx` is supported, and `.blend` needs Blender's path set. Name suffixes
  in the source file add physics on import: `-col` (mesh + collision), `-colonly` (collision only),
  `-convcol` (convex). The suffix `-loop` loops an animation. The Advanced Import Settings dialog, or an
  import script, sets the rest.
- **Audio:** WAV for SFX (loop mode and trim in the import dock); OGG Vorbis for music (loop toggle and
  offset); MP3 also works.
- **Fonts:** TTF/OTF/WOFF2 directly. For pixel fonts set Antialiasing to None and turn off subpixel
  positioning, or use a BMFont `.fnt`.

## Unity 6
- **Sprites:**
  - Texture Type = Sprite (2D and UI), Sprite Mode = Single or Multiple;
  - Pixels Per Unit = your tile size, Mesh Type = Full Rect for tiling sprites;
  - pixel art: Filter Mode = **Point (no filter)**, Compression = **None**, Generate Mip Maps **off**;
  - URP's 2D Pixel Perfect Camera for crisp scaling.
- **Do it in code:** an `AssetPostprocessor` in `Assets/Editor/` sets import settings by folder, so files an
  agent drops in arrive correct:
  ```csharp
  using UnityEditor;
  using UnityEngine;
  class PixelArtImporter : AssetPostprocessor {
      void OnPreprocessTexture() {
          if (!assetPath.StartsWith("Assets/Art/Pixel/")) return;
          var t = (TextureImporter)assetImporter;
          t.textureType = TextureImporterType.Sprite;
          t.spritePixelsPerUnit = 16;
          t.filterMode = FilterMode.Point;
          t.textureCompression = TextureImporterCompression.Uncompressed;
          t.mipmapEnabled = false;
      }
  }
  ```
  Default Presets with folder filters (Preset Manager) are the no-code alternative. For slicing sheets from
  code, use the 2D Sprite package's sprite-editor data provider API, or slice once in the Sprite Editor.
- **Audio:** Load Type = Decompress On Load for short SFX and Streaming for music; Compression = Vorbis
  (or ADPCM for very frequent short sounds).
- **3D:** FBX natively; glTF through the glTFast package (`com.unity.cloud.gltfast`). Check Scale Factor and
  axis conversion. Use the Humanoid rig for retargeting, and Loop Time on looping clips.
- **Fonts:** TextMeshPro font assets (Font Asset Creator). For pixel fonts, sample at the font's native size
  with point filtering.

## Unreal 5
- **2D (Paper2D):** right-click textures → Sprite Actions → *Apply Paper2D Texture Settings*. That sets
  Compression "UserInterface2D (RGBA)", Texture Group "2D Pixels (unfiltered)" and no mipmaps. Then use
  sprites, flipbooks, tile sets and tile maps.
- **3D:** FBX, glTF or USD through the Interchange importer. Unreal is Z-up and in centimetres. Use Nanite
  for dense static meshes, and collision from simple primitives or `UCX_`-prefixed meshes.
- **Do it in code:** with the Python Editor Script Plugin enabled, build `unreal.AssetImportTask` objects
  and pass them to `unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([...])`. Run it in the
  editor or headless with `-run=pythonscript -script=<file>`.
- **Audio:** 16-bit PCM WAV becomes Sound Waves. Use Sound Classes and Submixes for buses, and MetaSounds
  for procedural audio.
- **Fonts:** import TTF/OTF as Font assets (runtime cache for UMG text).

## Web: Phaser, three.js, PixiJS
- **Phaser:**
  - `pixelArt: true` in the game config for crisp scaling;
  - `this.load.spritesheet("hero", "hero.png", { frameWidth: 32, frameHeight: 32 })`;
  - atlases: `this.load.atlas("ui", "ui.png", "ui.json")` (TexturePacker JSON hash/array, which
    TexturePacker and free-tex-packer both write);
  - animations: `this.anims.create({ key, frames: this.anims.generateFrameNumbers("hero", { start: 0, end: 5 }), frameRate: 10, repeat: -1 })`;
  - Tiled maps: `this.load.tilemapTiledJSON`;
  - audio with fallbacks: `this.load.audio("jump", ["jump.ogg", "jump.mp3"])`.
- **three.js:**
  - `GLTFLoader` (with DRACO, meshopt or KTX2 decoders for compressed assets);
  - colour textures need `texture.colorSpace = THREE.SRGBColorSpace`;
  - pixel art uses `texture.magFilter = THREE.NearestFilter`;
  - optimize GLBs with glTF-Transform: `npx @gltf-transform/cli optimize in.glb out.glb`.
- **PixiJS (v8):** `await Assets.load(...)` for textures and TexturePacker sheets. For pixel art, set the
  texture source's `scaleMode` to `"nearest"` (or change the default texture style globally).
- **Everywhere:** CSS `image-rendering: pixelated` on the canvas when scaling up. Audio: MP3 plays
  everywhere; test OGG/Opus on Safari. Keep total download size small: compress textures and audio, and
  lazy-load later levels.

## Bevy
- **Pixel art:** `DefaultPlugins.set(ImagePlugin::default_nearest())`.
- **Files:** assets live in `assets/` at the crate root and load with `asset_server.load("sprites/hero.png")`.
- **Sheets:** `TextureAtlasLayout::from_grid(UVec2::splat(32), columns, rows, None, None)` plus a sprite that
  references the layout and an index.
- **3D:** `asset_server.load(GltfAssetLabel::Scene(0).from_asset("models/hero.glb"))`.
- **Audio:** OGG works by default; WAV, MP3 and FLAC need their cargo features.
- **API names move between Bevy releases.** Read `examples/2d/sprite_sheet.rs` and the other examples at the
  git tag matching your Bevy version rather than writing from memory.

## LÖVE
- **Pixel art:** `love.graphics.setDefaultFilter("nearest", "nearest")` before loading any images. Draw to a
  low-resolution `Canvas` and scale it up by a whole number.
- **Sheets:** `love.graphics.newQuad(x, y, w, h, sheetW, sheetH)`, or the anim8 library.
- **Audio:** `love.audio.newSource(path, "static")` for SFX and `"stream"` for music; OGG, WAV and MP3.
- **Fonts:** `love.graphics.newFont("font.ttf", size)`, or `newImageFont` for bitmap fonts.

## pygame-ce
- **Images:** `pygame.image.load(path).convert_alpha()`, after `set_mode`; converting makes blits fast.
- **Pixel art:** `pygame.display.set_mode((320, 180), pygame.SCALED)` scales the window with nearest
  neighbour and letterboxing. `pygame.transform.scale` / `scale_by` are nearest; `smoothscale` is for HD art.
- **Sheets:** `sheet.subsurface(pygame.Rect(x, y, w, h))` per frame.
- **Audio:** `pygame.mixer.Sound` for SFX (WAV/OGG) and `pygame.mixer.music` for streamed music.
  `pygame.mixer.pre_init(44100, -16, 2, 512)` before `pygame.init()` lowers latency.

## MonoGame / FNA
- **Content pipeline (MonoGame):** `Content/Content.mgcb` is built during `dotnet build`. Edit it with the
  MGCB Editor or as text. MonoGame 3.8.5 adds a code-first Content Builder project (`dotnet new mgcb`),
  which the docs present as the successor to the MGCB Editor; follow whichever the project already uses. Textures use the Texture processor (premultiplied alpha, mipmaps off for 2D);
  audio uses `SoundEffect` (WAV) and `Song` (OGG/MP3); fonts use `.spritefont` (or FontStashSharp for
  dynamic text).
- **Skipping the pipeline:** `Texture2D.FromFile(GraphicsDevice, path)` loads a PNG directly, which is handy
  for prototypes and tools.
- **Pixel art:** `spriteBatch.Begin(samplerState: SamplerState.PointClamp)`. Render to a low-resolution
  `RenderTarget2D` and scale it up by a whole number.

## raylib
- Textures default to point filtering, so pixel art is crisp unless you call `SetTextureFilter`.
- Draw to a low-resolution `RenderTexture2D` and scale it with `DrawTexturePro`.
- Audio: `LoadSound` for SFX; `LoadMusicStream` + `UpdateMusicStream` every frame for music.

## GameMaker
- Import strips with "Import Strip Image". Set each sprite's origin and collision mask. Group sprites into
  texture groups per level or area.
- Pixel art: turn off "Interpolate colours between pixels" in the platform's Game Options → Graphics.
- Audio: WAV, OGG or MP3. Stream music, and decompress short SFX.

## Ren'Py
- Images in `game/images/` are declared automatically by file name.
- Pixel art: `define config.nearest_neighbor = True`.
- Audio: `play music "audio/theme.ogg"`. Ren'Py plays OGG Vorbis/Opus, MP3 and WAV.
