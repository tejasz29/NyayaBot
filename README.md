# ⚖️ NyayaBot — Indian Legal Research Assistant

> Ask any legal question in plain English. Get answers grounded in real Indian court judgments — with citations.


---

## 🧠 What Makes It Different

Most RAG systems stop at basic vector search. NyayaBot uses a **3-layer hybrid retrieval pipeline**:

| Layer | Method | Purpose |
|---|---|---|
| 1 | Dense Search (BGE embeddings + Qdrant) | Semantic similarity — finds conceptually related content |
| 2 | BM25 Sparse Search | Keyword matching — catches exact legal terms and section numbers |
| 3 | Cross-Encoder Reranking | Re-scores all candidates together for much higher precision |

Only after all 3 layers does the answer go to **LLaMA 3.3 70B** for grounded generation with source citations.

---

## 🏗️ Architecture
```
User Query
    ↓
BGE Embedding Model (BAAI/bge-small-en-v1.5)
    ↓
┌─────────────────────┐    ┌─────────────────┐
│  Dense Search       │    │  BM25 Search    │
│  (Qdrant Vector DB) │    │  (Keyword)      │
└─────────────────────┘    └─────────────────┘
              ↓ Merge & Deduplicate ↓
         Cross-Encoder Reranker
         (ms-marco-MiniLM-L-6-v2)
                    ↓
            Top 5 Chunks
                    ↓
         LLaMA 3.3 70B (Groq)
                    ↓
      Cited Answer + Sources
```

---

## ⚙️ Tech Stack

**AI / ML**
- Embeddings: `BAAI/bge-small-en-v1.5` (top MTEB leaderboard, runs locally)
- Reranker: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- LLM: LLaMA 3.3 70B via Groq (fast LPU inference)
- Vector DB: Qdrant (local, 4500+ chunks)
- Retrieval: Hybrid (Dense + BM25 via `rank-bm25`)

**Backend**
- FastAPI with Pydantic validation
- CORS enabled for frontend communication
- Single `/ask` endpoint — clean and simple

**Frontend**
- Next.js 14 + Tailwind CSS
- Real-time loading states
- Clickable source cards with relevance scores

**Data**
- 1000+ Indian legal Q&A records from Hugging Face (`viber1/indian-law-dataset`)
- Custom scraper for indiankanoon.org judgments

---

## 🚀 Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Backend
```bash
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in the root:

Load the dataset and generate embeddings:
```bash
python scraper/load_dataset.py
python embedder/embed.py
```

Start the API:
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## 📁 Project Structure
```
nyayabot/
├── scraper/
│   ├── scrape.py           # indiankanoon.org scraper
│   └── load_dataset.py     # Hugging Face dataset loader
├── embedder/
│   └── embed.py            # Chunking + embedding pipeline
├── retriever/
│   ├── search.py           # Hybrid retrieval (Dense + BM25 + Reranker)
│   └── answer.py           # End-to-end answer generation
├── api/
│   └── main.py             # FastAPI backend
├── frontend/               # Next.js app
├── qdrant_storage/         # Local vector database (auto-generated)
├── data/                   # Raw judgment files (auto-generated)
└── .env                    # API keys (never commit this)
```

---

## 🔮 Roadmap

- [ ] Real Supreme Court & High Court judgments from indiankanoon.org
- [ ] Multilingual support — Hindi, Marathi, Tamil (IndicBERT embeddings)
- [ ] Legal guidance mode — procedural steps, required documents, authority contacts
- [ ] Ragas evaluation pipeline — faithfulness and context precision scoring
- [ ] Full cloud deployment (Railway + Vercel)
- [ ] Topic filters — criminal, property, employment, family, consumer law

---

## 🙋 Author

**Tejas Eklare**
- GitHub: [@tejasz29](https://github.com/tejasz29)
- LinkedIn: [tejas-eklare-236794329](https://linkedin.com/in/tejas-eklare-236794329)
- Email: tejaseklare111@gmail.com

---

## ⭐ If you found this useful, leave a star!
