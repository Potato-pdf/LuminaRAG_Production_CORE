# src/parse_docs/sources/api_source.py
import os
import json
import boto3
from typing import List
from dataclasses import dataclass
from pathlib import Path
from src.config import DOCUMENT_SOURCE_CONFIG, S3_CONFIG


@dataclass
class DocumentMetadata:
    """Metadata for a document from S3"""
    empresa: str
    private: bool
    s3_key: str
    file_name: str
    local_path: str


class APISource:
    """Source for S3-based documents with company/privacy structure"""

    def __init__(self):
        self.bucket_name = DOCUMENT_SOURCE_CONFIG["s3_bucket"]
        self.s3_prefix = DOCUMENT_SOURCE_CONFIG["s3_prefix"]
        self.local_temp_dir = "/tmp/lumina_s3_downloads"
        self.processed_files_path = "/tmp/processed_files_s3.json"

        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=S3_CONFIG["access_key"],
            aws_secret_access_key=S3_CONFIG["secret_key"],
            region_name=S3_CONFIG["region"]
        )

        # Ensure temp directory exists
        os.makedirs(self.local_temp_dir, exist_ok=True)

    def get_documents_with_metadata(self) -> List[DocumentMetadata]:
        """Get documents from S3 with metadata based on company/privacy structure"""
        documents = []

        try:
            # List objects in bucket with prefix
            paginator = self.s3_client.get_paginator('list_objects_v2')
            prefix = self.s3_prefix if self.s3_prefix else ""

            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        s3_key = obj['Key']

                        # Parse company/privacy from path structure: empresa/(public|private)/files
                        parts = s3_key.split('/')
                        if len(parts) >= 3:
                            empresa = parts[0]
                            privacy_str = parts[1]
                            file_name = parts[-1]

                            # Skip if not a document file
                            if not file_name.endswith(('.pdf', '.txt', '.docx', '.md')):
                                continue

                            # Determine privacy
                            private = privacy_str.lower() == 'private'

                            # Download file locally
                            local_path = self._download_file(s3_key, file_name)

                            if local_path:
                                doc_metadata = DocumentMetadata(
                                    empresa=empresa,
                                    private=private,
                                    s3_key=s3_key,
                                    file_name=file_name,
                                    local_path=local_path
                                )
                                documents.append(doc_metadata)

        except Exception as e:
            print(f"Error accessing S3: {e}")
            return []

        return documents

    def mark_files_processed(self, file_paths: List[str]):
        """Mark files as processed to avoid re-indexing"""
        processed_files = self._load_processed_files()

        for file_path in file_paths:
            # Extract S3 key from local path if possible
            s3_key = self._get_s3_key_from_local_path(file_path)
            processed_files[s3_key] = {
                "processed_at": str(Path(file_path).stat().st_mtime),
                "source": "s3",
                "local_path": file_path
            }

        self._save_processed_files(processed_files)

    def _download_file(self, s3_key: str, file_name: str) -> str:
        """Download file from S3 to local temp directory"""
        try:
            local_path = os.path.join(self.local_temp_dir, file_name)
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            return local_path
        except Exception as e:
            print(f"Error downloading {s3_key}: {e}")
            return None

    def _get_s3_key_from_local_path(self, local_path: str) -> str:
        """Extract S3 key from local path (reverse mapping)"""
        # This is a simplified implementation - in production you'd maintain a mapping
        file_name = os.path.basename(local_path)
        # For now, return a placeholder - you'd need to maintain proper mapping
        return f"s3_key_placeholder_{file_name}"

    def _load_processed_files(self) -> dict:
        """Load processed files tracking"""
        if os.path.exists(self.processed_files_path):
            try:
                with open(self.processed_files_path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def get_file_paths(self) -> List[str]:
        """Get file paths from downloaded documents"""
        documents_metadata = self.get_documents_with_metadata()
        return [doc.local_path for doc in documents_metadata]