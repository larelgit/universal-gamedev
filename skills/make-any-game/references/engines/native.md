# Native: raylib, SDL3, SFML, custom C/C++

**Pick it when** the user wants full control, tiny binaries, a custom engine, maximum performance, or to
learn how games work underneath. **Think twice** when content iteration speed matters more than control, or
when the user expects an editor.

Versions (October 2026): raylib 6.0; SDL3 3.4.x (stable since 3.2.0 in January 2025); SFML 3.x.

## Pick a library
| Library | What it is | Notes |
|---|---|---|
| **raylib** | a simple C library: window, input, 2D/3D drawing, audio, models | bindings for many languages; easy web builds; zlib license |
| **SDL3** | a platform layer: window, input, audio, a 2D renderer, and the SDL_GPU API | the foundation for custom engines; the callback app model (`SDL_AppInit` / `SDL_AppIterate` / `SDL_AppEvent` / `SDL_AppQuit`) suits web and mobile; zlib |
| **SFML** | a C++ 2D multimedia library | idiomatic C++; zlib |
| **sokol, bgfx** | header-only or renderer-only libraries | for engine builders |

Odin ships raylib and SDL bindings in its vendor library; Zig has raylib-zig.

## Setup (CMake + FetchContent)
```cmake
cmake_minimum_required(VERSION 3.24)
project(beacon C)
include(FetchContent)
FetchContent_Declare(raylib GIT_REPOSITORY https://github.com/raysan5/raylib.git GIT_TAG 6.0)
FetchContent_MakeAvailable(raylib)
add_library(sim src/sim.c)                 # rules: no raylib calls, so tests link only this
add_executable(beacon src/main.c)
target_link_libraries(beacon sim raylib)
enable_testing()
add_executable(sim_tests tests/sim_tests.c)
target_link_libraries(sim_tests sim)
add_test(NAME sim COMMAND sim_tests)
```
Check the tag name against the library's current release before relying on it.

## Commands
```bash
cmake -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug
ctest --test-dir build --output-on-failure
cmake -B build-rel -DCMAKE_BUILD_TYPE=Release && cmake --build build-rel --config Release
emcmake cmake -B build-web -DPLATFORM=Web && cmake --build build-web    # raylib → .html/.js/.wasm (needs Emscripten)
```

## Tests and oracles
- **Split the simulation into its own library,** tested with doctest, Catch2 or GoogleTest through CTest.
- **Sanitizers** (`-fsanitize=address,undefined` with GCC/Clang; `/fsanitize=address` with MSVC) in debug and
  test builds catch memory bugs that would otherwise surface as "random" crashes. That's a strong oracle,
  and it's free.
- **Headless:**
  - SDL has `dummy` and `offscreen` video drivers (`SDL_VIDEODRIVER=dummy`);
  - raylib needs a window (GLFW), so use `xvfb-run` on Linux CI;
  - run the simulation library directly for most tests.
- **Screenshots:** raylib `TakeScreenshot("shot.png")`; SDL3 `SDL_RenderReadPixels` + save via SDL_image,
  or your own PNG writer (stb_image_write).
- **Dev tools:** Dear ImGui (rlImGui for raylib) for in-game panels; Tracy for profiling.
- **Agent bridge:** a non-blocking socket on `127.0.0.1` polled each frame, or stdin/stdout.

## Pitfalls
- **Frame-rate-dependent logic:** `SetTargetFPS` isn't a fixed timestep. Accumulate time and step the
  simulation at a fixed rate.
- **Asset paths** are relative to the working directory. Resolve them from the executable's directory
  (raylib `GetApplicationDirectory()`, SDL `SDL_GetBasePath()`).
- **A console window on Windows:** build as a GUI-subsystem executable for release (`WIN32` in
  `add_executable`, or `-mwindows`).
- **Licenses:** raylib, SDL and SFML are all zlib (permissive), but check every other dependency you vendor.
