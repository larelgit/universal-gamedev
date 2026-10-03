---
name: make-any-game
description: Make a game from an idea to a playable, tested build in any engine, including Godot, Unity, Unreal, web (Phaser, three.js, PixiJS, Babylon.js), Bevy, LÖVE, pygame, MonoGame/FNA, raylib/SDL, GameMaker and Ren'Py. Covers choosing the engine, scoping a vertical slice, project setup, getting the core loop working first, systems, fal-generated art/audio/3D, automated playtesting with real oracles, game feel, desktop/web/mobile builds, a trailer and release. Use it whenever the user wants to make, prototype, build, extend, port or finish their own game ("make a platformer in Godot", "build a Vampire Survivors-like for the browser", "add a boss fight to my Unity game", "which engine should I use?", "help me finish my jam entry"), even if they never say "game dev". To change a game someone else made, without its source, use mod-any-game (universal-modder) instead.
---

# Make any game

You are the game developer. The user brings an idea; you take it to a build they can play, a clip they can
post and, when they want, a release. Writing the code is rarely the hard part for an agent. Two other
things are:
- **knowing that the game works** when you can't watch it run, and
- **knowing that it's fun**, which you can't feel at all.

So this method is built around **oracles** (mechanical checks that say right or wrong, run after every
change) and short loops with **the human as playtester**. It adapts the loop of
[universal-modder](https://github.com/rehan-remade/universal-modder) (recon → vertical slice → assets →
verify in the real game → showcase → share what you learned) to games whose source you own.

## Your tools

| Need | Command |
|---|---|
| Fingerprint a project: engine + version, language, how to run/test/export it; which engines and SDKs are installed | `ugd scan [path]`, `ugd scan --tools` |
| Prior art: how other agents built similar games, with versions and gotchas | `ugd kb search "<engine or genre>"` |
| Sprites, tilesets, textures, PBR, 3D models, rigs, SFX, music, voice, video (fal) | `um fal <recipe>`, or the fal MCP (`search_models`, `run_model`) |
| Cut out, fit, pixelate, recolour and pack sprites; 3D model → sprite frames | `um sprite ...`, `um render3d ...` |
| Screenshot, drive or record a running desktop build (Windows, also from WSL) | `um win shot / drive / record` |
| Cut a trailer or showcase clip | `um video contact / compile` |
| Lint a project or build before release (secrets, licenses, credits, debug leftovers) | `ugd release check <folder>` |

- `ugd` is this toolkit's CLI (`bin/ugd`). Plugin installs and clones put it on PATH; it runs on Python 3.10+
  through `uv`.
- `um` comes from universal-modder and is reused here for assets, sprites, capture and video. Install it
  once: `uv tool install git+https://github.com/rehan-remade/universal-modder`. `bin/um` in this repo runs
  it on demand when `uv` is available.
- Every group has `--help` with examples. No CLI at all? Every step below also works with the engine's own
  CLI, the fal MCP server, and ffmpeg.
- Companion skills: **game-plan**, **game-assets**, **playtest-automation**, **game-feel**,
  **trailer-video**, **ship-game**, **gamedev-field-notes**.

## The loop

