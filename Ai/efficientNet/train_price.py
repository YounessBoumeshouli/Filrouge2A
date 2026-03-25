"""
train_price.py
──────────────
One-shot runner: prepare dataset → train → done.

Usage:
    python train_price.py                    # full pipeline
    python train_price.py --skip-prepare     # skip data prep (already done)
    python train_price.py --skip-finetune    # skip Phase-2 fine-tuning
    python train_price.py --epochs 15 --batch 8   # quick test run
"""

import argparse
import os
import sys
from pathlib import Path

# ── Paths (relative to this script's directory) ──────────────
SCRIPT_DIR  = Path(__file__).parent
RAW_DATASET = str(SCRIPT_DIR / ".." / ".." / "marrakech_dataset")
DATA_DIR    = str(SCRIPT_DIR / ".." / "data" / "price")
MODELS_DIR  = str(SCRIPT_DIR / ".." / "models")


def step_prepare(raw: str, out: str, overwrite: bool):
    """Run the dataset preparation step."""
    from prepare_price_data import prepare
    raw_p = Path(raw)
    out_p = Path(out)
    if not raw_p.exists():
        print(f"[ERROR] Raw dataset not found: {raw_p.resolve()}")
        sys.exit(1)
    print(f"\n{'='*55}")
    print("  STEP 1 / 2 — Preparing dataset")
    print(f"{'='*55}")
    prepare(raw_p, out_p, overwrite=overwrite)


def step_train(data_dir: str, models_dir: str, epochs: int,
               ft_epochs: int, batch: int, skip_finetune: bool):
    """Run the training step."""
    from train_price_model import train
    print(f"\n{'='*55}")
    print("  STEP 2 / 2 — Training EfficientNetB0")
    print(f"{'='*55}")
    acc = train(
        data_dir=data_dir,
        models_dir=models_dir,
        epochs=epochs,
        ft_epochs=ft_epochs,
        batch_size=batch,
        skip_finetune=skip_finetune,
    )
    return acc


def main():
    parser = argparse.ArgumentParser(
        description="End-to-end training pipeline for Marrakech product classifier"
    )
    parser.add_argument("--raw",          default=RAW_DATASET,
                        help="Raw marrakech_dataset path")
    parser.add_argument("--data",         default=DATA_DIR,
                        help="Prepared train/val/test output path")
    parser.add_argument("--models-dir",   default=MODELS_DIR,
                        help="Where to save model files")
    parser.add_argument("--epochs",       type=int, default=25,
                        help="Phase-1 training epochs (default: 25)")
    parser.add_argument("--ft-epochs",   type=int, default=15,
                        help="Phase-2 fine-tuning epochs (default: 15)")
    parser.add_argument("--batch",        type=int, default=16,
                        help="Batch size (default: 16)")
    parser.add_argument("--skip-prepare", action="store_true",
                        help="Skip dataset preparation (use existing split)")
    parser.add_argument("--skip-finetune",action="store_true",
                        help="Skip Phase-2 fine-tuning")
    parser.add_argument("--overwrite",    action="store_true",
                        help="Overwrite existing prepared images")
    args = parser.parse_args()

    print("\n╔══════════════════════════════════════════════════════╗")
    print("║  Tourist Helper — Price Classifier Training Pipeline  ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"  Raw dataset : {Path(args.raw).resolve()}")
    print(f"  Data dir    : {Path(args.data).resolve()}")
    print(f"  Models dir  : {Path(args.models_dir).resolve()}")
    print(f"  Epochs      : {args.epochs}  (fine-tune: {args.ft_epochs})")
    print(f"  Batch size  : {args.batch}")

    # Step 1
    if not args.skip_prepare:
        step_prepare(args.raw, args.data, args.overwrite)
    else:
        print("\n[INFO] Skipping data preparation (--skip-prepare).")
        if not Path(args.data).exists():
            print(f"[ERROR] Data dir not found: {args.data}")
            print("  Remove --skip-prepare to generate it.")
            sys.exit(1)

    # Step 2
    acc = step_train(
        data_dir=args.data,
        models_dir=args.models_dir,
        epochs=args.epochs,
        ft_epochs=args.ft_epochs,
        batch=args.batch,
        skip_finetune=args.skip_finetune,
    )

    print("\n╔══════════════════════════════════════════════════════╗")
    print(f"║  Pipeline complete!  Final test accuracy: {acc*100:5.2f}%      ║")
    print("╚══════════════════════════════════════════════════════╝\n")


if __name__ == "__main__":
    main()
