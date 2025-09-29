#!/usr/bin/env python3
"""
Legal Embeddings Script for RAG-SaaS
Generates embeddings for legal documents using local embedding models
"""

import json
import os
import numpy as np
from typing import List, Dict, Any
from pathlib import Path
from sentence_transformers import SentenceTransformer
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.schema import Document

class LegalEmbeddingsGenerator:
    def __init__(self, converted_data_path: str = "legal_data/converted"):
        # Get the script directory and resolve paths relative to project root
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        self.converted_data_path = project_root / converted_data_path
        self.embeddings_path = project_root / "legal_data/embeddings"
        self.embeddings_path.mkdir(exist_ok=True)
        
        # Initialize local embedding models
        self.embedding_models = {
            "sentence-transformers": SentenceTransformer('all-MiniLM-L6-v2'),
            "legal-specific": SentenceTransformer('law-ai/InLegalBERT'),
            "multilingual": SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        }
        
        # Initialize LlamaIndex embedding models
        self.llamaindex_embeddings = {
            "huggingface": HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2"),
            "legal-bert": HuggingFaceEmbedding(model_name="law-ai/InLegalBERT")
        }
    
    def load_converted_documents(self) -> List[Document]:
        """Load all converted legal documents"""
        print("📖 Loading converted legal documents...")
        
        documents = []
        
        # Load combined documents
        combined_file = self.converted_data_path / "all_legal_documents.json"
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
        
        print(f"✅ Loaded {len(documents)} legal documents")
        return documents
    
    def generate_embeddings_sentence_transformers(self, documents: List[Document], model_name: str = "sentence-transformers") -> Dict[str, Any]:
        """Generate embeddings using sentence-transformers"""
        print(f"🤖 Generating embeddings using {model_name}...")
        
        model = self.embedding_models[model_name]
        
        # Extract texts
        texts = [doc.text for doc in documents]
        
        # Generate embeddings
        embeddings = model.encode(texts, show_progress_bar=True)
        
        # Create embeddings data
        embeddings_data = {
            "model_name": model_name,
            "model_type": "sentence-transformers",
            "embedding_dimension": embeddings.shape[1],
            "total_documents": len(documents),
            "embeddings": embeddings.tolist(),
            "document_ids": [doc.id_ for doc in documents],
            "metadata": [doc.metadata for doc in documents]
        }
        
        return embeddings_data
    
    def generate_embeddings_llamaindex(self, documents: List[Document], model_name: str = "huggingface") -> Dict[str, Any]:
        """Generate embeddings using LlamaIndex HuggingFace embedding"""
        print(f"🤖 Generating embeddings using LlamaIndex {model_name}...")
        
        embedding_model = self.llamaindex_embeddings[model_name]
        
        # Generate embeddings for each document
        embeddings = []
        for doc in documents:
            embedding = embedding_model.get_text_embedding(doc.text)
            embeddings.append(embedding)
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings)
        
        # Create embeddings data
        embeddings_data = {
            "model_name": model_name,
            "model_type": "llamaindex-huggingface",
            "embedding_dimension": embeddings_array.shape[1],
            "total_documents": len(documents),
            "embeddings": embeddings_array.tolist(),
            "document_ids": [doc.id_ for doc in documents],
            "metadata": [doc.metadata for doc in documents]
        }
        
        return embeddings_data
    
    def test_embedding_quality(self, embeddings_data: Dict[str, Any]) -> Dict[str, float]:
        """Test the quality of generated embeddings"""
        print("🧪 Testing embedding quality...")
        
        embeddings = np.array(embeddings_data["embeddings"])
        
        # Calculate statistics
        stats = {
            "mean_norm": float(np.mean(np.linalg.norm(embeddings, axis=1))),
            "std_norm": float(np.std(np.linalg.norm(embeddings, axis=1))),
            "min_norm": float(np.min(np.linalg.norm(embeddings, axis=1))),
            "max_norm": float(np.max(np.linalg.norm(embeddings, axis=1))),
            "mean_similarity": float(np.mean(np.dot(embeddings, embeddings.T))),
            "std_similarity": float(np.std(np.dot(embeddings, embeddings.T)))
        }
        
        print(f"  📊 Embedding Quality Stats:")
        print(f"    Mean Norm: {stats['mean_norm']:.4f}")
        print(f"    Std Norm: {stats['std_norm']:.4f}")
        print(f"    Min Norm: {stats['min_norm']:.4f}")
        print(f"    Max Norm: {stats['max_norm']:.4f}")
        
        return stats
    
    def save_embeddings(self, embeddings_data: Dict[str, Any], filename: str):
        """Save embeddings to file"""
        print(f"💾 Saving embeddings to {filename}...")
        
        # Save embeddings data
        with open(self.embeddings_path / filename, "w", encoding="utf-8") as f:
            json.dump(embeddings_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved embeddings to {filename}")
    
    def generate_all_embeddings(self):
        """Generate embeddings using all available models"""
        print("🚀 Starting legal embeddings generation...")
        
        # Load documents
        documents = self.load_converted_documents()
        
        if not documents:
            print("❌ No documents found to process")
            return
        
        # Generate embeddings with different models
        embedding_results = {}
        
        # 1. Sentence Transformers - General Purpose
        print("\n1️⃣ Generating embeddings with sentence-transformers...")
        st_embeddings = self.generate_embeddings_sentence_transformers(documents, "sentence-transformers")
        st_quality = self.test_embedding_quality(st_embeddings)
        st_embeddings["quality_stats"] = st_quality
        self.save_embeddings(st_embeddings, "sentence_transformers_embeddings.json")
        embedding_results["sentence_transformers"] = st_embeddings
        
        # 2. Legal-Specific BERT
        print("\n2️⃣ Generating embeddings with legal-specific BERT...")
        try:
            legal_embeddings = self.generate_embeddings_sentence_transformers(documents, "legal-specific")
            legal_quality = self.test_embedding_quality(legal_embeddings)
            legal_embeddings["quality_stats"] = legal_quality
            self.save_embeddings(legal_embeddings, "legal_bert_embeddings.json")
            embedding_results["legal_bert"] = legal_embeddings
        except Exception as e:
            print(f"⚠️ Could not generate legal BERT embeddings: {e}")
        
        # 3. LlamaIndex HuggingFace
        print("\n3️⃣ Generating embeddings with LlamaIndex HuggingFace...")
        llamaindex_embeddings = self.generate_embeddings_llamaindex(documents, "huggingface")
        llamaindex_quality = self.test_embedding_quality(llamaindex_embeddings)
        llamaindex_embeddings["quality_stats"] = llamaindex_quality
        self.save_embeddings(llamaindex_embeddings, "llamaindex_embeddings.json")
        embedding_results["llamaindex"] = llamaindex_embeddings
        
        # 4. Multilingual Model
        print("\n4️⃣ Generating embeddings with multilingual model...")
        try:
            multilingual_embeddings = self.generate_embeddings_sentence_transformers(documents, "multilingual")
            multilingual_quality = self.test_embedding_quality(multilingual_embeddings)
            multilingual_embeddings["quality_stats"] = multilingual_quality
            self.save_embeddings(multilingual_embeddings, "multilingual_embeddings.json")
            embedding_results["multilingual"] = multilingual_embeddings
        except Exception as e:
            print(f"⚠️ Could not generate multilingual embeddings: {e}")
        
        # Print summary
        print(f"\n📊 Embeddings Generation Summary:")
        print(f"  Total Documents: {len(documents)}")
        print(f"  Models Used: {len(embedding_results)}")
        for model_name, data in embedding_results.items():
            print(f"  {model_name}: {data['embedding_dimension']}D embeddings")
        
        return embedding_results

def main():
    """Main execution function"""
    generator = LegalEmbeddingsGenerator()
    results = generator.generate_all_embeddings()
    print("\n✅ Legal embeddings generation completed successfully!")

if __name__ == "__main__":
    main()
