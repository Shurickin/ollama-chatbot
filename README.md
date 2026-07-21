# AI Chatbot Backend

A FastAPI backend that powers an AI chatbot using Ollama. The backend supports streaming responses, conversation memory, document uploads, and Retrieval-Augmented Generation (RAG).

## Features

- 🤖 Local LLM inference using Ollama
- ⚡ Streaming responses
- 🧠 Conversation memory
- 📄 PDF document upload
- 🔍 Vector search with embeddings
- 🛠 Tool calling support
- 🚀 REST API built with FastAPI

---

## Technologies

- Python
- FastAPI
- Ollama
- SQLite
- NumPy
- PyPDF
- Uvicorn

---

## Architecture

```
React Frontend
        │
        ▼
    FastAPI Server
        │
        ├── Conversation Memory
        ├── PDF Upload
        ├── Embedding Generator
        ├── Vector Search
        └── Ollama
              │
              ├── Llama 3
              ├── Qwen
              └── Embedding Model
```

---

## Requirements

- Python 3.11+
- Ollama installed
- One or more downloaded models

Example:

```bash
ollama pull llama3
ollama pull qwen3.5
ollama pull embeddinggemma
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/yourusername/chatbot-backend.git

cd chatbot-backend
```

Create a virtual environment

Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

Mac/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the server

```bash
uvicorn main:app --reload
```

The API will run at

```
http://127.0.0.1:8000
```

---

## API Endpoints

### Chat

```
POST /ask
```

Streams an AI response.

Example request

```json
{
    "session_id": "abc123",
    "question": "Explain machine learning."
}
```

---

### Upload Document

```
POST /upload
```

Uploads a PDF, chunks the contents, generates embeddings, and stores them for retrieval.

---

## Project Structure

```
backend/

├── main.py
├── rag.py
├── memory.py
├── upload.py
├── embeddings.py
├── database.py
├── requirements.txt
└── uploads/
```

---

## How RAG Works

1. Upload a PDF.
2. Extract text.
3. Split into chunks.
4. Generate embeddings using Ollama.
5. Store embeddings.
6. Embed the user's question.
7. Retrieve the most similar chunks.
8. Send context to the language model.
9. Stream the generated response back to the frontend.

---

## Models Used

Example configuration

- Llama 3
- Qwen 3.5
- EmbeddingGemma

These can be changed inside the configuration file.

---

## Future Improvements

- ChromaDB
- PostgreSQL
- Authentication
- Docker deployment
- Multiple document collections
- Citation support
- Better chunk ranking
- Async embedding generation

## License

MIT
