---
name: game-feel
description: Make a working game feel good to play. Covers responsive controls (input buffering, coyote time, acceleration curves), impact (hit-stop, screen shake, knockback, flashes, particles, rumble), layered sound, animation principles (anticipation, squash and stretch, follow-through), camera work, easing and tweens, UI juice, readability and telegraphs, fast retries, onboarding in the first minute, and pacing. Every effect stays tunable and can be switched off for accessibility. Use when the user says the game "feels flat", "floaty", "stiff", "unresponsive", "boring" or "cheap", asks for juice, polish or game feel, wants combat, movement, jumping, shooting or menus to feel more satisfying, or when the core loop works and a trailer or playtest is coming up.
---

# Game feel

Feel is the part of game development an agent is worst placed to judge: you can't hold the controller. So
work like a careful sound engineer with a client in the room:
1. **Make every effect a named tunable** in the tuning file, with a global multiplier and an off switch.
2. **Apply the proven recipes** below at conservative values.
3. **Measure what can be measured:** frames from press to response, time from death to control, hit-stop
   in milliseconds, frame time with every effect on.
4. **Show the human a before/after clip** and let them choose. Change one thing at a time.

Polish comes after function. Juice amplifies everything, including what's broken. If the graybox isn't fun,
fix the mechanic first (make-any-game, step 3).

## 1. Controls first: responsiveness
- **Respond on the frame of the input.** The player's own movement never waits for a wind-up animation
  (heavy weapons are the deliberate exception). Measure input-to-visible-change in frames with a scripted
  input and a state dump.
- **Acceleration curves:** snappy starts and stops on the ground, reduced control in the air, a hint of
  overshoot for weight.
- **Forgiveness that players never notice:** coyote time, jump buffering, corner correction, ledge
  forgiveness. Give player attacks generous hitboxes and the player a tight hurtbox, so it feels fair.
- **Variable jump height, apex hang, fast fall,** with the numbers in `make-any-game/references/genres.md`.
- **Input buffers and cancel windows** for attacks and dodges, so mashing feels intentional rather than
  ignored.
- **Gamepad aim assist:** subtle magnetism and slowdown near targets.

## 2. Impact: selling a hit
Layer these, roughly in order:
1. **Hit-stop (freeze frames):** 30-100 ms (2-6 frames), scaled with damage, on both attacker and target.
   Global time scale freezes everything, including particles and some audio. A per-entity freeze (pause just
   the two involved) is often better.
2. **Flash:** the target goes white or tinted for 1-2 frames.
3. **Knockback and reaction:** push along the hit direction; the enemy staggers or recoils.
4. **Screen shake, trauma-based:** each event adds "trauma" (0-1); shake amount = trauma² (or ³) × the max
   offset and rotation; trauma decays at 1-2 per second. Sample smooth noise (Perlin or simplex) instead of
   fresh random offsets every frame. Keep translation to a few percent of the screen and rotation to a few
   degrees. Add a small zoom punch in 2D.
5. **Particles:** a burst at the contact point, aligned with the hit direction. Leave debris, shells and
   decals for a while: permanence makes the world remember the fight.
6. **Sound:** layered (a sharp transient, a body, a tail), pitch varied ±5-10%, volume by intensity. Duck
   everything else briefly for the biggest hits.
7. **Optional:** damage numbers (pooled and readable) and gamepad rumble proportional to impact.

Kills get a bigger version of the same: a longer freeze, a lingering corpse or debris, and a sound sting.

## 3. Animation and motion
- **Anticipation → action → follow-through.** A short wind-up makes an attack readable; follow-through makes
  it feel heavy. The classic principles of animation (squash and stretch, slow in and out, arcs, secondary
  motion, exaggeration) apply to code-driven motion too.
- **Squash and stretch** on jump and land (about 1.2 / 0.8 scale for ~0.1 s, preserving volume), with landing
  dust.
- **Never move UI or cameras linearly.** Ease out on arrival, ease in on departure, and use back or elastic
  easing for playful pops.
- **Procedural life:** lean the body slightly into velocity, add bob and sway, and drive trailing parts
  (capes, antennae, tails) with damped springs.

