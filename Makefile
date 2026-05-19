.PHONY: delete apply

all: delete apply

apply:
	-kubectl create ns stratvm
	kubectl -n stratvm apply -f ./k8s/

delete:
	-kubectl -n stratvm delete -f ./k8s/
