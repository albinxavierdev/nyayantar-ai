#!/usr/bin/env python3
"""
Legal Knowledge Base Integration Script for RAG-SaaS
Main script to integrate legal knowledge with existing RAG pipeline
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
from legal_embeddings import LegalEmbeddingsGenerator
from legal_vector_db import LegalVectorDB

class LegalKnowledgeBaseIntegrator:
    def __init__(self):
        self.raw_data_path = "legal_data/raw"
        self.processed_data_path = "legal_data/processed"
        self.converted_data_path = "legal_data/converted"
        self.embeddings_path = "legal_data/embeddings"
        
        # Initialize components
        self.extractor = LegalDataExtractor(self.raw_data_path)
        self.converter = LegalDataConverter(self.processed_data_path)
        self.embeddings_generator = LegalEmbeddingsGenerator(self.converted_data_path)
        self.vector_db = LegalVectorDB(self.embeddings_path)
    
    def run_full_integration(self):
        """Run the complete legal knowledge base integration"""
        print("🚀 Starting Legal Knowledge Base Integration for RAG-SaaS")
        print("=" * 60)
        
        try:
            # Step 1: Extract legal data
            print("\n📖 Step 1: Extracting Legal Data")
            print("-" * 40)
            legal_data = self.extractor.extract_all_legal_data()
            
            # Step 2: Convert to LlamaIndex format
            print("\n🔄 Step 2: Converting to LlamaIndex Format")
            print("-" * 40)
            documents = self.converter.convert_all_legal_data()
            
            # Step 3: Generate embeddings
            print("\n🤖 Step 3: Generating Embeddings")
            print("-" * 40)
            embeddings_results = self.embeddings_generator.generate_all_embeddings()
            
            # Step 4: Integrate with vector database
            print("\n🗄️ Step 4: Integrating with Vector Database")
            print("-" * 40)
            self.vector_db.integrate_legal_knowledge()
            
            # Step 5: Test integration
            print("\n🧪 Step 5: Testing Integration")
            print("-" * 40)
            self.test_legal_integration()
            
            print("\n✅ Legal Knowledge Base Integration Completed Successfully!")
            print("=" * 60)
            
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
            "What is the procedure for filing a complaint?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            try:
                results = self.vector_db.test_retrieval(query, top_k=3)
                if results:
                    print(f"  ✅ Found {len(results)} relevant results")
                else:
                    print(f"  ⚠️ No results found")
            except Exception as e:
                print(f"  ❌ Error testing query: {e}")
    
    def create_legal_loader_for_rag(self):
        """Create a legal data loader for the existing RAG pipeline"""
        print("🔧 Creating Legal Data Loader for RAG Pipeline...")
        
        loader_code = '''
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
'''
        
        # Save loader code
        loader_path = Path("backend/app/api/chat/engine/loaders/legal_data.py")
        loader_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(loader_path, "w", encoding="utf-8") as f:
            f.write(loader_code)
        
        print(f"✅ Created legal data loader at {loader_path}")
    
    def update_rag_pipeline(self):
        """Update the RAG pipeline to include legal data"""
        print("🔧 Updating RAG Pipeline for Legal Data...")
        
        # Read existing loaders file
        loaders_file = Path("backend/app/api/chat/engine/loaders/__init__.py")
        if loaders_file.exists():
            with open(loaders_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Add legal data loader import
            if "legal_data" not in content:
                content = content.replace(
                    "from .file import get_file_documents",
                    "from .file import get_file_documents\nfrom .legal_data import LegalDataLoader"
                )
                
                with open(loaders_file, "w", encoding="utf-8") as f:
                    f.write(content)
                
                print("✅ Updated loaders __init__.py")
        
        # Update get_documents function
        file_loader_path = Path("backend/app/api/chat/engine/loaders/file.py")
        if file_loader_path.exists():
            with open(file_loader_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Add legal data loading
            if "legal_data" not in content:
                content = content.replace(
                    "def get_file_documents(config: FileLoaderConfig):",
                    '''def get_file_documents(config: FileLoaderConfig):
    # Load legal data if enabled
    if getattr(config, 'include_legal_data', False):
        from .legal_data import LegalDataLoader
        legal_loader = LegalDataLoader()
        legal_docs = legal_loader.load_data()
        if legal_docs:
            return legal_docs'''
                )
                
                with open(file_loader_path, "w", encoding="utf-8") as f:
                    f.write(content)
                
                print("✅ Updated file loader for legal data")
    
    def create_legal_config(self):
        """Create configuration for legal data integration"""
        print("⚙️ Creating Legal Data Configuration...")
        
        config = {
            "legal_knowledge_base": {
                "enabled": True,
                "data_path": "legal_data/converted",
                "embeddings_path": "legal_data/embeddings",
                "vector_collection": "legal_knowledge",
                "include_acts": [
                    "IPC", "CRPC", "CPC", "MVA", "IEA", "IDA", "HMA", "NIA"
                ],
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "chunk_size": 1024,
                "chunk_overlap": 100
            }
        }
        
        config_path = Path("legal_data/legal_config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Created legal configuration at {config_path}")

def main():
    """Main execution function"""
    integrator = LegalKnowledgeBaseIntegrator()
    
    # Run full integration
    integrator.run_full_integration()
    
    # Create additional components
    integrator.create_legal_loader_for_rag()
    integrator.update_rag_pipeline()
    integrator.create_legal_config()
    
    print("\n🎉 Legal Knowledge Base Integration Complete!")
    print("The legal knowledge base is now ready for use with RAG-SaaS!")

if __name__ == "__main__":
    main()
