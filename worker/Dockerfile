FROM python:3.14-slim

WORKDIR /app

RUN pip install uv

COPY . .

RUN uv sync --frozen

CMD ["uv", "run", "main.py"]
