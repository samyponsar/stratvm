.PHONY: all up down rebuild clean

all: rebuild

up: clean
	docker compose up --build -d

down:
	docker compose down

rebuild: down up

clean:
	find . -type d \( -name '__pycache__' -o -name '.pytest_cache' -o -name '.ruff_cache' -o -name '.venv' \) -exec rm -rf {} +