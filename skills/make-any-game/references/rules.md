# Rules, with their reasons

These rules keep the user's project shippable, their accounts and machine safe, and their players
protected. None of this is legal advice. When IP, licensing or store terms matter for a commercial release,
read the actual terms, and suggest the user ask a lawyer when the stakes are high. Policies below were
checked in October 2026; stores change their rules, so re-check before a release.

## Original work: mechanics yes, expression no
- **What's free to use:** in the US, copyright doesn't protect ideas, methods or systems (17 U.S.C. §102(b);
  37 CFR 202.1(b)), so genres and game mechanics are generally free to use. Other countries are broadly
  similar.
- **What isn't:** the *expression* is protected: art, music, text, characters, names, level layouts, and
  the distinctive look and feel (trade dress). In *Tetris Holding v. Xio Interactive* (D.N.J. 2012), a
  clone lost because it copied the pieces' visual design and the overall look. "We only copied the rules"
  didn't save it. Trademarks protect names and logos, so another game's name never belongs in your title or
  store tags.
- **So "make X, but Y" means** the same genre and mechanics, with new names, characters, art, audio, UI and
  levels. Change the fiction and visual identity enough that nobody mistakes it for the original.
- **Fan games** are legally grey at best, and rights holders range from tolerant to aggressive. It's the
  user's call: don't use ripped assets, don't monetize, and expect takedowns.
- Never use leaked source code, builds or assets of any game. Remaking the user's *own* game is fine.

## Assets, licenses and credits
- **Every asset you didn't make from scratch** gets a line in `CREDITS.md`: name, source, author, license,
  and where it's used. Release review then takes five minutes instead of an afternoon of archaeology.
- **Cheat sheet:**

| License | Means |
|---|---|
| CC0 | no attribution required (credit anyway) |
| CC-BY | attribution required |
| CC-BY-SA | derived assets must carry the same license |
| CC-BY-NC | non-commercial only; avoid for anything that might be sold |
| OFL (fonts) | embed freely; don't sell the font on its own |
| MIT / BSD / zlib / Apache code | permissive; keep the notices |
| GPL / LGPL code | copyleft; can impose terms on the whole game; ask before using in a closed-source game |
| Asset stores (Unity Asset Store, Fab, itch packs) | read each license; usually "use in your game, don't redistribute raw" |

- **Engine notices:** Godot is MIT, so include its license notice (and its third-party notices) in your
  credits or docs. Unity and Unreal have EULAs with revenue thresholds or royalties: check the current terms
  for commercial releases.
- **Generated assets:** fal's terms don't expressly grant you ownership of outputs, and each model has its
  own license; fal marks commercial use per model. Record the model for each asset (`fal_manifest.jsonl`
  does this) and check its license before a commercial release. In the US, raw AI output without human
  authorship isn't copyrightable (Copyright Office guidance; *Thaler v. Perlmutter*). Human selection,
  editing and the game as a whole can be. Describe styles instead of naming living artists.

## AI disclosure and honesty
- **Steam** asks for AI disclosure in the Content Survey. Since its January 2026 rewrite, this covers
  AI-generated content that ships with the game or that players see, including store-page and marketing
  assets. Live-generated content needs a description of its guardrails. AI tools used only for development
  efficiency (code assistants) are explicitly out of scope.
- **itch.io** has had a "Generative AI disclosure" field since November 2024. "Yes" adds "AI Generated" tags
  per area (graphics, sound, text, code). It's mandatory for asset pages, and the quality guidelines expect
  every game that uses generative AI to be tagged; untagged ones can lose browse visibility.
- **Game jams:** many ban AI-generated assets. Read the jam's rules before generating anything for an entry.
- **Everywhere:** credit the tools in the game's credits and README. Never present generated work as
  hand-made, and never claim testing, platforms or playtests that didn't happen.

## Secrets and keys
- **Never commit or ship:**
  - `.env` files and API keys (fal, OpenAI, Anthropic, cloud providers);
  - Android keystores (`.jks`, `.keystore`) and their passwords;
  - Apple certificates and keys (`.p12`, `.p8`, `.mobileprovision`);
  - Windows signing certificates (`.pfx`);
  - Steam credentials (`config.vdf`, `ssfn*` files) and Steamworks web API keys;
  - service-account JSON.
- **A shipped client is public:** anything in the build can be extracted. Runtime AI features
  (live-generated content) call a server the user controls, which holds the key, rate-limits and moderates.
- `ugd release check` scans for the common patterns, but it's a lint, not a guarantee.

## The user's machine
- **Installs:** an engine or SDK can be large (Unity with platform modules is 10+ GB; Unreal 50-100+ GB;
  Android SDK/NDK; Xcode). Ask first, prefer user-level installs, and write what you installed in
  `DEVLOG.md`.
- **Global changes:** don't change PATH, the registry, global git config, drivers or system settings without
  asking.
- **Input automation takes over the mouse and keyboard.** Check idle time (`um win drive --proc X idle`), ask
  before long runs, and prefer in-game input injection, which touches nothing outside the game.
- **Processes:** kill by exact PID. `pkill -f <pattern>` from an agent shell can match and kill the agent's own
  shell. Don't leave editors, dev servers, headless engines or recorders running. Editors also hold project
  locks: Unity refuses a batch run while the editor has the project open.
- **Network:** bind dev servers, agent bridges and debug ports to `127.0.0.1`. `vite --host` and similar flags
  expose the game to the LAN.
- **Downloads:** engines, plugins and asset packs come only from official sites, the official GitHub repo's
  releases, or the engine's asset store. A "free plugin" from a random link can be malware.

## Accounts, stores and publishing
- **The human handles accounts:** creating them, logging in (`butler login` opens a browser; steamcmd asks for
  Steam Guard), signing agreements, paying fees and filling in tax forms. You never handle their passwords or
  2FA codes.
- **Before any upload or post**, show exactly what goes where and get an explicit yes for that action. That
  covers `butler push`, `steamcmd +run_app_build`, Play Console, App Store Connect, web portals, social posts
  and PRs.
- Pushing to a channel players see (an itch.io channel, Steam's default branch) *is* publishing. Use
  private channels and beta branches for test builds.

## Players: online features, data and safety
- **Server authority:** never trust the client with positions, damage, currency or scores. Validate and
  rate-limit everything; check leaderboard scores server-side (replays or plausibility bounds).
- **Data:** collect nothing by default. Analytics and crash reporting are opt-in and covered by a privacy
  policy (stores require one when you collect data, plus mobile privacy labels or data-safety forms).
  Games aimed at children fall under COPPA, GDPR-K and stricter store rules (Google Play's Families policy):
  avoid collecting their data at all.
- **Chat and user-generated content** need moderation, reporting and blocking. Otherwise leave free text
  out.
- **Photosensitivity:** no full-screen flashes faster than 3 per second (WCAG 2.3.1), plus settings to
  reduce flashes and screen shake.
- **Monetization:** no dark patterns. Paid random loot boxes are restricted in some places (Belgium treats
  them as gambling). Since June 2026, PEGI rates newly submitted games with paid random items at 16 by
  default. Disclose in-app purchases.
- **Saves:** version the format, migrate old saves, write atomically, keep the previous save as a backup, and
  never delete player data on update.

## When to stop and ask
- The idea copies another game's protected expression (names, characters, art, music, levels), or uses
  ripped or leaked material.
- A step needs the user's accounts, money, or legal acceptance (fees, agreements, signing keys).
- A step installs something large or changes the system.
- A step would delete or overwrite work that isn't committed or backed up.
- Anything public: uploads, store pages, posts, PRs.
- The game would collect personal data, involve real money, or target children.
