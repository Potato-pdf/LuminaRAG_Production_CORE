# src/parse_docs/sources/local_source.py
import os
import json
from typing import List
from pathlib import Path
from src.config import DOCUMENT_SOURCE_CONFIG


class LocalFileSource:
    """Source for local file system documents"""

    def __init__(self):
        self.local_dir = DOCUMENT_SOURCE_CONFIG["local_directory"]
        self.processed_files_path = os.path.join(self.local_dir, "processed_files.json")

    def get_file_paths(self) -> List[str]:
        """Get all file paths from local directory"""
        if not os.path.exists(self.local_dir):
            return []

        file_paths = []
        for root, dirs, files in os.walk(self.local_dir):
            for file in files:
                if file.endswith(('.pdf', '.txt', '.docx', '.md')):
                    file_paths.append(os.path.join(root, file))

        return file_paths

    def mark_files_processed(self, file_paths: List[str]):
        """Mark files as processed to avoid re-indexing"""
        processed_files = self._load_processed_files()

        for file_path in file_paths:
            processed_files[file_path] = {
                "processed_at": str(Path(file_path).stat().st_mtime),
                "source": "local"
            }

        self._save_processed_files(processed_files)

    def _load_processed_files(self) -> dict:
        """Load processed files tracking"""
        if os.path.exists(self.processed_files_path):
            try:
                with open(self.processed_files_path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_processed_files(self, processed_files: dict):
        """Save processed files tracking"""
        os.makedirs(os.path.dirname(self.processed_files_path), exist_ok=True)
        with open(self.processed_files_path, 'w') as f:
            json.dump(processed_files, f, indent=2)