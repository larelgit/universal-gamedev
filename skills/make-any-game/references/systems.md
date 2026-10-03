# Systems cookbook

Cross-engine patterns for the systems most games need, with the engine-specific names where they differ.
Each section ends with the oracle that keeps it honest. Netcode has its own file: `multiplayer.md`.

## Contents
- [Time, frame rate and the game loop](#time-frame-rate-and-the-game-loop)
- [Input](#input)
- [State machines and events](#state-machines-and-events)
- [Data-driven content](#data-driven-content)
- [Save and load](#save-and-load)
- [Scenes, levels and global state](#scenes-levels-and-global-state)
- [UI, menus and settings](#ui-menus-and-settings)
- [Camera](#camera)
- [Audio](#audio)
- [Physics](#physics)
- [Game AI](#game-ai)
- [Procedural generation](#procedural-generation)
- [Localization](#localization)
- [Accessibility](#accessibility)
- [Performance](#performance)

---

## Time, frame rate and the game loop
- **Frame-rate independence.** Movement in `update` multiplies by delta time. Simulation that must be
  exact (physics, platformer jumps, netcode, replays) runs in a **fixed timestep** with an accumulator,
  and rendering interpolates between the last two states ("Fix Your Timestep!", Glenn Fiedler).
- **Smoothing that doesn't depend on frame rate:** `value = lerp(value, target, 1 - exp(-speed * dt))`.
  Plain `lerp(value, target, 0.1)` per frame runs faster at higher frame rates.
- **Pause** sets the game's time scale to 0 while UI keeps running. Godot: `get_tree().paused = true`, with
  `process_mode = PROCESS_MODE_ALWAYS` on the pause menu. Unity: `Time.timeScale = 0`, and UI animations use
  unscaled time. Hit-stop and slow motion use the same time scale, so decide what must ignore it (UI, audio,
  input).
- **Oracle:** run the same scripted input at 30, 60 and 144 fps (or with fixed deltas of those sizes);
  positions after N seconds match within a tolerance.

## Input
- **Map actions, not keys:** "jump", "fire", "move". Godot `InputMap` (Project Settings → Input Map); Unity's
  Input System package (Input Actions asset); Unreal Enhanced Input; on the web, `KeyboardEvent.code`
  (physical key, layout-independent) rather than `.key`, plus the Gamepad API.
- **Every menu works without a mouse** (gamepad and keyboard focus navigation), and rebinding is in the
  settings from the first public build.
- **Read input where it can't be missed.** Unity's `GetKeyDown` inside `FixedUpdate` drops presses; read in
  `Update` and buffer the action for the next fixed step. Godot's `Input.is_action_just_pressed` is safe in
  `_physics_process`.
- **Buffers make games feel responsive:** keep "jump pressed" alive for ~0.1 s, and attack inputs for
  ~0.2 s during recovery frames.
- **Sticks:** a radial dead zone of 0.15-0.25, rescaled so movement starts at 0 just outside it.
- **Show the right glyphs** for the active device (keyboard, Xbox, PlayStation, Switch), switching on last
  input.
- **Oracle:** the agent bridge or a test injects actions (not OS key events), so input tests run headless.

## State machines and events
- **Replace boolean soup with states.** Five flags `is_jumping`, `is_attacking`, `is_hurt`... allow 32
  combinations, most of them bugs. An enum-based state machine with explicit `enter` / `update` / `exit`
  allows only the states you designed. Use hierarchical states (grounded → idle/run) when it grows, and a
  pushdown stack for menus and modal UI.
- **Events decouple systems:** Godot signals; C# events or `UnityEvent`; observer callbacks in code-first
  engines. Keep a *small* set of well-named global events (`player_died`, `level_completed`). A global bus
  carrying everything is hard to debug.
- **Oracle:** unit-test the transition table (from state X, input Y leads to state Z). Log transitions, so a
  replay shows exactly where behaviour diverged.

## Data-driven content
- Content and tuning live in data the engine can hot-reload: Godot custom `Resource`s (`.tres`, text),
  Unity `ScriptableObject` assets, Unreal Data Assets and Data Tables (CSV/JSON import), JSON/TOML/CSV in
  code-first engines, and Tiled or LDtk for levels.
- **Balance in a spreadsheet, exported to CSV,** is how designers already work; give the human that loop.
- **Validate every content file in a test:** IDs are unique, references resolve, numbers sit in sane ranges,
  and every referenced sprite or sound exists. That one test catches most content bugs before a playtest
  does.

## Save and load
- **What to save:** the minimum state that can't be rebuilt, by stable IDs (not engine object references or
  scene paths). Settings go in a separate file from progress.
- **Format:** JSON (or another plain, versioned format). Every save has a `version` and **migrations** from
  every older version. Never delete a player's data on update.
- **Write atomically:** write to `save.tmp`, flush, rename over `save.json`, and keep `save.bak` from the
  previous write. A crash mid-write then can't destroy progress.
- **Where:**

| Engine | API | Folder |
|---|---|---|
| Godot | `FileAccess`, `JSON`, `ConfigFile` under `user://` | Windows `%APPDATA%\Godot\app_userdata\<project>` (or a custom user dir) |
| Unity | `Application.persistentDataPath` + `JsonUtility` or Newtonsoft JSON | Windows `AppData\LocalLow\<company>\<product>` |
| Unreal | `USaveGame` + `UGameplayStatics::SaveGameToSlot` | `Saved/SaveGames` |
| Web | `localStorage` (small, synchronous) or IndexedDB (large) | per origin: a new domain means new, empty saves |
| Code-first engines | serde (Rust), JSON libraries, `love.filesystem` (LÖVE), `platformdirs` (Python) | Windows `%APPDATA%`, macOS `~/Library/Application Support`, Linux `~/.local/share` |

- **Security:** don't load save files with formats that can execute code. A Godot `.tres`/`.res` can embed
  scripts, so player-editable saves should be JSON or `ConfigFile`, not Resources. In .NET, never use
  `BinaryFormatter`.
- **Steam Cloud:** configure Auto-Cloud paths in Steamworks rather than writing sync code.
- **Oracle:** a round trip test (save → load → compare state). Load the fixture saves from every older
  version through the migrations. Kill the process mid-save in a test and make sure the previous save
  survives.

## Scenes, levels and global state
- One small global layer for things that outlive scenes (settings, audio, save, session): Godot autoloads,
  Unity a bootstrap scene or `DontDestroyOnLoad`, Unreal the `GameInstance` and subsystems. Everything
  else lives in the scene that owns it.
- Load levels asynchronously behind a loading screen or transition. Keep level data (layout, spawns)
  separate from logic, so one level scene works for every level file.
- **Launch flags straight into a scene** (`--scene level_3 --seed 42`). They're for tests and for the
  human, who otherwise replays the intro every time.
- **Oracle:** load every scene or level in a loop headless, and fail on any error in the log.

## UI, menus and settings
- **The flow:** title → play (one click to gameplay), pause (resume, settings, quit), and game over → retry
  in under a second. Juice the buttons (game-feel skill).
- **Resolution independence:**
  - Godot: stretch mode `canvas_items` with aspect `expand`, or `viewport` for pixel art;
  - Unity: Canvas Scaler "Scale With Screen Size";
  - web: CSS scaling.

  For pixel art, use integer scaling with letterboxing.
- **Settings to ship:**
  - display mode (windowed, borderless, fullscreen), resolution, vsync, frame cap, quality preset;
  - UI scale;
  - volume per bus;
  - controls (rebinding);
  - accessibility (below);
  - language.

  Apply them immediately, and give display changes a revert timer.
- **Text:** fonts that cover every language you'll ship; no hard-coded strings.
- **Oracle:** screenshot every menu at 16:9, 16:10, 21:9 and a small window size, and look for overflow and
  clipping. A test navigates every menu with gamepad actions only.

## Camera
- **Follow:** a dead zone or soft zone, look-ahead in the movement direction, smoothing with the
  frame-rate-independent lerp above, and limits at level bounds.
- **2D pixel art:** snap the camera to whole pixels after smoothing (or render to a low-resolution viewport
  and upscale), or sprites shimmer.
- **3D:** a spring arm with collision for third person. Smooth the yaw separately from the pitch, and put
  FOV in the settings.
- **Shake and kicks:** the game-feel skill (trauma-based shake, with a setting to turn it off).
- **Oracle:** a scripted run along a path checks that the player never leaves the safe frame and the
  camera never leaves the level bounds.

## Audio
- **Buses:** master, music, SFX, UI, voice, each with a settings slider. Sliders are linear, buses take dB:
  `db = 20 · log10(slider)` (and mute at 0).
- **Variation:** 2-4 samples per frequent sound, ±5-10% random pitch, and a cap on simultaneous instances
  per sound.
- **Mixing:** duck music under dialogue and big moments; normalize assets to a common loudness (see the
  game-assets skill).
- **Music:** crossfade on bar boundaries. Loop points belong in the asset (OGG loop metadata, or the engine's
  loop settings).
- **Web:** browsers block audio until a user gesture. Resume the `AudioContext` (or the engine's audio) on
  the first click or key press, behind a "click to start" screen.
- **Formats:** WAV for short SFX, OGG Vorbis for music in most engines. On the web, test Safari, and ship
  MP3/M4A when OGG won't play.
- **Oracle:** a test that every sound referenced in data exists, plus the engine's audio debug view showing
  no clipping on the master bus.

## Physics
- **Fixed step + interpolation** (above). Use continuous collision detection for fast objects (bullets,
  cars). Collision layers and masks keep pair counts down. Keep sizes near real-world units (0.1-10).
- **Kinematic for characters, dynamic for props.** Players almost always want a kinematic or raycast
  controller you fully control. Dynamic bodies are for crates, debris and ragdolls.
- **Libraries:** Godot Physics or Jolt (3D); Unity PhysX (3D) and Box2D (2D); Unreal Chaos; Avian or Rapier
  in Bevy; on the web Rapier (WASM), Matter.js, Planck.js or cannon-es.
- **Traps:** moving "static" colliders every frame, tunnelling, stacking jitter (raise solver iterations,
  tune sleeping), and expecting engine physics to be deterministic across machines.
- **Oracle:** drop and stack tests at rest for 10 s; a fast projectile against a thin wall never passes
  through.

## Game AI
- **Decision layers, from simple to heavy:**
  - an **FSM** (patrol → chase → attack), which is enough for most action games;
  - **behaviour trees** for many reusable behaviours: built into Unreal; plugins in Godot (LimboAI,
    Beehave); Unity's Behavior package;
  - **utility AI** (score every option, pick the best) for sims and tactics;
  - **GOAP** for planners, as in F.E.A.R.
- **Pathfinding:**
  - A* on grids (Manhattan, octile or Euclidean heuristic);
  - navmeshes: Godot `NavigationServer2D/3D` + `NavigationAgent`, Unity's AI Navigation package
    (`NavMeshSurface`), Unreal's Recast navmesh, `recast-navigation` on the web;
  - flow fields for crowds heading to one goal;
  - hierarchical pathfinding for big maps.
- **Movement:** steering (seek, arrive, flee, wander, separation) with local avoidance (RVO; Godot's
  navigation agents include it).
- **Perception:** line-of-sight raycasts, vision cones, hearing events, and memory of the last known
  position.
- **Fairness and readability:** reaction delays, accuracy spread, telegraphed attacks, and limits on how
  many enemies attack at once (the "kung fu circle"). Hard AI isn't fun AI.
- **Debug draw:** paths, current state and targets drawn in the world, and dumped as JSON on demand. That's
  how you, the agent, see what the AI thinks.
- **Oracle:** AI-vs-scripted-player runs headless with assertions (the enemy reaches the player within N s
  on every spawn point; it never gets stuck for over 2 s).

## Procedural generation
- **Seeded randomness only:**
  - Godot `RandomNumberGenerator` with `.seed`;
  - in C#, `System.Random(seed)` or `Unity.Mathematics.Random` per stream (Unity's `Random.InitState` is
    global and shared);
  - Rust `rand_pcg` / `rand_chacha`;
  - JavaScript: a small PRNG such as mulberry32 or sfc32, never `Math.random`.

  Use one stream per system.
- **Toolbox:**
  - Noise (Perlin, Simplex, OpenSimplex2; `FastNoiseLite` is built into Godot and ported elsewhere) with
    fBm octaves and domain warping.
  - BSP rooms; cellular automata for caves (~45% fill, 4-5 neighbour rule, ~5 iterations).
  - Drunkard's walk.
  - Wave Function Collapse for tile adjacency.
  - Poisson disk sampling for natural placement.
  - L-systems for plants.
  - Voronoi for regions.
  - Marching squares or cubes for smooth terrain.
- **Mix in hand-made pieces:** generated layouts built from designed chunks read better and are easier to
  balance than pure noise.
- **Validate everything you generate:** connectivity (flood fill), the start-to-goal path, resource counts
  and difficulty bounds. This is the oracle: generate thousands of seeds in a test and assert the
  invariants. Log the seed of any failure and turn it into a regression test.

## Localization
- **String tables from day one:** Godot `TranslationServer` with CSV or PO; Unity's Localization package;
  Unreal's localization dashboard; i18n libraries on the web. Use keys, not English text, in code.
- **Never build sentences by concatenation.** Use named placeholders (`"{player} found {count} coins"`) and
  plural rules (ICU-style), because word order and plurals differ between languages.
- **Room to grow:** German and French run ~30% longer than English. CJK needs large fonts (Noto covers most
  scripts), and Arabic and Hebrew need right-to-left shaping (Godot 4's text server supports it).
- **Oracle:** a pseudo-localized build (accented, 40% longer strings) screenshotted on every menu, plus a
  test that every key exists in every language file.

## Accessibility
Start from the Game Accessibility Guidelines (gameaccessibilityguidelines.com) and the Xbox Accessibility
Guidelines. The cheap, high-value set:
- **Controls:** full remapping; hold-to-toggle alternatives; no required rapid button mashing.
- **Hearing:** subtitles with size, background and speaker names; visual cues for important sounds.
- **Colour:** never use colour alone to carry information (add shapes or icons); offer colour-blind
  palettes.
- **Motion and flashes:** screen shake and flash intensity sliders; no full-screen flashes faster than 3
  per second (WCAG's three-flash threshold).
- **Text:** UI scale and text size settings; readable fonts.
- **Difficulty:** assist options (more time, more health, skip a section) presented without judgement.
- **Oracle:** a checklist in `GAME_PLAN.md` with each item checked in a playtest, and a test that every
  rebindable action has a default binding on keyboard and gamepad.

## Performance
- **Budgets:** 16.6 ms per frame at 60 fps, 8.3 ms at 120, 33.3 ms at 30. Mobile also has a heat budget, so
  cap the frame rate.
- **Measure before optimizing:** the Godot debugger's Profiler and Monitors; Unity's Profiler and Frame
  Debugger; Unreal Insights, `stat unit` and `stat gpu`; browser DevTools Performance; Tracy for native and
  Bevy. Optimize the top item, then measure again.
- **CPU:**
  - no per-frame allocations (garbage collection spikes in C# and JavaScript);
  - pools for frequently spawned objects;
  - spatial partitioning (grid, quadtree, BVH) for proximity queries;
  - time-slice expensive work over frames, and update distant AI less often;
  - jobs and threads where the engine supports them (Unity Jobs + Burst, Bevy's parallel systems).
- **GPU:**
  - draw calls: atlases, instancing, batching;
  - overdraw from particles and transparent UI;
  - shader cost, shadow distance and cascades, post-processing;
  - texture memory: BCn on desktop, ASTC/ETC2 on mobile.
- **Stutter:** shader compilation hitches on first use. Warm shaders and pipelines during loading (Unity
  shader variant collections, Unreal PSO caching; recent Godot versions compile ubershaders up front). Use
  async loading for big assets.
- **Web:** download size (compressed textures and audio, code splitting), memory limits on mobile browsers,
  WebGL context loss.
- **Oracle:** a stress scene (worst-case enemy count, particles and UI) that logs average and P99 frame
  time headless or on the target machine, and fails above the budget. Shared CI runners are noisy: compare
  against the previous run on the same machine, not against an absolute.
