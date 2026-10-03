# Web: Phaser, three.js, PixiJS, Babylon.js, Kaplay

**Pick it when** the game should run in a browser, be shared with a link, or ship at a jam, or when you want
the most agent-friendly stack there is: everything is text, reloads are instant, and Playwright can drive
and screenshot the real game. **Think twice** for heavy 3D with gigabytes of assets, for console targets,
and for games that need native threads or file access (desktop wrappers can add those).

## Pick a library
| Library | What it is | Good for |
|---|---|---|
| **Phaser** (4.x; 3.x still common) | a full 2D framework: scenes, Arcade/Matter physics, tilemaps, input, audio, cameras, tweens, particles | most 2D games |
| **PixiJS** (v8) | a fast 2D renderer only; you bring the loop, physics and structure | custom 2D engines, UI-heavy games |
| **Kaplay** (the Kaboom successor) | a tiny, friendly API | jams, beginners |
| **Excalibur** | a TypeScript-first 2D engine | typed 2D projects |
| **three.js** (r186) | a 3D renderer: scenes, materials, glTF; add Rapier or cannon-es for physics | stylised 3D, custom engines |
| **Babylon.js** | a full 3D engine with an inspector and Havok physics | 3D games wanting batteries included |
| **PlayCanvas** | an open-source engine with a cloud editor | teams using its editor |

Phaser 4.0.0 shipped in April 2026, and `npm create @phaserjs/game@latest` scaffolds it. For three.js, the
`WebGLRenderer` is the recommended choice; the `WebGPURenderer` (from `three/webgpu`, with a WebGL2
fallback) was still experimental in October 2026.

## Setup
- Node LTS (ask before installing). Vite + TypeScript:
  `npm create vite@latest my-game -- --template vanilla-ts`, or the Phaser template.
- **Layout:**
  - `src/main.ts`, `src/scenes/`;
  - `src/sim/` for pure game logic with no DOM or engine imports, so Vitest runs it in milliseconds;
  - `src/data/*.json`;
  - `public/assets/`;
  - `tests/unit/` (Vitest) and `tests/e2e/` (Playwright).
- `vite.config.ts`: `base: "./"`, so the build runs from any subfolder (itch.io hosts games in one).
- **Git:** ignore `node_modules/`, `dist/`, `test-results/` and `playwright-report/`.

## Commands
```bash
npm run dev                        # Vite dev server on localhost (keep it in the background; --host would expose it to the LAN)
npm run build                      # production build → dist/
npm run preview                    # serve dist/ the way players will get it
npx vitest run                     # logic tests
npx playwright test                # the game in a real browser (headless)
npx playwright test --update-snapshots    # re-approve golden screenshots after a deliberate change
```

## Agent hooks and oracles
- **A dev-only game API:**
  ```ts
  if (import.meta.env.DEV) {
    (window as any).__game = {
      observe: () => sim.snapshot(),                   // JSON state
      press: (action: string, frames = 1) => input.inject(action, frames),
      step: (frames: number) => loop.stepManually(frames),
      load: (scene: string, seed: number) => game.load(scene, seed),
    };
  }
  ```
  Vite removes the block from production builds. In Playwright, `await page.evaluate(() =>
  window.__game.observe())` is your agent bridge.
- **URL parameters** for test setups: `?scene=arena&seed=7&autotest=smoke`.
- **Determinism:** a seeded PRNG (never `Math.random()` in game logic), a fixed-timestep loop driven by
  `requestAnimationFrame` with an accumulator, and a manual-step mode for tests.
- **Playwright:**
  - start the dev server through `webServer` in `playwright.config.ts`;
  - fail on `page.on("pageerror")` and console errors;
  - golden images with `await expect(page.locator("canvas")).toHaveScreenshot("arena.png", { maxDiffPixelRatio: 0.01 })`.

  Headless Chromium renders WebGL in software (SwiftShader) without extra flags in current Playwright. It's
  slow, so keep test scenes small.
- **WebGL screenshots from inside the page** (`canvas.toDataURL`) need `preserveDrawingBuffer: true`, or must
  run in the same frame as rendering. Playwright's own screenshots don't care.

## Audio, input and display
- **Autoplay policy:** browsers start audio only after a user gesture. Use a click-to-start screen. Phaser
  handles the unlock itself; Howler.js does it for vanilla projects.
- **Keys:** use `KeyboardEvent.code`, and call `preventDefault()` on arrows and space, or the page scrolls.
  Give the canvas `tabindex` and focus it: itch.io embeds games in an iframe that needs a click first.
- **High-DPI:** size the canvas by `devicePixelRatio` (capped at 2). For pixel art, use integer scaling and
  `image-rendering: pixelated`.
- **Tab switching:** `requestAnimationFrame` pauses in background tabs, so the first delta after returning is
  huge. Clamp it.

## Ship it
- **itch.io:** zip `dist/` with `index.html` at the root (`base: "./"` matters here).
- **Other hosts:**
  - GitHub Pages (no custom headers);
  - Netlify or Cloudflare Pages (`_headers` for COOP/COEP when a threaded WASM library needs it);
  - CrazyGames, Newgrounds and Game Jolt.
- **Desktop and Steam:** wrap the game with Tauri (small) or Electron. steamworks.js gives Electron access to
  Steamworks.

## Pitfalls
- **Case-sensitive paths:** `Player.png` vs `player.png` works on Windows and 404s on a Linux host.
- **Root-absolute paths** (`/assets/x.png`) break under subfolder hosting. Use relative paths or
  `import.meta.env.BASE_URL`.
- **`file://` doesn't work** (CORS blocks loading assets). Always serve over HTTP, even for local tests.
- **Restarting a scene leaks** listeners, timers and textures unless the scene's shutdown cleans them up.
- **Bundle size:** compress textures (WebP or KTX2) and audio, and lazy-load later levels.
