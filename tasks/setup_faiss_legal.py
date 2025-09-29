#!/usr/bin/env python3
"""
Setup FAISS Legal Index for RAG-SaaS
Creates FAISS index with InLegalBERT embeddings for deep IPC knowledge
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent.parent / "backend"))

def setup_faiss_legal_index():
    """Setup FAISS index with InLegalBERT embeddings"""
    print("🚀 Setting up FAISS Legal Index for RAG-SaaS")
    print("=" * 60)
    
    try:
        # Check if FAISS is available
        try:
            import faiss
            from langchain_community.vectorstores import FAISS
            from langchain_huggingface import HuggingFaceEmbeddings
            from langchain.schema import Document
            print("✅ FAISS and dependencies available")
        except ImportError as e:
            print(f"❌ FAISS not available: {e}")
            print("Please install with: pip install faiss-cpu langchain-community langchain-huggingface")
            return False
        
        # Load IPC data
        print("\n📖 Loading IPC data...")
        legal_data_path = Path("legal_data/raw/laws_raw.json")
        if not legal_data_path.exists():
            print(f"❌ Legal data not found at {legal_data_path}")
            return False
        
        with open(legal_data_path, "r", encoding="utf-8") as f:
            ipc_data = json.load(f)
        
        print(f"✅ Loaded IPC data: {len(ipc_data.get('IPC', {}))} sections")
        
        # Create documents
        print("\n📄 Creating documents...")
        docs = []
        for section, details in ipc_data["IPC"].items():
            title = details.get("title", "")
            content = details.get("content", "")
            text = f"{section}: {title}\n{content}"
            
            doc = Document(
                page_content=text,
                metadata={
                    "section": section,
                    "title": title,
                    "act_type": "IPC",
                    "source": "Ratanlal & Dhirajlal (36th Edition)",
                    "content_length": len(content)
                }
            )
            docs.append(doc)
        
        print(f"✅ Created {len(docs)} documents")
        
        # Initialize InLegalBERT embedding model
        print("\n🤖 Initializing InLegalBERT embedding model...")
        try:
            embedding_model = HuggingFaceEmbeddings(
                model_name="law-ai/InLegalBERT",
                model_kwargs={'device': 'cpu'}
            )
            print("✅ InLegalBERT embedding model loaded")
        except Exception as e:
            print(f"❌ Failed to load InLegalBERT: {e}")
            print("Falling back to general-purpose embedding...")
            embedding_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        
        # Build FAISS index
        print("\n🔨 Building FAISS index...")
        try:
            vectorstore = FAISS.from_documents(docs, embedding_model)
            print("✅ FAISS index built successfully")
        except Exception as e:
            print(f"❌ Failed to build FAISS index: {e}")
            return False
        
        # Save index
        print("\n💾 Saving FAISS index...")
        faiss_index_path = Path("legal_data/faiss_index")
        faiss_index_path.mkdir(exist_ok=True)
        
        index_file = faiss_index_path / "ipc_embed_db_inlegalbert"
        vectorstore.save_local(str(index_file))
        print(f"✅ FAISS index saved to {index_file}")
        
        # Test the index
        print("\n🧪 Testing FAISS index...")
        try:
            test_results = vectorstore.similarity_search("theft punishment", k=3)
            print(f"✅ Test search successful: Found {len(test_results)} results")
            
            for i, result in enumerate(test_results):
                print(f"  {i+1}. {result.metadata.get('section', '')} - {result.metadata.get('title', '')[:50]}...")
        except Exception as e:
            print(f"⚠️ Test search failed: {e}")
        
        # Get index statistics
        print("\n📊 FAISS Index Statistics:")
        print(f"  Total Documents: {len(docs)}")
        print(f"  Index Size: {vectorstore.index.ntotal if hasattr(vectorstore, 'index') else 'Unknown'}")
        print(f"  Embedding Model: {embedding_model.model_name}")
        print(f"  Index Path: {index_file}")
        
        print("\n✅ FAISS Legal Index setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error setting up FAISS index: {e}")
        return False

def main():
    """Main execution function"""
    success = setup_faiss_legal_index()
    if success:
        print("\n🎉 FAISS Legal Index is ready for use!")
        print("The hybrid legal knowledge system can now use deep IPC knowledge.")
    else:
        print("\n❌ FAISS Legal Index setup failed.")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
