# Stores and platforms: the details

Checked in October 2026 against the stores' own documentation. Fees, sizes, review times and policies
change, so re-check the linked docs before a release. Account creation, logins, agreements, fees and tax
forms are always done by the user.

## itch.io
- **Uploads with butler** (itch.io's command-line uploader):
  ```bash
  butler login                                                     # the user does this once (it opens a browser)
  butler push build/windows <user>/<game>:windows --userversion 1.2.0
  butler push build/web <user>/<game>:html5 --userversion 1.2.0
  butler status <user>/<game>                                      # channels, latest and pending builds
  ```
  Channel names containing `windows`/`win`, `linux`, `mac`/`osx` or `android` are tagged with that platform
  automatically. butler only uploads what changed, so patches are small.
- **HTML5:** upload a zip with `index.html` (keep it at the root) and tick "This file will be played in the
  browser". Set the embed size, the fullscreen button and mobile friendliness. *SharedArrayBuffer support*
  (Embed options → Frame options) adds the COOP/COEP headers that threaded Emscripten and Godot builds need.
  It's experimental and doesn't work in Safari.
- **Generative AI disclosure** (since November 2024): a field on the project's edit page. "Yes" adds "AI
  Generated" tags per area (graphics, sound, text and dialogue, code). It's mandatory for asset pages, and
  the quality guidelines expect every game using generative AI to be tagged.
- Pricing: free, paid, or pay-what-you-want. Jam entries are submitted from the jam's page.
- Docs: https://itch.io/docs/butler/

## Steam
- **Steam Direct:** $100 per app, recouped once the app reaches $1,000 adjusted gross revenue. There's a
  waiting period after paying before release is possible (Valve's pages state 21-30 days).
- **Builds:** define the app and depot build scripts (`app_build_<appid>.vdf`, depot VDFs; ContentBuilder in
  the Steamworks SDK's `tools/` folder), then:
  ```bash
  steamcmd +login <account> +run_app_build <path>/app_build_<appid>.vdf +quit    # the user logs in (Steam Guard)
  ```
  Upload to a beta branch, test it, then set the build live from the partner site.
- **Review and timing:**
  - a Coming Soon page must be live at least 2 weeks before release;
  - the store page and the build are each reviewed, typically in 3-5 business days, so plan for 7;
  - wishlists drive launch visibility (a Steam Next Fest demo helps).
- **Store graphics** (https://partner.steamgames.com/doc/store/assets/standard):

| Asset | Size |
|---|---|
| Header capsule | 920×430 |
| Small capsule | 462×174 |
| Main capsule | 1232×706 |
| Vertical capsule | 748×896 |
| Library capsule | 600×900 |
| Library header | 920×430 |
| Library hero | 3840×1240 |
| Library logo | up to 1280×720, transparent PNG |
| Page background (optional) | 1438×810 |
| Screenshots | at least 5, at least 1920×1080, 16:9 |

  Capsules may show only artwork, the game's name and an official subtitle.
- **Trailers:** up to 1920×1080 (16:9 preferred), H.264 + AAC in `.mp4`, 5,000+ kbps, 30 or 60 fps.
- **Content Survey:**
  - It covers mature content and AI disclosure. Since January 2026, disclosure covers AI-generated content
    that ships with the game or that players see, including store-page and marketing assets.
    Live-generated content needs a guardrails description. Code assistants and other development-efficiency
    tools are out of scope.
  - The survey also generates Valve's ratings for regional boards. Germany has required a rating since
    November 2024, and the survey's rating covers it.
- **Steamworks features:**
  - achievements and stats need the Steamworks API: GodotSteam, Steamworks.NET or Facepunch.Steamworks
    (Unity/C#), the Steam Online Subsystem (Unreal), steamworks-rs (Rust);
  - **cloud saves need no code** with Steam Auto-Cloud (configure the save paths in Steamworks);
  - for local testing, put `steam_appid.txt` (containing the app id) next to the executable, and never ship
    it in the depot.

## Epic Games Store
Self-publishing has been open to all developers since March 2023: $100 per title and an 88/12 revenue split.
Since June 2025, developers keep 100% of the first $1M net revenue per product per year.

## Web portals and your own site
- **CrazyGames:** an open developer portal. Its SDK is optional for a Basic Launch and required for a Full
  Launch.
- **Newgrounds:** any account can upload an HTML5 zip, which then goes through Judgment.
- **Game Jolt:** HTML builds as a zip with `index.html` at the root.
- **Poki:** not self-serve. You apply, and games are hand-picked. Its SDK is required, and Poki asks for web
  exclusivity.
- **Your own site:** GitHub Pages can't set custom headers, so threaded builds need a service-worker
  workaround there. Cloudflare Pages and Netlify set COOP/COEP through a `_headers` file.

## Google Play
- Upload **Android App Bundles (AAB)**, which require **Play App Signing**: Google holds the app signing
  key, and the user signs uploads with an *upload key*. The keystore and its passwords never go in the repo.
- **Target API level:** new apps and updates must target API 36 (Android 16) from 31 August 2026 (an
  extension can be requested to 1 November 2026). Existing apps need API 35 or higher to stay
  discoverable.
- **New personal developer accounts** (created after 13 November 2023) must run a closed test with at least
  12 opted-in testers for 14 consecutive days before applying for production.
- Every app needs an **IARC content rating** and a **data safety form**.

## Apple App Store
- Apple Developer Program: 99 USD per year (fee waivers exist for nonprofits, education and government).
- Since 28 April 2026, uploads must be built with Xcode 26 or later and the iOS 26 SDK.
- TestFlight for betas (included), then App Store review and privacy "nutrition labels".
- Notarization for macOS apps distributed outside the Mac App Store also uses this account.

## Microsoft Store (PC)
Partner Center registration has been free for individual developers since September 2025. Many engines can
produce MSIX packages, or you can submit a regular installer.

## Consoles
Nintendo, PlayStation and Xbox require approved developer accounts, plus SDKs and dev kits under NDA. Unity and
Unreal have console platform support once approved. Godot reaches consoles through porting partners (W4
Games, Lone Wolf Technology, Pineapple Works, RAWRLAB and others; see https://godotengine.org/consoles/).
The user applies; an agent can prepare the pitch and the build plan, not the access.
