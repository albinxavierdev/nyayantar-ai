# Legal Data Loader for RAG-SaaS
# Add this to backend/app/api/chat/engine/loaders/legal_data.py

import json
from typing import List
from pathlib import Path
from llama_index.core.schema import Document
from llama_index.core.readers import BaseReader

class LegalDataLoader(BaseReader):
    """Loader for legal knowledge base data"""
    
    def __init__(self, legal_data_path: str = "legal_data/converted"):
        self.legal_data_path = Path(legal_data_path)
    
    def load_data(self) -> List[Document]:
        """Load all legal documents"""
        documents = []
        
        # Load combined legal documents
        combined_file = self.legal_data_path / "all_legal_documents.json"
        if combined_file.exists():
            with open(combined_file, "r", encoding="utf-8") as f:
                doc_data = json.load(f)
            
            for doc_info in doc_data:
                doc = Document(
                    text=doc_info["text"],
                    metadata=doc_info["metadata"],
                    id_=doc_info["id_"]
                )
                documents.append(doc)
        
        return documents
