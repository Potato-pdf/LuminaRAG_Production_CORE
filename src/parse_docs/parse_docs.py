import os
from typing import List, Optional
from pathlib import Path
from llama_index.readers.llama_parse import LlamaParse
from llama_index.core import Document

def parse_documents(directory_path: str = "pdfs", api_key: Optional[str] = None) -> List[Document]:
    api_key = api_key or os.environ.get("LLAMA_CLOUD_API_KEY") or os.environ.get("LLAMA_API_KEY")
    
    if not api_key:
        raise ValueError(
            "Se requiere API key para LlamaParse. Configúrala como variable de entorno "
            "LLAMA_CLOUD_API_KEY o LLAMA_API_KEY, o pásala como parámetro."
        )
    
    reader = LlamaParse(
        api_key=api_key,
        result_type="markdown",  # También puedes usar "text" o "all"
        language="es",           # Español para mejor procesamiento de documentos en español
        verbose=True             # Muestra información sobre el proceso
    )
    
    pdf_dir = Path(directory_path)
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No se encontraron archivos PDF en {directory_path}")
        return []
    
    print(f"Procesando {len(pdf_files)} archivos PDF con LlamaParse...")

    all_documents = []
    for pdf_file in pdf_files:
        result = reader.parse(file_path=str(pdf_file))
        documents = result.get_markdown_documents()
        all_documents.extend(documents)
    
    print(f"Procesamiento completo. Se generaron {len(all_documents)} documentos.")
    
    return all_documents