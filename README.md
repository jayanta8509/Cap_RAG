# Document RAG Chatbot

A powerful AI-powered document Q&A system using Retrieval Augmented Generation (RAG) with Pinecone vector database, LangChain, and OpenAI.

## 🌟 Features

- **Multi-Source Document Retrieval**: Query across CSV and PDF document sources
- **User-Specific Memory**: Maintains conversation context per user
- **Dual Processing Modes**:
  - **Counselor Mode**: Quick, single-step retrieval for straightforward questions
  - **Agent Mode**: Multi-step retrieval for complex queries requiring research
- **Source Attribution**: Clear indication of which documents were used
- **REST API**: FastAPI-based endpoints for easy integration
- **Real-time Processing**: Streaming support for responsive interactions

## 📋 Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Upload PDFs to Pinecone](#upload-pdfs-to-pinecone)
  - [Run the API](#run-the-api)
  - [Interactive Chat](#interactive-chat)
- [API Documentation](#api-documentation)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- OpenAI API key
- Pinecone API key

### Setup

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd Cap_RAG
```

2. **Create and activate virtual environment:**
```bash
python -m venv env

# Windows
env\Scripts\activate

# Linux/Mac
source env/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create `.env` file:**
```bash
# Create .env file in the root directory
touch .env
```

Add the following to `.env`:
```env
OPENAI_API_KEY=your-openai-api-key-here
PINECONE_API_KEY=your-pinecone-api-key-here
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |
| `PINECONE_API_KEY` | Your Pinecone API key | Yes |
| `PORT` | API server port (default: 8000) | No |

### Default Index Names

The system uses two Pinecone indexes:
- **CSV Index**: `cap-website-data` (for structured CSV data)
- **PDF Index**: `cap-rag-index` (for PDF documents)

You can change these in `rag.py`:
```python
initialize_rag_system(
    csv_index_name="your-csv-index",
    pdf_index_name="your-pdf-index"
)
```

## 🎯 Quick Start

### 1. Upload PDFs to Pinecone

**Option A: Using Specific PDF Files**
```python
from vector_store.pdf_pinecone import PDFPineconeManager

# Define your PDF files
pdf_paths = [
    "pdf_data/1.pdf",
    "pdf_data/2.pdf",
    "pdf_data/3.pdf"
]

# Initialize manager
manager = PDFPineconeManager(
    pdf_paths=pdf_paths,
    index_name="cap-rag-index"
)

# Upload to Pinecone
manager.create_and_upload_vector_store()
```

**Option B: Using a Directory**
```python
manager = PDFPineconeManager(
    data_dir="pdf_data",
    index_name="cap-rag-index"
)
manager.create_and_upload_vector_store()
```

### 2. Start the API Server

```bash
python app.py
```

The API will be available at `http://localhost:8000`

### 3. Test the API

**Using cURL:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "query": "What information is available in the documents?",
    "use_agent": false
  }'
```

**Using Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={
        "user_id": "user123",
        "query": "What information is in the documents?",
        "use_agent": False
    }
)

print(response.json())
```

## 📖 Usage

### Upload PDFs to Pinecone

#### Command Line (using examples)
```bash
cd vector_store
python pdf_pinecone.py
```

Edit `pdf_pinecone.py` to uncomment the desired example:
```python
if __name__ == "__main__":
    # Uncomment to run:
    example_with_pdf_list()      # Use specific files
    # example_with_directory()   # Use directory
    # example_search_only()      # Search only
```

#### Programmatic Usage
```python
from vector_store.pdf_pinecone import PDFPineconeManager

# Method 1: List of PDF files
pdf_paths = ["doc1.pdf", "doc2.pdf"]
manager = PDFPineconeManager(
    pdf_paths=pdf_paths,
    index_name="my-index"
)

# Method 2: Directory
manager = PDFPineconeManager(
    data_dir="pdf_data",
    index_name="my-index"
)

# Analyze PDFs (optional)
manager.analyze_pdf_files()

# Upload to Pinecone
vector_store = manager.create_and_upload_vector_store()

# Search
results = manager.search_vectors("your query", k=5)
```

### Run the API

```bash
# Development mode (with auto-reload)
python app.py

# Production mode
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Interactive Chat

```bash
python rag.py
```

**Interactive Commands:**
- Type your question to chat
- `agent` - Toggle between counselor and agent mode
- `clear` - Clear conversation history
- `quit` or `exit` - Exit the chat

## 📚 API Documentation

### Endpoints

#### 1. Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "Document RAG API is running",
  "timestamp": 1699123456.789,
  "pinecone_connected": true,
  "models_loaded": true,
  "status_code": 200
}
```

#### 2. Chat (Counselor Mode)
```
POST /chat
```

**Request Body:**
```json
{
  "user_id": "user123",
  "query": "What information is in the documents?",
  "use_agent": false
}
```

**Response:**
```json
{
  "user_id": "user123",
  "query": "What information is in the documents?",
  "response": "Based on the retrieved documents...",
  "mode": "counselor",
  "data_source": "pdf",
  "timestamp": 1699123456.789,
  "status_code": 200
}
```

**Data Source Values:**
- `"csv"` - Answer from CSV data
- `"pdf"` - Answer from PDF documents
- `"both"` - Answer from both sources
- `"none"` - No retrieval (general response)

#### 3. Chat (Agent Mode)
```
POST /chat/agent
```

Automatically enables agent mode for complex, multi-step retrieval.

**Request Body:**
```json
{
  "user_id": "user123",
  "query": "Provide comprehensive information from all documents"
}
```

### Interactive API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Server                       │
│                       (app.py)                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   RAG System                            │
│                    (rag.py)                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • Initialize Models (OpenAI GPT-4o-mini)        │  │
│  │  • Setup Pinecone Connections                    │  │
│  │  • Create Retrieval Tools                        │  │
│  │  • Setup Conversational Chain                    │  │
│  │  • User Memory Management                        │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────┬────────────────────────────────────┘
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│  CSV Vector DB   │    │  PDF Vector DB   │
│   (Pinecone)     │    │   (Pinecone)     │
│                  │    │                  │
│ • Website Data   │    │ • Documents      │
│ • Structured     │    │ • Catalogs       │
│   Data           │    │ • Guides         │
└──────────────────┘    └──────────────────┘
```

### Data Flow

```
User Query → FastAPI → RAG System → Retrieval Tools
                                         ↓
                          ┌──────────────┴──────────────┐
                          ▼                             ▼
                    CSV Vector DB              PDF Vector DB
                          │                             │
                          └──────────────┬──────────────┘
                                         ▼
                              Retrieve Documents
                                         ↓
                              LLM (GPT-4o-mini)
                                         ↓
                              Generate Response
                                         ↓
                              Return to User
```

## 📁 Project Structure

```
Cap_RAG/
├── app.py                      # FastAPI server
├── rag.py                      # RAG system core
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── README.md                   # This file
│
├── vector_store/
│   ├── pdf_pinecone.py        # PDF upload manager
│   └── vector_database_manager.py  # General vector DB manager
│
├── pdf_data/                   # PDF documents folder
│   ├── 1.pdf
│   ├── 2.pdf
│   └── 3.pdf
│
├── scraping/
│   ├── capamerica_data.json   # Scraped data
│   └── flightaware_scraper.py
│
└── env/                        # Virtual environment (created)
```

## 💡 Examples

### Example 1: Simple Document Query
```python
import requests

response = requests.post(
    "http://localhost:8000/chat",
    json={
        "user_id": "user001",
        "query": "What are the main topics covered in the documents?",
        "use_agent": False
    }
)

result = response.json()
print(f"Response: {result['response']}")
print(f"Source: {result['data_source']}")
```

### Example 2: Complex Multi-Document Query
```python
response = requests.post(
    "http://localhost:8000/chat/agent",
    json={
        "user_id": "user001",
        "query": "Compare information across all documents and provide a comprehensive summary"
    }
)

result = response.json()
print(f"Agent Response: {result['response']}")
print(f"Mode: {result['mode']}")
```

### Example 3: Conversation with Context
```python
user_id = "user001"

# First question
response1 = requests.post(
    "http://localhost:8000/chat",
    json={
        "user_id": user_id,
        "query": "What information is available about pricing?"
    }
)

# Follow-up question (uses conversation context)
response2 = requests.post(
    "http://localhost:8000/chat",
    json={
        "user_id": user_id,
        "query": "Can you provide more details about that?"
    }
)
```

### Example 4: Upload Custom PDFs
```python
from vector_store.pdf_pinecone import PDFPineconeManager

# Your PDF files
my_pdfs = [
    "documents/report_2024.pdf",
    "documents/analysis.pdf",
    "documents/summary.pdf"
]

# Create manager
manager = PDFPineconeManager(
    pdf_paths=my_pdfs,
    index_name="my-company-docs"
)

# Analyze before upload
manager.analyze_pdf_files()

# Upload
print("Uploading to Pinecone...")
manager.create_and_upload_vector_store()
print("Upload complete!")

# Search
results = manager.search_vectors("quarterly results", k=5)
for i, result in enumerate(results, 1):
    print(f"\n{i}. {result.metadata['source']}")
    print(f"   {result.page_content[:200]}...")
```

## 🔧 Troubleshooting

### Common Issues

#### 1. "PINECONE_API_KEY not found"
**Solution:** Create a `.env` file in the root directory with your API keys.

#### 2. "No PDF files found"
**Solution:** 
- Check that PDF files exist in the specified directory
- Use forward slashes in paths: `pdf_data/file.pdf` (not backslashes)
- Verify the path is correct relative to where you run the script

#### 3. "Index not found"
**Solution:** 
- Upload your PDFs first using `pdf_pinecone.py`
- Check index names match between upload and query
- Verify indexes exist in Pinecone dashboard

#### 4. API Returns 503 Error
**Solution:**
- Check server logs for initialization errors
- Verify environment variables are set
- Ensure Pinecone indexes exist
- Check OpenAI API key is valid

#### 5. Slow Response Times
**Solution:**
- Reduce `k` value in retrieval (fewer documents)
- Use counselor mode instead of agent mode for simple queries
- Optimize chunk size in `RecursiveCharacterTextSplitter`

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check System Status

```bash
curl http://localhost:8000/health
```

## 🛠️ Advanced Configuration

### Customize Chunk Size

Edit `rag.py`:
```python
self.text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Adjust this
    chunk_overlap=200,    # Adjust this
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)
```

### Change Embedding Model

Edit `rag.py`:
```python
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")  # or text-embedding-3-small
```

### Change LLM Model

```python
initialize_rag_system(model_name="gpt-4o")  # or gpt-4, gpt-3.5-turbo
```

### Adjust Retrieval Count

```python
# In rag.py retrieval tools
retrieved_docs = csv_vector_store.similarity_search(query, k=5)  # Change k value
```

## 📊 System Requirements

### Minimum Requirements
- **RAM**: 4GB
- **Storage**: 1GB (plus your document size)
- **CPU**: 2 cores
- **Internet**: Stable connection for API calls

### Recommended Requirements
- **RAM**: 8GB+
- **Storage**: 5GB+
- **CPU**: 4+ cores
- **Internet**: High-speed connection

## 🔐 Security Notes

- Keep your `.env` file secure and never commit it to version control
- Use environment-specific API keys (dev/staging/prod)
- Configure CORS properly for production
- Implement rate limiting for production APIs
- Use HTTPS in production
- Implement authentication for user access

## 🙏 Acknowledgments

Built with:
- [LangChain](https://langchain.com/) - LLM framework
- [Pinecone](https://www.pinecone.io/) - Vector database
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [OpenAI](https://openai.com/) - Language models
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Agent orchestration

---

**Version**: 1.0.0  
**Last Updated**: November 4, 2025  
**Status**: ✅ Production Ready

