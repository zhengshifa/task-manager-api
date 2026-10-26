# Kubernetes Deployment (Minikube)

Deploy Task Manager API to a local Minikube cluster.

## Prerequisites

- Minikube >= v1.30
- kubectl
- Docker

## Steps

### 1. Start Minikube

```bash
minikube start
# Install Envoy Gateway (once per cluster)
helm install eg oci://docker.io/envoyproxy/gateway-helm \
  --version v1.2.6 \
  -n envoy-gateway-system --create-namespace
```

### 2. Build image into Minikube

```bash
# From repository root
eval $(minikube docker-env)   # Linux/macOS
# On Windows PowerShell:
# & minikube -p minikube docker-env --shell powershell | Invoke-Expression

docker build -t task-manager-api:local .
```

### 3. Apply manifests

```bash
kubectl apply -f k8s/
```

### 4. Verify Pods

```bash
kubectl get pods -n task-manager
kubectl get all -n task-manager
kubectl get gatewayclass,gateway,httproute -n task-manager
```

All Pods should be `Running` and ready (`2/2` replicas). Gateway/HTTPRoute should show `Accepted=True`.

### 5. Configure local DNS

Add host mapping so `task-manager.local` resolves to the Envoy Gateway Service:

```bash
kubectl get svc -n envoy-gateway-system
# or, if the Gateway Service is in task-manager:
kubectl get svc -n task-manager -l gateway.envoyproxy.io/owning-gateway-name=task-manager-api
```

Then edit `/etc/hosts` (Linux/macOS) or `C:\Windows\System32\drivers\etc\hosts` (Windows):

```text
<GATEWAY_EXTERNAL_IP_OR_NODE_IP> task-manager.local
```

On Minikube without an external LoadBalancer, use port-forward:

```bash
export ENVOY_SERVICE=$(kubectl get svc -n envoy-gateway-system \
  -l gateway.envoyproxy.io/owning-gateway-namespace=task-manager \
  -o jsonpath='{.items[0].metadata.name}')
kubectl -n envoy-gateway-system port-forward svc/${ENVOY_SERVICE} 8888:80
```

### 6. Test the API

```bash
# via hosts mapping
curl http://task-manager.local/health
curl http://task-manager.local/tasks

# or via port-forward
curl -H "Host: task-manager.local" http://127.0.0.1:8888/health

curl -X POST http://task-manager.local/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"demo","description":"from minikube","status":"todo"}'
```

### 7. Cleanup

```bash
kubectl delete -f k8s/
minikube stop
```

## Notes

- Deployment uses image `task-manager-api:local` with `imagePullPolicy: IfNotPresent`, so the image must exist in the Minikube Docker daemon.
- Liveness and readiness probes hit `/health`.
- Non-sensitive settings (`LOG_LEVEL`, `PORT`) come from `ConfigMap`.
