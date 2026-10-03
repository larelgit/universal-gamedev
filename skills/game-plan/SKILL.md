---
name: game-plan
description: Turn a game idea into a one-page plan before building anything. Covers the pitch, core loop, controls, the vertical slice to build first, scope and cut list, engine choice, art and audio style bible, and the tech and test plan. Also fingerprints an existing game project (engine and version, language, layout, how to run, test and export it). Use when the user asks "which engine should I use?", "help me plan / scope / design my game", "write a GDD", "is this idea doable in a weekend?", "what is this project and how do I run it?", or at the start of any new game, even if they jump straight to "make me a game". Produces GAME_PLAN.md.
---

# Game plan

Goal: in about ten minutes, decide what to build first and with what, and write it down so every later
step, and every later session, can rely on it. A short plan beats a long design document: the vertical
slice will teach you more than any amount of up-front design.

## 0. Has another agent built something like this?
`ugd kb search "<genre>"` and `ugd kb search "<engine>"`. A field note can hand you a working engine version,
an architecture, and the gotchas that cost the last agent hours. See the **gamedev-field-notes** skill.

## 1. Existing project? Fingerprint it first
```bash
ugd scan .            # engine + version, language, tests, CI, run/test/export commands, the playbook to read
ugd scan . --json     # the same, machine-readable
ugd scan --tools      # which engines, SDKs and runtimes are installed on this machine
```
`ugd` lives at `bin/ugd` in this repo (plugins and clones put it on PATH). Without it, look for the marker
files by hand:

| Marker | Engine | The version is in |
|---|---|---|
| `project.godot` | Godot | `config/features=PackedStringArray("4.x", ...)` |
| `ProjectSettings/ProjectVersion.txt` + `Assets/` | Unity | `m_EditorVersion` |
| `*.uproject` | Unreal | `"EngineAssociation"` |
| `Cargo.toml` depending on `bevy` (or `macroquad`, `ggez`) | Rust engines | the dependency version |
| `package.json` depending on `phaser`, `three`, `pixi.js`, `@babylonjs/core`, `kaplay`... | web | the dependency version |
| `main.lua` (+ `conf.lua`) | LÖVE | `t.version` in `conf.lua` |
| Python importing `pygame` / `arcade` / `pyxel` / `ursina` | Python | `requirements.txt` / `pyproject.toml` |
| `*.csproj` referencing `MonoGame.Framework.*`, FNA or KNI | .NET | the package reference |
| `*.yyp` | GameMaker | `"IDEVersion"` in the `.yyp` metadata |
| `game.project` | Defold | the editor/bob version used to build |
| `game/*.rpy` | Ren'Py | the SDK it was built with |
| `CMakeLists.txt` finding `raylib`, `SDL3`, `SFML` | native | `find_package` / `FetchContent` tags |

Then read the README and build scripts, find the commands that run, test and export the game, **run the
existing tests and note how many already fail**, and note the conventions (folders, naming, code style).
Write all of this under "Project facts" in `GAME_PLAN.md`, then read the engine playbook
(`skills/make-any-game/references/engines/`).

## 2. Find the core
- **Pitch:** one sentence, usually "it's <genre> where you <twist>".
- **Core verbs:** the 1-3 things the player does constantly (jump, shoot, place, match, talk).
- **Loops:** the moment-to-moment loop (5-30 s: "dodge → shoot → collect → upgrade"), the session loop (a
  level, a run, a day) and the long loop (unlocks, story, mastery).
- **Win, lose and feedback:** how the player fails, how fast they retry, and what tells them they're
  getting better.
- **Pillars:** two or three words that settle design arguments ("fast, readable, chaotic").
- **Reference games:** for mechanics and feel only. Names, art, music and levels stay original (see
  `skills/make-any-game/references/rules.md`).
- **The first minute:** what the player sees and does in the first 60 seconds, and how it teaches the core
  verb without a wall of text.

## 3. Choose the engine
If the user already has an engine or a project, use it. Otherwise, recommend one with reasons and let them
decide.

| Criterion | Ask |
|---|---|
| Targets | Desktop, web, mobile? Consoles need approved developer accounts and usually Unity, Unreal, or Godot via a porting partner. |
| 2D or 3D | Pixel art and 2D suit Godot, Phaser, LÖVE and pygame. High-end 3D suits Unreal or Unity. Stylised 3D suits Godot, Unity or three.js. |
| Language | What does the user know, or want to learn? |
| Agent-friendliness | Text scenes and data, CLI run/test/export, a headless mode (table below). |
| Existing assets | Asset Store or Fab purchases, an existing codebase. |
| License and cost | Godot is MIT. Unity and Unreal have EULAs with revenue thresholds or royalties. Check the current terms. |
| Install size | Godot is ~100 MB; Unity with platform modules is 10+ GB; Unreal is 50-100+ GB. |

**Agent-friendliness**, the property that decides how well you can verify your own work:

