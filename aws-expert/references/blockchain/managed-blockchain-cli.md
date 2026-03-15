# Amazon Managed Blockchain — CLI Reference

For service concepts, see [managed-blockchain-capabilities.md](managed-blockchain-capabilities.md).

---

## Amazon Managed Blockchain — Hyperledger Fabric

### Networks

```bash
# --- Create a new Fabric network (founding member created simultaneously) ---
aws managedblockchain create-network \
  --client-request-token "unique-token-$(date +%s)" \
  --name "SupplyChainNetwork" \
  --description "Multi-org supply chain consortium" \
  --framework HYPERLEDGER_FABRIC \
  --framework-version "2.2" \
  --framework-configuration '{
    "Fabric": {
      "Edition": "STANDARD"
    }
  }' \
  --voting-policy '{
    "ApprovalThresholdPolicy": {
      "ThresholdPercentage": 50,
      "ProposalDurationInHours": 24,
      "ThresholdComparator": "GREATER_THAN_OR_EQUAL_TO"
    }
  }' \
  --member-configuration '{
    "Name": "FoundingOrg",
    "Description": "The founding organization",
    "FrameworkConfiguration": {
      "Fabric": {
        "AdminUsername": "AdminUser",
        "AdminPassword": "P@ssw0rd-Admin123"
      }
    },
    "LogPublishingConfiguration": {
      "Fabric": {
        "CaLogs": {
          "Cloudwatch": {"Enabled": true}
        }
      }
    }
  }'

# --- List / describe networks ---
aws managedblockchain list-networks
aws managedblockchain list-networks --framework HYPERLEDGER_FABRIC --status AVAILABLE

aws managedblockchain get-network --network-id n-EXAMPLE1234567890ABCDEF01234

# --- Delete a network (all members must be deleted first) ---
aws managedblockchain delete-network --network-id n-EXAMPLE1234567890ABCDEF01234
```

---

### Members

```bash
# --- Create a new member (join network after invitation) ---
aws managedblockchain create-member \
  --client-request-token "member-token-$(date +%s)" \
  --network-id n-EXAMPLE1234567890ABCDEF01234 \
  --member-configuration '{
    "Name": "PartnerOrgB",
    "Description": "Partner organization B",
    "FrameworkConfiguration": {
      "Fabric": {
        "AdminUsername": "PartnerAdmin",
        "AdminPassword": "P@ssw0rd-Partner456"
      }
    },
    "LogPublishingConfiguration": {
      "Fabric": {
        "CaLogs": {
          "Cloudwatch": {"Enabled": true}
        }
      }
    }
  }'

# --- List / describe members ---
aws managedblockchain list-members --network-id n-EXAMPLE1234567890ABCDEF01234
aws managedblockchain list-members \
  --network-id n-EXAMPLE1234567890ABCDEF01234 \
  --status AVAILABLE \
  --is-owned true   # only members owned by calling account

aws managedblockchain get-member \
  --network-id n-EXAMPLE1234567890ABCDEF01234 \
  --member-id m-EXAMPLE1234567890ABCDEF01234

# --- Update member log publishing ---
aws managedblockchain update-member \
  --network-id n-EXAMPLE1234567890ABCDEF01234 \
  --member-id m-EXAMPLE1234567890ABCDEF01234 \
  --log-publishing-configuration '{
    "Fabric": {
      "CaLogs": {
        "Cloudwatch": {"Enabled": true}
      }
    }
  }'

# --- Delete a member (all peer nodes must be deleted first) ---
aws managedblockchain delete-member \
  --network-id n-EXAMPLE1234567890ABCDEF01234 \
  --member-id m-EXAMPLE1234567890ABCDEF01234
```

---

### Nodes (Peer Nodes)

