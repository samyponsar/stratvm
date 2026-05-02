.PHONY: k8s-build k8s-apply k8s-delete k8s-serve k8s

k8s-build:
	eval $$(minikube docker-env) && \
	docker build -t api:latest -f ./api/Containerfile . && \
	docker build -t worker:latest -f ./worker/Containerfile . && \
	docker build -t dashboard:latest -f ./dashboard/Containerfile .

k8s-apply:
	kubectl apply -f ./k8s/

k8s-delete:
	kubectl delete -f ./k8s/ --ignore-not-found

k8s-serve:
	minikube service dashboard-service -n default

k8s: k8s-build k8s-apply k8s-serve

