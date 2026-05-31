FROM ghcr.io/astral-sh/uv:alpine

COPY app/ /app

WORKDIR /app

RUN uv sync

CMD ["uv", "run", "fastapi", "run", "--host", "0.0.0.0"]
