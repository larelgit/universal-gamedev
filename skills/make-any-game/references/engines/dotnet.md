# .NET: MonoGame, FNA, KNI

**Pick it when** the user writes C# and wants a code-only 2D framework with full control: the XNA lineage
behind Celeste, Stardew Valley and many others. **Think twice** for 3D-heavy games, for the web (only KNI
targets it), or if the user wants an editor (Godot C#, Unity or Stride instead).

Versions (October 2026): MonoGame 3.8.5.1 (3.8.6 in preview). FNA is source-based and tracks its own
releases. KNI is an XNA-compatible fork with a web target (BlazorGL).

## Pick a framework
- **MonoGame:** templates, a content pipeline, and desktop, mobile and console support once approved.
- **FNA:** an accurate XNA 4 reimplementation, used as source (a git submodule) plus native fnalibs. It has
  no content pipeline of its own: load PNG/WAV/OGG directly, or use XNBs built by MonoGame's pipeline.
- **KNI:** when the web is a must.
- **Related:** MonoGame.Extended (tilemaps, cameras, tweens), Nez (an ECS-style framework), Raylib-cs (raylib
  for C#), FontStashSharp (runtime fonts).

## Identify
A `*.csproj` referencing `MonoGame.Framework.*` (or FNA, or KNI packages), plus `Content/Content.mgcb` for
MonoGame.

## Setup
```bash
dotnet new install MonoGame.Templates.CSharp
dotnet new mgdesktopgl -o Beacon            # cross-platform DesktopGL (mgwindowsdx for DirectX on Windows)
dotnet new xunit -o Beacon.Tests             # tests for the logic library
dotnet new classlib -o Beacon.Sim            # rules with no MonoGame dependency
```
- Reference `Beacon.Sim` from both the game and the tests. The `Game` class needs a GPU and a window, so
  keep the rules out of it.
- **Content:** MonoGame builds `Content/Content.mgcb` during `dotnet build`. Edit it as text or with the MGCB
  Editor (`dotnet tool restore`, then `dotnet mgcb-editor`). 3.8.5 adds a code-first Content Builder
  project (`dotnet new mgcb`) that the docs present as its successor. For prototypes,
  `Texture2D.FromFile(GraphicsDevice, path)` skips the pipeline entirely.

## Commands
```bash
dotnet run --project Beacon                  # play
dotnet test                                  # rules and simulation tests
dotnet publish Beacon -c Release -r win-x64 --self-contained       # also linux-x64, osx-arm64, osx-x64
```
macOS needs an `.app` bundle structure and notarization for distribution (MonoGame's packaging docs cover
the bundle layout).

## Debug hooks and oracles
- **Fixed timestep:** `IsFixedTimeStep = true` and `TargetElapsedTime = TimeSpan.FromSeconds(1.0 / 60)` are the
  defaults; keep them for deterministic simulation.
- **Edge-triggered input:** store last frame's `KeyboardState` / `GamePadState`; "just pressed" means down now
  and up before. Put input behind an action layer that tests can drive.
- **Screenshots:** draw the frame into a `RenderTarget2D`, then `SaveAsPng(stream, width, height)`. Render
  to a low-resolution target and scale up for pixel art.
- **Headless:** run `Beacon.Sim` directly from tests or a console runner. Rendering tests need a real GPU
  session (or xvfb plus Mesa on Linux).
- **Agent bridge:** a `TcpListener` on `127.0.0.1` with a queue drained in `Update`, or stdin/stdout when
  you launch the process.

## Pitfalls
- **Content build failures:** a missing tool restore (`dotnet tool restore`), fonts referenced by
  `.spritefont` not installed on Linux, or wrong processor parameters. Read the MGCB output.
- **Premultiplied alpha:** MonoGame premultiplies by default. Mixing straight and premultiplied art gives
  dark halos; set `BlendState` and the processor's settings consistently.
- **Pixel art blurs** unless `spriteBatch.Begin(samplerState: SamplerState.PointClamp)`.
- **DesktopGL vs WindowsDX** differ in shaders and behaviour; pick one early.
