# Amazon GameLift Servers — CLI Reference

For service concepts, see [gamelift-servers-capabilities.md](gamelift-servers-capabilities.md).

---

## Builds

```bash
# --- Upload a game server build ---
aws gamelift create-build \
  --name "MyGame-Server" \
  --version "1.4.2" \
  --operating-system AMAZON_LINUX_2023 \
  --storage-location '{
    "Bucket": "my-gamelift-builds",
    "Key": "builds/mygame-server-1.4.2.zip",
    "RoleArn": "arn:aws:iam::123456789012:role/GameLiftS3Access"
  }'

# --- Describe / list builds ---
aws gamelift describe-build --build-id build-1a2b3c4d-5678-90ab-cdef-EXAMPLE
aws gamelift list-builds
aws gamelift list-builds --status READY   # INITIALIZED | READY | FAILED

# --- Update build metadata ---
aws gamelift update-build \
  --build-id build-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --name "MyGame-Server" \
  --version "1.4.3"

# --- Delete a build ---
aws gamelift delete-build --build-id build-1a2b3c4d-5678-90ab-cdef-EXAMPLE

# --- Get upload credentials for direct S3 upload ---
aws gamelift request-upload-credentials --build-id build-1a2b3c4d-5678-90ab-cdef-EXAMPLE
```

---

## Scripts (Realtime Servers)

```bash
# --- Create a Realtime Server script ---
aws gamelift create-script \
  --name "MyRealtimeScript" \
  --version "2.0" \
  --storage-location '{
    "Bucket": "my-gamelift-scripts",
    "Key": "scripts/realtime-script.zip",
    "RoleArn": "arn:aws:iam::123456789012:role/GameLiftS3Access"
  }'

aws gamelift describe-script --script-id script-1a2b3c4d-5678-90ab-cdef-EXAMPLE
aws gamelift list-scripts

aws gamelift update-script \
  --script-id script-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --version "2.1" \
  --storage-location '{
    "Bucket": "my-gamelift-scripts",
    "Key": "scripts/realtime-script-v2.1.zip",
    "RoleArn": "arn:aws:iam::123456789012:role/GameLiftS3Access"
  }'

aws gamelift delete-script --script-id script-1a2b3c4d-5678-90ab-cdef-EXAMPLE
```

---

## Fleets

```bash
# --- Create an EC2 On-Demand fleet ---
aws gamelift create-fleet \
  --name "MyGame-ProdFleet" \
  --description "Production fleet for MyGame" \
  --build-id build-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --ec2-instance-type c5.large \
  --ec2-inbound-permissions '[
    {"FromPort": 7777, "ToPort": 7777, "IpRange": "0.0.0.0/0", "Protocol": "UDP"},
    {"FromPort": 7778, "ToPort": 7778, "IpRange": "0.0.0.0/0", "Protocol": "TCP"}
  ]' \
  --runtime-configuration '{
    "GameSessionActivationTimeoutSeconds": 60,
    "MaxConcurrentGameSessionActivations": 2,
    "ServerProcesses": [
      {
        "LaunchPath": "/local/game/GameServer",
        "Parameters": "-port 7777 -queryport 7778 -logFile /local/game/logs/GameSession.log",
        "ConcurrentExecutions": 5
      }
    ]
  }' \
  --new-game-session-protection-policy FULL_PROTECTION \
  --locations '[{"Location": "us-east-1"}, {"Location": "eu-west-1"}]'

# --- Create a Spot fleet ---
aws gamelift create-fleet \
  --name "MyGame-SpotFleet" \
  --build-id build-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --ec2-instance-type c5.large \
  --fleet-type SPOT \
  --ec2-inbound-permissions '[{"FromPort": 7777, "ToPort": 7780, "IpRange": "0.0.0.0/0", "Protocol": "UDP"}]' \
  --runtime-configuration '{
    "ServerProcesses": [{"LaunchPath": "/local/game/GameServer", "ConcurrentExecutions": 4}]
  }'

# --- Create an Anywhere fleet ---
aws gamelift create-fleet \
  --name "MyGame-AnywhereFleet" \
  --compute-type ANYWHERE \
  --locations '[{"Location": "custom-location-1"}]'

# --- Register compute in an Anywhere fleet ---
aws gamelift register-compute \
  --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --compute-name "OnPremServer01" \
  --ip-address "203.0.113.42" \
  --location "custom-location-1"

aws gamelift get-compute-auth-token \
  --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --compute-name "OnPremServer01"

# --- Describe / list fleets ---
aws gamelift describe-fleet-attributes --fleet-ids fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE
aws gamelift describe-fleet-attributes  # all fleets
aws gamelift list-fleets

# --- Fleet events (for debugging activation issues) ---
aws gamelift describe-fleet-events \
  --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --start-time 2024-01-01T00:00:00Z

# --- Fleet port settings ---
aws gamelift describe-fleet-port-settings --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE

# --- Update fleet attributes ---
aws gamelift update-fleet-attributes \
  --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --name "MyGame-ProdFleet-v2" \
  --new-game-session-protection-policy NO_PROTECTION

# --- Update runtime configuration ---
aws gamelift update-runtime-configuration \
  --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --runtime-configuration '{
    "ServerProcesses": [
      {"LaunchPath": "/local/game/GameServer", "ConcurrentExecutions": 8}
    ]
  }'

# --- Update inbound port settings ---
aws gamelift update-fleet-port-settings \
  --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --inbound-permission-authorizations '[{"FromPort": 8888, "ToPort": 8888, "IpRange": "0.0.0.0/0", "Protocol": "UDP"}]' \
  --inbound-permission-revocations '[{"FromPort": 7779, "ToPort": 7779, "IpRange": "0.0.0.0/0", "Protocol": "UDP"}]'

# --- Delete a fleet (must have 0 instances first) ---
aws gamelift delete-fleet --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE
```

