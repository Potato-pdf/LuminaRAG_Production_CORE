import os
import json
from pathlib import Path
from typing import List, Optional
from src.config import PATH_CONFIG, PARSING_CONFIG, STORAGE_CONFIG

class LocalFileSource:

    def __init__(self):
        self.directory_path = PATH_CONFIG["pdf_directory"]
        self.supported_extensions = PARSING_CONFIG["supported_extensions"]
        self.tracking_file = os.path.join(STORAGE_CONFIG["base_dir"], "processed_files_local.json")

        # Crear directorio de storage si no existe
        os.makedirs(STORAGE_CONFIG["base_dir"], exist_ok=True)

    def get_file_paths(self) -> List[Path]:
        """Obtener rutas de archivos locales no procesados, buscando recursivamente en subdirectorios"""
        doc_dir = Path(self.directory_path)
        processed_files = self._load_processed_files()

        all_files = []
        for ext in self.supported_extensions:
            # Buscar recursivamente en todos los subdirectorios
            all_files.extend(doc_dir.glob(f"**/*{ext}"))

        # Filtrar archivos ya procesados
        new_files = []
        for file_path in all_files:
            file_name = file_path.name
            if file_name in processed_files:
                print(f"📁 Archivo ya procesado: {file_path}")
                continue
            new_files.append(file_path)

        if not new_files:
            print(f"📁 No se encontraron archivos nuevos {self.supported_extensions} en {self.directory_path} o subdirectorios")

        print(f"📁 Encontrados {len(new_files)} archivos nuevos para procesar")
        return new_files

    def _load_processed_files(self) -> set:
        """Cargar set de archivos procesados localmente"""
        if os.path.exists(self.tracking_file):
            try:
                with open(self.tracking_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('processed_files', []))
            except Exception as e:
                print(f"⚠️ Error cargando tracking file local: {e}")
        return set()

    def mark_files_processed(self, file_paths: List[Path]):
        """Marcar archivos locales como procesados"""
        processed_files = self._load_processed_files()
        for path in file_paths:
            file_name = path.name
            processed_files.add(file_name)

        try:
            with open(self.tracking_file, 'w') as f:
                json.dump({'processed_files': list(processed_files)}, f, indent=2)
            print(f"✅ Marcados {len(file_paths)} archivos locales como procesados")
        except Exception as e:
            print(f"❌ Error guardando tracking file local: {e}")