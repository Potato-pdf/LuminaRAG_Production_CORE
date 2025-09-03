from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

def read_pdf():

    documents = SimpleDirectoryReader("pdfs").load_data()
    return documents