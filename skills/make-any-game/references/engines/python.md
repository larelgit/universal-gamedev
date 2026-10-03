# Python: pygame-ce, Arcade, Pyxel, Ursina

**Pick it when** the user knows Python or is learning, for prototypes, jams, simulation-heavy games and
tools, and for games where the agent should verify everything headless. **Think twice** for high-end 3D,
mobile, and large commercial releases (performance and packaging take work).

## Pick a library
| Library | What it is | Notes |
|---|---|---|
| **pygame-ce** (2.5.x) | the maintained community fork of pygame: SDL2 surfaces, input, mixer | `pip install pygame-ce`, still imported as `pygame`; never install both `pygame` and `pygame-ce` |
| **Arcade** (3.x) | a modern OpenGL 2D framework: sprites, cameras, physics helpers | nicer API for bigger 2D games |
| **Pyxel** | a retro fantasy-console engine with built-in sprite and sound editors | tiny pixel-art games; exports to web |
| **Ursina** (on Panda3D) | quick 3D | prototypes and learning |
| **Panda3D**, **pyglet** | lower-level 3D/2D | when you need control |

## Setup
- `uv init beacon && cd beacon && uv add pygame-ce`, with `uv add --dev pytest` for tests.
- **Layout:** a `beacon/` package (`sim/` pure logic, `scenes/`, `assets.py`), `main.py`, `assets/` and
  `tests/`.
- **Window:** `pygame.display.set_mode((320, 180), pygame.SCALED)` renders at low resolution and scales with
  nearest neighbour and letterboxing, which is ideal for pixel art.
- **Game loop:** `dt = clock.tick(60) / 1000`, plus an accumulator for a fixed-step simulation. Pump events
  every frame, or the OS thinks the window has hung.

## Commands
```bash
uv run python main.py                               # play
uv run python main.py --scene arena --seed 7        # your own flags via argparse
uv run pytest                                       # tests (set the SDL dummy drivers in conftest.py, below)
uv run pyinstaller --windowed --name Beacon main.py # desktop build (test the frozen build: data paths change)
uv run pygbag .                                     # web build + local server on http://localhost:8000
uv run pygbag --build .                             # web build only → build/web
```

## Tests and oracles
- **Headless pygame:** set the drivers before pygame is imported, e.g. in `tests/conftest.py`:
  ```python
  import os
  os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
  os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
  ```
  `pygame.display.set_mode` works, surfaces render, and `pygame.image.save(screen, "shot.png")` writes a real
  screenshot. That's the cheapest golden-image setup of any engine (`ugd shot diff` compares them).
- **Input:** call your input handler with actions, or post events
  (`pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))`).
- **Simulation:** step `sim.update(1/60)` N times and assert on its state. No window needed.
- **Agent bridge:** a stdin/stdout JSON-lines loop when you launch the game yourself, or a socket server on
  `127.0.0.1` polled once per frame.

## Web (pygbag)
pygbag (0.9.x) packages pygame-ce games for the browser, and supports pygame-ce only. The main loop must be
async and yield every frame:
```python
import asyncio

async def main():
    while running:
        step_frame()
        await asyncio.sleep(0)    # yield to the browser every frame

asyncio.run(main())
```
The project folder needs a `main.py`. Zip `build/web` for itch.io, and test audio formats (OGG works best).

## Pitfalls
- **`convert_alpha()`** needs a display mode set first, even under the dummy driver.
- **Performance:** Python loops over thousands of entities are slow. Use sprite groups, spatial hashing,
  and numpy for bulk maths, and profile with `cProfile`.
- **Audio latency:** call `pygame.mixer.pre_init(44100, -16, 2, 512)` before `pygame.init()`.
- **Frozen builds** (PyInstaller) move data files. Resolve paths relative to `sys._MEIPASS` when it
  exists, and include assets with `--add-data`.
