from sentence_transformers import SentenceTransformer, CrossEncoder
from qdrant_client import QdrantClient
from rank_bm25 import BM25Okapi
import os

# ── Load models ──────────────────────────────────────────────────
print("Loading models...")
embedder = SentenceTransformer("BAAI/bge-small-en-v1.5")
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
client   = QdrantClient(path="./qdrant_storage")

# ── Load all chunks into memory for BM25 ─────────────────────────
print("Loading chunks for BM25...")
all_points = client.scroll(collection_name="nyayabot", limit=500)[0]
all_texts  = [p.payload["text"] for p in all_points]
tokenized  = [t.lower().split() for t in all_texts]
bm25       = BM25Okapi(tokenized)

def hybrid_search(query, top_k=5):
    # 1. Dense search (semantic)
    query_vec = embedder.encode(query).tolist()
    dense_response = client.query_points(
        collection_name="nyayabot",
        query=query_vec,
        limit=15
    )
    dense_results = dense_response.points

    # 2. Sparse search (BM25 keyword)
    tokens = query.lower().split()
    bm25_scores = bm25.get_scores(tokens)
    top_bm25_indices = sorted(
        range(len(bm25_scores)),
        key=lambda i: bm25_scores[i],
        reverse=True
    )[:15]

    # 3. Merge both result sets (deduplicate by text)
    seen  = set()
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

    # 4. Rerank all candidates
    pairs  = [(query, c["text"]) for c in candidates]
    scores = reranker.predict(pairs)

    ranked = sorted(
        zip(scores, candidates),
        key=lambda x: x[0],
        reverse=True
    )

    return ranked[:top_k]

def ask(query):
    print(f"\n{'─'*60}")
    print(f"Question: {query}")
    print(f"{'─'*60}")

    results = hybrid_search(query)

    print(f"\nTop {len(results)} relevant chunks:\n")
    for i, (score, payload) in enumerate(results):
        print(f"[{i+1}] Score: {score:.3f}")
        print(f"     Title:  {payload.get('title', 'N/A')[:70]}")
        print(f"     Source: {payload.get('source', 'N/A')}")
        print(f"     Text:   {payload['text'][:200]}...")
        print()

if __name__ == "__main__":
    # Test queries
    ask("Can an employer terminate without giving notice?")
    ask("What are the rights of a dismissed employee?")