"""
Streamlit Frontend for Road Safety Intervention GPT
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for API key
if not os.getenv("GROQ_API_KEY"):
    st.error("⚠️ **GROQ_API_KEY not found!** Please create a `.env` file with your Groq API key. See `SETUP_ENV.txt` for instructions.")
    st.stop()

from main import RoadSafetyRAG

# Page configuration
st.set_page_config(
    page_title="Road Safety Intervention GPT",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stContainer {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .response-box {
        background-color: #f8f9fa;
        border-left: 4px solid #28a745;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        color: #212529;
    }
    .response-box p, .response-box li, .response-box div {
        color: #212529 !important;
    }
    .intervention-box {
        background-color: #e7f3ff;
        border-left: 4px solid #007bff;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        color: #212529;
    }
    .intervention-box h4, .intervention-box p, .intervention-box strong {
        color: #212529 !important;
    }
    h1 {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "rag_system" not in st.session_state:
    st.session_state.rag_system = None
if "kb_built" not in st.session_state:
    st.session_state.kb_built = False
if "last_response" not in st.session_state:
    st.session_state.last_response = None

def initialize_rag():
    """Initialize RAG system"""
    if st.session_state.rag_system is None:
        with st.spinner("Initializing RAG system..."):
            st.session_state.rag_system = RoadSafetyRAG()
            # Try to build/load knowledge base
            if st.session_state.rag_system.build_knowledge_base():
                st.session_state.kb_built = True
            else:
                st.warning("⚠️ No PDFs found in /data folder. Please upload PDFs first.")

# Initialize on load
initialize_rag()

# Sidebar
with st.sidebar:
    st.title("🚦 Road Safety GPT")
    st.markdown("---")
    
    st.subheader("📚 Knowledge Base")
    
    if st.button("🔄 Rebuild Knowledge Base", use_container_width=True):
        with st.spinner("Rebuilding knowledge base..."):
            if st.session_state.rag_system:
                success = st.session_state.rag_system.build_knowledge_base(force_rebuild=True)
                if success:
                    st.success("✅ Knowledge base rebuilt successfully!")
                    st.session_state.kb_built = True
                else:
                    st.error("❌ Failed to rebuild knowledge base. Check if PDFs exist in /data folder.")
    
    st.markdown("---")
    
    st.subheader("📤 Upload PDFs")
    uploaded_files = st.file_uploader(
        "Upload road safety PDFs",
        type=["pdf"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        for uploaded_file in uploaded_files:
            file_path = data_dir / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✅ Saved: {uploaded_file.name}")
        
        if st.button("Process Uploaded PDFs", use_container_width=True):
            with st.spinner("Processing uploaded PDFs..."):
                success = st.session_state.rag_system.build_knowledge_base(force_rebuild=True)
                if success:
                    st.success("✅ PDFs processed successfully!")
                    st.session_state.kb_built = True
                    st.rerun()
    
    st.markdown("---")
    
    st.markdown("""
    ### 📖 About
    **Road Safety Intervention GPT**  
    Powered by LangChain + Groq + ChromaDB
    
    Built for: **IIT Madras Hackathon 2025**
    
    This app provides evidence-based road safety intervention recommendations by analyzing official documents and standards.
    """)
    
    # Display status
    st.markdown("---")
    if st.session_state.kb_built:
        st.success("✅ Knowledge Base Ready")
    else:
        st.warning("⚠️ Knowledge Base Not Built")

# Main area
st.title("🚦 Road Safety Intervention GPT")
st.markdown("Ask about road safety problems and get evidence-based intervention recommendations.")

st.markdown("---")

# Query input
query = st.text_area(
    "Describe the road safety problem:",
    placeholder="e.g., Frequent crashes at curved rural intersections at night with poor visibility and speeding vehicles...",
    height=100
)

col1, col2 = st.columns([1, 5])
with col1:
    get_recommendations = st.button("🔍 Get Recommendations", type="primary", use_container_width=True)

if get_recommendations and query:
    if not st.session_state.kb_built:
        st.error("❌ Knowledge base not ready. Please upload PDFs and rebuild the knowledge base first.")
    else:
        with st.spinner("🔍 Analyzing problem and generating recommendations..."):
            try:
                result = st.session_state.rag_system.generate_response(query)
                st.session_state.last_response = result
            except Exception as e:
                st.error(f"❌ Error generating response: {str(e)}")
                st.stop()

# Display results
if st.session_state.last_response:
    result = st.session_state.last_response
    
    # GPT Response Section
    st.markdown("---")
    st.header("🧠 GPT Response")
    st.markdown(
        f'<div class="response-box" style="color: #212529;">{result["response"]}</div>',
        unsafe_allow_html=True
    )
    
    # Intervention Matches Section
    st.markdown("---")
    st.header("✅ Intervention Matches")
    
    if result["matched_interventions"]:
        for i, intervention in enumerate(result["matched_interventions"], 1):
            with st.container():
                st.markdown(f"""
                <div class="intervention-box" style="color: #212529;">
                    <h4 style="color: #212529 !important;">Intervention {i}: {intervention['intervention']}</h4>
                    <p style="color: #212529 !important;"><strong style="color: #212529 !important;">Context:</strong> {intervention['context']}</p>
                    <p style="color: #212529 !important;"><strong style="color: #212529 !important;">Source:</strong> {intervention['source']}</p>
                    <p style="color: #212529 !important;"><strong style="color: #212529 !important;">Expected Impact:</strong> {intervention['impact']}</p>
                    <p style="color: #212529 !important;"><strong style="color: #212529 !important;">Keywords:</strong> {', '.join(intervention.get('keywords', []))}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No specific interventions matched from the database.")
    
    # Sources Section (Collapsible)
    st.markdown("---")
    with st.expander("📚 Sources Used", expanded=False):
        if result["sources"]:
            st.markdown("**Documents referenced:**")
            for source in result["sources"]:
                st.markdown(f"- 📄 {source}")
            
            st.markdown("---")
            st.markdown("**Relevant chunks:**")
            for i, chunk in enumerate(result["relevant_chunks"][:3], 1):  # Show top 3 chunks
                with st.container():
                    st.markdown(f"**Chunk {i}** (from {chunk.metadata.get('source', 'Unknown')}):")
                    st.text(chunk.page_content[:500] + "..." if len(chunk.page_content) > 500 else chunk.page_content)
        else:
            st.info("No sources available. This might be because no PDFs were processed.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6c757d; padding: 20px;'>"
    "Built with ❤️ for Road Safety | Powered by Groq & LangChain"
    "</div>",
    unsafe_allow_html=True
)

