# Azure Gaming Architecture — Capabilities Reference
For CLI commands, see [gaming-architecture-cli.md](gaming-architecture-cli.md).

## AKS for Game Servers (Agones)

**Purpose**: Run dedicated game servers on Kubernetes using Agones for lifecycle management. Provides autoscaling, allocation, and health checking for multiplayer game server fleets.

### Why Agones on AKS

- **Game server lifecycle**: Agones adds game server awareness to Kubernetes (Ready, Allocated, Shutdown states)
- **Player-aware scaling**: Scale based on active game sessions, not just CPU/memory
- **Server allocation**: Request and allocate game servers for new match sessions
- **Health checking**: Agones monitors game server health; replaces unhealthy servers automatically
- **Fleet autoscaling**: Custom Fleet Autoscaler (buffer-based or webhook-based policies)
- **No vendor lock-in**: Open-source (CNCF project); runs on any Kubernetes cluster

### Agones Key Resources

| Resource | Description |
|---|---|
| **GameServer** | Single game server instance; wraps a Kubernetes Pod |
| **Fleet** | Collection of identically configured GameServers (like a ReplicaSet) |
| **FleetAutoscaler** | Scales Fleet up/down based on buffer size or custom webhook policy |
| **GameServerAllocation** | Request to allocate an available game server for a new match |
| **GameServerSet** | Lower-level controller for Fleet; rarely configured directly |

### Game Server Lifecycle

```
Fleet creates GameServers in Starting state
  → game server process initializes
  → calls Agones SDK: Ready()
  ← Agones marks GameServer as Ready
  ← Match orchestrator calls GameServerAllocation
  → Agones marks server as Allocated
  → Players connect directly to GameServer pod IP:port
  ← Game session ends; server calls SDK: Shutdown()
  → Agones terminates pod; Fleet creates replacement in Starting state
```

### Fleet Configuration

```yaml
apiVersion: agones.dev/v1
kind: Fleet
metadata:
  name: dedicated-game-server
spec:
  replicas: 5                           # Minimum ready servers
  template:
    spec:
      ports:
      - name: game
        containerPort: 7777
        protocol: UDP
      template:
        spec:
          containers:
          - name: game-server
            image: myacr.azurecr.io/game-server:v1.2.0
            resources:
              requests:
                cpu: "1"
                memory: "512Mi"
              limits:
                cpu: "2"
                memory: "1Gi"
```

### FleetAutoscaler (Buffer Policy)

```yaml
apiVersion: autoscaling.agones.dev/v1
kind: FleetAutoscaler
metadata:
  name: game-server-autoscaler
spec:
  fleetName: dedicated-game-server
  policy:
    type: Buffer
    buffer:
      bufferSize: 3                     # Maintain 3 ready (unallocated) servers
      minReplicas: 3                    # Never go below 3 total
      maxReplicas: 50                   # Never exceed 50 total
```

### Node Pool Sizing for Games

| Game Type | Recommended VM | Notes |
|---|---|---|
| Battle royale (large maps) | D8s_v5 / D16s_v5 | High CPU/memory per server |
| FPS (small lobbies, 16-32 players) | D4s_v5 | Multiple servers per node |
| Strategy/MOBA | D4s_v5 | Moderate resources; many simultaneous matches |
| GPU rendering/VR | NV6ads_A10_v5 | GPU for server-side rendering |

---

## Azure Cosmos DB for Games

**Purpose**: Global, low-latency NoSQL database for game state, player profiles, leaderboards, and matchmaking data requiring millisecond reads/writes at planetary scale.

### Game Use Cases

| Use Case | Cosmos DB Design |
|---|---|
| **Leaderboards** | Container: `/gameId`; item per player; sorted queries by score |
| **Player profile** | Container: `/playerId`; single item per player with full profile |
| **Session data** | Container: `/sessionId` or `/gameId`; TTL for auto-expiry |
| **Match history** | Container: `/playerId` (partition by querying player) |
| **Game world state** | Container: `/regionId` or `/chunkId` for spatial partitioning |
| **Real-time inventory** | Container: `/playerId`; optimistic concurrency with ETags |

### Global Leaderboards

```python
from azure.cosmos import CosmosClient

client = CosmosClient(COSMOS_URL, credential)
container = client.get_database_client("game-db").get_container_client("leaderboard")

# Update player score (upsert for idempotency)
player_score = {
    "id": f"score-{player_id}",
    "playerId": player_id,
    "playerName": display_name,
    "score": new_score,
    "gameMode": "ranked",
    "updatedAt": datetime.utcnow().isoformat()
}
container.upsert_item(player_score, populate_query_metrics=False)

# Top 100 leaderboard query
top_players = container.query_items(
    query="SELECT TOP 100 * FROM c WHERE c.gameMode = 'ranked' ORDER BY c.score DESC",
    enable_cross_partition_query=True
)

# Player's rank (count players with higher score)
rank_result = container.query_items(
    query=f"SELECT VALUE COUNT(1) FROM c WHERE c.gameMode = 'ranked' AND c.score > {player_score}",
    enable_cross_partition_query=True
)
```

### Cosmos DB Change Feed for Real-time Events

- Triggered whenever an item is created or updated in a container
- Power: real-time score update notifications, leaderboard cache invalidation, player activity tracking
- Consumed by: Azure Functions (built-in trigger), custom processors