## 4. Camera
- Frame-rate-independent smoothing, look-ahead toward movement or aim, and framing that keeps combat
  targets in view.
- Zoom punches on big events. A brief slow motion on the final kill (0.2-0.5 s at 0.2-0.3× speed).
- No unmotivated camera roll. Respect the player's motion settings.

## 5. Audio
- Every player action makes a sound, and every important event has a distinct one. Vary, limit concurrency,
  duck the music under big moments.
- Music can carry intensity layers that rise with the action.
- UI has sounds too (hover, confirm, back).
- A moment of silence before a big reveal hits harder than more noise.

## 6. UI juice
- **Buttons:** grow ~1.05× on hover, shrink ~0.95× on press, with a sound.
- **Motion:** panels slide or fade in with 0.15-0.3 s easing; numbers count up; health bars show a delayed
  "ghost" segment for chip damage; notifications pop with a slight overshoot.
- **Menus stay fast:** never block input behind an animation longer than ~0.3 s, and make every transition
  skippable.

## 7. Readability and fairness
- **Telegraphs:** enemies announce attacks 0.3-1 s ahead (a wind-up pose, a flash, a sound, a ground marker).
  Danger always uses the same colours.
- **Contrast:** characters and threats stand out from backgrounds by value (darker or desaturated
  backgrounds). Projectiles never look like pickups.
- **Death explains itself:** freeze on the killing blow, highlight the killer, show what hit them.
- **Fast retries:** under 1 second from death to control in skill-based games, checkpoints placed
  generously, and no unskippable scenes on retry.

## 8. The first minute
- Teach by doing: a safe space to try the core verb, with level geometry that requires it.
- Introduce one thing at a time, then combine.
- Minimal text: contextual prompts with the right device glyphs.
- The first success within 10-30 seconds.

## 9. Pacing and difficulty
- Alternate tension and release, and give the player rest moments.
- Introduce a mechanic, test it, then combine it with earlier ones.
- Offer assists openly (or adjust difficulty subtly).
- Measure deaths and time per section with bots and playtests; spikes in either are where the pacing
  breaks.

## 10. Verify the feel
- **Numbers:** input-to-motion latency in frames, death-to-control time, hit-stop duration, the shake curve,
  and frame time with every effect at maximum (particles and post-processing are the usual performance
  hogs).
- **Clips:** record a before/after pair (the trailer-video skill's capture tools) and a contact sheet. Ask the
  human "A or B?" and log the answer in `DEVLOG.md`.
- **Accessibility pass:** with shake at 0 and flashes reduced, the game must still read clearly.

## Engine hooks
| Effect | Godot | Unity | Unreal | Web |
|---|---|---|---|---|
| Tweens | `create_tween()` | DOTween, PrimeTween or LitMotion; coroutines | Timelines; `FMath::FInterpTo` | Phaser `this.tweens.add`; GSAP |
| Hit-stop | `Engine.time_scale`, or pause the two nodes | `Time.timeScale` + unscaled timers, or per-object pause | `SetGlobalTimeDilation`, or per-actor `CustomTimeDilation` | skip N update ticks |
| Shake | `Camera2D/3D` offset driven by `FastNoiseLite` | Cinemachine Impulse | Camera Shake classes via the player camera manager | Phaser `cameras.main.shake()`; offset the camera in three.js |
| Particles | `GPUParticles2D/3D`, `CPUParticles2D/3D` | VFX Graph, Particle System | Niagara | Phaser particle emitters; three.js `Points` or instancing |
| Rumble | `Input.start_joy_vibration()` | `Gamepad.current.SetMotorSpeeds()` | Force Feedback effects | `gamepad.vibrationActuator.playEffect()` |

## Further reading (the canon)
- Steve Swink, *Game Feel* (2008).
- Jan Willem Nijman, "The Art of Screenshake" (2013 talk).
- Martin Jonasson & Petri Purho, "Juice it or lose it" (2012 talk).
- Squirrel Eiserloh, "Juicing Your Cameras With Math" (GDC 2016).
- Kyle Pittman, "Building a Better Jump" (GDC 2016).
