# Stage 1: Base
FROM python:3.12-slim AS base

WORKDIR /app

# Install system deps (nếu cần cho psycopg2, matplotlib, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy only pyproject.toml + poetry.lock trước (để tận dụng cache)
COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --without dev --no-root

# Copy source code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI with Uvicorn
CMD ["python", "main.py"]
