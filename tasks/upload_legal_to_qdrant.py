#!/usr/bin/env python3
"""
Upload Legal Data to Qdrant Vector Database
Embeds legal knowledge and stores it in Qdrant for LLM usage
"""

import json
import os
import sys
import numpy as np
from typing import List, Dict, Any
from pathlib import Path

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent.parent / "backend"))

def upload_legal_to_qdrant():
    """Upload legal data to Qdrant vector database"""
    print("🚀 Uploading Legal Data to Qdrant Vector Database")
    print("=" * 60)
    
    try:
        # Step 1: Load legal data
        print("\n📖 Step 1: Loading Legal Data")
        print("-" * 40)
        legal_data = load_legal_data()
        if not legal_data:
            print("❌ No legal data found")
            return False
        
        print(f"✅ Loaded {len(legal_data)} legal documents")
        
        # Step 2: Generate embeddings
        print("\n🤖 Step 2: Generating Embeddings")
        print("-" * 40)
        embeddings_data = generate_embeddings(legal_data)
        print(f"✅ Generated embeddings: {embeddings_data['embedding_dimension']}D vectors")
        
        # Step 3: Connect to Qdrant
        print("\n🗄️ Step 3: Connecting to Qdrant")
        print("-" * 40)
        qdrant_client = connect_to_qdrant()
        if not qdrant_client:
            print("❌ Failed to connect to Qdrant")
            return False
        
        # Step 4: Create legal collection
        print("\n📚 Step 4: Creating Legal Collection")
        print("-" * 40)
        collection_name = "legal_knowledge"
        create_legal_collection(qdrant_client, collection_name, embeddings_data['embedding_dimension'])
        
        # Step 5: Upload legal data
        print("\n📤 Step 5: Uploading Legal Data")
        print("-" * 40)
        upload_legal_documents(qdrant_client, collection_name, legal_data, embeddings_data)
        
        # Step 6: Test the upload
        print("\n🧪 Step 6: Testing Upload")
        print("-" * 40)
        test_legal_search(qdrant_client, collection_name)
        
        print("\n✅ Legal data successfully uploaded to Qdrant!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error uploading legal data: {e}")
        return False

def load_legal_data() -> List[Dict[str, Any]]:
    """Load legal data from processed files"""
    # Get the script directory and resolve paths relative to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    legal_data_path = project_root / "legal_data/converted/all_legal_documents.json"
    
    if not legal_data_path.exists():
        print(f"❌ Legal data file not found: {legal_data_path}")
        return []
    
    with open(legal_data_path, "r", encoding="utf-8") as f:
        legal_data = json.load(f)
    
    print(f"📄 Loaded {len(legal_data)} legal documents")
    return legal_data

