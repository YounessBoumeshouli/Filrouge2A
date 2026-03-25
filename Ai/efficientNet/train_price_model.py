"""
train_price_model.py
────────────────────
EfficientNetB0 transfer-learning pipeline for the Marrakech souk
**product** classifier (8 classes for the Price Helper feature).

Two-phase training:
  Phase 1 – Frozen base model, train only the classification head.
  Phase 2 – Fine-tune: unfreeze last N layers with a smaller LR.

Usage:
    python train_price_model.py
    python train_price_model.py --data ../data/price --epochs 25 --batch 16
    python train_price_model.py --skip-finetune
"""

import os
import sys
import json
import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")   # headless backend (no display required)
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import (Dense, GlobalAveragePooling2D,
                                     Dropout, BatchNormalization)
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import (EarlyStopping, ReduceLROnPlateau,
                                        ModelCheckpoint, TensorBoard)
from pathlib import Path

# ─────────────────────────────────────────────────────────────
#  Default paths  (relative to effiientNet/ directory)
# ─────────────────────────────────────────────────────────────
DEFAULT_DATA_DIR   = "../data/price"
DEFAULT_MODELS_DIR = "../models"
IMG_SIZE           = 224
NUM_CLASSES        = 8


# ─────────────────────────────────────────────────────────────
#  Model
# ─────────────────────────────────────────────────────────────

def build_model(num_classes: int = NUM_CLASSES, img_size: int = IMG_SIZE) -> Model:
    """Build EfficientNetB0 with a custom classification head."""
    base = EfficientNetB0(
        weights="imagenet",
        include_top=False,
        input_shape=(img_size, img_size, 3)
    )
    base.trainable = False  # Phase 1: frozen

    x = base.output
    x = GlobalAveragePooling2D()(x)
    x = BatchNormalization()(x)
    x = Dropout(0.3)(x)
    x = Dense(256, activation="relu")(x)
    x = Dropout(0.2)(x)
    outputs = Dense(num_classes, activation="softmax")(x)

    model = Model(inputs=base.input, outputs=outputs)
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model


def unfreeze_model(model: Model, unfreeze_layers: int = 50, lr: float = 1e-4):
    """Unfreeze the last N layers of the EfficientNet base for fine-tuning."""
    base = model.layers[0]          # EfficientNetB0 sub-model
    if hasattr(base, 'layers'):
        base.trainable = True
        for layer in base.layers[:-unfreeze_layers]:
            layer.trainable = False
    else:
        base.trainable = True
    model.compile(
        optimizer=Adam(learning_rate=lr),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )
    print(f"  Unfrozen last {unfreeze_layers} layers of EfficientNetB0 for fine-tuning.")
    return model


# ─────────────────────────────────────────────────────────────
#  Data generators
# ─────────────────────────────────────────────────────────────

def make_generators(data_dir: str, batch_size: int, img_size: int = IMG_SIZE):
    """Return (train_gen, val_gen, test_gen, class_indices)."""
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.15,
        zoom_range=0.2,
        horizontal_flip=True,
        brightness_range=[0.8, 1.2],
        fill_mode="nearest"
    )
    val_datagen = ImageDataGenerator(rescale=1.0 / 255)

    train_gen = train_datagen.flow_from_directory(
        os.path.join(data_dir, "train"),
        target_size=(img_size, img_size),
        batch_size=batch_size,
        class_mode="categorical",
        shuffle=True
    )
    val_gen = val_datagen.flow_from_directory(
        os.path.join(data_dir, "val"),
        target_size=(img_size, img_size),
        batch_size=batch_size,
        class_mode="categorical",
        shuffle=False
    )
    test_gen = val_datagen.flow_from_directory(
        os.path.join(data_dir, "test"),
        target_size=(img_size, img_size),
        batch_size=batch_size,
        class_mode="categorical",
        shuffle=False
    )
    return train_gen, val_gen, test_gen, train_gen.class_indices


# ─────────────────────────────────────────────────────────────
#  Training helpers
# ─────────────────────────────────────────────────────────────

def make_callbacks(checkpoint_path: str, log_dir: str, patience: int = 5):
    return [
        EarlyStopping(patience=patience, restore_best_weights=True,
                      monitor="val_accuracy", verbose=1),
        ReduceLROnPlateau(factor=0.3, patience=3, min_lr=1e-7,
                          monitor="val_loss", verbose=1),
        ModelCheckpoint(checkpoint_path, save_best_only=True,
                        monitor="val_accuracy", verbose=1),
        TensorBoard(log_dir=log_dir, histogram_freq=0)
    ]


def plot_history(histories: list, labels: list, save_path: str):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for hist, lbl in zip(histories, labels):
        # Handle different history key names
        acc_key = 'accuracy' if 'accuracy' in hist.history else 'acc'
        val_acc_key = 'val_accuracy' if 'val_accuracy' in hist.history else 'val_acc'
        
        axes[0].plot(hist.history[acc_key],    label=f"{lbl} train acc")
        axes[0].plot(hist.history[val_acc_key],label=f"{lbl} val acc", linestyle="--")
        axes[1].plot(hist.history["loss"],         label=f"{lbl} train loss")
        axes[1].plot(hist.history["val_loss"],     label=f"{lbl} val loss", linestyle="--")
    for ax, title in zip(axes, ["Accuracy", "Loss"]):
        ax.set_title(title)
        ax.set_xlabel("Epoch")
        ax.legend()
        ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=120)
    print(f"  Training curves saved → {save_path}")