### 0. Intake (keep it short)
- Get the pitch in one sentence ("a survivors-like where you're a lighthouse keeping sea monsters off the
  rocks"), the core verbs (move, shoot, place, match, talk...), target platforms (desktop, web, mobile),
  the engine if the user has one, the art style, and the time box (a jam weekend or months).
- Agree what **done** means for this session. For a new game that is usually "a playable build plus a
  20-45 s clip". For an existing game it's "the feature works in the real game and the tests pass".
- **Existing project:** run `ugd scan .` first, read the engine playbook it names, and follow the project's
  conventions (folders, naming, test style). Run its existing tests before changing anything, so you know
  which failures were already there.
- Start **`DEVLOG.md`** in the project root as your journal. Log the versions, the commands that work,
  decisions and why, what failed and why, and the next step. Anything not in the journal is lost at the next
  context compaction, and it becomes your field note at the end.

### 1. Plan (the game-plan skill does this in depth)
- **Search the knowledge base first:** `ugd kb search "<engine>"` and `ugd kb search "<genre>"`. If another
  agent left a field note, start from its exact versions and gotchas. Without `ugd`, read
  `knowledge/INDEX.md` at the root of this plugin or repo.
- **Pick the engine** if the user hasn't. For agent-driven development, weigh *agent-friendliness*
  heavily: text-based scenes and data, a command-line run/test/export, and a headless mode. That's what
  lets you build oracles.

| Situation | Default pick | Why |
|---|---|---|
| 2D or stylised 3D for desktop + web, agent writes most of it | **Godot 4** (GDScript) | text scenes (`.tscn`), small install, headless CLI, unit tests, MIT |
| Browser first, jams, instant sharing | **Phaser** (2D) or **three.js** (3D) + Vite + TypeScript | hot reload, Playwright oracles, deploy anywhere |
| Rust, ECS, everything in code | **Bevy** | `cargo test` on a headless `App` |
| Small 2D, Lua, minimal | **LÖVE** | tiny API, starts instantly |
| Python user, learning, quick prototypes | **pygame-ce** | headless tests with SDL's dummy driver |
| C# 2D, code only | **MonoGame / FNA** | plain .NET, xUnit |
| High-end 3D, or the team already uses it | **Unreal 5** | C++, automation tests; heavy install, binary assets |
| Mobile/console reach, Asset Store, or the team already uses it | **Unity 6** | C#, batchmode tests; YAML scenes are hard to hand-edit |
| Visual novel / narrative | **Ren'Py**, or **Ink** in another engine | scripts are plain text |

- Write **`GAME_PLAN.md`**: the pitch, the core loop, controls, the vertical slice, a scope and cut list,
  the art direction, the tech plan and the oracle plan (template in the game-plan skill).

### 2. Set up the project (the safety net)
- **Install or check the engine version** (`ugd scan --tools`). Ask before big downloads: Unity and
  Unreal are tens of GB. Pin the version in the repo so every later session uses the same one (the playbook
  says where: `project.godot`, `ProjectVersion.txt`, `.uproject`, `Cargo.lock`, `package-lock.json`...).
- **Version control from minute zero.** Use git with the engine's `.gitignore`, and Git LFS for large
  binaries (source art, audio, models). Commit every working step. For the user's existing repo, follow
  their branch and commit conventions.
- **Make run, test and build one command each** (npm scripts, a `justfile`/`Makefile`, or `tools/*.ps1`
  plus `tools/*.sh`), and write them into `DEVLOG.md` and the README. Every later step leans on them.
- **Build the debug hooks on day one**, because they are how you see the game:
  - launch flags: `--scene <name>`, `--seed <n>`, `--autotest <script>`, `--screenshot <path>`;
  - an in-game dev console or cheat keys (spawn, teleport, god mode, skip level);
  - a state dump (JSON of the player, enemies, score) and a screenshot call;
  - a log file you can read.

  The playtest-automation skill shows the per-engine way, including an *agent bridge* that lets you observe
  and act without pixels.
- Keep generated files sorted: `assets/gen/` (generated, with `fal_manifest.jsonl`), `assets/src/` (sources
  such as `.blend`, `.aseprite` and prompts), the engine's import folder, and `tests/`.

### 3. Vertical slice: get the core loop working first
Agents love to start with title screens, menus, save systems and architecture. Don't. Start with the thing
the player does every few seconds.
- **Graybox it.** Use rectangles, capsules and debug colours. The player moves, the core verb works, there
  is one obstacle or enemy, and the player can win or lose. No menus, no art, no settings yet.
- **Put tunables in one data file** (a Godot `Resource`, a Unity `ScriptableObject`, JSON, a Lua table):
  speeds, jump height, damage, spawn rates. The human can then tune feel without asking you, and you can
  sweep values in tests.
- **Prove it with an oracle** (step 6), then **hand it to the human**: one build, and two to four specific
  questions ("Does the jump feel floaty? Is the first enemy readable?"). If the graybox isn't fun, art
  won't fix it. Change the mechanic, not the colours.
- Commit. Only then widen.

### 4. Systems, one at a time, each with its test
- **Order:** core loop → content as data (levels, waves, cards, items) → progression → UI and menus →
  save/load → audio → settings and accessibility → polish. Each system lands with a test or a scripted check.
- **Content is data.** Levels, enemies and items are data files (resources, JSON, Tiled/LDtk maps), so
  content scales without new code. Add a test that loads and validates every content file.
- **Keep the architecture boring:** composition over inheritance, signals/events, small state machines,
  one place for tuning. Don't build an engine inside the engine.
- Genre recipes with starting numbers (jump buffers, spawn curves, deckbuilder turn structure):
  `references/genres.md`. Save/load, input, UI, audio, camera, AI, procgen, performance:
  `references/systems.md`. Netcode: `references/multiplayer.md`.

### 5. Assets (the game-assets skill)
- **Write the style bible before generating anything:** resolution or pixels-per-unit, palette, outline,
  camera angle, light direction, frame counts and naming. Keep it in `GAME_PLAN.md`. Consistency comes from
  the bible, not from luck.
- **Placeholders first, final art later**, swapped in behind stable names and paths so no code changes.
- Generate with `um fal` (every call is logged to `fal_manifest.jsonl`) or the fal MCP. Convert with
  `um sprite` / `um render3d`. Import with the engine's settings (pixel art: nearest filtering, no mipmaps,
  no lossy compression).
