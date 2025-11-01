# 🚦 Road Safety Intervention GPT

A Retrieval-Augmented Generation (RAG) application powered by Streamlit, LangChain, and Groq that provides evidence-based road safety intervention recommendations by analyzing official documents and standards.

## 📋 Features

- **PDF Processing**: Automatically processes and embeds road safety PDFs (MoRTH reports, IRC standards, WHO/World Bank manuals)
- **RAG-powered Q&A**: Uses LangChain + ChromaDB for semantic search and retrieval
- **Groq LLM Integration**: Fast, factual responses using Groq's `llama-3.1-8b-instant` model
- **Intervention Matching**: Matches user queries with predefined interventions from JSON database
- **Source Attribution**: Shows document references and relevant chunks for transparency

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **LLM**: Groq (Llama 3.1 8B Instant)
- **RAG Framework**: LangChain
- **Vector Database**: ChromaDB
- **Embeddings**: HuggingFace (sentence-transformers/all-MiniLM-L6-v2)
- **PDF Processing**: PyPDF

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- Groq API key (Get one from [Groq Console](https://console.groq.com))

### Step 1: Clone or Download the Project

```bash
cd road_safety_gpt
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Create .env file
# Windows (PowerShell):
New-Item -Path .env -ItemType File

# Linux/Mac:
touch .env
```

Add the following content to `.env`:

```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

Replace `your_groq_api_key_here` with your actual Groq API key.

### Step 4: Add PDF Documents

Place your road safety PDFs in the `data/` folder:

- `MoRTH_2023.pdf` - MoRTH 2023 Road Safety Report
- `IRC_35.pdf` - IRC Standard 35
- `IRC_67.pdf` - IRC Standard 67
- `WHO_Road_Safety_Handbook.pdf` - WHO Road Safety Handbook
- `World_Bank_Road_Safety_Manual.pdf` - World Bank Road Safety Manual

**Note**: The app will work even without PDFs, but will only show intervention matches from the JSON database.

## 🚀 Running the App

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`.

## 📁 Folder Structure

```
road_safety_gpt/
├── app.py                 # Streamlit frontend
├── main.py                # RAG + Groq logic
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .env                  # Environment variables (create this)
├── data/                 # PDF documents folder
│   ├── interventions.json
│   ├── MoRTH_2023.pdf (add your PDFs here)
│   ├── IRC_35.pdf
│   └── ...
└── chroma_db/            # Vector database (auto-created)
```

## 🎯 Usage

1. **First Time Setup**:
   - Add PDF files to the `data/` folder
   - Click "Rebuild Knowledge Base" in the sidebar
   - Wait for the embeddings to be created

2. **Querying**:
   - Enter a road safety problem description in the text area
   - Example: *"Frequent crashes at curved rural intersections at night with poor visibility"*
   - Click "Get Recommendations"

3. **Results**:
   - **GPT Response**: LLM-generated recommendations with rationale
   - **Intervention Matches**: Matched interventions from JSON database
   - **Sources Used**: Expandable section showing referenced documents

4. **Uploading New PDFs**:
   - Use the sidebar file uploader
   - After uploading, click "Process Uploaded PDFs"
   - Or use "Rebuild Knowledge Base" to reprocess all PDFs

## 🔧 Configuration

### Embedding Settings

In `main.py`, you can adjust:
- `chunk_size`: Currently 1000 characters
- `chunk_overlap`: Currently 150 characters
- Embedding model: Currently `sentence-transformers/all-MiniLM-L6-v2`

### LLM Settings

In `main.py`, GroqLLM class:
- `temperature`: Currently 0.3 (lower = more factual)
- `max_tokens`: Currently 1000

## 📝 Adding New Interventions

Edit `data/interventions.json` to add new interventions:

```json
{
  "intervention": "Your intervention name",
  "context": "When to use this intervention",
  "source": "Document reference",
  "impact": "Expected safety impact",
  "keywords": ["keyword1", "keyword2", "keyword3"]
}
```

## 🐛 Troubleshooting

### "Knowledge Base Not Built" Error
- Ensure PDF files exist in the `data/` folder
- Click "Rebuild Knowledge Base" in the sidebar
- Check that PDFs are not corrupted

### Groq API Errors
- Verify your API key in `.env` file
- Check your Groq account quota/limits
- Ensure internet connection is active

### ChromaDB Errors
- Delete the `chroma_db/` folder and rebuild
- Ensure write permissions in the project directory

### Import Errors
- Run `pip install -r requirements.txt` again
- Ensure you're using Python 3.10+

## 📄 License

Built for IIT Madras Hackathon 2025

## 🙏 Acknowledgments

- Groq for fast LLM inference
- LangChain for RAG framework
- ChromaDB for vector storage
- Streamlit for the UI framework

---

**Happy Building! Stay Safe on the Roads! 🚗💨**

