# 🔍 Intervention Extraction Script

## Overview

The `extract_interventions.py` script automatically extracts road safety interventions from your PDF documents and ChromaDB vector database, then updates `interventions.json` with new findings.

## Features

- 🤖 **AI-Powered Extraction**: Uses Groq LLM to intelligently extract interventions from documents
- 📚 **Uses Existing Database**: Queries your ChromaDB for relevant content (fast)
- 📄 **Direct PDF Processing**: Can also process PDFs directly if needed
- 🔄 **Deduplication**: Avoids adding duplicate interventions
- ✅ **Preserves Existing**: Keeps your current interventions and adds new ones

## Usage

### Basic Usage (Recommended)
```bash
python extract_interventions.py
```

This uses your existing ChromaDB vector database (fastest method).

### Process PDFs Directly
```bash
python extract_interventions.py --process-pdfs
```

This processes PDFs directly instead of using the database.

### Both Methods
```bash
python extract_interventions.py --use-db --process-pdfs
```

## Requirements

- `.env` file with `GROQ_API_KEY` set
- Existing ChromaDB (run the app first to build it) OR PDFs in `/data` folder
- All dependencies from `requirements.txt`

## How It Works

1. **Loads existing interventions** from `interventions.json`
2. **Queries vector database** with intervention-related search terms:
   - "road safety intervention"
   - "traffic calming measures"
   - "pedestrian safety measures"
   - "intersection safety"
   - etc.
3. **Extracts interventions** using Groq LLM with structured prompts
4. **Validates and formats** each intervention
5. **Merges with existing** interventions (no duplicates)
6. **Saves updated** `interventions.json`

## Output

The script will:
- Show progress as it searches for interventions
- List each intervention found
- Skip duplicates if found
- Display summary:
  ```
  ✅ Updated interventions.json!
     Total interventions: 25
     Added: 15
  ```

## Tips

- Run after uploading new PDFs to extract new interventions
- The script is smart enough to avoid duplicates
- If extraction fails for some chunks, it continues with others
- Check the output to see which interventions were added

## Integration with App

The app automatically loads the updated `interventions.json` on next run - no restart needed!

