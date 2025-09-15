from pathlib import Path
from typing import List, Optional
from src.config import PATH_CONFIG, PARSING_CONFIG

class LocalFileSource:

    def __init__(self):
        self.directory_path = PATH_CONFIG["pdf_directory"]

    def get_file_paths(self) -> List[Path]:
        doc_dir = Path(self.directory_path)
        all_files = []
        for ext in PARSING_CONFIG["supported_extensions"]:
            all_files.extend(doc_dir.glob(f"*{ext}"))
        
        if not all_files:
            print(f"No se encontraron archivos {PARSING_CONFIG['supported_extensions']} en {self.directory_path}")
        
        return all_files