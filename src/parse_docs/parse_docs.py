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
    
    doc_dir = Path(directory_path)
    
    # Buscar archivos PDF y DOCX
    pdf_files = list(doc_dir.glob("*.pdf"))
    docx_files = list(doc_dir.glob("*.docx"))
    all_files = pdf_files + docx_files
    
    if not all_files:
        print(f"No se encontraron archivos PDF o DOCX en {directory_path}")
        return []
    
    print(f"Procesando {len(all_files)} archivos con LlamaParse...")
    print(f"  - PDFs: {len(pdf_files)}")
    print(f"  - DOCX: {len(docx_files)}")

    all_documents = []
    for doc_file in all_files:
        print(f"  Procesando: {doc_file.name}")
        result = reader.parse(file_path=str(doc_file))
        documents = result.get_markdown_documents()
        
        # Agregar metadata del archivo
        for doc in documents:
            doc.metadata.update({
                'file_name': doc_file.name,
                'file_path': str(doc_file),
                'file_type': doc_file.suffix.lower()
            })
        
        all_documents.extend(documents)
    
    print(f"Procesamiento completo. Se generaron {len(all_documents)} documentos.")
    
    return all_documents