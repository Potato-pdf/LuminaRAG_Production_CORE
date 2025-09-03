
from langchain_community.llms import Ollama
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

def connect_ollama():
    llm = Ollama(model="llama3.2", base_url="http://localhost:11435")
    return llm