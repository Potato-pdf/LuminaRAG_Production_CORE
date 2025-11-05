# =============================================================================
# DOCKERFILE - LUMINA RAG API (Producción)
# =============================================================================

FROM python:3.12-slim

# Dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libmagic-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configuración Python
WORKDIR /app

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Variables de entorno
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Crear directorios
RUN mkdir -p /app/storage /app/logs

# Exponer puerto (variable)
ARG PORT_LUMINA=3205
ENV PORT_LUMINA=${PORT_LUMINA}
EXPOSE ${PORT_LUMINA}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT_LUMINA}/health || exit 1

# Comando de producción
CMD python3 api_server.py --host 0.0.0.0