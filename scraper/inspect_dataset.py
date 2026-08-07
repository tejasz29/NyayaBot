from datasets import load_dataset

dataset = load_dataset("viber1/indian-law-dataset", split="train")

print(f"Total records: {len(dataset)}")
print(f"\nColumn names: {dataset.column_names}")
print(f"\nFirst record:")

item = dataset[0]
for key, value in item.items():
    val_str = str(value)[:200]
    print(f"  {key}: {val_str}")