---

## Fleet Capacity

```bash
# --- Describe current capacity ---
aws gamelift describe-fleet-capacity --fleet-ids fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE

# --- Manually set desired capacity ---
aws gamelift update-fleet-capacity \
  --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --desired-instances 10 \
  --min-size 2 \
  --max-size 20 \
  --location us-east-1

# --- Target tracking auto scaling ---
aws gamelift put-scaling-policy \
  --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --name "KeepSpareCap20Pct" \
  --policy-type TargetBased \
  --target-configuration '{"TargetValue": 0.8}' \
  --metric-name PercentAvailableGameSessions

# --- Rule-based scaling policy ---
aws gamelift put-scaling-policy \
  --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --name "ScaleUpOnLoad" \
  --policy-type RuleBased \
  --metric-name AvailableGameSessions \
  --comparison-operator LessThanThreshold \
  --threshold 5 \
  --evaluation-periods 1 \
  --scaling-adjustment 2 \
  --scaling-adjustment-type ChangeInCapacity

aws gamelift describe-scaling-policies --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE
aws gamelift delete-scaling-policy --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE --name "ScaleUpOnLoad"
```

---

## Fleet Utilization

```bash
# --- Describe active processes, game sessions, and player sessions ---
aws gamelift describe-fleet-utilization --fleet-ids fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE

# --- List instances in a fleet ---
aws gamelift describe-instances --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE

# --- Get remote access credentials for an instance (for debugging) ---
aws gamelift get-instance-access \
  --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --instance-id i-0abcdef1234567890
```

---

## Game Sessions

```bash
# --- Create a game session directly on a fleet ---
aws gamelift create-game-session \
  --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --name "Room-42" \
  --maximum-player-session-count 8 \
  --game-properties '[{"Key": "map", "Value": "dungeon_1"}, {"Key": "mode", "Value": "ranked"}]' \
  --game-session-data '{"region": "us-east-1", "tier": "gold"}' \
  --location us-east-1

# --- Create a game session via alias ---
aws gamelift create-game-session \
  --alias-id alias-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --maximum-player-session-count 4

# --- Describe game sessions ---
aws gamelift describe-game-sessions --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE
aws gamelift describe-game-sessions --game-session-id arn:aws:gamelift:us-east-1::gamesession/fleet-xxx/gsess-xxx
aws gamelift describe-game-session-details --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE

# --- Search for available game sessions ---
aws gamelift search-game-sessions \
  --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --filter-expression "hasAvailablePlayerSessions=true AND gameSessionProperties.mode='ranked'" \
  --sort-expression "creationTimeMillis ASC" \
  --limit 10 \
  --location us-east-1

# --- Update a game session ---
aws gamelift update-game-session \
  --game-session-id arn:aws:gamelift:us-east-1::gamesession/fleet-xxx/gsess-xxx \
  --maximum-player-session-count 10 \
  --protection-policy FULL_PROTECTION \
  --player-session-creation-policy ACCEPT_ALL   # ACCEPT_ALL | DENY_ALL
```

---

## Player Sessions

```bash
# --- Create a player session (reserve a slot) ---
aws gamelift create-player-session \
  --game-session-id arn:aws:gamelift:us-east-1::gamesession/fleet-xxx/gsess-xxx \
  --player-id "player-uuid-1234"

# --- Create multiple player sessions at once ---
aws gamelift create-player-sessions \
  --game-session-id arn:aws:gamelift:us-east-1::gamesession/fleet-xxx/gsess-xxx \
  --player-ids '["player-uuid-1234", "player-uuid-5678"]'

# --- Describe player sessions ---
aws gamelift describe-player-sessions \
  --game-session-id arn:aws:gamelift:us-east-1::gamesession/fleet-xxx/gsess-xxx

aws gamelift describe-player-sessions \
  --player-id "player-uuid-1234"

aws gamelift describe-player-sessions \
  --game-session-id arn:aws:gamelift:us-east-1::gamesession/fleet-xxx/gsess-xxx \
  --player-session-status-filter ACTIVE   # RESERVED | ACTIVE | COMPLETED | TIMEDOUT
```

