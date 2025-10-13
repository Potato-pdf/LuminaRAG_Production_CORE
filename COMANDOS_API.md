# 🚀 COMANDOS PARA EJECUTAR LA API

## 📋 Pre-requisitos

### 1. Verificar servicios externos

```bash
# Verificar Ollama (REQUERIDO)
curl http://localhost:11435/api/tags

# Si no está activo, iniciar Ollama:
cd ../LuminaMO_Model_IA
docker-compose up -d
cd -
```

### 2. Verificar sistema FAISS

```bash
# Verificar si existe el sistema FAISS
ls -lh storage/graphs/faiss_system.pkl

# Si NO existe, ejecutar:
python3 migrate_to_faiss.py
```

## 🔧 INSTALACIÓN

### Opción 1: Script automático (Recomendado)
```bash
./install_api.sh
```

### Opción 2: Manual
```bash
# Instalar dependencias
pip install fastapi==0.115.0 uvicorn[standard]==0.32.0

# O instalar todo desde requirements.txt
pip install -r requirements.txt
```

## 🚀 INICIAR EL SERVIDOR API

### Modo desarrollo (recomendado para pruebas)
```bash
python3 api_server.py --reload
```

### Modo producción
```bash
python3 api_server.py
```

### Personalizar host y puerto
```bash
python3 api_server.py --host 0.0.0.0 --port 8080
```

### Con logs detallados
```bash
python3 api_server.py --reload 2>&1 | tee api.log
```

## 📚 ACCEDER A LA DOCUMENTACIÓN

Una vez el servidor esté corriendo, abre en tu navegador:

- **Swagger UI (Interactiva)**: http://localhost:8000/docs
- **ReDoc (Documentación)**: http://localhost:8000/redoc
- **Endpoint raíz**: http://localhost:8000/

## 🧪 PROBAR LA API

### Opción 1: Script de pruebas automático
```bash
# Asegúrate de que el servidor esté corriendo en otra terminal
python3 test_api.py
```

### Opción 2: cURL (Manual)

#### Health Check
```bash
curl http://localhost:8000/api/v1/health | jq
```

#### Estadísticas del sistema
```bash
curl http://localhost:8000/api/v1/stats | jq
```

#### Listar documentos
```bash
curl http://localhost:8000/api/v1/documents | jq
```

#### Realizar consulta
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿De qué trata este documento?",
    "k": 5,
    "k_roots": 5,
    "include_context": true
  }' | jq
```

#### Consulta simple sin contexto
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuáles son los procedimientos principales?",
    "k": 3,
    "k_roots": 3,
    "include_context": false
  }' | jq
```

### Opción 3: Python requests

```bash
# Crear un script de prueba rápido
cat > quick_test.py << 'EOF'
import requests
import json

# Realizar consulta
response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={
        "query": "¿De qué trata este documento?",
        "k": 5,
        "k_roots": 5
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Respuesta recibida:")
    print(f"\nPregunta: {data['query']}")
    print(f"\nRespuesta:\n{data['answer']}")
    print(f"\n📊 Documentos usados: {', '.join(data['documents_used'])}")
    print(f"⏱️ Tiempo: {data['processing_time']:.2f}s")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
EOF

python3 quick_test.py
```

### Opción 4: HTTPie (si está instalado)

```bash
# Instalar HTTPie (opcional)
pip install httpie

# Health check
http GET localhost:8000/api/v1/health

# Consulta
http POST localhost:8000/api/v1/query \
  query="¿De qué trata este documento?" \
  k:=5 \
  k_roots:=5 \
  include_context:=true
```

## 🔍 EJEMPLOS DE CONSULTAS

### Consulta básica
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Qué información contiene este documento?"}' | jq '.answer'
```

### Consulta con más resultados
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuáles son los procedimientos técnicos?",
    "k": 10,
    "k_roots": 8
  }' | jq
```

### Consulta sin contexto adicional (más rápida)
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Resume el contenido principal",
    "k": 3,
    "k_roots": 3,
    "include_context": false
  }' | jq
```

## 📊 MONITOREO

### Ver logs en tiempo real
```bash
# El servidor muestra logs en consola
# Para guardarlos:
python3 api_server.py --reload 2>&1 | tee -a logs/api.log
```

### Estadísticas del sistema
```bash
# Ver estadísticas periódicamente
watch -n 5 'curl -s http://localhost:8000/api/v1/stats | jq'
```

### Health check continuo
```bash
# Verificar salud cada 10 segundos
watch -n 10 'curl -s http://localhost:8000/api/v1/health | jq'
```

## 🐛 TROUBLESHOOTING

### Si el servidor no inicia

```bash
# 1. Verificar que el puerto 8000 esté libre
lsof -i :8000

# 2. Verificar dependencias
pip list | grep -E "fastapi|uvicorn|pydantic"

# 3. Verificar sistema FAISS
python3 -c "from src.FAISS.faiss_integration import load_faiss_system; print('OK' if load_faiss_system() else 'FAIL')"
```

### Si Ollama no responde

```bash
# Verificar estado de Ollama
curl http://localhost:11435/api/tags

# Reiniciar Ollama
cd ../LuminaMO_Model_IA
docker-compose restart
cd -
```

### Si no encuentra documentos

```bash
# Verificar documentos indexados
curl -s http://localhost:8000/api/v1/documents | jq 'length'

# Re-indexar si es necesario
python3 index.py
python3 migrate_to_faiss.py
```

## 🔄 WORKFLOW COMPLETO

```bash
# 1. Iniciar servicios externos (si no están activos)
cd ../LuminaMO_Model_IA && docker-compose up -d && cd -

# 2. Verificar sistema FAISS
ls storage/graphs/faiss_system.pkl || python3 migrate_to_faiss.py

# 3. Iniciar API
python3 api_server.py --reload

# 4. En otra terminal, probar API
python3 test_api.py

# 5. O hacer consultas manuales
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "¿De qué trata este documento?"}' | jq
```

## 📝 NOTAS IMPORTANTES

- ✅ El servidor corre en **http://localhost:8000** por defecto
- ✅ La API **NO modifica** la lógica del modelo ni del grafo
- ✅ Puedes usar el sistema de consola (`query_faiss.py`) y la API **simultáneamente**
- ✅ Los parámetros `k` y `k_roots` controlan la cantidad de resultados
- ✅ `include_context=true` incluye contexto adicional (más lento pero más completo)

## 🔗 ENLACES ÚTILES

- **Documentación completa**: `API_README.md`
- **Sistema original**: `query_faiss.py`
- **Documentación interactiva**: http://localhost:8000/docs

---

💡 **Tip**: Usa `jq` para formatear las respuestas JSON en terminal.
Si no lo tienes: `sudo apt install jq` o `brew install jq`
