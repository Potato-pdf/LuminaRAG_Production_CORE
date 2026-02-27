
from langchain_community.llms import Ollama
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from src.config import LLM_CONFIG

def connect_ollama():
    llm = Ollama(
        model=LLM_CONFIG["model_name"],
        base_url=LLM_CONFIG["base_url"]
    )
    return llm