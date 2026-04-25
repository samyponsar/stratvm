FROM python:3.14-slim

WORKDIR /app

RUN pip install uv

COPY . .

RUN uv sync --frozen

EXPOSE 8000

CMD ["uv", "run", "fastapi", "dev", "--host", "0.0.0.0"]
