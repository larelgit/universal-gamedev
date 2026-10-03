---
name: ship-game
description: Build, package and release a game. Covers the pre-release lint (secrets, licenses, credits, debug leftovers), exports per platform (Windows, macOS, Linux, web, Android, iOS), versioning and changelogs, itch.io (butler), Steam (Steamworks, steamcmd, store assets, review times, AI disclosure), Epic, web portals (CrazyGames, Newgrounds, Game Jolt, Poki), mobile stores, the store page, a press kit and the launch post. Use when the user wants to ship, release, export, upload, publish or submit a game, put it on itch.io or Steam, make a release build, set up a store page, or prepare a game jam submission.
---

# Ship a game

Shipping is a project of its own. The build pipeline starts in the first session (make-any-game, step 8);
release day is a checklist, not an adventure. **Uploading, store pages and posts are always the user's
call:** prepare everything, show them, and let them press the button with their own accounts.

## 1. Lint the project and the build
```bash
ugd release check .                   # the project: secrets, sensitive files, credits, licenses, paths
ugd release check build/windows      # the exported build: secrets, steam_appid.txt, stray files, web paths
```
- **FAIL:**
  - leaked keys (fal, OpenAI, Anthropic, GitHub, AWS, Google, private keys);
  - `.env` files;
  - keystores and certificates (`.jks`, `.keystore`, `.p12`, `.pfx`, `.p8`, `.mobileprovision`);
  - Steam credential files;
  - Godot's `export_credentials.cfg`.
- **WARN:**
  - a missing README, LICENSE or CREDITS;
  - generated assets (`fal_manifest.jsonl`) without a fal credit, or without a reminder to disclose AI
    content;
  - Godot projects without the engine's license notice;
  - absolute user paths;
  - files over 100 MB;
  - file names that differ only by case (they break on Windows, macOS and the web);
  - `steam_appid.txt` in a build;
  - root-absolute paths (`src="/..."`) in web builds, which break under itch.io's subfolder hosting.

Fix every FAIL. Decide on each WARN deliberately. The lint can't see everything, so also walk through this
checklist:
- [ ] Dev console, cheats, debug overlays and the agent bridge are compiled out or locked behind a dev flag.
- [ ] The version is shown in game (title or settings screen) and matches the build metadata.
- [ ] Saves from the previous release load (a migration test).
- [ ] Settings, rebinding and accessibility options work; defaults are sane (windowed or borderless,
      moderate volume, no crash without a gamepad).
- [ ] The credits screen covers the engine's notice, libraries, fonts, asset packs, generated assets (with
      models) and the tools.
- [ ] The exported build passed its smoke test (playtest-automation) on every target, and someone played
      it on minimum-spec hardware.

## 2. Export per platform
Use the engine's command-line export from a script, so a release is one command (`tools/release.sh` /
`.ps1`).

| Engine | Release export | Notes |
|---|---|---|
| Godot | `godot --headless --path . --export-release "<Preset>" build/<file>` | needs `export_presets.cfg` (commit it) and export templates for the exact engine version |
| Unity | `Unity -batchmode -quit -projectPath . -executeMethod BuildScript.Build -logFile -` | `BuildScript.Build` calls `BuildPipeline.BuildPlayer`; platform modules must be installed |
| Unreal | `RunUAT BuildCookRun -project=<uproject> -platform=Win64 -clientconfig=Shipping -build -cook -stage -pak -archive -archivedirectory=<dir>` | Shipping config strips console commands |
| Web (Vite) | `npm run build` → `dist/` | set `base: "./"` so it runs from any subfolder |
| Bevy | `cargo build --release`; web: `trunk build --release` (or the community `bevy run web` prototype) | shrink WASM with `wasm-opt`; enable LTO for size |
| LÖVE | zip the game as `.love`; fuse with `love.exe` for Windows | makelove automates it; love.js (web) is unmaintained, so test it hard or pick another engine for web |
| pygame-ce | PyInstaller (`pyinstaller --windowed main.py`) or Nuitka; web: pygbag | test the frozen build: data paths change |
| MonoGame / FNA | `dotnet publish -c Release -r win-x64 --self-contained` (and `linux-x64`, `osx-arm64`) | ship the content folder alongside |
| raylib / native | CMake Release build; web: Emscripten (`emcmake cmake ..`) | |
| Ren'Py | `renpy.sh launcher distribute <project>` | builds every platform at once |
| GameMaker | the IDE's Create Executable, or Igor from the command line | per-platform licenses |

