
from langchain_community.llms import Ollama
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from src.config import OLLAMA_CONFIG

def connect_ollama():
dev
    llm = Ollama(
        model=OLLAMA_CONFIG["model"],
        base_url=OLLAMA_CONFIG["base_url"]
    )
    return llm