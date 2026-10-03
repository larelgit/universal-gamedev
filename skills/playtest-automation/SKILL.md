---
name: playtest-automation
description: Let an agent verify its own game instead of guessing. Covers unit tests for game rules, headless simulation with scripted input, load-every-scene smoke tests, screenshots taken from inside the game, golden-image comparison, input record and replay, bot playthroughs, frame-time budgets, smoke-testing exported builds, CI, preparing human playtests, and an in-game agent bridge (JSON over localhost) to observe and act without pixels. Per-engine commands for Godot (GUT, gdUnit4), Unity (Test Framework in batchmode), Unreal (Automation), web (Vitest, Playwright), Bevy, LÖVE, pygame, MonoGame and native. Use whenever a game feature must be verified, a game bug reproduced, tests written for a game, a screenshot of the game taken, the game launched or driven automatically, or a playtest prepared.
---

# Playtest automation: the agent's eyes and hands

You can't watch the game run and you can't feel it. So build things that watch it for you, and save the
human's time for the one thing only they can judge: whether it's fun. The loop after every change is:
**run the cheapest oracle → read the result (logs, state dumps, screenshots you actually open) → decide.**

Owning the source changes the game: instead of clicking through menus from outside (as a modder must), you
can build the hooks into the game itself. Do that early. Every later change then checks itself in seconds.

## 1. Make the game testable (once, in the first session)
- **Separate rules from presentation.** Damage maths, inventory, scoring, card effects, level generation and
  AI decisions live in plain classes or functions that run without rendering. Nodes and GameObjects call
  them. That's the difference between millisecond unit tests and minutes of clicking.
- **Determinism switches:** `--seed <n>`, a fixed timestep, a fixed delta for tests, and seeded or disabled
  randomness in juice (shake offsets, particle spread) so golden images are stable.
- **Launch flags:** `--scene <name>`, `--autotest <script>`, `--screenshot <path>`, `--quit-after <frames>`,
  `--record <file>` / `--replay <file>`. Read them via Godot `OS.get_cmdline_user_args()` (arguments after
  `--`), Unity `System.Environment.GetCommandLineArgs()`, URL query parameters on the web, or `argv`.
- **A state dump:** one call that returns JSON for what matters (scene, player position, velocity and health,
  enemies, score, current state-machine states, UI focus). You read JSON far more reliably than pixels.
- **An in-game screenshot call** (per engine, in `references/per-engine.md`). It frames the game exactly,
  works in CI, and needs no OS permissions.
- **Logs to stdout and to a file**, with unmistakable result lines (`AUTOTEST PASS`, or `AUTOTEST FAIL:
  <reason>`) and a non-zero exit code on failure.

## 2. The oracle ladder: cheapest first
| Oracle | How | Catches |
|---|---|---|
| **Unit tests** | the engine's test framework on rule code | logic errors, edge cases |
| **Headless simulation** | run the real loop without rendering at a fixed delta; feed actions from a script by frame; assert on state dumps | movement, collisions, win/lose, softlocks |
| **Load-every-scene smoke test** | instantiate each scene or level, run 60 frames, fail on any logged error | missing resources, broken references, script errors |
| **Screenshot you look at** | in-game capture (or `um win shot`), viewed at reduced scale | scale, facing, layering, UI overflow, "is it on screen at all" |
| **Golden image** | fixed seed, camera and resolution; compare to an approved PNG with a tolerance (`ugd shot diff`, Playwright `toHaveScreenshot`) | visual regressions |
| **Input replay** | record a human's inputs per frame; replay deterministically and assert the outcome | levels that stop being completable |
| **Bots** | random "monkey" input for crashes; scripted or search bots for completability; heuristic bots for balance | rare crashes, softlocks, difficulty spikes |
| **Frame-time budget** | a stress scene logging average and P99 frame time | performance regressions |
| **Exported build smoke test** | build with the real export command, launch the artifact with `--autotest smoke`, check the exit code and log | export-only bugs: missing files, case-sensitive paths, stripped code, web headers |
| **Human playtest** | a build plus 2-4 specific questions | fun, clarity, feel |

