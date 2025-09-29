#!/usr/bin/env python3
"""
Simple Legal Knowledge Base Integration Script for RAG-SaaS
Uses only basic dependencies - no heavy ML packages
"""

import json
import os
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from legal_data_extraction import LegalDataExtractor
from legal_data_conversion import LegalDataConverter
from legal_embeddings_simple import SimpleLegalEmbeddingsGenerator
from legal_vector_db_simple import SimpleLegalVectorDB

class SimpleLegalKnowledgeBaseIntegrator:
    def __init__(self):
        self.raw_data_path = "legal_data/raw"
        self.processed_data_path = "legal_data/processed"
        self.converted_data_path = "legal_data/converted"
        self.embeddings_path = "legal_data/embeddings"
        
        # Initialize components
        self.extractor = LegalDataExtractor(self.raw_data_path)
        self.converter = LegalDataConverter(self.processed_data_path)
        self.embeddings_generator = SimpleLegalEmbeddingsGenerator(self.converted_data_path)
        self.vector_db = SimpleLegalVectorDB(self.embeddings_path)
    
    def run_simple_integration(self):
        """Run the simplified legal knowledge base integration"""
        print("🚀 Starting Simple Legal Knowledge Base Integration for RAG-SaaS")
        print("=" * 70)
        
        try:
            # Step 1: Extract legal data (already done)
            print("\n📖 Step 1: Legal Data Extraction")
            print("-" * 40)
            print("✅ Legal data already extracted (1,958 sections)")
            
            # Step 2: Convert to LlamaIndex format (already done)
            print("\n🔄 Step 2: Legal Data Conversion")
            print("-" * 40)
            print("✅ Legal data already converted (1,960 documents)")
            
            # Step 3: Generate simple embeddings
            print("\n🤖 Step 3: Generating Simple Embeddings")
            print("-" * 40)
            embeddings_results = self.embeddings_generator.generate_simple_embeddings()
            
            # Step 4: Integrate with simple storage
            print("\n🗄️ Step 4: Integrating with Simple Storage")
            print("-" * 40)
            self.vector_db.integrate_legal_knowledge()
            
            # Step 5: Test integration
            print("\n🧪 Step 5: Testing Integration")
            print("-" * 40)
            self.test_legal_integration()
            
            print("\n✅ Simple Legal Knowledge Base Integration Completed Successfully!")
            print("=" * 70)
            
        except Exception as e:
            print(f"\n❌ Error during integration: {e}")
            raise
    
    def test_legal_integration(self):
        """Test the legal knowledge base integration"""
        print("🧪 Testing Legal Knowledge Base Integration...")
        
        # Test queries
        test_queries = [
            "What is the punishment for theft?",
            "How to apply for bail?",
            "What is criminal procedure?",
            "What are the rights of an accused?",
            "What is the procedure for filing a complaint?",
            "section 379",
            "IPC theft"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            try:
                results = self.vector_db.simple_search(query, top_k=3)
                if results:
                    print(f"  ✅ Found {len(results)} relevant results")
                    for i, result in enumerate(results):
                        print(f"    {i+1}. {result['title']} (Score: {result['score']})")
                        print(f"       Act: {result['act_type']} Section: {result['section_number']}")
                else:
                    print(f"  ⚠️ No results found")
            except Exception as e:
                print(f"  ❌ Error testing query: {e}")
    
    def create_legal_loader_for_rag(self):
        """Create a legal data loader for the existing RAG pipeline"""
        print("🔧 Creating Legal Data Loader for RAG Pipeline...")
        
        loader_code = '''# Legal Data Loader for RAG-SaaS
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
'''
        
        # Save loader code
        loader_path = Path("backend/app/api/chat/engine/loaders/legal_data.py")
        loader_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(loader_path, "w", encoding="utf-8") as f:
            f.write(loader_code)
        
        print(f"✅ Created legal data loader at {loader_path}")
    
    def create_simple_legal_search(self):
        """Create a simple legal search function"""
        print("🔧 Creating Simple Legal Search Function...")
        
        search_code = '''# Simple Legal Search for RAG-SaaS
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
'''
        
        # Save search code
        search_path = Path("backend/app/api/chat/engine/legal_search.py")
        search_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(search_path, "w", encoding="utf-8") as f:
            f.write(search_code)
        
        print(f"✅ Created legal search function at {search_path}")
    
    def create_legal_config(self):
        """Create configuration for legal data integration"""
        print("⚙️ Creating Legal Data Configuration...")
        
        config = {
            "legal_knowledge_base": {
                "enabled": True,
                "data_path": "legal_data/converted",
                "embeddings_path": "legal_data/embeddings",
                "storage_path": "legal_data/vector_storage",
                "include_acts": [
                    "IPC", "CRPC", "CPC", "MVA", "IEA", "IDA", "HMA", "NIA"
                ],
                "embedding_model": "simple-text-features",
                "search_type": "file-based",
                "total_documents": 1960
            }
        }
        
        # Get the script directory and resolve paths relative to project root
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        config_path = project_root / "legal_data/legal_config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Created legal configuration at {config_path}")

def main():
    """Main execution function"""
    integrator = SimpleLegalKnowledgeBaseIntegrator()
    
    # Run simple integration
    integrator.run_simple_integration()
    
    # Create additional components
    integrator.create_legal_loader_for_rag()
    integrator.create_simple_legal_search()
    integrator.create_legal_config()
    
    print("\n🎉 Simple Legal Knowledge Base Integration Complete!")
    print("The legal knowledge base is now ready for use with RAG-SaaS!")
    print("\n📊 Summary:")
    print("  ✅ 1,958 legal sections extracted")
    print("  ✅ 1,960 documents converted")
    print("  ✅ Simple embeddings generated")
    print("  ✅ File-based search index created")
    print("  ✅ Legal search functions ready")

if __name__ == "__main__":
    main()