```bash
# --- Create a peer node ---
aws managedblockchain create-node \
  --client-request-token "node-token-$(date +%s)" \
  --network-id n-EXAMPLE1234567890ABCDEF01234 \
  --member-id m-EXAMPLE1234567890ABCDEF01234 \
  --node-configuration '{
    "InstanceType": "bc.m5.xlarge",
    "AvailabilityZone": "us-east-1a",
    "LogPublishingConfiguration": {
      "Fabric": {
        "ChaincodeLogs": {
          "Cloudwatch": {"Enabled": true}
        },
        "PeerLogs": {
          "Cloudwatch": {"Enabled": true}
        }
      }
    },
    "StateDB": "CouchDB"
  }'

# --- List / describe nodes ---
aws managedblockchain list-nodes \
  --network-id n-EXAMPLE1234567890ABCDEF01234 \
  --member-id m-EXAMPLE1234567890ABCDEF01234

aws managedblockchain list-nodes \
  --network-id n-EXAMPLE1234567890ABCDEF01234 \
  --member-id m-EXAMPLE1234567890ABCDEF01234 \
  --status AVAILABLE

aws managedblockchain get-node \
  --network-id n-EXAMPLE1234567890ABCDEF01234 \
  --member-id m-EXAMPLE1234567890ABCDEF01234 \
  --node-id nd-EXAMPLE1234567890ABCDEF01234

# --- Update node log publishing ---
aws managedblockchain update-node \
  --network-id n-EXAMPLE1234567890ABCDEF01234 \
  --member-id m-EXAMPLE1234567890ABCDEF01234 \
  --node-id nd-EXAMPLE1234567890ABCDEF01234 \
  --log-publishing-configuration '{
    "Fabric": {
      "ChaincodeLogs": {"Cloudwatch": {"Enabled": true}},
      "PeerLogs": {"Cloudwatch": {"Enabled": true}}
    }
  }'

# --- Delete a node ---
aws managedblockchain delete-node \
  --network-id n-EXAMPLE1234567890ABCDEF01234 \
  --member-id m-EXAMPLE1234567890ABCDEF01234 \
  --node-id nd-EXAMPLE1234567890ABCDEF01234
```

---

### Proposals and Invitations

```bash
# --- Create a proposal to invite a new member ---
aws managedblockchain create-proposal \
  --client-request-token "proposal-token-$(date +%s)" \
  --network-id n-EXAMPLE1234567890ABCDEF01234 \
  --member-id m-EXAMPLE1234567890ABCDEF01234 \
  --actions '{
    "Invitations": [
      {"Principal": "210987654321"}
    ]
  }' \
  --description "Invite PartnerOrg C to the network"

# --- List / describe proposals ---
aws managedblockchain list-proposals --network-id n-EXAMPLE1234567890ABCDEF01234
aws managedblockchain get-proposal \
  --network-id n-EXAMPLE1234567890ABCDEF01234 \
  --proposal-id pr-EXAMPLE1234567890ABCDEF01234

# --- Vote on a proposal ---
aws managedblockchain vote-on-proposal \
  --network-id n-EXAMPLE1234567890ABCDEF01234 \
  --proposal-id pr-EXAMPLE1234567890ABCDEF01234 \
  --voter-member-id m-EXAMPLE1234567890ABCDEF01234 \
  --vote YES   # YES | NO

aws managedblockchain list-proposal-votes \
  --network-id n-EXAMPLE1234567890ABCDEF01234 \
  --proposal-id pr-EXAMPLE1234567890ABCDEF01234

# --- Invitations (recipient account) ---
aws managedblockchain list-invitations
aws managedblockchain get-invitation --invitation-id in-EXAMPLE1234567890ABCDEF01234

# Reject an invitation
aws managedblockchain reject-invitation --invitation-id in-EXAMPLE1234567890ABCDEF01234
```

---

### Accessor Tokens (Ethereum / Fabric API access)

```bash
# --- Create an accessor token (grants API access to Ethereum or Fabric nodes) ---
aws managedblockchain create-accessor \
  --accessor-type BILLING_TOKEN \
  --client-request-token "accessor-token-$(date +%s)"

aws managedblockchain list-accessors
aws managedblockchain get-accessor --accessor-id ac-EXAMPLE1234567890ABCDEF01234

# --- Delete an accessor token ---
aws managedblockchain delete-accessor --accessor-id ac-EXAMPLE1234567890ABCDEF01234
```

---

## Amazon Managed Blockchain — Ethereum Nodes

```bash
# --- List available Ethereum networks ---
aws managedblockchain list-networks --framework ETHEREUM

# --- Create an Ethereum node on Mainnet ---
aws managedblockchain create-node \
  --client-request-token "eth-node-token-$(date +%s)" \
  --network-id n-ETHEREUM-MAINNET \
  --node-configuration '{
    "InstanceType": "bc.m5.xlarge",
    "AvailabilityZone": "us-east-1a"
  }'
# Note: Ethereum nodes do not require a --member-id

# --- Describe an Ethereum node ---
aws managedblockchain get-node \
  --network-id n-ETHEREUM-MAINNET \
  --node-id nd-EXAMPLE1234567890ABCDEF01234

# --- List Ethereum nodes ---
aws managedblockchain list-nodes --network-id n-ETHEREUM-MAINNET

# --- Delete an Ethereum node ---
aws managedblockchain delete-node \
  --network-id n-ETHEREUM-MAINNET \
  --node-id nd-EXAMPLE1234567890ABCDEF01234
```
