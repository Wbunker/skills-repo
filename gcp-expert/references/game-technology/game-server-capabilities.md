# Game Technology on GCP — Capabilities

## Agones

**Agones** is an open-source Kubernetes framework for hosting and scaling dedicated multiplayer game servers on GKE. It was created by Google and Epic Games and is now a CNCF-hosted project.

### Why Dedicated Game Servers?

Real-time multiplayer games (FPS, battle royale, racing, sports) require dedicated server processes per match:
- Each game session runs as a separate server process
- Players connect directly to a single authoritative server
- Server manages game state (physics, collision, scoring) — not clients
- Low latency (sub-50ms) is critical; servers should be near players geographically

Traditional Kubernetes is not designed for this use case (pods are not "allocatable game sessions"). Agones adds game-server-aware primitives to Kubernetes.

### Agones Architecture

**Custom Resource Definitions (CRDs):**

| CRD | Description |
|---|---|
| `GameServer` | A single dedicated game server instance; wraps a Kubernetes Pod |
| `Fleet` | A set of GameServer instances (like a Deployment); maintains desired count |
| `FleetAutoscaler` | Autoscales Fleet size based on buffer (keep N ready servers) |
| `GameServerAllocation` | Request an Available server from a Fleet and mark it Allocated |

**GameServer Lifecycle:**
```
PortAllocation → Scheduled → RequestReady → Ready → Allocated → Shutdown
```
- `Ready`: server is ready to accept players; available for allocation
- `Allocated`: server has been assigned a game session; players connect
- `Shutdown`: game session ended; pod is deleted

### Agones SDK

Game server process communicates with Agones via the **Agones SDK**:
- Available for: C++, C#/.NET, Go, Rust, Unreal Engine, Unity
- SDK runs as a sidecar container in the game server pod
- Key calls:
  - `sdk.Ready()`: tell Agones "I'm ready to accept players"
  - `sdk.Allocate()`: self-allocate (called by the game server itself)
  - `sdk.Shutdown()`: match ended; Agones will delete the pod
  - `sdk.Health()`: heartbeat; if missing for too long, Agones marks server Unhealthy
  - `sdk.SetLabel(key, value)`: set labels for filtering during allocation
  - `sdk.PlayerConnect(playerID)`: track connected players (for capacity-based allocation)

### Game Server Allocation

**GameServerAllocation** is how your matchmaker claims a `Ready` server:
- Send a `GameServerAllocation` request to the Kubernetes API (via your matchmaker service)
- Agones finds a matching `Ready` server (by label selectors, priority, fleet name)
- Server moves to `Allocated` state; allocation response includes the server's IP and port
- Matchmaker returns connection info to players

**Priority-based allocation**: prioritize servers with more players (pack servers to reduce idle count) or prefer lower-latency regions.

### FleetAutoscaler

Automatically adjusts fleet size to maintain a buffer of ready servers:

```yaml
# Buffer-based autoscaler: keep 10 Ready servers at all times
apiVersion: autoscaling.agones.dev/v1
kind: FleetAutoscaler
metadata:
  name: my-game-fleet-autoscaler
spec:
  fleetName: my-game-fleet
  policy:
    type: Buffer
    buffer:
      bufferSize: 10          # keep 10 Ready servers
      minReplicas: 10         # never scale below 10
      maxReplicas: 200        # never scale above 200
```

**Webhook autoscaler**: call a custom HTTP endpoint to determine scale; implement custom logic (time-based scaling, tournament schedule, etc.).

### GKE Configuration for Agones

**Dedicated node pools for game servers:**
- Isolate game server pods from system workloads
- Use node taints: `agones.dev/gameserver=true:NoExecute`
- Game server pods have matching tolerations
- High-performance networking: enable gVNIC (Google Virtual NIC) for lower latency
- Use `n2-highcpu-*` or `c2-*` for CPU-intensive game servers

**Spot VMs for cost reduction:**
- Configure a `spot` node pool + standard node pool
- Agones handles evictions: `Shutdown` is called, players disconnected gracefully
- Suitable for non-ranked/casual game modes; not for ranked competitive where mid-game eviction is unacceptable

**Multi-cluster / multi-region:**
- Deploy Agones-enabled GKE clusters in multiple regions
- Use Agones Multi-cluster Allocation to route allocation requests to the best cluster
- Deploy a global allocation service (e.g., using Cloud Run or GKE + Traffic Director)

---

## Open Match

**Open Match** is an open-source matchmaking framework for games. It handles the complex logic of matching players into game sessions based on skill, latency, preferences, and queue status. Also a CNCF sandbox project.

### Architecture

| Component | Description |
|---|---|
| **Director** | Your code that drives the matchmaking cycle; calls Open Match APIs |
| **Match Function (MMF)** | Your custom code that implements the matching logic; runs as a gRPC service |
| **Open Match Frontend** | API for players to join/leave matchmaking queues |
| **Open Match Backend** | API for the Director to fetch matches and assign game servers |
| **Tickets** | Player entries in the matchmaking queue; contain attributes (rating, latency, preferences) |
| **Profiles** | Criteria defining what a valid match looks like (skill range, region, team size) |
| **Matches** | Proposed groups of tickets that should play together |

### Matchmaking Flow

```
1. Players send Ticket to Open Match Frontend (via your game client backend)
2. Director fetches Tickets matching a Profile from Open Match Backend
3. Director calls Match Function (MMF) with candidate Tickets
4. MMF implements your matching algorithm; returns proposed Matches
5. Director assigns each Match to a game server (via Agones allocation)
6. Director notifies players of server connection info
7. Players connect to game server
```

### Match Function Examples

