````markdown
# AI Chatbot Backend

A production-oriented FastAPI backend for a full-stack AI chatbot application. The backend provides streaming LLM responses, conversation memory, tool calling, PDF document ingestion, embedding-based retrieval, and Retrieval-Augmented Generation (RAG).

The service is designed to work with a separate React frontend and supports configurable language models through the API.

## ✨ Features

- 🤖 **LLM-powered conversations** with configurable models
- ⚡ **Streaming responses** for real-time output
- 🧠 **Conversation memory** with session-based chat history
- 📄 **PDF document ingestion**
- 🔍 **Embedding-based semantic search**
- 📚 **Retrieval-Augmented Generation (RAG)**
- 🛠️ **Tool calling** for tasks such as calculations and weather retrieval
- 🔀 **Model selection** from the frontend
- 🌐 **REST API** built with FastAPI
- 🚀 **Cloud deployment** with Render
- 🔐 **Environment-based configuration** for API credentials and service settings

---

## 🏗️ Architecture

```text
┌─────────────────────┐
│   React Frontend    │
│                     │
│  Chat UI            │
│  Model Selection    │
│  File Upload        │
└──────────┬──────────┘
           │
           │ HTTP / Streaming
           ▼
┌─────────────────────┐
│   FastAPI Backend   │
│                     │
│  /ask               │
│  /upload            │
│  /new-chat          │
└──────────┬──────────┘
           │
     ┌─────┴──────┐
     │            │
     ▼            ▼
┌──────────┐  ┌───────────────┐
│  Memory  │  │      RAG      │
│          │  │               │
│ Sessions │  │ PDF → Chunks  │
│ History  │  │ → Embeddings  │
└──────────┘  │ → Vector Search│
              └───────┬───────┘
                      │
                      ▼
             ┌─────────────────┐
             │   LLM Provider  │
             │                 │
             │ Chat Models     │
             │ Embedding Model │
             └─────────────────┘
````

---

## 🧰 Technologies

| Technology                | Purpose                        |
| ------------------------- | ------------------------------ |
| **Python**                | Backend development            |
| **FastAPI**               | REST API framework             |
| **Uvicorn**               | ASGI server                    |
| **OpenAI-compatible API** | LLM and embedding requests     |
| **SQLite**                | Local application data storage |
| **NumPy**                 | Vector similarity calculations |
| **PyPDF**                 | PDF text extraction            |
| **Requests**              | External API requests          |
| **Geopy**                 | Location/geocoding support     |

---

## 📋 Requirements

* Python 3.11+
* An OpenAI-compatible LLM/embedding API provider
* API credentials configured through environment variables

> **Note:** Earlier versions of this project used local Ollama inference. The current deployed version is configured to use remotely hosted models through an OpenAI-compatible API.

---

## ⚙️ Environment Variables

Create a `.env` file in the backend directory:

```env
OPENROUTER_API_KEY=your_api_key

EMBEDDING_MODEL=your_embedding_model
```

Additional environment variables may be required depending on the selected database and deployment configuration.

**Never commit your `.env` file or API keys to source control.**

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Shurickin/chatbot-backend.git

cd chatbot-backend
```

### 2. Create a virtual environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file and add the required API credentials and model configuration.

### 5. Start the development server

```bash
uvicorn server:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI's interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

## 🔌 API

### `POST /ask`

Processes a user message and streams the generated response.

#### Request

```json
{
    "session_id": "abc123",
    "question": "Explain machine learning."
}
```

The endpoint:

1. Loads the conversation history.
2. Determines whether tools or document context are required.
3. Retrieves relevant document context when applicable.
4. Sends the request to the selected language model.
5. Streams the response back to the client.
6. Stores the conversation history.

---

### `POST /new-chat`

Creates a new conversation session.

#### Request

```json
{
    "user_id": "user123"
}
```

Returns a new conversation identifier used by subsequent `/ask` requests.

---

### `POST /upload`

Uploads a PDF document for use with the RAG system.

The backend:

1. Extracts text from the PDF.
2. Splits the text into chunks.
3. Generates embeddings.
4. Stores the resulting vectors and document metadata.
5. Makes the document available for semantic retrieval.

---

## 🧠 Retrieval-Augmented Generation

The RAG pipeline follows this process:

```text
PDF
 │
 ▼