---

## Game Session Queues

```bash
# --- Create a multi-region queue ---
aws gamelift create-game-session-queue \
  --name "GlobalMatchQueue" \
  --timeout-in-seconds 300 \
  --destinations '[
    {"DestinationArn": "arn:aws:gamelift:us-east-1::fleet/fleet-aaa"},
    {"DestinationArn": "arn:aws:gamelift:us-east-1::alias/alias-bbb"},
    {"DestinationArn": "arn:aws:gamelift:eu-west-1::fleet/fleet-ccc"}
  ]' \
  --player-latency-policies '[
    {"MaximumIndividualPlayerLatencyMilliseconds": 100, "PolicyDurationSeconds": 60},
    {"MaximumIndividualPlayerLatencyMilliseconds": 200}
  ]' \
  --priority-configuration '{
    "PriorityOrder": ["LATENCY", "COST", "DESTINATION"],
    "LocationOrder": ["us-east-1", "eu-west-1"]
  }' \
  --notification-target "arn:aws:sns:us-east-1:123456789012:GameLiftQueueNotifications"

aws gamelift describe-game-session-queues --names GlobalMatchQueue
aws gamelift list-game-session-queues

# --- Place a game session via queue ---
aws gamelift start-game-session-placement \
  --placement-id "placement-uuid-2024-001" \
  --game-session-queue-name "GlobalMatchQueue" \
  --maximum-player-session-count 8 \
  --player-latencies '[
    {"PlayerId": "player-1", "RegionIdentifier": "us-east-1", "LatencyInMilliseconds": 30},
    {"PlayerId": "player-1", "RegionIdentifier": "eu-west-1", "LatencyInMilliseconds": 110}
  ]' \
  --game-session-name "Room-42" \
  --game-properties '[{"Key": "map", "Value": "arena_2"}]'

aws gamelift describe-game-session-placement --placement-id placement-uuid-2024-001
aws gamelift stop-game-session-placement --placement-id placement-uuid-2024-001

aws gamelift update-game-session-queue \
  --name "GlobalMatchQueue" \
  --timeout-in-seconds 600

aws gamelift delete-game-session-queue --name "GlobalMatchQueue"
```

---

## FlexMatch Matchmaking

```bash
# --- Create a matchmaking rule set ---
aws gamelift create-matchmaking-rule-set \
  --name "2v2RankedRuleSet" \
  --rule-set-body '{
    "name": "2v2Ranked",
    "ruleLanguageVersion": "1.0",
    "teams": [
      {"name": "red", "minPlayers": 2, "maxPlayers": 2},
      {"name": "blue", "minPlayers": 2, "maxPlayers": 2}
    ],
    "rules": [
      {
        "name": "FairTeams",
        "description": "Teams within 10 skill points",
        "type": "distance",
        "measurements": ["avg(teams[*].players.playerAttributes[skill])"],
        "referenceValue": 10,
        "maxDistance": 10
      },
      {
        "name": "EqualTeamSkill",
        "description": "Balance teams by skill",
        "type": "distanceSort",
        "sortDirection": "ascending",
        "sortAttribute": "playerAttributes[skill]",
        "teamPartitions": [["red"], ["blue"]]
      }
    ],
    "expansions": [
      {
        "target": "rules[FairTeams].maxDistance",
        "steps": [
          {"waitTimeSeconds": 60, "value": 20},
          {"waitTimeSeconds": 120, "value": 50}
        ]
      }
    ]
  }'

aws gamelift describe-matchmaking-rule-sets --names 2v2RankedRuleSet
aws gamelift list-matchmaking-rule-sets
aws gamelift validate-matchmaking-rule-set --rule-set-body file://ruleset.json

# --- Create a matchmaking configuration ---
aws gamelift create-matchmaking-configuration \
  --name "2v2RankedConfig" \
  --description "2v2 ranked matchmaking" \
  --game-session-queue-arns '["arn:aws:gamelift:us-east-1::gamesessionqueue/GlobalMatchQueue"]' \
  --rule-set-name "2v2RankedRuleSet" \
  --request-timeout-seconds 180 \
  --acceptance-required \
  --acceptance-timeout-seconds 30 \
  --notification-target "arn:aws:sns:us-east-1:123456789012:MatchmakingEvents" \
  --additional-player-count 0 \
  --backfill-mode MANUAL \
  --flex-match-mode WITH_QUEUE

aws gamelift describe-matchmaking-configurations --names 2v2RankedConfig
aws gamelift list-matchmaking-configurations

# --- Start a matchmaking ticket ---
aws gamelift start-matchmaking \
  --configuration-name "2v2RankedConfig" \
  --players '[
    {
      "PlayerId": "player-uuid-1234",
      "PlayerAttributes": {"skill": {"N": 1850}},
      "LatencyInMs": {"us-east-1": 25, "eu-west-1": 105}
    },
    {
      "PlayerId": "player-uuid-5678",
      "PlayerAttributes": {"skill": {"N": 1780}},
      "LatencyInMs": {"us-east-1": 35, "eu-west-1": 115}
    }
  ]'

# --- Poll ticket status ---
aws gamelift describe-matchmaking --ticket-ids ticket-1a2b3c4d-5678-90ab-cdef-EXAMPLE

# --- Accept / decline a match (when acceptance required) ---
aws gamelift accept-match \
  --ticket-id ticket-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --player-ids '["player-uuid-1234"]' \
  --acceptance-type ACCEPT   # ACCEPT | REJECT

# --- Stop a matchmaking ticket ---
aws gamelift stop-matchmaking --ticket-id ticket-1a2b3c4d-5678-90ab-cdef-EXAMPLE

# --- Backfill an in-progress game session ---
aws gamelift start-match-backfill \
  --configuration-name "2v2RankedConfig" \
  --game-session-arn "arn:aws:gamelift:us-east-1::gamesession/fleet-xxx/gsess-xxx" \
  --players '[{"PlayerId": "existing-player", "PlayerAttributes": {"skill": {"N": 1900}}}]'

# --- Delete matchmaking resources ---
aws gamelift delete-matchmaking-configuration --name "2v2RankedConfig"
aws gamelift delete-matchmaking-rule-set --name "2v2RankedRuleSet"
```