Common matching algorithms implemented in the MMF:
- **Skill-based**: group players within ±200 ELO rating
- **Low-latency**: prefer players with <50ms ping to the same region
- **Team-based**: 5v5; balance team average skill rating within 100 ELO
- **Lobby-based**: wait until 10 players are queued before creating a match
- **Backfill**: fill incomplete game sessions with queued players

---

## GKE for Game Servers

### Recommended GKE Configuration

```bash
# Create a game server cluster (control plane + dedicated game server node pool)
gcloud container clusters create game-servers-us-central1 \
  --region=us-central1 \
  --release-channel=stable \
  --num-nodes=3 \
  --machine-type=n2-standard-4 \
  --enable-autoscaling \
  --min-nodes=3 \
  --max-nodes=10 \
  --node-labels=app=game-server

# Add dedicated high-performance game server node pool
gcloud container node-pools create gameserver-pool \
  --cluster=game-servers-us-central1 \
  --region=us-central1 \
  --machine-type=c2-standard-8 \
  --num-nodes=0 \
  --enable-autoscaling \
  --min-nodes=0 \
  --max-nodes=100 \
  --node-taints=agones.dev/gameserver=true:NoExecute \
  --node-labels=agones.dev/gameserver=true \
  --enable-gvnic
```

---

## Cloud Spanner for Games

**Cloud Spanner** is the recommended relational database for globally distributed game backends where consistency, scale, and availability are critical.

### Common Game Use Cases

**Player State and Inventory:**
- Consistent transaction semantics for in-game item purchases
- No item duplication (ACID transactions prevent double-spend)
- Multi-region reads for global player base with low latency

**Leaderboards:**
- Global leaderboard updated in real time as players complete matches
- Read leaderboard from any region with consistent results
- Efficient top-N queries with Spanner's indexing

**Economy and Currency:**
- Virtual currency balance with atomic debit/credit
- Purchase history
- Currency exchange (trading system) requires serializable transactions

**Match History:**
- Store match results, statistics, and replay metadata
- Query historical performance for analytics
- Time-series queries for rank progression

### Spanner Schema Design for Games

```sql
-- Player table (globally distributed)
CREATE TABLE Players (
  player_id STRING(36) NOT NULL,
  username STRING(64) NOT NULL,
  email STRING(128),
  created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
  rating INT64 NOT NULL DEFAULT (1000),
  currency_coins INT64 NOT NULL DEFAULT (0),
  currency_gems INT64 NOT NULL DEFAULT (0),
) PRIMARY KEY (player_id);

-- Inventory table (interleaved with Players for co-location)
CREATE TABLE PlayerInventory (
  player_id STRING(36) NOT NULL,
  item_id STRING(64) NOT NULL,
  quantity INT64 NOT NULL DEFAULT (1),
  acquired_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
) PRIMARY KEY (player_id, item_id),
  INTERLEAVE IN PARENT Players ON DELETE CASCADE;

-- Leaderboard table (for efficient rank queries)
CREATE TABLE Leaderboard (
  player_id STRING(36) NOT NULL,
  season STRING(16) NOT NULL,
  score INT64 NOT NULL,
  updated_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
) PRIMARY KEY (season, score DESC, player_id);
-- DESC on score enables efficient top-N queries

-- Global secondary index on username
CREATE UNIQUE INDEX PlayersByUsername ON Players(username);
```

### Multi-Region Configuration

For a global game, use a **multi-region Spanner instance** for low-latency reads worldwide:
- `nam4`: North America multi-region (us-central1 + us-east4)
- `nam6`: North America 6-region
- `eur3`: Europe multi-region
- `nam-eur-asia1`: Global multi-region (most expensive; best global latency)

---

## Firebase for Game Backend

Firebase provides lightweight, real-time backend services ideal for many game use cases.

### Firebase Authentication for Games

- **Anonymous sign-in**: let players start playing immediately without registration; upgrade to full account later (link with Google, Apple, email)
- **Guest → account conversion**: persist progress when player creates an account; `linkWithCredential()` in SDK
- **Social sign-in**: Google Play Games, Apple Game Center, Facebook

### Firebase Realtime Database / Firestore for Game Data

| Use Case | Recommendation |
|---|---|
| Simple key-value game state (settings, profile) | Firestore |
| Small real-time game state (lobby, turn-based) | Realtime Database |
| Complex game data with queries | Firestore |
| Session-less, ultra-low-latency state | Realtime Database |
| Offline support | Both (Firestore has better offline) |

### Firebase Remote Config for Game Tuning

Live update game parameters without an app release:
- Adjust weapon damage values, economy drop rates, event parameters
- A/B test different configurations (Firebase A/B Testing)
- Gradually roll out changes to % of players
- Emergency "kill switch" to disable a broken feature

### Firebase Analytics for Player Behavior

- Automatic player event tracking (level start/complete, in-app purchase, session length)
- Custom events: `track("level_failed", {level: 12, cause: "time_expired"})`
- Funnel analysis: find where players drop out
- User segments: create cohorts of players by behavior for targeted offers
- Integration with Google Ads for re-engagement campaigns

---

## Vertex AI for Games

### Recommendations AI for Item Suggestions

- Recommend in-game items, characters, bundles to individual players
- Train on player purchase history and game behavior
- Available via `recommendationengine.googleapis.com` or Vertex AI Recommendations

### Game AI Opponents

- Train game AI using Vertex AI custom training (reinforcement learning, imitation learning)
- Serve AI models on Vertex AI Prediction endpoints for low-latency inference
- Pre-built frameworks: OpenSpiel for game AI research

### Fraud Detection for In-Game Economy

- Train fraud detection models on purchase patterns, account age, device fingerprints
- Detect virtual currency farming, account compromise, chargebacks
- Deploy as a real-time scoring function in Cloud Run (call at purchase time)
