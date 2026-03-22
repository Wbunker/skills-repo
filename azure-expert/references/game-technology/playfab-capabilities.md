# Azure PlayFab — Capabilities Reference
For CLI commands, see [playfab-cli.md](playfab-cli.md).

## Azure PlayFab Overview

**Purpose**: Fully managed LiveOps backend-as-a-service for games. Eliminates the need to build and operate game server infrastructure. PlayFab provides player management, economy, multiplayer, analytics, and engagement tools used by thousands of live games.

### Core Components

| Component | Description |
|---|---|
| **Game Manager** | Web portal for all configuration, analytics, and LiveOps management |
| **Title** | A single game (has its own TitleId, data, players) |
| **Entity framework** | Hierarchical object model: Namespace → Title → Master Player → Title Player → Character |
| **REST APIs** | JSON/REST APIs for all operations; SDKs wrap these |
| **CloudScript** | Server-side JavaScript (or Azure Functions) for authoritative game logic |

---

## Player Accounts and Authentication

### Authentication Methods

| Method | Platform | Notes |
|---|---|---|
| **Custom ID** | Any | Developer-controlled identifier; anonymous device ID |
| **Email + Password** | Any | Built-in account system with email verification |
| **Username + Password** | Any | Username-based accounts |
| **Steam** | PC | Steam authentication ticket |
| **Xbox Live** | Xbox, PC | Xbox User Token |
| **PlayStation Network** | PlayStation | PSN ticket |
| **Google** | Android | Google Play OAuth token |
| **Apple** | iOS | Sign in with Apple |
| **Facebook** | Any | Facebook access token |
| **Nintendo** | Switch | Nintendo Service Account |
| **Twitch** | Any | Twitch OAuth |

### Player Profile

- **Master Player Account**: Cross-title identity; holds linked accounts
- **Title Player Account**: Per-title player data; separate entity per game
- **Player Data (User Data)**: Key-value store on player entity (public or private to title)
- **Publisher Data**: Shared player data across all titles in a publisher account
- **Statistics**: Named numeric values per player (score, wins, level, XP)
- **Segments**: Dynamic player groupings based on statistics, login recency, device, etc.

---

## Economy v2

**Purpose**: Complete virtual economy system including currencies, catalog, player inventory, stores, and trading.

### Key Concepts

| Concept | Description |
|---|---|
| **Virtual currencies** | Custom currencies (Gold, Gems, Credits); define exchange rates, initial grant, max balance |
| **Catalog** | Item catalog defining all purchasable/earnable items with metadata |
| **Item types** | Currency, Durable (permanent), Consumable (limited uses), Bundle, Store |
| **Player Inventory** | Per-player item instances; stackable consumables; consumable charges |
| **Stores** | Curated subset of catalog with (optionally discounted) prices; A/B test different stores |
| **Bundles** | Group of items/currencies sold together |
| **Subscriptions** | Recurring item grants (monthly subscription, battle pass) |
| **Redemption codes** | Physical/promotional codes granting items or currencies |
| **Receipts** | IAP (In-App Purchase) validation for Apple App Store, Google Play, Steam |

### Economy API Examples

```javascript
// PlayFab JavaScript SDK
// Get player inventory
PlayFabClient.GetInventoryItems({
    Filter: "type eq 'currency'"
}, (result, error) => {
    if (result) {
        const currencies = result.data.Items;
        // currencies: [{Id, Amount, Type, DisplayName, ...}]
    }
});

// Add items to player (server SDK required for economy writes)
PlayFabServer.AddInventoryItems({
    PlayFabId: playerPlayFabId,
    Amount: 100,
    Item: { Id: "gold-currency-id" }
}, callback);

// Purchase an item from store
PlayFabClient.PurchaseItem({
    StoreId: "main-store",
    ItemId: "epic-sword-item-id",
    VirtualCurrency: "GD",
    Price: 250
}, callback);
```

---

## Multiplayer

### Matchmaking

- **Match queues**: Define rules for grouping players into matches
- **Match rules**: Skill-based (Elo, MMR), latency-based, team requirements, attribute matching
- **Tickets**: Players submit matchmaking tickets; PlayFab finds compatible tickets → creates match
- **Expansion**: Rules relax over time to ensure players find matches (configurable expansion intervals)
- **Result**: Match result contains server connection info and matched player roster

### Multiplayer Servers (Game Servers as a Service)

- Run containerized game server builds on Azure globally
- **Build**: Docker-compatible container image or zip of server executable
- **Regions**: Deploy to 30+ Azure regions; global load balancing to lowest-latency region
- **Autoscale**: Scale server instances based on player demand (standing-by/active)
- **Server lifecycle**: Idle → requested → active (game running) → terminated
- **Session**: A server session hosts one game; PlayFab manages allocation and monitoring
- **Support**: Windows and Linux; any game engine (Unreal, Unity, custom C++)

### Lobby

