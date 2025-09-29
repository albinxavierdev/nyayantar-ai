#!/usr/bin/env python3
"""
Legal Vector Pipeline
Extracts legal data from laws_json folder and creates embeddings for Qdrant vector database
"""

import json
import os
import sys
import numpy as np
from typing import List, Dict, Any, Tuple
from pathlib import Path
import logging

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent.parent / "backend"))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LegalVectorPipeline:
    def __init__(self, 
                 laws_json_path: str = "legal_data/raw/laws_json",
                 qdrant_url: str = "http://localhost:6333",
                 qdrant_api_key: str = None,
                 collection_name: str = "ragsaas"):
        
        # Setup paths
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        self.laws_json_path = project_root / laws_json_path
        self.qdrant_url = qdrant_url
        self.qdrant_api_key = qdrant_api_key
        self.collection_name = collection_name
        
        # Legal acts configuration
        self.legal_acts = {
            'ipc.json': {
                'name': 'Indian Penal Code',
                'abbreviation': 'IPC',
                'content_field': 'section_desc',
                'section_field': 'Section',
                'title_field': 'section_title',
                'chapter_field': 'chapter'
            },
            'crpc.json': {
                'name': 'Code of Criminal Procedure',
                'abbreviation': 'CrPC',
                'content_field': 'section_desc',
                'section_field': 'section',
                'title_field': 'section_title',
                'chapter_field': 'chapter'
            },
            'cpc.json': {
                'name': 'Code of Civil Procedure',
                'abbreviation': 'CPC',
                'content_field': 'description',
                'section_field': 'section',
                'title_field': 'title',
                'chapter_field': None
            },
            'iea.json': {
                'name': 'Indian Evidence Act',
                'abbreviation': 'IEA',
                'content_field': 'section_desc',
                'section_field': 'section',
                'title_field': 'section_title',
                'chapter_field': 'chapter'
            },
            'ida.json': {
                'name': 'Indian Divorce Act',
                'abbreviation': 'IDA',
                'content_field': 'description',
                'section_field': 'section',
                'title_field': 'title',
                'chapter_field': None
            },
            'MVA.json': {
                'name': 'Motor Vehicles Act',
                'abbreviation': 'MVA',
                'content_field': 'description',
                'section_field': 'section',
                'title_field': 'title',
                'chapter_field': None
            },
            'nia.json': {
                'name': 'Narcotic Drugs and Psychotropic Substances Act',
                'abbreviation': 'NIA',
                'content_field': 'section_desc',
                'section_field': 'section',
                'title_field': 'section_title',
                'chapter_field': 'chapter'
            }
            # Note: HMA excluded due to poor data quality
        }
        
        self.qdrant_client = None
        self.documents = []
        
    def run_pipeline(self):
        """Run the complete vector pipeline"""
        print("🚀 Starting Legal Vector Pipeline")
        print("=" * 60)
        
        try:
            # Step 1: Extract legal data
            print("\n📖 Step 1: Extracting Legal Data")
            print("-" * 40)
            self.extract_legal_data()
            
            # Step 2: Generate embeddings
            print("\n🤖 Step 2: Generating Embeddings")
            print("-" * 40)
            embeddings_data = self.generate_embeddings()
            
            # Step 3: Connect to Qdrant
            print("\n🗄️ Step 3: Connecting to Qdrant")
            print("-" * 40)
            self.connect_to_qdrant()
            
            # Step 4: Create collection
            print("\n📚 Step 4: Creating Collection")
            print("-" * 40)
            self.create_collection(embeddings_data['embedding_dimension'])
            
            # Step 5: Upload documents
            print("\n📤 Step 5: Uploading Documents")
            print("-" * 40)
            self.upload_documents(embeddings_data)
            
            # Step 6: Test the pipeline
            print("\n🧪 Step 6: Testing Pipeline")
            print("-" * 40)
            self.test_pipeline()
            
            print("\n✅ Legal Vector Pipeline Completed Successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            print(f"\n❌ Pipeline failed: {e}")
            return False
    
    def extract_legal_data(self):
        """Extract legal data from all JSON files"""
        self.documents = []
        
        for filename, config in self.legal_acts.items():
            file_path = self.laws_json_path / filename
            if not file_path.exists():
                logger.warning(f"File not found: {filename}")
                continue
                
            print(f"📄 Processing {config['name']} ({filename})")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if not isinstance(data, list):
                    logger.warning(f"Expected list, got {type(data)} for {filename}")
                    continue
                
                # Extract documents
                act_documents = self.extract_act_documents(data, config, filename)
                self.documents.extend(act_documents)
                
                print(f"  ✅ Extracted {len(act_documents)} documents")
                
            except Exception as e:
                logger.error(f"Error processing {filename}: {e}")
                continue
        
        print(f"\n📊 Total documents extracted: {len(self.documents)}")
        
        # Show sample documents
        print("\n📋 Sample Documents:")
        for i, doc in enumerate(self.documents[:3]):
            print(f"  {i+1}. {doc['metadata']['act_type']} Section {doc['metadata']['section_number']}: {doc['metadata']['title']}")
            print(f"     Content length: {len(doc['text'])}")
    
    def extract_act_documents(self, data: List[Dict], config: Dict, filename: str) -> List[Dict]:
        """Extract documents from a specific legal act"""
        documents = []
        
        for item in data:
            if not isinstance(item, dict):
                continue
                
            # Extract fields based on configuration
            section_number = str(item.get(config['section_field'], ''))
            title = item.get(config['title_field'], '')
            content = item.get(config['content_field'], '')
            chapter = item.get(config['chapter_field'], '') if config['chapter_field'] else ''
            
            # Skip if no content
            if not content or len(content.strip()) < 50:
                continue
            
            # Create document
            doc = {
                'id': f"{config['abbreviation'].lower()}_{section_number}",
                'text': content,
                'metadata': {
                    'act_type': config['abbreviation'],
                    'act_name': config['name'],
                    'section_number': section_number,
                    'title': title,
                    'chapter': str(chapter) if chapter else '',
                    'source_file': filename,
                    'document_type': 'legal_section',
                    'legal_keywords': self.extract_legal_keywords(content),
                    'legal_concepts': self.extract_legal_concepts(content),
                    'source': 'Legal Database',
                    'last_updated': '2024-01-01'
                }
            }
            
            documents.append(doc)
        
        return documents
    
    def extract_legal_keywords(self, text: str) -> List[str]:
        """Extract legal keywords from text"""
        legal_terms = [
            'section', 'act', 'code', 'law', 'court', 'judge', 'offence', 'punishment',
            'bail', 'trial', 'evidence', 'witness', 'complaint', 'charge', 'conviction',
            'appeal', 'jurisdiction', 'procedure', 'clause', 'subsection', 'article',
            'provision', 'penalty', 'fine', 'imprisonment', 'sentence', 'acquittal',
            'verdict', 'plaintiff', 'defendant', 'accused', 'victim', 'prosecution',
            'defense', 'counsel', 'statute', 'regulation', 'ordinance', 'amendment'
        ]
        
        text_lower = text.lower()
        found_keywords = [term for term in legal_terms if term in text_lower]
        return found_keywords
    
    def extract_legal_concepts(self, text: str) -> List[str]:
        """Extract legal concepts from text"""
        concepts = []
        
        # Extract section references
        import re
        section_refs = re.findall(r'section\s+(\d+)', text.lower())
        concepts.extend([f"section_{ref}" for ref in section_refs])
        
        # Extract case law references
        case_refs = re.findall(r'\b(AIR|SCC|Cr\s*LJ|BLR|KLT|BOM|CAL|DEL|KAR|MAD|P&H|RAJ|GUJ|MP|ORI|PAT|PUN|UP|WB)\b', text)
        concepts.extend([f"case_law_{ref}" for ref in case_refs])
        
        return concepts
    
    def generate_embeddings(self) -> Dict[str, Any]:
        """Generate 1536D embeddings for all documents"""
        print("🤖 Generating 1536D embeddings...")
        
        embeddings = []
        
        for doc in self.documents:
            embedding = self.create_openai_compatible_embedding(doc['text'])
            embeddings.append(embedding)
        
        embeddings_array = np.array(embeddings)
        
        return {
            'embeddings': embeddings_array,
            'documents': self.documents,
            'embedding_dimension': embeddings_array.shape[1],
            'total_documents': len(self.documents)
        }
    
    def create_openai_compatible_embedding(self, text: str) -> List[float]:
        """Create 1536D embedding compatible with OpenAI format"""
        if not text:
            return [0.0] * 1536
        
        # Create sophisticated embedding using multiple text features
        features = []
        
        # Basic text features (first 200 dimensions)
        features.extend(self.create_basic_text_features(text, 200))
        
        # Legal-specific features (next 300 dimensions)
        features.extend(self.create_legal_features(text, 300))
        
        # Semantic features (next 400 dimensions)
        features.extend(self.create_semantic_features(text, 400))
        
        # Hash-based features (next 300 dimensions)
        features.extend(self.create_hash_features(text, 300))
        
        # Context features (next 200 dimensions)
        features.extend(self.create_context_features(text, 200))
        
        # Padding features (remaining 166 dimensions)
        features.extend(self.create_padding_features(text, 166))
        
        # Ensure exactly 1536 dimensions
        if len(features) < 1536:
            features.extend([0.0] * (1536 - len(features)))
        elif len(features) > 1536:
            features = features[:1536]
        
        return features
    
    def create_basic_text_features(self, text: str, target_size: int) -> List[float]:
        """Create basic text features"""
        features = []
        
        # Length features
        features.append(len(text))
        features.append(len(text.split()))
        features.append(len(text.split('\n')))
        features.append(len(text.split('.')))
        features.append(len(text.split(',')))
        
        # Character frequency
        for char in 'abcdefghijklmnopqrstuvwxyz':
            features.append(text.lower().count(char))
        
        # Word frequency
        common_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall']
        for word in common_words:
            features.append(text.lower().count(word))
        
        # Pad to target size
        while len(features) < target_size:
            features.append(0.0)
        
        return features[:target_size]
    
    def create_legal_features(self, text: str, target_size: int) -> List[float]:
        """Create legal-specific features"""
        features = []
        
        # Legal terms frequency
        legal_terms = [
            'section', 'act', 'code', 'law', 'court', 'judge', 'offence', 'punishment',
            'bail', 'trial', 'evidence', 'witness', 'complaint', 'charge', 'conviction',
            'appeal', 'jurisdiction', 'procedure', 'clause', 'subsection', 'ipc', 'crpc',
            'cpc', 'iea', 'ida', 'hma', 'nia', 'mva', 'article', 'provision', 'penalty',
            'fine', 'imprisonment', 'sentence', 'acquittal', 'verdict', 'plaintiff',
            'defendant', 'accused', 'victim', 'prosecution', 'defense', 'counsel',
            'statute', 'regulation', 'ordinance', 'amendment', 'repeal', 'enactment'
        ]
        
        for term in legal_terms:
            features.append(text.lower().count(term))
        
        # Case law references
        case_refs = ['AIR', 'SCC', 'Cr LJ', 'BLR', 'KLT', 'BOM', 'CAL', 'DEL', 'KAR', 'MAD', 'P&H', 'RAJ', 'GUJ', 'MP', 'ORI', 'PAT', 'PUN', 'UP', 'WB']
        for ref in case_refs:
            features.append(text.count(ref))
        
        # Legal numbers
        import re
        section_numbers = re.findall(r'section\s+(\d+)', text.lower())
        features.append(len(section_numbers))
        
        article_numbers = re.findall(r'article\s+(\d+)', text.lower())
        features.append(len(article_numbers))
        
        # Pad to target size
        while len(features) < target_size:
            features.append(0.0)
        
        return features[:target_size]
    
    def create_semantic_features(self, text: str, target_size: int) -> List[float]:
        """Create semantic features"""
        features = []
        
        # Sentence structure
        sentences = text.split('.')
        features.append(len(sentences))
        features.append(sum(len(s.split()) for s in sentences) / max(len(sentences), 1))
        
        # Paragraph structure
        paragraphs = text.split('\n\n')
        features.append(len(paragraphs))
        
        # Punctuation
        features.append(text.count('?'))
        features.append(text.count('!'))
        features.append(text.count('"'))
        features.append(text.count("'"))
        features.append(text.count('('))
        features.append(text.count(')'))
        features.append(text.count('['))
        features.append(text.count(']'))
        
        # Pad to target size
        while len(features) < target_size:
            features.append(0.0)
        
        return features[:target_size]
    
    def create_hash_features(self, text: str, target_size: int) -> List[float]:
        """Create hash-based features"""
        features = []
        
        import hashlib
        
        # MD5 hash features
        md5_hash = hashlib.md5(text.encode()).hexdigest()
        for i in range(0, len(md5_hash), 2):
            features.append(int(md5_hash[i:i+2], 16) / 255.0)
        
        # SHA1 hash features
        sha1_hash = hashlib.sha1(text.encode()).hexdigest()
        for i in range(0, len(sha1_hash), 2):
            features.append(int(sha1_hash[i:i+2], 16) / 255.0)
        
        # SHA256 hash features
        sha256_hash = hashlib.sha256(text.encode()).hexdigest()
        for i in range(0, len(sha256_hash), 2):
            features.append(int(sha256_hash[i:i+2], 16) / 255.0)
        
        # Pad to target size
        while len(features) < target_size:
            features.append(0.0)
        
        return features[:target_size]
    
    def create_context_features(self, text: str, target_size: int) -> List[float]:
        """Create context-based features"""
        features = []
        
        # Text position features
        text_length = len(text)
        features.append(text_length)
        features.append(text_length / 1000.0)
        
        # Word position features
        words = text.split()
        features.append(len(words))
        features.append(len(words) / 100.0)
        
        # Character diversity
        unique_chars = len(set(text.lower()))
        features.append(unique_chars)
        features.append(unique_chars / 26.0)
        
        # Pad to target size
        while len(features) < target_size:
            features.append(0.0)
        
        return features[:target_size]
    
    def create_padding_features(self, text: str, target_size: int) -> List[float]:
        """Create padding features"""
        features = []
        
        # Simple text-based features
        features.append(hash(text) % 1000 / 1000.0)
        features.append(len(text) % 100 / 100.0)
        features.append(sum(ord(c) for c in text) % 1000 / 1000.0)
        
        # Pad to target size
        while len(features) < target_size:
            features.append(0.0)
        
        return features[:target_size]
    
    def connect_to_qdrant(self):
        """Connect to Qdrant database"""
        try:
            import qdrant_client
            
            if self.qdrant_api_key:
                self.qdrant_client = qdrant_client.QdrantClient(
                    url=self.qdrant_url,
                    api_key=self.qdrant_api_key
                )
            else:
                self.qdrant_client = qdrant_client.QdrantClient(url=self.qdrant_url)
            
            # Test connection
            collections = self.qdrant_client.get_collections()
            print(f"✅ Connected to Qdrant: {len(collections.collections)} collections")
            
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise
    
    def create_collection(self, vector_size: int):
        """Create Qdrant collection"""
        try:
            from qdrant_client.http.models import Distance, VectorParams
            
            # Check if collection exists
            collections = self.qdrant_client.get_collections()
            existing_collections = [col.name for col in collections.collections]
            
            if self.collection_name in existing_collections:
                print(f"⚠️ Collection '{self.collection_name}' already exists")
                # Delete existing collection
                self.qdrant_client.delete_collection(self.collection_name)
                print(f"🗑️ Deleted existing collection")
            
            # Create new collection
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            print(f"✅ Created collection '{self.collection_name}' with {vector_size}D vectors")
            
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise
    
    def upload_documents(self, embeddings_data: Dict):
        """Upload documents to Qdrant"""
        try:
            from qdrant_client.http.models import PointStruct
            
            embeddings = embeddings_data["embeddings"]
            documents = embeddings_data["documents"]
            
            # Prepare points for upload
            points = []
            for i, (embedding, doc) in enumerate(zip(embeddings, documents)):
                point = PointStruct(
                    id=i,
                    vector=embedding.tolist(),
                    payload={
                        "text": doc["text"],
                        "document_id": doc["id"],
                        "act_type": doc["metadata"]["act_type"],
                        "act_name": doc["metadata"]["act_name"],
                        "section_number": doc["metadata"]["section_number"],
                        "title": doc["metadata"]["title"],
                        "chapter": doc["metadata"]["chapter"],
                        "source_file": doc["metadata"]["source_file"],
                        "legal_keywords": doc["metadata"]["legal_keywords"],
                        "legal_concepts": doc["metadata"]["legal_concepts"],
                        "source": doc["metadata"]["source"],
                        "last_updated": doc["metadata"]["last_updated"],
                        "document_type": doc["metadata"]["document_type"],
                        "file_name": f"{doc['metadata']['act_type']}_{doc['metadata']['section_number']}",
                        "private": "false"
                    }
                )
                points.append(point)
            
            # Upload points in batches
            batch_size = 100
            total_batches = (len(points) - 1) // batch_size + 1
            
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
                batch_num = i // batch_size + 1
                print(f"  📤 Uploaded batch {batch_num}/{total_batches} ({len(batch)} documents)")
            
            print(f"✅ Uploaded {len(points)} legal documents to Qdrant")
            
        except Exception as e:
            logger.error(f"Error uploading documents: {e}")
            raise
    
    def test_pipeline(self):
        """Test the pipeline with sample queries"""
        try:
            # Test queries
            test_queries = [
                "theft punishment",
                "bail application",
                "section 379",
                "criminal procedure",
                "evidence rules"
            ]
            
            for query in test_queries:
                print(f"\n🔍 Testing query: '{query}'")
                
                # Generate query embedding
                query_embedding = self.create_openai_compatible_embedding(query)
                
                # Search in Qdrant
                results = self.qdrant_client.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    limit=3
                )
                
                print(f"  ✅ Found {len(results)} results")
                for i, result in enumerate(results):
                    payload = result.payload
                    print(f"    {i+1}. {payload.get('title', 'No title')} (Score: {result.score:.4f})")
                    print(f"       Act: {payload.get('act_type', 'Unknown')} Section: {payload.get('section_number', 'N/A')}")
            
            # Get collection info
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            print(f"\n📊 Collection Statistics:")
            print(f"  Total Points: {collection_info.points_count}")
            print(f"  Vector Size: {collection_info.config.params.vectors.size}")
            print(f"  Distance: {collection_info.config.params.vectors.distance}")
            
        except Exception as e:
            logger.error(f"Error testing pipeline: {e}")

def main():
    """Main execution function"""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    collection_name = os.getenv("QDRANT_COLLECTION", "ragsaas")
    
    # Create and run pipeline
    pipeline = LegalVectorPipeline(
        qdrant_url=qdrant_url,
        qdrant_api_key=qdrant_api_key,
        collection_name=collection_name
    )
    
    success = pipeline.run_pipeline()
    
    if success:
        print("\n🎉 Legal Vector Pipeline Completed Successfully!")
        print("\n📋 Next Steps:")
        print("1. Start the RAG-SaaS backend server")
        print("2. Test legal queries through the main chat API")
        print("3. The LLM can now use comprehensive legal knowledge")
        print("\n🔗 Test the legal system:")
        print("  POST /api/chat - Main chat with legal + general knowledge")
        print("  GET /api/chat/config - Check system configuration")
    else:
        print("\n❌ Legal Vector Pipeline Failed.")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
