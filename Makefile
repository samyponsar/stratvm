.PHONY: k8s-build k8s-import k8s-apply k8s

k8s-build:
	docker buildx build -o type=oci,dest=api.tar -t api:latest -f ./api/Containerfile . && \
	docker buildx build -o type=oci,dest=worker.tar -t worker:latest -f ./worker/Containerfile . && \
	docker buildx build -o type=oci,dest=dashboard.tar -t dashboard:latest -f ./dashboard/Containerfile .

k8s-import:
	k3s ctr -n k8s.io image import api.tar
	k3s ctr -n k8s.io image import worker.tar 
	k3s ctr -n k8s.io image import dashboard.tar

k8s-apply:
	kubectl apply -f ./k8s/

k8s: k8s-build k8s-import k8s-apply

