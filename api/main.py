from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, CrossEncoder
from qdrant_client import QdrantClient
from rank_bm25 import BM25Okapi
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load everything once on startup ──────────────────────────────
print("Loading models...")
embedder     = SentenceTransformer("BAAI/bge-small-en-v1.5", local_files_only=True)
reranker     = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", local_files_only=True)
qdrant       = QdrantClient(path="./qdrant_storage")
groq_client  = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("Loading chunks for BM25...")
all_points = qdrant.scroll(collection_name="nyayabot", limit=500)[0]
all_texts  = [p.payload["text"] for p in all_points]
tokenized  = [t.lower().split() for t in all_texts]
bm25       = BM25Okapi(tokenized)
print("API ready!")

# ── Request/Response models ───────────────────────────────────────
class QuestionRequest(BaseModel):
    question: str

class Source(BaseModel):
    title: str
    url: str
    score: float

class AnswerResponse(BaseModel):
    answer: str
    sources: list[Source]

# ── Hybrid search ─────────────────────────────────────────────────
def hybrid_search(query, top_k=5):
    query_vec = embedder.encode(query).tolist()
    dense_response = qdrant.query_points(
        collection_name="nyayabot",
        query=query_vec,
        limit=15
    )
    dense_results = dense_response.points

    tokens      = query.lower().split()
    bm25_scores = bm25.get_scores(tokens)
    top_bm25    = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:15]

    seen, candidates = set(), []
    for r in dense_results:
        if r.payload["text"] not in seen:
            seen.add(r.payload["text"])
            candidates.append(r.payload)
    for i in top_bm25:
        if all_texts[i] not in seen:
            seen.add(all_texts[i])
            candidates.append(all_points[i].payload)

    pairs  = [(query, c["text"]) for c in candidates]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)
    return ranked[:top_k]

# ── Routes ────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "NyayaBot API is running"}


@app.post("/ask", response_model=AnswerResponse)
def ask(body: QuestionRequest):

    # Step 1 — Expand query into formal legal language
    expansion_prompt = f"""Convert this question into formal Indian legal terminology for better search results.
Return ONLY the expanded query, nothing else. Keep it under 30 words.

Question: {body.question}
Expanded legal query:"""

    expansion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": expansion_prompt}],
        max_tokens=60
    )
    expanded_query = expansion.choices[0].message.content.strip()
    print(f"Original: {body.question}")
    print(f"Expanded: {expanded_query}")

    # Step 2 — Search with both original and expanded query, merge results
    results_original = hybrid_search(body.question, top_k=3)
    results_expanded = hybrid_search(expanded_query, top_k=3)

    # Merge and deduplicate
    seen = set()
    merged = []
    for score, payload in results_original + results_expanded:
        if payload["text"] not in seen:
            seen.add(payload["text"])
            merged.append((score, payload))

    # Sort by score and take top 5
    merged = sorted(merged, key=lambda x: x[0], reverse=True)[:5]

    # Step 3 — Generate answer
    context = ""
    sources = []
    for i, (score, payload) in enumerate(merged):
        context += f"[Case {i+1}] {payload.get('title', 'Unknown')}\n{payload['text']}\n\n"
        sources.append(Source(
            title=payload.get("title", "Unknown")[:80],
            url=payload.get("source", ""),
            score=round(float(score), 3)
        ))

    prompt = f"""You are NyayaBot, an Indian legal assistant.
Answer using ONLY the case excerpts below.
Cite cases by title. Use plain English. Keep answer under 200 words.
If cases don't have enough info, say so honestly.

Cases:
{context}

Question: {body.question}

Answer:"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return AnswerResponse(
        answer=response.choices[0].message.content,
        sources=sources
    )