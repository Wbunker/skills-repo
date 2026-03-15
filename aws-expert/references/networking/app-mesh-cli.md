# AWS App Mesh — CLI Reference
For service concepts, see [app-mesh-capabilities.md](app-mesh-capabilities.md).

> **Note**: App Mesh does not have a dedicated CLI service prefix. Management of App Mesh resources is done through the AWS Management Console, AWS CloudFormation, or the AWS SDKs. The `aws appmesh` CLI commands cover mesh, virtual node, virtual router, virtual service, virtual gateway, and route management.

```bash
# --- Mesh ---
aws appmesh create-mesh --mesh-name my-mesh

aws appmesh list-meshes
aws appmesh describe-mesh --mesh-name my-mesh
aws appmesh delete-mesh --mesh-name my-mesh

# --- Virtual Nodes ---
aws appmesh create-virtual-node \
  --mesh-name my-mesh \
  --virtual-node-name my-service-node \
  --spec '{
    "listeners": [{
      "portMapping": {"port": 8080, "protocol": "http"}
    }],
    "serviceDiscovery": {
      "awsCloudMap": {
        "namespaceName": "my-namespace",
        "serviceName": "my-service"
      }
    },
    "logging": {
      "accessLog": {
        "file": {"path": "/dev/stdout"}
      }
    }
  }'

aws appmesh list-virtual-nodes --mesh-name my-mesh
aws appmesh describe-virtual-node --mesh-name my-mesh --virtual-node-name my-service-node
aws appmesh delete-virtual-node --mesh-name my-mesh --virtual-node-name my-service-node

# --- Virtual Routers ---
aws appmesh create-virtual-router \
  --mesh-name my-mesh \
  --virtual-router-name my-router \
  --spec '{
    "listeners": [{
      "portMapping": {"port": 8080, "protocol": "http"}
    }]
  }'

aws appmesh list-virtual-routers --mesh-name my-mesh
aws appmesh describe-virtual-router --mesh-name my-mesh --virtual-router-name my-router
aws appmesh delete-virtual-router --mesh-name my-mesh --virtual-router-name my-router

# --- Routes ---
# HTTP route with weighted targets (canary/blue-green)
aws appmesh create-route \
  --mesh-name my-mesh \
  --virtual-router-name my-router \
  --route-name my-http-route \
  --spec '{
    "httpRoute": {
      "match": {"prefix": "/"},
      "action": {
        "weightedTargets": [
          {"virtualNode": "my-service-v1", "weight": 90},
          {"virtualNode": "my-service-v2", "weight": 10}
        ]
      },
      "retryPolicy": {
        "httpRetryEvents": ["server-error", "gateway-error"],
        "maxRetries": 3,
        "perRetryTimeout": {"value": 5, "unit": "s"}
      }
    }
  }'

aws appmesh list-routes --mesh-name my-mesh --virtual-router-name my-router
aws appmesh describe-route \
  --mesh-name my-mesh \
  --virtual-router-name my-router \
  --route-name my-http-route

aws appmesh update-route \
  --mesh-name my-mesh \
  --virtual-router-name my-router \
  --route-name my-http-route \
  --spec file://updated-route-spec.json

aws appmesh delete-route \
  --mesh-name my-mesh \
  --virtual-router-name my-router \
  --route-name my-http-route

# --- Virtual Services ---
aws appmesh create-virtual-service \
  --mesh-name my-mesh \
  --virtual-service-name my-service.my-namespace.svc.cluster.local \
  --spec '{
    "provider": {
      "virtualRouter": {"virtualRouterName": "my-router"}
    }
  }'

# Virtual service backed directly by a virtual node (no routing)
aws appmesh create-virtual-service \
  --mesh-name my-mesh \
  --virtual-service-name simple-service.my-namespace.svc.cluster.local \
  --spec '{
    "provider": {
      "virtualNode": {"virtualNodeName": "my-service-node"}
    }
  }'

aws appmesh list-virtual-services --mesh-name my-mesh
aws appmesh describe-virtual-service \
  --mesh-name my-mesh \
  --virtual-service-name my-service.my-namespace.svc.cluster.local
aws appmesh delete-virtual-service \
  --mesh-name my-mesh \
  --virtual-service-name my-service.my-namespace.svc.cluster.local

# --- Virtual Gateways ---
aws appmesh create-virtual-gateway \
  --mesh-name my-mesh \
  --virtual-gateway-name my-ingress-gw \
  --spec '{
    "listeners": [{
      "portMapping": {"port": 8080, "protocol": "http"}
    }]
  }'

aws appmesh list-virtual-gateways --mesh-name my-mesh
aws appmesh describe-virtual-gateway \
  --mesh-name my-mesh \
  --virtual-gateway-name my-ingress-gw

# --- Gateway Routes ---
aws appmesh create-gateway-route \
  --mesh-name my-mesh \
  --virtual-gateway-name my-ingress-gw \
  --gateway-route-name my-gw-route \
  --spec '{
    "httpRoute": {
      "match": {"prefix": "/"},
      "action": {
        "target": {
          "virtualService": {"virtualServiceName": "my-service.my-namespace.svc.cluster.local"}
        }
      }
    }
  }'

aws appmesh list-gateway-routes \
  --mesh-name my-mesh \
  --virtual-gateway-name my-ingress-gw

aws appmesh delete-gateway-route \
  --mesh-name my-mesh \
  --virtual-gateway-name my-ingress-gw \
  --gateway-route-name my-gw-route
```
