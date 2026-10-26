# Task Manager API

[![CI](https://github.com/zhengshifa/task-manager-api/actions/workflows/ci.yml/badge.svg)](https://github.com/zhengshifa/task-manager-api/actions/workflows/ci.yml)

A containerized RESTful Task Manager service with Minikube deployment and GitHub Actions CI/CD.

## Features

- CRUD APIs for tasks (`todo` / `in_progress` / `done`)
- Health check endpoint
- In-memory storage (easy to swap for a database later)
- Request logging, input validation, and error handling
- OpenAPI / Swagger UI at `/docs`
- Rate limiting (100 requests / minute / IP)
- Multi-stage Docker image (non-root)
- Kubernetes manifests for Minikube
- GitHub Actions: Lint → Test → Build → Trivy → Push (Aliyun ACR)

## Tech Stack

| Tool | Purpose | Version |
|------|---------|---------|
| Python + FastAPI | API server | Python 3.11+ |
| Docker | Containerization | >= 24.0 |
| Minikube | Local Kubernetes | >= v1.30 |
| GitHub Actions | CI/CD | `ubuntu-latest` |
| Git | Version control | >= 2.30 |

## Project Structure

```text
task-manager-api/
├── .github/workflows/ci.yml
├── k8s/
├── src/
│   ├── app.py
│   ├── models/
│   ├── routes/
│   └── storage.py
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## API Endpoints

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| GET | `/health` | Health check | 200 |
| GET | `/tasks` | List tasks | 200 |
| GET | `/tasks?status=todo\|in_progress\|done` | List tasks filtered by status | 200 / 400 |
| GET | `/tasks/{id}` | Get task | 200 / 404 |
| POST | `/tasks` | Create task | 201 / 400 |
| PUT | `/tasks/{id}` | Update task | 200 / 404 |
| DELETE | `/tasks/{id}` | Delete task | 204 / 404 |

### Task model

```json
{
  "id": "uuid-string",
  "title": "任务标题",
  "description": "任务描述",
  "status": "todo | in_progress | done",
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

Interactive docs: `http://localhost:8080/docs`

## Local Development

```bash
# Create virtualenv
python3.11 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1

# Install dependencies (runtime + test/lint)
pip install -r requirements-dev.txt

# Run API (default port 8080)
python -m src.app
# or
uvicorn src.app:app --host 0.0.0.0 --port 8080

# Run tests (coverage gate > 60%)
pytest

# Lint
pylint src --fail-under=7.0
```

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8080` | Listen port |
| `HOST` | `0.0.0.0` | Bind address |
| `LOG_LEVEL` | `INFO` | Logging level |

### Example requests

```bash
curl http://localhost:8080/health

curl -X POST http://localhost:8080/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn Kubernetes","description":"Deploy to Minikube","status":"todo"}'

curl http://localhost:8080/tasks
curl 'http://localhost:8080/tasks?status=todo'
```

## Docker

```bash
docker build -t task-manager-api .
docker run -p 8080:8080 task-manager-api
curl http://localhost:8080/health
```

Optional Compose:

```bash
docker compose up --build
```

## Minikube Deployment

See [k8s/README.md](k8s/README.md) for full steps.

Quick path:

```bash
minikube start
# Install Envoy Gateway once, then:
eval $(minikube docker-env)
docker build -t task-manager-api:local .
kubectl apply -f k8s/
kubectl get pods,gateway,httproute -n task-manager
```

Map `task-manager.local` to the Envoy Gateway address (see [k8s/README.md](k8s/README.md)), then:

```bash
curl http://task-manager.local/health
curl http://task-manager.local/tasks
```


## CI/CD

### Pipeline — CI then Push

```text
Lint → Test → Build → Security Scan → Push (Aliyun)
```

- **`.github/workflows/ci.yml`**：质量门禁；仅在 push 到 `main` 且前面全部成功后，才调用 push  
- **`.github/workflows/push.yml`**：可复用推送工作流；也可手动 `workflow_dispatch`  
- **PR**：只跑到 Security Scan，不推镜像  

镜像地址：

`{ALIYUN_REGISTRY}/{ALIYUN_NAME_SPACE}/task-manager-api:{YYYYMMDDHHMMSS}_{arch}`

Platforms 来自仓库根目录 `platforms` 文件。

Required GitHub Secrets:

| Secret | Example |
|--------|---------|
| `ALIYUN_REGISTRY` | `registry.cn-hangzhou.aliyuncs.com` |
| `ALIYUN_NAME_SPACE` | `your-namespace` |
| `ALIYUN_REGISTRY_USER` | ACR username |
| `ALIYUN_REGISTRY_PASSWORD` | ACR password / token |

## Git Workflow

This repository follows a lightweight trunk-based workflow:

- `main` – stable, deployable branch
- `feature/*` – short-lived feature branches
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/)

## Screenshots (recommended for submission)

After deploying locally, capture:

1. `kubectl get all -n task-manager`
2. Successful `curl` responses for `/health` and `/tasks`

## License

MIT
