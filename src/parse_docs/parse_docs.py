import os
from typing import List, Optional
from pathlib import Path
from llama_index.readers.llama_parse import LlamaParse
from llama_index.core import Document
# 🎯 CONFIGURACIÓN 100% CENTRALIZADA - TODO VIENE DE SETTINGS
from src.config import PATH_CONFIG, API_CONFIG, PARSING_CONFIG

directory_path = PATH_CONFIG["pdf_directory"]
api_key = API_CONFIG["llama_cloud_api_key"]


def parse_documents(directory_path: str = None, api_key: Optional[str] = None) -> List[Document]:

    reader = LlamaParse( #| inicializa llamaparse
        api_key=api_key,
        result_type=PARSING_CONFIG["result_type"],   # ← DESDE SETTINGS
        language=PARSING_CONFIG["language"],         # ← DESDE SETTINGS  
        verbose=PARSING_CONFIG["verbose"]            # ← DESDE SETTINGS
    )

    doc_dir = Path(directory_path)

    all_files = [] #| busca los archivos con extenciones definidas en settings
    for ext in PARSING_CONFIG["supported_extensions"]:
        all_files.extend(doc_dir.glob(f"*{ext}"))
    
    if not all_files:
        print(f"No se encontraron archivos {PARSING_CONFIG['supported_extensions']} en {directory_path}")
        return []
    
    files_by_type = {} #| Clasifica por el tipo de archivo
    for ext in PARSING_CONFIG["supported_extensions"]:
        files_by_type[ext] = len([f for f in all_files if f.suffix.lower() == ext])
    
    for ext, count in files_by_type.items():
        if count > 0: #| cuenta cada tipo de archivo
            print(f"   - {ext.upper()}: {count}")

    all_documents = []
    for doc_file in all_files: #| parsea el archivo
        print(f"  🔄 Procesando: {doc_file.name}")
        result = reader.parse(file_path=str(doc_file))
        documents = result.get_markdown_documents()
        
        #| Agregar metadata del archivo
        for doc in documents: 
            doc.metadata.update({
                'file_name': doc_file.name,
                'file_path': str(doc_file),
                'file_type': doc_file.suffix.lower()
            })
        
        all_documents.extend(documents) #| agrega a la lista principal
    
    print(f"✅ Procesamiento completo. Se generaron {len(all_documents)} documentos.")
    
    return all_documents #| Retorna la lista de documentos parseados