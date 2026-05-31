.PHONY: build apply restart talos-create talos-rm

all: apply restart

build:
	docker build -t api:latest ./api
	docker build -t worker:latest ./worker

apply:
	kubectl apply -f k8s

delete:
	kubectl delete -f k8s

restart:
	kubectl rollout restart -f k8s -l "app in (api,postgres,redis,worker)"

talos:
	mkdir talos

talos-create: talos
	talosctl cluster create qemu
	mv controlplane.yaml worker.yaml talos
	chown $(SUDO_USER):$(SUDO_USER) -R talos
	chown $(SUDO_USER):$(SUDO_USER) -R $(HOME)/.kube
	chown $(SUDO_USER):$(SUDO_USER) -R $(HOME)/.talos

talos-rm:
	-talosctl cluster destroy
	-rm -rf talos
	-rm -rf $(HOME)/.talos
	-rm -rf $(HOME)/.kube
