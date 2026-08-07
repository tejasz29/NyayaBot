from sentence_transformers import SentenceTransformer, CrossEncoder
from qdrant_client import QdrantClient
from rank_bm25 import BM25Okapi
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))



# ── Load models ───────────────────────────────────────────────────
print("Loading models...")
embedder = SentenceTransformer("BAAI/bge-small-en-v1.5")
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
client   = QdrantClient(path="./qdrant_storage")

# ── Load all chunks for BM25 ──────────────────────────────────────
print("Loading chunks for BM25...")
all_points = client.scroll(collection_name="nyayabot", limit=500)[0]
all_texts  = [p.payload["text"] for p in all_points]
tokenized  = [t.lower().split() for t in all_texts]
bm25       = BM25Okapi(tokenized)

def hybrid_search(query, top_k=5):
    # Dense search
    query_vec = embedder.encode(query).tolist()
    dense_response = client.query_points(
        collection_name="nyayabot",
        query=query_vec,
        limit=15
    )
    dense_results = dense_response.points

    # BM25 search
    tokens = query.lower().split()
    bm25_scores = bm25.get_scores(tokens)
    top_bm25_indices = sorted(
        range(len(bm25_scores)),
        key=lambda i: bm25_scores[i],
        reverse=True
    )[:15]

    # Merge
    seen = set()
    candidates = []
    for r in dense_results:
        text = r.payload["text"]
        if text not in seen:
            seen.add(text)
            candidates.append(r.payload)
    for i in top_bm25_indices:
        text = all_texts[i]
        if text not in seen:
            seen.add(text)
            candidates.append(all_points[i].payload)

    # Rerank
    pairs  = [(query, c["text"]) for c in candidates]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)

    return ranked[:top_k]

def ask(query):
    print(f"\n{'─'*60}")
    print(f"Question: {query}")
    print(f"{'─'*60}\n")

    results = hybrid_search(query)

    # Build context from top chunks
    context = ""
    sources = []
    for i, (score, payload) in enumerate(results):
        context += f"[Case {i+1}] {payload.get('title', 'Unknown')}\n"
        context += f"{payload['text']}\n\n"
        sources.append({
            "title": payload.get("title", "Unknown"),
            "source": payload.get("source", ""),
            "score": round(float(score), 3)
        })

    # Build prompt
    prompt = f"""You are NyayaBot, an Indian legal assistant.
Answer the user's question using ONLY the case excerpts provided below.
- Cite each case by its title when you use it
- Use plain simple English, not legal jargon
- If the cases don't contain enough information, say so honestly
- Keep the answer under 200 words

Case excerpts:
{context}

Question: {query}

Answer:"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    answer = response.choices[0].message.content

    print("ANSWER:")
    print(answer)
    print("\nSOURCES:")
    for i, s in enumerate(sources):
        print(f"  [{i+1}] {s['title'][:70]}")
        print(f"       {s['source']}")
        print(f"       Relevance score: {s['score']}")

if __name__ == "__main__":
    print("NyayaBot is ready!\n")

    questions = [
        "Can an employer terminate without giving notice?",
        "What are the rights of a dismissed employee?",
    #     "Is verbal termination legally valid in India?"
    ]

    for q in questions:
        ask(q)
        print()