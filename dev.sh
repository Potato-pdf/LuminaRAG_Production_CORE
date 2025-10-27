#!/bin/bash

# Script para desarrollo local de la API Lumina RAG

set -e

echo "🔧 Configurando entorno de desarrollo..."

# Verificar que existe el entorno virtual
if [ ! -d ".venv" ]; then
    echo "🐍 Creando entorno virtual..."
    python3 -m venv .venv
fi

# Activar entorno virtual
echo "🔄 Activando entorno virtual..."
source .venv/bin/activate

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Verificar que Ollama esté corriendo (opcional)
echo "🔍 Verificando conexión con Ollama..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama está ejecutándose"
else
    echo "⚠️ Ollama no está ejecutándose. Asegúrate de tener Ollama corriendo en localhost:11434"
    echo "   Para instalar Ollama: https://ollama.ai/download"
fi

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p data
mkdir -p logs

echo ""
echo "🚀 Iniciando servidor de desarrollo..."
echo "📚 Documentación: http://localhost:8000/docs"
echo "🌐 API: http://localhost:8000"
echo ""
echo "Presiona Ctrl+C para detener"

# Ejecutar servidor con auto-reload
python api_server.py --reload