# Narrative: Ren'Py, Ink, Yarn Spinner, Twine, RPG Maker MZ

Story-heavy games are unusually agent-friendly: the content is text, and the oracle is a graph traversal
that visits every branch.

## Ren'Py (visual novels)
Versions (October 2026): 8.5.x. The automated testing framework (`testcase` / `testsuite`) arrived in 8.5.0.
- **Layout:** `game/script.rpy` (labels, dialogue, menus), `game/options.rpy` (config), `gui.rpy`,
  `screens.rpy` (screen language), and `game/images/` (files are declared automatically by name).
- **Commands** (`renpy.sh` on Linux/macOS, `renpy.exe` on Windows, from the SDK):
  ```bash
  renpy.sh <project> lint                     # static checks: missing images, bad jumps, unreachable labels
  renpy.sh <project> test                     # run testcase blocks (Ren'Py 8.5+)
  renpy.sh launcher distribute <project>      # build PC, Mac and Linux distributions
  ```
  Web and Android builds come from the launcher (the web build and RAPT).
- **Variables:** `default` for state that changes (it's saved and rolls back correctly); `define` for
  constants. Mixing them up breaks saves and rollback in subtle ways.
- **Python blocks** (`init python:`, `$ ...`) should only change Ren'Py's store, so rollback stays correct.
- **Oracle:** lint on every change, testcases that click through the critical paths, and a traversal of
  every menu choice (your own script, or testcases that pick each option).
- **Pixel art:** `define config.nearest_neighbor = True`.

## Ink (inkle), inside any engine
- Write `.ink` files in Inky or any editor, then compile them to JSON with `inklecate`.
- **Runtimes:** ink-unity-integration (C#), inkjs (web), godot-ink (Godot C#) or inkgd (GDScript).
- **Oracle:** drive the runtime headless: `Continue()` until there are choices, then `ChooseChoiceIndex(i)`
  for every option, depth-first (or random walks for big stories). Assert there are no dead ends or runtime
  errors, and that every knot is visited. Count visits to find unreachable content.

## Yarn Spinner
- `.yarn` dialogue files with nodes, options and commands.
- Official Unity integration; Godot support through Yarn Spinner for Godot (C#).
- Commands (`<<give_item sword>>`) call into your game code. Keep them in one registry, so tests can stub
  them.
- **Oracle:** the same traversal idea: run the dialogue runner headless and pick every option.

## Twine
- Story formats: Harlowe, SugarCube, Chapbook. Write in Twee 3 (plain text) and compile with Tweego, which is
  the agent-friendly route.
- The output is a single HTML file: Playwright can click through links as a traversal oracle.

## RPG Maker MZ (and MV)
- A commercial editor (the user buys it). The engine is JavaScript (NW.js): plugins in `js/plugins/*.js`,
  registered in `js/plugins.js`; the database in `data/*.json` (Actors, Items, Skills, Maps, CommonEvents).
- **Agent workflow:** write plugins freely (plain JS). Edit the JSON database only while the editor is
  closed, because the editor overwrites the files on save. Map events are JSON too, but complex; let the
  human build events in the editor.
- **Testing:** playtest from the editor. A web deployment runs in a browser, so Playwright can drive it for
  smoke tests.
- Asset licenses: the bundled RTP assets are licensed for use in games made with that RPG Maker version.
  Read the EULA before mixing them elsewhere.
