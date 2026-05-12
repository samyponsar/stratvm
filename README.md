<img src="stratvm-white.svg" alt="stratvm logo" width="200">

# stratvm — CKA-Ready Kubernetes Lab

An event processing pipeline created in order to practice every domain of the **Certified Kubernetes Administrator (CKA)** exam.

## Running the cluster

### Prerequisite

A running Kubernetes cluster.

### Run

```bash
make 
```

## Event Pipeline

└─ POST → **API** → **Redis** → **Worker** → **PostgreSQL**

└─ GET → **API** → **PostgreSQL** → **Dashboard**
