from datasets import load_dataset
import os

SAVE_DIR = "data/"
os.makedirs(SAVE_DIR, exist_ok=True)

for f in os.listdir(SAVE_DIR):
    if f.endswith(".txt"):
        os.remove(f"{SAVE_DIR}{f}")
print("Cleared old data.")

saved = 0

# Dataset 1 — Indian Law Q&A (1000 records)
print("Loading Dataset 1: viber1/indian-law-dataset...")
ds1 = load_dataset("viber1/indian-law-dataset", split="train")
print(f"Records: {len(ds1)}")

for i, item in enumerate(ds1):
    try:
        question = item.get("Instruction", "").strip()
        answer   = item.get("Response", "").strip()
        if len(answer) < 100:
            continue
        text = f"Question: {question}\n\nAnswer: {answer}"
        with open(f"{SAVE_DIR}judgment_{saved}.txt", "w", encoding="utf-8") as f:
            f.write(f"SOURCE: https://huggingface.co/datasets/viber1/indian-law-dataset\nTITLE: {question[:100]}\n\n{text}")
        saved += 1
        if saved >= 1000:
            break
    except:
        continue
print(f"Saved {saved} records from Dataset 1")

# Dataset 2 — Lawyer GPT India (realistic case scenarios)
print("\nLoading Dataset 2: nisaar/Lawyer_GPT_India...")
ds2 = load_dataset("nisaar/Lawyer_GPT_India", split="train")
print(f"Records: {len(ds2)}")

start = saved
for i, item in enumerate(ds2):
    try:
        question = item.get("question", "").strip()
        answer   = item.get("answer", "").strip()
        if len(answer) < 100:
            continue
        text = f"Question: {question}\n\nAnswer: {answer}"
        with open(f"{SAVE_DIR}judgment_{saved}.txt", "w", encoding="utf-8") as f:
            f.write(f"SOURCE: https://huggingface.co/datasets/nisaar/Lawyer_GPT_India\nTITLE: {question[:100]}\n\n{text}")
        saved += 1
        if saved - start >= 1000:
            break
    except:
        continue
print(f"Saved {saved - start} records from Dataset 2")

print(f"\nTotal saved: {saved} records to data/")