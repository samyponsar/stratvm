.PHONY: build apply restart

all: build apply restart

build:
	docker build -t api:latest ./api
	docker build -t worker:latest ./worker

apply:
	kubectl apply -f k8s

restart:
	kubectl rollout restart -f k8s -l "app in (api,postgres,redis,worker)"
