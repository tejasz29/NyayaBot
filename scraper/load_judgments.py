from datasets import load_dataset
import os

SAVE_DIR = "data/"
os.makedirs(SAVE_DIR, exist_ok=True)

for f in os.listdir(SAVE_DIR):
    if f.endswith(".txt"):
        os.remove(f"{SAVE_DIR}{f}")
print("Cleared old data.")

print("Loading full dataset (24k records)...")
ds = load_dataset("viber1/indian-law-dataset", split="train")
print(f"Total: {len(ds)}")

# Topic buckets with keywords
topics = {
    "landlord_tenant": ["landlord", "tenant", "rent", "evict", "security deposit", "lease", "premises", "possession"],
    "employment": ["employer", "employee", "terminat", "dismiss", "retrench", "salary", "wages", "labour", "workman", "notice period", "fired"],
    "criminal": ["arrest", "bail", "fir", "police", "ipc", "accused", "crime", "offence", "custody", "warrant"],
    "consumer": ["consumer", "refund", "defective", "product", "service", "complaint", "forum", "compensation"],
    "property": ["property", "ownership", "transfer", "registration", "sale deed", "mutation", "land"],
    "family": ["divorce", "marriage", "maintenance", "custody", "alimony", "matrimonial", "spouse"],
    "contract": ["contract", "agreement", "breach", "damages", "enforce", "consideration"],
    "cheque": ["cheque", "bounce", "dishonour", "negotiable", "138", "drawee"],
    "accident": ["accident", "motor", "compensation", "negligence", "injury", "death claim"],
    "fraud": ["fraud", "cheat", "misrepresent", "deceit", "forgery", "420"],
}

saved_per_topic = {}
all_saved = []

for topic, keywords in topics.items():
    matches = []
    for item in ds:
        text = (item.get("Instruction", "") + " " + item.get("Response", "")).lower()
        if any(k in text for k in keywords):
            matches.append(item)
        if len(matches) >= 150:  # 150 per topic
            break
    saved_per_topic[topic] = len(matches)
    all_saved.extend(matches[:150])
    print(f"  {topic}: {len(matches)} records")

print(f"\nTotal collected: {len(all_saved)} records")

# Save all
saved = 0
seen = set()
for item in all_saved:
    try:
        question = item.get("Instruction", "").strip()
        answer   = item.get("Response", "").strip()
        if len(answer) < 100 or question in seen:
            continue
        seen.add(question)
        text = f"Question: {question}\n\nAnswer: {answer}"
        with open(f"{SAVE_DIR}judgment_{saved}.txt", "w", encoding="utf-8") as f:
            f.write(f"SOURCE: https://huggingface.co/datasets/viber1/indian-law-dataset\nTITLE: {question[:100]}\n\n{text}")
        saved += 1
    except:
        continue

print(f"Saved {saved} topic-specific records to data/")