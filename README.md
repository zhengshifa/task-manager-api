# Task Manager API

[![CI](https://github.com/OWNER/task-manager-api/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/task-manager-api/actions/workflows/ci.yml)

A containerized RESTful Task Manager service with Minikube deployment and GitHub Actions CI/CD.

> Replace `OWNER` in the badge URL with your GitHub username after creating the public repository.

## Features

- CRUD APIs for tasks (`todo` / `in_progress` / `done`)
- Health check endpoint
- In-memory storage (easy to swap for a database later)
- Request logging, input validation, and error handling
- OpenAPI / Swagger UI at `/docs`
- Rate limiting (100 requests / minute / IP)
- Multi-stage Docker image (non-root)
- Kubernetes manifests for Minikube
- GitHub Actions: Lint → Test → Build → Trivy scan

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
minikube addons enable ingress
eval $(minikube docker-env)
docker build -t task-manager-api:local .
kubectl apply -f k8s/
kubectl get pods -n task-manager
```

Map `task-manager.local` to `$(minikube ip)` in your hosts file, then:

```bash
curl http://task-manager.local/health
curl http://task-manager.local/tasks
```

## CI/CD

Workflow: `.github/workflows/ci.yml`

Triggers:

- Push to `main`
- Pull request to `main`

Pipeline stages (fail-fast):

1. **Lint** – pylint
2. **Test** – pytest + coverage
3. **Build** – Docker image tagged `ghcr.io/<username>/task-manager-api:<sha>`
4. **Security Scan** – Trivy (CRITICAL/HIGH)

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