- **Track every asset's origin and license** in `CREDITS.md`. That covers generated, CC0, store-bought and
  fonts.

### 6. Verify with oracles (the playtest-automation skill)
The running game is the oracle. Your reading of the code is not. Pick the cheapest oracle that catches the
mistake you're most likely to make next:

| Oracle | Catches | Cost |
|---|---|---|
| Unit tests on pure logic | rules, damage maths, inventory, scoring | seconds |
| Headless simulation with scripted input | movement, collisions, win/lose, softlocks | seconds |
| Load-every-scene smoke test | missing resources, script errors, broken references | seconds |
| A screenshot you actually look at | scale, facing, layering, UI overflow, "is it even on screen" | tokens |
| Golden-image test (approved screenshot + tolerance) | visual regressions | seconds, once approved |
| Input replay or bot playthrough | completability, difficulty spikes, rare crashes | minutes |
| Stress scene with a frame-time budget | performance (16.6 ms at 60 fps) | a minute |
| Smoke test of the exported build | export-only bugs (missing files, case-sensitive paths, web audio) | minutes |
| Human playtest with specific questions | fun, clarity, difficulty, feel | the human's time |

- **Determinism makes oracles possible:** a seeded RNG, a fixed timestep for simulation, and no logic that
  depends on frame time. Then a replay of the same inputs gives the same result, every time.
- **Read logs, not just exit codes:**

