# Amazon GameLift Streams — Capabilities Reference

For CLI commands, see [gamelift-streams-cli.md](gamelift-streams-cli.md).

---

## Amazon GameLift Streams

**Purpose**: A cloud game streaming service that streams an interactive game application running in AWS datacenters directly to players' devices via WebRTC. Distinct from GameLift Servers — streams the entire game client rendered in cloud rather than hosting dedicated game server logic.

### Core Concepts

| Concept | Description |
|---|---|
| **Application** | The game or interactive application package uploaded to GameLift Streams (Windows executable + assets). |
| **Stream Group** | A pool of streaming instances (with a defined instance type and capacity) that host and stream application sessions. |
| **Stream Session** | A single active streaming session between a player's device and a GameLift Streams instance. |
| **WebRTC delivery** | Low-latency audio/video stream delivered to the player's browser or native client; inputs sent back over the same connection. |

### Key Characteristics

- **Player input**: Keyboard, mouse, gamepad inputs sent back to the cloud instance in real time
- **Instance types**: GPU-backed instances for graphics-intensive games (e.g., `g4dn`, `g5`)
- **Scaling**: Stream groups define minimum and maximum standby instance counts; autoscaling maintains pool based on demand
- **Locations**: Stream groups can be deployed across multiple AWS Regions to minimize player latency
- **Access**: Integrate via the GameLift Streams SDK or API; generate stream session URLs for players

### Capacity Management

Stream groups manage capacity through desired session counts:

- **MinimumDesiredSessions**: Warm standby instances kept ready to accept new stream sessions immediately
- **MaximumDesiredSessions**: Upper bound on concurrent active streaming sessions
- Per-location capacity overrides allow fine-grained regional control

### Multi-Location Support

Stream groups can span multiple AWS Regions:

- Configure per-location desired capacity when creating or updating a stream group
- Add locations post-creation with `add-stream-group-locations`
- Remove locations with `remove-stream-group-locations`
- Players are routed to the nearest available stream group location

### Important Distinctions from GameLift Servers

| GameLift Servers | GameLift Streams |
|---|---|
| Hosts dedicated game **server logic** | Streams the entire **game client** rendered in cloud |
| Players connect their game client to the server | Players receive an AV stream; no local game client needed |
| Matchmaking, sessions, player slots | Stream groups, stream sessions |
| `aws gamelift` CLI | `aws gameliftstreams` CLI |

### Integration Pattern

- **GameLift Streams + CloudFront**: Distribute stream session creation endpoints globally via CloudFront for low-latency session startup
