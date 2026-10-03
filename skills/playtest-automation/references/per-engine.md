# Test harnesses, per engine

Concrete starting points for each engine: a test, input injection, a state dump, a screenshot and an agent
bridge. APIs drift between versions. If something doesn't compile, check the docs for the exact version in
`GAME_PLAN.md`, and fix the snippet rather than the game.

## Contents
- [Godot 4](#godot-4)
- [Unity 6](#unity-6)
- [Unreal 5](#unreal-5)
- [Web (Vitest + Playwright)](#web-vitest--playwright)
- [Bevy](#bevy)
- [pygame-ce](#pygame-ce)
- [LÖVE](#löve)
- [MonoGame / FNA](#monogame--fna)
- [Golden images with ugd shot diff](#golden-images-with-ugd-shot-diff)

---

## Godot 4
**A GUT test** (`res://test/test_player.gd`; run with
`godot --headless -s addons/gut/gut_cmdln.gd -gdir=res://test -gexit`):
```gdscript
extends GutTest

func test_damage_rules() -> void:
    assert_eq(Damage.compute(10, true), 20, "crits double damage")

func test_player_walks_right() -> void:
    var player: CharacterBody2D = preload("res://scenes/player.tscn").instantiate()
    add_child_autofree(player)
    var x0 := player.position.x
    Input.action_press("move_right")
    await wait_physics_frames(30)
    Input.action_release("move_right")
    assert_gt(player.position.x, x0 + 50.0)
```

**An autotest entry point** (an autoload; run with `godot --path . -- --autotest smoke`):
```gdscript
extends Node

func _ready() -> void:
    var args := OS.get_cmdline_user_args()
    var i := args.find("--autotest")
    if i == -1 or not OS.is_debug_build():
        return
    var name := args[i + 1] if i + 1 < args.size() else "smoke"
    await get_tree().process_frame
    var ok: bool = await run(name)          # your scripted scenario: load scene, press actions, assert on snapshot()
    print("AUTOTEST %s: %s" % ["PASS" if ok else "FAIL", name])
    get_tree().quit(0 if ok else 1)
```

**A screenshot** (needs a renderer, so not `--headless`):
```gdscript
await RenderingServer.frame_post_draw
get_viewport().get_texture().get_image().save_png("user://shots/%s.png" % name)
```

**An agent bridge** (an autoload; dev builds only; JSON lines on 127.0.0.1):
```gdscript
extends Node

var server := TCPServer.new()
var peers: Array[StreamPeerTCP] = []
var buffers := {}

func _ready() -> void:
    if OS.is_debug_build() and "--bridge" in OS.get_cmdline_user_args():
        server.listen(47800, "127.0.0.1")

func _process(_delta: float) -> void:
    if not server.is_listening():
        return
    while server.is_connection_available():
        var p := server.take_connection()
        peers.append(p)
        buffers[p] = ""
    for p in peers:
        p.poll()
        if p.get_status() != StreamPeerTCP.STATUS_CONNECTED:
            continue
        var n := p.get_available_bytes()
        if n <= 0:
            continue
        buffers[p] += p.get_utf8_string(n)
        while "\n" in buffers[p]:
            var line: String = buffers[p].get_slice("\n", 0)
            buffers[p] = buffers[p].substr(line.length() + 1)
            var reply := handle(JSON.parse_string(line))
            p.put_data((JSON.stringify(reply) + "\n").to_utf8_buffer())

func handle(cmd) -> Dictionary:
    if typeof(cmd) != TYPE_DICTIONARY:
        return {"ok": false, "error": "bad json"}
    match cmd.get("cmd", ""):
        "observe": return Game.snapshot()                       # your state dump
        "press": Input.action_press(cmd.action); return {"ok": true}
        "release": Input.action_release(cmd.action); return {"ok": true}
        _: return {"ok": false, "error": "unknown command"}
```
Releasing a press after N frames, stepping while paused, and loading scenes follow the same pattern. Keep the
command list short and explicit.

## Unity 6
**EditMode test** (rules; in a test assembly that references the game assembly):
```csharp
using NUnit.Framework;

public class DamageTests {
    [Test] public void CritDoublesDamage() => Assert.AreEqual(20, Damage.Compute(10, crit: true));
}
```
**PlayMode test with virtual input.** It needs `"testables": ["com.unity.inputsystem"]` in
`Packages/manifest.json`, and test-assembly references to `Unity.InputSystem` and
`Unity.InputSystem.TestFramework`:
```csharp
using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class PlayerMoveTests : InputTestFixture {
    [UnityTest] public IEnumerator HoldingRightMovesPlayer() {
        var keyboard = InputSystem.AddDevice<Keyboard>();
        yield return SceneManager.LoadSceneAsync("TestArena");
        var player = GameObject.FindWithTag("Player").transform;
        float x0 = player.position.x;
        Press(keyboard.rightArrowKey);
        for (int i = 0; i < 30; i++) yield return new WaitForFixedUpdate();
        Release(keyboard.rightArrowKey);
        Assert.Greater(player.position.x, x0 + 1f);
    }
}
```
**A screenshot of one camera** (exact framing; needs graphics):
```csharp
static void SaveCameraPng(Camera cam, string path, int w = 1280, int h = 720) {
    var rt = new RenderTexture(w, h, 24);
    cam.targetTexture = rt; cam.Render();
    RenderTexture.active = rt;
    var tex = new Texture2D(w, h, TextureFormat.RGB24, false);
    tex.ReadPixels(new Rect(0, 0, w, h), 0, 0); tex.Apply();
    cam.targetTexture = null; RenderTexture.active = null;
    System.IO.File.WriteAllBytes(path, tex.EncodeToPNG());
}
```
**Bridge:** a `TcpListener(IPAddress.Loopback, port)` on a background thread pushes parsed commands into a
`ConcurrentQueue`. A `MonoBehaviour.Update` drains it on the main thread and writes replies back. Wrap the
whole thing in `#if UNITY_EDITOR || DEVELOPMENT_BUILD`.

## Unreal 5
**A spec test** (C++; run with `-ExecCmds="Automation RunTests Beacon.;Quit"`):
```cpp
#include "Misc/AutomationTest.h"

BEGIN_DEFINE_SPEC(FDamageSpec, "Beacon.Rules.Damage",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
END_DEFINE_SPEC(FDamageSpec)

void FDamageSpec::Define() {
    Describe("Crit", [this]() {
        It("doubles damage", [this]() { TestEqual(TEXT("crit"), UDamageLibrary::Compute(10, true), 20); });
    });
}
```
- **Gameplay checks:** `AFunctionalTest` actors placed in a test map call `FinishTest(...)` with the result,
  and the automation system runs every functional test in its maps.
- **Input injection:** `GetLocalPlayer()->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>()->InjectInputForAction(JumpAction, FInputActionValue(true));`.
- **Bridge:** the Remote Control API plugin. For example, `PUT http://127.0.0.1:30010/remote/object/call` with
  `{"objectPath": "...", "functionName": "DumpState"}` calls a `UFUNCTION` on a live object.
- **Screenshot:** `FScreenshotRequest::RequestScreenshot(TEXT("shot.png"), false, false)`, or the
  `HighResShot` console command.

## Web (Vitest + Playwright)
**`playwright.config.ts`:**
```ts
import { defineConfig } from "@playwright/test";
export default defineConfig({
  webServer: { command: "npm run dev -- --port 5173 --strictPort", url: "http://localhost:5173", reuseExistingServer: true },
  use: { baseURL: "http://localhost:5173" },
});
```
**An end-to-end test using the dev-only `window.__game` API:**
```ts
import { test, expect } from "@playwright/test";

test("jump reaches apex", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  await page.goto("/?scene=arena&seed=7");
  await page.waitForFunction(() => (window as any).__game?.ready === true);
  await page.evaluate(() => (window as any).__game.press("jump", 6));
  await page.evaluate(() => (window as any).__game.step(24));
  const s = await page.evaluate(() => (window as any).__game.observe());
  expect(s.player.y).toBeLessThan(-40);
  await expect(page.locator("canvas")).toHaveScreenshot("arena-jump.png", { maxDiffPixelRatio: 0.01 });
  expect(errors).toEqual([]);
});
```
Pure logic in `src/sim/` gets plain Vitest tests with no browser.

## Bevy
The headless-app test is in `skills/make-any-game/references/engines/bevy-rust.md`. For a live bridge, add
`RemotePlugin` and `RemoteHttpPlugin` in dev builds; the Bevy Remote Protocol answers JSON-RPC requests over
HTTP on localhost (the `bevy_remote` docs list the methods for your version). For screenshots, see
`examples/window/screenshot.rs` at your version's tag.

## pygame-ce
**`tests/conftest.py`** sets the dummy drivers before anything imports pygame (see `python.md`). Then:
```python
import pygame
from beacon.sim import Sim
from beacon.render import draw

def test_player_moves_right():
    sim = Sim(seed=7)
    for _ in range(60):
        sim.update(1 / 60, actions={"right"})
    assert sim.player.x > 50

def test_arena_frame(tmp_path):
    pygame.init()
    screen = pygame.display.set_mode((320, 180))
    sim = Sim(seed=7)
    draw(screen, sim)
    pygame.image.save(screen, str(tmp_path / "arena.png"))
    # compare: ugd shot diff tests/golden/arena.png <tmp_path>/arena.png
```

## LÖVE
**busted** (`spec/sim_spec.lua`) on pure modules:
```lua
local Sim = require("src.sim")

describe("sim", function()
  it("moves the player right", function()
    local s = Sim.new(7)
    for _ = 1, 60 do s:update(1 / 60, { right = true }) end
    assert.is_true(s.player.x > 50)
  end)
end)
```
For in-engine checks, `love . --autotest smoke` runs a scenario, prints `AUTOTEST PASS` or `FAIL`, and
calls `love.event.quit(code)`.

## MonoGame / FNA
**xUnit** on the simulation library:
```csharp
public class SimTests {
    [Fact] public void PlayerMovesRight() {
        var sim = new Sim(seed: 7);
        for (int i = 0; i < 60; i++) sim.Update(1f / 60f, Actions.Right);
        Assert.True(sim.Player.X > 50);
    }
}
```

## Golden images with ugd shot diff
Any engine that can save a PNG can have golden images:
```bash
ugd shot diff tests/golden/arena.png out/arena.png --out out/arena.diff.png    # exit 1 if too different
ugd shot diff tests/golden/arena.png out/arena.png --threshold 12 --max-ratio 0.002
ugd shot diff tests/golden/arena.png out/arena.png --update                     # approve the new look (after the human agrees)
```
- `--threshold` is the per-channel difference (0-255) that counts a pixel as changed.
- `--max-ratio` is the fraction of changed pixels allowed.
- The diff image shows the actual frame dimmed, with changed pixels in red.
- Keep goldens per platform and renderer, and approve a new one only after looking at it (or having the
  human look).
