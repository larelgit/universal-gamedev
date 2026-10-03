# Other engines and platforms, quick routes

Short notes for engines without their own playbook. The method (the make-any-game loop, oracles,
`DEVLOG.md`) is the same everywhere. What changes is how much of the project is text and what runs from the
command line. Check each engine's current docs for exact commands.

## Defold (Lua)
- Free, from the Defold Foundation; strong on web and mobile, with small builds.
- **Files:** `game.project` (INI), plus `.collection`, `.go`, `.gui` and `.script` files. Most are protobuf
  *text* formats, so they're diffable and carefully editable.
- **Builds from the command line with bob.jar** (Java):
  `java -jar bob.jar --platform x86_64-win32 --archive --bundle-output build/ resolve build bundle`
  (set `--platform` per target).
- **Oracle:** pure Lua modules tested outside the engine; in-engine smoke runs via a test collection loaded
  by a launch flag.

## GDevelop
- Open-source and no-code (event sheets), with a JSON project file (`game.json` with `gdVersion`).
- Events are JSON, so an agent *can* edit them, but structures are deep. Prefer that the human edits events
  in the editor; the agent writes JavaScript code events and extensions, and reviews logic.

## Construct 3
- Browser-based and no-code; projects are `.c3p` zips or folder projects (`project.c3proj`). A subscription
  is needed for full use.
- Agents help most through Construct's JavaScript scripting feature and by planning event logic for the human
  to enter.

## Ebitengine (Go)
- A 2D library: `go.mod` requires `github.com/hajimehoshi/ebiten/v2`. `Update()` runs at a fixed tick rate
  (60 TPS by default), which makes simulations deterministic and easy to test.
- **Commands:** `go run .`, `go test ./...`, `go build`. Web: build with `GOOS=js GOARCH=wasm` plus the
  `wasm_exec.js` shim. Very agent-friendly.

## Haxe: HaxeFlixel, Heaps, OpenFL
- **HaxeFlixel** (on OpenFL/Lime): `Project.xml` lists `<haxelib name="flixel"/>`; run with `lime test html5`
  or `lime test windows`.
- **Heaps** (behind Dead Cells): `.hxml` build files, the HashLink VM (`hl`) for desktop and JavaScript for
  the web.

## Solar2D (formerly Corona)
Lua, mobile-first 2D, free and open source: `main.lua` + `config.lua` + `build.settings`. The Simulator
runs it; builds come from the Simulator's build dialog or its command-line options.

## Cocos Creator
TypeScript with an editor, 2D and 3D, strong in mobile and web markets. Editor-centric, with
`package.json` holding `creator.version`. Agents work best in the TypeScript components.

## Stride, Flax, O3DE (3D engines with editors)
- **Stride:** C#, editor-based, Windows-centric.
- **Flax:** C# and C++, with an editor; `.flaxproj` files.
- **O3DE:** C++, Lua and Script Canvas; heavy, aimed at large 3D projects.

For all three, agents contribute code; scenes and assets mostly go through the editor.

## Fantasy consoles
- **PICO-8** (paid): 128×128 pixels, 16 colours and an 8,192-token code limit.
  - **Files:** `.p8` carts are text (Lua plus hex-encoded graphics, map and sound sections), so an agent can
    write the code section.
  - **Commands:** run with `pico8 -run cart.p8`; export to web with `export game.html` in PICO-8's console.
  - The constraints are the design: count tokens as you go.
- **TIC-80** (free, plus a paid Pro): carts and scripts in several languages (Lua, JavaScript, Python and
  more). Pro supports text-based cart sources.
- **Picotron:** Lexaloffle's newer fantasy workstation.
- **Pyxel:** Python, with built-in editors (see `python.md`).

## Roblox (Luau)
- Roblox Studio is required. **Rojo** syncs a filesystem project (`default.project.json`) into Studio
  (`rojo serve`) and builds place files (`rojo build -o game.rbxlx`). Toolchains are managed with Rokit
  (or Aftman, Foreman).
- **Tests:** Jest-Lua (Roblox's Jest port) or TestEZ inside Studio. **Lune** runs standalone Luau scripts for
  tooling.
- Platform rules (age ratings, community standards, monetization through Robux) apply. The user owns the
  account and publishing.

## UEFN (Unreal Editor for Fortnite)
Verse code plus Fortnite Creative devices, published through Epic's island review. It's an Unreal-based
editor with its own rules, and its own documentation is the source of truth.

## Godot forks
Redot and other Godot forks: treat them like `godot.md`, and match the fork's exact version.

## Modding instead of making?
To change a game that someone else made, without its source (a new weapon in Terraria, a civilization in
Age of Empires), that's modding: use universal-modder's mod-any-game skill.
