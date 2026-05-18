<img src="stratvm-white.svg" alt="stratvm logo" width="200">

# stratvm — Event Processing Pipeline

Multi-service event processing system deployed on Kubernetes.

## Event Pipeline

└─ POST → **API** → **Redis** → **Worker** → **PostgreSQL**

└─ GET → **API** → **PostgreSQL** → **Dashboard**

## Configuration

All resources are deployed in the `stratvm` **namespace** with a **default-deny ingress** baseline — only Traefik can reach the api and dashboard, while the worker receives no ingress at all. Egress is restricted per service: api talks to redis, postgres, and kube-dns; dashboard reaches only the api; postgres and redis accept connections from no outbound traffic.

Configuration is externalized through **ConfigMaps** (service endpoints, Redis ACL, PostgreSQL init SQL) while credentials stay in **Kubernetes Secrets** referenced via `secretKeyRef`. PostgreSQL data persists on a 10Gi **hostPath PersistentVolume** with a **PVC** using Retain reclaim policy; a writable **emptyDir** backs `/tmp` for the container's **readOnlyRootFilesystem**.

Every pod runs as non-root (**runAsNonRoot**, UID/GID `65534`) with no auto-mounted service accounts. Stateless services — api (5 replicas), dashboard (5), worker (3) — each have a **PodDisruptionBudget** (minAvailable: 1) and **pod anti-affinity** (preferred, hostname) to spread across nodes. All containers declare separate **liveness** and **readiness probes** (httpGet, tcpSocket, exec) and have **cpu**, **memory**, and **ephemeral-storage** requests and limits. CI builds on every `main` push and publishes tagged images to **GHCR** with `imagePullPolicy: Always`.

## Deploy

```bash
make          # delete + apply manifests
```