| Engine | Scenes/data as text | CLI run, test, export | Headless | Caveats for agents |
|---|---|---|---|---|
| Godot 4 | yes (`.tscn`, `.tres`) | yes | yes (`--headless`; no rendering, so no screenshots) | match the editor version exactly |
| Web: Phaser, three.js, PixiJS | yes (it's all code) | yes (npm scripts) | yes (Playwright) | browser quirks: audio unlock, WebGL in CI |
| Bevy | yes (code) | yes (`cargo`) | yes (`MinimalPlugins`) | long first compile; breaking changes between releases |
| LÖVE | yes | yes | partly | packaging per platform is manual |
| pygame-ce | yes | yes | yes (SDL dummy driver) | 3D isn't its thing |
| MonoGame / FNA | yes (code + `.mgcb`) | yes (`dotnet`) | logic only | content pipeline step |
| Unity 6 | YAML with GUIDs and fileIDs (don't hand-edit scenes) | yes (`-batchmode`) | yes (`-nographics`) | big install, license activation, editor scripts or MCP for scene work |
| Unreal 5 | binary `.uasset` | yes (UAT, `UnrealEditor-Cmd`) | yes (`-nullrhi`) | huge install, C++ compile times, Python editor scripting or MCP for assets |
| GameMaker | `.yy` JSON | partly | no | IDE-centric |
| Ren'Py | yes (`.rpy`) | yes (lint, distribute) | partly | narrative only |

The default picks by situation are in `skills/make-any-game/SKILL.md` (step 1). The details per engine are
in its playbook.

## 4. Scope
- **The vertical slice:** the smallest playable build that proves the core loop is fun. One arena or level,
  one enemy type, the core verb, graybox art, win and lose. A few hours to a day of work.
- **MVP:** what a complete, small version of the game needs. **Later:** nice-to-haves. **Cut:** written down
  now, so cutting later is a decision rather than a failure.
- **Scope by time box:**
  - a 48-hour jam is one mechanic, one level type and 5-10 minutes of play;
  - a month is a small complete game with one hour of content;
  - anything longer is phased in milestones, each ending in a build.
- Everything takes 2-3× longer than planned, and late in a project content (levels, art, audio, balance)
  dominates the time, not code.

## 5. Style bible (art and audio direction)
Write it before generating a single asset. Consistency comes from these decisions:
- **2D:**
  - **Base resolution.** For pixel art that scales to 1080p by whole numbers: 320×180 (×6), 384×216 (×5),
    480×270 (×4) or 640×360 (×3).
  - **Grid and palette:** tile size (8, 16 or 32 px) and a palette (a named Lospec palette, or N colours).
  - **Look:** outline (none, dark 1 px, coloured), light direction (usually top-left) and perspective
    (side, top-down 3/4, isometric 2:1).
  - **Animation:** frame counts (idle 4, run 6-8, attack 4-6 at 8-12 fps for pixel art).
- **3D:** the look (flat-shaded low-poly, toon, PBR), polygon and texture budgets, texel density, a shared
  palette texture or material library, and scale (1 unit = 1 m).
- **UI:** fonts (OFL-licensed), the colour roles, and icon style.
- **Audio:** music genre, tempo and mood per area; SFX style (chiptune, foley, synth); a loudness target.
- **Sources:** generated with fal (the game-assets skill), hand-made, or store/CC0 packs. Plan the credits.
  **Check jam rules:** many jams ban AI-generated assets.

## 6. Tech and test plan
- Structure: folders, the tuning data file, the save format, the input action list.
- Debug hooks: launch flags (`--scene`, `--seed`, `--autotest`), a dev console or cheats, state dumps, the
  agent bridge (the playtest-automation skill).
- **The oracle plan:** for each milestone, the check that proves it (unit tests for rules, a headless
  simulation for movement, screenshots for the UI, specific questions for the human).
- Builds: which targets to export, and when (the first one in the first session).
- **Risks → spikes:** each unknown gets a time-boxed experiment on day one ("Can a Godot web build keep 500
  enemies at 60 fps on a laptop?").

## 7. Write GAME_PLAN.md
```markdown
# <Title>: game plan
- Pitch: <one sentence>   Pillars: <2-3 words>
- Platforms: <desktop / web / mobile>; input: <keyboard+mouse, gamepad, touch>
- Engine: <engine + exact version>, because <reasons>; also considered: <...>
- Loops: <moment-to-moment> → <session> → <long-term>
- Controls: <action → keys / buttons>
- Win / lose / retry: <conditions; time to retry>
- Vertical slice: <list>; done when: <oracle> + playtest questions: <2-4 questions>
- MVP: <list>   Later: <list>   Cut: <list>
- Style bible: <resolution/PPU, palette, outline, camera, light, frame counts, fonts>
- Audio: <music direction, SFX style, loudness target>
- Assets: <generated (fal) / hand-made / store or CC0>; credits in CREDITS.md
- Tech: <structure, tuning file, save format, debug hooks>
- Commands: run `<...>` | test `<...>` | export `<...>`
- Oracles: <per milestone>
- Risks → spikes: <list>
- Accessibility: <the items you'll ship>
- Project facts (existing projects): <engine/version, layout, tests passing/failing before changes, conventions>
```
Then continue with the make-any-game loop: project setup, then the vertical slice.
