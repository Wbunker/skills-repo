# eBPF for Networking

Reference for XDP, TC, packet parsing, load balancing, Kubernetes networking, and iptables replacement.

## Table of Contents
- [XDP (eXpress Data Path)](#xdp-express-data-path)
- [Packet Parsing](#packet-parsing)
- [XDP Load Balancing](#xdp-load-balancing)
- [XDP Offloading](#xdp-offloading)
- [TC (Traffic Control)](#tc-traffic-control)
- [Packet Encryption and Decapsulation](#packet-encryption-and-decapsulation)
- [Kubernetes Networking with eBPF](#kubernetes-networking-with-ebpf)

## XDP (eXpress Data Path)

### XDP Position in Network Stack
```
Packet arrives at NIC
        │
        ▼
   ┌─────────┐
   │   XDP   │ ← earliest possible hook (before sk_buff allocation)
   └────┬────┘
        │ XDP_PASS
        ▼
   sk_buff allocation
        │
        ▼
   ┌─────────┐
   │ TC ingr │ ← traffic control (after sk_buff)
   └────┬────┘
        │
        ▼
   Network stack (iptables, routing, etc.)
        │
        ▼
   ┌─────────┐
   │ TC egr  │ ← traffic control egress
   └────┬────┘
        │
        ▼
   NIC transmit
```

### XDP Return Codes
| Return Code | Action |
|------------|--------|
| `XDP_PASS` | Continue to normal network stack processing |
| `XDP_DROP` | Drop the packet (highest performance) |
| `XDP_TX` | Transmit back out the same interface |
| `XDP_REDIRECT` | Redirect to another interface, CPU, or socket |
| `XDP_ABORTED` | Error — drop and trigger tracepoint for debugging |

### XDP Attach Modes
```bash
# Generic mode (any NIC, slower — uses kernel sk_buff path)
ip link set dev eth0 xdpgeneric obj prog.bpf.o sec xdp

# Native/driver mode (NIC driver support required, faster)
ip link set dev eth0 xdp obj prog.bpf.o sec xdp

# Offloaded mode (runs on NIC hardware, fastest)
ip link set dev eth0 xdpoffload obj prog.bpf.o sec xdp

# Detach
ip link set dev eth0 xdp off

# Check attached programs
ip link show dev eth0
```

### Minimal XDP Program
```c
#include "vmlinux.h"
#include <bpf/bpf_helpers.h>

SEC("xdp")
int xdp_drop_all(struct xdp_md *ctx) {
    return XDP_DROP;  // drop everything
}

char LICENSE[] SEC("license") = "GPL";
```

## Packet Parsing

### Ethernet Header Parsing
```c
SEC("xdp")
int xdp_parse(struct xdp_md *ctx) {
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;

    // Layer 2: Ethernet
    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end)
        return XDP_PASS;

    // Check protocol
    if (eth->h_proto != bpf_htons(ETH_P_IP))
        return XDP_PASS;  // not IPv4

    // Layer 3: IP
    struct iphdr *ip = (void *)(eth + 1);
    if ((void *)(ip + 1) > data_end)
        return XDP_PASS;

    // Check for TCP
    if (ip->protocol != IPPROTO_TCP)
        return XDP_PASS;

    // Layer 4: TCP
    struct tcphdr *tcp = (void *)ip + (ip->ihl * 4);
    if ((void *)(tcp + 1) > data_end)
        return XDP_PASS;

    // Now we can inspect tcp->dest, tcp->source, etc.
    if (tcp->dest == bpf_htons(8080))
        return XDP_DROP;  // block port 8080

    return XDP_PASS;
}
```

### Verifier-Safe Parsing Pattern
```c
// Always follow this pattern for packet access:
// 1. Get data and data_end pointers
// 2. Cast data to header struct pointer
// 3. Bounds check: if (ptr + size > data_end) return;
// 4. Only then access header fields
// 5. Advance pointer for next layer

// Common mistake: accessing variable-length IP header
struct iphdr *ip = data + sizeof(struct ethhdr);
if ((void *)(ip + 1) > data_end) return XDP_PASS;

// ihl is the header length in 32-bit words (minimum 5 = 20 bytes)
int ip_hdr_len = ip->ihl * 4;
if (ip_hdr_len < sizeof(struct iphdr)) return XDP_PASS;
if ((void *)ip + ip_hdr_len > data_end) return XDP_PASS;

// Now safe to access L4 header at (void *)ip + ip_hdr_len
```

## XDP Load Balancing

### Simple Hash-Based Load Balancer
```c
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 4);
    __type(key, __u32);
    __type(value, __u32);  // backend IP in network byte order
} backends SEC(".maps");

SEC("xdp")
int xdp_lb(struct xdp_md *ctx) {
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;

    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end) return XDP_PASS;
    if (eth->h_proto != bpf_htons(ETH_P_IP)) return XDP_PASS;

    struct iphdr *ip = (void *)(eth + 1);
    if ((void *)(ip + 1) > data_end) return XDP_PASS;

    // Hash source IP to pick backend
    __u32 idx = ip->saddr % 4;
    __u32 *backend_ip = bpf_map_lookup_elem(&backends, &idx);
    if (!backend_ip) return XDP_PASS;

    // Rewrite destination IP
    ip->daddr = *backend_ip;

    // Recompute IP checksum (simplified — real code uses incremental)
    ip->check = 0;
    ip->check = compute_ip_csum(ip);

    return XDP_TX;  // send back out same interface
}
```

### XDP Redirect (to another interface)
```c
// Redirect map for interface forwarding
struct {
    __uint(type, BPF_MAP_TYPE_DEVMAP);
    __uint(max_entries, 64);
    __type(key, __u32);
    __type(value, __u32);  // ifindex of target interface
} tx_port SEC(".maps");

SEC("xdp")
int xdp_redirect(struct xdp_md *ctx) {
    __u32 port = 0;  // map index
    return bpf_redirect_map(&tx_port, port, 0);
}
```

## XDP Offloading

### Hardware Offload
```
Software XDP (generic):  ~1-5 Mpps
Driver XDP (native):     ~10-25 Mpps
Hardware XDP (offload):  ~50-100+ Mpps (NIC line rate)
```

- Hardware offload runs the eBPF program on the NIC's processor
- Supported by Netronome (Agilio) and some Mellanox NICs
- Limited instruction set and map types
- Packets never reach the CPU for dropped/redirected packets

## TC (Traffic Control)

### TC vs XDP
| Feature | XDP | TC |
|---------|-----|----|
| Position | Before sk_buff | After sk_buff |
| Direction | Ingress only | Ingress and egress |
| Context | `struct xdp_md *` | `struct __sk_buff *` |
| Packet modification | Limited (raw bytes) | Rich (sk_buff helpers) |
| Performance | Highest | High |
| Socket info | No | Yes (via `skb->sk`) |

### TC Program
```c
SEC("tc")
int tc_ingress(struct __sk_buff *skb) {
    void *data = (void *)(long)skb->data;
    void *data_end = (void *)(long)skb->data_end;

    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end)
        return TC_ACT_OK;

    // TC has richer context than XDP
    __u32 ifindex = skb->ifindex;
    __u32 len = skb->len;
    __u32 protocol = skb->protocol;

    // Can modify packet bytes
    // bpf_skb_store_bytes(skb, offset, &new_data, len, flags);

    // Can adjust headers
    // bpf_skb_change_head(skb, delta, flags);
    // bpf_skb_change_tail(skb, new_len, flags);

    return TC_ACT_OK;
}
```

### TC Direct-Action Mode
```bash
# Modern approach: direct-action (da) mode
# Program returns TC_ACT_* directly, no separate action needed
tc filter add dev eth0 ingress bpf da obj prog.bpf.o sec tc
```

## Packet Encryption and Decapsulation

### VXLAN/Geneve Decapsulation
```c
// Strip outer encapsulation headers at XDP layer
SEC("xdp")
int decap(struct xdp_md *ctx) {
    // Parse outer Ethernet + IP + UDP + VXLAN headers
    int outer_hdr_size = sizeof(struct ethhdr) +
                         sizeof(struct iphdr) +
                         sizeof(struct udphdr) +
                         sizeof(struct vxlanhdr);

    // Remove outer headers
    if (bpf_xdp_adjust_head(ctx, outer_hdr_size))
        return XDP_DROP;

    return XDP_PASS;  // inner packet continues to stack
}
```

### IPsec/WireGuard Acceleration
- eBPF can accelerate packet classification for encrypted tunnels
- Fast path selection: determine tunnel/route before crypto
- Post-decryption policy enforcement

## Kubernetes Networking with eBPF

### Traditional Kubernetes Networking
```
Pod A → veth → bridge → iptables → routing → bridge → veth → Pod B
         ↑                ↑                          ↑
    many copies    O(n) rules            many copies
```

### eBPF-Based Kubernetes Networking (Cilium)
```
Pod A → veth → eBPF (TC/XDP) → veth → Pod B
         ↑          ↑                    ↑
     single     O(1) lookup          single
      copy      (BPF map)            copy
```

### Why eBPF Replaces iptables
| Aspect | iptables | eBPF |
|--------|----------|------|
| Rule lookup | O(n) linear scan | O(1) hash map lookup |
| Rule count impact | Degrades linearly | Constant time |
| Programmability | Fixed match/action | Arbitrary logic |
| Visibility | Limited counters | Full observability |
| Update | Full chain rebuild | Atomic map update |
| Connection tracking | conntrack module | BPF CT map |

### Cilium Architecture
```
┌──────────────────────────────┐
│         Cilium Agent         │  (user space: policy, maps)
└────────────┬─────────────────┘
             │ loads/manages
     ┌───────┴───────┐
     │  eBPF Programs │
     ├───────────────┤
     │ XDP (ingress) │ → early packet drop / LB
     │ TC (ingress)  │ → identity-based policy
     │ TC (egress)   │ → egress policy
     │ Socket ops    │ → socket-level acceleration
     │ Sockmap       │ → pod-to-pod shortcut
     └───────────────┘
```

### Service Load Balancing
```
Without eBPF:
  Pod → iptables DNAT (kube-proxy) → random backend selection
  (iptables rules scale O(n) with services × endpoints)

With eBPF (Cilium):
  Pod → eBPF (TC hook) → BPF map lookup → direct redirect to backend
  (O(1) regardless of number of services/endpoints)
```

### Network Policy Enforcement
```c
// Cilium-style identity-based policy (conceptual)
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 65536);
    __type(key, struct policy_key);    // {src_identity, dst_identity, port, proto}
    __type(value, struct policy_entry); // {allow, deny, audit}
} policy_map SEC(".maps");

SEC("tc")
int enforce_policy(struct __sk_buff *skb) {
    struct policy_key key = {
        .src_id = get_identity(skb),
        .dst_id = get_dst_identity(skb),
        .port = get_dst_port(skb),
        .proto = get_protocol(skb),
    };

    struct policy_entry *entry = bpf_map_lookup_elem(&policy_map, &key);
    if (!entry || !entry->allow)
        return TC_ACT_SHOT;  // drop

    return TC_ACT_OK;
}
```

### Socket-Level Acceleration
```
Normal path:     Pod A → TC → routing → TC → Pod B  (traverse full stack)
Sockmap shortcut: Pod A → socket redirect → Pod B   (bypass stack entirely)

// bpf_msg_redirect_hash / bpf_sk_redirect_hash
// Used for same-node pod-to-pod communication
// Eliminates IP processing for local traffic
```
