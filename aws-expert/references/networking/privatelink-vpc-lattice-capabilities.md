# AWS PrivateLink & VPC Lattice — Capabilities Reference
For CLI commands, see [privatelink-vpc-lattice-cli.md](privatelink-vpc-lattice-cli.md).

## AWS PrivateLink & VPC Endpoints

**Purpose**: Access AWS services and your own services privately within the AWS network without traffic traversing the internet.

### Endpoint Types

| Type | Services | Mechanism |
|---|---|---|
| **Gateway endpoint** | S3, DynamoDB only | Route table entry; free; not powered by PrivateLink |
| **Interface endpoint** | 100+ AWS services, third-party services, your own endpoint services | ENI with private IP in your subnet; powered by PrivateLink |
| **Gateway Load Balancer endpoint** | Virtual appliances behind GWLB | Route table entry; redirects traffic through GWLB |
| **Resource endpoint** | Databases, EC2 instances, IPs in other VPCs | Direct private access to specific resources |
| **Service network endpoint** | VPC Lattice service networks | Access multiple services via a single endpoint |

### Interface Endpoint Details

- Creates one or more **Endpoint Network Interfaces (ENIs)** in your specified subnets
- Private DNS enabled by default: the service's public DNS name resolves to the endpoint's private IP within the VPC
- **Acceptance model**: Endpoint service owner can require manual acceptance of connection requests (state: `PendingAcceptance` → `Pending` → `Available`)
- **Endpoint policy**: IAM resource policy attached to the endpoint; controls which principals can use it; default allows all

### Creating an Endpoint Service (PrivateLink)

1. Create an NLB or GWLB in front of your service
2. Create a **VPC Endpoint Service** pointing to the NLB/GWLB
3. Optionally require acceptance; configure allowed principals
4. Share the service name with consumers; they create interface endpoints to connect

### DNS Resolution Pattern

```
Consumer VPC → Interface endpoint ENI (private IP in consumer subnet)
             → PrivateLink → Provider VPC NLB → Provider service

DNS: service.region.amazonaws.com → resolves to endpoint ENI private IP (within VPC)
                                  → resolves to public IP (outside VPC, if DNS override disabled)
```

---

## Amazon VPC Lattice

**Purpose**: Fully managed application networking layer for connecting, securing, and monitoring communication between services across multiple VPCs and accounts — without managing VPC peering, route tables, or security groups between services.

### Core Concepts

| Concept | Description |
|---|---|
| **Service network** | Logical boundary that groups services; VPCs associate with a service network to access all services in it |
| **Service** | Represents an application or microservice; has a DNS name; associated with a service network |
| **Listener** | Accepts incoming traffic on a protocol/port (HTTP, HTTPS, gRPC) for a service |
| **Rule** | Conditions + action within a listener; routes traffic to target groups based on path, header, method |
| **Target group** | Group of compute targets (EC2 instances, ECS tasks, Lambda functions, ALBs, IPs) |
| **Auth policy** | Resource-based IAM policy on the service or service network; enforces SigV4 authentication |

### Auth Policies

VPC Lattice supports two auth types:
- **None**: No authentication required (network-level controls only)
- **AWS_IAM**: Requires SigV4-signed requests; callers must have IAM permissions to invoke the service

Auth policy example — allow only a specific IAM role:
```json
{
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::123456789012:role/ServiceA"},
    "Action": "vpc-lattice-svcs:Invoke",
    "Resource": "*"
  }]
}
```

### Key Features

- **Cross-VPC and cross-account**: Services and consumers can be in different VPCs and accounts; no peering or route table changes needed
- **Built-in observability**: Access logs per service (to S3, CloudWatch, Kinesis Firehose); CloudWatch metrics
- **Traffic management**: Weighted target groups per rule for canary deployments
- **TLS**: HTTPS listeners support ACM certificates; end-to-end encryption option
