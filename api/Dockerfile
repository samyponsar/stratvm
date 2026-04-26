FROM ghcr.io/astral-sh/uv:alpine

WORKDIR /app

COPY shared/ ./shared/
COPY api/ ./

EXPOSE 8000

CMD ["uv", "run", "fastapi", "dev", "--host", "0.0.0.0"]
