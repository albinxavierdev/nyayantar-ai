#!/usr/bin/env python3
"""
Legal Vector Database Integration Script for RAG-SaaS
Integrates legal embeddings with Qdrant vector database
"""

import json
import os
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.schema import Document

class LegalVectorDB:
    def __init__(self, 
                 embeddings_path: str = "legal_data/embeddings",
                 qdrant_url: str = "http://localhost:6333",
                 collection_name: str = "legal_knowledge"):
        # Get the script directory and resolve paths relative to project root
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        self.embeddings_path = project_root / embeddings_path
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        
        # Initialize Qdrant client
        self.client = QdrantClient(url=qdrant_url)
        
        # Initialize LlamaIndex Qdrant vector store
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=collection_name
        )
    
    def load_embeddings(self, filename: str) -> Dict[str, Any]:
        """Load embeddings from file"""
        print(f"📖 Loading embeddings from {filename}...")
        
        with open(self.embeddings_path / filename, "r", encoding="utf-8") as f:
            embeddings_data = json.load(f)
        
        print(f"✅ Loaded {embeddings_data['total_documents']} embeddings")
        return embeddings_data
    
    def create_collection(self, embedding_dimension: int):
        """Create Qdrant collection for legal knowledge"""
        print(f"🗄️ Creating Qdrant collection: {self.collection_name}")
        
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            existing_collections = [col.name for col in collections.collections]
            
            if self.collection_name in existing_collections:
                print(f"  ⚠️ Collection {self.collection_name} already exists")
                # Delete existing collection
                self.client.delete_collection(self.collection_name)
                print(f"  🗑️ Deleted existing collection")
            
            # Create new collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=embedding_dimension,
                    distance=Distance.COSINE
                )
            )
            print(f"  ✅ Created collection with {embedding_dimension}D vectors")
            
        except Exception as e:
            print(f"❌ Error creating collection: {e}")
            raise
    
    def upload_embeddings_to_qdrant(self, embeddings_data: Dict[str, Any]):
        """Upload embeddings to Qdrant"""
        print("📤 Uploading embeddings to Qdrant...")
        
        embeddings = np.array(embeddings_data["embeddings"])
        document_ids = embeddings_data["document_ids"]
        metadata = embeddings_data["metadata"]
        
        # Prepare points for upload
        points = []
        for i, (embedding, doc_id, meta) in enumerate(zip(embeddings, document_ids, metadata)):
            point = PointStruct(
                id=i,
                vector=embedding.tolist(),
                payload={
                    "document_id": doc_id,
                    "text": meta.get("content", ""),
                    "act_type": meta.get("act_type", ""),
                    "section_number": meta.get("section_number", ""),
                    "title": meta.get("title", ""),
                    "chapter": meta.get("chapter", ""),
                    "case_references": meta.get("case_references", []),
                    "legal_keywords": meta.get("legal_keywords", []),
                    "legal_concepts": meta.get("legal_concepts", []),
                    "source": meta.get("source", ""),
                    "last_updated": meta.get("last_updated", ""),
                    "document_type": meta.get("document_type", "legal_section")
                }
            )
            points.append(point)
        
        # Upload points in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
            print(f"  📤 Uploaded batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")
        
        print(f"✅ Uploaded {len(points)} legal documents to Qdrant")
    
    def test_retrieval(self, query: str = "theft punishment", top_k: int = 5):
        """Test retrieval from Qdrant"""
        print(f"🔍 Testing retrieval with query: '{query}'")
        
        # Generate query embedding (using sentence-transformers for testing)
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode([query])[0].tolist()
        
        # Search in Qdrant
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k
        )
        
        print(f"📋 Retrieved {len(search_results)} results:")
        for i, result in enumerate(search_results):
            payload = result.payload
            print(f"  {i+1}. {payload['title']} (Score: {result.score:.4f})")
            print(f"     Act: {payload['act_type']} Section: {payload['section_number']}")
            print(f"     Keywords: {', '.join(payload.get('legal_keywords', [])[:5])}")
            print()
        
        return search_results
    
    def test_metadata_filtering(self, act_type: str = "IPC", top_k: int = 3):
        """Test metadata filtering"""
        print(f"🔍 Testing metadata filtering for act_type: {act_type}")
        
        # Generate query embedding
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode(["legal section"])[0].tolist()
        
        # Search with filter
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="act_type",
                        match=models.MatchValue(value=act_type)
                    )
                ]
            ),
            limit=top_k
        )
        
        print(f"📋 Retrieved {len(search_results)} {act_type} sections:")
        for i, result in enumerate(search_results):
            payload = result.payload
            print(f"  {i+1}. Section {payload['section_number']}: {payload['title']}")
        
        return search_results
    
    def get_collection_info(self):
        """Get collection information"""
        print(f"📊 Collection Information:")
        
        try:
            collection_info = self.client.get_collection(self.collection_name)
            print(f"  Name: {collection_info.config.params.vectors.size}")
            print(f"  Vector Size: {collection_info.config.params.vectors.size}")
            print(f"  Distance: {collection_info.config.params.vectors.distance}")
            print(f"  Points Count: {collection_info.points_count}")
            
            return collection_info
        except Exception as e:
            print(f"❌ Error getting collection info: {e}")
            return None
    
    def integrate_legal_knowledge(self, embeddings_filename: str = "sentence_transformers_embeddings.json"):
        """Integrate legal knowledge with Qdrant"""
        print("🚀 Starting legal knowledge integration...")
        
        # Load embeddings
        embeddings_data = self.load_embeddings(embeddings_filename)
        
        # Create collection
        self.create_collection(embeddings_data["embedding_dimension"])
        
        # Upload embeddings
        self.upload_embeddings_to_qdrant(embeddings_data)
        
        # Test retrieval
        print("\n🧪 Testing retrieval functionality...")
        self.test_retrieval("theft punishment")
        self.test_retrieval("bail application")
        self.test_retrieval("criminal procedure")
        
        # Test metadata filtering
        print("\n🧪 Testing metadata filtering...")
        self.test_metadata_filtering("IPC")
        self.test_metadata_filtering("CRPC")
        
        # Get collection info
        print("\n📊 Final collection status:")
        self.get_collection_info()
        
        print("\n✅ Legal knowledge integration completed successfully!")

def main():
    """Main execution function"""
    vector_db = LegalVectorDB()
    vector_db.integrate_legal_knowledge()

if __name__ == "__main__":
    main()
