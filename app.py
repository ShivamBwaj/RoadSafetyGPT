"""
Streamlit Frontend for Road Safety Intervention GPT
Enhanced with Dashboard, Multilingual Support, Scoring, PDF Export, Quiz Mode, and Voice I/O
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
try:
    import speech_recognition as sr
    # Try to check if pyaudio is available (optional dependency)
    try:
        import pyaudio  # noqa: F401
        SPEECH_RECOGNITION_AVAILABLE = True
    except ImportError:
        # Speech recognition is installed but pyaudio is not
        SPEECH_RECOGNITION_AVAILABLE = False
        sr = None
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    sr = None
import io
import base64

# Load environment variables
load_dotenv()

# Check for API key
if not os.getenv("GROQ_API_KEY"):
    st.error("⚠️ **GROQ_API_KEY not found!** Please create a `.env` file with your Groq API key. See `SETUP_ENV.txt` for instructions.")
    st.stop()

from main import RoadSafetyRAG
from utils import (
    translate_text, calculate_intervention_score, get_score_color, 
    get_score_color_hex, generate_quiz_questions, generate_pdf_report,
    get_dashboard_data
)

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
    .score-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 15px;
        font-weight: bold;
        color: white;
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
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "en"
if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False
if "quiz_mode" not in st.session_state:
    st.session_state.quiz_mode = False
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0

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

def recognize_speech():
    """Capture voice input using speech recognition"""
    if not SPEECH_RECOGNITION_AVAILABLE:
        st.error("⚠️ Speech recognition not available. Please install: pip install speechrecognition pyaudio")
        return None
    
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎤 Listening... Speak now!")
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        
        text = r.recognize_google(audio)
        return text
    except sr.WaitTimeoutError:
        return None
    except sr.UnknownValueError:
        st.error("Could not understand audio. Please try again.")
        return None
    except OSError as e:
        if "PyAudio" in str(e) or "pyaudio" in str(e).lower():
            st.error("⚠️ PyAudio not found. Please install: pip install pyaudio")
            st.info("💡 On Windows, you may need: pip install pipwin && pipwin install pyaudio")
        else:
            st.error(f"Microphone error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def text_to_speech(text: str, lang: str = "en") -> str:
    """
    Convert text to speech using yabes-api TTS service
    Returns audio URL instead of bytes to avoid file locking issues
    Reference: https://yabes-api.pages.dev/api/tools/tts
    """
    try:
        # Map languages to appropriate voices from yabes-api
        # Available voices: adam, aiko, alex, alice, alloy, anaya, antonio, aoede, arjun, bella, daniel, dora, etc.
        voice_map = {
            "en": "adam",   # Default English voice
            "hi": "arjun",  # Indian name voice for Hindi
            "ta": "arjun"   # Indian name voice for Tamil
        }
        voice = voice_map.get(lang, "adam")
        
        # Call yabes-api TTS endpoint
        api_url = "https://yabes-api.pages.dev/api/tools/tts"
        params = {
            "text": text,
            "voice": voice
        }
        
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("success") and data.get("result", {}).get("audio_url"):
            return data["result"]["audio_url"]
        else:
            st.error(f"TTS API Error: {data.get('message', 'Unknown error')}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"TTS Request Error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"TTS Error: {str(e)}")
        return None

# Initialize on load
initialize_rag()

# Sidebar
with st.sidebar:
    st.title("🚦 Road Safety GPT")
    st.markdown("---")
    
    # Language Selection
    st.subheader("🌎 Language")
    language = st.selectbox(
        "Select Language",
        ["English", "Hindi (हिंदी)", "Tamil (தமிழ்)"],
        index=0 if st.session_state.selected_language == "en" else (1 if st.session_state.selected_language == "hi" else 2)
    )
    lang_map = {"English": "en", "Hindi (हिंदी)": "hi", "Tamil (தமிழ்)": "ta"}
    st.session_state.selected_language = lang_map.get(language, "en")
    
    st.markdown("---")
    
    # Dashboard Toggle
    st.subheader("📊 Dashboard")
    show_dashboard = st.checkbox("📈 Show Dashboard", value=st.session_state.show_dashboard)
    st.session_state.show_dashboard = show_dashboard
    
    st.markdown("---")
    
    # Quiz Mode Toggle
    st.subheader("🎓 Learning Mode")
    quiz_mode = st.checkbox("🎓 Learn Road Safety", value=st.session_state.quiz_mode)
    st.session_state.quiz_mode = quiz_mode
    
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

# Main area - Tabs for different modes
if st.session_state.quiz_mode:
    # Quiz Mode
    st.title("🎓 Road Safety Awareness Quiz")
    st.markdown("Test your knowledge about road safety interventions!")
    
    if not st.session_state.quiz_questions:
        if st.button("Generate Quiz Questions"):
            with st.spinner("Generating quiz questions..."):
                st.session_state.quiz_questions = generate_quiz_questions(
                    st.session_state.rag_system, num_questions=5
                )
                st.session_state.quiz_submitted = False
                st.session_state.quiz_answers = {}
                st.rerun()
    else:
        if not st.session_state.quiz_submitted:
            st.markdown("---")
            for i, question in enumerate(st.session_state.quiz_questions):
                st.markdown(f"**Question {i+1}:** {question['question']}")
                selected = st.radio(
                    f"Select your answer:",
                    question['options'],
                    key=f"q_{i}",
                    label_visibility="collapsed"
                )
                st.session_state.quiz_answers[i] = question['options'].index(selected)
                st.markdown("---")
            
            if st.button("Submit Answers", type="primary"):
                st.session_state.quiz_submitted = True
                correct = 0
                for i, question in enumerate(st.session_state.quiz_questions):
                    if st.session_state.quiz_answers.get(i) == question['correct']:
                        correct += 1
                st.session_state.quiz_score = correct
                st.rerun()
        
        if st.session_state.quiz_submitted:
            st.success(f"🎉 Quiz Complete! You scored {st.session_state.quiz_score}/{len(st.session_state.quiz_questions)}")
            st.markdown("---")
            
            for i, question in enumerate(st.session_state.quiz_questions):
                user_answer = st.session_state.quiz_answers.get(i)
                is_correct = user_answer == question['correct']
                
                if is_correct:
                    st.success(f"✅ **Question {i+1}:** {question['question']}")
                    st.markdown(f"**Your Answer:** {question['options'][user_answer]} ✓")
                else:
                    st.error(f"❌ **Question {i+1}:** {question['question']}")
                    st.markdown(f"**Your Answer:** {question['options'][user_answer]} ✗")
                    st.markdown(f"**Correct Answer:** {question['options'][question['correct']]}")
                
                st.info(f"💡 **Explanation:** {question['explanation']}")
                st.markdown("---")
            
            if st.button("Take Quiz Again"):
                st.session_state.quiz_questions = []
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.rerun()
    
elif st.session_state.show_dashboard:
    # Dashboard Mode
    st.title("📊 Road Safety Dashboard")
    st.markdown("Analytics and insights on road safety interventions")
    
    dashboard_data = get_dashboard_data()
    
    # Top 5 Crash Causes
    st.subheader("🔴 Top 5 Crash Causes")
    crash_df = pd.DataFrame(dashboard_data["crash_causes"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_bar = px.bar(
            crash_df, 
            x="cause", 
            y="count",
            color="count",
            color_continuous_scale="Reds",
            title="Crash Causes by Count"
        )
        fig_bar.update_layout(height=400)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        fig_pie = px.pie(
            crash_df,
            values="percentage",
            names="cause",
            title="Crash Causes Distribution (%)"
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("---")
    
    # Intervention Impact
    st.subheader("📈 Intervention Impact Analysis")
    impact_df = pd.DataFrame(dashboard_data["intervention_impact"])
    
    fig_impact = px.bar(
        impact_df,
        x="intervention",
        y="impact",
        color="impact",
        color_continuous_scale="Greens",
        title="Intervention Effectiveness (Impact %)",
        labels={"impact": "Impact %", "intervention": "Intervention Type"}
    )
    fig_impact.update_layout(height=400, xaxis_tickangle=-45)
    st.plotly_chart(fig_impact, use_container_width=True)
    
    st.markdown("---")
    
    # Intervention Categories
    st.subheader("📋 Intervention Categories")
    category_df = pd.DataFrame(dashboard_data["intervention_categories"])
    
    fig_category = px.pie(
        category_df,
        values="count",
        names="category",
        title="Intervention Categories Distribution"
    )
    fig_category.update_layout(height=400)
    st.plotly_chart(fig_category, use_container_width=True)

else:
    # Main Query Mode
    st.title("🚦 Road Safety Intervention GPT")
    
    # Language indicator
    lang_names = {"en": "English", "hi": "Hindi", "ta": "Tamil"}
    current_lang = lang_names.get(st.session_state.selected_language, "English")
    st.markdown(f"*Language: {current_lang}*")
    st.markdown("Ask about road safety problems and get evidence-based intervention recommendations.")
    
    st.markdown("---")
    
    # Initialize query_value in session state if not exists
    if "query_text_area" not in st.session_state:
        st.session_state.query_text_area = ""
    
    # Voice Input
    col_voice, col_text = st.columns([1, 4])
    with col_voice:
        if st.button("🎤 Voice Input"):
            voice_text = recognize_speech()
            if voice_text:
                # Append or set voice text to query
                current_value = st.session_state.get("query_text_area", "")
                if current_value:
                    st.session_state.query_text_area = current_value + " " + voice_text
                else:
                    st.session_state.query_text_area = voice_text
                # Force rerun to update text area
                st.rerun()
    
    # Query input - Streamlit automatically manages state via key
    query = st.text_area(
        "Describe the road safety problem:",
        value=st.session_state.query_text_area,
        placeholder="e.g., Frequent crashes at curved rural intersections at night with poor visibility and speeding vehicles...",
        height=100,
        key="query_text_area"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        get_recommendations = st.button("🔍 Get Recommendations", type="primary", use_container_width=True)
    
    # Translate query if needed (user query in non-English -> translate to English)
    original_query = query
    if query and st.session_state.selected_language != "en":
        try:
            # Translate query from selected language to English for processing
            query = translate_text(query, target_lang="en", source_lang=st.session_state.selected_language)
        except:
            pass  # Use original if translation fails
    
    if get_recommendations and original_query:
        if not st.session_state.kb_built:
            st.error("❌ Knowledge base not ready. Please upload PDFs and rebuild the knowledge base first.")
        else:
            with st.spinner("🔍 Analyzing problem and generating recommendations..."):
                try:
                    result = st.session_state.rag_system.generate_response(query)
                    st.session_state.last_response = result
                    # Keep the query value so user can see what they asked
                except Exception as e:
                    st.error(f"❌ Error generating response: {str(e)}")
                    st.stop()
    
    # Display results
    if st.session_state.last_response:
        result = st.session_state.last_response
        
        # Translate response if needed
        response_text = result["response"]
        if st.session_state.selected_language != "en":
            try:
                response_text = translate_text(result["response"], target_lang=st.session_state.selected_language)
            except:
                response_text = result["response"]  # Use original if translation fails
        
        # GPT Response Section
        st.markdown("---")
        col_resp, col_audio = st.columns([5, 1])
        with col_resp:
            st.header("🧠 GPT Response")
        with col_audio:
            if st.button("🔊 Speak Response"):
                audio_url = text_to_speech(response_text, st.session_state.selected_language)
                if audio_url:
                    st.audio(audio_url, format="audio/wav")
        
        st.markdown(
            f'<div class="response-box" style="color: #212529;">{response_text}</div>',
            unsafe_allow_html=True
        )
        
        # Intervention Matches Section with Scoring
        st.markdown("---")
        st.header("✅ Intervention Matches")
        
        if result["matched_interventions"]:
            for i, intervention in enumerate(result["matched_interventions"], 1):
                score = intervention.get("priority_score", 50)
                color_icon = get_score_color(score)
                color_hex = get_score_color_hex(score)
                
                with st.container():
                    # Create score badge HTML
                    score_badge = f'<span class="score-badge" style="background-color: {color_hex}; padding: 5px 10px; border-radius: 15px; margin-left: 10px;">{color_icon} Priority: {score}/100</span>'
                    
                    st.markdown(f"""
                    <div class="intervention-box" style="color: #212529;">
                        <h4 style="color: #212529 !important;">Intervention {i}: {intervention['intervention']}{score_badge}</h4>
                        <p style="color: #212529 !important;"><strong style="color: #212529 !important;">Context:</strong> {intervention['context']}</p>
                        <p style="color: #212529 !important;"><strong style="color: #212529 !important;">Source:</strong> {intervention['source']}</p>
                        <p style="color: #212529 !important;"><strong style="color: #212529 !important;">Expected Impact:</strong> {intervention['impact']}</p>
                        <p style="color: #212529 !important;"><strong style="color: #212529 !important;">Keywords:</strong> {', '.join(intervention.get('keywords', []))}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No specific interventions matched from the database.")
        
        # PDF Export
        st.markdown("---")
        col_pdf, _ = st.columns([1, 4])
        with col_pdf:
            if st.button("📥 Download Report (PDF)"):
                with st.spinner("Generating PDF report..."):
                    try:
                        pdf_bytes = generate_pdf_report(
                            original_query if original_query else query,
                            result
                        )
                        st.download_button(
                            label="⬇️ Download PDF",
                            data=pdf_bytes,
                            file_name=f"road_safety_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")
        
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
