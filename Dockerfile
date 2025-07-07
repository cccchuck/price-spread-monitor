FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv sync --no-dev

# Copy source code
COPY . .

# Expose Prometheus metrics port (for internal communication only)
EXPOSE 8000

# Set environment variable for Python to use uv's virtual environment
ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "main.py"]