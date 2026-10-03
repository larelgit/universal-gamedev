# Unity 6

**Pick it when** the user or team already knows Unity, the game targets mobile or consoles, or it leans on
the Asset Store and mature 2D/3D tooling. **Think twice** for agent-only work: scenes and prefabs are YAML
full of GUIDs and fileIDs, the editor is a 10+ GB install with license activation, and only one editor
instance may hold a project at a time.

Versions (October 2026): 6.3 LTS (6000.3) is the current LTS; 6.6 (6000.6) is the newest supported release.
Prefer the LTS. Unity Personal is free under $200K of revenue plus funding in the last 12 months. Check
current terms for commercial releases.

## Identify
- `ProjectSettings/ProjectVersion.txt` → `m_EditorVersion: 6000.3.x`.
- `Assets/` (with a `.meta` file next to every asset), `Packages/manifest.json` (URP or HDRP, Input System,
  Test Framework...).

## Setup
- **Install** with Unity Hub (the user signs in and activates the license; you don't). The Hub has a
  headless CLI for installs: `"Unity Hub.exe" -- --headless install --version <version> --module <module>`.
  Editors live in `C:\Program Files\Unity\Hub\Editor\<version>\Editor\Unity.exe`, in
  `/Applications/Unity/Hub/Editor/<version>/Unity.app/Contents/MacOS/Unity` on macOS, and in
  `~/Unity/Hub/Editor/<version>/Editor/Unity` on Linux.
- **Render pipeline:** decide at the start. URP (with the 2D Renderer for 2D games) suits most games; HDRP
  is high-end only.
- **Git:** ignore `Library/`, `Temp/`, `Obj/`, `Logs/`, `UserSettings/`, `Build*/` and the generated
  `*.csproj`/`*.sln`. Commit `Assets/` **including every `.meta`**, `Packages/` and `ProjectSettings/`. Keep
  Asset Serialization on Force Text (the default). Use LFS for binary art and audio.

## Agent workflow
- **Code:** C# with assembly definitions (`.asmdef`): one for game code, one for tests. Put rules in plain C#
  classes, not `MonoBehaviour`s, so EditMode tests reach them without a scene.
- **Scenes and prefabs: don't hand-edit the YAML** beyond trivial value tweaks. Create and modify them with
  editor scripts (`[MenuItem]` methods using `EditorSceneManager`, `PrefabUtility`, `AssetDatabase`) run in
  batch mode via `-executeMethod`. Or use an MCP server: the community "MCP for Unity" (CoplayDev/unity-mcp)
  is actively maintained, and Unity's own experimental Unity CLI has a `unity mcp` command (it replaced the
  deprecated in-editor MCP server).
- **`.meta` files carry GUIDs.** Unity generates them on import. Never delete or regenerate one on its own:
  every reference to the asset breaks. Rename the class and its file together; use `[FormerlySerializedAs]`
  when renaming serialized fields.
- **Data:** `ScriptableObject` assets for designer-facing data. For data an agent edits often, JSON or CSV in
  `Assets/Data/` (loaded as `TextAsset`) is more robust than YAML assets.
- **Packages worth knowing:** Input System, Cinemachine, AI Navigation (`NavMeshSurface`), Test Framework,
  Recorder, Netcode for GameObjects, glTFast.

## Commands
Close the editor first, or batch mode fails with "another Unity instance is running with this project open".
```bash
Unity -batchmode -nographics -projectPath . -runTests -testPlatform EditMode -testResults results/editmode.xml -logFile -
Unity -batchmode -projectPath . -runTests -testPlatform PlayMode -testResults results/playmode.xml -logFile -
Unity -batchmode -quit -projectPath . -executeMethod BuildScript.BuildWindows -logFile -
```
- Don't add `-quit` to `-runTests`: it exits before the tests finish.
- `-logFile -` streams the log to stdout. A batch run with compile errors can still look "done", so search
  the log for `error CS`.
- A minimal build script (`Assets/Editor/BuildScript.cs`):
  ```csharp
  using System.Linq;
  using UnityEditor;
  using UnityEditor.Build.Reporting;

  public static class BuildScript {
      public static void BuildWindows() {
          var scenes = EditorBuildSettings.scenes.Where(s => s.enabled).Select(s => s.path).ToArray();
          var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions {
              scenes = scenes, locationPathName = "Builds/Windows/Game.exe",
              target = BuildTarget.StandaloneWindows64, options = BuildOptions.None });
          EditorApplication.Exit(report.summary.result == BuildResult.Succeeded ? 0 : 1);
      }
  }
  ```
- Built players accept `-batchmode -nographics` too (servers and headless sims), and your own arguments via
  `System.Environment.GetCommandLineArgs()`.

## Debug hooks and oracles
- **Tests:** the Unity Test Framework. EditMode tests cover rules; PlayMode tests (`[UnityTest]` coroutines
  that `yield return null` for frames) cover behaviour in scenes. An unexpected `Debug.LogError` fails a
  test by default (`LogAssert`). The Input System's `InputTestFixture` presses virtual devices.
- **Dev-only code:** `#if UNITY_EDITOR || DEVELOPMENT_BUILD`, or check `Debug.isDebugBuild`.
- **Screenshots:** `ScreenCapture.CaptureScreenshot(path)` needs a graphics device (not `-nographics`). For
  exact framing, render a camera into a `RenderTexture`, then `ReadPixels` and `EncodeToPNG`.
- **Logs:** Editor `%LOCALAPPDATA%\Unity\Editor\Editor.log`; player
  `%USERPROFILE%\AppData\LocalLow\<company>\<product>\Player.log`. Hook `Application.logMessageReceived`
  to fail autotests on errors.
- **Agent bridge:** a `TcpListener` on `127.0.0.1` on a background thread, handing commands to a main-thread
  queue, because Unity's API is main-thread only.
- **CI:** GameCI (`game-ci/unity-test-runner@v4`; `game-ci/unity-builder`, now v6 with v4 still patched).
  It needs the user's license as repository secrets: `UNITY_LICENSE` (Personal) or `UNITY_SERIAL` (Pro),
  plus `UNITY_EMAIL` and `UNITY_PASSWORD`.

## Pitfalls
- **Input inside `FixedUpdate`:** `GetKeyDown` there drops presses. Read in `Update` and buffer.
- **Serialization rules:** fields must be public or `[SerializeField]`; properties and plain dictionaries
  aren't serialized.
- **Lookups:** cache `GetComponent` results. Use `FindFirstObjectByType`; `FindObjectOfType` is
  deprecated.
- **Domain reload** after every script change slows iteration. Enter Play Mode options help, but then static
  state must be reset manually.
- **IL2CPP code stripping** removes code only reached by reflection; protect it with `link.xml` or
  `[Preserve]`.
- **License activation** in batch mode on a new machine or CI needs the user's credentials. Ask; never
  guess or store them.