Patterns that make these work:
- **Inject actions, not OS key events,** so tests run headless and can't type into other apps:
  - Godot: `Input.action_press("jump")` / `Input.action_release(...)`;
  - Unity: the Input System's `InputTestFixture`;
  - Unreal: Enhanced Input's `InjectInputForAction`;
  - Bevy: press keys on the `ButtonInput<KeyCode>` resource;
  - web: Playwright `page.keyboard`, or call your own `window.__game` API;
  - pygame and LÖVE: call your input handler directly.
- **Input scripts as data:** `[{"frame": 0, "down": "right"}, {"frame": 30, "down": "jump"}, {"frame": 34,
  "up": "jump"}]`. Assert on the state dump at given frames.
- **Softlock detector:** if the progress metric (distance, score, room id) doesn't change for N seconds, fail
  and dump the state.
- **Golden images need the same renderer.** Keep goldens per platform and renderer, have the human approve
  the first one, and never compare a CI software renderer against a local GPU. Turn off or seed everything
  random on screen.
- **See every new test fail once** (break the code, or assert the wrong value), so you know it can fail.

## 3. Per-engine commands
Versions move: pin the test framework version in the project, and check its README for the current
invocation.

| Engine | Tests | Headless | Notes |
|---|---|---|---|
| Godot 4 | GUT 9: `godot --headless -s addons/gut/gut_cmdln.gd -gdir=res://test -gexit` (from the project root, or add `--path`); gdUnit4: `addons/gdUnit4/runtest.sh -a res://test` (`.cmd` on Windows; needs `GODOT_BIN`) | `godot --headless --path . -- --autotest smoke` | `--headless` has no renderer: take screenshots with a display (or `xvfb-run` on Linux) |
| Unity 6 | `Unity -batchmode -nographics -projectPath . -runTests -testPlatform EditMode -testResults results.xml -logFile -` (then `PlayMode`) | `-batchmode -executeMethod <Class.Method>` | don't add `-quit` to `-runTests` (it exits before tests finish); close the editor first (one instance per project) |
| Unreal 5 | `UnrealEditor-Cmd <Project>.uproject -ExecCmds="Automation RunTests <Filter>;Quit" -unattended -nullrhi -nosplash -log -ReportExportPath=<dir>` | `-nullrhi` | functional tests and screenshot comparison live in the Automation system |
| Web | `npx vitest run` (logic), `npx playwright test` (game in a browser) | headless Chromium | expose `window.__game` for state; headless Chromium renders WebGL in software (SwiftShader), so keep test scenes small |
| Bevy | `cargo test` on an `App` (plus `MinimalPlugins` as needed), calling `app.update()` | the same | Linux CI needs `libasound2-dev libudev-dev` |
| LÖVE | busted (or any Lua test runner) on pure modules | `love . --autotest smoke` | |
| pygame-ce | `pytest` | `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy` | screenshots work headless |
| MonoGame / FNA | `dotnet test` on a logic project (xUnit/NUnit) | | the `Game` class needs a GPU: keep rules out of it |
| raylib / SDL / native | doctest, Catch2 or GoogleTest via `ctest` | SDL dummy video driver | |
| Ren'Py | `renpy.sh <project> lint`; `renpy.sh <project> test` runs `testcase` blocks (Ren'Py 8.5+) | | plus a scripted traversal of choices |

Setup details, input injection, screenshot code and state dumps per engine: `references/per-engine.md`.

