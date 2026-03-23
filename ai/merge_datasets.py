"""
Merge and remap multiple rice datasets into a single YOLOv8-compatible dataset.

Class mapping:
  0 = Full  (whole, sound grains)
  1 = Broken (broken, unsound grains)

Sources:
  - generated_train       : already labeled (0=Full, 1=Broken)
  - Rice-Quality 3        : remap sound/whole-chalky→0, broken-chalky/broken-clear/unsound→1, skip rest
  - Counting Rice Grains  : all varieties are whole grains → 0 (Full)
"""

import os
import shutil
import random
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent
DATASETS_DIR = BASE / "datasets"
OUTPUT_DIR   = DATASETS_DIR / "merged_dataset"

TRAIN_IMG = OUTPUT_DIR / "train" / "images"
TRAIN_LBL = OUTPUT_DIR / "train" / "labels"
VAL_IMG   = OUTPUT_DIR / "valid" / "images"
VAL_LBL   = OUTPUT_DIR / "valid" / "labels"

for d in [TRAIN_IMG, TRAIN_LBL, VAL_IMG, VAL_LBL]:
    d.mkdir(parents=True, exist_ok=True)

# ── Class remapping definitions ───────────────────────────────────────────────

# Rice-Quality 3: ['broken-chalky','broken-clear','foreign-object','plastic','sound','stone','unsound','whole-chalky']
RICE_QUALITY_MAP = {
    0: 1,   # broken-chalky  → Broken
    1: 1,   # broken-clear   → Broken
    2: None, # foreign-object → skip
    3: None, # plastic        → skip
    4: 0,   # sound          → Full
    5: None, # stone          → skip
    6: 1,   # unsound        → Broken
    7: 0,   # whole-chalky   → Full
}

# Counting Rice Grains: ['Basmati Rice','Brown Rice','Japanese Rice'] → all Full
COUNTING_MAP = {0: 0, 1: 0, 2: 0}

# generated_train: already correct (0=Full, 1=Broken)
GENERATED_MAP = {0: 0, 1: 1}

# ── Helper functions ──────────────────────────────────────────────────────────

def remap_label_file(src_label: Path, class_map: dict) -> list[str]:
    """Read a YOLO label file and remap class IDs. Returns remapped lines."""
    lines = []
    if not src_label.exists():
        return lines
    for line in src_label.read_text().strip().splitlines():
        parts = line.strip().split()
        if not parts:
            continue
        cls = int(parts[0])
        new_cls = class_map.get(cls)
        if new_cls is None:
            continue  # skip this annotation
        lines.append(f"{new_cls} " + " ".join(parts[1:]))
    return lines


def collect_samples(images_dir: Path, labels_dir: Path, class_map: dict, prefix: str):
    """Return list of (image_path, remapped_label_lines, unique_stem) tuples."""
    samples = []
    for img_path in sorted(images_dir.glob("*")):
        if img_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".bmp"}:
            continue
        lbl_path = labels_dir / (img_path.stem + ".txt")
        lines = remap_label_file(lbl_path, class_map)
        if not lines:
            continue  # skip images with no valid annotations after remapping
        stem = f"{prefix}_{img_path.stem}"
        samples.append((img_path, lines, stem, img_path.suffix))
    return samples


def write_sample(img_path: Path, label_lines: list, stem: str, suffix: str,
                 img_dir: Path, lbl_dir: Path):
    shutil.copy2(img_path, img_dir / f"{stem}{suffix}")
    (lbl_dir / f"{stem}.txt").write_text("\n".join(label_lines))


# ── Collect all samples ───────────────────────────────────────────────────────
all_samples = []

# 1. generated_train (existing labeled data)
gen_img = DATASETS_DIR / "generated_train" / "images"
gen_lbl = DATASETS_DIR / "generated_train" / "labels"
all_samples += collect_samples(gen_img, gen_lbl, GENERATED_MAP, "gen")
print(f"generated_train:     {len([s for s in all_samples if s[2].startswith('gen')])} samples")

# 2. Rice-Quality 3
rq3_base = DATASETS_DIR / "Rice-Quality 3.v4i.yolov8"
before = len(all_samples)
for split in ["train", "valid", "test"]:
    img_d = rq3_base / split / "images"
    lbl_d = rq3_base / split / "labels"
    if img_d.exists():
        all_samples += collect_samples(img_d, lbl_d, RICE_QUALITY_MAP, f"rq3_{split}")
print(f"Rice-Quality 3:      {len(all_samples) - before} samples")

# 3. Counting Rice Grains
crg_base = DATASETS_DIR / "Counting Rice Grains.v9i.yolov8"
before = len(all_samples)
for split in ["train", "valid", "test"]:
    img_d = crg_base / split / "images"
    lbl_d = crg_base / split / "labels"
    if img_d.exists():
        all_samples += collect_samples(img_d, lbl_d, COUNTING_MAP, f"crg_{split}")
print(f"Counting Rice Grains:{len(all_samples) - before} samples")

print(f"\nTotal samples collected: {len(all_samples)}")

# ── Train / Val split (80/20) ─────────────────────────────────────────────────
random.seed(42)
random.shuffle(all_samples)

split_idx  = int(len(all_samples) * 0.8)
train_set  = all_samples[:split_idx]
val_set    = all_samples[split_idx:]

print(f"Train: {len(train_set)} | Val: {len(val_set)}")

# ── Write files ───────────────────────────────────────────────────────────────
for img_path, label_lines, stem, suffix in train_set:
    write_sample(img_path, label_lines, stem, suffix, TRAIN_IMG, TRAIN_LBL)

for img_path, label_lines, stem, suffix in val_set:
    write_sample(img_path, label_lines, stem, suffix, VAL_IMG, VAL_LBL)

# ── Write data.yaml ───────────────────────────────────────────────────────────
yaml_content = f"""path: {OUTPUT_DIR}
train: train/images
val: valid/images

nc: 2
names:
  0: Full
  1: Broken
"""
(OUTPUT_DIR / "data.yaml").write_text(yaml_content)

# ── Class distribution stats ──────────────────────────────────────────────────
full_count = broken_count = 0
for _, lines, _, _ in all_samples:
    for line in lines:
        cls = int(line.split()[0])
        if cls == 0:
            full_count += 1
        else:
            broken_count += 1

print(f"\nAnnotation breakdown:")
print(f"  Full grains:   {full_count}")
print(f"  Broken grains: {broken_count}")
print(f"\nMerged dataset written to: {OUTPUT_DIR}")
print("Ready to train!")