def generate_embeddings(legal_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate embeddings for legal data using simple text features"""
    print("🤖 Generating simple text-based embeddings...")
    
    embeddings = []
    documents = []
    
    for doc in legal_data:
        # Create simple embedding based on text features
        text = doc.get("text", "")
        embedding = create_text_features(text)
        embeddings.append(embedding)
        documents.append(doc)
    
    # Convert to numpy array
    embeddings_array = np.array(embeddings)
    
    return {
        "embeddings": embeddings_array,
        "documents": documents,
        "embedding_dimension": embeddings_array.shape[1],
        "total_documents": len(documents)
    }

def create_text_features(text: str) -> List[float]:
    """Create simple text features for embedding"""
    if not text:
        return [0.0] * 50  # Return zero vector for empty text
    
    # Basic text features
    features = []
    
    # Length features
    features.append(len(text))
    features.append(len(text.split()))
    features.append(len(text.split('\n')))
    
    # Character frequency features
    features.append(text.count(' '))
    features.append(text.count('\n'))
    features.append(text.count('.'))
    features.append(text.count(','))
    features.append(text.count(';'))
    features.append(text.count(':'))
    
    # Legal-specific features
    legal_terms = [
        'section', 'act', 'code', 'law', 'court', 'judge', 'offence', 'punishment',
        'bail', 'trial', 'evidence', 'witness', 'complaint', 'charge', 'conviction',
        'appeal', 'jurisdiction', 'procedure', 'clause', 'subsection', 'ipc', 'crpc',
        'cpc', 'iea', 'ida', 'hma', 'nia', 'mva'
    ]
    
    for term in legal_terms:
        features.append(text.lower().count(term))
    
    # Case law references
    features.append(text.count('AIR'))
    features.append(text.count('SCC'))
    features.append(text.count('Cr LJ'))
    
    # Text hash features (for uniqueness)
    import hashlib
    text_hash = hashlib.md5(text.encode()).hexdigest()
    hash_features = [int(text_hash[i:i+2], 16) / 255.0 for i in range(0, 8, 2)]
    features.extend(hash_features)
    
    # Pad or truncate to fixed size
    target_size = 50
    if len(features) < target_size:
        features.extend([0.0] * (target_size - len(features)))
    elif len(features) > target_size:
        features = features[:target_size]
    
    return features

def connect_to_qdrant():
    """Connect to Qdrant database"""
    try:
        import qdrant_client
        from dotenv import load_dotenv
        load_dotenv()
        
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        if qdrant_api_key:
            client = qdrant_client.QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key
            )
        else:
            client = qdrant_client.QdrantClient(url=qdrant_url)
        
        # Test connection
        collections = client.get_collections()
        print(f"✅ Connected to Qdrant: {len(collections.collections)} collections")
        return client
        
    except Exception as e:
        print(f"❌ Failed to connect to Qdrant: {e}")
        return None

def create_legal_collection(client, collection_name: str, vector_size: int):
    """Create legal knowledge collection in Qdrant"""
    try:
        from qdrant_client.http.models import Distance, VectorParams
        
        # Check if collection exists
        collections = client.get_collections()
        existing_collections = [col.name for col in collections.collections]
        
        if collection_name in existing_collections:
            print(f"⚠️ Collection '{collection_name}' already exists")
            # Delete existing collection
            client.delete_collection(collection_name)
            print(f"🗑️ Deleted existing collection")
        
        # Create new collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )
        print(f"✅ Created collection '{collection_name}' with {vector_size}D vectors")
        
    except Exception as e:
        print(f"❌ Error creating collection: {e}")
        raise

def upload_legal_documents(client, collection_name: str, legal_data: List[Dict], embeddings_data: Dict):
    """Upload legal documents to Qdrant"""
    try:
        from qdrant_client.http.models import PointStruct
        
        embeddings = embeddings_data["embeddings"]
        documents = embeddings_data["documents"]
        
        # Prepare points for upload
        points = []
        for i, (embedding, doc) in enumerate(zip(embeddings, documents)):
            metadata = doc.get("metadata", {})
            
            point = PointStruct(
                id=i,
                vector=embedding.tolist(),
                payload={
                    "text": doc.get("text", ""),
                    "document_id": doc.get("id_", f"legal_doc_{i}"),
                    "act_type": metadata.get("act_type", ""),
                    "section_number": metadata.get("section_number", ""),
                    "title": metadata.get("title", ""),
                    "chapter": metadata.get("chapter", ""),
                    "case_references": metadata.get("case_references", []),
                    "legal_keywords": metadata.get("legal_keywords", []),
                    "legal_concepts": metadata.get("legal_concepts", []),
                    "source": metadata.get("source", ""),
                    "last_updated": metadata.get("last_updated", ""),
                    "document_type": metadata.get("document_type", "legal_section")
                }
            )
            points.append(point)
        
        # Upload points in batches
        batch_size = 100
        total_batches = (len(points) - 1) // batch_size + 1
        
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            client.upsert(
                collection_name=collection_name,
                points=batch
            )
            batch_num = i // batch_size + 1
            print(f"  📤 Uploaded batch {batch_num}/{total_batches} ({len(batch)} documents)")
        
        print(f"✅ Uploaded {len(points)} legal documents to Qdrant")
        
    except Exception as e:
        print(f"❌ Error uploading documents: {e}")
        raise

def test_legal_search(client, collection_name: str):
    """Test legal search functionality"""
    try:
        # Test queries
        test_queries = [
            "theft punishment",
            "bail application",
            "section 379",
            "criminal procedure"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            
            # Generate query embedding
            query_embedding = create_text_features(query)
            
            # Search in Qdrant
            results = client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=3
            )
            
            print(f"  ✅ Found {len(results)} results")
            for i, result in enumerate(results):
                payload = result.payload
                print(f"    {i+1}. {payload.get('title', 'No title')} (Score: {result.score:.4f})")
                print(f"       Act: {payload.get('act_type', 'Unknown')} Section: {payload.get('section_number', 'N/A')}")
        
        # Get collection info
        collection_info = client.get_collection(collection_name)
        print(f"\n📊 Collection Statistics:")
        print(f"  Total Points: {collection_info.points_count}")
        print(f"  Vector Size: {collection_info.config.params.vectors.size}")
        print(f"  Distance: {collection_info.config.params.vectors.distance}")
        
    except Exception as e:
        print(f"❌ Error testing search: {e}")

def main():
    """Main execution function"""
    success = upload_legal_to_qdrant()
    
    if success:
        print("\n🎉 Legal Data Successfully Uploaded to Qdrant!")
        print("\n📋 Next Steps:")
        print("1. Start the RAG-SaaS backend server")
        print("2. Test legal queries through the API")
        print("3. The LLM can now use legal knowledge for responses")
        print("\n🔗 Test the legal system:")
        print("  POST /api/legal - Legal chat with hybrid knowledge")
        print("  GET /api/legal/legal/stats - Legal knowledge statistics")
    else:
        print("\n❌ Failed to upload legal data to Qdrant.")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
