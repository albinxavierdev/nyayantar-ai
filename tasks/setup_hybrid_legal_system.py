#!/usr/bin/env python3
"""
Setup Hybrid Legal System for RAG-SaaS
Complete setup script for the hybrid FAISS + Qdrant legal knowledge system
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent.parent / "backend"))

def setup_hybrid_legal_system():
    """Setup the complete hybrid legal system"""
    print("🚀 Setting up Hybrid Legal System for RAG-SaaS")
    print("=" * 70)
    
    try:
        # Step 1: Check dependencies
        print("\n📋 Step 1: Checking Dependencies")
        print("-" * 40)
        check_dependencies()
        
        # Step 2: Setup FAISS index
        print("\n🤖 Step 2: Setting up FAISS Index")
        print("-" * 40)
        setup_faiss_index()
        
        # Step 3: Setup Qdrant integration
        print("\n🗄️ Step 3: Setting up Qdrant Integration")
        print("-" * 40)
        setup_qdrant_integration()
        
        # Step 4: Test hybrid system
        print("\n🧪 Step 4: Testing Hybrid System")
        print("-" * 40)
        test_hybrid_system()
        
        # Step 5: Create configuration
        print("\n⚙️ Step 5: Creating Configuration")
        print("-" * 40)
        create_legal_config()
        
        print("\n✅ Hybrid Legal System setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error setting up hybrid legal system: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are available"""
    dependencies = {
        "faiss-cpu": False,
        "langchain-community": False,
        "langchain-huggingface": False,
        "transformers": False,
        "qdrant-client": False,
        "llama-index": False
    }
    
    for dep in dependencies:
        try:
            if dep == "faiss-cpu":
                import faiss
            elif dep == "langchain-community":
                from langchain_community.vectorstores import FAISS
            elif dep == "langchain-huggingface":
                from langchain_huggingface import HuggingFaceEmbeddings
            elif dep == "transformers":
                import transformers
            elif dep == "qdrant-client":
                import qdrant_client
            elif dep == "llama-index":
                from llama_index.core.settings import Settings
            
            dependencies[dep] = True
            print(f"  ✅ {dep}")
        except ImportError:
            print(f"  ❌ {dep}")
    
    missing_deps = [dep for dep, available in dependencies.items() if not available]
    if missing_deps:
        print(f"\n⚠️ Missing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install " + " ".join(missing_deps))
        return False
    
    print("✅ All dependencies available")
    return True

def setup_faiss_index():
    """Setup FAISS index with InLegalBERT"""
    try:
        from setup_faiss_legal import setup_faiss_legal_index
        success = setup_faiss_legal_index()
        if success:
            print("✅ FAISS index setup completed")
        else:
            print("❌ FAISS index setup failed")
        return success
    except Exception as e:
        print(f"❌ Error setting up FAISS index: {e}")
        return False

def setup_qdrant_integration():
    """Setup Qdrant integration for multi-act coverage"""
    try:
        # Check if Qdrant is running
        import qdrant_client
        
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        client = qdrant_client.QdrantClient(url=qdrant_url)
        
        # Test connection
        collections = client.get_collections()
        print(f"✅ Qdrant connected: {len(collections.collections)} collections")
        
        # Check if legal collection exists
        collection_name = os.getenv("QDRANT_COLLECTION", "legal_knowledge")
        existing_collections = [col.name for col in collections.collections]
        
        if collection_name in existing_collections:
            print(f"✅ Legal collection '{collection_name}' exists")
        else:
            print(f"⚠️ Legal collection '{collection_name}' not found")
            print("Run the legal data integration script to create it")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Qdrant integration: {e}")
        return False

def test_hybrid_system():
    """Test the hybrid legal system"""
    try:
        # Import the hybrid system
        from backend.app.api.chat.engine.legal_hybrid import get_hybrid_legal_system
        
        # Initialize system
        hybrid_system = get_hybrid_legal_system()
        
        # Get stats
        stats = hybrid_system.get_legal_knowledge_stats()
        print(f"📊 Legal Knowledge Stats:")
        print(f"  FAISS Available: {stats.get('faiss_available', False)}")
        print(f"  Qdrant Available: {stats.get('qdrant_available', False)}")
        print(f"  Laws Raw Sections: {stats.get('laws_raw_sections', 0)}")
        print(f"  Legal Documents: {stats.get('legal_documents', 0)}")
        print(f"  System Type: {stats.get('system_type', 'unknown')}")
        
        # Test hybrid retrieval
        print("\n🔍 Testing hybrid retrieval...")
        context, source, metadata = hybrid_system.hybrid_retrieve("theft punishment", k=3)
        
        print(f"  Query: 'theft punishment'")
        print(f"  Source: {source}")
        print(f"  Context Length: {len(context)}")
        print(f"  Results: {len(metadata)}")
        
        if context:
            print(f"  Context Preview: {context[:100]}...")
        
        print("✅ Hybrid system test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing hybrid system: {e}")
        return False

def create_legal_config():
    """Create legal system configuration"""
    try:
        config = {
            "legal_system": {
                "enabled": True,
                "type": "hybrid",
                "faiss": {
                    "enabled": True,
                    "model": "law-ai/InLegalBERT",
                    "index_path": "legal_data/faiss_index/ipc_embed_db_inlegalbert",
                    "description": "Deep IPC knowledge with case law"
                },
                "qdrant": {
                    "enabled": True,
                    "collection": "legal_knowledge",
                    "description": "Broad multi-act coverage"
                },
                "hybrid_retrieval": {
                    "enabled": True,
                    "score_threshold": 0.65,
                    "top_k": 5,
                    "description": "Combines FAISS and Qdrant for optimal results"
                }
            }
        }
        
        config_path = Path("legal_data/legal_system_config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Legal system configuration saved to {config_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating legal config: {e}")
        return False

def main():
    """Main execution function"""
    success = setup_hybrid_legal_system()
    
    if success:
        print("\n🎉 Hybrid Legal System is ready!")
        print("\n📋 Next Steps:")
        print("1. Start the RAG-SaaS backend server")
        print("2. Test the legal chat endpoint: /api/legal")
        print("3. Use the legal knowledge system for legal queries")
        print("\n🔗 Available Endpoints:")
        print("  POST /api/legal - Legal chat with hybrid knowledge")
        print("  GET /api/legal/legal/stats - Legal knowledge statistics")
        print("  POST /api/legal/legal/search - Search legal sections")
        print("  POST /api/legal/legal/enable - Enable legal system")
        print("  POST /api/legal/legal/disable - Disable legal system")
    else:
        print("\n❌ Hybrid Legal System setup failed.")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
