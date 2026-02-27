#!/bin/bash
# 🚀 Script de instalación rápida para la API REST

echo "🌐 INSTALACIÓN API REST - LUMINA RAG"
echo "===================================="
echo ""

# Verificar Python
echo "1️⃣ Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado. Por favor instalar Python 3.8+"
    exit 1
fi
echo "✅ Python $(python3 --version) encontrado"
echo ""

# Instalar dependencias de la API
echo "2️⃣ Instalando dependencias de la API..."
pip install fastapi==0.115.0 uvicorn[standard]==0.32.0
echo "✅ Dependencias instaladas"
echo ""

# Verificar sistema FAISS
echo "3️⃣ Verificando sistema FAISS..."
if [ ! -f "storage/graphs/faiss_system.pkl" ]; then
    echo "⚠️ Sistema FAISS no encontrado"
    echo ""
    echo "Para inicializar el sistema FAISS:"
    echo "  1. python3 index.py          # Indexar documentos"
    echo "  2. python3 migrate_to_faiss.py  # Migrar a FAISS"
    echo ""
    read -p "¿Deseas ejecutar la migración ahora? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 Ejecutando migración..."
        python3 migrate_to_faiss.py
    else
        echo "⚠️ Recuerda ejecutar la migración antes de iniciar la API"
    fi
else
    echo "✅ Sistema FAISS encontrado"
fi
echo ""

# Verificar servicios externos
echo "4️⃣ Verificando servicios externos..."

# Milvus
echo -n "  Milvus... "
if curl -s http://localhost:19530 > /dev/null 2>&1; then
    echo "✅"
else
    echo "⚠️ No disponible (opcional para consultas)"
fi

# Ollama
echo -n "  Ollama... "
if curl -s http://localhost:11435/api/tags > /dev/null 2>&1; then
    echo "✅"
else
    echo "❌ No disponible (REQUERIDO)"
    echo ""
    echo "Para iniciar Ollama:"
    echo "  cd ../LuminaMO_Model_IA"
    echo "  docker-compose up -d"
    echo ""
fi
echo ""

# Resumen
echo "📋 RESUMEN"
echo "=========="
echo "✅ Dependencias instaladas"
echo "📁 Archivos API creados:"
echo "   • api_server.py"
echo "   • src/api/models.py"
echo "   • src/api/routes.py"
echo "   • src/api/service.py"
echo "   • test_api.py"
echo "   • API_README.md"
echo ""

echo "🚀 INICIAR API"
echo "=============="
echo "# Modo desarrollo (con auto-reload):"
echo "python3 api_server.py --reload"
echo ""
echo "# Modo producción:"
echo "python3 api_server.py"
echo ""
echo "# Personalizar host/puerto:"
echo "python3 api_server.py --host 0.0.0.0 --port 8080"
echo ""

echo "📚 DOCUMENTACIÓN"
echo "==============="
echo "Una vez iniciado el servidor:"
echo "• Swagger UI: http://localhost:8000/docs"
echo "• ReDoc: http://localhost:8000/redoc"
echo "• Guía completa: API_README.md"
echo ""

echo "🧪 PROBAR API"
echo "============"
echo "python3 test_api.py"
echo ""

echo "✨ ¡Instalación completada!"