## 4. The agent bridge: observe and act without pixels
A tiny command server inside **dev builds** of the game, the same idea as the agent bridge in
universal-modder's Terraria example, but simpler, because you own the code. It speaks JSON lines on
`127.0.0.1`:
```json
{"cmd": "observe"}                                  → {"scene": "level_1", "frame": 1840, "player": {...}, "enemies": [...], "ui": {...}}
{"cmd": "press", "action": "jump", "frames": 6}     → {"ok": true}
{"cmd": "step", "frames": 30}                       → {"ok": true, "frame": 1870}
{"cmd": "screenshot", "path": "shots/after_jump.png"}
{"cmd": "load", "scene": "level_2", "seed": 7}
```
- Handle each request on the main thread after an update, so replies are consistent.
- Whitelist commands. No arbitrary code evaluation, and leave destructive operations out.
- Bind to `127.0.0.1` with a token, compile it into dev builds only, and make sure release builds don't
  contain it (`ugd release check` looks for leftover debug servers).
- Some engines ship one already:
  - **Unreal:** the Remote Control API plugin (HTTP/WebSocket on localhost);
  - **Bevy:** the Bevy Remote Protocol (`RemotePlugin` + `RemoteHttpPlugin`, JSON-RPC);
  - **web:** `page.evaluate(() => window.__game.observe())` in Playwright *is* the bridge.

  Elsewhere, write a small `TCPServer` (Godot autoload), a `TcpListener` with a main-thread queue (Unity), or
  use stdin/stdout when you launch the process yourself.
- With a bridge, an agent can play the game: observe → decide → act → step. That makes bots, replays and
  repro scripts cheap.

## 5. Outside-in: drive the built game
When the in-game hooks can't reach something (the real exported `.exe`, fullscreen switching, gamepad
hot-plugging), drive the build from outside. On Windows, use universal-modder's `um win`:
```bash
um win launch "build\windows\Game.exe" -- --scene level_1    # start the build
um win ps                                                     # windowed processes: pid, name, title
um win shot --exe Game.exe shots\menu.png --scale 0.33        # GPU-safe capture of that window + a cheap 1/3 copy
um win drive --proc Game idle                                 # seconds since the user last touched the mouse/keyboard
um win drive --proc Game "focus" "key 0x0D" "hold 0x44 800"   # input that only reaches the game window
um win kill <pid>                                             # exact PID only
```
- **Linux:** `xvfb-run -a ./game --autotest smoke`, `xdotool` for input, `import -window` for screenshots.
- **macOS:** `screencapture -l <windowid>`; needs Screen Recording permission for the terminal.
- **Driving input takes over the user's machine.** Check `idle` first, ask before long runs, and prefer
  in-game injection whenever it can do the job.

## 6. CI
- Run unit tests, headless simulations and smoke tests on every push. Upload screenshots and diff images as
  artifacts when something fails.
- **Per engine:**
  - Godot: download a pinned headless Godot in the workflow, or use a setup action;
  - Unity: GameCI, which needs the user's Unity license as repository secrets, so ask them;
  - Unreal: usually a self-hosted runner;
  - web: Playwright with `npx playwright install --with-deps chromium`;
  - Rust: cache `target/`;
  - Python: pytest with SDL's dummy drivers.
- Cache the import caches (Unity `Library/`, Godot `.godot/`), or CI will spend most of its time importing.

## 7. Human playtests
- **Prepare:** a build or web link, what to try, 2-4 questions with 1-5 scales ("How readable were enemy
  attacks?"), known issues, and how to report (a screenshot and the time).
- **Listen for** where they got stuck, what they ignored, and what surprised them. Ask follow-ups; don't
  defend the design.
- **Log the answers** in `DEVLOG.md` under a dated "Playtest" heading. Turn them into tunable changes, and
  ask the same questions again after the change.

## Rules of the road
- **Look at every screenshot you take,** at reduced scale. Describe what you see before claiming success.
- **Circuit breaker:** after 3 identical failures, stop, write down what you know, and change approach or
  ask.
- **Processes:** kill only processes you started, by PID. Close editors that hold project locks before
  batch runs. Don't leave headless engines, servers or recorders running.
- **Bridges, debuggers and dev servers** bind to `127.0.0.1`, exist in dev builds only, and never ship.
