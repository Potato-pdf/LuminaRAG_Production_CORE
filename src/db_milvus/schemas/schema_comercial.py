from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, list_collections, utility
from src.db_milvus.connection import connect_milvus
import time

def create_dynamic_schema(empresa: str, private: bool):
    """
    Crear esquema dinámico basado en empresa y privacidad
    Nombre de colección: {empresa}_{privacidad}
    """
    connection = connect_milvus()

    # Crear nombre de colección: empresa_privacidad (ej: Finfessa_public, Finfessa_private)
    privacidad_str = "private" if private else "public"
    collection_name = f"{empresa}_{privacidad_str}"

    print(f"🏗️ Creando colección dinámica: {collection_name}")

    # Definir campos del esquema
    fields = [
        FieldSchema(
            name="id", dtype=DataType.VARCHAR, max_length=100, is_primary=True
        ),
        FieldSchema(
            name="text", dtype=DataType.VARCHAR, max_length=65535
        ),
        FieldSchema(
            name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768
        ),
        # Metadata adicional
        FieldSchema(
            name="empresa", dtype=DataType.VARCHAR, max_length=100
        ),
        FieldSchema(
            name="private", dtype=DataType.BOOL
        ),
        FieldSchema(
            name="file_name", dtype=DataType.VARCHAR, max_length=255
        ),
        FieldSchema(
            name="s3_key", dtype=DataType.VARCHAR, max_length=500
        ),
        # Campos jerárquicos
        FieldSchema(
            name="document_name", dtype=DataType.VARCHAR, max_length=255
        ),
        FieldSchema(
            name="is_document_root", dtype=DataType.BOOL
        ),
        FieldSchema(
            name="tree_level", dtype=DataType.INT64
        ),
        FieldSchema(
            name="hierarchical_importance", dtype=DataType.FLOAT
        )
    ]

    schema = CollectionSchema(
        fields,
        description=f"Document embeddings para {empresa} ({privacidad_str})",
        enable_dynamic_field=True
    )

    try:
        # Eliminar colección si existe (para recrear con esquema actualizado)
        if utility.has_collection(collection_name):
            utility.drop_collection(collection_name)
            print(f"🗑️ Colección {collection_name} eliminada para recrear")
            time.sleep(1)

        # Crear nueva colección
        collection = Collection(name=collection_name, schema=schema)
        print(f"✅ Colección {collection_name} creada")

        # Crear índice en el campo de embedding
        index_params = {
            'metric_type': 'IP',  # Inner Product para similitud coseno
            'index_type': 'FLAT',
            'params': {}
        }
        collection.create_index('embedding', index_params)
        print(f"✅ Índice creado para {collection_name}")

        # Cargar colección
        collection.load()
        print(f"✅ Colección {collection_name} cargada")

        return collection_name

    except Exception as e:
        print(f"❌ Error creando colección {collection_name}: {e}")
        raise

def get_or_create_collection(empresa: str, private: bool):
    """
    Obtener colección existente o crear nueva si no existe
    """
    privacidad_str = "private" if private else "public"
    collection_name = f"{empresa}_{privacidad_str}"

    try:
        connection = connect_milvus()

        # Verificar si colección existe
        if utility.has_collection(collection_name):
            print(f"📂 Usando colección existente: {collection_name}")
            collection = Collection(collection_name)
            if not collection.is_loaded:
                collection.load()
            return collection_name
        else:
            # Crear nueva colección
            return create_dynamic_schema(empresa, private)

    except Exception as e:
        print(f"❌ Error obteniendo/creando colección {collection_name}: {e}")
        raise

def list_dynamic_collections():
    """
    Listar todas las colecciones dinámicas creadas
    """
    try:
        connection = connect_milvus()
        collections = list_collections()
        dynamic_collections = [c for c in collections if '_' in c and ('_private' in c or '_public' in c)]
        print(f"📋 Colecciones dinámicas encontradas: {dynamic_collections}")
        return dynamic_collections
    except Exception as e:
        print(f"❌ Error listando colecciones: {e}")
        return []

# Función legacy para compatibilidad
def create_schema_comercial():
    """
    Función legacy - ahora usa create_dynamic_schema
    """
    print("⚠️ Función legacy: use create_dynamic_schema(empresa, private) en su lugar")
    return create_dynamic_schema("Default", False)