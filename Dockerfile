# =============================================================================
# DOCKERFILE - LUMINA RAG API
# =============================================================================
# Multi-stage build para optimizar tamaño de imagen
# =============================================================================

FROM python:3.11-slim as base

# Metadata
LABEL maintainer="Lumina RAG Team"
LABEL description="Lumina RAG API - Sistema comercial multi-tenant"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/storage/faiss_collections \
    /app/storage/graphs \
    /app/logs \
    /app/pdfs

# Exponer puerto
EXPOSE 3205

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3205/health || exit 1

# Comando para ejecutar la aplicación
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "3205", "--reload"]
