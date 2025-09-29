#!/usr/bin/env python3
"""
Legal Data Extraction Script for RAG-SaaS
Extracts legal knowledge from AskLegal.ai data sources
"""

import json
import os
import re
from typing import Dict, List, Any
from pathlib import Path

class LegalDataExtractor:
    def __init__(self, raw_data_path: str = "legal_data/raw"):
        # Get the script directory and resolve paths relative to project root
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        self.raw_data_path = project_root / raw_data_path
        self.processed_data_path = project_root / "legal_data/processed"
        self.processed_data_path.mkdir(exist_ok=True)
        
    def extract_ipc_sections(self) -> Dict[str, Any]:
        """Extract IPC sections from laws_raw.json"""
        print("📖 Extracting IPC sections from laws_raw.json...")
        
        with open(self.raw_data_path / "laws_raw.json", "r", encoding="utf-8") as f:
            ipc_data = json.load(f)
        
        sections = []
        for section_key, section_data in ipc_data["IPC"].items():
            # Extract section number from key (e.g., "section1" -> "1")
            section_number = section_key.replace("section", "")
            
            # Clean and normalize content
            content = self.clean_legal_text(section_data.get("content", ""))
            
            section = {
                "act_type": "IPC",
                "section_number": section_number,
                "title": section_data.get("title", ""),
                "content": content,
                "chapter": self.extract_chapter_from_content(content),
                "case_references": self.extract_case_references(content),
                "source": "Ratanlal & Dhirajlal (36th Edition)",
                "last_updated": "2020-04-28"
            }
            sections.append(section)
        
        print(f"✅ Extracted {len(sections)} IPC sections")
        return {"ipc_sections": sections}
    
    def extract_additional_acts(self) -> Dict[str, Any]:
        """Extract additional legal acts from laws_json folder"""
        print("📚 Extracting additional legal acts...")
        
        acts_data = {}
        laws_json_path = self.raw_data_path / "laws_json"
        
        act_mapping = {
            "ipc.json": "IPC",
            "crpc.json": "CRPC", 
            "cpc.json": "CPC",
            "mva.json": "MVA",
            "iea.json": "IEA",
            "ida.json": "IDA",
            "hma.json": "HMA",
            "nia.json": "NIA"
        }
        
        for filename, act_type in act_mapping.items():
            file_path = laws_json_path / filename
            if file_path.exists():
                print(f"  📄 Processing {act_type} from {filename}...")
                
                with open(file_path, "r", encoding="utf-8") as f:
                    act_data = json.load(f)
                
                sections = []
                for item in act_data:
                    # Clean and normalize content
                    content = self.clean_legal_text(item.get("section_desc", ""))
                    
                    section = {
                        "act_type": act_type,
                        "section_number": str(item.get("section", "")),
                        "title": item.get("section_title", ""),
                        "content": content,
                        "chapter": item.get("chapter", ""),
                        "case_references": self.extract_case_references(content),
                        "source": f"{act_type} Legal Database",
                        "last_updated": "2020-04-28"
                    }
                    sections.append(section)
                
                acts_data[f"{act_type.lower()}_sections"] = sections
                print(f"  ✅ Extracted {len(sections)} {act_type} sections")
        
        return acts_data
    
    def clean_legal_text(self, text: str) -> str:
        """Clean and normalize legal text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and formatting artifacts
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'LNIND\s+\d+\s+\w+', '', text)
        
        # Clean up case citations
        text = re.sub(r'AIR\s+\d+\s+\w+\s+\[LNIND[^\]]*\]', '', text)
        text = re.sub(r'SCC\s+\[LNIND[^\]]*\]', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{3,}', '...', text)
        
        return text.strip()
    
    def extract_chapter_from_content(self, content: str) -> str:
        """Extract chapter information from content"""
        # Look for chapter patterns in content
        chapter_match = re.search(r'CHAPTER\s+([IVX]+)\s+([A-Z\s]+)', content)
        if chapter_match:
            return chapter_match.group(2).strip()
        return ""
    
    def extract_case_references(self, content: str) -> List[str]:
        """Extract case law references from content"""
        case_refs = []
        
        # Extract AIR citations
        air_cases = re.findall(r'AIR\s+\d+\s+\w+\s+[^\]]*', content)
        case_refs.extend(air_cases)
        
        # Extract SCC citations
        scc_cases = re.findall(r'SCC\s+[^\]]*', content)
        case_refs.extend(scc_cases)
        
        # Extract Cr LJ citations
        crlj_cases = re.findall(r'Cr\s+LJ\s+\d+', content)
        case_refs.extend(crlj_cases)
        
        return list(set(case_refs))  # Remove duplicates
    
    def save_processed_data(self, data: Dict[str, Any]):
        """Save processed legal data"""
        print("💾 Saving processed legal data...")
        
        # Save IPC data
        with open(self.processed_data_path / "ipc_sections.json", "w", encoding="utf-8") as f:
            json.dump(data["ipc_sections"], f, indent=2, ensure_ascii=False)
        
        # Save additional acts data
        for act_name, act_sections in data.items():
            if act_name != "ipc_sections":
                with open(self.processed_data_path / f"{act_name}.json", "w", encoding="utf-8") as f:
                    json.dump(act_sections, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved processed data to {self.processed_data_path}")
    
    def extract_all_legal_data(self):
        """Extract all legal data from AskLegal sources"""
        print("🚀 Starting legal data extraction...")
        
        # Extract IPC sections
        ipc_data = self.extract_ipc_sections()
        
        # Extract additional acts
        additional_acts = self.extract_additional_acts()
        
        # Combine all data
        all_data = {**ipc_data, **additional_acts}
        
        # Save processed data
        self.save_processed_data(all_data)
        
        # Print summary
        total_sections = sum(len(sections) for sections in all_data.values())
        print(f"\n📊 Extraction Summary:")
        print(f"  Total Legal Sections: {total_sections}")
        for act_name, sections in all_data.items():
            print(f"  {act_name}: {len(sections)} sections")
        
        return all_data

def main():
    """Main execution function"""
    extractor = LegalDataExtractor()
    legal_data = extractor.extract_all_legal_data()
    print("\n✅ Legal data extraction completed successfully!")

if __name__ == "__main__":
    main()
