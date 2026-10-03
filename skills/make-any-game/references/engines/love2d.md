# LÖVE (Lua)

**Pick it when** the game is 2D and small-to-medium, the user likes Lua, and the goal is minimal ceremony:
three callbacks and you're drawing. Balatro shipped on LÖVE. **Think twice** for 3D, for the web (the love.js
port has been unmaintained since 2024), and for consoles.

Versions (October 2026): 11.5 is the latest stable; 12.0 is still unreleased.

## Identify
`main.lua` defining `love.load` / `love.update` / `love.draw`, and usually a `conf.lua`
(`t.version = "11.5"`).

## Setup
- Install LÖVE from https://love2d.org. `love .` runs the current folder. On Windows, `lovec.exe` keeps a
  console for `print` output (or set `t.console = true` in `conf.lua`).
- **Structure:** `main.lua` stays thin. Put states in `src/states/`, entities in `src/entities/`, and keep
  `src/sim/` pure Lua (no `love.*` calls) so it runs under a test runner without LÖVE.
- **Libraries** (vendor them into `lib/`):
  - anim8 (animations), bump.lua (AABB collision), STI (Tiled maps);
  - hump or knife (gamestate, timers, vectors), classic or middleclass (OOP);
  - push (resolution scaling).

## Commands
```bash
love .                                   # play (lovec . on Windows for console output)
love . --autotest smoke                  # your own flags arrive in love.load(arg)
busted spec/                             # tests for pure-Lua modules (busted via LuaRocks)
HEADLESS=1 love . --autotest sim         # a run with window/graphics disabled in conf.lua (below)
```
- **Headless runs:** in `conf.lua`, read an environment variable and switch off the window and graphics
  modules:
  ```lua
  function love.conf(t)
    t.version = "11.5"
    if os.getenv("HEADLESS") then t.modules.window = false; t.modules.graphics = false end
  end
  ```
  Your update loop must then tolerate `love.graphics` being absent, which is one more reason to keep the
  simulation pure.
- **Exit codes:** `love.event.quit(1)` exits with status 1, so autotests can fail CI.

## Debug hooks and oracles
- **Screenshots:** `love.graphics.captureScreenshot("shot.png")` writes to the save directory
  (`love.filesystem.getSaveDirectory()`).
- **Fixed timestep:** LÖVE's default `love.run` passes a variable `dt`. For determinism, accumulate it and
  step the simulation at 1/60 s. Clamp `dt` (dragging the window on Windows stalls the loop).
- **Agent bridge:** LuaSocket ships with LÖVE (`require "socket"`). Run a non-blocking TCP server on
  `127.0.0.1`, polled from `love.update`, or read commands from stdin when you launch the process.
- **Saves:** `love.filesystem.setIdentity("beacon")` puts them in `%APPDATA%\LOVE\beacon` (a fused game uses
  its own folder).

## Packaging
- **`.love`:** a zip of the game folder with `main.lua` at the zip root.
- **Windows:** fuse it, `copy /b love.exe+game.love game.exe`, and ship it with LÖVE's DLLs and
  `license.txt`.
- **macOS:** put `game.love` inside `love.app/Contents/Resources/` and edit `Info.plist`.
- **Linux:** an AppImage or a tarball.
- **makelove** automates all of these (love-release was archived in 2025).
- **Web:** love.js hasn't been maintained since 2024. If the web matters, test it early or pick a web-native
  engine.

## Pitfalls
- **Pixel art blurs** unless `love.graphics.setDefaultFilter("nearest", "nearest")` runs before any image
  loads.
- **Globals leak everywhere:** declare everything `local`.
- **LuaJIT is Lua 5.1:** no `//` integer division, and arrays start at 1.
- **`love.physics`** (Box2D) needs `love.physics.setMeter()` to match your pixel scale.