```csharp
// Azure Functions Cosmos DB trigger for real-time score updates
[FunctionName("ScoreUpdated")]
public static async Task Run(
    [CosmosDBTrigger(
        databaseName: "game-db",
        containerName: "leaderboard",
        Connection = "CosmosDBConnection",
        LeaseContainerName = "leases")] IReadOnlyList<ScoreDocument> changes,
    [SignalR(HubName = "leaderboard")] IAsyncCollector<SignalRMessage> signalRMessages,
    ILogger log)
{
    foreach (var change in changes)
    {
        // Broadcast leaderboard update to connected clients
        await signalRMessages.AddAsync(new SignalRMessage
        {
            Target = "leaderboardUpdate",
            Arguments = new[] { change }
        });
    }
}
```

### Session Data with TTL

```python
# Game session with automatic TTL cleanup
session = {
    "id": session_id,
    "gameMode": "battle-royale",
    "players": [player1_id, player2_id],
    "serverIp": "1.2.3.4",
    "serverPort": 7777,
    "startedAt": datetime.utcnow().isoformat(),
    "ttl": 3600  # Auto-delete after 1 hour (Cosmos DB TTL)
}
container.create_item(session)
```

---

## Azure CDN for Game Asset Delivery

**Purpose**: Deliver game patches, DLC downloads, game launcher updates, static assets, and streaming video at global scale with low latency.

### CDN Tiers for Games

| Tier | Use Case | Notes |
|---|---|---|
| **Azure CDN Standard from Microsoft** | Moderate traffic; standard game patches | 40+ PoP locations |
| **Azure CDN Standard from Verizon** | High-scale game downloads | 150+ PoP; Verizon network |
| **Azure CDN Premium from Verizon** | Enterprise rules engine; custom caching | Full rule engine; advanced analytics |
| **Azure CDN from Akamai** (deprecated) | Migrating to Microsoft CDN | Use Microsoft CDN for new deployments |
| **Azure Front Door** | Global load balancing + CDN + WAF | Dynamic content acceleration; game APIs |

### Game Content Delivery Patterns

| Content Type | CDN Strategy |
|---|---|
| **Game patches** | Large blob files; cache indefinitely; URL versioning (`/v1.5.2/patch.zip`) |
| **DLC packages** | Conditional access via Azure CDN token authentication |
| **Texture assets** | Aggressive caching (immutable with versioned URLs) |
| **Game launcher** | Short-lived cache; version check API + CDN for installer |
| **Trailer videos** | Azure Media Services + CDN |

### CDN Token Authentication (Paid DLC Protection)

```bash
# Verizon Premium CDN token auth
az cdn endpoint create \
  --resource-group myRG \
  --profile-name myGameCDN \
  --name myDLCEndpoint \
  --origin "mystorageacct.blob.core.windows.net" \
  --query-string-caching-behavior UseQueryString  # Vary cache by query string (for token)
```

---

## Azure Communication Services for In-game

**Purpose**: Embed voice chat, text chat, and direct messaging into games using cloud APIs — without building communication infrastructure.

### In-game Communications Patterns

| Feature | ACS Service | SDK |
|---|---|---|
| **Team voice chat** | Calling SDK (VoIP) | Unity, Unreal, iOS, Android, Browser |
| **In-game text chat** | Chat service | Any SDK |
| **Player-to-player messaging** | Chat threads | Any SDK |
| **Group voice (party)** | Calling SDK (group call) | Unity, Unreal |
| **Moderator alerts** | SMS / Email | REST API |

> For in-game voice at massive scale, consider PlayFab Parties (purpose-built for games) over ACS.

---

## Azure Spatial Anchors for AR Games

**Purpose**: Create augmented reality games with physical world anchors that persist across sessions and are shared between players.

### AR Game Architecture

```
Player A: scans environment → creates anchor at treasure location
             → uploads anchor to Azure Spatial Anchors cloud
             → shares anchor ID with other players

Player B/C: downloads anchor ID → scans environment
             → Azure localizes anchor against visual data
             → sees virtual treasure at exact same physical location
```

### Use Cases

- Location-based AR games (anchored POIs at physical locations)
- Collaborative AR puzzles (multiple players interact with shared virtual objects)
- Indoor AR experiences (museum, retail, escape room)
- Mixed reality multiplayer (HoloLens-based training with shared virtual objects)

---

## Game Build and Rendering

### Batch + Spot VMs for CI/CD and Rendering

- **Game build servers**: Azure Batch with Spot VMs for parallel shader compilation, asset processing
- **Rendering farms**: Batch with GPU VMs for pre-rendered cinematics, baked lighting
- **Spot VM savings**: 60-90% cost reduction vs on-demand; acceptable for interruptible build/render jobs
- **Auto-retry**: Batch automatically retries tasks on node pre-emption

### Azure Monitor for Game Telemetry

```csharp
// Application Insights custom metrics from game server
var telemetryClient = new TelemetryClient();

// Track active players
telemetryClient.TrackMetric("ActivePlayers", activePlayerCount);
telemetryClient.TrackMetric("MatchesRunning", runningMatchCount);

// Track game events
telemetryClient.TrackEvent("PlayerKilled", new Dictionary<string, string> {
    {"WeaponType", "rifle"},
    {"GameMode", "battle-royale"},
    {"Region", "eastus"}
});

// Track performance
telemetryClient.TrackMetric("ServerTickRate", currentTickRate);
telemetryClient.TrackMetric("NetworkLatencyMs", avgPlayerLatency);
```
