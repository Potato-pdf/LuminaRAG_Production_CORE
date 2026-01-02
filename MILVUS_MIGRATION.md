# 🔄 Guía de Migración: FAISS → Milvus

## ¿Por qué Milvus?

### Ventajas sobre FAISS:

| Característica | FAISS | Milvus |
|----------------|-------|--------|
| **Escalabilidad** | Limitada (memoria) | Millones de vectores |
| **Multi-tenancy** | Manual (múltiples índices) | Nativo (colecciones) |
| **Actualizaciones** | Requiere rebuild | Tiempo real |
| **Filtros** | Básicos | Avanzados (metadata) |
| **Distribución** | No | Sí (clusters) |
| **Gestión** | Manual | API completa |
| **Persistencia** | Archivos | Base de datos |

---

## 📋 Pasos para Migrar

### 1. ✅ Docker Compose Actualizado

Ya agregué Milvus al `docker-compose.yml` con:
- **Milvus** - Vector database
- **etcd** - Metadata storage
- **MinIO** - Object storage

### 2. ✅ Variables de Entorno

Ya agregué al `.env`:
```bash
MILVUS_HOST=milvus
MILVUS_PORT=19530
USE_MILVUS=true
```

### 3. Levantar Servicios

```bash
# Detener servicios actuales
docker-compose down

# Levantar con Milvus
docker-compose up -d

# Verificar que Milvus está corriendo
docker logs lumina_milvus

# Verificar salud
curl http://localhost:9091/healthz
```

### 4. Crear Servicio de Milvus

Ya tienes el código base en `src/db_milvus/` y `src/create_vectors/`. Solo necesitas integrarlo.

---

## 🔧 Implementación

### Opción A: Usar Código Existente (Recomendado)

Tu proyecto YA tiene código de Milvus en:
- `src/db_milvus/connection.py`
- `src/create_vectors/create_vector_milvus.py`

Solo necesitas:

1. **Actualizar el servicio de indexación** para usar Milvus
2. **Actualizar el servicio de consultas** para buscar en Milvus

### Opción B: Migración Gradual (Más Seguro)

1. **Mantener FAISS** como fallback
2. **Agregar Milvus** en paralelo
3. **Migrar gradualmente** las colecciones
4. **Desactivar FAISS** cuando todo funcione

---

## 📝 Código de Ejemplo

### Crear Colección en Milvus

```python
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType

# Conectar
connections.connect(
    alias="default",
    host="milvus",
    port="19530"
)

# Definir schema
fields = [
    FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=500, is_primary=True),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=384),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="company_id", dtype=DataType.INT64),
    FieldSchema(name="is_private", dtype=DataType.BOOL),
    FieldSchema(name="metadata", dtype=DataType.JSON)
]

schema = CollectionSchema(fields=fields, description="Lumina RAG Commercial")
collection = Collection(name="lumina_commercial", schema=schema)

# Crear índice
index_params = {
    "metric_type": "COSINE",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 1024}
}
collection.create_index(field_name="vector", index_params=index_params)
```

### Insertar Vectores

```python
# Preparar datos
entities = [
    ["id1", "id2", "id3"],  # IDs
    [[0.1, 0.2, ...], [0.3, 0.4, ...], ...],  # Vectores
    ["texto1", "texto2", "texto3"],  # Textos
    [1, 1, 2],  # company_ids
    [False, True, False],  # is_private
    [{"key": "value"}, {...}, {...}]  # metadata
]

# Insertar
collection.insert(entities)
collection.flush()
```

### Buscar

```python
# Buscar vectores similares
search_params = {
    "metric_type": "COSINE",
    "params": {"nprobe": 10}
}

results = collection.search(
    data=[query_vector],
    anns_field="vector",
    param=search_params,
    limit=5,
    expr="company_id == 1 and is_private == false"  # Filtros!
)
```

---

## 🚀 Ventajas para tu Sistema

### 1. Multi-Tenancy Mejorado

```python
# FAISS (actual): Un índice por empresa
faiss_empresa1.index
faiss_empresa2.index
# Problema: Difícil de gestionar

# Milvus: Una colección, filtros por empresa
collection.search(
    expr="company_id == 1"  # ¡Mucho más fácil!
)
```

