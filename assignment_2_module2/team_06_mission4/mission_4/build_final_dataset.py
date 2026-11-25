
import numpy as np
import csv
from pathlib import Path
from collections import Counter

RESULTS = Path("team_06_mission4/results")

INPUT = RESULTS / "continuous_loss_dataset.npz"
OUTPUT = RESULTS / "mission4_final_dataset.npz"
CSV_OUTPUT = RESULTS / "mission4_final_dataset.csv"

# Load the original, unfiltered dataset
data = np.load(INPUT, allow_pickle=True)

features = data["features"]
labels = data["labels"]
clip_ids = data["clip_id"]
first_samples = data["first_sample"]
statuses = data["frame_status"]

# Keep only frames belonging entirely to one clip
mask = statuses == "single_clip"

X = features[mask]
y = labels[mask]
clip_id = clip_ids[mask]
first_sample = first_samples[mask]

# Validate the filtered dataset
assert len(X) == len(y) == len(clip_id) == len(first_sample)
assert np.all(clip_id >= 0)
assert np.isfinite(X).all()

# Save compressed NumPy dataset
np.savez_compressed(
    OUTPUT,
    features=X.astype(np.float32),
    labels=y,
    clip_id=clip_id.astype(np.int32),
    first_sample=first_sample.astype(np.int64)
)

# Save a CSV with metadata and all 40 feature values
feature_columns = [f"feature_{i:02d}" for i in range(X.shape[1])]
columns = ["label", "clip_id", "first_sample"] + feature_columns

with open(CSV_OUTPUT, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(columns)

    for i in range(len(X)):
        writer.writerow([
            y[i],
            int(clip_id[i]),
            int(first_sample[i]),
            *X[i].tolist()
        ])

print("\n========== FINAL DATASET ==========")
print("Original frames:", len(features))
print("Excluded boundary frames:", int((~mask).sum()))
print("Final supervised frames:", len(X))
print("Feature dimensions:", X.shape)
print("Class distribution:")

for label, count in sorted(Counter(y.tolist()).items()):
    print(f"  {label}: {count}")

print("\nUnique clip IDs:", len(np.unique(clip_id)))
print("Contains NaN:", np.isnan(X).any())
print("Contains Inf:", np.isinf(X).any())

print("\nSaved:")
print(OUTPUT)
print(CSV_OUTPUT)
print("===================================")
