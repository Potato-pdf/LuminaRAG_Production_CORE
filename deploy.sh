#!/bin/bash

# Script para construir y ejecutar la aplicación Lumina RAG API

set -e

echo "🐳 Construyendo imagen Docker para Lumina RAG API..."
docker build -t lumina-rag-api .

echo "🚀 Iniciando servicios con Docker Compose..."
docker-compose up -d

echo "⏳ Esperando a que la aplicación esté lista..."
sleep 10

echo "🔍 Verificando estado de los servicios..."
docker-compose ps

echo "📊 Verificando health check..."
curl -f http://localhost:8000/health || echo "⚠️ Health check falló, revisa los logs"

echo ""
echo "🎉 ¡Aplicación Lumina RAG API desplegada exitosamente!"
echo ""
echo "📚 Documentación API: http://localhost:8000/docs"
echo "🌐 API Base: http://localhost:8000"
echo ""
echo "📋 Comandos útiles:"
echo "  - Ver logs: docker-compose logs -f"
echo "  - Detener: docker-compose down"
echo "  - Reiniciar: docker-compose restart"
echo "  - Acceder al contenedor: docker-compose exec lumina-rag-api bash"