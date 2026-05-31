FROM ghcr.io/astral-sh/uv:alpine

RUN useradd -u 1000 -s /bin/bash runner

COPY --chown=1000 app/ /app

USER 1000

WORKDIR /app

RUN uv sync

CMD ["uv", "run", "fastapi", "run", "--host", "0.0.0.0"]