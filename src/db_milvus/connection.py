from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType
from src.config import MILVUS_CONFIG

def connect_milvus():
    connectionMilvus = connections.connect(
        alias='default',
        host=MILVUS_CONFIG["host"],
        port=MILVUS_CONFIG["port"],
        user=MILVUS_CONFIG["user"],
        password=MILVUS_CONFIG["password"],
    )
    return connectionMilvus