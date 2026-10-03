# Genre recipes

Each recipe covers the core loop, the **slice to build first**, starting numbers, the systems that come
after the slice, the traps, and an **oracle** that proves it works. The numbers are starting points to tune
with the human, not truths: put them in the tuning file and change them there.

Units: "tiles" assume a 16 px tile in pixel art; "m" is 1 world unit in 3D engines. At 60 fps, a frame is
16.7 ms.

## Contents
- [Platformer (2D)](#platformer-2d)
- [Top-down action / twin-stick shooter](#top-down-action--twin-stick-shooter)
- [Survivors-like (bullet heaven)](#survivors-like-bullet-heaven)
- [Roguelike / roguelite](#roguelike--roguelite)
- [Metroidvania](#metroidvania)
- [Tower defense](#tower-defense)
- [RTS](#rts)
- [Turn-based tactics and strategy](#turn-based-tactics-and-strategy)
- [Deckbuilder / card game](#deckbuilder--card-game)
- [Puzzle (grid and logic)](#puzzle-grid-and-logic)
- [Match-3](#match-3)
- [Idle / incremental](#idle--incremental)
- [Visual novel / narrative](#visual-novel--narrative)
- [Racing](#racing)
- [First-person shooter](#first-person-shooter)
- [Third-person action / soulslike](#third-person-action--soulslike)
- [Fighting game](#fighting-game)
- [Rhythm](#rhythm)
- [Management, sim, city builder](#management-sim-city-builder)
- [Survival, crafting, sandbox](#survival-crafting-sandbox)
- [Endless runner / hyper-casual](#endless-runner--hyper-casual)
- [Physics puzzler / sandbox](#physics-puzzler--sandbox)
- [Local multiplayer / party](#local-multiplayer--party)

---

## Platformer (2D)
- **Loop:** run, jump, avoid hazards, reach the goal.
- **Slice:** one screen of test geometry. Walk, jump, fall, land, one hazard that kills, one goal that
  wins, instant respawn.
- **Starting numbers:**
  - **Jump: design by height and time, then derive the physics.** Gravity `g = 2h / t²`, launch speed
    `v = 2h / t`, with `h` the jump height and `t` the time to apex. Start at h = 3-4 tiles and
    t = 0.35-0.45 s.
  - **Falling:** gravity × 1.5-3 on the way down, and cap fall speed (terminal velocity).
  - **Variable jump height:** when the button is released while rising, multiply the upward velocity by
    0.4-0.5 (or switch to the fall gravity).
  - **Forgiveness:** coyote time 0.08-0.12 s (jump just after leaving a ledge), a jump buffer of
    0.1-0.15 s (a press just before landing still jumps), and corner correction (nudge a few pixels past a
    ceiling corner).
  - **Apex hang:** halve gravity while |vertical speed| is small, for a moment of control at the top.
  - **Run:** max speed 6-10 tiles/s. Reach it in 0.1-0.2 s on the ground and stop within 0.05-0.1 s. Air
    control is 0.5-0.8× ground acceleration.
  - **Camera:** a dead zone, look-ahead in the facing direction, and vertical "platform snapping" (only
    move the camera's Y when the player lands).
- **After the slice:** checkpoints, enemies (patrol, chase, shoot), collectibles, a level format
  (Tiled/LDtk or the engine's tilemap), moving platforms (the rider inherits the platform's velocity),
  one-way platforms. Add slopes only if the design needs them: they're the most bug-prone part.
- **Traps:**
  - A dynamic physics body as the player feels floaty and slides. Use a kinematic character controller
    (Godot `CharacterBody2D`, a raycast controller in Unity, your own in code-first engines).
  - Jump height that changes with frame rate. Integrate in a fixed step, or use the exact formula.
  - Snagging on seams between tile colliders. Merge colliders (Unity `CompositeCollider2D`, Godot
    tilemap physics layers) or use slightly rounded feet.
  - Camera jitter: physics moves in fixed steps and the camera in render frames. Interpolate.
- **Oracle:** scripted input. "Hold right for 1 s and jump at 0.5 s" should reach the apex at 3 tiles
  ± 0.1 at t ≈ 0.4 s, every run. Replay a recorded human run of each level to prove it's still completable
  after changes.

## Top-down action / twin-stick shooter
- **Loop:** move, aim, shoot, dodge; clear rooms or waves.
- **Slice:** a player that moves in 8 directions with analog support, one weapon, one enemy type that
  chases and one that shoots, one arena, death and restart.
- **Starting numbers:** normalize diagonal input. Use a dash with invulnerability frames (0.15-0.25 s,
  cooldown 0.5-1 s). Fire rate 5-12 shots/s for automatics. Bullets should cross the screen in 0.5-1 s so
  they're readable. Enemy attacks need a wind-up "tell" of 0.3-0.6 s (flash, pose or sound) before
  they fire.
- **After the slice:** rooms or waves as data, pickups, weapons as data (rate, spread, speed, damage,
  pierce), a gamepad aim assist (slight magnetism on the right stick), a boss with telegraphed phases.
- **Traps:** a scene node per bullet costs too much with hundreds of them (pool them, or draw them from one
  manager); mouse aim needs a screen → world conversion; unreadable bullet colours against the floor.
- **Oracle:** a headless arena fight with a bot that strafes and shoots: time-to-kill and damage taken stay
  within bands. A stress scene with 500 bullets stays under the frame budget.

## Survivors-like (bullet heaven)
- **Loop:** you only move; weapons fire on their own. Kills drop XP gems, a level-up offers 1 of 3-4
  upgrades, and you survive N minutes (a jam version needs 5-10 minutes; classics run 15-30).
- **Slice:** movement, one auto-weapon, one enemy type spawning in rings off-screen, XP gems with a magnet
  radius, a level-up screen with 3 random upgrades, and a timer.
- **Starting numbers:** the first level-up arrives within 10-20 s. XP per level grows roughly linearly
  early (e.g. `5 + 10·level`), then steeper. A *wave director* keyed on elapsed time sets spawn rate and
  enemy mix per minute; an elite or boss arrives every 3-5 minutes. Late game shows 200-1,000 enemies.
- **After the slice:** weapons and upgrades as data with tags, evolutions (weapon + passive → upgraded
  weapon), chests, meta-progression between runs (gold → permanent stats), characters.
- **Traps:** performance is the genre's real enemy.
  - No per-enemy physics bodies pushing each other. Use a spatial hash grid for proximity and simple
    separation steering.
  - Pool enemies, projectiles, gems and damage numbers.
  - Batch the drawing (Godot `MultiMeshInstance2D`, GPU instancing, sprite batching).
  - Avoid per-frame allocations (GC spikes).

  Readability is the other enemy: too many particles bury the enemies.
- **Oracle:** a headless 10-minute run with a kiting bot (move away from the nearest enemies, grab gems),
  logging level-up times and time of death per build. A 1,000-enemy stress scene with a frame-time
  assertion.

## Roguelike / roguelite
- **Loop:** run through generated floors, die or win, then (in a lite) spend meta-currency and start a
  new run.
- **Slice:** one generated floor (rooms + corridors), a player, one enemy type, stairs down, death →
  new seed.
- **Must-haves:**
  - **Seeded generation.** Log the seed and accept `--seed`, so any bug can be reproduced. Use separate RNG
    streams (layout, loot, combat) so a change in one doesn't reshuffle the others.
  - **A validator** that runs on every generated floor: everything is connected, start → exit exists, keys
    come before their locks, nothing spawns inside walls.
  - Difficulty as a function of depth.
- **Generation recipes:**
  - BSP rooms + corridors;
  - drunkard's walk or cellular automata for caves;
  - hand-made prefab rooms stitched on a grid (Spelunky-style), which reads well and is easy to validate;
  - Wave Function Collapse for tile adjacency.

  Place content after the layout using a distance-from-start map (a "Dijkstra map").
- **Turn-based roguelikes:** an energy/speed scheduler, shadowcasting field of view, and input as
  commands (which makes replays and undo trivial).
- **Traps:** hidden unseeded randomness (shuffles, hash-map iteration order, `Math.random`), floors that can
  softlock, runs too long to test (add a fast-forward or turbo flag).
- **Oracle:** generate 1,000 seeds headless and assert the invariants; a bot that walks to the exit on each.

## Metroidvania
- **Loop:** explore a connected map, gain abilities that open new paths, backtrack, fight bosses.
- **Slice:** the full movement controller, one ability gate (e.g. double jump opens a ledge), and a
  5-10 room graph with one lock and key, room transitions and a save room.
- **Must-haves:** a room graph as data, with the ability each connection requires. A graph search proves
  every room is reachable in the intended order and that no ability state can strand the player.
  Persistent world state (doors opened, bosses killed, items taken), map discovery, save/load.
- **Traps:** softlocks (a one-way drop without the ability to climb back), camera bugs at transitions, and
  content explosion (scope it to a small map with dense secrets).
- **Oracle:** the reachability search over the room graph runs as a test on every content change; replay a
  recorded route through the whole map.

## Tower defense
- **Loop:** enemies walk a path; you place and upgrade towers with currency; waves escalate.
- **Slice:** one path, one tower type, one enemy type, 5 waves, currency and placement.
- **Starting numbers:** wave 1 is beatable with 1-2 towers. Enemy HP grows 10-20% per wave, and new enemy
  types arrive every few waves. Income per wave and per kill. Targeting modes: first, last, strongest,
  closest.
- **Pathing:** a fixed path (waypoints or a spline), or maze-building (recompute A* or a flow field when a
  tower is placed, and reject placements that would seal the path).
- **Traps:** projectiles missing fast enemies (home in, or hitscan with travel visuals); overkill (track
  incoming damage so towers don't all shoot one enemy); projectile count in late waves.
- **Oracle:** simulate waves headless with a scripted tower layout and assert which waves are beatable.
  Plot DPS against HP per wave.

## RTS
- **Loop:** gather, build, train, command, destroy the enemy base.
- **Slice:** box-select and right-click move for 10 units with pathfinding and local avoidance, one
  resource, one building that trains one unit.
- **Systems:** pathfinding for many units (navmesh, or flow fields once groups get large), steering and
  avoidance (RVO or boids), command queues, formations, grid-based fog of war, a minimap, an AI opponent
  (build orders + a state machine).
- **Multiplayer:** RTS games classically use deterministic lockstep: send commands, not state. That needs
  a deterministic simulation (fixed-point maths, or very careful floats, and a fixed command order). Decide
  this before writing the simulation (see `multiplayer.md`).
- **Traps:** pathfinding cost spikes (time-slice requests, hierarchical paths), units jittering and clumping
  at the goal, selection that feels sticky.
- **Oracle:** an AI-vs-AI match headless to completion; determinism checksums per tick if multiplayer.

## Turn-based tactics and strategy
- **Loop:** move units on a grid, attack, use abilities, end the turn; the AI responds.
- **Slice:** one map, 3 units per side, move + attack, a damage preview, a simple AI, win/lose.
- **Systems:** square or hex grids (hex: axial/cube coordinates; Red Blob Games' guide is the reference),
  movement ranges with Dijkstra and terrain costs, line of sight, cover, actions as command objects (this
  gives undo, replays and AI search for free), and AI that scores candidate actions (utility).
- **Traps:** unclear UI (always show reachable tiles, hit chance and predicted damage), slow AI turns (cap
  the search and spread it over frames), RNG that feels unfair (show the true odds; decide deliberately
  whether to fudge).
- **Oracle:** rules unit tests (damage, ranges, LoS); AI-vs-AI games headless to completion.

## Deckbuilder / card game
- **Loop:** draw a hand, play cards with energy, resolve effects, enemies act on shown intents, end the
  turn. Between fights: add or remove cards, gain relics, choose a path on a branching map.
- **Slice:** a 10-card starter deck, 3 energy, a 5-card hand, one enemy with intents, rewards after the
  fight.
- **Cards are data:** id, cost, type, target, and an effect list such as
  `[{"op": "damage", "amount": 6}, {"op": "apply", "status": "vulnerable", "stacks": 2}]`. Effects resolve
  through an **action queue**. Statuses and relics hook events (`on_play`, `on_damage`, `on_turn_start`).
  Logic resolves instantly and emits events; the presentation animates the event log afterwards.
- **Seeded RNG streams** for the map, rewards and shuffles, so runs are reproducible.
- **Traps:** effect-ordering bugs, infinite combos (cap the loop depth), animation and logic out of sync,
  outlier cards (find them by simulation, not by feel alone).
- **Oracle:** a unit test per card and status; thousands of simulated fights with simple bots, flagging
  cards whose win-rate delta is an outlier; replays of action logs.

## Puzzle (grid and logic)
- **Loop:** a small rule set, a level, solve it, next.
- **Slice:** the rules, 3 levels, instant undo and restart.
- **Must-haves:**
  - **Levels as text** (ASCII grids). They're readable, diffable and agent-friendly.
  - **An undo stack.** Snapshot the whole state; it's cheap for small grids.
  - **A solver** (BFS/A*) that proves every level is solvable and reports the minimum number of moves. Use
    that number as a difficulty proxy to order levels.
  - Teach each rule with a level built for it before combining rules.
- **Traps:** unsolvable states the player can't see (offer undo or detect deadlocks), rules that are never
  taught, key-repeat that makes the player overshoot.
- **Oracle:** the solver runs over every level as a test; stored solutions replay correctly after every
  rules change.

## Match-3
- **Loop:** swap, match 3+, clear, gravity, refill, cascades; level goals and a move limit.
- **Slice:** an 8×8 board, 5 colours, swap, match, gravity, refill, a score.
- **Must-haves:** a deterministic resolution order. Generate the initial board with no ready-made matches,
  detect "no moves left" and shuffle, and create specials from 4- and 5-matches.
- **Traps:** animation and logic desync (resolve logic step by step and animate the events), input during
  cascades (lock it or queue it).
- **Oracle:** board logic unit tests; a random-play bot doing 10,000 moves without a crash, an invalid
  state or a stuck board.

## Idle / incremental
- **Loop:** generators produce currency, currency buys more generators, and a prestige reset trades
  progress for a permanent multiplier.
- **Slice:** one currency, 3 generators with exponential costs, a buy button, number formatting, save and
  offline progress.
- **Starting numbers:** `cost_n = base × growth^n` with growth 1.07-1.15 (Cookie Clicker buildings use
  1.15). Milestone purchases double output. Prestige currency scales sub-linearly (e.g. the square root of
  lifetime earnings).
- **Big numbers:** doubles reach ~1.8e308. Past that, use a mantissa + exponent type (break_infinity.js or
  a port). Format as K/M/B, then scientific.
- **Offline progress:** on load, take elapsed real time, cap it, and compute the gains in closed form or in
  coarse steps.
- **Traps:** walls where nothing is affordable for too long (plot time-to-next-purchase), save corruption
  (autosave with a backup copy), floating-point drift in long sums.
- **Oracle:** simulate 24 hours of play with a greedy buyer bot and plot the time between purchases; it
  should stay within a band, without walls.

## Visual novel / narrative
- **Tools:** Ren'Py; or Ink / Yarn Spinner inside another engine (`narrative.md`).
- **Slice:** one scene with two characters, one choice that changes a variable, one later line that
  depends on it, save/load and rollback.
- **Systems:** branching with flags, choices, history log, auto and skip, text speed, save anywhere,
  localization-ready strings.
- **Traps:** combinatorial branch explosion (use flags and converge branches), branches nobody tested,
  missing images on rare paths.
- **Oracle:** traverse the story graph headless (every choice, or random walks for big graphs). Assert that
  every node is reachable, there are no dead ends and no missing assets. Run the engine's lint.

## Racing
- **Loop:** drive laps or a course against time or rivals.
- **Slice:** one car, one test track, checkpoints, a lap timer.
- **Arcade or sim:** arcade uses a velocity-based controller with a "drift factor" (blend velocity toward
  the facing direction), boost and mild rubber-banding. Sim uses raycast or wheel-collider suspension and a
  tyre model. Decide first.
- **AI:** follow a racing-line spline with look-ahead, with target speed from upcoming curvature.
- **Traps:** tunnelling at high speed (continuous collision detection), physics that changes with frame rate
  (fixed step), a jittery chase camera (smooth it, add speed-based FOV), checkpoint skipping.
- **Oracle:** an AI car laps the track headless within a time band; a lap is only counted through all
  checkpoints in order.

## First-person shooter
- **Slice:** a first-person controller (mouse look, WASD, jump, crouch), one hitscan weapon with feedback,
  a target dummy, and one blocked-out room.
- **Starting numbers:** default horizontal FOV 90 on PC with a slider; run speed 5-7 m/s; sensitivity in
  settings; hitscan from the camera centre (visuals from the muzzle); a headshot multiplier; projectiles
  for slow weapons.
- **Feel:** view-model recoil plus camera kick, muzzle flash, hit markers with sound, enemy hit reactions.
  See the game-feel skill.
- **AI:** navmesh movement, perception (sight cones + hearing), states (patrol, alert, attack, take
  cover), cover points marked in levels.
- **Traps:**
  - Don't multiply mouse delta by frame time: it's already a per-frame distance, and scaling it makes
    sensitivity depend on frame rate.
  - Camera jitter: update the camera in the render step and interpolate physics.
  - Shooting from the muzzle instead of the camera makes shots miss the crosshair.
- **Oracle:** scripted aim + fire at a dummy at known distances (hits, damage); a bot walks the level's
  navmesh to every spawn point.

## Third-person action / soulslike
- **Slice:** a third-person controller with a spring-arm camera, lock-on, a light attack, a dodge with
  invulnerability frames, stamina, and one enemy with two readable attacks.
- **Combat as data:** each attack has startup, active and recovery phases, with hitboxes live only during
  active frames, cancel windows, and an input buffer (~0.2 s). Enemy wind-ups of 0.4-1 s keep attacks
  readable. Hit-stop on impact.
- **Traps:** root motion fighting physics, hitbox timing tied to frame rate, the camera clipping through
  walls, lock-on switching that grabs the wrong target.
- **Oracle:** frame-accurate tests of attack phases; a headless duel with a scripted player bot (dodge on
  wind-up) to check that the attacks are avoidable.

## Fighting game
- **Must-haves:** fixed 60 Hz logic. Frame data per move: startup, active, recovery, and advantage on hit
  and on block. Hitboxes and hurtboxes per frame, an input buffer (3-8 frames), and a motion-input parser
  (quarter-circle and the like) with leniency.
- **Netcode:** rollback (GGPO-style) needs a deterministic simulation and fast save/load of the whole game
  state. Design for it from day one (`multiplayer.md`).
- **Traps:** non-deterministic logic (floats across machines, engine physics), rendering tied to logic.
- **Oracle:** frame-data unit tests; replay a recorded match and compare a per-frame state checksum.

## Rhythm
- **Use the audio clock, not frame time.** Song position = audio playback time minus output latency;
  schedule notes and judge hits against it. In Godot, `AudioServer.get_time_since_last_mix()` and
  `get_output_latency()` (see "Sync the gameplay with audio and music" in the docs); in Unity,
  `AudioSettings.dspTime`; in Web Audio, `audioContext.currentTime` and `outputLatency`.
- **Calibration:** a screen that measures the player's input and audio offset (setups differ, and
  Bluetooth adds a lot).
- **Starting windows:** perfect ±30-50 ms, good ±80-100 ms, miss beyond ~150 ms.
- Charts are data files, with a recording tool to author them.
- **Traps:** drift from summing frame deltas, audio start delay, judging against video frames.
- **Oracle:** auto-play a chart with perfect timing and assert all "perfect"; feed jittered inputs and check
  that the judgement distribution matches the windows.

## Management, sim, city builder
- **Must-haves:** a simulation tick separate from rendering (e.g. 10-20 ticks/s, or per in-game hour), time
  controls (pause, 1×, 2×, 4×, which means the sim must run fast), economy sources and sinks, agents with
  needs (utility AI).
- **Traps:** thousands of agents (data-oriented layouts, ECS, time-slicing), a runaway economy, huge saves.
- **Oracle:** simulate N in-game days headless and assert invariants (no negative stock, bounded population,
  no stuck agents); plot resource curves.

## Survival, crafting, sandbox
- **Systems:** an inventory (slots, stacking, items defined as data), crafting recipes as data, needs
  meters, a day/night cycle, building placement (grid snapping and validity checks), resource respawns.
  Large worlds save in chunks, storing only changes from the generated baseline.
- **Traps:** item duplication (make inventory operations transactional), save bloat, scope.
- **Oracle:** inventory invariants (stack, split and merge conserve the total count); a recipe-graph test
  (every item is obtainable, and there are no unintended loops that create items from nothing).

## Endless runner / hyper-casual
- **Shape:** one-touch input, procedural chunks, speed that ramps, instant restart, portrait orientation,
  short sessions.
- **Traps:** frame pacing on low-end phones (cap at 60 or 30 fps), touch latency, safe areas and notches,
  battery drain.
- **Oracle:** a bot that survives N chunks at each speed tier; a performance run on the weakest target
  device.

## Physics puzzler / sandbox
- Use the engine's physics (Box2D, Jolt, Rapier, Godot Physics) and keep objects within about 0.1-10
  physics units in size. Raise solver iterations for stacks, and use continuous collision for fast objects.
- Engine physics is usually not deterministic across machines. For replays, record outcomes, or pick a
  physics library with an explicit determinism mode.
- **Oracle:** each level's stored solution replays to the win state on the same build; a stability test
  (stacks at rest stay at rest for 10 s).

## Local multiplayer / party
- **Must-haves:** gamepad assignment and a join screen, hot-plugging, a shared camera that zooms to fit
  everyone (or split screen), short rounds, and a quick rematch.
- Online play for a local game: Steam Remote Play Together, before writing netcode.
- **Oracle:** simulated devices joining and leaving mid-round; 4 bot players for a full match headless.
