# Simple Legal Search for RAG-SaaS
# Add this to backend/app/api/chat/engine/legal_search.py

import json
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path

class SimpleLegalSearch:
    """Simple legal search using file-based storage"""
    
    def __init__(self, storage_path: str = "legal_data/vector_storage"):
        self.storage_path = Path(storage_path)
        self.load_index()
    
    def load_index(self):
        """Load the legal index"""
        index_file = self.storage_path / "legal_index.json"
        if index_file.exists():
            with open(index_file, "r", encoding="utf-8") as f:
                self.index_data = json.load(f)
        else:
            self.index_data = {"document_ids": [], "metadata": []}
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search legal documents"""
        query_lower = query.lower()
        results = []
        
        for i, meta in enumerate(self.index_data["metadata"]):
            score = 0
            
            # Title matching
            if query_lower in meta.get("title", "").lower():
                score += 10
            
            # Content matching
            if query_lower in meta.get("text", "").lower():
                score += 5
            
            # Act type matching
            if query_lower in meta.get("act_type", "").lower():
                score += 3
            
            # Section number matching
            if query_lower in str(meta.get("section_number", "")):
                score += 8
            
            if score > 0:
                results.append({
                    "document_id": self.index_data["document_ids"][i],
                    "score": score,
                    "metadata": meta,
                    "title": meta.get("title", ""),
                    "act_type": meta.get("act_type", ""),
                    "section_number": meta.get("section_number", "")
                })
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def search_by_act_type(self, act_type: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search documents by act type"""
        results = []
        for i, meta in enumerate(self.index_data["metadata"]):
            if meta.get("act_type", "").upper() == act_type.upper():
                results.append({
                    "document_id": self.index_data["document_ids"][i],
                    "score": 1.0,
                    "metadata": meta,
                    "title": meta.get("title", ""),
                    "act_type": meta.get("act_type", ""),
                    "section_number": meta.get("section_number", "")
                })
        
        return results[:top_k]
