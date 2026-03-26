#!/usr/bin/env python3
"""
Dataset Validator for YOLO Training
===================================

Validates the dataset before training to ensure everything is ready.
"""

from pathlib import Path
import json


def validate_dataset(images_root):
    """Validate the complete dataset"""

    print("🔍 DATASET VALIDATION")
    print("=" * 50)

    images_root = Path(images_root)

    # Find all product and label folders
    product_folders = [
        f for f in images_root.iterdir() if f.is_dir() and f.name.startswith("product_")
    ]
    label_folders = [
        f for f in images_root.iterdir() if f.is_dir() and f.name.startswith("labels_")
    ]

    print(f"📁 Product folders: {len(product_folders)}")
    print(f"🏷️ Label folders: {len(label_folders)}")

    # Validate each product
    validation_results = {}
    total_pairs = 0
    total_issues = 0

    for product_folder in product_folders:
        print(f"\n📦 Validating {product_folder.name}...")

        # Extract product ID
        parts = product_folder.name.split("_", 2)
        if len(parts) < 2:
            print("  ❌ Invalid folder name format")
            continue

        product_id = parts[1]
        product_name = parts[2] if len(parts) > 2 else f"Product_{product_id}"

        # Find corresponding label folder
        label_folder = None
        for lf in label_folders:
            if f"product_{product_id}_" in lf.name:
                label_folder = lf
                break

        if not label_folder:
            print("  ❌ No corresponding label folder found")
            total_issues += 1
            continue

        print(f"  🏷️ Label folder: {label_folder.name}")

        # Count files
        image_extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}
        images = [
            f
            for f in product_folder.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ]
        labels = [
            f
            for f in label_folder.iterdir()
            if f.is_file() and f.suffix.lower() == ".txt"
        ]

        print(f"  📸 Images: {len(images)}")
        print(f"  🏷️ Labels: {len(labels)}")

        # Check for matched pairs
        matched_pairs = 0
        orphaned_images = []
        orphaned_labels = []
        invalid_labels = []

        # Check images for corresponding labels
        for img in images:
            label_file = label_folder / f"{img.stem}.txt"
            if label_file.exists():
                # Validate label format
                try:
                    with open(label_file, "r") as f:
                        lines = f.readlines()

                    valid_lines = 0
                    for line in lines:
                        line = line.strip()
                        if line:
                            parts = line.split()
                            if len(parts) >= 5:
                                # Check if coordinates are valid (0-1 range)
                                coords = [float(x) for x in parts[1:5]]
                                if all(0 <= x <= 1 for x in coords):
                                    valid_lines += 1
                                else:
                                    invalid_labels.append(
                                        f"{label_file.name}: invalid coordinates"
                                    )
                            else:
                                invalid_labels.append(
                                    f"{label_file.name}: insufficient data"
                                )

                    if valid_lines > 0:
                        matched_pairs += 1
                    else:
                        invalid_labels.append(
                            f"{label_file.name}: no valid annotations"
                        )

                except Exception as e:
                    invalid_labels.append(f"{label_file.name}: read error - {e}")
            else:
                orphaned_images.append(img.name)

        # Check labels for corresponding images
        for label in labels:
            img_found = False
            for ext in image_extensions:
                if (product_folder / f"{label.stem}{ext}").exists():
                    img_found = True
                    break
            if not img_found:
                orphaned_labels.append(label.name)

        # Report results
        print(f"  ✅ Matched pairs: {matched_pairs}")

        if orphaned_images:
            print(f"  ⚠️ Images without labels: {len(orphaned_images)}")
            if len(orphaned_images) <= 3:
                for img in orphaned_images:
                    print(f"     - {img}")
            else:
                print(
                    f"     - {orphaned_images[0]} (and {len(orphaned_images)-1} more)"
                )

        if orphaned_labels:
            print(f"  ⚠️ Labels without images: {len(orphaned_labels)}")
            if len(orphaned_labels) <= 3:
                for lbl in orphaned_labels:
                    print(f"     - {lbl}")
            else:
                print(
                    f"     - {orphaned_labels[0]} (and {len(orphaned_labels)-1} more)"
                )

        if invalid_labels:
            print(f"  ❌ Invalid labels: {len(invalid_labels)}")
            for inv in invalid_labels[:3]:  # Show first 3
                print(f"     - {inv}")
            if len(invalid_labels) > 3:
                print(f"     - ... and {len(invalid_labels)-3} more")

        # Store results
        validation_results[product_id] = {
            "name": product_name,
            "images": len(images),
            "labels": len(labels),
            "matched_pairs": matched_pairs,
            "orphaned_images": len(orphaned_images),
            "orphaned_labels": len(orphaned_labels),
            "invalid_labels": len(invalid_labels),
        }

        total_pairs += matched_pairs
        total_issues += (
            len(orphaned_images) + len(orphaned_labels) + len(invalid_labels)
        )

    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    print(f"📦 Products validated: {len(validation_results)}")
    print(f"✅ Total valid pairs: {total_pairs}")
    print(f"⚠️ Total issues: {total_issues}")

    # Detailed breakdown
    print("\n📋 DETAILED BREAKDOWN:")
    for product_id, results in validation_results.items():
        status = "✅" if results["matched_pairs"] > 0 else "❌"
        print(f"{status} {results['name']}: {results['matched_pairs']} pairs")

    # Training readiness
    print("\n🚀 TRAINING READINESS:")
    if total_pairs >= 50:
        print("✅ Dataset is ready for training!")
        print(f"   - {total_pairs} valid image-label pairs")
        print(f"   - {len(validation_results)} product categories")
    elif total_pairs >= 20:
        print("⚠️ Dataset is minimal but trainable")
        print(f"   - {total_pairs} valid pairs (recommend 50+)")
        print("   - Consider adding more data for better results")
    else:
        print("❌ Dataset too small for effective training")
        print(f"   - Only {total_pairs} valid pairs (need 20+ minimum)")
        print("   - Add more labeled data before training")

    if total_issues > 0:
        print(f"⚠️ {total_issues} issues found - consider fixing before training")

    # Save validation report
    report_path = Path("dataset_validation_report.json")
    with open(report_path, "w") as f:
        json.dump(
            {
                "summary": {
                    "total_products": len(validation_results),
                    "total_valid_pairs": total_pairs,
                    "total_issues": total_issues,
                    "training_ready": total_pairs >= 20,
                },
                "products": validation_results,
            },
            f,
            indent=2,
        )

    print(f"\n📄 Validation report saved: {report_path}")

    return total_pairs >= 20, validation_results


def main():
    IMAGES_ROOT = r"c:\Users\boume\Briefs\Filrouge2A\images"

    print("🏺 Dataset Validator for YOLO Training")
    print("=" * 50)

    ready, results = validate_dataset(IMAGES_ROOT)

    if ready:
        print("\n🎉 Your dataset is ready for YOLO training!")
        print("Run: python train_yolo_simple.py")
    else:
        print("\n⚠️ Please fix the issues before training")


if __name__ == "__main__":
    main()
