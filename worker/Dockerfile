FROM ghcr.io/astral-sh/uv:alpine

RUN adduser -u 1000 -D runner runner

COPY --chown=1000 app/ /app

USER 1000

WORKDIR /app

RUN uv sync

CMD ["uv", "run", "main.py"]