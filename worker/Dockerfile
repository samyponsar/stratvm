FROM ghcr.io/astral-sh/uv:alpine

WORKDIR /app

COPY shared/ ./shared/
COPY worker/ ./

CMD ["uv", "run", "main.py"]
