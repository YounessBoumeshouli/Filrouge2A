"""
prepare_price_data.py
─────────────────────
Flattens the marrakech_dataset/<category>/{bing,google}/ structure into
a Keras-friendly  data/price/{train,val,test}/<category>/  layout.

Split ratios: 70% train | 15% val | 15% test  (stratified per source)

Usage:
    python prepare_price_data.py
    python prepare_price_data.py --raw ../../marrakech_dataset --out ../data/price
"""

import os
import shutil
import random
import argparse
import json
from pathlib import Path

CATEGORIES = ["argan", "crafts", "jewelry", "lanterns",
              "leather", "price_tags", "spices", "textiles"]

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def collect_images(raw_dir: Path, category: str) -> list[Path]:
    """Gather all images from bing/ and google/ sub-folders."""
    images = []
    cat_path = raw_dir / category
    for source in ("bing", "google"):
        source_path = cat_path / source
        if source_path.exists():
            for f in sorted(source_path.iterdir()):
                if f.suffix.lower() in IMAGE_EXTS:
                    images.append(f)
    return images


def split_images(images: list, train_ratio=0.70, val_ratio=0.15):
    """Deterministic random split – shuffled with fixed seed."""
    random.seed(42)
    shuffled = images[:]
    random.shuffle(shuffled)
    n = len(shuffled)
    n_train = int(n * train_ratio)
    n_val   = int(n * val_ratio)
    train   = shuffled[:n_train]
    val     = shuffled[n_train:n_train + n_val]
    test    = shuffled[n_train + n_val:]
    return train, val, test


def prepare(raw_dir: Path, out_dir: Path, overwrite: bool = False):
    stats = {}
    for category in CATEGORIES:
        images = collect_images(raw_dir, category)
        if not images:
            print(f"  [WARNING] No images found for category: {category}")
            continue

        train, val, test = split_images(images)
        stats[category] = {"train": len(train), "val": len(val),
                           "test": len(test), "total": len(images)}

        for split_name, split_imgs in [("train", train), ("val", val), ("test", test)]:
            dest_dir = out_dir / split_name / category
            dest_dir.mkdir(parents=True, exist_ok=True)
            for img_path in split_imgs:
                dest_file = dest_dir / img_path.name
                if overwrite or not dest_file.exists():
                    shutil.copy2(img_path, dest_file)

    # print summary table
    print("\n" + "=" * 55)
    print(f"{'Category':<14} {'Train':>7} {'Val':>7} {'Test':>7} {'Total':>7}")
    print("-" * 55)
    grand = {"train": 0, "val": 0, "test": 0, "total": 0}
    for cat, s in stats.items():
        print(f"{cat:<14} {s['train']:>7} {s['val']:>7} {s['test']:>7} {s['total']:>7}")
        for k in grand:
            grand[k] += s[k]
    print("-" * 55)
    print(f"{'TOTAL':<14} {grand['train']:>7} {grand['val']:>7} {grand['test']:>7} {grand['total']:>7}")
    print("=" * 55)
    print(f"\n✓ Dataset prepared at: {out_dir.resolve()}")

    # save metadata
    info = {"categories": CATEGORIES, "splits": stats, "totals": grand}
    with open(out_dir / "dataset_info.json", "w") as f:
        json.dump(info, f, indent=2)

    return stats


def main():
    parser = argparse.ArgumentParser(description="Prepare Marrakech price dataset")
    parser.add_argument("--raw", default="../../marrakech_dataset",
                        help="Path to raw marrakech_dataset folder")
    parser.add_argument("--out", default="../data/price",
                        help="Output directory for train/val/test splits")
    parser.add_argument("--overwrite", action="store_true",
                        help="Re-copy images even if destination already exists")
    args = parser.parse_args()

    raw_dir = Path(args.raw)
    out_dir = Path(args.out)

    if not raw_dir.exists():
        print(f"[ERROR] Raw dataset not found at: {raw_dir.resolve()}")
        print("  Expected structure: marrakech_dataset/<category>/{bing,google}/")
        return

    print(f"Preparing dataset from: {raw_dir.resolve()}")
    prepare(raw_dir, out_dir, overwrite=args.overwrite)


if __name__ == "__main__":
    main()
