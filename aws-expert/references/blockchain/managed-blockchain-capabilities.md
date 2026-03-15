# Amazon Managed Blockchain — Capabilities Reference

For CLI commands, see [managed-blockchain-cli.md](managed-blockchain-cli.md).

---

## Overview

**Purpose**: Fully managed service for creating and managing scalable blockchain networks using open-source frameworks. Eliminates the operational overhead of provisioning hardware, configuring software, and setting up security.

### Supported Frameworks

| Framework | Use case |
|---|---|
| **Hyperledger Fabric** | Private, permissioned blockchain for enterprise consortia; fine-grained access control, private channels, smart contracts (chaincode) |
| **Ethereum** | Public blockchain node access; run managed Ethereum mainnet or testnet nodes for decentralized application (dApp) development |

---

## Hyperledger Fabric on Managed Blockchain

### Core Concepts

| Concept | Description |
|---|---|
| **Network** | The top-level Fabric blockchain. One organization creates it; others join via invitation. |
| **Member** | A participant organization in the network. Each member has its own peer nodes, certificate authority, and endorsement policies. |
| **Peer Node** | A managed EC2-backed node that hosts a copy of the ledger and runs chaincode. Participates in transaction endorsement and block validation. |
| **Ordering Service** | Managed by Amazon (Raft-based); orders endorsed transactions into blocks and distributes them to peers. |
| **Channel** | A private sub-ledger shared between specific members. Members on a channel can see only that channel's transactions. |
| **Chaincode** | Smart contract logic running on peer nodes. Installed per-peer and instantiated per-channel. Supports Go, Node.js, Java. |
| **Certificate Authority (CA)** | Managed CA per member; issues enrollment certificates (ECert) and transaction certificates (TCert) using Fabric CA. |
| **Anchor Peer** | A peer configured as the gossip anchor for cross-organization communication within a channel. |

### Network Configuration

- **Framework version**: Hyperledger Fabric 1.4 and 2.x supported
- **Edition**: `STARTER` (for development; limited features) or `STANDARD` (for production)
- **Voting policy**: Configures how many members must approve proposals (member invitations, network deletion). Expressed as `ThresholdComparator` + `ThresholdPercentage`.
- **Proposal threshold**: When a member creates a proposal (e.g., to invite a new member), other members vote `YES` or `NO`. The proposal passes if the threshold is met within the expiration window.

### Network Invitations and Voting

- Any existing member can create a **proposal** to invite a new organization (by AWS account ID)
- Proposals have a configurable `ProposalDurationInHours` expiration window
- Members vote `YES` or `NO` via `vote-on-proposal`
- Proposal passes when `ThresholdPercentage` of eligible votes are `YES` (using `GREATER_THAN` or `GREATER_THAN_OR_EQUAL_TO` comparator)
- Invited account receives an **invitation** and must call `create-member` to join before the invitation expires
- Network deletion also requires a proposal and vote

### Fabric Node Types

| Node type | Description |
|---|---|
| **bc.t3.small** | Development/testing; limited throughput |
| **bc.t3.medium** | Small workloads |
| **bc.m5.large / xlarge / 2xlarge / 4xlarge** | Production workloads; higher TPS |

### Managed CA and Enrollment

