from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType

def connect_milvus():
    connectionMilvus =connections.connect(
        alias='default',
        host='localhost',
        port='19530',
        user='minioadmin',
        password='minioadmin',
    )
    return connectionMilvus