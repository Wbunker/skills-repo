# Azure PlayFab — CLI Reference
For service concepts, see [playfab-capabilities.md](playfab-capabilities.md).

> **Note**: PlayFab is primarily accessed via the Game Manager web portal and PlayFab REST APIs/SDKs. There is no official `az` CLI support for PlayFab operations. The PlayFab CLI (`pfab`) provides limited configuration management. Most automation uses the PlayFab REST API directly or via SDK.

## PlayFab CLI (pfab)

```bash
# --- Install PlayFab CLI ---
# Windows (via npm)
npm install -g playfab-cli

# macOS/Linux
npm install -g playfab-cli

# Verify installation
pfab --version
pfab --help

# --- Authentication ---
pfab login                                     # Interactive login (opens browser)
pfab logout                                    # Sign out

# Set default developer account
pfab config set --key "DeveloperClientToken" --value "<your-developer-token>"

# --- Configuration ---
pfab config set --key "TitleId" --value "ABCD1"  # Set default TitleId
pfab config get --key "TitleId"                # Get a config value
pfab config list                               # List all config values

# --- Entity Management ---
pfab entity get --type "title" --id "ABCD1"   # Get title entity details
pfab entity get --type "master_player_account" --id "<player-id>"  # Get player entity
```

## PlayFab REST API (via curl)

