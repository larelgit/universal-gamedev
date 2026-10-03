# Multiplayer and netcode

Decide early. Retrofitting online multiplayer into a single-player architecture is one of the most expensive
changes in game development, because the authority model shapes all gameplay code.

## First: how much networking does the idea need?
Take the cheapest rung that delivers the idea:
1. **Local multiplayer** (couch, shared screen): no netcode at all.
2. **Steam Remote Play Together:** local co-op played over the internet, with no netcode (Steam only).
3. **Asynchronous:** leaderboards, ghosts and replays, daily seeds, shared levels. That needs a backend, but
   no real-time sync.
4. **Turn-based online:** request/response through a server, or a lobby plus relay.
5. **Real-time co-op:** players are on the same side, so host authority and some trust are acceptable.
6. **Real-time competitive:** server authority, validation, matchmaking, usually dedicated servers. The
   most expensive rung, and an ongoing cost.

## Topologies
- **Listen server (host):** one player's game is the server. Cheap, but the host has an advantage and needs
  NAT traversal or a relay.
- **Dedicated authoritative server:** fair and controllable, but it costs money per player-hour and needs
  operations work.
- **Peer-to-peer:** every peer simulates (lockstep or rollback). Needs NAT punch-through or a relay.
- **Relays** solve NAT for listen servers and P2P: Steam Datagram Relay (SteamNetworkingSockets), Epic
  Online Services P2P, Unity Relay, or WebRTC with TURN.

## Sync models

| Model | How it works | Fits | Requires |
|---|---|---|---|
| Deterministic lockstep | everyone sends inputs/commands; each machine simulates the same ticks | RTS, turn-based, thousands of units | a deterministic simulation, input delay, desync detection (state checksums) |
| Rollback (GGPO-style) | predict remote inputs and run ahead; when a late input arrives, restore and re-simulate | fighting games, small-state action | determinism plus fast save/restore of the whole state; 2-8 frames of rollback |
| Snapshot interpolation | the server sends world snapshots; clients render ~100 ms in the past, interpolating | shooters, action with many entities | bandwidth work (deltas, quantization) |
| Client prediction + reconciliation | the client moves its own player at once; the server is authoritative; on correction the client replays its unacknowledged inputs | any responsive authoritative game | input sequence numbers; movement code shared by client and server |
| Lag compensation | the server rewinds hitboxes to what the shooter saw | hitscan shooters | a short history of positions per entity |

Most real-time games combine the last three: snapshot interpolation for other entities, prediction for your
own character, lag compensation for hits.

## Engine options (versions move: check the current release and docs)
- **Godot:**
  - the high-level multiplayer API (`MultiplayerAPI`, `@rpc`, `MultiplayerSpawner`,
    `MultiplayerSynchronizer`) over `ENetMultiplayerPeer`, `WebSocketMultiplayerPeer` (web) or
    `WebRTCMultiplayerPeer`;
  - GodotSteam for Steam networking;
  - netfox (prediction, rollback, lag compensation addon);
  - the Nakama client.
- **Unity:**
  - Netcode for GameObjects, or Netcode for Entities (prediction built in);
  - Mirror and FishNet (open source);
  - Photon Fusion; Photon Quantum (deterministic, commercial);
  - Unity's Relay, Lobby and Matchmaker services.
- **Unreal:**
  - built-in replication (replicated properties; Server, Client and NetMulticast RPCs);
  - the Character Movement Component (predicted movement);
  - the Iris replication system;
  - the Gameplay Ability System for predicted abilities;
  - Online Subsystems (Steam, EOS).
- **Web:**
  - WebSocket servers (Node `ws`, uWebSockets.js, Colyseus, Socket.IO);
  - WebRTC data channels for unreliable, unordered real-time traffic (e.g. geckos.io);
  - WebTransport where browsers support it.
- **Rust / Bevy:**
  - Lightyear (prediction, interpolation, rollback), bevy_replicon, renet;
  - GGRS rollback with bevy_ggrs;
  - matchbox for WebRTC P2P in WASM.
- **Backends:**
  - Nakama (open source: matchmaking, realtime, leaderboards);
  - Epic Online Services (lobbies, P2P, voice);
  - Steamworks (lobbies, matchmaking, SteamNetworkingSockets);
  - PlayFab, Photon, Colyseus Cloud;
  - Supabase or Firebase for asynchronous features.

## Rules that save the project
- **Choose the authority model before gameplay code,** and write gameplay as simulation code that runs the
  same on server and client.
- **Ticks and inputs:** a 20-60 Hz server tick. Clients send inputs with sequence numbers, and the
  interpolation buffer holds 2-3 snapshots (~100 ms).
- **Bandwidth:** quantize (positions to centimetres, angles to 16 bits), delta-compress against
  acknowledged snapshots, and only send what each client needs (interest management).
- **Never trust the client:**
  - validate speeds, cooldowns, inventory and currency changes, and scores on the server;
  - validate hits server-side;
  - rate-limit every message type;
  - keep admin commands out of the client build.
- **Determinism, for lockstep and rollback:**
  - a fixed timestep and a shared seeded RNG;
  - no unordered iteration;
  - no engine physics (usually non-deterministic);
  - fixed-point maths if you need cross-platform guarantees.

  Checksum the state every tick, so desyncs are caught on the tick they happen.
- **Security:**
  - bind dev servers to `127.0.0.1` unless you're testing on a LAN;
  - `wss://` (TLS) for web;
  - authenticate players with platform tickets (Steam session tickets, EOS) before trusting an identity.

## Testing: oracles for netcode
- **Several instances on one machine:**
  - Godot: Debug → Customize Run Instances;
  - Unity: the Multiplayer Play Mode package;
  - Unreal: Play-In-Editor with several players and "Play As Client";
  - web: several browser contexts in Playwright.
- **Simulate bad networks from day one, not at the end** (100-200 ms latency, 1-5% loss):
  - Unreal: `Net PktLag=150` and `Net PktLoss=3` console commands, or Network Emulation in the editor
    preferences;
  - Unity: the Unity Transport / Multiplayer Tools network simulator;
  - anywhere: clumsy on Windows, `tc netem` on Linux, toxiproxy for TCP.
- **Headless bots:** N bot clients join a headless server and play scripted inputs. Assert that the server
  state stays consistent, that there are no desyncs (checksums), and that bandwidth per client stays under
  budget.
- **Soak test:** an hour of bots joining and leaving, watching memory and connection counts.

## Hosting
- **Headless server builds:** Godot's "Dedicated Server" export mode (strips visuals); Unity's Dedicated
  Server build target; Unreal server targets (these need an engine built from source).
- **Where:** a VPS, containers, or managed game-server hosting (AWS GameLift, Agones on Kubernetes,
  Edgegap and others). Servers cost money per concurrent player, which is the user's decision. Start
  co-op games on a listen server plus a relay.
