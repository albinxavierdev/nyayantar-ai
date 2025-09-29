#!/usr/bin/env python3
"""
Legal Data Conversion Script for RAG-SaaS
Converts extracted legal data to LlamaIndex Document format
"""

import json
import os
import re
from typing import List, Dict, Any
from pathlib import Path
from llama_index.core.schema import Document
from llama_index.core.text_splitter import SentenceSplitter

class LegalDataConverter:
    def __init__(self, processed_data_path: str = "legal_data/processed"):
        # Get the script directory and resolve paths relative to project root
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        self.processed_data_path = project_root / processed_data_path
        self.converted_data_path = project_root / "legal_data/converted"
        self.converted_data_path.mkdir(exist_ok=True)
        
        # Initialize text splitter for legal documents
        self.text_splitter = SentenceSplitter(
            chunk_size=1024,
            chunk_overlap=100,
            separator="\n\n"
        )
    
    def load_processed_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all processed legal data"""
        print("📖 Loading processed legal data...")
        
        data = {}
        for file_path in self.processed_data_path.glob("*.json"):
            act_name = file_path.stem
            print(f"  📄 Loading {act_name}...")
            
            with open(file_path, "r", encoding="utf-8") as f:
                data[act_name] = json.load(f)
        
        return data
    
    def convert_to_llamaindex_documents(self, sections: List[Dict[str, Any]], act_type: str) -> List[Document]:
        """Convert legal sections to LlamaIndex Documents"""
        documents = []
        
        for section in sections:
            # Create document content
            content = f"Section {section['section_number']}: {section['title']}\n\n{section['content']}"
            
            # Create metadata
            metadata = {
                "act_type": section["act_type"],
                "section_number": section["section_number"],
                "title": section["title"],
                "chapter": section.get("chapter", ""),
                "case_references": section.get("case_references", []),
                "source": section.get("source", ""),
                "last_updated": section.get("last_updated", ""),
                "document_type": "legal_section"
            }
            
            # Create LlamaIndex Document
            doc = Document(
                text=content,
                metadata=metadata,
                id_=f"{act_type}_{section['section_number']}"
            )
            
            documents.append(doc)
        
        return documents
    
    def split_legal_documents(self, documents: List[Document]) -> List[Document]:
        """Split large legal documents into smaller chunks"""
        print("✂️ Splitting large legal documents...")
        
        split_documents = []
        for doc in documents:
            # Split document if it's too long
            if len(doc.text) > 2000:  # Split if longer than 2000 characters
                chunks = self.text_splitter.split_text(doc.text)
                
                for i, chunk in enumerate(chunks):
                    # Create new document for each chunk
                    chunk_doc = Document(
                        text=chunk,
                        metadata={
                            **doc.metadata,
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "is_chunk": True
                        },
                        id_=f"{doc.id_}_chunk_{i}"
                    )
                    split_documents.append(chunk_doc)
            else:
                split_documents.append(doc)
        
        return split_documents
    
    def add_legal_metadata(self, documents: List[Document]) -> List[Document]:
        """Add additional legal-specific metadata"""
        for doc in documents:
            # Add legal keywords for better search
            legal_keywords = self.extract_legal_keywords(doc.text)
            doc.metadata["legal_keywords"] = legal_keywords
            
            # Add legal concepts
            legal_concepts = self.extract_legal_concepts(doc.text)
            doc.metadata["legal_concepts"] = legal_concepts
            
            # Add searchable text
            doc.metadata["searchable_text"] = f"{doc.metadata['title']} {doc.text}"
        
        return documents
    
    def extract_legal_keywords(self, text: str) -> List[str]:
        """Extract legal keywords from text"""
        keywords = []
        
        # Common legal terms
        legal_terms = [
            "offence", "punishment", "imprisonment", "fine", "bail", "arrest",
            "trial", "court", "judge", "magistrate", "evidence", "witness",
            "complaint", "charge", "conviction", "acquittal", "appeal",
            "jurisdiction", "procedure", "act", "section", "clause"
        ]
        
        text_lower = text.lower()
        for term in legal_terms:
            if term in text_lower:
                keywords.append(term)
        
        return keywords
    
    def extract_legal_concepts(self, text: str) -> List[str]:
        """Extract legal concepts from text"""
        concepts = []
        
        # Look for legal concept patterns
        concept_patterns = [
            r"criminal\s+\w+",
            r"civil\s+\w+",
            r"procedural\s+\w+",
            r"substantive\s+\w+",
            r"constitutional\s+\w+",
            r"administrative\s+\w+"
        ]
        
        for pattern in concept_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            concepts.extend(matches)
        
        return list(set(concepts))
    
    def save_converted_data(self, documents: List[Document], act_type: str):
        """Save converted documents"""
        print(f"💾 Saving converted {act_type} documents...")
        
        # Convert documents to serializable format
        doc_data = []
        for doc in documents:
            doc_data.append({
                "text": doc.text,
                "metadata": doc.metadata,
                "id_": doc.id_
            })
        
        # Save to file
        with open(self.converted_data_path / f"{act_type}_documents.json", "w", encoding="utf-8") as f:
            json.dump(doc_data, f, indent=2, ensure_ascii=False)
    
    def convert_all_legal_data(self):
        """Convert all legal data to LlamaIndex format"""
        print("🔄 Starting legal data conversion...")
        
        # Load processed data
        processed_data = self.load_processed_data()
        
        all_documents = []
        
        for act_name, sections in processed_data.items():
            print(f"\n📚 Converting {act_name}...")
            
            # Convert to LlamaIndex documents
            documents = self.convert_to_llamaindex_documents(sections, act_name)
            
            # Split large documents
            documents = self.split_legal_documents(documents)
            
            # Add legal metadata
            documents = self.add_legal_metadata(documents)
            
            # Save converted data
            self.save_converted_data(documents, act_name)
            
            all_documents.extend(documents)
            
            print(f"  ✅ Converted {len(documents)} documents")
        
        # Save combined data
        self.save_combined_data(all_documents)
        
        print(f"\n📊 Conversion Summary:")
        print(f"  Total Documents: {len(all_documents)}")
        print(f"  Acts Processed: {len(processed_data)}")
        
        return all_documents
    
    def save_combined_data(self, documents: List[Document]):
        """Save all documents in a combined format"""
        print("💾 Saving combined legal documents...")
        
        # Convert documents to serializable format
        doc_data = []
        for doc in documents:
            doc_data.append({
                "text": doc.text,
                "metadata": doc.metadata,
                "id_": doc.id_
            })
        
        # Save combined data
        with open(self.converted_data_path / "all_legal_documents.json", "w", encoding="utf-8") as f:
            json.dump(doc_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(doc_data)} combined legal documents")

def main():
    """Main execution function"""
    import re  # Import re for regex operations
    
    converter = LegalDataConverter()
    documents = converter.convert_all_legal_data()
    print("\n✅ Legal data conversion completed successfully!")

if __name__ == "__main__":
    main()
