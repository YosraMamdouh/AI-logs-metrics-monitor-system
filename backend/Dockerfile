# # ==========================================
# # Stage 1: Build & Dependencies Stage
# # ==========================================
# FROM python:3.11-slim AS builder

# WORKDIR /build

# # Install build dependencies for compiling C extensions (e.g. psycopg2)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     gcc \
#     libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

# COPY requirements.txt .
# RUN pip install --no-cache-dir --user -r requirements.txt

# # ==========================================
# # Stage 2: Minimal Production Runtime
# # ==========================================
# FROM python:3.11-slim AS runner

# WORKDIR /app

# # Install runtime PostgreSQL client library
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     libpq5 \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# # Create dedicated non-root user for container security
# RUN groupadd -g 10001 appgroup && \
#     useradd -u 10001 -g appgroup -s /bin/bash -m appuser

# # Copy installed Python packages from builder stage
# COPY --from=builder /root/.local /home/appuser/.local

# # Copy application source code
# COPY --chown=appuser:appgroup app /app/app

# # Set environment paths and configurations
# ENV PATH=/home/appuser/.local/bin:$PATH \
#     PYTHONUNBUFFERED=1 \
#     PYTHONDONTWRITEBYTECODE=1 \
#     PORT=8000

# # Switch to non-root user
# USER appuser

# # Expose microservice HTTP port
# EXPOSE 8000

# # Native container healthcheck
# HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
#     CMD curl -f http://localhost:8000/api/v1/health/live || exit 1

# # Start Uvicorn ASGI server
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# ==========================================
# Stage 1: Build & Dependencies Stage
# ==========================================
FROM python:3.11-slim-bookworm AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt


# ==========================================
# Stage 2: Minimal Production Runtime
# ==========================================
FROM python:3.11-slim-bookworm AS runner

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser

# Copy Python packages
COPY --from=builder /root/.local /home/appuser/.local

# Copy application
COPY --chown=appuser:appgroup app /app/app

# Environment
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

USER appuser

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/live || exit 1

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