# ─────────────────────────────────────────────────────────────
#  Main training function
# ─────────────────────────────────────────────────────────────

def train(data_dir: str, models_dir: str, epochs: int, ft_epochs: int,
          batch_size: int, skip_finetune: bool):

    models_path = Path(models_dir)
    models_path.mkdir(parents=True, exist_ok=True)

    model_save        = str(models_path / "price_efficientnet.h5")
    finetuned_save    = str(models_path / "price_efficientnet_finetuned.h5")
    class_indices_out = str(models_path / "price_class_indices.json")
    history_plot      = str(models_path / "training_history.png")
    log_dir           = str(models_path / "logs")

    # ── Data ────────────────────────────────────────────────
    print("\n[1/4] Loading data generators …")
    train_gen, val_gen, test_gen, class_indices = make_generators(
        data_dir, batch_size)

    print(f"  Classes ({len(class_indices)}): {list(class_indices.keys())}")
    print(f"  Train batches : {len(train_gen)}")
    print(f"  Val   batches : {len(val_gen)}")
    print(f"  Test  batches : {len(test_gen)}")

    # ── Build model ────────────────────────────────────────
    print("\n[2/4] Building EfficientNetB0 model …")
    model = build_model(num_classes=len(class_indices))
    model.summary(line_length=90)

    # ── Phase 1: Transfer learning ─────────────────────────
    print(f"\n[3/4] Phase 1 – Transfer learning ({epochs} epochs max) …")
    callbacks_p1 = make_callbacks(model_save, os.path.join(log_dir, "phase1"))
    hist1 = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=epochs,
        callbacks=callbacks_p1,
        verbose=1
    )
    model.save(model_save)
    print(f"  ✓ Phase-1 model saved → {model_save}")

    # Save class indices
    with open(class_indices_out, "w") as f:
        idx_to_class = {v: k for k, v in class_indices.items()}
        json.dump(idx_to_class, f, indent=2)
    print(f"  ✓ Class indices saved → {class_indices_out}")

    histories = [hist1]
    labels    = ["Phase-1"]

    # ── Phase 2: Fine-tuning ──────────────────────────────
    if not skip_finetune:
        print(f"\n[4/4] Phase 2 – Fine-tuning ({ft_epochs} epochs max) …")
        model = tf.keras.models.load_model(model_save)
        model = unfreeze_model(model, unfreeze_layers=50, lr=1e-4)
        callbacks_p2 = make_callbacks(finetuned_save, os.path.join(log_dir, "phase2"),
                                      patience=5)
        hist2 = model.fit(
            train_gen,
            validation_data=val_gen,
            epochs=ft_epochs,
            callbacks=callbacks_p2,
            verbose=1
        )
        model.save(finetuned_save)
        print(f"  ✓ Fine-tuned model saved → {finetuned_save}")
        histories.append(hist2)
        labels.append("Phase-2")
        best_model_path = finetuned_save
    else:
        print("\n[4/4] Fine-tuning skipped (--skip-finetune).")
        best_model_path = model_save

    # ── Evaluation on test set ─────────────────────────────
    print("\n── Test-set evaluation ─────────────────────────────")
    best_model = tf.keras.models.load_model(best_model_path)
    loss, acc = best_model.evaluate(test_gen, verbose=1)
    print(f"  Test Loss     : {loss:.4f}")
    print(f"  Test Accuracy : {acc:.4f}  ({acc*100:.2f}%)")

    # ── Plot ───────────────────────────────────────────────
    plot_history(histories, labels, history_plot)

    print("\n══════════════════════════════════════════════════")
    print("  Training complete!")
    print(f"  Best model  : {best_model_path}")
    print(f"  Class map   : {class_indices_out}")
    print(f"  History plot: {history_plot}")
    print("══════════════════════════════════════════════════\n")

    return acc


# ─────────────────────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train EfficientNetB0 price classifier")
    parser.add_argument("--data",          default=DEFAULT_DATA_DIR,
                        help="Path to prepared train/val/test dataset")
    parser.add_argument("--models-dir",    default=DEFAULT_MODELS_DIR,
                        help="Directory to save models and artefacts")
    parser.add_argument("--epochs",        type=int, default=25,
                        help="Max epochs for Phase 1")
    parser.add_argument("--ft-epochs",     type=int, default=15,
                        help="Max epochs for Phase 2 fine-tuning")
    parser.add_argument("--batch",         type=int, default=16,
                        help="Batch size")
    parser.add_argument("--skip-finetune", action="store_true",
                        help="Skip Phase 2 fine-tuning")
    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"[ERROR] Data directory not found: {args.data}")
        print("  Run prepare_price_data.py first.")
        sys.exit(1)

    train(
        data_dir=args.data,
        models_dir=args.models_dir,
        epochs=args.epochs,
        ft_epochs=args.ft_epochs,
        batch_size=args.batch,
        skip_finetune=args.skip_finetune
    )
