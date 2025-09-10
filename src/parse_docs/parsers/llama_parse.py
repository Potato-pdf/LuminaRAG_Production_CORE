from typing import List
from llama_parse import LlamaParse
from llama_index.core import Document
from src.config import API_CONFIG, PARSING_CONFIG

class LlamaParseParser:
    def __init__(self, api_key: str = None):
        self.api_key = API_CONFIG["llama_cloud_api_key"]
        self.reader = LlamaParse(
            api_key=self.api_key,
            result_type=PARSING_CONFIG["result_type"],
            language=PARSING_CONFIG["language"],
            verbose=PARSING_CONFIG["verbose"]
        )
    
    def parse_files(self, file_paths: List) -> List[Document]:
        all_documents = []

        for doc_file in file_paths:
            print(f"Procesando: {doc_file.name}")
            documents = self.reader.load_data(str(doc_file))
            
            # Agregar metadata del archivo
            for doc in documents:
                doc.metadata.update({
                    'file_name': doc_file.name,
                    'file_path': str(doc_file),
                    'file_type': doc_file.suffix.lower()
                })
            
            all_documents.extend(documents)

        return all_documents