- Each member gets a managed Hyperledger Fabric CA endpoint
- Use `fabric-ca-client enroll` to obtain an admin identity
- Admin identity used to register and enroll additional users and peer identities
- Certificates stored in Amazon S3 (accessible via member's CA endpoint)

### CloudWatch Logs Integration

- Peer node logs (`ca`, `peer`, `chaincode`, `couchdb`) forwarded to CloudWatch Logs
- Orderer logs forwarded per network
- Configure log publishing on node/member creation or update
- Use CloudWatch Logs Insights to query chaincode and peer logs for transaction debugging and audit

### Fabric SDK and REST API

- Submit transactions via **Fabric SDK** (Node.js, Java, Go)
- **Managed Blockchain Query** provides a REST API for querying transaction history, token balances, and NFT data without running Fabric SDK directly
- Channels are configured using Fabric SDK or CLI tools via Hyperledger Fabric client

### Key Workflow (Fabric)

1. Create network — founding member is created automatically
2. Invite other organizations (proposals + vote)
3. Create peer nodes per member
4. Configure channels (using Fabric SDK or CLI tools via Hyperledger Fabric client)
5. Install and instantiate chaincode on peers/channels
6. Submit transactions via Fabric SDK (Node.js, Java, Go)

---

## Ethereum on Managed Blockchain

**Purpose**: Run managed Ethereum nodes (full or archive) without managing the underlying infrastructure.

### Node Types

| Type | Description |
|---|---|
| **Full node** | Stores recent state and validates transactions; cannot query historical state older than ~128 blocks |
| **Archive node** | Stores complete historical state from genesis; required for queries like `eth_getBalance` at a historical block number |

### Supported Networks

| Network | Description |
|---|---|
| **Ethereum Mainnet** | The live public Ethereum network (ETH, ERC-20, NFTs, DeFi) |
| **Goerli (Görli)** | Ethereum test network (Proof-of-Authority; faucet ETH available for development) |
| **Sepolia** | Ethereum test network; lightweight proof-of-work testnet used for smart contract testing |

### Access Endpoints

Each Ethereum node exposes two endpoints:

| Endpoint | Protocol | Use case |
|---|---|---|
| **HTTP** | JSON-RPC over HTTPS | Request-response queries (e.g., `eth_blockNumber`, `eth_getBalance`) |
| **WebSocket** | WSS | Subscribe to events (e.g., `eth_subscribe` for new blocks or logs) |

Endpoints are accessible within the VPC where the node is deployed (private). Access controlled via VPC security groups.

### dApp Connectivity

- Connect Web3.js or ethers.js to the HTTP or WebSocket endpoint
- Use standard Ethereum JSON-RPC methods
- Archive nodes support `eth_getLogs` for historical event queries (used by DeFi indexers, NFT marketplaces)
- Accessor tokens (`BILLING_TOKEN`) are used to authenticate API access to Ethereum nodes

### Managed Blockchain Query (Ethereum)

- REST API for querying on-chain data without running a full Ethereum node client
- **Transaction history**: query transactions by address or block
- **Token balances**: ERC-20 and ERC-721 token balance lookups
- **NFT data**: metadata and ownership queries for ERC-721 tokens
- Reduces need for custom indexing infrastructure

### Limits

| Resource | Limit |
|---|---|
| Nodes per account per Region | 2 (adjustable) |
| Supported node instance types | `bc.t3.large`, `bc.m5.xlarge`, `bc.m5.2xlarge`, `bc.m5.4xlarge` |

---

## Billing

| Resource | Pricing basis |
|---|---|
| **Fabric member** | Per-member hourly charge (varies by edition: STARTER vs. STANDARD) |
| **Fabric peer node** | Per-node hourly charge based on instance type |
| **Fabric storage** | Per GB-month for ledger storage |
| **Ethereum node** | Per-node hourly charge based on instance type |
| **Managed Blockchain Query** | Per API request |

- Billing begins when a member or node reaches `AVAILABLE` status
- Storage charges apply to the ledger and CouchDB state database (Fabric)

---

## Quotas

| Resource | Limit |
|---|---|
| Fabric: members per network | 5 (STARTER) / 14 (STANDARD) |
| Fabric: peer nodes per member | 3 (STARTER) / 3 (STANDARD) |
| Ethereum: nodes per account per Region | 2 (adjustable) |

---

## Integration Patterns

| Pattern | Description |
|---|---|
| **Managed Blockchain + API Gateway + Lambda** | Build a REST API that invokes Fabric transactions via the Fabric SDK running in Lambda |
| **Managed Blockchain + CloudWatch Logs Insights** | Query chaincode and peer logs for transaction debugging and audit |
| **Ethereum node + Web3.js/ethers.js** | Connect dApp front-ends or backend services to mainnet or testnet via HTTP/WebSocket endpoints |
| **Managed Blockchain Query + Lambda** | Serverless queries for token balances and transaction history without managing node client libraries |
