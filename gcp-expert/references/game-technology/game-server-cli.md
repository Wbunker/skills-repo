# Game Technology on GCP — CLI Reference

## GKE Cluster for Agones

```bash
# Create a GKE cluster for game servers
gcloud container clusters create game-servers-us-central1 \
  --region=us-central1 \
  --release-channel=stable \
  --num-nodes=1 \
  --machine-type=n2-standard-4 \
  --workload-pool=my-project.svc.id.goog \
  --enable-ip-alias \
  --project=my-project

# Create a dedicated game server node pool with:
# - High-performance machine type (c2-standard-8 for CPU-intensive games)
# - gVNIC for better network performance
# - Node taint so only game server pods schedule here
# - Autoscaling 0-100 nodes
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
  --enable-gvnic \
  --disk-type=pd-ssd \
  --disk-size=100GB \
  --project=my-project

# Create a Spot VM node pool for cost-sensitive casual game modes
gcloud container node-pools create gameserver-spot-pool \
  --cluster=game-servers-us-central1 \
  --region=us-central1 \
  --machine-type=n2-standard-8 \
  --num-nodes=0 \
  --enable-autoscaling \
  --min-nodes=0 \
  --max-nodes=200 \
  --spot \
  --node-taints=agones.dev/gameserver=true:NoExecute,agones.dev/spot=true:NoSchedule \
  --node-labels=agones.dev/gameserver=true,agones.dev/spot=true \
  --enable-gvnic \
  --project=my-project

# Get credentials for the cluster
gcloud container clusters get-credentials game-servers-us-central1 \
  --region=us-central1 \
  --project=my-project
```

---

## Agones Installation

```bash
# Install Agones using kubectl (YAML from Agones releases)
kubectl create namespace agones-system

kubectl apply \
  --server-side \
  -f https://raw.githubusercontent.com/googleforgames/agones/release-1.37.0/install/yaml/install.yaml

# Wait for Agones to be ready
kubectl wait --for=condition=available --timeout=120s deployment/agones-controller \
  -n agones-system

kubectl wait --for=condition=available --timeout=120s deployment/agones-allocator \
  -n agones-system

# Check Agones components
kubectl get pods -n agones-system

# Install Agones with Helm (alternative)
helm repo add agones https://agones.dev/chart/stable
helm repo update

helm install agones --namespace agones-system \
  --create-namespace \
  agones/agones \
  --set agones.featureGates="NodeExternalDNS=true" \
  --set agones.controller.safeToEvict=true
```

---

## Agones Game Server Operations

```bash
# Deploy a simple game server
cat > game-server.yaml << 'EOF'
apiVersion: agones.dev/v1
kind: GameServer
metadata:
  name: my-game-server
  labels:
    game-mode: deathmatch
    region: us-central1
spec:
  ports:
    - name: default
      portPolicy: Dynamic    # Agones assigns a dynamic NodePort
      containerPort: 7777
      protocol: UDP
  template:
    spec:
      nodeSelector:
        agones.dev/gameserver: "true"
      tolerations:
        - key: "agones.dev/gameserver"
          operator: "Exists"
          effect: "NoExecute"
      containers:
        - name: game-server
          image: us-central1-docker.pkg.dev/my-project/games/my-game-server:1.0.0
          resources:
            requests:
              cpu: "2"
              memory: "4Gi"
            limits:
              cpu: "4"
              memory: "8Gi"
EOF

kubectl apply -f game-server.yaml

# Watch game server status
kubectl get gameserver my-game-server --watch

# Get the game server's external IP and port
kubectl get gameserver my-game-server \
  -o jsonpath='{.status.address}:{.status.ports[0].port}'

# Delete a game server
kubectl delete gameserver my-game-server
```

---

## Agones Fleet

