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
minikube addons enable ingress
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
kubectl describe ingress -n task-manager
```

All Pods should be `Running` and ready (`2/2` replicas).

### 5. Configure local DNS

Add host mapping so `task-manager.local` resolves to the Minikube IP:

```bash
minikube ip
```

Then edit `/etc/hosts` (Linux/macOS) or `C:\Windows\System32\drivers\etc\hosts` (Windows):

```text
<MINIKUBE_IP> task-manager.local
```

### 6. Test the API

```bash
curl http://task-manager.local/health
curl http://task-manager.local/tasks

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
