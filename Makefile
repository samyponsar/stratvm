.PHONY: delete build import apply clean push-events

all: delete build import clean apply forward

build:
	docker buildx build -o type=oci,dest=api.tar -t api:latest -f ./api/Containerfile . && \
	docker buildx build -o type=oci,dest=worker.tar -t worker:latest -f ./worker/Containerfile . && \
	docker buildx build -o type=oci,dest=dashboard.tar -t dashboard:latest -f ./dashboard/Containerfile .

import:
	k3s ctr -n k8s.io image import api.tar
	k3s ctr -n k8s.io image import worker.tar 
	k3s ctr -n k8s.io image import dashboard.tar

clean:
	rm -f *.tar


apply:
	-kubectl create ns stratvm
	kubectl -n stratvm apply -f ./k8s/

delete:
	-kubectl -n stratvm delete -f ./k8s/
	
forward:
	kubectl port-forward svc/traefik -n kube-system 8080:80
