from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, list_collections
from db_milvus.connection import connect_milvus 

def create_schema_comercial():
    connection = connect_milvus()
    collection_name = "comercial"

    fields = [
        FieldSchema(
            name="id", dtype=DataType.INT64, is_primary=True, auto_id=True
        ),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768)
    ]
    schema = CollectionSchema(fields, description="Document embeddings comerciales")


    if collection_name not in list_collections():
        Collection(name=collection_name, schema=schema)
    # Mostrar las colecciones existentes
    print("Colecciones existentes en Milvus:", list_collections())
    return collection_name