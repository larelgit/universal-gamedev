---
name: trailer-video
description: Capture and cut a game trailer, a gameplay clip, a devlog GIF or store screenshots for a game you're making. Covers a deterministic trailer mode (scripted camera, fixed seed, HUD toggle, slow motion), in-engine capture at a fixed frame rate (Godot Movie Maker, Unity Recorder, Unreal Movie Render Queue/Graph, canvas capture on the web), window capture with only the game's audio on Windows, picking moments from contact sheets, and editing with one-line titles, music, transitions and an end card via an EDL. Also covers export settings for Steam, itch.io and social posts, including vertical 9:16 cuts. Use when the user wants a trailer, teaser, gameplay video, GIF, clip, devlog video, store screenshots or a montage of their game.
---

# Trailer and clips

A game isn't finished until you can show it in 30 seconds. Owning the source makes this much easier than
it is for a modder: you can build a **trailer mode** into the game and capture frames inside the engine at a
fixed rate, so heavy effects never stutter on video. The editing half (contact sheets, EDL, titles) is
universal-modder's `um video` toolchain, and the style rules come from its showcase-video skill.

## 1. Build a trailer mode (once)
A `--trailer` launch flag (or a dev menu) that gives you:
- **a fixed seed and scripted action:** spawn waves, cue the boss and trigger the set pieces from a shot
  list, so a reshoot after a fix is one command;
- **camera control:** a free or photo camera, plus spline paths for fly-throughs, with smoothing;
- **HUD on/off,** god mode, slow motion on a key, a time-of-day control;
- **a shot list as data,** e.g. `shots.json` with the scene, seed, camera path, duration and actions for each
  shot.

Restore or regenerate the world before every take, because explosions, deaths and pickups change it.

## 2. Capture
**In the engine, at a fixed frame rate (best quality, deterministic):**
- **Godot:**
  ```bash
  godot --path . --write-movie captures/shot1.avi --fixed-fps 60 -- --trailer --shot boss_intro
  ```
  This is Movie Maker mode: it renders every frame at the fixed rate however slow rendering is, with the
  audio mixed in sync. Output is AVI (MJPEG), OGV (Godot 4.5+), or a PNG sequence plus WAV when the path
  ends in `.png`. The project settings under `editor/movie_writer/` set quality and audio.
- **Unity:** the Recorder package (`com.unity.recorder`). Record the Game view to MP4, ProRes or image
  sequences, and drive it from Timeline with a Recorder track for scripted shots. It works in the editor's
  Play mode, not in builds.
- **Unreal:** Sequencer with the Movie Render Queue / Movie Render Graph for cinematic shots (anti-aliasing
  samples, high resolution, image sequences). For raw gameplay, use window capture.
- **Web:** `canvas.captureStream(60)` with `MediaRecorder` saves WebM from inside the page. Playwright's
  `recordVideo` is fine for quick checks but too low quality for a trailer.

**From outside, on Windows (any build):**
```bash
um win record --exe Game.exe --out C:\caps\take1 --seconds 40    # gfxcapture of the window + process-loopback audio of the game only
um video first-frame C:/caps/take1.mkv                            # where real gameplay starts
um video mux C:/caps/take1.mkv C:/caps/take1.audio.raw C:/caps/take1.json take1.mp4 [--offset 0.25]
```
- **Video** is the game window only (GPU frames, no desktop or notifications), encoded with NVENC, AMF or
  QSV when available. NVENC H.264 tops out at 4096 px wide, so crop ultrawide captures to 16:9 (`--crop`).
- **Audio** is a WASAPI process-loopback capture of the game's PID, timestamped for muxing. Fine-tune sync
  with a visible-and-audible event (a flash and its boom) via `--offset`.
- **OBS** works on every OS when neither option fits.

## 3. Look before you cut
```bash
um video probe clip.mp4
um video contact clip.mp4 sheet.png --every 1.5 --cols 6        # timestamped grid: read it, pick in/out points
um video contact clip.mp4 zoom.png --start 20 --end 30 --every 0.5
```
Pick the peaks: the core verb landing, the biggest hit, the boss reveal, the best-looking vista. Write the
in/out times into the EDL.

## 4. Edit with an EDL
`um video compile edl.json trailer.mp4` (`--preview` renders at half size, quickly). The full format is in
`um video --help`.
```json
{
  "size": [1920, 1080], "fps": 60,
  "theme": {"accent": "#FFB000"},
  "transition": {"type": "fade", "duration": 0.25},
  "clip_volume": 0.7,
  "music": {"path": "assets/gen/trailer_music.mp3", "volume": 0.6},
  "segments": [
    {"clip": "shot_boss.mp4", "in": 2.0, "dur": 2.5, "hook": "Keep the sea monsters off the rocks."},
    {"clip": "shot_core.mp4", "in": 0.5, "dur": 4.0, "title": "Aim the lighthouse beam"},
    {"clip": "shot_upgrades.mp4", "in": 1.0, "dur": 3.5, "title": "Build a stranger lighthouse every night"},
    {"clip": "shot_boss.mp4", "in": 6.0, "dur": 4.0, "title": "Survive until dawn"},
    {"card": {"title": "Beacon", "sub": "Wishlist on Steam"}, "dur": 2.5}
  ]
}
```
- **Transitions:** any ffmpeg xfade type (fade, pixelize, slideleft, circleopen, zoomin...), or `cut`.
- **Per clip:** `speed`, `volume`, `zoom` (punch in past UI), `crop` [x, y, w, h], and `fill`
  (`blur`/`crop`/`pad`) for clips that aren't 16:9.
- **Music:** `um fal music "<mood>, <tempo> bpm, builds to a climax" --seconds 60` makes a bed (the
  game-assets skill). Set `bpm` and use `beats` instead of `dur` to cut on the beat; `um video beats
  music.mp3` estimates tempo and the first beat.

## Structure and style that work
- **Hook in 2-3 seconds:** the strongest gameplay moment first. No logos, no slow fade-ins. Many viewers see
  the first seconds muted in a feed, so they have to read visually.
- **Show the core verb, then variety, then escalation.** End on the name, a call to action ("Wishlist now",
  "Play free on itch.io") and the URL, then fade out.
- **Pace:** clips of 3-5 s; 30-60 s for a store trailer, 15-30 s for social.
- **Titles:** one line naming what's on screen. How it was made belongs in the post text, not over the
  footage.
- **Real gameplay:** stores and players punish trailers that don't look like the game. Keep the game's own
  sound effects in; they sell the impacts.
- **Last step:** look at a contact sheet of the finished video before handing it over.

## Formats and exports
- **Steam trailers:** up to 1920×1080 (16:9 preferred), H.264 + AAC in `.mp4`, 5,000+ kbps, 30 or 60 fps.
  Screenshots are at least 1920×1080, 16:9, at least 5 of them. Take them in trailer mode with the HUD on:
  players want to see the game as they'll play it. Sizes are in
  `skills/ship-game/references/stores.md`.
- **Vertical cuts (9:16)** for Shorts, TikTok and Reels: `"size": [1080, 1920]` with `fill: blur`, or reframe
  with `crop`. Put titles in the middle third, clear of app UI.
- **Devlog GIFs:** short loops (3-8 s) of one feature:
  ```bash
  ffmpeg -i clip.mp4 -vf "fps=15,scale=640:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" out.gif
  ```
- **Footage you didn't make** (other games, other creators) doesn't belong in your trailer. Credit
  collaborators on screen and in the post.