---

## Aliases

```bash
# --- Create a simple alias (points to a fleet) ---
aws gamelift create-alias \
  --name "ProdAlias" \
  --description "Points to current production fleet" \
  --routing-strategy '{"Type": "SIMPLE", "FleetId": "fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE"}'

# --- Create a terminal alias (returns a message instead of routing) ---
aws gamelift create-alias \
  --name "MaintenanceAlias" \
  --routing-strategy '{"Type": "TERMINAL", "Message": "Servers are down for maintenance. Try again in 30 minutes."}'

aws gamelift describe-alias --alias-id alias-1a2b3c4d-5678-90ab-cdef-EXAMPLE
aws gamelift list-aliases
aws gamelift list-aliases --routing-strategy-type SIMPLE   # SIMPLE | TERMINAL

# --- Update alias (swap fleet — zero-downtime fleet rotation) ---
aws gamelift update-alias \
  --alias-id alias-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --routing-strategy '{"Type": "SIMPLE", "FleetId": "fleet-NEW-fleet-id"}'

aws gamelift delete-alias --alias-id alias-1a2b3c4d-5678-90ab-cdef-EXAMPLE

# --- Resolve alias to current fleet ---
aws gamelift resolve-alias --alias-id alias-1a2b3c4d-5678-90ab-cdef-EXAMPLE
```

---

## Locations (Multi-Region Fleet Management)

```bash
# --- Create a custom location (for Anywhere fleets) ---
aws gamelift create-location --location-name "custom-location-1"
aws gamelift list-locations
aws gamelift list-locations --filters CUSTOM   # AWS | CUSTOM
aws gamelift delete-location --location-name "custom-location-1"

# --- Add / remove locations from an existing fleet ---
aws gamelift create-fleet-locations \
  --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --locations '[{"Location": "ap-southeast-1"}]'

aws gamelift describe-fleet-location-attributes \
  --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE

aws gamelift describe-fleet-location-capacity \
  --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --location us-east-1

aws gamelift describe-fleet-location-utilization \
  --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --location us-east-1

aws gamelift delete-fleet-locations \
  --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --locations ap-southeast-1
```

---

## VPC Peering

```bash
# --- Authorize a VPC peering connection ---
aws gamelift create-vpc-peering-authorization \
  --game-lift-aws-account-id 123456789012 \
  --peer-vpc-id vpc-0abcdef1234567890

aws gamelift describe-vpc-peering-authorizations

# --- Create the peering connection ---
aws gamelift create-vpc-peering-connection \
  --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --peer-vpc-aws-account-id 123456789012 \
  --peer-vpc-id vpc-0abcdef1234567890

aws gamelift describe-vpc-peering-connections --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE

aws gamelift delete-vpc-peering-connection \
  --fleet-id fleet-1a2b3c4d-5678-90ab-cdef-EXAMPLE \
  --vpc-peering-connection-id pcx-0abcdef1234567890

aws gamelift delete-vpc-peering-authorization \
  --game-lift-aws-account-id 123456789012 \
  --peer-vpc-id vpc-0abcdef1234567890
```
