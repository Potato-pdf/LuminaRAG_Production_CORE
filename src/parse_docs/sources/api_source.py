import os
import json
import tempfile
from pathlib import Path
from typing import List
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from src.config import S3_CONFIG, PARSING_CONFIG, STORAGE_CONFIG

class APISource:
    def __init__(self):
        self.bucket_name = S3_CONFIG["bucket_name"]
        self.region = S3_CONFIG["region"]
        self.access_key = S3_CONFIG["access_key"]
        self.secret_key = S3_CONFIG["secret_key"]
        self.supported_extensions = PARSING_CONFIG["supported_extensions"]
        self.tracking_file = os.path.join(STORAGE_CONFIG["base_dir"], "processed_files.json")
        self.temp_dir = tempfile.mkdtemp(prefix="s3_docs_")

        # Crear directorio de storage si no existe
        os.makedirs(STORAGE_CONFIG["base_dir"], exist_ok=True)

        # Inicializar cliente S3
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            )
        except (NoCredentialsError, PartialCredentialsError) as e:
            raise Exception(f"Error de credenciales S3: {e}")

    def get_file_paths(self) -> List[str]:
        """Obtener rutas locales de archivos de S3 que no han sido procesados"""
        try:
            # Obtener archivos procesados previamente
            processed_files = self._load_processed_files()

            # Listar objetos en el bucket
            objects = self.s3_client.list_objects_v2(Bucket=self.bucket_name)

            if 'Contents' not in objects:
                print(f"No se encontraron archivos en el bucket {self.bucket_name}")
                return []

            new_files = []
            for obj in objects['Contents']:
                file_key = obj['Key']
                file_name = os.path.basename(file_key)

                # Verificar extensión
                if not any(file_name.lower().endswith(ext) for ext in self.supported_extensions):
                    continue

                # Verificar si ya fue procesado
                if file_name in processed_files:
                    print(f"Archivo ya procesado: {file_name}")
                    continue

                # Descargar archivo
                local_path = self._download_file(file_key, file_name)
                if local_path:
                    new_files.append(local_path)

            print(f"📥 Descargados {len(new_files)} archivos nuevos de S3")
            return new_files

        except Exception as e:
            print(f"❌ Error obteniendo archivos de S3: {e}")
            return []

    def _download_file(self, file_key: str, file_name: str) -> str:
        """Descargar archivo de S3 a directorio temporal"""
        try:
            local_path = os.path.join(self.temp_dir, file_name)
            self.s3_client.download_file(self.bucket_name, file_key, local_path)
            return local_path
        except Exception as e:
            print(f"❌ Error descargando {file_key}: {e}")
            return None

    def _load_processed_files(self) -> set:
        """Cargar set de archivos procesados"""
        if os.path.exists(self.tracking_file):
            try:
                with open(self.tracking_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('processed_files', []))
            except Exception as e:
                print(f"⚠️ Error cargando tracking file: {e}")
        return set()

    def mark_files_processed(self, file_paths: List[str]):
        """Marcar archivos como procesados"""
        processed_files = self._load_processed_files()
        for path in file_paths:
            file_name = os.path.basename(path)
            processed_files.add(file_name)

        try:
            with open(self.tracking_file, 'w') as f:
                json.dump({'processed_files': list(processed_files)}, f, indent=2)
            print(f"✅ Marcados {len(file_paths)} archivos como procesados")
        except Exception as e:
            print(f"❌ Error guardando tracking file: {e}")