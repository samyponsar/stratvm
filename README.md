<img src="stratvm-white.svg" alt="stratvm logo" width="200">

# stratvm — CKA-Ready Kubernetes Lab

A hands-on Kubernetes training environment for practicing every domain of the **Certified Kubernetes Administrator (CKA)** exam, from cluster provisioning with kubeadm to observability and troubleshooting.

## Running the cluster

### Prerequisite

minikube

### Run

```bash
make k8s
```

## Event Pipeline

└─ POST → **API** → **Redis** → **Worker** → **PostgreSQL**

└─ GET → **API** → **PostgreSQL** → **Dashboard**
