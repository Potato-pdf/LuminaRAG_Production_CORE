# src/parse_docs/parsers/llama_parse.py
from typing import List, Optional
from llama_index.core import Document, SimpleDirectoryReader
from llama_parse import LlamaParse


class LlamaParseParser:
    """Parser using LlamaParse for document processing"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.parser = None

        if api_key:
            try:
                self.parser = LlamaParse(
                    api_key=api_key,
                    result_type="markdown",
                    verbose=True,
                    language="es",  # Spanish documents
                )
            except Exception as e:
                print(f"Warning: Could not initialize LlamaParse: {e}")
                print("Falling back to SimpleDirectoryReader")

    def parse_files(self, file_paths: List[str]) -> List[Document]:
        """Parse files using LlamaParse or fallback to SimpleDirectoryReader"""
        if self.parser and self.api_key:
            return self._parse_with_llamaparse(file_paths)
        else:
            return self._parse_with_simple_reader(file_paths)

    def _parse_with_llamaparse(self, file_paths: List[str]) -> List[Document]:
        """Parse files using LlamaParse"""
        documents = []

        try:
            for file_path in file_paths:
                print(f"Parsing {file_path} with LlamaParse...")
                file_docs = self.parser.load_data(file_path)
                documents.extend(file_docs)

        except Exception as e:
            print(f"Error with LlamaParse: {e}")
            print("Falling back to SimpleDirectoryReader")
            return self._parse_with_simple_reader(file_paths)

        return documents

    def _parse_with_simple_reader(self, file_paths: List[str]) -> List[Document]:
        """Fallback parser using SimpleDirectoryReader"""
        documents = []

        try:
            # Create a temporary directory structure for SimpleDirectoryReader
            import tempfile
            import shutil
            import os

            with tempfile.TemporaryDirectory() as temp_dir:
                # Copy files to temp directory
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        shutil.copy2(file_path, temp_dir)

                # Use SimpleDirectoryReader
                reader = SimpleDirectoryReader(temp_dir)
                documents = reader.load_data()

        except Exception as e:
            print(f"Error with SimpleDirectoryReader: {e}")
            # Last resort: create basic documents from file content
            documents = self._create_basic_documents(file_paths)

        return documents

    def _create_basic_documents(self, file_paths: List[str]) -> List[Document]:
        """Create basic documents from file content as last resort"""
        documents = []

        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                doc = Document(
                    text=content,
                    metadata={
                        "file_path": file_path,
                        "file_name": os.path.basename(file_path),
                        "source": "basic_parser"
                    }
                )
                documents.append(doc)

            except Exception as e:
                print(f"Error reading {file_path}: {e}")

        return documents