Text Extraction
 │
 ▼
Chunking
 │
 ▼
Embedding Generation
 │
 ▼
Vector Storage
 │
 └──────────────────────┐
                        │
User Question           │
 │                      │
 ▼                      │
Query Embedding         │
 │                      │
 ▼                      │
Cosine Similarity ◄─────┘
 │
 ▼
Relevant Chunks
 │
 ▼
LLM Context
 │
 ▼
Generated Response
```

The system uses embedding similarity to determine which document chunks are most relevant to a user's question before supplying them as context to the language model.

---

## 🛠️ Tool Calling

The backend supports model-driven tool selection.

Available tools include:

* **Calculator** — performs arithmetic operations
* **Weather** — retrieves weather information for a specified location
* **Notes Search** — searches stored notes
* **Document Context** — retrieves relevant context from uploaded documents

The model first determines whether a tool is necessary. If a tool is selected, the backend executes it and incorporates the result into the conversation.

---

## 💬 Streaming

Responses are streamed from the backend rather than waiting for the entire model response to be generated.

```text
User
 │
 ▼
FastAPI
 │
 ▼
LLM API
 │
 │ token/chunk
 │ token/chunk
 │ token/chunk
 ▼
React Frontend
```

This allows the frontend to display the response progressively, creating a more responsive chat experience.

---

## 🤖 Model Selection

The frontend allows the user to select between available language models.

The selected model is included in the request to the backend, allowing the same application to use different models without modifying the backend source code.

This makes it possible to experiment with different models based on:

* Response quality
* Speed
* Reasoning ability
* Cost
* Tool-calling performance

---

## 📁 Project Structure

```text
backend/
│
├── server.py              # FastAPI application and API routes
├── rag.py                 # Retrieval and similarity search
├── memory.py              # Conversation memory
├── database.py            # Database operations
├── upload.py              # PDF upload and processing
├── embeddings.py          # Embedding generation
├── requirements.txt       # Python dependencies
├── .env                   # Local environment configuration
│
└── uploads/               # Uploaded documents
```

> File names may change as the project evolves.

---

## 🌐 Deployment

The backend is deployed using [Render](https://render.com).

The production API is available at:

**[https://ollama-chatbot-v6ad.onrender.com](https://ollama-chatbot-v6ad.onrender.com)**

FastAPI's interactive documentation can be accessed at:

**[https://ollama-chatbot-v6ad.onrender.com/docs](https://ollama-chatbot-v6ad.onrender.com/docs)**

The frontend communicates with the backend through the deployed API rather than relying on localhost.

---

## ⚠️ Current Limitations

This project is primarily designed as a portfolio and demonstration application.

### Database Persistence

The current deployment uses local SQLite storage. Because the deployed service uses an ephemeral filesystem, application data may be lost when the service is redeployed or restarted.

### RAG Retrieval

The current RAG implementation uses basic embedding similarity and cosine-distance scoring. More sophisticated retrieval techniques could improve relevance for complex documents.

### Authentication

The current application does not implement user authentication or authorization.

---

## 🔮 Future Improvements

Potential improvements include:

* [ ] PostgreSQL for persistent production storage
* [ ] ChromaDB or another dedicated vector database
* [ ] Improved chunking and document preprocessing
* [ ] Hybrid keyword + semantic retrieval
* [ ] Reranking retrieved document chunks
* [ ] Document citations in generated responses
* [ ] User authentication
* [ ] Persistent user accounts and conversations
* [ ] Docker containerization
* [ ] Automated testing
* [ ] Improved error handling and observability
* [ ] Background document processing
* [ ] Support for additional document formats

---
