from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
import os
import uuid

DATA_DIR = "data/"
COLLECTION = "nyayabot"

print("Loading embedding model... (first time takes 2-3 mins to download)")
model = SentenceTransformer("BAAI/bge-small-en-v1.5")  # smaller/faster than bge-m3

client = QdrantClient(path="./qdrant_storage")

try:
    client.delete_collection(COLLECTION)
except:
    pass

client.create_collection(
    collection_name=COLLECTION,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
    separators=["\n\n", "\n", ".", " "]
)

all_chunks = []
all_metadata = []

print("Reading and chunking judgment files...")
for filename in os.listdir(DATA_DIR):
    if not filename.endswith(".txt"):
        continue

    with open(f"{DATA_DIR}{filename}", encoding="utf-8") as f:
        text = f.read()

    lines = text.split("\n")
    source_url = lines[0].replace("SOURCE: ", "").strip()
    title = lines[1].replace("TITLE: ", "").strip() if len(lines) > 1 else filename

    chunks = splitter.split_text(text)
    for chunk in chunks:
        all_chunks.append(chunk)
        all_metadata.append({
            "source": source_url,
            "title": title,
            "file": filename
        })

print(f"Total chunks to embed: {len(all_chunks)}")
print("Embedding... (this takes a few minutes)")

vectors = model.encode(
    all_chunks,
    show_progress_bar=True,
    batch_size=32
)

print("Storing in Qdrant...")
points = [
    PointStruct(
        id=str(uuid.uuid4()),
        vector=vectors[i].tolist(),
        payload={
            "text": all_chunks[i],
            **all_metadata[i]
        }
    )
    for i in range(len(all_chunks))
]

client.upsert(collection_name=COLLECTION, points=points)
print(f"\nDone! Stored {len(points)} chunks from {len(os.listdir(DATA_DIR))} judgments.")