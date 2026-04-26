.PHONY: all up down rebuild clean

all: rebuild

up:
	docker compose up --build -d

down:
	docker compose down

rebuild: down up