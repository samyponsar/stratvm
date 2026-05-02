REG = 127.0.0.1:5000


.PHONY: all up down rebuild

all: rebuild

up:
	docker compose up --build -d

down:
	docker compose down

build:
	docker build -t ${REG}/api:latest -f ./api/Containerfile .
	docker build -t ${REG}/worker:latest -f ./worker/Containerfile .
	docker build -t ${REG}/dashboard:latest -f ./dashboard/Containerfile .
	docker push ${REG}/api:latest
	docker push ${REG}/worker:latest
	docker push ${REG}/dashboard:latest

registry:
	docker run -d --restart=always \
	--name lan-registry \
	-p 0.0.0.0:5000:5000 \
	registry:3