# Bevy (and other Rust engines)

**Pick it when** the user likes Rust, wants an ECS architecture, or wants a code-only workflow with excellent
performance. **Think twice** if they want a visual editor (Bevy's isn't stable yet), are new to Rust, or need
API stability: Bevy ships breaking changes every few months, and third-party crates lag behind each
release.

Versions (October 2026): Bevy 0.19.1, with 0.20 in release candidates. Pin the exact version, and read
the official migration guide before every upgrade.

**Other Rust options:**
- **macroquad:** simple, immediate-mode, WASM-friendly; great for small 2D games and jams.
- **Fyrox:** an editor-based engine.
- **ggez:** a 2D framework, now less active.

## Identify
`Cargo.toml` depending on `bevy` (or `macroquad`, `fyrox`, `ggez`), plus an `assets/` folder at the crate root.

## Setup
- Install rustup (ask first). On Windows, use the MSVC toolchain. On Linux, install the ALSA and udev dev
  packages (`libasound2-dev libudev-dev`, and the Wayland/xkbcommon ones for Wayland).
- `cargo new beacon && cd beacon && cargo add bevy`.
- **Fast iteration** (from Bevy's quick start):
  ```toml
  [profile.dev]
  opt-level = 1
  [profile.dev.package."*"]
  opt-level = 3
  ```
  Add the `dynamic_linking` feature for dev builds only; never ship it. A faster linker (lld, or mold on
  Linux) cuts link times further.

## Architecture
- **Plugins per feature** (`PlayerPlugin`, `EnemyPlugin`). Components are plain data, systems are
  functions, and resources hold globals.
- **Simulation runs in `FixedUpdate`;** presentation runs in `Update`. Use `States` (`OnEnter`/`OnExit`,
  `in_state`) for menus and levels.
- **Order systems explicitly** (`.chain()`, `.before()`, `.after()`) when order matters. Remember that
  `Commands` take effect at the next sync point, not immediately.
- **Assets** load from `assets/`. The `file_watcher` feature hot-reloads them.
- **Version drift:** event and message APIs, `Query::single` and similar have changed between releases.
  When unsure, read the examples and tests in the Bevy repo **at your version's git tag**.

## Commands
```bash
cargo run                                   # play
cargo test                                  # unit + headless app tests
cargo clippy -- -D warnings                 # lint
cargo build --release                       # release build (consider lto = "thin" and strip = true)
rustup target add wasm32-unknown-unknown    # once, for web
trunk serve                                 # web dev server (Trunk.toml + index.html); or wasm-server-runner
trunk build --release                       # web build → dist/
```
A community Bevy CLI (TheBevyFlock, with `bevy new` and `bevy run web`) exists as an alpha prototype
installed from git. It's not an official tool.

## Tests and oracles
- **A headless `App` is the oracle.** Build an app without rendering, add your gameplay plugin, inject
  input, call `app.update()` N times and assert on the world:
  ```rust
  use std::time::Duration;
  use bevy::prelude::*;
  use bevy::time::TimeUpdateStrategy;

  #[test]
  fn player_moves_right() {
      let mut app = App::new();
      app.add_plugins(MinimalPlugins)                       // scheduling + time, no window or renderer
          .insert_resource(TimeUpdateStrategy::ManualDuration(Duration::from_secs_f64(1.0 / 60.0)))
          .init_resource::<ButtonInput<KeyCode>>()
          .add_plugins(beacon::GameplayPlugin);             // your logic, without rendering plugins
      app.world_mut().resource_mut::<ButtonInput<KeyCode>>().press(KeyCode::ArrowRight);
      for _ in 0..60 { app.update(); }
      // query the player's Transform and assert it moved; mirror Bevy's own tests for the query API of your version
  }
  ```
  `TimeUpdateStrategy::ManualDuration` makes time advance by a fixed step per update, so tests are
  deterministic.
- **The agent bridge comes built in:** the Bevy Remote Protocol (`RemotePlugin` + `RemoteHttpPlugin`) serves
  JSON-RPC over HTTP on localhost. You can query and modify entities and components of a running game. Enable
  it in dev builds only.
- **Screenshots:** spawn a `Screenshot` entity for the primary window and save it to disk with the observer
  helper (see `examples/window/screenshot.rs` at your version's tag).
- **Diagnostics:** `FrameTimeDiagnosticsPlugin` + `LogDiagnosticsPlugin`; `RUST_LOG=info` (or `debug`).
  bevy-inspector-egui is a community in-game inspector for dev builds.

## Ecosystem
- Physics: Avian, bevy_rapier.
- Tilemaps: bevy_ecs_tilemap, bevy_ecs_ldtk.
- Dev UI: bevy_egui.
- Networking: Lightyear, bevy_replicon, bevy_ggrs (see `../multiplayer.md`).

Check each crate's compatibility table against your Bevy version before adding it.

## Pitfalls
- **Breaking upgrades:** upgrade on a branch, follow the migration guide, and wait for your crates to
  catch up.
- **System ordering ambiguities** cause one-frame-late bugs. Order systems explicitly, and use the ambiguity
  detection when debugging.
- **Compile times:** keep the dev profile settings above, and split big crates.
- **WASM:** no threads by default, audio waits for a user gesture, and asset paths are relative to the
  served folder.
