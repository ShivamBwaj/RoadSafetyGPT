"""
Script to extract road safety interventions from PDFs/ChromaDB
and update interventions.json automatically
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from main import RoadSafetyRAG

# Define paths (matching main.py)
DATA_DIR = Path("data")
INTERVENTIONS_JSON = DATA_DIR / "interventions.json"
import groq

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

class InterventionExtractor:
    """Extract interventions from PDF documents using LLM"""
    
    def __init__(self):
        self.rag_system = RoadSafetyRAG()
        self.client = groq.Groq(api_key=GROQ_API_KEY)
        self.model_name = GROQ_MODEL
        
    def extract_from_text_chunks(self, chunks: List, num_chunks: int = 20) -> List[Dict]:
        """Extract interventions from document chunks"""
        print(f"\n📖 Analyzing {min(len(chunks), num_chunks)} document chunks...")
        
        # Get sample chunks for analysis
        sample_chunks = chunks[:num_chunks]
        
        # Combine chunks into context
        context_text = "\n\n---\n\n".join([
            f"[Source: {chunk.metadata.get('source', 'Unknown')}]\n{chunk.page_content}"
            for chunk in sample_chunks
        ])
        
        prompt = f"""You are analyzing road safety documents. Extract specific road safety interventions mentioned in the following text.

Text from documents:
{context_text}

For each intervention found, extract and format it as JSON with this structure:
{{
    "intervention": "Brief intervention name",
    "context": "When/where this intervention should be used",
    "source": "Document name and clause/section if mentioned",
    "impact": "Expected safety impact or benefit",
    "keywords": ["keyword1", "keyword2", "keyword3"]
}}

Return a JSON array of interventions. Only extract interventions that are:
1. Specific and actionable (not general advice)
2. Mentioned with context or rationale
3. Include source information if available

Format your response as a valid JSON array. Example:
[
    {{
        "intervention": "Install rumble strips",
        "context": "Straight rural highways with frequent overspeeding",
        "source": "IRC:SP:84 - Clause 5.2.3",
        "impact": "Reduces speeding-related crashes by alerting inattentive drivers",
        "keywords": ["speeding", "rural", "highway", "rumble"]
    }}
]

Return ONLY the JSON array, no other text."""

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured data from road safety documents. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON from response
            # Sometimes LLM wraps it in markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            interventions = json.loads(response_text)
            
            # Validate structure
            valid_interventions = []
            for inv in interventions:
                if isinstance(inv, dict) and "intervention" in inv:
                    # Ensure all required fields
                    inv_clean = {
                        "intervention": inv.get("intervention", ""),
                        "context": inv.get("context", ""),
                        "source": inv.get("source", ""),
                        "impact": inv.get("impact", ""),
                        "keywords": inv.get("keywords", [])
                    }
                    if inv_clean["intervention"]:  # Only add if intervention name exists
                        valid_interventions.append(inv_clean)
            
            return valid_interventions
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error: {e}")
            print(f"Response was: {response_text[:500]}...")
            return []
        except Exception as e:
            print(f"❌ Error extracting interventions: {e}")
            return []
    
    def extract_from_database(self) -> List[Dict]:
        """Extract interventions by querying the vector database"""
        print("\n🔍 Querying vector database for intervention-related content...")
        
        # Query terms related to interventions
        query_terms = [
            "road safety intervention",
            "traffic calming measures",
            "pedestrian safety measures",
            "intersection safety",
            "speed management",
            "road marking and signage",
            "barrier and guardrail",
            "lighting and visibility",
            "blackspot treatment"
        ]
        
        all_interventions = []
        seen_interventions = set()  # To avoid duplicates
        
        for query_term in query_terms:
            print(f"  📋 Searching for: {query_term}")
            chunks = self.rag_system.retrieve_relevant_chunks(query_term, top_k=5)
            
            if chunks:
                extracted = self.extract_from_text_chunks(chunks, num_chunks=len(chunks))
                
                # Deduplicate based on intervention name
                for inv in extracted:
                    inv_name_lower = inv["intervention"].lower().strip()
                    if inv_name_lower not in seen_interventions:
                        seen_interventions.add(inv_name_lower)
                        all_interventions.append(inv)
        
        return all_interventions
    
    def merge_interventions(self, existing: List[Dict], new: List[Dict]) -> List[Dict]:
        """Merge new interventions with existing ones, avoiding duplicates"""
        # Create a set of existing intervention names (normalized)
        existing_names = {inv["intervention"].lower().strip() for inv in existing}
        
        merged = existing.copy()
        
        for new_inv in new:
            new_name = new_inv["intervention"].lower().strip()
            if new_name not in existing_names:
                merged.append(new_inv)
                existing_names.add(new_name)
                print(f"  ✅ Added: {new_inv['intervention']}")
            else:
                print(f"  ⏭️  Skipped duplicate: {new_inv['intervention']}")
        
        return merged
    
    def run_extraction(self, use_database: bool = True, process_all_pdfs: bool = False):
        """Run the extraction process"""
        print("🚀 Starting intervention extraction process...\n")
        
        # Load existing interventions
        if INTERVENTIONS_JSON.exists():
            with open(INTERVENTIONS_JSON, 'r', encoding='utf-8') as f:
                existing_interventions = json.load(f)
            print(f"📚 Loaded {len(existing_interventions)} existing interventions")
        else:
            existing_interventions = []
            print("📚 No existing interventions found, starting fresh")
        
        new_interventions = []
        
        if use_database:
            # Use vector database (faster, already processed)
            if self.rag_system.vectorstore:
                print("\n📊 Using existing vector database...")
                new_interventions = self.extract_from_database()
            else:
                print("\n⚠️ No vector database found. Building it first...")
                self.rag_system.build_knowledge_base()
                if self.rag_system.vectorstore:
                    new_interventions = self.extract_from_database()
                else:
                    print("❌ Failed to build database")
                    return
        
        if process_all_pdfs or not use_database:
            # Process PDFs directly
            print("\n📄 Processing PDFs directly...")
            documents = self.rag_system.process_pdfs()
            if documents:
                # Split into chunks
                split_docs = self.rag_system.text_splitter.split_documents(documents)
                extracted = self.extract_from_text_chunks(split_docs, num_chunks=30)
                new_interventions.extend(extracted)
        
        if not new_interventions:
            print("\n⚠️ No new interventions extracted")
            return
        
        print(f"\n✨ Extracted {len(new_interventions)} new interventions")
        
        # Merge with existing
        merged = self.merge_interventions(existing_interventions, new_interventions)
        
        # Save updated interventions
        with open(INTERVENTIONS_JSON, 'w', encoding='utf-8') as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Updated interventions.json!")
        print(f"   Total interventions: {len(merged)}")
        print(f"   Added: {len(merged) - len(existing_interventions)}")
        print(f"   Location: {INTERVENTIONS_JSON}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract interventions from PDFs/database")
    parser.add_argument("--use-db", action="store_true", default=True, 
                       help="Use existing vector database (default: True)")
    parser.add_argument("--process-pdfs", action="store_true", 
                       help="Also process PDFs directly")
    
    args = parser.parse_args()
    
    if not GROQ_API_KEY:
        print("❌ Error: GROQ_API_KEY not found in environment variables")
        print("   Please set it in .env file or environment")
        exit(1)
    
    extractor = InterventionExtractor()
    extractor.run_extraction(
        use_database=args.use_db,
        process_all_pdfs=args.process_pdfs
    )

