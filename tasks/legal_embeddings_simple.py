#!/usr/bin/env python3
"""
Simple Legal Embeddings Script for RAG-SaaS
Uses only basic dependencies - no heavy ML packages
"""

import json
import os
import hashlib
import numpy as np
from typing import List, Dict, Any
from pathlib import Path

class SimpleLegalEmbeddingsGenerator:
    def __init__(self, converted_data_path: str = "legal_data/converted"):
        # Get the script directory and resolve paths relative to project root
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        self.converted_data_path = project_root / converted_data_path
        self.embeddings_path = project_root / "legal_data/embeddings"
        self.embeddings_path.mkdir(exist_ok=True)
    
    def load_converted_documents(self) -> List[Dict[str, Any]]:
        """Load all converted legal documents"""
        print("📖 Loading converted legal documents...")
        
        documents = []
        
        # Load combined documents
        combined_file = self.converted_data_path / "all_legal_documents.json"
        if combined_file.exists():
            with open(combined_file, "r", encoding="utf-8") as f:
                doc_data = json.load(f)
            documents = doc_data
        
        print(f"✅ Loaded {len(documents)} legal documents")
        return documents
    
    def create_simple_embeddings(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create simple embeddings using text hashing and basic features"""
        print("🤖 Creating simple embeddings...")
        
        embeddings = []
        document_ids = []
        metadata = []
        
        for doc in documents:
            # Create simple embedding based on text features
            text = doc["text"]
            
            # Simple text-based features
            embedding = self.create_text_features(text)
            embeddings.append(embedding)
            document_ids.append(doc["id_"])
            metadata.append(doc["metadata"])
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings)
        
        # Create embeddings data
        embeddings_data = {
            "model_name": "simple-text-features",
            "model_type": "basic-features",
            "embedding_dimension": embeddings_array.shape[1],
            "total_documents": len(documents),
            "embeddings": embeddings_array.tolist(),
            "document_ids": document_ids,
            "metadata": metadata
        }
        
        return embeddings_data
    
    def create_text_features(self, text: str) -> List[float]:
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
            'appeal', 'jurisdiction', 'procedure', 'clause', 'subsection'
        ]
        
        for term in legal_terms:
            features.append(text.lower().count(term))
        
        # Case law references
        features.append(text.count('AIR'))
        features.append(text.count('SCC'))
        features.append(text.count('Cr LJ'))
        
        # Text hash features (for uniqueness)
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
    
    def save_embeddings(self, embeddings_data: Dict[str, Any], filename: str):
        """Save embeddings to file"""
        print(f"💾 Saving embeddings to {filename}...")
        
        # Save embeddings data
        with open(self.embeddings_path / filename, "w", encoding="utf-8") as f:
            json.dump(embeddings_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved embeddings to {filename}")
    
    def generate_simple_embeddings(self):
        """Generate simple embeddings for all legal documents"""
        print("🚀 Starting simple legal embeddings generation...")
        
        # Load documents
        documents = self.load_converted_documents()
        
        if not documents:
            print("❌ No documents found to process")
            return
        
        # Generate simple embeddings
        embeddings_data = self.create_simple_embeddings(documents)
        
        # Save embeddings
        self.save_embeddings(embeddings_data, "simple_legal_embeddings.json")
        
        # Print summary
        print(f"\n📊 Simple Embeddings Summary:")
        print(f"  Total Documents: {len(documents)}")
        print(f"  Embedding Dimension: {embeddings_data['embedding_dimension']}")
        print(f"  Model Type: {embeddings_data['model_type']}")
        
        return embeddings_data

def main():
    """Main execution function"""
    generator = SimpleLegalEmbeddingsGenerator()
    results = generator.generate_simple_embeddings()
    print("\n✅ Simple legal embeddings generation completed successfully!")

if __name__ == "__main__":
    main()
