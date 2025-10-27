# =============================================================================
# DOCKERFILE UNIFICADO - LUMINA RAG API
# =============================================================================
# Este Dockerfile combina configuración de desarrollo y producción.
# Descomenta las líneas de PRODUCCIÓN cuando vayas a deploy.
# =============================================================================

FROM python:3.12-slim

# =============================================================================
# DEPENDENCIAS DEL SISTEMA (COMUNES)
# =============================================================================
RUN apt-get update && apt-get install -y \
    build-essential \
    libmagic-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# CONFIGURACIÓN PYTHON (COMUN)
# =============================================================================
WORKDIR /app

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# =============================================================================
# CONFIGURACIÓN DE DESARROLLO (ACTIVA)
# =============================================================================
ENV PYTHONPATH=./src

# Comando para desarrollo (con recarga automática)
CMD ["python3", "api_server.py", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# =============================================================================
# CONFIGURACIÓN DE PRODUCCIÓN (COMENTADA - Descomenta para producción)
# =============================================================================
# # Crear directorio para datos persistentes
# RUN mkdir -p /app/data
#
# # Exponer puerto
# EXPOSE 8000
#
# # Health check
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:8000/health || exit 1
#
# # Comando para producción (sin recarga)
# CMD ["python", "api_server.py", "--host", "0.0.0.0", "--port", "8000"]