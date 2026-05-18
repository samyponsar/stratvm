<img src="stratvm-white.svg" alt="stratvm logo" width="200">

# stratvm — CKA-Ready Kubernetes Lab

An event processing pipeline running entirely on Kubernetes. Built to practice every domain of the **Certified Kubernetes Administrator (CKA)** exam.

## Event Pipeline

└─ POST → **API** → **Redis** → **Worker** → **PostgreSQL**

└─ GET → **API** → **PostgreSQL** → **Dashboard**

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.14 |
| API | FastAPI |
| Queue | Redis 8 (with ACL-based auth per service) |
| Database | PostgreSQL 18 (JSONB columns for extensibility) |
| Frontend | Nginx Alpine (static HTML/JS) |
| Orchestration | Kubernetes (k3s) |
| Ingress | Traefik |
| CI/CD | GitHub Actions |
| Container Registry | GHCR |
| Image Build | Docker Buildx, multi-context builds |

## Kubernetes Features Used

- **Secrets & ConfigMaps** for all configuration (DB credentials, Redis ACL, service endpoints)
- **NetworkPolicies** — default-deny ingress per namespace, explicit allow rules per service (ingress/egress)
- **PersistentVolumes & PVCs** with `hostPath` for PostgreSQL data retention
- **Init scripts** via ConfigMap-mounted SQL for automatic DB schema creation
- **Health probes** — `/livez` for liveness, `/readyz` for readiness (checks Redis and PostgreSQL connectivity)
- **imagePullPolicy: Always** with tagged images from GHCR
- **Service accounts** disabled per pod (`automountServiceAccountToken: false`)

## Quickstart

Images are built by the CI pipeline on push to `main` and pushed to GHCR. To deploy locally:

```bash
make
```

This runs:
1. `kubectl delete -f ./k8s/` — remove existing resources
2. `kubectl apply -f ./k8s/` — apply all manifests
3. Requires kubectl configured to talk to your cluster (k3s, kind, etc.)

To build and import images manually:

```bash
make build-local import-local apply
```

## CI/CD

The GitHub Actions workflow at `.github/workflows/build.yml`:
- Triggers on push to `main`
- Builds `api`, `worker`, and `dashboard` images using Docker Buildx
- Pushes to `ghcr.io/samyponsar/` with `latest` and git SHA tags
- Tagged releases get the version tag (e.g. `v1.0.0`)
