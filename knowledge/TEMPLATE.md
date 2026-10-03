---
# Field note: how a game (or a feature) was built, written so the next agent can repeat it. Keep the keys; delete the comments.
kind: project
title: "A survivors-like in Godot 4 that keeps 1,000 enemies at 60 fps"   # what you built or learned, in plain words
game: "Beacon"                                       # the game's title or working title
genre: "survivors-like"                              # see skills/make-any-game/references/genres.md
engine: godot                                        # ugd scan's engine key (godot, unity, unreal, phaser, threejs, bevy, love2d, pygame, monogame, ...) or unknown
engine_version: "Godot 4.5.1 stable, GDScript"       # the exact build that worked
platforms: [windows, web]                            # windows | macos | linux | web | android | ios | console
tools: ["GUT 9.4", "um fal (gpt-image-2)", "Playwright"]
status: working                                      # idea | prototype | working | released | abandoned
agents: ["Claude Code (Opus 5.5)"]                   # agent + model that did the work
humans: []                                           # handles of the humans involved, if they want credit
date: 2026-10-02
links: []                                            # repo, playable build, video, post
tags: []                                             # free-form: performance, pooling, multimesh, web-export, ...
---

# A survivors-like in Godot 4 that keeps 1,000 enemies at 60 fps

> Two to four sentences: what you built, with which engine, and whether it runs in a real build (and how you
> know).

## Setup
Engine version, OS, plugins and addons with versions, SDKs, anything installed first. The versions that
worked are the most useful thing you can write down.

## Architecture
How it's put together: scenes or entities, data files, state machines, the tuning file, debug hooks, the
agent bridge. What you'd keep and what you'd change.

## Verification
How you knew it worked: the oracles (unit tests, headless simulations, screenshots you looked at, golden
images, replays, bots, playtests with the human), and what you did NOT verify.

## Gotchas
The most valuable section. Numbered; each one symptom → cause → fix.
1. **Symptom.** What you saw. **Cause:** what it really was. **Fix:** what worked.

## Assets
How art, audio and 3D were made (models, prompts, `um` commands) and their licenses, if any.

## Build and release
Export commands, platform quirks, store steps that mattered.

## Cost and time
Optional: wall-clock time, sessions, API spend.

## Open questions
What's unresolved, or the next step.
