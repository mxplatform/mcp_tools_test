FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    make \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv and system dependencies
RUN pip install uv

WORKDIR /app


# Copy dependency files and install with uv
COPY pyproject.toml uv.lock ./
RUN uv sync

# Copy .env file
COPY .env .env

ENV PATH="/app/.venv/bin:$PATH"

# Copy source code
COPY app/ app/

EXPOSE 8080

CMD ["uv", "run", "python", "-m", "app.server"]