Exact flags per engine are in its playbook (`skills/make-any-game/references/engines/`).

Platform notes:
- **Windows:** unsigned executables trigger SmartScreen warnings. Signing is optional for itch.io and
  Steam.
- **macOS:** Gatekeeper blocks apps that aren't notarized. Notarization needs the user's Apple Developer
  account (`xcrun notarytool`). Build universal (arm64 + x86_64) when the engine supports it.
- **Linux:** a tarball or AppImage; on Steam, the Steam Linux Runtime. Proton covers many players if you
  skip a native build.
- **Web:** `index.html` at the zip root, relative paths, a click-to-start screen (audio unlock and keyboard
  focus), and testing inside the real embed (itch.io uses an iframe). Threaded builds need COOP/COEP headers:
  itch.io has an experimental SharedArrayBuffer option that doesn't work in Safari. Ship single-threaded
  builds when you can.
- **Mobile and consoles:** `references/stores.md`.

## 3. Version and changelog
- **One source of truth** for the version: Godot `application/config/version`, Unity
  `PlayerSettings.bundleVersion`, Unreal `ProjectVersion` in `DefaultGame.ini`, `package.json`,
  `Cargo.toml`, or a `VERSION` file the build reads.
- Use `MAJOR.MINOR.PATCH` plus a build number, keep a `CHANGELOG.md`, and tag releases in git.
- Note save compatibility in every changelog entry, and re-run the oracles before every update.

## 4. Where to release
The short version (details, sizes and review times: `references/stores.md`):
- **itch.io:** the fastest. `butler push build/windows <user>/<game>:windows --userversion 1.0.0`. HTML5 games
  upload as a zip played in the browser. Fill in the generative AI disclosure.
- **Steam:** a $100 Steam Direct fee per app, store assets in fixed sizes, a Coming Soon page at least two
  weeks before release, and Valve reviews of both the store page and the build (plan a week each). The
  Content Survey covers AI disclosure.
- **Epic Games Store:** self-publishing with a $100 fee per title and an 88/12 split (100% of the first $1M
  per product per year since June 2025).
- **Web portals:** CrazyGames, Newgrounds and Game Jolt accept uploads; Poki is application-only.
- **Your own site:** GitHub Pages, Cloudflare Pages or Netlify. Only the last two can set the COOP/COEP
  headers threaded web builds need.
- **Mobile:** Google Play (AAB, Play App Signing, target API level, closed testing for new personal
  accounts) and the App Store (developer program, TestFlight, review).
- **Consoles:** approved developer accounts and dev kits under NDA. The user applies; an agent can't set
  this up.

## 5. Store page, press kit and the post
- **Capsule and key art:** `um fal image` for the illustration, with the real logo composited on top (models
  garble lettering). It must read at the smallest capsule size. On Steam, capsules may only show artwork,
  the game's name and an official subtitle: no review quotes, awards or discount text.
- **Screenshots and trailer:** real gameplay only (the trailer-video skill). Lead with the core verb.
- **Short description:** the hook in one sentence, what the player does, and the twist.
- **Press kit:** a fact sheet, description, features, screenshots, logo, trailer, credits and contact.
- **The post:** video first (20-45 s, gameplay within 2-3 s), the hook, the link, an honest "made with
  <engine> + <agent>" credit, and AI disclosure where it applies.
- Draft all of it and show the user. They publish.

## 6. After launch
Keep an opt-in crash report or feedback channel, ship hotfixes through the same release check, write patch
notes, protect save compatibility, and re-run the full oracle set before every update.