### 2. Actualizaciones en Tiempo Real

```python
# FAISS: Rebuild completo
rebuild_index()  # Lento, bloquea búsquedas

# Milvus: Insert directo
collection.insert([new_vector])  # Instantáneo
```

### 3. Gestión de Documentos

```python
# FAISS: No hay CRUD de vectores
# Tienes que rebuil todo

# Milvus: CRUD completo
collection.delete(expr="id in ['doc1', 'doc2']")  # Eliminar
collection.insert([new_doc])  # Agregar
```

---

## ⚙️ Configuración Recomendada

### docker-compose.yml

Ya está configurado con:
- Milvus standalone (perfecto para empezar)
- etcd para metadata
- MinIO para storage
- Health checks

### Recursos

```yaml
# Para producción, agregar límites:
milvus:
  deploy:
    resources:
      limits:
        cpus: '4'
        memory: 8G
      reservations:
        cpus: '2'
        memory: 4G
```

---

## 🧪 Testing

### 1. Verificar Milvus

```bash
# Logs
docker logs lumina_milvus

# Health
curl http://localhost:9091/healthz

# Conectar con Python
python3 -c "from pymilvus import connections; connections.connect('default', 'localhost', '19530'); print('✅ Conectado')"
```

### 2. Crear Colección de Prueba

```bash
python3 << 'EOF'
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType

connections.connect("default", "localhost", "19530")

fields = [
    FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=100, is_primary=True),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=384)
]

schema = CollectionSchema(fields=fields)
collection = Collection(name="test", schema=schema)

print(f"✅ Colección creada: {collection.name}")
EOF
```

---

## 📊 Comparación de Rendimiento

| Operación | FAISS | Milvus |
|-----------|-------|--------|
| Búsqueda (1M vectores) | ~100ms | ~50ms |
| Insert | Rebuild (minutos) | ~1ms |
| Delete | Rebuild | ~1ms |
| Filtros | Lento (post-processing) | Rápido (nativo) |
| Escalabilidad | Vertical | Horizontal |

---

## ✅ Checklist de Migración

- [x] Milvus agregado a docker-compose
- [x] Variables de entorno configuradas
- [x] Volumes creados
- [ ] Levantar servicios con Milvus
- [ ] Crear colección de prueba
- [ ] Migrar código de indexación
- [ ] Migrar código de consultas
- [ ] Testing completo
- [ ] Desactivar FAISS

---

## 🚀 Próximos Pasos

1. **Levantar Milvus:**
   ```bash
   docker-compose up -d
   ```

2. **Verificar que funciona:**
   ```bash
   curl http://localhost:9091/healthz
   ```

3. **Crear script de migración:**
   - Leer vectores de FAISS
   - Insertar en Milvus
   - Verificar resultados

4. **Actualizar código:**
   - Usar `src/db_milvus/connection.py`
   - Integrar en endpoints de indexación
   - Integrar en endpoints de consultas

---

## 💡 Recomendación

**Para empezar:** Usa Milvus en paralelo con FAISS

```python
# En tu código
USE_MILVUS = os.getenv("USE_MILVUS", "false") == "true"

if USE_MILVUS:
    # Usar Milvus
    from src.db_milvus import connect_milvus
    results = search_milvus(query)
else:
    # Usar FAISS (fallback)
    results = search_faiss(query)
```

Esto te permite:
- ✅ Testear Milvus sin romper nada
- ✅ Comparar resultados
- ✅ Migrar gradualmente
- ✅ Rollback fácil si hay problemas

---

## 📞 Soporte

- **Documentación Milvus:** https://milvus.io/docs
- **Python SDK:** https://github.com/milvus-io/pymilvus
- **Ejemplos:** https://github.com/milvus-io/bootcamp

---

## ✅ Conclusión

Milvus es **superior a FAISS** para un sistema comercial multi-tenant porque:

1. ✅ Multi-tenancy nativo
2. ✅ Actualizaciones en tiempo real
3. ✅ Mejor escalabilidad
4. ✅ Filtros avanzados
5. ✅ Gestión completa (CRUD)

**Ya está configurado en docker-compose**, solo necesitas:
1. Levantar los servicios
2. Integrar el código existente
3. Testear

¿Quieres que te ayude con la integración del código?