```bash
# Deploy a Fleet of game servers
cat > fleet.yaml << 'EOF'
apiVersion: agones.dev/v1
kind: Fleet
metadata:
  name: my-game-fleet
spec:
  replicas: 5            # Start with 5 ready servers
  template:
    metadata:
      labels:
        game-mode: battle-royale
    spec:
      ports:
        - name: default
          portPolicy: Dynamic
          containerPort: 7777
          protocol: UDP
      health:
        initialDelaySeconds: 30
        periodSeconds: 5
        failureThreshold: 3
      template:
        spec:
          nodeSelector:
            agones.dev/gameserver: "true"
          tolerations:
            - key: "agones.dev/gameserver"
              operator: "Exists"
              effect: "NoExecute"
          containers:
            - name: game-server
              image: us-central1-docker.pkg.dev/my-project/games/my-game-server:1.0.0
              resources:
                requests:
                  cpu: "2"
                  memory: "4Gi"
                limits:
                  cpu: "4"
                  memory: "8Gi"
EOF

kubectl apply -f fleet.yaml

# List fleets
kubectl get fleets

# Get fleet status (ready, allocated, total counts)
kubectl describe fleet my-game-fleet

# Scale a fleet manually
kubectl scale fleet my-game-fleet --replicas=20

# List game servers in a fleet
kubectl get gameservers -l agones.dev/fleet=my-game-fleet \
  -o custom-columns="NAME:.metadata.name,STATUS:.status.state,IP:.status.address,PORT:.status.ports[0].port"
```

---

## FleetAutoscaler

```bash
# Deploy a buffer-based FleetAutoscaler
cat > fleet-autoscaler.yaml << 'EOF'
apiVersion: autoscaling.agones.dev/v1
kind: FleetAutoscaler
metadata:
  name: my-game-fleet-autoscaler
spec:
  fleetName: my-game-fleet
  policy:
    type: Buffer
    buffer:
      bufferSize: 10       # Keep 10 Ready servers
      minReplicas: 5       # Never go below 5 total
      maxReplicas: 200     # Never go above 200 total
EOF

kubectl apply -f fleet-autoscaler.yaml

# Describe autoscaler (shows current scale decisions)
kubectl describe fleetautoscaler my-game-fleet-autoscaler

# List all fleet autoscalers
kubectl get fleetautoscalers
```

---

## GameServer Allocation

```bash
# Allocate a game server from a fleet (claim a Ready server)
cat > allocation.yaml << 'EOF'
apiVersion: allocation.agones.dev/v1
kind: GameServerAllocation
spec:
  selectors:
    - matchLabels:
        agones.dev/fleet: my-game-fleet
        game-mode: battle-royale
  scheduling: Packed     # Pack players onto fewer servers to save cost
                         # (alternative: Distributed for lower per-server load)
  metadata:
    labels:
      match-id: "match-12345"
    annotations:
      players: "player1,player2,player3,player4"
EOF

kubectl apply -f allocation.yaml

# The allocation response contains the server's IP and port
kubectl get gameserverallocation <allocation-name> \
  -o jsonpath='{.status.address}:{.status.ports[0].port}'

# Check if allocation was successful
kubectl get gameserverallocation <allocation-name> \
  -o jsonpath='{.status.state}'
# Returns: Allocated (success) or UnAllocated (no ready servers)
```

---

## Cloud Spanner for Games

