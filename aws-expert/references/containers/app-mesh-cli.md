# AWS App Mesh — CLI Reference
For service concepts, see [app-mesh-capabilities.md](app-mesh-capabilities.md).

> **Note**: AWS App Mesh reaches end of support on September 30, 2026. For new workloads, use ECS Service Connect or a Kubernetes-native service mesh.

```bash
# --- Mesh ---
aws appmesh create-mesh \
  --mesh-name my-mesh \
  --spec '{"egressFilter": {"type": "DROP_ALL"}}'
  # egressFilter: ALLOW_ALL (default) or DROP_ALL (only routed traffic exits)

aws appmesh list-meshes

aws appmesh describe-mesh --mesh-name my-mesh

aws appmesh update-mesh \
  --mesh-name my-mesh \
  --spec '{"egressFilter": {"type": "ALLOW_ALL"}}'

# --- Virtual Nodes ---
# Virtual node with Cloud Map service discovery
aws appmesh create-virtual-node \
  --mesh-name my-mesh \
  --virtual-node-name serviceA-vn \
  --spec '{
    "listeners": [{"portMapping": {"port": 8080, "protocol": "http"}, "healthCheck": {"protocol": "http", "path": "/health", "healthyThreshold": 2, "unhealthyThreshold": 3, "timeoutMillis": 2000, "intervalMillis": 5000}}],
    "serviceDiscovery": {
      "awsCloudMap": {
        "namespaceName": "my-namespace",
        "serviceName": "serviceA"
      }
    },
    "backends": [
      {"virtualService": {"virtualServiceName": "serviceB.my-mesh.local"}}
    ],
    "logging": {
      "accessLog": {"file": {"path": "/dev/stdout"}}
    }
  }'

aws appmesh list-virtual-nodes --mesh-name my-mesh

aws appmesh describe-virtual-node \
  --mesh-name my-mesh \
  --virtual-node-name serviceA-vn

aws appmesh update-virtual-node \
  --mesh-name my-mesh \
  --virtual-node-name serviceA-vn \
  --spec file://updated-vn-spec.json

aws appmesh delete-virtual-node \
  --mesh-name my-mesh \
  --virtual-node-name serviceA-vn

# --- Virtual Routers ---
aws appmesh create-virtual-router \
  --mesh-name my-mesh \
  --virtual-router-name serviceB-vr \
  --spec '{"listeners": [{"portMapping": {"port": 8080, "protocol": "http"}}]}'

aws appmesh list-virtual-routers --mesh-name my-mesh
aws appmesh describe-virtual-router --mesh-name my-mesh --virtual-router-name serviceB-vr

aws appmesh delete-virtual-router \
  --mesh-name my-mesh \
  --virtual-router-name serviceB-vr

# --- Routes ---
# Weighted route (canary: 10% to v2, 90% to v1)
aws appmesh create-route \
  --mesh-name my-mesh \
  --virtual-router-name serviceB-vr \
  --route-name serviceB-route \
  --spec '{
    "httpRoute": {
      "match": {"prefix": "/"},
      "action": {
        "weightedTargets": [
          {"virtualNode": "serviceB-v1-vn", "weight": 90},
          {"virtualNode": "serviceB-v2-vn", "weight": 10}
        ]
      },
      "retryPolicy": {
        "httpRetryEvents": ["server-error", "gateway-error"],
        "tcpRetryEvents": ["connection-error"],
        "maxRetries": 3,
        "perRetryTimeout": {"unit": "ms", "value": 2000}
      },
      "timeout": {
        "perRequest": {"unit": "s", "value": 30},
        "idle": {"unit": "s", "value": 300}
      }
    }
  }'

aws appmesh list-routes \
  --mesh-name my-mesh \
  --virtual-router-name serviceB-vr

aws appmesh describe-route \
  --mesh-name my-mesh \
  --virtual-router-name serviceB-vr \
  --route-name serviceB-route

# Shift 100% to v2 after validation
aws appmesh update-route \
  --mesh-name my-mesh \
  --virtual-router-name serviceB-vr \
  --route-name serviceB-route \
  --spec '{
    "httpRoute": {
      "match": {"prefix": "/"},
      "action": {
        "weightedTargets": [
          {"virtualNode": "serviceB-v2-vn", "weight": 100}
        ]
      }
    }
  }'

aws appmesh delete-route \
  --mesh-name my-mesh \
  --virtual-router-name serviceB-vr \
  --route-name serviceB-route

# --- Virtual Services ---
aws appmesh create-virtual-service \
  --mesh-name my-mesh \
  --virtual-service-name serviceB.my-mesh.local \
  --spec '{
    "provider": {
      "virtualRouter": {"virtualRouterName": "serviceB-vr"}
    }
  }'

# Virtual service backed directly by a virtual node (no routing)
aws appmesh create-virtual-service \
  --mesh-name my-mesh \
  --virtual-service-name serviceC.my-mesh.local \
  --spec '{
    "provider": {
      "virtualNode": {"virtualNodeName": "serviceC-vn"}
    }
  }'

aws appmesh list-virtual-services --mesh-name my-mesh

aws appmesh describe-virtual-service \
  --mesh-name my-mesh \
  --virtual-service-name serviceB.my-mesh.local

aws appmesh update-virtual-service \
  --mesh-name my-mesh \
  --virtual-service-name serviceB.my-mesh.local \
  --spec file://updated-vs-spec.json

aws appmesh delete-virtual-service \
  --mesh-name my-mesh \
  --virtual-service-name serviceB.my-mesh.local

# --- Virtual Gateways ---
aws appmesh create-virtual-gateway \
  --mesh-name my-mesh \
  --virtual-gateway-name ingress-gw \
  --spec '{
    "listeners": [{
      "portMapping": {"port": 8080, "protocol": "http"}
    }]
  }'

aws appmesh list-virtual-gateways --mesh-name my-mesh
aws appmesh describe-virtual-gateway \
  --mesh-name my-mesh \
  --virtual-gateway-name ingress-gw

# --- Gateway Routes ---
aws appmesh create-gateway-route \
  --mesh-name my-mesh \
  --virtual-gateway-name ingress-gw \
  --gateway-route-name default-route \
  --spec '{
    "httpRoute": {
      "match": {"prefix": "/"},
      "action": {
        "target": {
          "virtualService": {"virtualServiceName": "serviceA.my-mesh.local"}
        }
      }
    }
  }'

aws appmesh list-gateway-routes \
  --mesh-name my-mesh \
  --virtual-gateway-name ingress-gw

aws appmesh describe-gateway-route \
  --mesh-name my-mesh \
  --virtual-gateway-name ingress-gw \
  --gateway-route-name default-route

aws appmesh delete-gateway-route \
  --mesh-name my-mesh \
  --virtual-gateway-name ingress-gw \
  --gateway-route-name default-route

aws appmesh delete-virtual-gateway \
  --mesh-name my-mesh \
  --virtual-gateway-name ingress-gw

# --- Tagging ---
aws appmesh tag-resource \
  --resource-arn arn:aws:appmesh:us-east-1:123456789012:mesh/my-mesh \
  --tags key=Environment,value=production

aws appmesh list-tags-for-resource \
  --resource-arn arn:aws:appmesh:us-east-1:123456789012:mesh/my-mesh

# --- Cleanup ---
# Meshes must be empty before deletion
aws appmesh delete-mesh --mesh-name my-mesh
```