```bash
# Set common variables
TITLE_ID="ABCD1"
BASE_URL="https://${TITLE_ID}.playfabapi.com"
SECRET_KEY="your-title-secret-key"  # From Game Manager > Settings > Secret Keys

# --- Player Authentication ---
# Login with Custom ID (anonymous device)
curl -X POST \
  "$BASE_URL/Client/LoginWithCustomID" \
  -H "Content-Type: application/json" \
  -d '{
    "TitleId": "'$TITLE_ID'",
    "CustomId": "device-unique-id-123",
    "CreateAccount": true
  }'
# Returns: SessionTicket, PlayFabId, EntityToken, EntityId

# Login with email
curl -X POST \
  "$BASE_URL/Client/LoginWithEmailAddress" \
  -H "Content-Type: application/json" \
  -d '{
    "TitleId": "'$TITLE_ID'",
    "Email": "player@example.com",
    "Password": "PlayerPass123!"
  }'

# --- Player Profile ---
# Get player profile (client API - requires session ticket)
SESSION_TICKET="<session-ticket-from-login>"
curl -X POST \
  "$BASE_URL/Client/GetPlayerProfile" \
  -H "X-Authentication: $SESSION_TICKET" \
  -H "Content-Type: application/json" \
  -d '{"PlayFabId": "<player-playfab-id>", "ProfileConstraints": {"ShowStatistics": true, "ShowTags": true}}'

# --- Player Statistics ---
# Get player statistics (server API - requires secret key)
curl -X POST \
  "$BASE_URL/Server/GetPlayerStatistics" \
  -H "X-SecretKey: $SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{"PlayFabId": "<player-playfab-id>", "StatisticNames": ["XP", "Level", "Wins"]}'

# Update player statistics (server API)
curl -X POST \
  "$BASE_URL/Server/UpdatePlayerStatistics" \
  -H "X-SecretKey: $SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "PlayFabId": "<player-playfab-id>",
    "Statistics": [
      {"StatisticName": "XP", "Value": 1500},
      {"StatisticName": "Level", "Value": 5}
    ]
  }'

# --- Leaderboards ---
# Get top 10 players on a leaderboard
curl -X POST \
  "$BASE_URL/Client/GetLeaderboard" \
  -H "X-Authentication: $SESSION_TICKET" \
  -H "Content-Type: application/json" \
  -d '{"StatisticName": "Wins", "StartPosition": 0, "MaxResultsCount": 10}'

# Get leaderboard around a specific player
curl -X POST \
  "$BASE_URL/Client/GetLeaderboardAroundPlayer" \
  -H "X-Authentication: $SESSION_TICKET" \
  -H "Content-Type: application/json" \
  -d '{"StatisticName": "Score", "MaxResultsCount": 5}'

# --- Economy (Catalog/Inventory) ---
# Get player inventory
curl -X POST \
  "$BASE_URL/Client/GetInventoryItems" \
  -H "X-EntityToken: <entity-token>" \
  -H "Content-Type: application/json" \
  -d '{}'

# Grant items to player (server API)
curl -X POST \
  "$BASE_URL/Server/GrantItemsToUser" \
  -H "X-SecretKey: $SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "PlayFabId": "<player-playfab-id>",
    "ItemIds": ["item-001", "item-002"],
    "CatalogVersion": "main"
  }'

# Add virtual currency (server API)
curl -X POST \
  "$BASE_URL/Server/AddUserVirtualCurrency" \
  -H "X-SecretKey: $SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{"PlayFabId": "<player-playfab-id>", "VirtualCurrency": "GD", "Amount": 500}'

# Subtract virtual currency
curl -X POST \
  "$BASE_URL/Server/SubtractUserVirtualCurrency" \
  -H "X-SecretKey: $SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{"PlayFabId": "<player-playfab-id>", "VirtualCurrency": "GD", "Amount": 200}'

# Get player currencies
curl -X POST \
  "$BASE_URL/Client/GetUserInventory" \
  -H "X-Authentication: $SESSION_TICKET" \
  -H "Content-Type: application/json" \
  -d '{}'

# --- Player Data ---
# Get player data (client)
curl -X POST \
  "$BASE_URL/Client/GetUserData" \
  -H "X-Authentication: $SESSION_TICKET" \
  -H "Content-Type: application/json" \
  -d '{"Keys": ["preferences", "lastLoginLocation"]}'

# Update player data (server - can write protected keys)
curl -X POST \
  "$BASE_URL/Server/UpdateUserReadOnlyData" \
  -H "X-SecretKey: $SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "PlayFabId": "<player-playfab-id>",
    "Data": {
      "accountCreationDate": {"Value": "2024-01-15"},
      "subscriptionTier": {"Value": "premium"}
    }
  }'

# --- Title Data (Global Config) ---
# Get title data (server)
curl -X POST \
  "$BASE_URL/Server/GetTitleData" \
  -H "X-SecretKey: $SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{"Keys": ["gameConfig", "seasonNumber"]}'

# Update title data (server)
curl -X POST \
  "$BASE_URL/Server/SetTitleData" \
  -H "X-SecretKey: $SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{"Key": "seasonNumber", "Value": "5"}'

# --- CloudScript Execution ---
# Execute CloudScript (client)
curl -X POST \
  "$BASE_URL/Client/ExecuteCloudScript" \
  -H "X-Authentication: $SESSION_TICKET" \
  -H "Content-Type: application/json" \
  -d '{"FunctionName": "AwardXP", "FunctionParameter": {"xp": 100}, "GeneratePlayStreamEvent": true}'

# Execute CloudScript (server)
curl -X POST \
  "$BASE_URL/Server/ExecuteCloudScript" \
  -H "X-SecretKey: $SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{"PlayFabId": "<player-playfab-id>", "FunctionName": "ProcessDailyReward", "GeneratePlayStreamEvent": true}'

# --- Segments ---
# Get player segments
curl -X POST \
  "$BASE_URL/Client/GetPlayerSegments" \
  -H "X-Authentication: $SESSION_TICKET" \
  -H "Content-Type: application/json" \
  -d '{}'

# --- Matchmaking ---
# Create matchmaking ticket (client)
curl -X POST \
  "$BASE_URL/Client/CreateMatchmakingTicket" \
  -H "X-Authentication: $SESSION_TICKET" \
  -H "Content-Type: application/json" \
  -d '{
    "Creator": {
      "Entity": {"Id": "<entity-id>", "Type": "title_player_account"},
      "Attributes": {"DataObject": {"Skill": 1200, "Region": "eastus"}}
    },
    "GiveUpAfterSeconds": 120,
    "QueueName": "ranked-1v1"
  }'

# Get matchmaking ticket status
TICKET_ID="<ticket-id>"
curl -X POST \
  "$BASE_URL/Client/GetMatchmakingTicket" \
  -H "X-Authentication: $SESSION_TICKET" \
  -H "Content-Type: application/json" \
  -d '{"TicketId": "'$TICKET_ID'", "QueueName": "ranked-1v1", "EscapeObject": false}'

# --- Multiplayer Servers ---
# Request multiplayer server (server API)
curl -X POST \
  "$BASE_URL/MultiplayerServer/RequestMultiplayerServer" \
  -H "X-EntityToken: <entity-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "BuildId": "<build-id>",
    "SessionId": "<unique-session-id>",
    "SessionCookie": "game-session-data",
    "PreferredRegions": ["EastUs", "WestUs"],
    "InitialPlayers": ["<player-entity-id-1>", "<player-entity-id-2>"]
  }'
# Returns: IPV4Address, Ports, ServerId, SessionId
```

## PowerShell Module

```powershell
# Install PlayFab PowerShell module
Install-Module -Name PlayFabAdmin -Scope CurrentUser -Force
Install-Module -Name PlayFabServer -Scope CurrentUser -Force

# Set credentials
Set-PfApiSettings -titleId "ABCD1" -developerSecretKey "your-secret-key"

# Get player profile
Get-PfPlayerProfile -PlayFabId "<player-playfab-id>"

# Get title data
Get-PfTitleData

# Update title data
Set-PfTitleData -Key "MaxLevel" -Value "50"

# Grant items to all players in a segment
$segment = Get-PfAllSegments | Where-Object { $_.Name -eq "Premium Players" }
$players = Get-PfPlayersInSegment -SegmentId $segment.Id

foreach ($player in $players.PlayerProfiles) {
    Add-PfUserVirtualCurrency `
        -PlayFabId $player.PlayerId `
        -VirtualCurrency "GD" `
        -Amount 100  # Grant 100 gold to all premium players
}
```