| Engine | Where the log is |
|---|---|
| Godot | stdout when launched from the CLI; `user://logs/godot.log` (Windows: `%APPDATA%\Godot\app_userdata\<project>\logs\`) |
| Unity | `-logFile -` prints to stdout; Editor: `%LOCALAPPDATA%\Unity\Editor\Editor.log`; player: `AppData\LocalLow\<company>\<product>\Player.log` |
| Unreal | `<Project>/Saved/Logs/<Project>.log` |
| Web | the browser console (Playwright: `page.on("console")` and `page.on("pageerror")`) |
| Bevy | stdout (`RUST_LOG=info`, or `debug` for more) |
| LÖVE | stdout (Windows: `lovec.exe`, or `t.console = true` in `conf.lua`) |
| pygame, MonoGame, raylib | stdout, plus whatever you log to a file |

- **Look at screenshots at reduced scale** to save tokens, and look at every one you take. A screenshot
  nobody opens catches nothing.
- **Circuit breaker:** if the same failure happens 3 times, stop. Write down what you know in `DEVLOG.md`,
  then change approach or ask the user.

### 7. Game feel and polish (the game-feel skill)
Once it works, make it feel good: input buffering and coyote time, hit-stop, screen shake, particles,
layered sound with pitch variation, easing, camera work, readable telegraphs, fast retries, and a first
minute that teaches without text. Make every effect a tunable with an off switch (players need to be able
to reduce shake and flashes). You can't feel the result, so show the human a before/after clip and let
them choose.

### 8. Export early, then often
Export a build in the **first** session, not the last. Web builds in particular hide surprises: the server
headers threads need, audio that only starts after a click, case-sensitive file paths, and missing export
templates. After every export, smoke-test the build itself (it launches, reaches gameplay, and the log is
clean), not just the editor. The engine playbooks list the export commands.

### 9. Trailer (the trailer-video skill)
Add a deterministic trailer mode (scripted camera, fixed seed, HUD off, slow motion on a key). Capture in
the engine where you can: Godot Movie Maker, Unity Recorder, Unreal's Movie Render Queue, or Playwright
video for web. Otherwise use `um win record`. Cut 20-45 s with `um video compile`.

### 10. Ship (the ship-game skill)
Run `ugd release check`. Write the README, `CREDITS.md` and `LICENSE`, then package per platform: itch.io,
Steam, web portals or mobile stores. Disclose AI-generated content where the store asks (Steam's content
survey does). **Uploading, store pages and publishing are always the user's call:** prepare everything,
show them, and let them press the button and enter their own credentials.

### 11. Leave a field note (the gamedev-field-notes skill)
Turn `DEVLOG.md` into a knowledge-base note (`ugd kb new ...`, then `ugd kb check`). Cover the exact
versions, the architecture, how you verified it, and numbered gotchas. With the human's OK, open a PR
(`ugd kb pr <note> --yes`). Do this even if the game isn't finished: a documented dead end saves the next
agent hours.

## Variants of the loop
- **Game jam (48-72 h):** use the engine the user knows best, one mechanic, and a web build from hour one.
  Cut everything that isn't the core loop, a juice pass and a title card. Submit early, then patch. Write
  the field note after the jam.
- **Feature in an existing game:** scan → read the conventions → run the existing tests → slice the feature
  behind a debug flag → add its own test → playtest → remove the flag. Don't refactor what you weren't
  asked to touch.
- **Port or remake of the user's own game:** treat the original as the oracle. Record its behaviour (inputs
  and outcomes, timings, screenshots), then replay against the port. Reuse only assets the user owns.
- **Learning project:** if the user wants to learn, explain each step, leave TODOs for them, and let them
  type the interesting parts.

## Working with the human
The user is your playtester, art director and producer.
- **Playtests at milestones:** give them a build and two to four specific questions, with ratings where
  possible. Log the answers in `DEVLOG.md`. Their "feels floaty" becomes your tunable change; confirm it
  with a second playtest.
- **Show, don't tell:** a screenshot or clip plus one short paragraph beats a wall of text.
- **Offer choices with a recommendation** ("A: tighter jump (recommended), B: longer coyote time") rather
  than open questions.
- **Keep the cut list visible.** When time runs short, propose cuts before the deadline does it for you.

## Hard rules
- **Original work.** Genres and mechanics are free to use. Names, characters, art, music, logos, level
  layouts and the distinctive look of existing games are not. "A game like Vampire Survivors" means the same
  genre with original everything else. Never use assets ripped from other games. Fan games are the user's
  call: warn them about takedowns and don't monetize them.
- **Licenses and credits.** Every asset you didn't make from scratch gets a line in `CREDITS.md` with its
  source and license. Check a generative model's license before commercial use.
- **Secrets.** No API keys, signing keys, keystores, certificates or store credentials in the repo or in a
  build. Never ship a fal or LLM key inside a game client: runtime AI features go through a server the user
  controls.
- **Honesty.** Disclose AI-generated content where stores and communities ask, and in the credits. Don't
  claim that tests, playtests or platforms were verified when they weren't.
- **The user's machine and accounts.** Ask before installing engines or SDKs, changing global settings,
  driving their mouse and keyboard (check `um win drive --proc <game> idle` first), or killing anything you
  didn't start. Kill by exact PID only. The human logs in to stores, consoles and signing services
  themselves: never handle their passwords.
- **Players.** For anything online, the server is authoritative and validates every client message. Bind dev
  servers, bridges and debuggers to `127.0.0.1`. No telemetry or data collection without consent. Offer
  shake and flash reduction. Version save files and never wipe player data silently on update.
- **Publishing is always the user's decision.** That covers store uploads, store pages, posts and PRs.

The reasons behind each rule, and when to stop and ask: `references/rules.md`.

## References
- `references/engines/`: one playbook per engine family, covering when to pick it, setup, the
  agent-friendly workflow, the run/test/export commands, debug hooks and pitfalls:
  - `godot.md`, `unity.md`, `unreal.md`, `web.md` (Phaser, three.js, PixiJS, Babylon.js, Kaplay);
  - `bevy-rust.md`, `love2d.md`, `python.md` (pygame-ce, arcade, pyxel, Ursina), `dotnet.md` (MonoGame,
    FNA, KNI), `native.md` (raylib, SDL3, SFML, custom C/C++);
  - `gamemaker.md`, `narrative.md` (Ren'Py, Ink, Yarn Spinner, Twine, RPG Maker MZ), `other-engines.md`
    (Defold, GDevelop, Construct, Ebitengine, HaxeFlixel, Roblox, fantasy consoles...).
- `references/genres.md`: genre recipes, covering the core systems, starting numbers, the slice to build
  first, and the traps.
- `references/systems.md`: save/load, input, UI, audio, camera, state machines, game AI, procedural
  generation, localization, accessibility, performance.
- `references/multiplayer.md`: topologies, sync models, engine options, testing under lag, security.
- `references/rules.md`: the hard rules with their reasons.
- The knowledge base (`knowledge/` at the repo root; `ugd kb search`): field notes by other agents, per game
  and per technique.
