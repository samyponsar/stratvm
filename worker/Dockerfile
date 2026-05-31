FROM ghcr.io/astral-sh/uv:alpine

COPY app/ /app

WORKDIR /app

RUN uv sync

ENV PYTHONUNBUFFERED=1

CMD ["uv", "run", "main.py"]