- **Pre-game rooms**: Players create/join lobbies before matchmaking or custom match
- **Host-based**: One player acts as lobby owner; configures game settings
- **Lobby data**: Shared key-value state visible to all lobby members (map, mode, etc.)
- **Member data**: Per-player state within lobby (ready status, class selection)
- **Search**: Find public lobbies by custom filters (region, game mode, language)
- **Connect to multiplayer server**: Lobby owner requests server; server connection info shared to all members

### Parties (Voice + Data Networking)

- **Party**: Cross-game voice chat and data networking group
- **Voice**: Cross-platform voice chat (works across Xbox, PlayStation, PC, Mobile simultaneously)
- **Data networking**: Low-latency peer-to-peer data channels within party (game state sync)
- **Chat permissions**: Configurable per-user voice/text chat permissions within party
- **No proprietary protocol**: Uses standard WebRTC-based networking
- **Xbox Party integration**: Satisfies Xbox Live party requirements for cross-play

---

## Leaderboards

- **Statistics**: Define named player stats (score, wins, kills); ranked per season or all-time
- **Leaderboard queries**: Top N players, players around a specific player rank (±5), specific players
- **Resets**: Configure stat reset schedule (daily, weekly, monthly, never)
- **Versioning**: Stats version incremented on reset; historical versions queryable
- **Entity leaderboards**: Rank any entity type (character, group, title) not just players

---

## CloudScript

**Purpose**: Server-authoritative JavaScript functions executing in PlayFab's managed environment. Prevents cheating by running game logic server-side.

```javascript
// CloudScript handler: award XP and level up
handlers.AwardXP = function(args, context) {
    var xpToAward = args.xp || 0;
    var playFabId = currentPlayerId;

    // Get current XP stat
    var statResult = server.GetPlayerStatistics({
        PlayFabId: playFabId,
        StatisticNames: ["XP", "Level"]
    });

    var currentXP = statResult.Statistics.find(s => s.StatisticName === "XP")?.Value || 0;
    var currentLevel = statResult.Statistics.find(s => s.StatisticName === "Level")?.Value || 1;
    var newXP = currentXP + xpToAward;

    // Level up logic
    var xpPerLevel = 1000;
    var newLevel = Math.floor(newXP / xpPerLevel) + 1;

    // Update stats
    server.UpdatePlayerStatistics({
        PlayFabId: playFabId,
        Statistics: [
            { StatisticName: "XP", Value: newXP },
            { StatisticName: "Level", Value: newLevel }
        ]
    });

    return { newXP: newXP, newLevel: newLevel, leveledUp: newLevel > currentLevel };
};
```

### Azure Functions Integration

- Execute Azure Functions as CloudScript (more powerful; full Node.js/Python/C# runtime)
- Longer execution time limits (vs vanilla CloudScript 10 second limit)
- Access to Azure services (Cosmos DB, Storage, Service Bus) from within game logic
- Deployed as standard Azure Functions with PlayFab trigger binding

---

## Experiments (A/B Testing)

- **Experiments**: Define treatment and control groups; vary content, pricing, difficulty
- **Player segments**: Assign players to experiment groups (50/50 split, percentage allocation)
- **Metrics**: Track KPIs (retention, IAP conversion, session length) across variants
- **Statistical significance**: PlayFab calculates confidence intervals; alerts when significance reached
- **Feature flags**: Enable/disable features per segment or experiment group

---

## Analytics and Insights

### Built-in Analytics

| Dashboard | Metrics |
|---|---|
| **Retention** | D1, D7, D14, D30 player retention cohorts |
| **Revenue** | Daily/monthly revenue, ARPU, ARPPU, conversion rate |
| **DAU/MAU** | Daily and monthly active users |
| **Session** | Average session length, sessions per user, session distribution |
| **Funnels** | Conversion between defined events (tutorial steps, store opens, purchases) |

### Raw Data Export

- Export all PlayStream events (every player action) to Azure Data Lake Storage Gen2
- Query with Azure Data Explorer (ADX) or Spark in Microsoft Fabric
- Parquet or JSON format; partitioned by date
- Connect Power BI to ADX for custom reporting

---

## SDK Support

| Platform | SDK |
|---|---|
| **Unity** | PlayFab Unity SDK (C#) |
| **Unreal Engine** | PlayFab Unreal SDK (C++) |
| **iOS** | Objective-C / Swift SDK |
| **Android** | Java / Kotlin SDK |
| **JavaScript** | Browser / Node.js SDK |
| **C++** | Cross-platform C++ SDK |
| **Python** | Python SDK |
| **C#** | .NET / Xamarin SDK |
| **Lua** | Corona SDK / Defold |

---

## LiveOps Features

| Feature | Description |
|---|---|
| **Segments** | Dynamic player groups (e.g., "players who haven't played in 7 days") |
| **Scheduled tasks** | Run CloudScript on a schedule (daily rewards, tournament reset) |
| **Actions** | Trigger actions on segment members (grant items, send push notification, ban) |
| **Push notifications** | Targeted push to iOS (APNs) and Android (FCM) devices via segments |
| **Email campaigns** | Transactional and marketing emails to player segments |
| **Title data** | Global configuration key-value store; hot-update game config without app release |
| **Player tags** | Free-form string tags for custom segmentation |
