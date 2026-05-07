FROM python:3.12-slim

# -----------------------------
# Python settings
# -----------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# -----------------------------
# App directory
# -----------------------------
WORKDIR /app

# -----------------------------
# System dependencies
# -----------------------------
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    binutils \
    libpq-dev \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# GDAL environment
# -----------------------------
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# -----------------------------
# Install uv
# -----------------------------
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# -----------------------------
# Virtual environment outside /app
# Prevents docker volume overwrite issue
# -----------------------------
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# -----------------------------
# Dependency files
# -----------------------------
COPY pyproject.toml uv.lock ./

# -----------------------------
# Install Python dependencies
# -----------------------------
RUN uv sync --frozen --no-dev

# -----------------------------
# Copy project files
# -----------------------------
COPY . .

# -----------------------------
# Expose app port
# -----------------------------
EXPOSE 8000

# -----------------------------
# Start Django with Gunicorn
# -----------------------------
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]