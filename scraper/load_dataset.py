from datasets import load_dataset
import os

SAVE_DIR = "data/"
os.makedirs(SAVE_DIR, exist_ok=True)

for f in os.listdir(SAVE_DIR):
    if f.endswith(".txt"):
        os.remove(f"{SAVE_DIR}{f}")
print("Cleared old data.")

print("Loading dataset...")
dataset = load_dataset("viber1/indian-law-dataset", split="train")
print(f"Total records: {len(dataset)}")

saved = 0
for i, item in enumerate(dataset):
    try:
        question = item.get("Instruction", "").strip()
        answer   = item.get("Response", "").strip()

        if len(answer) < 100:
            continue

        # Store as Q&A pair so retrieval finds relevant legal answers
        text = f"Question: {question}\n\nAnswer: {answer}"

        with open(f"{SAVE_DIR}judgment_{saved}.txt", "w", encoding="utf-8") as f:
            f.write(f"SOURCE: huggingface/viber1/indian-law-dataset\nTITLE: {question[:100]}\n\n{text}")

        saved += 1

        if saved % 200 == 0:
            print(f"Saved {saved} records...")

        if saved >= 1000:
            break

    except Exception as e:
        continue

print(f"\nDone! Saved {saved} legal Q&A records to data/")