```bash
# Create a multi-region Spanner instance for global game
gcloud spanner instances create game-db \
  --config=nam4 \
  --description="Game Backend Database" \
  --nodes=3 \
  --project=my-project

# For lower cost (single region, less durability):
gcloud spanner instances create game-db-dev \
  --config=regional-us-central1 \
  --description="Game Backend Dev Database" \
  --processing-units=100 \
  --project=my-project

# Create the game database
gcloud spanner databases create game \
  --instance=game-db \
  --project=my-project

# Create tables with DDL file
cat > game-schema.sql << 'EOF'
CREATE TABLE Players (
  player_id STRING(36) NOT NULL,
  username STRING(64) NOT NULL,
  email STRING(128),
  created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
  rating INT64 NOT NULL DEFAULT (1000),
  currency_coins INT64 NOT NULL DEFAULT (0),
) PRIMARY KEY (player_id);

CREATE UNIQUE INDEX PlayersByUsername ON Players(username);

CREATE TABLE PlayerInventory (
  player_id STRING(36) NOT NULL,
  item_id STRING(64) NOT NULL,
  quantity INT64 NOT NULL DEFAULT (1),
  acquired_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
) PRIMARY KEY (player_id, item_id),
  INTERLEAVE IN PARENT Players ON DELETE CASCADE;

CREATE TABLE Leaderboard (
  season STRING(16) NOT NULL,
  score INT64 NOT NULL,
  player_id STRING(36) NOT NULL,
  username STRING(64) NOT NULL,
  updated_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
) PRIMARY KEY (season, score DESC, player_id);

CREATE TABLE MatchHistory (
  match_id STRING(36) NOT NULL,
  player_id STRING(36) NOT NULL,
  started_at TIMESTAMP NOT NULL,
  completed_at TIMESTAMP,
  placement INT64,
  kills INT64 DEFAULT (0),
  score INT64 DEFAULT (0),
  rating_delta INT64 DEFAULT (0),
) PRIMARY KEY (player_id, started_at DESC, match_id),
  INTERLEAVE IN PARENT Players ON DELETE CASCADE;
EOF

gcloud spanner databases ddl update game \
  --instance=game-db \
  --ddl-file=game-schema.sql \
  --project=my-project

# List databases
gcloud spanner databases list \
  --instance=game-db \
  --project=my-project

# Execute a query
gcloud spanner databases execute-sql game \
  --instance=game-db \
  --sql="SELECT player_id, username, rating FROM Players ORDER BY rating DESC LIMIT 10" \
  --project=my-project

# Insert test data
gcloud spanner databases execute-sql game \
  --instance=game-db \
  --sql="INSERT INTO Players (player_id, username, rating, currency_coins, created_at) VALUES ('p-001', 'ProGamer99', 2150, 5000, PENDING_COMMIT_TIMESTAMP())" \
  --project=my-project

# Describe instance (shows node count, state, config)
gcloud spanner instances describe game-db --project=my-project

# Scale Spanner instance
gcloud spanner instances update game-db \
  --nodes=6 \
  --project=my-project

# Delete Spanner database (irreversible)
gcloud spanner databases delete game \
  --instance=game-db \
  --project=my-project
```

---

## Firebase for Games

```bash
# Initialize Firebase in your project
firebase init --project=my-project

# Select features:
# - Firestore (game data, player profiles)
# - Authentication (player sign-in)
# - Functions (game backend logic)
# - Hosting (optional: game web portal)

# Deploy Firestore security rules
cat > firestore.rules << 'EOF'
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Players can only read/write their own data
    match /players/{playerId} {
      allow read: if request.auth != null;
      allow write: if request.auth.uid == playerId;
    }

    // Leaderboard: read only; write only by server (Cloud Function)
    match /leaderboard/{entry} {
      allow read: if request.auth != null;
      allow write: if false;  // Only Cloud Functions can write
    }

    // Game rooms: players can read rooms they're in
    match /rooms/{roomId} {
      allow read: if request.auth != null
                  && request.auth.uid in resource.data.playerIds;
      allow write: if false;  // Only server manages rooms
    }
  }
}
EOF

firebase deploy --only firestore:rules --project=my-project

# Deploy Cloud Functions for game logic
firebase deploy --only functions --project=my-project

# Run the Firebase Emulator Suite for local development
firebase emulators:start \
  --only auth,firestore,functions \
  --project=my-project
```

---

## Artifact Registry for Game Server Images

```bash
# Create a repository for game server container images
gcloud artifacts repositories create game-servers \
  --repository-format=docker \
  --location=us-central1 \
  --description="Game server container images" \
  --project=my-project

# Configure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build and push a game server image
docker build \
  -t us-central1-docker.pkg.dev/my-project/game-servers/my-game-server:1.0.0 \
  -f Dockerfile.gameserver \
  .

docker push us-central1-docker.pkg.dev/my-project/game-servers/my-game-server:1.0.0

# List images
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/my-project/game-servers \
  --include-tags \
  --project=my-project

# Tag latest stable for fleet deployment
gcloud artifacts docker tags add \
  us-central1-docker.pkg.dev/my-project/game-servers/my-game-server:1.0.0 \
  us-central1-docker.pkg.dev/my-project/game-servers/my-game-server:stable
```
