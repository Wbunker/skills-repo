# Amazon GameLift Servers — Capabilities Reference

For CLI commands, see [gamelift-servers-cli.md](gamelift-servers-cli.md).

---

## Amazon GameLift Servers

**Purpose**: Managed service for deploying, operating, and scaling dedicated game servers for session-based multiplayer games. Eliminates the need to manage underlying infrastructure.

### Core Concepts

| Concept | Description |
|---|---|
| **Build** | Your compiled game server binary and dependencies, uploaded to GameLift. Supports Windows and Linux executables. |
| **Script** | Realtime Servers script (Node.js); used instead of a build when you want GameLift to manage a lightweight JS-based game server. |
| **Fleet** | A group of Amazon EC2 instances (or Anywhere compute) running your build or script. The fleet is the unit of scaling and capacity. |
| **Instance** | A single EC2 (or Anywhere) host within a fleet. Each instance runs multiple concurrent game server processes. |
| **Game Session** | A single instance of your game running on a fleet instance. Has a capacity for a fixed number of player slots. |
| **Player Session** | A reservation slot within a game session for a specific player. A player must claim a session slot before connecting to the server. |
| **Alias** | A named pointer to a fleet. Used in matchmaking and game session placement to decouple clients from specific fleet IDs. Supports routing strategies (simple, terminal). |
| **Queue** | A game session queue spans multiple fleets (across regions) and prioritizes placement using latency, cost, and capacity rules. |
| **FlexMatch** | GameLift's matchmaking service. Evaluates match rule sets to group players into balanced matches, then triggers game session creation. |

---

## Fleet Types

| Fleet Type | Description |
|---|---|
| **EC2 On-Demand** | Standard reserved compute; predictable availability and pricing. |
| **EC2 Spot** | Uses EC2 Spot Instances for up to 90% cost savings; subject to interruption. Suitable for latency-tolerant, interruptible workloads. |
| **Anywhere Fleet** | Register and manage game servers running on your own hardware, on-premises, or in other cloud environments. GameLift orchestrates placement and matchmaking against Anywhere fleets just like EC2 fleets. |
| **Container Fleet** | Package your game server in a container image (Amazon ECR); GameLift manages container deployment on EC2. |

### Fleet Configuration

- **Instance type**: Selects the EC2 instance family and size (e.g., `c5.large`, `c6g.xlarge`).
- **Runtime configuration**: Defines which server processes to launch per instance, with launch path, parameters, and concurrent process count.
- **Port settings (inbound permissions)**: IP protocol, port ranges, and CIDR ranges that players are allowed to connect to.
- **Game session protection**: Optional; prevents interruption of active game sessions during scale-in or Spot interruptions.
- **Resource creation limit**: Maximum number of game sessions a single player can create within a time window.
- **Multi-location**: A fleet can span multiple AWS Regions (multi-location fleet); GameLift manages instance pools per location.

---

## Realtime Servers

A lightweight, fully managed, multiplayer game server framework built on Node.js. You provide a script (not a compiled binary). GameLift manages the infrastructure.

- Low-latency UDP messaging via WebRTC data channels
- Server-side game logic in JavaScript
- Suitable for turn-based, casual, and prototyping use cases
- Scripts uploaded similarly to builds; referenced when creating a fleet

---

## Game Session Queues

Queues enable **multi-region, multi-fleet placement** for game sessions.

| Feature | Description |
|---|---|
| **Fleet destinations** | List of fleets (by fleet ID or alias ARN) in priority order. Can span multiple Regions. |
| **Latency policies** | Enforce a maximum acceptable latency per player for a placement attempt. Rules expire progressively to widen the search. |
| **Player latency** | Reported by the client via `StartGameSessionPlacement`; GameLift uses this to select the lowest-latency destination. |
| **Priority** | Configure priority order: latency, cost, destination, or location. |
| **Timeout** | Maximum time (seconds) GameLift searches before the placement request fails. |
| **Notifications** | Queue publishes placement events to an SNS topic. |
| **FilterConfiguration** | Restrict eligible destinations by allowed locations. |

