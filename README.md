# NyayaBot — Indian Legal Research Assistant

An AI-powered legal research tool that answers questions grounded in real Indian court judgments and legal Q&A data.

## Tech Stack
- **Retrieval**: Hybrid search (Dense embeddings + BM25 + Cross-encoder reranking)
- **Embeddings**: BAAI/bge-small-en-v1.5
- **Vector DB**: Qdrant (local)
- **LLM**: LLaMA 3.3 70B via Groq
- **Backend**: FastAPI
- **Frontend**: Next.js + Tailwind CSS

## Architecture
User Query → Embedding → Dense Search + BM25 → Reranker → LLaMA 70B → Cited Answer

## Setup

### Backend
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables
Create a `.env` file:
```
GROQ_API_KEY=your-key-here
```