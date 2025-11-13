# 🚦 Road Safety Intervention GPT

<div align="center">

**An AI-Powered Road Safety Recommendation System**

*Built for IIT Madras Hackathon 2025*

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com/)
[![Groq](https://img.shields.io/badge/Groq-FF6B6B?style=for-the-badge)](https://groq.com/)

</div>

---

## 📖 Overview

**Road Safety Intervention GPT** is an intelligent Retrieval-Augmented Generation (RAG) application that provides evidence-based road safety intervention recommendations by analyzing official documents, standards, and data. The system combines the power of AI with comprehensive road safety knowledge to help engineers, planners, and policymakers make informed decisions.

### 🎯 Key Highlights

- 🤖 **AI-Powered Analysis**: Uses Groq's fast LLM for intelligent recommendations
- 📚 **Multi-Format Support**: Processes PDFs, Excel files (XLSX/XLS), and structured data
- 🌐 **Multilingual**: Supports English, Hindi (हिंदी), and Tamil (தமிழ்)
- 📊 **Interactive Dashboard**: Visual analytics and insights
- 🎓 **Educational Mode**: Quiz system for road safety awareness
- 🎤 **Voice Interface**: Hands-free querying with speech recognition
- 📥 **Report Generation**: Export professional PDF reports

---

## ✨ Features

### 🔍 Core RAG Capabilities

- **Document Processing**: Automatically processes and embeds road safety documents (MoRTH reports, IRC standards, WHO/World Bank manuals, Excel data)
- **Semantic Search**: Uses LangChain + ChromaDB for intelligent document retrieval
- **Evidence-Based Recommendations**: Provides citations and sources for all recommendations
- **Intervention Matching**: Matches queries with predefined interventions from database

### 🚀 Advanced Features

#### 1. 📊 Interactive Dashboard
- **Crash Analysis**: Top 5 crash causes with visual charts
- **Impact Metrics**: Intervention effectiveness analysis
- **Category Distribution**: Pie charts showing intervention categories
- **Real-time Visualization**: Interactive Plotly charts

#### 2. 🌐 Multilingual Support
- **3 Languages**: English, Hindi (हिंदी), Tamil (தமிழ்)
- **Auto-Translation**: Seamless translation of queries and responses
- **Cultural Accessibility**: Makes road safety knowledge accessible to diverse users

#### 3. 🧮 Intelligent Scoring System
- **Priority Scoring**: 1-100 scale for intervention prioritization
- **Color-Coded Badges**: 
  - 🟢 Green (>80): High priority
  - 🟡 Yellow (50-80): Moderate priority
  - 🔴 Red (<50): Low priority
- **Context-Aware**: Scoring based on query relevance and urgency

#### 4. 📥 Professional PDF Reports
- **Comprehensive Reports**: Query summary, recommendations, interventions, sources
- **Formatted Output**: Professional layout with branding
- **One-Click Export**: Download reports instantly

#### 5. 🎓 Educational Quiz Mode
- **Interactive Learning**: 5 multiple-choice questions
- **Instant Feedback**: Correct/incorrect answers with explanations
- **Score Tracking**: Monitor learning progress
- **Knowledge Reinforcement**: Based on real road safety data

#### 6. 🎤 Voice Interface
- **Voice Input**: Speak your queries instead of typing
- **Text-to-Speech**: Listen to AI responses
- **Multi-language Support**: Voice features in all supported languages

#### 7. 📊 Excel File Support
- **XLSX/XLS Processing**: Upload and process Excel spreadsheets
- **Multi-Sheet Support**: Processes all sheets in Excel files
- **Structured Data**: Converts tables to searchable text
- **Smart Chunking**: Handles large datasets efficiently

#### 8. 🤖 AI-Powered Intervention Extraction
- **Automatic Discovery**: Extracts interventions from documents using AI
- **Smart Deduplication**: Avoids duplicate entries
- **Structured Output**: Automatically formats and updates intervention database

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| **Frontend** | Streamlit |
| **LLM** | Groq (Llama 3.1 8B Instant) |
| **RAG Framework** | LangChain |
| **Vector Database** | ChromaDB |
| **Embeddings** | HuggingFace (sentence-transformers/all-MiniLM-L6-v2) |
| **Document Processing** | PyPDF, Pandas, OpenPyXL |
| **Visualization** | Plotly |
| **Translation** | Deep Translator |
| **Text-to-Speech** | yabes-api |
| **Report Generation** | ReportLab |

---

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- Groq API key ([Get one here](https://console.groq.com))

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd road_safety_gpt
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Windows (PowerShell)
New-Item -Path .env -ItemType File

# Linux/Mac
touch .env
```

Add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

### Step 4: Add Documents (Optional)

Place your road safety documents in the `data/` folder:

- **PDFs**: MoRTH reports, IRC standards, WHO/World Bank manuals
- **Excel Files**: Road safety data, intervention databases, crash statistics

**Note**: The app works even without documents, using the built-in intervention database.

---

## 🚀 Quick Start

### Running the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

### First-Time Setup

1. **Upload Documents** (optional):
   - Go to sidebar → "📤 Upload Documents"
   - Select PDF or Excel files
   - Click "Process Uploaded Documents"

2. **Build Knowledge Base**:
   - Click "🔄 Rebuild Knowledge Base" in sidebar
   - Wait for processing (1-2 minutes on first run)

3. **Start Querying**:
   - Enter a road safety problem
   - Click "🔍 Get Recommendations"
   - Explore results with sources and interventions

---

## 📁 Project Structure

```
road_safety_gpt/
├── app.py                      # Streamlit frontend
├── main.py                     # RAG + Groq logic
├── utils.py                    # Utility functions (translation, scoring, reports)
├── extract_interventions.py    # AI-powered intervention extraction
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .env                        # Environment variables (create this)
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── data/                       # Documents folder
│   ├── interventions.json     # Intervention database
│   ├── *.pdf                  # PDF documents
│   └── *.xlsx                 # Excel files
└── chroma_db/                 # Vector database (auto-created)
```

---

## 🎯 Usage Guide

### Basic Query Flow

1. **Enter Problem**: Describe a road safety issue
   - Example: *"Frequent crashes at curved rural intersections at night with poor visibility"*

2. **Get Recommendations**: Click "🔍 Get Recommendations"

3. **Review Results**:
   - **🧠 GPT Response**: AI-generated recommendations with rationale
   - **✅ Intervention Matches**: Matched interventions with priority scores
   - **📚 Sources Used**: Expandable section with document references

### Advanced Features

#### 📊 Dashboard Mode
- Toggle "📈 Show Dashboard" in sidebar
- View crash statistics and intervention analytics
- Interactive charts and visualizations

#### 🌐 Multilingual Mode
- Select language from sidebar dropdown
- Query and responses automatically translated
- Supports English, Hindi, Tamil

#### 🎓 Quiz Mode
- Toggle "🎓 Learn Road Safety" in sidebar
- Answer multiple-choice questions
- Get instant feedback and explanations

#### 🎤 Voice Mode
- Click "🎤 Voice Input" to speak queries
- Click "🔊 Speak Response" to hear answers
- Works in all supported languages

#### 📥 Export Reports
- After getting recommendations, click "📥 Download Report (PDF)"
- Professional PDF with all details
- Includes query, recommendations, interventions, and sources

#### 🤖 Extract Interventions
- Click "🔍 Extract Interventions from PDFs" in sidebar
- AI analyzes documents and updates intervention database
- Automatically discovers new interventions

---

## 🔧 Configuration

### Embedding Settings (`main.py`)

```python
chunk_size=1000          # Text chunk size
chunk_overlap=150        # Overlap between chunks
model_name="sentence-transformers/all-MiniLM-L6-v2"
```

### LLM Settings (`main.py`)

```python
temperature=0.3          # Lower = more factual
max_tokens=1000          # Response length
```

### Adding Custom Interventions

Edit `data/interventions.json`:

```json
{
  "intervention": "Install rumble strips",
  "context": "Straight rural highways with frequent overspeeding",
  "source": "IRC:SP:84 - Clause 5.2.3",
  "impact": "Reduces speeding-related crashes by alerting drivers",
  "keywords": ["speeding", "rural", "highway"]
}
```

Or use the AI extraction feature to automatically discover interventions from documents!

---

## 🌐 Deployment

### Streamlit Community Cloud (Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Streamlit**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select repository and branch
   - Main file: `app.py`
   - Add secrets: `GROQ_API_KEY`

3. **Your app is live!** 🎉

See `DEPLOYMENT.md` for detailed deployment instructions.

---

## 🐛 Troubleshooting

### Common Issues

**"Knowledge Base Not Built"**
- Ensure documents exist in `data/` folder
- Click "Rebuild Knowledge Base"
- Check file formats (PDF, XLSX supported)

**Groq API Errors**
- Verify API key in `.env` file
- Check Groq account quota
- Ensure internet connection

**PDF Processing Errors**
- Some PDFs may be corrupted (app will skip them)
- Try re-downloading problematic files
- Check PDF file integrity

**Voice Input Not Working**
- Install PyAudio: `pip install pyaudio`
- Grant microphone permissions
- Voice input is optional - app works without it

**Import Errors**
- Run `pip install -r requirements.txt`
- Ensure Python 3.10+
- Check all dependencies installed

---

## 📊 Performance

- **First Load**: 1-2 minutes (model download)
- **Subsequent Loads**: 10-30 seconds
- **Query Response**: 2-5 seconds
- **Document Processing**: ~1 second per PDF page
- **Excel Processing**: ~2 seconds per sheet

---

## 🎓 Educational Value

This project demonstrates:

- **RAG Architecture**: Retrieval-Augmented Generation implementation
- **Vector Databases**: ChromaDB for semantic search
- **LLM Integration**: Groq API for fast inference
- **Multi-Format Processing**: PDF and Excel handling
- **Multilingual AI**: Translation and localization
- **Voice Interfaces**: Speech recognition and TTS
- **Data Visualization**: Interactive dashboards
- **Report Generation**: Automated document creation

---

## 🤝 Contributing

This project was built for IIT Madras Hackathon 2025. Contributions and improvements are welcome!

### Areas for Enhancement

- [ ] Support for more document formats (DOCX, CSV)
- [ ] Real-time data integration
- [ ] Mobile app version
- [ ] Advanced analytics and predictions
- [ ] Integration with GIS systems

---

## 📄 License

Built for **IIT Madras Hackathon 2025**

---

## 🙏 Acknowledgments

- **Groq** for fast LLM inference
- **LangChain** for RAG framework
- **ChromaDB** for vector storage
- **Streamlit** for the UI framework
- **HuggingFace** for embeddings
- **Plotly** for visualizations
- **Deep Translator** for multilingual support

---

## 📞 Contact & Support

For questions, issues, or contributions, please open an issue on the repository.

---

<div align="center">

**🚗💨 Happy Building! Stay Safe on the Roads! 🚦**

Made with ❤️ for Road Safety

</div>