---

## Auto Scaling

| Method | Description |
|---|---|
| **Target tracking** | Maintain a target ratio of available game session slots (e.g., keep 20% idle capacity). Automatically adds/removes instances. |
| **Rule-based** | Custom scaling rules based on CloudWatch metrics (e.g., `ActiveGameSessions`, `AvailableGameSessions`, `IdleInstances`). |
| **Scheduled** | Scale fleet capacity on a time-based schedule for predictable traffic patterns. |
| **Spot + On-Demand balance** | Use Spot fleets with On-Demand fallback in queues to achieve cost savings without availability risk. |

---

## FlexMatch Matchmaking

FlexMatch is a fully managed matchmaking service that groups players based on configurable rule sets.

### Matchmaking Configuration

- References a **queue** for game session placement once a match is found
- Configures **acceptance requirement** (players must accept before a session is created)
- Sets **request timeout** (how long to search before failing)
- Defines **backfill mode** (automatic or manual)

### Match Rule Sets

A JSON document defining:

| Component | Description |
|---|---|
| **Teams** | Define team count, min/max player count per team |
| **Rules** | Conditions players must satisfy (latency, skill level, attributes); supports distance, comparison, collection, absoluteSort, latency, and batchDistance rule types |
| **Expansions** | Relax rules over time to improve match fill rate |
| **Algorithm** | `exhaustiveSearch` (exact) or `biased random sorting` strategies |

### Matchmaking Tickets

- `StartMatchmaking` creates a ticket; clients poll `DescribeMatchmaking` or subscribe to SNS/EventBridge events
- Ticket states: `QUEUED` → `SEARCHING` → `REQUIRES_ACCEPTANCE` → `PLACING` → `COMPLETED` / `FAILED` / `CANCELLED` / `TIMED_OUT`
- Backfill tickets (`StartMatchBackfill`) fill open slots in an active game session

---

## VPC Peering

Connect a GameLift fleet's VPC to your own VPC to allow game servers to access backend services (databases, auth services) over private networking.

- Authorize a VPC peering connection from the GameLift account to your VPC
- Requires non-overlapping CIDR blocks
- `CreateVpcPeeringConnection` and `CreateVpcPeeringAuthorization` manage the connection lifecycle

---

## GameLift Local

A standalone tool that mimics the GameLift service API on a local developer machine. Allows testing game server integration without deploying to AWS.

- Runs locally; game server calls `GameLift Local SDK` endpoints on `localhost:8080`
- Supports game session creation, player session creation, server process health checks
- Does not support FlexMatch, queues, or multi-region scenarios

---

## Important Limits & Quotas

| Resource | Default Limit |
|---|---|
| Fleets per Region | 20 (adjustable) |
| Instances per fleet (EC2) | 1 (adjustable up to thousands) |
| Game sessions per instance | Depends on runtime config (process count) |
| Player sessions per game session | Defined by game session `maximumPlayerSessionCount` |
| FlexMatch rule sets per Region | 10 (adjustable) |
| Matchmaking configurations per Region | 10 (adjustable) |
| Queues per Region | 20 (adjustable) |
| Max match rule set size | 65,535 bytes |
| Game session placement queue timeout | Up to 600 seconds |

---

## Integration Patterns

| Pattern | Description |
|---|---|
| **GameLift + API Gateway + Lambda** | Clients call a Lambda-backed API to request matchmaking tickets; Lambda calls `StartMatchmaking`; EventBridge/SNS delivers placement results |
| **GameLift + Cognito** | Authenticate players with Cognito; pass player attributes (skill, region) into FlexMatch tickets |
| **GameLift Anywhere + hybrid** | Run part of your fleet on premises (Anywhere) for latency-sensitive regions; combine with EC2 fleets in queues |
