#!/usr/bin/env python3
"""
Simple Legal Vector Database Integration Script for RAG-SaaS
Uses basic file-based storage instead of Qdrant
"""

import json
import os
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path

class SimpleLegalVectorDB:
    def __init__(self, 
                 embeddings_path: str = "legal_data/embeddings",
                 storage_path: str = "legal_data/vector_storage"):
        # Get the script directory and resolve paths relative to project root
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        self.embeddings_path = project_root / embeddings_path
        self.storage_path = project_root / storage_path
        self.storage_path.mkdir(exist_ok=True)
        
        # Simple in-memory storage
        self.documents = []
        self.embeddings = []
        self.metadata = []
    
    def load_embeddings(self, filename: str = "simple_legal_embeddings.json") -> Dict[str, Any]:
        """Load embeddings from file"""
        print(f"📖 Loading embeddings from {filename}...")
        
        with open(self.embeddings_path / filename, "r", encoding="utf-8") as f:
            embeddings_data = json.load(f)
        
        print(f"✅ Loaded {embeddings_data['total_documents']} embeddings")
        return embeddings_data
    
    def create_simple_index(self, embeddings_data: Dict[str, Any]):
        """Create a simple index for legal documents"""
        print("🗄️ Creating simple legal knowledge index...")
        
        embeddings = np.array(embeddings_data["embeddings"])
        document_ids = embeddings_data["document_ids"]
        metadata = embeddings_data["metadata"]
        
        # Store in memory
        self.embeddings = embeddings
        self.metadata = metadata
        self.documents = document_ids
        
        # Create simple index file
        index_data = {
            "total_documents": len(document_ids),
            "embedding_dimension": embeddings.shape[1],
            "document_ids": document_ids,
            "metadata": metadata,
            "index_type": "simple-file-based"
        }
        
        # Save index
        with open(self.storage_path / "legal_index.json", "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Created index with {len(document_ids)} legal documents")
    
    def simple_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Simple search using basic text matching"""
        print(f"🔍 Searching for: '{query}'")
        
        query_lower = query.lower()
        results = []
        
        for i, meta in enumerate(self.metadata):
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
            
            # Legal keywords matching
            keywords = meta.get("legal_keywords", [])
            for keyword in keywords:
                if query_lower in keyword.lower():
                    score += 2
            
            if score > 0:
                results.append({
                    "document_id": self.documents[i],
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
        print(f"🔍 Searching {act_type} documents...")
        
        results = []
        for i, meta in enumerate(self.metadata):
            if meta.get("act_type", "").upper() == act_type.upper():
                results.append({
                    "document_id": self.documents[i],
                    "score": 1.0,
                    "metadata": meta,
                    "title": meta.get("title", ""),
                    "act_type": meta.get("act_type", ""),
                    "section_number": meta.get("section_number", "")
                })
        
        return results[:top_k]
    
    def search_by_section_number(self, section_number: str) -> Optional[Dict[str, Any]]:
        """Search for specific section number"""
        print(f"🔍 Searching for section {section_number}...")
        
        for i, meta in enumerate(self.metadata):
            if str(meta.get("section_number", "")) == str(section_number):
                return {
                    "document_id": self.documents[i],
                    "score": 1.0,
                    "metadata": meta,
                    "title": meta.get("title", ""),
                    "act_type": meta.get("act_type", ""),
                    "section_number": meta.get("section_number", "")
                }
        
        return None
    
    def test_search_functionality(self):
        """Test the search functionality"""
        print("🧪 Testing search functionality...")
        
        # Test queries
        test_queries = [
            "theft punishment",
            "bail application", 
            "criminal procedure",
            "section 379",
            "IPC"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            results = self.simple_search(query, top_k=3)
            
            if results:
                print(f"  ✅ Found {len(results)} results:")
                for i, result in enumerate(results):
                    print(f"    {i+1}. {result['title']} (Score: {result['score']})")
                    print(f"       Act: {result['act_type']} Section: {result['section_number']}")
            else:
                print(f"  ⚠️ No results found")
        
        # Test act type search
        print(f"\n🔍 Testing act type search for IPC:")
        ipc_results = self.search_by_act_type("IPC", top_k=3)
        print(f"  ✅ Found {len(ipc_results)} IPC sections")
        
        # Test section number search
        print(f"\n🔍 Testing section number search for 379:")
        section_result = self.search_by_section_number("379")
        if section_result:
            print(f"  ✅ Found section: {section_result['title']}")
        else:
            print(f"  ⚠️ Section not found")
    
    def integrate_legal_knowledge(self, embeddings_filename: str = "simple_legal_embeddings.json"):
        """Integrate legal knowledge with simple storage"""
        print("🚀 Starting simple legal knowledge integration...")
        
        # Load embeddings
        embeddings_data = self.load_embeddings(embeddings_filename)
        
        # Create simple index
        self.create_simple_index(embeddings_data)
        
        # Test search functionality
        print("\n🧪 Testing search functionality...")
        self.test_search_functionality()
        
        print("\n✅ Simple legal knowledge integration completed successfully!")

def main():
    """Main execution function"""
    vector_db = SimpleLegalVectorDB()
    vector_db.integrate_legal_knowledge()

if __name__ == "__main__":
    main()
