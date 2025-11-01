"""
RAG + Groq Logic for Road Safety Intervention GPT
Handles PDF processing, embedding, and querying with Groq LLM
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    # Fallback for older versions
    from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader

import groq

# Load environment variables
load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
DATA_DIR = Path("data")
CHROMA_DB_DIR = Path("chroma_db")
INTERVENTIONS_JSON = DATA_DIR / "interventions.json"


class GroqLLM:
    """Wrapper for Groq LLM compatible with LangChain"""
    
    def __init__(self, model_name: str = None):
        self.client = groq.Groq(api_key=GROQ_API_KEY)
        self.model_name = model_name or GROQ_MODEL
    
    def __call__(self, prompt: str, **kwargs) -> str:
        """Invoke the LLM with a prompt"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert road safety engineer providing evidence-based recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling Groq API: {str(e)}"


class RoadSafetyRAG:
    """RAG system for road safety interventions"""
    
    def __init__(self):
        # Use new langchain-huggingface package to avoid deprecation warning
        # Model will be downloaded on first use (may take a moment on cloud)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}  # Use CPU for cloud compatibility
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            length_function=len
        )
        self.llm = GroqLLM()
        self.vectorstore = None
        self.interventions = []
        self.load_interventions()
    
    def load_interventions(self):
        """Load interventions from JSON file"""
        if INTERVENTIONS_JSON.exists():
            with open(INTERVENTIONS_JSON, 'r', encoding='utf-8') as f:
                self.interventions = json.load(f)
        else:
            self.interventions = []
    
    def get_pdf_files(self) -> List[Path]:
        """Get all PDF files from data directory"""
        if not DATA_DIR.exists():
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            return []
        return list(DATA_DIR.glob("*.pdf"))
    
    def process_pdfs(self) -> List[Document]:
        """Process all PDFs and return documents"""
        pdf_files = self.get_pdf_files()
        all_documents = []
        
        if not pdf_files:
            return []
        
        for pdf_path in pdf_files:
            try:
                loader = PyPDFLoader(str(pdf_path))
                documents = loader.load()
                # Add metadata with PDF name
                for doc in documents:
                    doc.metadata['source'] = pdf_path.name
                all_documents.extend(documents)
            except Exception as e:
                print(f"Error processing {pdf_path.name}: {str(e)}")
                continue
        
        # Split documents into chunks
        split_docs = self.text_splitter.split_documents(all_documents)
        return split_docs
    
    def build_knowledge_base(self, force_rebuild: bool = False):
        """Build or load the ChromaDB vector store"""
        if force_rebuild or not CHROMA_DB_DIR.exists() or not any(CHROMA_DB_DIR.rglob("*")):
            # Process PDFs and create embeddings
            documents = self.process_pdfs()
            
            if not documents:
                return False
            
            # Create vector store
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=str(CHROMA_DB_DIR)
            )
            print(f"Knowledge base built with {len(documents)} chunks from PDFs")
            return True
        else:
            # Load existing vector store
            try:
                self.vectorstore = Chroma(
                    persist_directory=str(CHROMA_DB_DIR),
                    embedding_function=self.embeddings
                )
                print("Loaded existing knowledge base")
                return True
            except Exception as e:
                print(f"Error loading vector store: {str(e)}")
                return False
    
    def search_interventions(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search interventions JSON based on query keywords"""
        query_lower = query.lower()
        scored_interventions = []
        
        for intervention in self.interventions:
            score = 0
            keywords = intervention.get("keywords", [])
            context = intervention.get("context", "").lower()
            intervention_name = intervention.get("intervention", "").lower()
            
            # Score based on keyword matches
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    score += 2
            
            # Score based on context match
            if any(word in context for word in query_lower.split() if len(word) > 3):
                score += 1
            
            # Score based on intervention name match
            if any(word in intervention_name for word in query_lower.split() if len(word) > 3):
                score += 1
            
            if score > 0:
                scored_interventions.append((score, intervention))
        
        # Sort by score and return top_k
        scored_interventions.sort(key=lambda x: x[0], reverse=True)
        return [intervention for _, intervention in scored_interventions[:top_k]]
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = 4) -> List[Document]:
        """Retrieve relevant chunks from vector store"""
        if not self.vectorstore:
            return []
        
        try:
            # Use similarity_search directly - more reliable across LangChain versions
            docs = self.vectorstore.similarity_search(query, k=top_k)
            return docs
        except Exception as e:
            print(f"Error retrieving documents: {str(e)}")
            return []
    
    def generate_response(self, query: str) -> Dict[str, Any]:
        """Generate comprehensive response with RAG and intervention matching"""
        # Retrieve relevant chunks
        relevant_chunks = self.retrieve_relevant_chunks(query)
        
        # Search interventions
        matched_interventions = self.search_interventions(query)
        
        # Build context from chunks
        context_text = "\n\n".join([
            f"[Source: {doc.metadata.get('source', 'Unknown')}]\n{doc.page_content}"
            for doc in relevant_chunks
        ])
        
        # Build prompt for LLM
        interventions_text = "\n".join([
            f"- {inv['intervention']}: {inv['context']} (Source: {inv['source']})"
            for inv in matched_interventions
        ])
        
        prompt = f"""You are an expert road safety engineer. A user has described a road safety problem. Based on the provided context from official documents and suggested interventions, provide a structured recommendation.

User's Problem Description:
{query}

Relevant Context from Documents:
{context_text}

Suggested Interventions from Database:
{interventions_text}

Please provide:
1. **Recommended Interventions**: List 3-5 specific interventions that address the problem
2. **Rationale**: Explain why each intervention is suitable
3. **References**: Mention document names and clauses where applicable
4. **Expected Impact**: Brief description of expected safety improvements

Format your response in a clear, structured manner."""

        # Get LLM response
        llm_response = self.llm(prompt)
        
        # Extract sources
        sources = list(set([
            doc.metadata.get('source', 'Unknown')
            for doc in relevant_chunks
        ]))
        
        # Add scoring to interventions
        from utils import calculate_intervention_score
        scored_interventions = []
        for inv in matched_interventions:
            inv_copy = inv.copy()
            inv_copy["priority_score"] = calculate_intervention_score(inv, query)
            scored_interventions.append(inv_copy)
        
        return {
            "response": llm_response,
            "matched_interventions": scored_interventions,
            "sources": sources,
            "relevant_chunks": relevant_chunks,
            "query": query
        }

