FROM ghcr.io/astral-sh/uv:alpine

RUN useradd -u 1000 -s /bin/bash runner

COPY app/ /app --chown runner:runner

USER runner

WORKDIR /app

RUN uv sync

CMD ["uv", "run", "fastapi", "run", "--host", "0.0.0.0"]